"""Tests for the advisory Standing layer.

Pins the classification AND the honesty: the hardest classes (non-human, non-present)
are reported as NOT representable in v1.0, and the layer never returns a verdict.
"""
from __future__ import annotations

from fdk_research.standing import (
    StandingAssessment,
    StandingFacts,
    StandingKind,
    assess_standing,
)


def test_competent_adult_is_full_person() -> None:
    a = assess_standing(StandingFacts(is_human=True))
    assert a.kind is StandingKind.FULL_PERSON
    assert a.representable_in_v1 is True
    assert "attests their own" in a.recommendation


def test_child_with_guardian_is_represented() -> None:
    a = assess_standing(
        StandingFacts(is_human=True, is_competent=False, has_guardian=True)
    )
    assert a.kind is StandingKind.GUARDIAN_REPRESENTED
    assert a.representable_in_v1 is True
    assert "GUARDIAN" in a.recommendation


def test_incapacitated_without_guardian_is_protected_by_deferral() -> None:
    a = assess_standing(
        StandingFacts(is_human=True, is_competent=False, has_guardian=False)
    )
    assert a.kind is StandingKind.PROTECTED_NON_CONSENTER
    assert a.representable_in_v1 is True  # protected, but only by default-deny
    assert "DEFER" in a.recommendation


def test_animal_has_no_standing_in_v1() -> None:
    a = assess_standing(StandingFacts(is_human=False))
    assert a.kind is StandingKind.NO_STANDING_IN_V1
    assert a.representable_in_v1 is False
    assert "out-of-frame" in a.recommendation.lower()


def test_future_generation_has_no_standing_in_v1() -> None:
    a = assess_standing(
        StandingFacts(is_human=True, is_living=True, is_present=False)
    )
    assert a.kind is StandingKind.NO_STANDING_IN_V1
    assert a.representable_in_v1 is False
    assert "non-present" in a.rationale


def test_the_dead_have_no_standing_in_v1() -> None:
    a = assess_standing(StandingFacts(is_human=True, is_living=False))
    assert a.kind is StandingKind.NO_STANDING_IN_V1
    assert a.representable_in_v1 is False


def test_assessment_carries_no_verdict() -> None:
    a = assess_standing(StandingFacts(is_human=True))
    assert isinstance(a, StandingAssessment)
    # No ALLOW/DENY surface anywhere — Standing classifies, it does not decide.
    assert not hasattr(a, "permissible")
    assert not hasattr(a, "legitimate")
