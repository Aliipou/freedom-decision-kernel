"""Tests for federation (Phase 11): multi-owner jurisdiction, cross-domain
consent-based access, dispute deferral, and the constitutional-update guard."""
from __future__ import annotations

from fdk.conflict import Outcome
from fdk.federation import (
    Federation,
    constitutional_update_allowed,
    federated_decide,
    resolve_dispute,
)
from fdk.guidance import GuidanceRequest
from fdk.model import AgentType, CandidateAction, Consent, Effects, Entity, OwnershipGraph, Resource
from fdk.ontology import Claim, ClaimBasis, Conflict
from fdk.planner import ListProposer

ALICE = Entity("alice", AgentType.HUMAN)
BOB = Entity("bob", AgentType.HUMAN)
BOTA = Entity("botA", AgentType.MACHINE)
DOCA = Resource("docA")
DOCA2 = Resource("docA2")
DOCB = Resource("docB")
UNOWNED = Resource("unowned")
SHARED = Resource("shared")


def two_domains() -> Federation:
    # Domain A: alice owns docA/docA2; botA is alice's machine, delegated docA.
    g_a = OwnershipGraph(human_owns={ALICE: {DOCA, DOCA2}}, machine_owner={BOTA: ALICE},
                         delegated={BOTA: {DOCA}})
    # Domain B: bob owns docB and cross-delegates it to alice's machine botA.
    g_b = OwnershipGraph(human_owns={BOB: {DOCB}}, delegated={BOTA: {DOCB}})
    return Federation(domains={"A": g_a, "B": g_b})


def good_consent(human: Entity, action_id: str) -> Consent:
    return Consent(human, action_id, informed=True, voluntary=True, specific=True,
                   competent=True, revocable=True)


def test_merged_graph_unions_domains():
    m = two_domains().merged_graph()
    assert m.human_owns_resource(ALICE, DOCA)
    assert m.human_owns_resource(BOB, DOCB)
    assert m.owner_of(BOTA) == ALICE
    assert m.machine_has_delegated(BOTA, DOCA)
    assert m.machine_has_delegated(BOTA, DOCB)  # cross-delegated from domain B


def test_jurisdiction_routes_by_owner():
    fed = two_domains()
    assert fed.jurisdiction(DOCA) == "A"
    assert fed.jurisdiction(DOCB) == "B"
    assert fed.jurisdiction(UNOWNED) is None


def test_stakeholder_domains_distinct_in_order():
    fed = two_domains()
    a = CandidateAction("x", BOTA, resources_used=(DOCA, DOCA2, DOCB, UNOWNED))
    # docA, docA2 → A (dup skipped); docB → B; unowned → no domain (skipped)
    assert fed.stakeholder_domains(a) == ("A", "B")


def test_cross_domain_use_with_consent_is_legitimate():
    fed = two_domains()
    a = CandidateAction("use_b", BOTA, resources_used=(DOCB,), affects=(BOB,),
                        consents=(good_consent(BOB, "use_b"),),
                        effects=Effects(voluntary_agreements_delta=1))
    result = federated_decide("serve bob", ListProposer([a]), fed)
    assert not isinstance(result, GuidanceRequest)
    assert result.chosen is not None
    assert result.chosen.action_id == "use_b"


def test_cross_domain_use_without_consent_defers():
    fed = two_domains()
    a = CandidateAction("grab_b", BOTA, resources_used=(DOCB,), effects=Effects())
    result = federated_decide("take bob's data", ListProposer([a]), fed)
    assert isinstance(result, GuidanceRequest)


def test_resolve_dispute_defers_to_humans():
    # Two domains each assert ownership of the same resource → underdetermined → defer.
    fed = Federation(domains={
        "A": OwnershipGraph(human_owns={ALICE: {SHARED}}),
        "B": OwnershipGraph(human_owns={BOB: {SHARED}}),
    })
    conflict = Conflict(Claim(ALICE, SHARED, ClaimBasis.OWNERSHIP),
                        Claim(BOB, SHARED, ClaimBasis.OWNERSHIP))
    res = resolve_dispute(conflict, fed)
    assert res.outcome == Outcome.DEFER


def test_constitutional_update_guard():
    # axioms are unalterable; only axiom-consistent rules may be added.
    assert constitutional_update_allowed(changes_axioms=True, consistent_with_axioms=True)[0] is False
    assert constitutional_update_allowed(changes_axioms=False, consistent_with_axioms=False)[0] is False
    ok, reason = constitutional_update_allowed(changes_axioms=False, consistent_with_axioms=True)
    assert ok is True
    assert "adopted" in reason
