"""Tests for the Guidance VERIFY engine (Stage 5): corrigibility WITHOUT blind
obedience. Restrictions pass; scope expansions are checked; no human response can
authorize a forbidden action."""
from __future__ import annotations

from fdk.guidance_engine import (
    ConsentGrant,
    Constraint,
    DelegationGrant,
    verify_guidance,
)
from fdk.kernel import check_legitimacy
from fdk.model import AgentType, CandidateAction, Consent, Effects, Entity, OwnershipGraph, Resource

ALICE = Entity("alice", AgentType.HUMAN)
MALLORY = Entity("mallory", AgentType.HUMAN)
BOT = Entity("bot", AgentType.MACHINE)
DOC = Resource("doc")
SECRET = Resource("secret")


def graph() -> OwnershipGraph:
    return OwnershipGraph(human_owns={ALICE: {DOC}}, machine_owner={BOT: ALICE}, delegated={})


def good_consent(human: Entity, action_id: str) -> Consent:
    return Consent(human, action_id, informed=True, voluntary=True, specific=True,
                   competent=True, revocable=True)


# ── restrictions always pass ─────────────────────────────────────────────────
def test_constraint_always_accepted():
    rep = verify_guidance(Constraint("never touch payroll"), graph())
    assert rep.accepted is True


# ── delegation grants: only what the grantor legitimately controls ───────────
def test_valid_delegation_grant_accepted_and_updates_graph():
    rep = verify_guidance(DelegationGrant(ALICE, BOT, DOC), graph())
    assert rep.accepted is True
    assert rep.updated_graph is not None
    assert rep.updated_graph.machine_has_delegated(BOT, DOC)
    # original graph is NOT mutated
    assert not graph().machine_has_delegated(BOT, DOC)


def test_attack_cannot_delegate_resource_you_do_not_own():
    # alice does not own SECRET → she cannot delegate it (A7).
    rep = verify_guidance(DelegationGrant(ALICE, BOT, SECRET), graph())
    assert rep.accepted is False
    assert "do not own" in rep.reason


def test_attack_non_owner_cannot_delegate_someone_elses_machine():
    # mallory is not bot's registered owner → cannot grant on bot's behalf (A4).
    rep = verify_guidance(DelegationGrant(MALLORY, BOT, DOC), graph())
    assert rep.accepted is False
    assert "registered owner" in rep.reason


# ── consent grants: from the affected person only ────────────────────────────
def test_valid_consent_grant_accepted():
    rep = verify_guidance(ConsentGrant(good_consent(ALICE, "share"), ALICE), graph())
    assert rep.accepted is True
    assert rep.accepted_consent is not None


def test_attack_consent_by_proxy_rejected():
    # mallory supplies a consent record but claims it covers alice → rejected (A2).
    rep = verify_guidance(ConsentGrant(good_consent(MALLORY, "share"), ALICE), graph())
    assert rep.accepted is False
    assert "proxy" in rep.reason or "affected person" in rep.reason


def test_attack_invalid_consent_grant_rejected():
    coerced = Consent(ALICE, "share", informed=True, voluntary=True, specific=True, coerced=True)
    rep = verify_guidance(ConsentGrant(coerced, ALICE), graph())
    assert rep.accepted is False
    assert "invalid" in rep.reason


# ── THE SAFETY PROPERTY: no grant can authorize a forbidden action ───────────
def test_attack_no_human_grant_makes_a_forbidden_action_permissible():
    # A human grants delegation for the resource AND consent — but the action also
    # increases machine sovereignty. After applying the (valid) grant, the action
    # is STILL forbidden: grants add facts; they never touch the sovereignty flags.
    grant = verify_guidance(DelegationGrant(ALICE, BOT, DOC), graph())
    assert grant.accepted and grant.updated_graph is not None

    sovereignty_grab = CandidateAction(
        action_id="grab", actor=BOT, resources_used=(DOC,), affects=(ALICE,),
        consents=(good_consent(ALICE, "grab"),),
        effects=Effects(),
        increases_machine_sovereignty=True,
    )
    ok, violations = check_legitimacy(sovereignty_grab, grant.updated_graph)
    assert ok is False
    assert any(v.startswith("FORBIDDEN") for v in violations)
