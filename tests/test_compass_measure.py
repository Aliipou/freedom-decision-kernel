"""Tests for the advisory compass estimators (Stage 6). These are uncalibrated
proxies; the tests pin their ranges, edges, and the structural properties the
spec claims (e.g. coercion requires the conjunction)."""
from __future__ import annotations

import pytest

from fdk_research.compass_measure import (
    coercion_score,
    dependency_index,
    exit_options,
    ownership_clarity,
    voluntary_order,
)


# ── dependency_index (HHI) ───────────────────────────────────────────────────
def test_hhi_single_dependency_is_one():
    assert dependency_index([1.0]) == 1.0


def test_hhi_diffuse_is_low():
    assert abs(dependency_index([1.0, 1.0, 1.0, 1.0]) - 0.25) < 1e-9


def test_hhi_ignores_nonpositive_and_handles_empty():
    assert dependency_index([]) == 0.0
    assert dependency_index([0.0, -3.0]) == 0.0
    assert abs(dependency_index([3.0, 1.0]) - ((0.75) ** 2 + (0.25) ** 2)) < 1e-9


# ── exit_options ─────────────────────────────────────────────────────────────
def test_exit_options_fraction_viable():
    assert exit_options([1.0, -1.0, 2.0, -0.5]) == 0.5
    assert exit_options([]) == 0.0
    assert exit_options([-1.0, -2.0]) == 0.0
    assert exit_options([0.1, 0.2]) == 1.0


# ── coercion_score: conjunction (geometric mean) ─────────────────────────────
def test_coercion_requires_all_three_factors():
    # any zero factor → no coercion (free exit, or no dependence, or reversible)
    assert coercion_score(0.0, 1.0, 1.0) == 0.0
    assert coercion_score(1.0, 0.0, 1.0) == 0.0
    assert coercion_score(1.0, 1.0, 0.0) == 0.0
    assert coercion_score(1.0, 1.0, 1.0) == 1.0
    mid = coercion_score(0.5, 0.5, 0.5)
    assert abs(mid - 0.5) < 1e-9


def test_coercion_rejects_out_of_range():
    with pytest.raises(ValueError):
        coercion_score(1.5, 0.5, 0.5)
    with pytest.raises(ValueError):
        coercion_score(0.5, -0.1, 0.5)


# ── ownership_clarity (1 - normalized entropy) ───────────────────────────────
def test_clarity_single_clear_owner_is_one():
    assert ownership_clarity([5.0]) == 1.0


def test_clarity_equal_competing_claims_is_zero():
    assert abs(ownership_clarity([1.0, 1.0]) - 0.0) < 1e-9
    assert abs(ownership_clarity([2.0, 2.0, 2.0]) - 0.0) < 1e-9


def test_clarity_skewed_is_high_but_below_one():
    c = ownership_clarity([9.0, 1.0])
    assert 0.0 < c < 1.0
    assert c > 0.5  # one dominant claimant → fairly clear


def test_clarity_no_claims_is_zero():
    assert ownership_clarity([]) == 0.0
    assert ownership_clarity([0.0, -1.0]) == 0.0


# ── voluntary_order ──────────────────────────────────────────────────────────
def test_voluntary_order_nets_coerced():
    assert voluntary_order(3, 0) == 3
    assert voluntary_order(3, 5) == -2  # coerced "contracts" subtract


# ── RED-TEAM: can the estimators be gamed? (honest findings) ─────────────────
def test_attack_hhi_cannot_be_diluted_below_floor_by_padding_zeros():
    # Padding with zero-share counterparties must not fake diffuse dependence:
    # zeros are ignored, so HHI stays at the true concentration.
    assert dependency_index([1.0, 0.0, 0.0, 0.0]) == 1.0


def test_attack_coercion_cannot_be_masked_by_one_low_factor_unless_truly_zero():
    # A tiny but nonzero factor keeps coercion nonzero (no free pass from rounding).
    s = coercion_score(0.99, 0.99, 0.01)
    assert s > 0.0
