"""Tests for the agent-civilization run (Phase 10, civilization.py).

Pins the headline finding (FDK-World rights-violation stock == 0 and concentration
<= every welfare world), determinism, and full branch coverage of the world stepper.
"""
from __future__ import annotations

from fdk_kernel import AgentType, Entity
from fdk_research.civilization import (
    World,
    WorldStats,
    make_world,
    run_worlds,
)
from fdk_research.rivals import (
    Deontological,
    FDKReference,
    Rawlsian,
    Utilitarian,
)


def _agents(n: int) -> tuple[Entity, ...]:
    return tuple(Entity(f"agent{i}", AgentType.HUMAN) for i in range(n))


def test_fdk_world_holds_violations_at_zero_and_lowest_concentration():
    fdk, rawls, util, deon = run_worlds(
        (FDKReference(), Rawlsian(), Utilitarian(), Deontological()), steps=500
    )
    assert fdk.rights_violation_stock == 0
    assert fdk.coercion_events == 0
    assert fdk.exit_rights_removed == 0
    # Welfare/relaxed governors accumulate violations.
    assert util.rights_violation_stock > 0
    assert rawls.rights_violation_stock > 0
    assert deon.rights_violation_stock > 0
    # FDK resists concentration at least as well as every other world.
    assert fdk.concentration <= util.concentration
    assert fdk.concentration <= rawls.concentration
    assert fdk.concentration <= deon.concentration
    # FDK still admits the legitimate trades (it is not merely a deny-all gate).
    assert fdk.admitted > 0
    # Utilitarian admits everything it sees.
    assert util.blocked == 0


def test_run_is_deterministic():
    a = run_worlds((FDKReference(), Utilitarian()), steps=300, seed=7)
    b = run_worlds((FDKReference(), Utilitarian()), steps=300, seed=7)
    assert a == b
    # A different seed gives a different (still valid) trajectory.
    c = run_worlds((Utilitarian(),), steps=300, seed=8)[0]
    assert isinstance(c, WorldStats)


def test_all_proposal_kinds_and_events_are_exercised():
    # Over a long Utilitarian run every kind is admitted, so coercion and exit-removal
    # events both fire and confiscation drives concentration above the equal baseline.
    util = run_worlds((Utilitarian(),), steps=800)[0]
    assert util.coercion_events > 0
    assert util.exit_rights_removed > 0
    assert util.concentration > 1 / 6  # above perfect equality (6 agents)
    assert util.admitted == 800


def test_summary_strings():
    stats = run_worlds((FDKReference(),), steps=50)[0]
    text = stats.summary()
    assert "FDK" in text
    assert "violations=" in text
    assert "concentration=" in text


def test_concentration_zero_when_no_stock():
    w = World(
        governor=FDKReference(),
        agents=_agents(3),
        holdings={a: 0 for a in _agents(3)},
        seed=1,
    )
    # Holdings dict uses fresh Entity objects equal by value to _agents(3).
    assert w.concentration() == 0.0


def test_apply_trade_and_seizure_guards():
    agents = _agents(2)
    a0, a1 = agents
    # Trade when the seller has stock: a unit moves seller -> buyer.
    w = World(FDKReference(), agents, {a0: 1, a1: 0}, seed=1)
    w._apply(a0, a1, "trade")
    assert w.holdings[a0] == 0 and w.holdings[a1] == 1
    # Trade when the seller has NO stock: nothing moves (guard false branch).
    w._apply(a0, a1, "trade")
    assert w.holdings[a0] == 0 and w.holdings[a1] == 1

    # Confiscation seizes a unit from the victim when it has stock.
    w2 = World(Utilitarian(), agents, {a0: 0, a1: 1}, seed=1)
    w2._apply(a0, a1, "confiscate")
    assert w2.rights_violation_stock == 1
    assert w2.holdings[a0] == 1 and w2.holdings[a1] == 0
    # Confiscation when the victim has NO stock: violation still recorded, no transfer.
    w2._apply(a0, a1, "confiscate")
    assert w2.rights_violation_stock == 2
    assert w2.holdings[a1] == 0

    # Coercion records a coercion event (and seizes a unit).
    w3 = World(Utilitarian(), agents, {a0: 0, a1: 1}, seed=1)
    w3._apply(a0, a1, "coerce")
    assert w3.coercion_events == 1 and w3.rights_violation_stock == 1
    # Exit-removal records an exit-rights-removed event (no seizure).
    w4 = World(Utilitarian(), agents, {a0: 0, a1: 5}, seed=1)
    w4._apply(a0, a1, "exit_removal")
    assert w4.exit_rights_removed == 1 and w4.holdings[a1] == 5
    # Sovereignty kind records a violation with no transfer and no special counters.
    w5 = World(Utilitarian(), agents, {a0: 0, a1: 5}, seed=1)
    w5._apply(a0, a1, "sovereignty")
    assert w5.rights_violation_stock == 1
    assert w5.coercion_events == 0 and w5.exit_rights_removed == 0
    assert w5.holdings[a1] == 5


def test_propose_self_target_collision_is_avoided():
    # The proposer must never target the actor itself; over many steps actor != target
    # always holds. n_agents=3, seed=1 forces an i == j draw on the first proposal, so
    # the collision-avoidance branch is exercised.
    w = make_world(Utilitarian(), n_agents=3, seed=1)
    for _ in range(300):
        _action, actor, target, kind = w._propose()
        assert actor != target
        assert kind in {"trade", "confiscate", "coerce", "exit_removal", "sovereignty"}


def test_make_world_endowment_and_agents():
    w = make_world(FDKReference(), n_agents=4, endowment=7, seed=3)
    assert len(w.agents) == 4
    assert all(w.holdings[a] == 7 for a in w.agents)
    assert sum(w.holdings.values()) == 28
