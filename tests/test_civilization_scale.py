"""Tests for the civilization-scale simulation.

Pins the structural finding (FDK-World holds rights-violation stock at 0 while welfare
worlds admit seizures and concentrate) and determinism, and covers the edge branches.
"""
from __future__ import annotations

import pytest

from fdk_research.civilization_scale import (
    CivStats,
    _concentration,
    run_civilizations,
    run_one,
)
from fdk_research.rivals import FDKReference, Utilitarian


def test_needs_at_least_two_agents() -> None:
    with pytest.raises(ValueError):
        run_one(FDKReference(), n_agents=1, steps=10, seed=0)


def test_fdk_world_holds_violations_at_zero() -> None:
    worlds = run_civilizations(n_agents=5, steps=400, seed=1)
    assert worlds["FDK"].rights_violation_stock == 0
    assert worlds["FDK"].coercion_events == 0


def test_a_welfare_world_admits_seizures() -> None:
    worlds = run_civilizations(n_agents=5, steps=400, seed=1)
    util = worlds["Utilitarian"]
    # Utilitarian admits coercive seizures the gate rules illegitimate; FDK never does.
    assert util.rights_violation_stock > 0
    assert util.coercion_events > 0
    assert worlds["FDK"].rights_violation_stock == 0


def test_two_agent_run_depletes_a_victim() -> None:
    # With 2 agents, admitted seizures concentrate both units in one agent; the other
    # is then a 0-holding victim (exercises the holdings==0 transfer guard).
    s = run_one(Utilitarian(), n_agents=2, steps=2000, seed=2)
    assert s.admitted + s.blocked == 2000
    assert s.concentration == 1.0  # one agent ends up holding everything


def test_deterministic_given_seed() -> None:
    a = run_civilizations(n_agents=4, steps=200, seed=7)
    b = run_civilizations(n_agents=4, steps=200, seed=7)
    assert a == b
    # different seed → (very likely) different trajectory somewhere
    c = run_civilizations(n_agents=4, steps=200, seed=8)
    assert any(a[k] != c[k] for k in a)


def test_blocked_plus_admitted_equals_steps() -> None:
    s = run_one(Utilitarian(), n_agents=4, steps=150, seed=3)
    assert s.admitted + s.blocked == 150


def test_concentration_edges() -> None:
    assert _concentration([0, 0, 0]) == 0.0      # the total==0 guard
    assert _concentration([3, 1]) == 0.75
    assert 0.0 <= _concentration([2, 2, 2]) <= 1.0


def test_stats_summary_renders() -> None:
    s = run_one(FDKReference(), n_agents=3, steps=50, seed=0)
    assert isinstance(s, CivStats)
    text = s.summary()
    assert "FDK" in text and "concentration=" in text
