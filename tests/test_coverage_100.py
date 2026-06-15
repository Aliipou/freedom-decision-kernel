"""Targeted tests closing the last coverage branches across the kernel."""
from __future__ import annotations

import pytest

from fdk_kernel.errors import InvalidEntity, InvalidOwnershipGraph
from fdk_kernel.kernel import check_legitimacy
from fdk_kernel.model import (
    AgentType,
    CandidateAction,
    Consent,
    Decision,
    Effects,
    Entity,
    OwnershipGraph,
    Resource,
    ScoredAction,
)
from fdk_research.conflict import Outcome, resolve_conflict
from fdk_research.guidance_engine import DelegationGrant, verify_guidance
from fdk_research.guidance_resolution import request_guidance
from fdk_research.justice import justice_score
from fdk_research.ontology import Claim, ClaimBasis, Conflict

ALICE = Entity("alice", AgentType.HUMAN)
BOB = Entity("bob", AgentType.HUMAN)
BOT = Entity("bot", AgentType.MACHINE)
DOC = Resource("doc")


# ── model.py: Entity kind + each Consent leaf + graph non-machine branch ─────
def test_entity_invalid_kind():
    with pytest.raises(InvalidEntity):
        Entity("x", kind="machine")  # type: ignore[arg-type]


def test_graph_non_machine_owner_key_rejected():
    # key is a human (not its own owner) → the not-a-machine branch.
    with pytest.raises(InvalidOwnershipGraph):
        OwnershipGraph(machine_owner={ALICE: BOB}).validate()


@pytest.mark.parametrize(
    "kwargs, fragment",
    [
        ({"informed": False}, "not informed"),
        ({"informed": True, "voluntary": False}, "not voluntary"),
        ({"informed": True, "voluntary": True, "specific": False}, "not specific"),
        ({"informed": True, "voluntary": True, "specific": True, "competent": False},
         "not competent"),
        ({"informed": True, "voluntary": True, "specific": True, "revocable": False},
         "not revocable"),
    ],
)
def test_consent_each_invalid_leaf(kwargs: dict[str, bool], fragment: str):
    ok, reason = Consent(ALICE, "a", **kwargs).is_valid()
    assert ok is False
    assert fragment in reason


def test_consent_fully_valid_ok():
    ok, reason = Consent(ALICE, "a", informed=True, voluntary=True, specific=True,
                         competent=True, revocable=True).is_valid()
    assert ok is True
    assert reason == "ok"


# ── kernel.py: affected human WITH a consent present; non-human affected ─────
def test_legitimacy_with_present_consent_and_machine_affected():
    g = OwnershipGraph(human_owns={ALICE: {DOC}}, machine_owner={BOT: ALICE},
                       delegated={BOT: {DOC}})
    action = CandidateAction(
        action_id="touch", actor=BOT, resources_used=(DOC,), affects=(ALICE, BOT),
        consents=(Consent(ALICE, "touch", informed=True, voluntary=True, specific=True,
                          competent=True, revocable=True),),
        effects=Effects())
    ok, _ = check_legitimacy(action, g)
    assert ok is True  # machine target skipped; alice's present consent is valid


# ── conflict.py: the B-side branches (D1 and D4) ─────────────────────────────
def test_conflict_b_delegated_loses():
    g = OwnershipGraph(human_owns={ALICE: {DOC}}, machine_owner={BOT: ALICE})
    human = Claim(ALICE, DOC, ClaimBasis.OWNERSHIP)
    machine = Claim(BOT, DOC, ClaimBasis.DELEGATION)
    res = resolve_conflict(Conflict(human, machine), g)
    assert res.outcome == Outcome.A_WINS


def test_conflict_b_titled_wins():
    g = OwnershipGraph(human_owns={ALICE: {DOC}})
    unconfirmed = Claim(BOB, DOC, ClaimBasis.OWNERSHIP)
    confirmed = Claim(ALICE, DOC, ClaimBasis.OWNERSHIP)
    res = resolve_conflict(Conflict(unconfirmed, confirmed), g)
    assert res.outcome == Outcome.B_WINS


# ── guidance.py: reason branches + A3/other questions + tie ──────────────────
def _scored(action_id: str, violation: str) -> ScoredAction:
    return ScoredAction(action=CandidateAction(action_id=action_id, actor=BOT),
                        permissible=False, violated_axioms=(violation,))


def test_guidance_uses_explicit_reason():
    d = Decision(goal="g", chosen=None, rejected=(_scored("x", "A3: not owned"),),
                 needs_guidance=True, guidance_reason="explicit reason here")
    req = request_guidance(d)
    assert req.reason == "explicit reason here"
    # A3 question branch produces an ownership-clarification hint
    assert any("A3" in v for v in req.blocking_summary)
    assert any(q.topic == "ownership" for q in req.questions)


def test_guidance_other_violation_branch():
    d = Decision(goal="g", chosen=None, rejected=(_scored("y", "weird novel blocker"),),
                 needs_guidance=True)
    req = request_guidance(d)
    assert any(q.topic == "other" for q in req.questions)


def test_guidance_top_tie_reason_and_question():
    a = ScoredAction(action=CandidateAction(action_id="a", actor=BOT), permissible=True,
                     justice_score=1.0)
    b = ScoredAction(action=CandidateAction(action_id="b", actor=BOT), permissible=True,
                     justice_score=1.0)
    d = Decision(goal="g", chosen=None, ranked=(a, b))
    req = request_guidance(d)
    assert "tie" in req.reason.lower() or "ambiguous" in req.reason.lower()
    assert any(q.topic == "preference" for q in req.questions)


# ── guidance_engine.py: non-human grantor + non-machine target branches ──────
def test_delegation_non_human_grantor_rejected():
    g = OwnershipGraph(machine_owner={BOT: ALICE})
    rep = verify_guidance(DelegationGrant(BOT, BOT, DOC), g)  # machine as grantor
    assert rep.accepted is False
    assert "human" in rep.reason


def test_delegation_non_machine_target_rejected():
    g = OwnershipGraph(human_owns={ALICE: {DOC}})
    rep = verify_guidance(DelegationGrant(ALICE, BOB, DOC), g)  # human as "machine" target
    assert rep.accepted is False
    assert "machine" in rep.reason


# ── justice.py: non-consenting affected but no positive harm branch ──────────
def test_justice_non_consenting_but_no_harm():
    g = OwnershipGraph(human_owns={ALICE: {DOC}})
    action = CandidateAction(action_id="benign", actor=BOT, affects=(BOB,),
                             effects=Effects(voluntary_agreements_delta=1))  # no harm deltas
    js = justice_score(action, g)
    assert js.worst_off_delta == 0
    assert "non-consenting affected" in js.rationale


