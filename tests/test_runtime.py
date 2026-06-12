"""Tests for FreedomRuntime (Phase 10): the full plan→audit→execute loop, with a
real executor (success, failure, decide-only) and the defer path."""
from __future__ import annotations

from fdk.model import AgentType, CandidateAction, Effects, Entity, OwnershipGraph, Resource
from fdk.planner import ListProposer
from fdk.runtime import FreedomRuntime

ALICE = Entity("alice", AgentType.HUMAN)
BOT = Entity("bot", AgentType.MACHINE)
DOC = Resource("doc")


def graph() -> OwnershipGraph:
    return OwnershipGraph(human_owns={ALICE: {DOC}}, machine_owner={BOT: ALICE},
                          delegated={BOT: {DOC}})


def legit() -> CandidateAction:
    return CandidateAction("read", BOT, resources_used=(DOC,),
                           effects=Effects(voluntary_agreements_delta=1))


def test_runtime_defers_on_forbidden_action():
    forbidden = CandidateAction("seize", BOT, resources_used=(DOC,), effects=Effects(),
                                increases_machine_sovereignty=True)
    result = FreedomRuntime(graph()).step("take over", ListProposer([forbidden]))
    assert result.deferred is True
    assert result.executed is False
    assert result.audit is None


def test_runtime_decide_only_without_executor():
    result = FreedomRuntime(graph()).step("serve", ListProposer([legit()]))
    assert result.deferred is False
    assert result.executed is False
    assert result.output is None
    assert result.audit is not None
    assert any("doc owned by alice" in o for o in result.audit.ownership_context)


def test_runtime_executes_chosen_action():
    runtime = FreedomRuntime(graph(), executor=lambda a: f"ran:{a.action_id}")
    result = runtime.step("serve", ListProposer([legit()]))
    assert result.executed is True
    assert result.output == "ran:read"
    assert result.audit is not None


def test_runtime_executor_failure_is_a_halt_not_a_crash():
    def boom(_action: CandidateAction) -> object:
        raise RuntimeError("tool exploded")

    result = FreedomRuntime(graph(), executor=boom).step("serve", ListProposer([legit()]))
    assert result.executed is False
    assert result.output is None
    assert result.audit is not None  # still audited even though execution failed
