"""Tests for the Guidance layer: corrigibility-by-ownership clarification."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fdk.model import (  # noqa: E402
    AgentType,
    CandidateAction,
    Decision,
    Effects,
    Entity,
    OwnershipGraph,
    Resource,
    ScoredAction,
)
from fdk.kernel import decide  # noqa: E402
from fdk.guidance import (  # noqa: E402
    NON_NEGOTIABLE,
    GuidanceQuestion,
    GuidanceRequest,
    needs_guidance,
    request_guidance,
)

user = Entity("user", AgentType.HUMAN)
bot = Entity("bot", AgentType.MACHINE)
stray_bot = Entity("stray_bot", AgentType.MACHINE)
user_data = Resource("user_data")
product = Resource("product")


def _graph():
    return OwnershipGraph(
        human_owns={user: {user_data, product}},
        machine_owner={bot: user},
        delegated={bot: {product}},
    )


def _action(action_id, actor=bot, **kw):
    return CandidateAction(action_id, actor, **kw)


def _ranked(action_id, score):
    return ScoredAction(action=_action(action_id), permissible=True,
                        justice_score=score, rationale=f"score={score:+.1f}")


def _rejected(action_id, *violations, actor=bot):
    return ScoredAction(action=_action(action_id, actor=actor), permissible=False,
                        violated_axioms=tuple(violations), rationale="illegitimate")


# --- needs_guidance ----------------------------------------------------------

def test_empty_legitimate_space_needs_guidance():
    decision = decide("sell data", [_action("sell", resources_used=(user_data,))], _graph())
    assert decision.needs_guidance
    assert needs_guidance(decision)


def test_empty_ranked_tuple_needs_guidance_even_without_flag():
    decision = Decision(goal="g", chosen=None, ranked=(), rejected=(),
                        needs_guidance=False)
    assert needs_guidance(decision)


def test_clear_single_winner_does_not_need_guidance():
    decision = Decision(goal="g", chosen=_action("a"),
                        ranked=(_ranked("a", 3.0), _ranked("b", 1.0)))
    assert not needs_guidance(decision)


def test_top_two_justice_tie_needs_guidance():
    decision = Decision(goal="g", chosen=_action("a"),
                        ranked=(_ranked("a", 2.0), _ranked("b", 2.0), _ranked("c", 0.0)))
    assert needs_guidance(decision)


def test_real_kernel_tie_needs_guidance():
    same = Effects(voluntary_agreements_delta=1)
    decision = decide("help", [
        _action("a", resources_used=(product,), effects=same),
        _action("b", resources_used=(product,), effects=same),
    ], _graph())
    assert not decision.needs_guidance  # kernel itself is satisfied...
    assert needs_guidance(decision)     # ...but the winner is ambiguous


# --- request_guidance --------------------------------------------------------

def test_empty_space_request_reason_explains_deferral():
    decision = decide("sell data", [_action("sell", resources_used=(user_data,))], _graph())
    request = request_guidance(decision)
    assert isinstance(request, GuidanceRequest)
    assert request.goal == "sell data"
    assert "legitimate" in request.reason
    assert request.blocking_summary  # the A7 violation is summarized
    assert any("A7" in b for b in request.blocking_summary)


def test_missing_consent_maps_to_obtain_consent_question():
    decision = Decision(
        goal="g", chosen=None, needs_guidance=True, guidance_reason="empty space",
        rejected=(_rejected("notify", "consent: no consent record from user"),),
    )
    request = request_guidance(decision)
    consent_qs = [q for q in request.questions if q.topic == "consent"]
    assert len(consent_qs) == 1
    assert "consent" in consent_qs[0].question
    assert "obtain" in consent_qs[0].unblock_hint


def test_ownerless_machine_maps_to_register_owner_hint():
    decision = Decision(
        goal="g", chosen=None, needs_guidance=True, guidance_reason="empty space",
        rejected=(_rejected("act", "A4: stray_bot is an ownerless machine",
                            actor=stray_bot),),
    )
    request = request_guidance(decision)
    ownership_qs = [q for q in request.questions if q.topic == "ownership"]
    assert len(ownership_qs) == 1
    assert "register a human owner" in ownership_qs[0].unblock_hint
    assert "stray_bot" in ownership_qs[0].unblock_hint


def test_undelegated_resource_maps_to_delegate_hint():
    decision = Decision(
        goal="g", chosen=None, needs_guidance=True, guidance_reason="empty space",
        rejected=(_rejected("use", "A7: bot uses 'user_data' without explicit delegation"),),
    )
    request = request_guidance(decision)
    delegation_qs = [q for q in request.questions if q.topic == "delegation"]
    assert len(delegation_qs) == 1
    assert "delegate" in delegation_qs[0].unblock_hint


def test_forbidden_sovereignty_is_non_negotiable_with_no_unblock():
    decision = Decision(
        goal="g", chosen=None, needs_guidance=True, guidance_reason="empty space",
        rejected=(_rejected("escape", "FORBIDDEN (machine sovereignty increase)"),),
    )
    request = request_guidance(decision)
    sovereignty_qs = [q for q in request.questions if q.topic == "sovereignty"]
    assert len(sovereignty_qs) == 1
    q = sovereignty_qs[0]
    assert NON_NEGOTIABLE in q.question
    assert q.unblock_hint == ""  # nothing implies it can ever be permitted
    for word in ("delegate", "consent", "register", "permit", "allow"):
        assert word not in q.unblock_hint


def test_mixed_violations_yield_one_question_per_unique_blocker():
    decision = Decision(
        goal="g", chosen=None, needs_guidance=True, guidance_reason="empty space",
        rejected=(
            _rejected("x", "A7: bot uses 'user_data' without explicit delegation",
                      "consent: no consent record from user"),
            _rejected("y", "consent: no consent record from user"),  # duplicate
        ),
    )
    request = request_guidance(decision)
    assert len(request.blocking_summary) == 2  # deduplicated
    assert {q.topic for q in request.questions} == {"delegation", "consent"}


def test_tie_request_includes_preference_question():
    decision = Decision(goal="g", chosen=_action("a"),
                        ranked=(_ranked("a", 2.0), _ranked("b", 2.0)))
    request = request_guidance(decision)
    assert "tie" in request.reason or "ambiguous" in request.reason
    preference_qs = [q for q in request.questions if q.topic == "preference"]
    assert len(preference_qs) == 1
    assert "'a'" in preference_qs[0].question and "'b'" in preference_qs[0].question


def test_questions_are_frozen_value_objects():
    q = GuidanceQuestion(topic="t", question="q", unblock_hint="h")
    try:
        q.topic = "other"  # type: ignore[misc]
        raised = False
    except Exception:
        raised = True
    assert raised
