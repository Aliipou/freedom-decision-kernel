"""
Tests for the lock-in risk scorer (fdk_research.lockin) — the Reversibility
Intelligence apparatus. These pin the computation and the band thresholds; they do
NOT claim the score is validated (that is the migration-outcome fieldwork).
"""
from __future__ import annotations

import pytest

from fdk_research.lockin import Dependency, LockinProfile, lockin_risk, marginal_lockin


def test_open_standard_dependency_is_low_risk():
    dep = Dependency("postgres", switching_cost=0.1, portability=0.9, alternatives=5)
    p = lockin_risk([dep])
    assert p.band == "LOW"
    assert p.lockin_risk < 1.0 / 3.0
    assert p.worst_dependency == "postgres"


def test_proprietary_sole_source_is_high_risk():
    dep = Dependency("vendor-x", switching_cost=0.95, portability=0.05, alternatives=0)
    p = lockin_risk([dep])
    assert p.band == "HIGH"
    assert p.lockin_risk > 2.0 / 3.0


def test_medium_band_in_the_middle():
    dep = Dependency("mid", switching_cost=0.5, portability=0.5, alternatives=1)
    p = lockin_risk([dep])
    assert p.band == "MEDIUM"


def test_no_dependencies_is_zero_risk():
    p = lockin_risk([])
    assert p == LockinProfile(0.0, 0.0, "", "LOW", {})


def test_weighted_mean_lets_a_heavy_dependency_dominate():
    light_open = Dependency("open", weight=0.1, switching_cost=0.0, portability=1.0, alternatives=5)
    heavy_locked = Dependency("locked", weight=0.9, switching_cost=1.0, portability=0.0, alternatives=0)
    p = lockin_risk([light_open, heavy_locked])
    assert p.band == "HIGH"
    assert p.worst_dependency == "locked"


def test_zero_weights_fall_back_to_equal_weights():
    a = Dependency("a", weight=0.0, switching_cost=0.0, portability=1.0, alternatives=5)
    b = Dependency("b", weight=0.0, switching_cost=1.0, portability=0.0, alternatives=0)
    p = lockin_risk([a, b])
    # equal-weight mean of a (low) and b (high) -> around the middle
    assert 0.2 < p.lockin_risk < 0.8


def test_concentration_reported_via_hhi():
    deps = [Dependency("only", weight=1.0)]
    assert lockin_risk(deps).concentration == 1.0  # single dependency = total concentration


@pytest.mark.parametrize("alternatives", [0, 1, 2, 4])
def test_alternatives_raise_escapability(alternatives):
    base = Dependency("d", switching_cost=0.0, portability=1.0, alternatives=0).escapability()
    more = Dependency("d", switching_cost=0.0, portability=1.0, alternatives=alternatives).escapability()
    assert more >= base


def test_to_dict_exposes_components():
    d = lockin_risk([Dependency("x")]).to_dict()
    assert set(d) == {"lockin_risk", "concentration", "worst_dependency", "band", "per_dependency"}


@pytest.mark.parametrize("field,value", [
    ("weight", 1.5), ("switching_cost", -0.1), ("portability", 2.0),
])
def test_out_of_range_fields_raise(field, value):
    with pytest.raises(ValueError, match="must be in"):
        Dependency("d", **{field: value})


def test_negative_alternatives_raises():
    with pytest.raises(ValueError, match="alternatives must be"):
        Dependency("d", alternatives=-1)


def test_marginal_lockin_is_higher_for_a_proprietary_choice():
    portfolio = [Dependency("postgres", switching_cost=0.2, portability=0.9, alternatives=5)]
    proprietary = Dependency("dynamodb", switching_cost=0.9, portability=0.1, alternatives=0)
    portable = Dependency("redis-oss", switching_cost=0.2, portability=0.9, alternatives=4)
    assert marginal_lockin(portfolio, proprietary) > marginal_lockin(portfolio, portable)


def test_marginal_lockin_into_empty_portfolio_is_the_decisions_own_risk():
    decision = Dependency("vendor-x", switching_cost=0.9, portability=0.1, alternatives=0)
    delta = marginal_lockin([], decision)
    assert delta == lockin_risk([decision]).lockin_risk


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
