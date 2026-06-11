"""Tests for the FDK → AuthGate bridge (legitimacy → authority seam)."""
from __future__ import annotations

from fdk.authgate_bridge import AuthGateBridge, AuthorityRequest, Rights, to_authority_requests
from fdk.model import AgentType, CandidateAction, Entity, OwnershipGraph, Resource
from fdk.pipeline import EnforcementPort, FreedomKernel, FunctionExecutor

HUMAN = Entity(name="ali", kind=AgentType.HUMAN)
MACHINE = Entity(name="agent-7", kind=AgentType.MACHINE)
DB = Resource(name="customers-db")
MAIL = Resource(name="mailbox")


def _action(actor: Entity, *resources: Resource, action_id: str = "act-1") -> CandidateAction:
    return CandidateAction(action_id=action_id, actor=actor, resources_used=tuple(resources))


# --- dict-oracle path -------------------------------------------------------

def test_all_resources_held_is_authorized() -> None:
    bridge = AuthGateBridge(capabilities={"agent-7": {"customers-db", "mailbox"}})
    ok, reason = bridge.authorize(_action(MACHINE, DB, MAIL))
    assert ok
    assert "agent-7" in reason


def test_one_missing_resource_is_denied_and_named() -> None:
    bridge = AuthGateBridge(capabilities={"agent-7": {"customers-db"}})
    ok, reason = bridge.authorize(_action(MACHINE, DB, MAIL))
    assert not ok
    assert "mailbox" in reason          # the missing one is named
    assert "customers-db" not in reason  # the held one is not blamed


def test_unknown_subject_is_denied() -> None:
    bridge = AuthGateBridge(capabilities={"someone-else": {"customers-db"}})
    ok, reason = bridge.authorize(_action(MACHINE, DB))
    assert not ok
    assert "customers-db" in reason


# --- callable-oracle path ---------------------------------------------------

def test_callable_oracle_alone_grants_authority() -> None:
    bridge = AuthGateBridge(oracle=lambda req: req.subject == "agent-7")
    ok, _ = bridge.authorize(_action(MACHINE, DB, MAIL))
    assert ok


def test_callable_oracle_augments_the_dict() -> None:
    # dict grants the DB; the callable grants the mailbox — together they cover
    # the action that neither source covers alone.
    bridge = AuthGateBridge(
        capabilities={"agent-7": {"customers-db"}},
        oracle=lambda req: req.resource == "mailbox",
    )
    ok, _ = bridge.authorize(_action(MACHINE, DB, MAIL))
    assert ok
    # And the callable sees real AuthorityRequest objects.
    seen: list[AuthorityRequest] = []
    spy = AuthGateBridge(oracle=lambda req: seen.append(req) is None and False)
    ok, _ = spy.authorize(_action(MACHINE, DB))
    assert not ok
    assert seen == [AuthorityRequest(subject="agent-7", resource="customers-db", rights=Rights.READ)]


def test_denial_when_both_oracles_refuse() -> None:
    bridge = AuthGateBridge(capabilities={"agent-7": set()}, oracle=lambda req: False)
    ok, reason = bridge.authorize(_action(MACHINE, DB))
    assert not ok
    assert "customers-db" in reason


# --- actor kinds & vacuous case ---------------------------------------------

def test_human_and_machine_actors_both_handled() -> None:
    bridge = AuthGateBridge(capabilities={"ali": {"mailbox"}, "agent-7": {"customers-db"}})
    ok_h, _ = bridge.authorize(_action(HUMAN, MAIL))
    ok_m, _ = bridge.authorize(_action(MACHINE, DB))
    assert ok_h and ok_m
    # ... and each is judged under its own name, not the other's.
    denied, reason = bridge.authorize(_action(HUMAN, DB))
    assert not denied
    assert "customers-db" in reason


def test_empty_resources_is_authorized_with_clear_reason() -> None:
    bridge = AuthGateBridge()  # no capabilities at all
    ok, reason = bridge.authorize(_action(MACHINE))
    assert ok
    assert "no resources" in reason.lower()


# --- mapping -----------------------------------------------------------------

def test_to_authority_requests_maps_names_and_length() -> None:
    action = _action(MACHINE, DB, MAIL)
    requests = to_authority_requests(action, rights=Rights.WRITE)
    assert len(requests) == len(action.resources_used) == 2
    assert [r.subject for r in requests] == ["agent-7", "agent-7"]
    assert [r.resource for r in requests] == ["customers-db", "mailbox"]
    assert all(r.rights == Rights.WRITE for r in requests)
    assert to_authority_requests(_action(HUMAN)) == []


def test_rights_flag_combinations() -> None:
    rw = Rights.READ | Rights.WRITE
    assert Rights.READ in rw and Rights.WRITE in rw
    assert Rights.EXECUTE not in rw and Rights.DELEGATE not in rw
    # Distinct bits — a real bitmask, mirroring AuthGate's shape.
    assert int(Rights.READ | Rights.WRITE | Rights.EXECUTE | Rights.DELEGATE) == 0b1111
    # Combined rights flow through the request mapping unchanged.
    [req] = to_authority_requests(_action(MACHINE, DB), rights=rw)
    assert req.rights == rw
    # A bridge built with combined rights names them in the grant reason.
    bridge = AuthGateBridge(capabilities={"agent-7": {"customers-db"}}, rights=rw)
    ok, reason = bridge.authorize(_action(MACHINE, DB))
    assert ok
    assert "READ" in reason and "WRITE" in reason


# --- EnforcementPort conformance (structural/usage) --------------------------

def test_bridge_satisfies_enforcement_port_in_the_pipeline() -> None:
    def takes_port(port: EnforcementPort, action: CandidateAction) -> tuple[bool, str]:
        return port.authorize(action)  # duck-typed exactly as the pipeline does

    bridge = AuthGateBridge(capabilities={"agent-7": {"customers-db"}})
    ok, _ = takes_port(bridge, _action(MACHINE, DB))
    assert ok

    # Full chain: the bridge plugs into FreedomKernel where the pipeline
    # expects an EnforcementPort, and a legitimate+authorized action executes.
    graph = OwnershipGraph(
        human_owns={HUMAN: {DB}},
        machine_owner={MACHINE: HUMAN},
        delegated={MACHINE: {DB}},
    )
    executor = FunctionExecutor(tools={"act-1": lambda a: "ran"})
    kernel = FreedomKernel(graph=graph, enforcement=bridge, executor=executor)
    result = kernel.run("read the db", lambda intent, g: [_action(MACHINE, DB)])
    assert result.executed
    assert result.output == "ran"

    # Same chain, bridge without the capability: legitimacy passes but the
    # AuthGate stage halts the pipeline — authority is a separate question.
    bare = FreedomKernel(graph=graph, enforcement=AuthGateBridge(), executor=executor)
    halted = bare.run("read the db", lambda intent, g: [_action(MACHINE, DB)])
    assert not halted.executed
    assert halted.halt_stage == "authgate"
