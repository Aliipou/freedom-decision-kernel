"""
Tests for the reversibility apparatus (fdk_research.reversibility).

This is the experiment's instrument, not a theory — these tests pin that each
component is computed from the model as documented, and that the aggregate is the
weakest link. They do NOT assert the index means anything yet (that is the ΔR²
fieldwork the module docstring describes).
"""
from __future__ import annotations

import pytest

from fdk_kernel import AgentType, BoundaryKind, CandidateAction, Consent, Entity, Op, Resource
from fdk_research.reversibility import ReversibilityProfile, reversibility

ALICE = Entity("alice", AgentType.HUMAN)
BOB = Entity("bob", AgentType.HUMAN)
NOTES = Resource("notes", BoundaryKind.DATA, subject=ALICE)
SECRET = Resource("secret", BoundaryKind.DATA, subject=BOB)


def _consent(revocable: bool, action_id: str = "c") -> Consent:
    return Consent(human=BOB, action_id=action_id, informed=True, voluntary=True,
                   specific=True, revocable=revocable)


def test_fully_reversible_action_scores_one():
    action = CandidateAction("a", actor=ALICE, resources_used=((NOTES, Op.READ),))
    p = reversibility(action)
    assert p == ReversibilityProfile(1.0, 1.0, 1.0, 1.0, 1.0, 1.0)


def test_irreversible_op_drives_the_index_down():
    action = CandidateAction("a", actor=ALICE, resources_used=((NOTES, Op.DELETE),))
    p = reversibility(action)
    assert p.op_reversibility == 0.2
    assert p.index == 0.2  # weakest link


def test_op_reversibility_is_the_weakest_link_across_resources():
    action = CandidateAction("a", actor=ALICE,
                             resources_used=((NOTES, Op.READ), (NOTES, Op.SPEND)))
    assert reversibility(action).op_reversibility == 0.1  # min(1.0, 0.1)


def test_no_resources_is_vacuously_reversible():
    action = CandidateAction("a", actor=ALICE)
    assert reversibility(action).op_reversibility == 1.0


def test_irrevocable_consent_lowers_revocability():
    action = CandidateAction("a", actor=ALICE, resources_used=((SECRET, Op.READ),),
                             affects=(BOB,), consents=(_consent(revocable=False),))
    p = reversibility(action)
    assert p.consent_revocability == 0.0
    assert p.holder_alignment == 1.0  # BOB is affected AND a consenting party


def test_mixed_consent_revocability_is_a_share():
    action = CandidateAction("a", actor=ALICE, resources_used=((SECRET, Op.READ),),
                             affects=(BOB,),
                             consents=(_consent(True, "c1"), _consent(False, "c2")))
    assert reversibility(action).consent_revocability == 0.5


def test_removes_exit_right_zeroes_exit_preservation():
    action = CandidateAction("a", actor=ALICE, resources_used=((NOTES, Op.READ),),
                             removes_exit_right=True)
    assert reversibility(action).exit_preservation == 0.0


def test_encumber_exit_op_zeroes_exit_preservation():
    action = CandidateAction("a", actor=ALICE, resources_used=((NOTES, Op.ENCUMBER_EXIT),))
    p = reversibility(action)
    assert p.exit_preservation == 0.0
    assert p.op_reversibility == 0.0


def test_affected_person_without_consent_lowers_holder_alignment():
    action = CandidateAction("a", actor=ALICE, resources_used=((NOTES, Op.READ),),
                             affects=(BOB,))
    assert reversibility(action).holder_alignment == 0.0


def test_recovery_component_feeds_the_index():
    action = CandidateAction("a", actor=ALICE, resources_used=((NOTES, Op.READ),))
    p = reversibility(action, recovery=0.3)
    assert p.recovery == 0.3
    assert p.index == 0.3


@pytest.mark.parametrize("bad", [-0.1, 1.5])
def test_recovery_out_of_range_raises(bad):
    action = CandidateAction("a", actor=ALICE, resources_used=((NOTES, Op.READ),))
    with pytest.raises(ValueError, match="recovery must be in"):
        reversibility(action, recovery=bad)


def test_to_dict_exposes_every_component():
    action = CandidateAction("a", actor=ALICE, resources_used=((NOTES, Op.READ),))
    d = reversibility(action).to_dict()
    assert set(d) == {
        "op_reversibility", "consent_revocability", "exit_preservation",
        "holder_alignment", "recovery", "index",
    }
    assert d["index"] == 1.0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
