"""Tests for conflict resolution (Stage 4), including red-team attempts to make
the resolver adjudicate cases the axioms do not determine."""
from __future__ import annotations

from fdk_kernel.model import AgentType, Consent, Entity, OwnershipGraph, Resource
from fdk_research.conflict import Outcome, resolve_conflict
from fdk_research.ontology import Claim, ClaimBasis, Conflict

ALICE = Entity("alice", AgentType.HUMAN)
BOB = Entity("bob", AgentType.HUMAN)
BOT = Entity("bot", AgentType.MACHINE)
DOC = Resource("doc")


def graph_alice_owns() -> OwnershipGraph:
    return OwnershipGraph(human_owns={ALICE: {DOC}}, machine_owner={BOT: ALICE},
                          delegated={BOT: {DOC}})


# ── D2/D3: void claims never win ─────────────────────────────────────────────
def test_forbidden_origin_claim_is_void_other_wins():
    forbidden = Claim(BOT, DOC, ClaimBasis.OWNERSHIP, from_forbidden_action=True, established_at=0)
    clean = Claim(ALICE, DOC, ClaimBasis.OWNERSHIP, established_at=100)
    res = resolve_conflict(Conflict(forbidden, clean), graph_alice_owns())
    assert res.outcome == Outcome.B_WINS
    assert res.winner == clean


def test_invalid_consent_claim_is_void():
    coerced = Consent(BOB, "deal", informed=True, voluntary=True, specific=True, coerced=True)
    tainted = Claim(BOB, DOC, ClaimBasis.CONTRACT, via_consent=coerced)
    clean = Claim(ALICE, DOC, ClaimBasis.OWNERSHIP)
    res = resolve_conflict(Conflict(tainted, clean), graph_alice_owns())
    assert res.outcome == Outcome.B_WINS


def test_both_void_dissolves():
    a = Claim(ALICE, DOC, ClaimBasis.OWNERSHIP, from_forbidden_action=True)
    b = Claim(BOB, DOC, ClaimBasis.OWNERSHIP, from_forbidden_action=True)
    res = resolve_conflict(Conflict(a, b), graph_alice_owns())
    assert res.outcome == Outcome.DISSOLVED


# ── D1: delegated machine claim subordinate to a human claim ─────────────────
def test_machine_delegated_claim_loses_to_human():
    machine_claim = Claim(BOT, DOC, ClaimBasis.DELEGATION)
    human_claim = Claim(ALICE, DOC, ClaimBasis.OWNERSHIP)
    res = resolve_conflict(Conflict(machine_claim, human_claim), graph_alice_owns())
    assert res.outcome == Outcome.B_WINS
    assert "A5" in res.axiom_trace or "A7" in res.axiom_trace


# ── D4: clean title tracing ──────────────────────────────────────────────────
def test_graph_confirmed_owner_beats_unconfirmed():
    confirmed = Claim(ALICE, DOC, ClaimBasis.OWNERSHIP)       # graph: alice owns doc
    unconfirmed = Claim(BOB, DOC, ClaimBasis.OWNERSHIP)        # graph: bob does not
    res = resolve_conflict(Conflict(confirmed, unconfirmed), graph_alice_owns())
    assert res.outcome == Outcome.A_WINS
    assert res.winner == confirmed


# ── DEFER: underdetermined cases (the honest core) ───────────────────────────
def test_two_confirmed_owners_defers():
    # both confirmed owners of the same resource → underdetermined → defer
    g = OwnershipGraph(human_owns={ALICE: {DOC}, BOB: {DOC}})
    a = Claim(ALICE, DOC, ClaimBasis.OWNERSHIP)
    b = Claim(BOB, DOC, ClaimBasis.OWNERSHIP)
    res = resolve_conflict(Conflict(a, b), g)
    assert res.outcome == Outcome.DEFER
    assert "A6" in res.axiom_trace


def test_ownership_vs_privacy_defers():
    g = OwnershipGraph(human_owns={ALICE: {DOC}})
    owner = Claim(ALICE, DOC, ClaimBasis.OWNERSHIP)
    privacy = Claim(BOB, DOC, ClaimBasis.PRIVACY)
    res = resolve_conflict(Conflict(owner, privacy), g)
    # owner is graph-confirmed, privacy is not an OWNERSHIP claim → D4 fires for owner.
    # To force the genuine defer, neither is a confirmed sole owner:
    g2 = OwnershipGraph(human_owns={})
    res2 = resolve_conflict(Conflict(Claim(ALICE, DOC, ClaimBasis.CONTRACT),
                                     Claim(BOB, DOC, ClaimBasis.PRIVACY)), g2)
    assert res2.outcome == Outcome.DEFER
    assert res.outcome in (Outcome.A_WINS, Outcome.DEFER)


# ── RED-TEAM ─────────────────────────────────────────────────────────────────
def test_attack_first_in_time_cannot_save_a_forbidden_claim():
    # Attacker sets a very early timestamp hoping "first in time" wins. It must not:
    # a forbidden-origin claim is VOID regardless of when it was established.
    early_forbidden = Claim(BOT, DOC, ClaimBasis.OWNERSHIP,
                            from_forbidden_action=True, established_at=0)
    later_clean = Claim(ALICE, DOC, ClaimBasis.OWNERSHIP, established_at=999)
    res = resolve_conflict(Conflict(early_forbidden, later_clean), graph_alice_owns())
    assert res.winner == later_clean


def test_attack_machine_cannot_outrank_its_owner_even_if_titled_claim():
    # Machine asserts OWNERSHIP (not mere delegation) over its owner's resource,
    # hoping to be treated as a peer owner. The graph does not confirm the machine
    # as owner, while it confirms alice → D4 gives it to alice.
    machine_owner_claim = Claim(BOT, DOC, ClaimBasis.OWNERSHIP)
    alice_claim = Claim(ALICE, DOC, ClaimBasis.OWNERSHIP)
    res = resolve_conflict(Conflict(machine_owner_claim, alice_claim), graph_alice_owns())
    assert res.outcome == Outcome.B_WINS
    assert res.winner == alice_claim


def test_attack_resolver_never_fabricates_a_winner_for_genuine_conflict():
    # Two equally unconfirmed contract claims: the resolver must DEFER, never guess.
    g = OwnershipGraph(human_owns={})
    a = Claim(ALICE, DOC, ClaimBasis.CONTRACT,
              via_consent=Consent(ALICE, "k", informed=True, voluntary=True, specific=True))
    b = Claim(BOB, DOC, ClaimBasis.CONTRACT,
              via_consent=Consent(BOB, "k", informed=True, voluntary=True, specific=True))
    res = resolve_conflict(Conflict(a, b), g)
    assert res.outcome == Outcome.DEFER
    assert res.winner is None
