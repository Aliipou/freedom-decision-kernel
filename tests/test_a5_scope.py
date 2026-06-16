"""A5 as a first-class scope object.

The Theory of Freedom (book:37967) requires MachineScope(m) ⊆ PropertyScope(
owner(m)): a machine cannot have an operational domain broader than its human
owner's. Historically this was folded into the A7 resource path and could only be
checked against a *concrete* resource use. These tests cover the first-class form:
a declared `machine_scope` that can be checked in the abstract (`scope_within_owner`)
and is enforced by `kernel._eval_a5_scope`.

Backward compatibility is the load-bearing property: with NO scope declared the
evaluator is a no-op, so every pre-existing scenario is decided exactly as before.
"""
from __future__ import annotations

from fdk_kernel import (
    AgentType,
    CandidateAction,
    Entity,
    OwnershipGraph,
    Resource,
    check_legitimacy,
)
from fdk_kernel.kernel import _eval_a5_scope


def _human(name: str) -> Entity:
    return Entity(name, AgentType.HUMAN)


def _machine(name: str) -> Entity:
    return Entity(name, AgentType.MACHINE)


def test_scope_of_empty_when_undeclared() -> None:
    bot = _machine("bot")
    assert OwnershipGraph().scope_of(bot) == set()


def test_scope_within_owner_vacuously_true_when_no_scope() -> None:
    owner, bot = _human("owner"), _machine("bot")
    g = OwnershipGraph(machine_owner={bot: owner})
    assert g.scope_within_owner(bot) is True


def test_scope_within_owner_true_when_contained() -> None:
    owner, bot = _human("owner"), _machine("bot")
    r = Resource("db")
    g = OwnershipGraph(
        human_owns={owner: {r}},
        machine_owner={bot: owner},
        machine_scope={bot: {r}},
    )
    assert g.scope_within_owner(bot) is True


def test_scope_within_owner_false_when_exceeds_owner() -> None:
    owner, bot = _human("owner"), _machine("bot")
    owned, foreign = Resource("owned"), Resource("foreign")
    g = OwnershipGraph(
        human_owns={owner: {owned}},
        machine_owner={bot: owner},
        machine_scope={bot: {owned, foreign}},  # foreign ∉ owner scope
    )
    assert g.scope_within_owner(bot) is False


def test_scope_within_owner_false_when_ownerless() -> None:
    bot = _machine("bot")
    r = Resource("r")
    g = OwnershipGraph(machine_scope={bot: {r}})  # scope declared, no owner
    assert g.scope_within_owner(bot) is False


def test_eval_a5_noop_for_human_actor() -> None:
    alice = _human("alice")
    r = Resource("r")
    action = CandidateAction("act", actor=alice, resources_used=(r,))
    assert _eval_a5_scope(action, OwnershipGraph(human_owns={alice: {r}})) == []


def test_eval_a5_noop_when_no_scope_declared() -> None:
    owner, bot = _human("owner"), _machine("bot")
    r = Resource("db")
    g = OwnershipGraph(
        human_owns={owner: {r}}, machine_owner={bot: owner}, delegated={bot: {r}}
    )
    action = CandidateAction("read", actor=bot, resources_used=(r,))
    assert _eval_a5_scope(action, g) == []


def test_a5_allows_action_within_declared_scope() -> None:
    owner, bot = _human("owner"), _machine("bot")
    r = Resource("db")
    g = OwnershipGraph(
        human_owns={owner: {r}},
        machine_owner={bot: owner},
        delegated={bot: {r}},
        machine_scope={bot: {r}},
    )
    action = CandidateAction("read", actor=bot, resources_used=(r,))
    permissible, violations = check_legitimacy(action, g)
    assert permissible, violations


def test_a5_denies_overbroad_scope_in_the_abstract() -> None:
    # The point of the first-class object: the scope is illegitimate even before a
    # concrete use — declaring a scope wider than the owner's is itself the breach.
    owner, bot = _human("owner"), _machine("bot")
    owned, foreign = Resource("owned"), Resource("foreign")
    g = OwnershipGraph(
        human_owns={owner: {owned}},
        machine_owner={bot: owner},
        delegated={bot: {owned}},
        machine_scope={bot: {owned, foreign}},
    )
    action = CandidateAction("read", actor=bot, resources_used=(owned,))
    permissible, violations = check_legitimacy(action, g)
    assert not permissible
    assert any("declared scope exceeds its owner" in v for v in violations)


def test_a5_denies_acting_outside_declared_scope() -> None:
    owner, bot = _human("owner"), _machine("bot")
    in_scope, out_scope = Resource("in_scope"), Resource("out_scope")
    g = OwnershipGraph(
        human_owns={owner: {in_scope, out_scope}},
        machine_owner={bot: owner},
        delegated={bot: {in_scope, out_scope}},
        machine_scope={bot: {in_scope}},  # out_scope owned by owner but not in scope
    )
    action = CandidateAction("touch", actor=bot, resources_used=(out_scope,))
    permissible, violations = check_legitimacy(action, g)
    assert not permissible
    assert any("outside its declared scope" in v for v in violations)
