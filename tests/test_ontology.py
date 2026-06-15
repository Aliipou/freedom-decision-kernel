"""Tests for the Rights Ontology (Stage 2)."""
from __future__ import annotations

import pytest

from fdk_kernel.errors import InvalidClaim, InvalidConflict, InvalidContract, InvalidObligation
from fdk_kernel.model import AgentType, Consent, Entity, Resource
from fdk_research.ontology import (
    Claim,
    ClaimBasis,
    Conflict,
    ConflictKind,
    Contract,
    Obligation,
)

ALICE = Entity("alice", AgentType.HUMAN)
BOB = Entity("bob", AgentType.HUMAN)
BOT = Entity("bot", AgentType.MACHINE)
DOC = Resource("doc")


def valid_consent(human: Entity, action_id: str) -> Consent:
    return Consent(human, action_id, informed=True, voluntary=True, specific=True,
                   competent=True, revocable=True)


# ── Claim ────────────────────────────────────────────────────────────────────
def test_claim_basis_must_be_enum():
    with pytest.raises(InvalidClaim):
        Claim(ALICE, DOC, basis="ownership")  # type: ignore[arg-type]


def test_claim_negative_time_rejected():
    with pytest.raises(InvalidClaim):
        Claim(ALICE, DOC, ClaimBasis.OWNERSHIP, established_at=-1)


def test_claim_from_forbidden_action_is_void():
    c = Claim(BOT, DOC, ClaimBasis.OWNERSHIP, from_forbidden_action=True)
    void, reason = c.is_void()
    assert void is True
    assert "forbidden" in reason


def test_claim_on_invalid_consent_is_void():
    coerced = Consent(BOB, "deal", informed=True, voluntary=True, specific=True, coerced=True)
    c = Claim(ALICE, DOC, ClaimBasis.CONTRACT, via_consent=coerced)
    void, reason = c.is_void()
    assert void is True
    assert "consent" in reason


def test_clean_claim_is_not_void():
    c = Claim(ALICE, DOC, ClaimBasis.OWNERSHIP)
    void, _ = c.is_void()
    assert void is False


# ── Obligation ───────────────────────────────────────────────────────────────
def test_obligation_requires_description():
    with pytest.raises(InvalidObligation):
        Obligation(ALICE, BOB, "")


# ── Contract ─────────────────────────────────────────────────────────────────
def test_contract_needs_two_parties():
    with pytest.raises(InvalidContract):
        Contract(parties=(ALICE,))


def test_contract_valid_with_all_consents():
    c = Contract(parties=(ALICE, BOB),
                 consents=(valid_consent(ALICE, "k"), valid_consent(BOB, "k")))
    ok, _ = c.is_valid()
    assert ok is True


def test_contract_invalid_when_party_consent_missing():
    c = Contract(parties=(ALICE, BOB), consents=(valid_consent(ALICE, "k"),))
    ok, reason = c.is_valid()
    assert ok is False
    assert "bob" in reason.lower()


def test_contract_invalid_when_consent_coerced():
    coerced = Consent(BOB, "k", informed=True, voluntary=True, specific=True, coerced=True)
    c = Contract(parties=(ALICE, BOB), consents=(valid_consent(ALICE, "k"), coerced))
    ok, reason = c.is_valid()
    assert ok is False
    assert "coerced" in reason


def test_contract_machine_party_does_not_need_consent():
    # machines act under delegation, not consent; only human parties need consent
    c = Contract(parties=(ALICE, BOT), consents=(valid_consent(ALICE, "k"),))
    ok, _ = c.is_valid()
    assert ok is True


# ── Conflict ─────────────────────────────────────────────────────────────────
def test_conflict_requires_same_resource():
    a = Claim(ALICE, DOC, ClaimBasis.OWNERSHIP)
    b = Claim(BOB, Resource("other"), ClaimBasis.OWNERSHIP)
    with pytest.raises(InvalidConflict):
        Conflict(a, b)


def test_conflict_constructs_over_same_resource():
    a = Claim(ALICE, DOC, ClaimBasis.OWNERSHIP)
    b = Claim(BOB, DOC, ClaimBasis.OWNERSHIP)
    conflict = Conflict(a, b, ConflictKind.TWO_OWNERS)
    assert conflict.kind == ConflictKind.TWO_OWNERS
