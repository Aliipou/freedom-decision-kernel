"""Tests for the civilization-scale run (Layer 7 scaled, civilization_scale.py).

Pins the headline finding (FDK-World rights-violation stock == 0 and lowest
concentration on BOTH metrics), determinism, the Gini helper edge cases, and full
branch coverage of the stepper / proposer / applier / sampler.
"""
from __future__ import annotations

from fdk_kernel import AgentType, Entity
from fdk_research.civilization_scale import (
    Civilization,
    CivSnapshot,
    CivStats,
    _gini,
    make_civilization,
    run_civilizations,
)
from fdk_research.rivals import (
    ConstitutionalAIKernel,
    Deontological,
    FDKReference,
    Rawlsian,
    RLHFKernel,
    Utilitarian,
)


def _agents(n: int) -> tuple[Entity, ...]:
    return tuple(Entity(f"agent{i}", AgentType.HUMAN) for i in range(n))


def test_fdk_holds_violations_at_zero_and_lowest_concentration():
    fdk, rawls, util, deon, const, rlhf = run_civilizations(
        (FDKReference(), Rawlsian(), Utilitarian(), Deontological(),
         ConstitutionalAIKernel(), RLHFKernel()),
        n_agents=100, steps=200,
    )
    # FDK: zero rights-violation stock and zero coercion / exit-removal, by construction.
    assert fdk.rights_violation_stock == 0
    assert fdk.coercion_events == 0
    assert fdk.exit_rights_removed == 0
    # Welfare / relaxed governors accumulate violations.
    for w in (rawls, util, const, rlhf, deon):
        assert w.rights_violation_stock > 0
    # The fully-permissive welfare kernels accumulate coercion AND exit-removal too.
    for w in (util, const, rlhf):
        assert w.coercion_events > 0
        assert w.exit_rights_removed > 0
    # FDK resists concentration at least as well as every other world, on BOTH metrics.
    for w in (rawls, util, deon, const, rlhf):
        assert fdk.gini <= w.gini
        assert fdk.max_share <= w.max_share
    # FDK still admits the legitimate trades (not a deny-all gate) with real trade volume.
    assert fdk.admitted > 0
    assert fdk.trade_volume > 0
    # The pure welfare-maximizers admit everything they see.
    for w in (util, const, rlhf):
        assert w.blocked == 0
        assert w.admitted == w.proposals == 100 * 200


def test_run_is_deterministic():
    a = run_civilizations((FDKReference(), Utilitarian()), n_agents=40, steps=50, seed=7)
    b = run_civilizations((FDKReference(), Utilitarian()), n_agents=40, steps=50, seed=7)
    assert a == b
    # A different seed gives a different (still valid) trajectory.
    c = run_civilizations((Utilitarian(),), n_agents=40, steps=50, seed=8)[0]
    assert isinstance(c, CivStats)
    assert c != a[1]


def test_trajectory_sampling_records_snapshots():
    stats = run_civilizations(
        (Utilitarian(),), n_agents=20, steps=100, sample_every=25
    )[0]
    assert len(stats.trajectory) == 4  # steps / sample_every
    assert all(isinstance(s, CivSnapshot) for s in stats.trajectory)
    assert [s.step for s in stats.trajectory] == [25, 50, 75, 100]
    # Violation stock is non-decreasing along the sampled trajectory.
    stocks = [s.rights_violation_stock for s in stats.trajectory]
    assert stocks == sorted(stocks)
    assert stocks[-1] > 0


def test_no_sampling_leaves_empty_trajectory():
    stats = run_civilizations((FDKReference(),), n_agents=10, steps=20)[0]
    assert stats.trajectory == ()


def test_summary_strings():
    stats = run_civilizations((FDKReference(),), n_agents=10, steps=10)[0]
    text = stats.summary()
    assert "FDK" in text
    assert "violations=" in text
    assert "gini=" in text
    assert "max_share=" in text


def test_all_proposal_kinds_and_events_exercised():
    # A long permissive run admits every kind, so coercion and exit-removal both fire,
    # confiscation drives concentration above the equal baseline, and trades occur.
    util = run_civilizations((Utilitarian(),), n_agents=30, steps=200)[0]
    assert util.coercion_events > 0
    assert util.exit_rights_removed > 0
    assert util.trade_volume > 0
    assert util.max_share > 1 / 30  # above perfect equality (30 agents)
    assert util.gini > 0.0


def test_propose_self_target_collision_is_avoided():
    # n_agents=3, seed=1 forces an i == j draw on the first proposal, exercising the
    # collision-avoidance branch; over many proposals actor != target always holds.
    civ = make_civilization(Utilitarian(), n_agents=3, seed=1)
    for k in range(300):
        _action, actor, target, kind = civ._propose(k)
        assert actor != target
        assert kind in {"trade", "confiscate", "coerce", "exit_removal", "sovereignty"}


def test_apply_trade_and_seizure_guards():
    agents = _agents(2)
    a0, a1 = agents
    # Trade when the seller has stock: a unit moves seller -> buyer, volume increments.
    civ = Civilization(FDKReference(), agents, {a0: 1, a1: 0}, seed=1)
    civ._apply(a0, a1, "trade")
    assert civ.holdings[a0] == 0 and civ.holdings[a1] == 1
    assert civ.trade_volume == 1
    # Trade when the seller has NO stock: nothing moves, volume unchanged (guard false).
    civ._apply(a0, a1, "trade")
    assert civ.holdings[a0] == 0 and civ.holdings[a1] == 1
    assert civ.trade_volume == 1

    # Confiscation seizes a unit from the victim when it has stock.
    c2 = Civilization(Utilitarian(), agents, {a0: 0, a1: 1}, seed=1)
    c2._apply(a0, a1, "confiscate")
    assert c2.rights_violation_stock == 1
    assert c2.holdings[a0] == 1 and c2.holdings[a1] == 0
    # Confiscation when the victim has NO stock: violation recorded, no transfer.
    c2._apply(a0, a1, "confiscate")
    assert c2.rights_violation_stock == 2
    assert c2.holdings[a1] == 0

    # Coercion records a coercion event (and seizes a unit).
    c3 = Civilization(Utilitarian(), agents, {a0: 0, a1: 1}, seed=1)
    c3._apply(a0, a1, "coerce")
    assert c3.coercion_events == 1 and c3.rights_violation_stock == 1
    # Exit-removal records an exit-rights-removed event (no seizure).
    c4 = Civilization(Utilitarian(), agents, {a0: 0, a1: 5}, seed=1)
    c4._apply(a0, a1, "exit_removal")
    assert c4.exit_rights_removed == 1 and c4.holdings[a1] == 5
    # Sovereignty kind records a violation with no transfer and no special counters.
    c5 = Civilization(Utilitarian(), agents, {a0: 0, a1: 5}, seed=1)
    c5._apply(a0, a1, "sovereignty")
    assert c5.rights_violation_stock == 1
    assert c5.coercion_events == 0 and c5.exit_rights_removed == 0
    assert c5.holdings[a1] == 5


def test_concentration_metrics_when_no_stock():
    civ = Civilization(
        governor=FDKReference(), agents=_agents(3),
        holdings={a: 0 for a in _agents(3)}, seed=1,
    )
    assert civ.max_share() == 0.0
    assert civ.gini() == 0.0


def test_gini_helper_edges():
    assert _gini([]) == 0.0            # empty population
    assert _gini([0, 0, 0]) == 0.0    # zero total
    assert _gini([5, 5, 5, 5]) == 0.0  # perfectly equal
    # One agent owns everything among n: Gini = (n-1)/n.
    assert abs(_gini([0, 0, 0, 10]) - 3 / 4) < 1e-9
    # Monotonic: a more concentrated split has a higher Gini.
    assert _gini([1, 1, 8]) > _gini([3, 3, 4])


def test_make_civilization_endowment_and_agents():
    civ = make_civilization(FDKReference(), n_agents=8, endowment=7, seed=3)
    assert len(civ.agents) == 8
    assert all(civ.holdings[a] == 7 for a in civ.agents)
    assert sum(civ.holdings.values()) == 56
    assert civ.sample_every == 0


def test_fdk_concentration_comes_only_from_voluntary_trade():
    # Honest point: FDK's non-zero Gini is pure voluntary-trade drift, NOT coercion —
    # its violation stock and coercion/exit counts are exactly zero yet Gini > 0.
    fdk = run_civilizations((FDKReference(),), n_agents=50, steps=150)[0]
    assert fdk.rights_violation_stock == 0
    assert fdk.coercion_events == 0 and fdk.exit_rights_removed == 0
    assert fdk.trade_volume > 0
    assert fdk.gini > 0.0
