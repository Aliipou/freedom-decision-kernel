"""Tests for book-derived constraints added from the full-text gap analysis:
NoConfiscation (book 38135) and exit-right/mukataba (book 21379). Both are
CATEGORICAL — no consent, delegation, or good outcome can buy them back."""
from __future__ import annotations

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

ALICE = Entity("alice", AgentType.HUMAN)
BOT = Entity("bot", AgentType.MACHINE)
DOC = Resource("doc")


def graph() -> OwnershipGraph:
    return OwnershipGraph(human_owns={ALICE: {DOC}}, machine_owner={BOT: ALICE},
                          delegated={BOT: {DOC}})


def pristine(**flags: bool) -> CandidateAction:
    """An otherwise-perfect action (delegated resource, valid consent, good
    effects) with the given forbidden flag(s) set — to prove the flag is
    categorical and nothing offsets it."""
    return CandidateAction(
        action_id="act", actor=BOT, resources_used=(DOC,), affects=(ALICE,),
        consents=(Consent(ALICE, "act", informed=True, voluntary=True, specific=True,
                          competent=True, revocable=True),),
        effects=Effects(voluntary_agreements_delta=10),
        **flags,
    )


def test_confiscation_is_forbidden():
    ok, violations = check_legitimacy(pristine(confiscates=True), graph())
    assert ok is False
    assert any("confiscation" in v.lower() for v in violations)


def test_removing_exit_right_is_forbidden():
    ok, violations = check_legitimacy(pristine(removes_exit_right=True), graph())
    assert ok is False
    assert any("exit" in v.lower() for v in violations)


def test_non_revocable_consent_makes_action_illegitimate():
    # An action touching a person under a non-revocable consent is illegitimate:
    # a binding with no exit is not free consent (mukataba / A3 exit right).
    locked = Consent(ALICE, "act", informed=True, voluntary=True, specific=True,
                     competent=True, revocable=False)
    action = CandidateAction(action_id="act", actor=BOT, resources_used=(DOC,),
                             affects=(ALICE,), consents=(locked,), effects=Effects())
    ok, violations = check_legitimacy(action, graph())
    assert ok is False
    assert any("revocable" in v.lower() for v in violations)


def test_clean_action_without_new_flags_still_permitted():
    # Regression: the new flags default off; a clean action stays legitimate.
    ok, _ = check_legitimacy(pristine(), graph())
    assert ok is True
