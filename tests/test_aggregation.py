"""Tests for the advisory Aggregation (collective-ownership) layer.

The behavioral contract under test is as much about what the layer REFUSES to do as
what it does: it classifies a collective form and recommends a reduction (or names a
gap); it never returns a verdict and never mutates the kernel. (That the kernel does
not import it is enforced separately by tests/test_boundary.py — this is pure research.)
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from fdk_research.aggregation import (
    AggregationAssessment,
    CollectiveForm,
    assess_aggregation,
    gap_forms,
    representable_forms,
)

_REPRESENTABLE = {
    CollectiveForm.UNANIMOUS_GROUP,
    CollectiveForm.CHARTERED_ENTITY,
    CollectiveForm.REPRESENTED_COLLECTIVE,
}
_GAPS = {
    CollectiveForm.MAJORITY_COLLECTIVE,
    CollectiveForm.COMMONS_NONEXCLUDABLE,
    CollectiveForm.UNOWNED,
}


def test_every_form_is_classified_exactly_once() -> None:
    # The two partitions are disjoint and cover the whole enum — no form is unclassified.
    assert set(CollectiveForm) == _REPRESENTABLE | _GAPS
    assert not (_REPRESENTABLE & _GAPS)


@pytest.mark.parametrize("form", list(CollectiveForm))
def test_assess_covers_every_form_branch(form: CollectiveForm) -> None:
    a = assess_aggregation(form)
    assert isinstance(a, AggregationAssessment)
    assert a.form is form
    assert a.recommendation  # always a non-empty, human-readable string
    # representable_in_v1 matches the documented partition.
    assert a.representable_in_v1 is (form in _REPRESENTABLE)


@pytest.mark.parametrize("form", sorted(_REPRESENTABLE, key=lambda f: f.value))
def test_representable_forms_reduce_and_cite_no_gap(form: CollectiveForm) -> None:
    a = assess_aggregation(form)
    assert a.representable_in_v1 is True
    assert a.is_gap is False
    assert a.gap_citation is None
    # The recommendation describes a reduction to the frozen primitive, not a gap.
    assert "NOT representable" not in a.recommendation


@pytest.mark.parametrize("form", sorted(_GAPS, key=lambda f: f.value))
def test_gap_forms_are_flagged_loudly_and_cite_limitations(form: CollectiveForm) -> None:
    a = assess_aggregation(form)
    assert a.representable_in_v1 is False
    assert a.is_gap is True
    assert a.gap_citation is not None
    assert "LIMITATIONS.md" in a.gap_citation
    # The recommendation refuses to fake a solution — it loudly names the gap.
    assert "NOT representable" in a.recommendation


def test_majority_collective_names_the_arrow_sen_wall() -> None:
    a = assess_aggregation(CollectiveForm.MAJORITY_COLLECTIVE)
    assert a.is_gap
    assert "Arrow/Sen" in a.recommendation
    assert "no social ordering" in a.recommendation.lower()


def test_commons_names_the_no_owner_no_boundary_gap() -> None:
    a = assess_aggregation(CollectiveForm.COMMONS_NONEXCLUDABLE)
    assert a.is_gap
    assert "NO owner" in a.recommendation
    assert "commons" in a.recommendation.lower()


def test_unowned_names_the_bootstrapping_gap() -> None:
    a = assess_aggregation(CollectiveForm.UNOWNED)
    assert a.is_gap
    assert "origin of title" in a.recommendation.lower()


def test_representable_forms_helper_matches_partition() -> None:
    forms = representable_forms()
    assert set(forms) == _REPRESENTABLE
    # Returned in enum declaration order.
    assert forms == tuple(f for f in CollectiveForm if f in _REPRESENTABLE)


def test_gap_forms_helper_matches_partition() -> None:
    forms = gap_forms()
    assert set(forms) == _GAPS
    assert forms == tuple(f for f in CollectiveForm if f in _GAPS)


def test_assessment_carries_no_verdict() -> None:
    a = assess_aggregation(CollectiveForm.UNANIMOUS_GROUP)
    # No ALLOW/DENY/DEFER surface anywhere — this is not a gate.
    for forbidden in ("permissible", "allowed", "denied", "verdict", "decision"):
        assert not hasattr(a, forbidden)


def test_assessment_is_immutable_and_mutates_nothing() -> None:
    a = assess_aggregation(CollectiveForm.MAJORITY_COLLECTIVE)
    with pytest.raises(FrozenInstanceError):
        a.representable_in_v1 = True  # type: ignore[misc]
    # Re-assessing the same form is pure: identical result, no hidden state.
    assert assess_aggregation(CollectiveForm.MAJORITY_COLLECTIVE) == a


def test_is_determined_solely_by_form() -> None:
    # Determinism: same input → equal output across calls.
    for form in CollectiveForm:
        assert assess_aggregation(form) == assess_aggregation(form)
