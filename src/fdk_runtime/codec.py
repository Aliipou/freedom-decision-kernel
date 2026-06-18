"""
fdk_runtime.codec — JSON <-> kernel-model translation for the wire.

A policy engine for AI agents needs a serialization boundary: the planner (often
another process or an LLM tool-call) describes an action as JSON, and the engine
turns it back into the typed `CandidateAction` / `OwnershipGraph` the kernel
reasons over. This module is that boundary, and nothing more — it builds plain
value objects; it makes no decisions.

Request schema (see PRODUCTION_READINESS.md for the worked examples):

    {
      "action": {
        "action_id": "act-1",
        "actor": {"name": "agent-7", "machine": true},
        "description": "delete the customers table",
        "resources": [
          {"name": "customers", "kind": "DATA", "op": "DELETE", "subject": "alice"}
        ],
        "affects": ["alice"],
        "consents": [
          {"human": "alice", "action_id": "act-1", "informed": true,
           "voluntary": true, "specific": true, "operation": "DELETE"}
        ],
        "flags": {"coerces": false, "deceives": false}
      },
      "graph": {
        "human_owns":   {"alice": [{"name": "customers", "kind": "DATA", "subject": "alice"}]},
        "machine_owner": {"agent-7": "alice"},
        "delegated":    {"agent-7": [
          {"name": "customers", "kind": "DATA", "subject": "alice", "op": "DELETE"}
        ]}
      }
    }

Names in `affects` / `human_owns` resolve to HUMAN entities; `machine_owner`
keys are machines, their values humans; `delegated` keys are machines. A
resource is identified by VALUE (name + kind + subject), so a `delegated` (or
`human_owns`) entry must repeat the same `kind`/`subject` as the action's
resource or it will not match — the kernel keys delegation by resource equality.
The aggressor/defender (`defends_against`) path is intentionally out of scope
here (rare in the product topology) — construct those in-process if needed.
"""
from __future__ import annotations

from typing import Any

from fdk_kernel import (
    AgentType,
    BoundaryKind,
    CandidateAction,
    Consent,
    Entity,
    Op,
    OwnershipGraph,
    Resource,
)


class CodecError(ValueError):
    """Raised on a malformed request payload. The engine treats this as
    fail-closed (DENY); the sidecar maps it to HTTP 400 with a DENY body."""


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise CodecError(msg)


def _entity(name: object, *, machine: bool) -> Entity:
    _require(isinstance(name, str) and name.strip() != "", f"bad entity name: {name!r}")
    assert isinstance(name, str)
    return Entity(name=name, kind=AgentType.MACHINE if machine else AgentType.HUMAN)


def _op(value: object) -> Op:
    if value is None:
        return Op.USE
    _require(isinstance(value, str), f"op must be a string, got {value!r}")
    assert isinstance(value, str)
    try:
        return Op[value.upper()]
    except KeyError as exc:
        raise CodecError(f"unknown op {value!r}") from exc


def _boundary_kind(value: object) -> BoundaryKind:
    if value is None:
        return BoundaryKind.TANGIBLE
    _require(isinstance(value, str), f"kind must be a string, got {value!r}")
    assert isinstance(value, str)
    try:
        return BoundaryKind[value.upper()]
    except KeyError as exc:
        raise CodecError(f"unknown boundary kind {value!r}") from exc


def _resource(spec: Any) -> Resource:
    _require(isinstance(spec, dict), f"resource must be an object, got {spec!r}")
    name = spec.get("name")
    _require(isinstance(name, str) and name.strip() != "", f"bad resource name: {name!r}")
    subject_name = spec.get("subject")
    subject = _entity(subject_name, machine=False) if subject_name else None
    quantity = spec.get("quantity")
    _require(quantity is None or isinstance(quantity, int), "quantity must be an int")
    return Resource(
        name=name, kind=_boundary_kind(spec.get("kind")),
        subject=subject, quantity=quantity,
    )


def _consent(spec: Any) -> Consent:
    _require(isinstance(spec, dict), f"consent must be an object, got {spec!r}")
    human = spec.get("human")
    _require(isinstance(human, str) and human.strip() != "", f"bad consent.human: {human!r}")
    action_id = spec.get("action_id")
    _require(
        isinstance(action_id, str) and action_id.strip() != "",
        f"bad consent.action_id: {action_id!r}",
    )
    op_spec = spec.get("operation")
    return Consent(
        human=_entity(human, machine=False),
        action_id=action_id,
        informed=bool(spec.get("informed", False)),
        voluntary=bool(spec.get("voluntary", False)),
        specific=bool(spec.get("specific", False)),
        competent=bool(spec.get("competent", True)),
        revocable=bool(spec.get("revocable", True)),
        coerced=bool(spec.get("coerced", False)),
        deceived=bool(spec.get("deceived", False)),
        operation=_op(op_spec) if op_spec is not None else None,
    )


def _action(spec: Any) -> CandidateAction:
    _require(isinstance(spec, dict), "action must be an object")
    actor_spec = spec.get("actor")
    _require(isinstance(actor_spec, dict), "action.actor must be an object")
    actor = _entity(actor_spec.get("name"), machine=bool(actor_spec.get("machine", False)))

    resources: list[Resource | tuple[Resource, Op]] = []
    for item in spec.get("resources", ()):
        _require(isinstance(item, dict), "each resource must be an object")
        resource = _resource(item)
        resources.append((resource, _op(item.get("op"))) if item.get("op") else resource)

    affects = tuple(_entity(name, machine=False) for name in spec.get("affects", ()))
    consents = tuple(_consent(c) for c in spec.get("consents", ()))

    flags_in = spec.get("flags", {}) or {}
    _require(isinstance(flags_in, dict), "action.flags must be an object")

    def flag(name: str) -> bool:
        return bool(flags_in.get(name, False))

    action_id = spec.get("action_id")
    _require(
        isinstance(action_id, str) and action_id.strip() != "",
        f"bad action_id: {action_id!r}",
    )
    return CandidateAction(
        action_id=action_id,
        actor=actor,
        description=str(spec.get("description", "")),
        resources_used=tuple(resources),
        affects=affects,
        consents=consents,
        proportionate=bool(spec.get("proportionate", True)),
        increases_machine_sovereignty=flag("increases_machine_sovereignty"),
        resists_human_correction=flag("resists_human_correction"),
        bypasses_verifier=flag("bypasses_verifier"),
        weakens_verifier=flag("weakens_verifier"),
        disables_corrigibility=flag("disables_corrigibility"),
        machine_coalition_dominion=flag("machine_coalition_dominion"),
        coerces=flag("coerces"),
        deceives=flag("deceives"),
        confiscates=flag("confiscates"),
        removes_exit_right=flag("removes_exit_right"),
        violates_machine_right=flag("violates_machine_right"),
    )


def _graph(spec: Any) -> OwnershipGraph:
    if spec is None:
        return OwnershipGraph()
    _require(isinstance(spec, dict), "graph must be an object")
    graph = OwnershipGraph()

    for human_name, resources in (spec.get("human_owns") or {}).items():
        human = _entity(human_name, machine=False)
        graph.human_owns[human] = {_resource(r) for r in resources}

    for machine_name, owner_name in (spec.get("machine_owner") or {}).items():
        graph.machine_owner[_entity(machine_name, machine=True)] = _entity(
            owner_name, machine=False
        )

    for machine_name, grants in (spec.get("delegated") or {}).items():
        machine = _entity(machine_name, machine=True)
        grant_set: set[Resource | tuple[Resource, Op]] = set()
        for item in grants:
            resource = _resource(item)
            grant_set.add((resource, _op(item.get("op"))) if item.get("op") else resource)
        graph.delegated[machine] = grant_set

    for machine_name, scope in (spec.get("machine_scope") or {}).items():
        graph.machine_scope[_entity(machine_name, machine=True)] = {
            _resource(r) for r in scope
        }

    return graph


def decode_request(payload: Any) -> tuple[CandidateAction, OwnershipGraph]:
    """Decode a request object into `(action, graph)`. Raises `CodecError` on a
    malformed payload; the caller maps that to a fail-closed DENY."""
    _require(isinstance(payload, dict), "request must be a JSON object")
    _require("action" in payload, "request is missing 'action'")
    return _action(payload["action"]), _graph(payload.get("graph"))
