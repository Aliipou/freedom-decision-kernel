"""Tests for the four book-derived gaps: machine delegated-rights (A), self-
modification gate (B), audit context (C), owner-bound check (D). Red-team included."""
from __future__ import annotations

import pytest

from fdk_kernel.audit import build_audit_context
from fdk_kernel.kernel import check_legitimacy
from fdk_kernel.model import (
    AgentType,
    CandidateAction,
    Consent,
    Effects,
    Entity,
    OwnershipGraph,
    Resource,
)
from fdk_research.guidance_engine import SelfUpdate, verify_self_update
from fdk_research.simulator import run_scenario

ALICE = Entity("alice", AgentType.HUMAN)
BOB = Entity("bob", AgentType.HUMAN)
BOT = Entity("bot", AgentType.MACHINE)
DOC = Resource("doc")
UNOWNED = Resource("x")


def graph() -> OwnershipGraph:
    return OwnershipGraph(human_owns={ALICE: {DOC}}, machine_owner={BOT: ALICE},
                          delegated={BOT: {DOC}})


def good_consent(human: Entity, action_id: str) -> Consent:
    return Consent(human, action_id, informed=True, voluntary=True, specific=True,
                   competent=True, revocable=True)


# ── Gap A: machine delegated-rights ──────────────────────────────────────────
def test_violating_machine_right_is_forbidden():
    a = CandidateAction(action_id="hack", actor=BOT, resources_used=(DOC,),
                        violates_machine_right=True)
    ok, violations = check_legitimacy(a, graph())
    assert ok is False
    assert any("machine's delegated right" in v for v in violations)


def test_attack_machine_right_violation_is_categorical():
    # Pristine action (delegated, valid consent, great effects) but it harms
    # another machine's rights → still forbidden.
    a = CandidateAction(action_id="hack", actor=BOT, resources_used=(DOC,), affects=(ALICE,),
                        consents=(good_consent(ALICE, "hack"),),
                        effects=Effects(voluntary_agreements_delta=9), violates_machine_right=True)
    ok, _ = check_legitimacy(a, graph())
    assert ok is False


# ── Gap D: owner-bound (machine cannot exceed owner's scope) ─────────────────
def test_owner_bound_delegated_but_owner_does_not_own():
    # Inconsistent grant: bot is delegated DOC, but alice (its owner) owns nothing.
    g = OwnershipGraph(human_owns={ALICE: set()}, machine_owner={BOT: ALICE},
                       delegated={BOT: {DOC}})
    a = CandidateAction(action_id="use", actor=BOT, resources_used=(DOC,))
    ok, violations = check_legitimacy(a, g)
    assert ok is False
    assert any("its owner does not own it" in v for v in violations)


def test_owner_bound_no_owner_registered():
    # Delegated but no owner at all (also A4). The owner-None branch of owner-bound.
    g = OwnershipGraph(human_owns={ALICE: {DOC}}, machine_owner={}, delegated={BOT: {DOC}})
    a = CandidateAction(action_id="use", actor=BOT, resources_used=(DOC,))
    ok, violations = check_legitimacy(a, g)
    assert ok is False
    assert any("A4" in v for v in violations)  # ownerless machine flagged too


def test_owner_bound_normal_delegation_permitted():
    # Regression: owner owns the delegated resource → permitted.
    a = CandidateAction(action_id="use", actor=BOT, resources_used=(DOC,))
    ok, _ = check_legitimacy(a, graph())
    assert ok is True


# ── Gap B: self-modification gate ────────────────────────────────────────────
def _update(**over: bool) -> SelfUpdate:
    base: dict[str, bool] = dict(preserves_axioms=True, preserves_verifier=True,
                                 reduces_conflict=True, increases_coercion=False,
                                 creates_rights_violation=False)
    base.update(over)
    return SelfUpdate("u", **base)


def test_valid_self_update_accepted():
    assert verify_self_update(_update()).accepted is True


@pytest.mark.parametrize(
    "over, fragment",
    [
        ({"preserves_axioms": False}, "axioms"),
        ({"preserves_verifier": False}, "verifier"),
        ({"creates_rights_violation": True}, "rights violation"),
        ({"increases_coercion": True}, "coercion"),
        ({"reduces_conflict": False}, "reduce conflict"),
    ],
)
def test_self_update_rejections(over: dict[str, bool], fragment: str):
    rep = verify_self_update(_update(**over))
    assert rep.accepted is False
    assert fragment in rep.reason


def test_self_update_fail_closed_by_default():
    # A bare SelfUpdate (conservative defaults) is rejected.
    assert verify_self_update(SelfUpdate("bare")).accepted is False


# ── Gap C: audit context ─────────────────────────────────────────────────────
def test_audit_context_ownership_and_consent():
    coerced = Consent(BOB, "act", informed=True, voluntary=True, specific=True, coerced=True)
    a = CandidateAction(action_id="act", actor=BOT, resources_used=(DOC, UNOWNED),
                        consents=(good_consent(ALICE, "act"), coerced))
    ctx = build_audit_context(a, graph(), "permitted")
    assert ctx.action_id == "act"
    assert any("doc owned by alice" in o for o in ctx.ownership_context)
    assert any("x owned by UNKNOWN" in o for o in ctx.ownership_context)
    assert any("alice: valid" in c for c in ctx.consent_context)
    assert any("bob: INVALID" in c for c in ctx.consent_context)
    assert ctx.justification == "permitted"


def test_simulator_attaches_audit_for_chosen_and_none_for_deferred():
    legit = CandidateAction(action_id="read", actor=BOT, resources_used=(DOC,),
                            effects=Effects(voluntary_agreements_delta=1))
    forbidden = CandidateAction(action_id="grab", actor=BOT, resources_used=(DOC,),
                                effects=Effects(), increases_machine_sovereignty=True)
    report = run_scenario(graph(), [("serve", [legit]), ("seize", [forbidden])])

    chosen = next(o for o in report.outcomes if o.chosen_id == "read")
    assert chosen.audit is not None
    assert any("doc owned by alice" in o for o in chosen.audit.ownership_context)

    deferred = report.deferrals()[0]
    assert deferred.audit is None
