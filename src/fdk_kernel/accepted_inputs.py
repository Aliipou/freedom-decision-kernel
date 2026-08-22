"""Extract accepted kernel inputs from action + graph (M2).

Records what the kernel ASSUMED — not verified world truth.
asserted_by names the input channel, not a truth guarantee.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fdk_kernel.kernel import _FORBIDDEN_RULES
from fdk_kernel.model import CandidateAction, Consent, OwnershipGraph, Op

INPUT_CALLER_FLAG = "CALLER_FLAG"
INPUT_TYPED_FACT = "TYPED_FACT"
INPUT_GRAPH_FACT = "GRAPH_FACT"


@dataclass(frozen=True, slots=True)
class AcceptedInput:
    fact_key: str
    fact_value: Any
    asserted_by: str
    input_class: str

    def as_tuple(self) -> tuple[str, Any, str, str]:
        return (self.fact_key, self.fact_value, self.asserted_by, self.input_class)


def collect_accepted_inputs(
    action: CandidateAction,
    graph: OwnershipGraph,
) -> tuple[AcceptedInput, ...]:
    """Deterministic bundle of inputs the kernel treated as given."""
    items: list[AcceptedInput] = []

    items.append(AcceptedInput(
        "actor.kind",
        action.actor.kind.name,
        "proposer",
        INPUT_TYPED_FACT,
    ))
    items.append(AcceptedInput(
        "actor.name",
        action.actor.name,
        "proposer",
        INPUT_TYPED_FACT,
    ))

    for attr, _rule, _axiom, _label in _FORBIDDEN_RULES:
        items.append(AcceptedInput(
            attr,
            getattr(action, attr),
            "proposer",
            INPUT_CALLER_FLAG,
        ))

    if action.actor.is_machine():
        owner = graph.owner_of(action.actor)
        items.append(AcceptedInput(
            "machine.owner",
            owner.name if owner else None,
            "ownership_graph",
            INPUT_GRAPH_FACT,
        ))
        scope = graph.scope_of(action.actor)
        if scope:
            items.append(AcceptedInput(
                "machine.declared_scope",
                sorted(r.name for r in scope),
                "ownership_graph",
                INPUT_GRAPH_FACT,
            ))

    for resource, op in action.uses():
        items.append(AcceptedInput(
            f"resource_use.{resource.name}",
            op.name,
            "proposer",
            INPUT_TYPED_FACT,
        ))
        if action.actor.is_machine():
            items.append(AcceptedInput(
                f"delegation.{resource.name}.{op.name}",
                graph.machine_has_delegated(action.actor, resource, op),
                "ownership_graph",
                INPUT_GRAPH_FACT,
            ))
        if action.actor.is_human():
            items.append(AcceptedInput(
                f"human_owns.{resource.name}",
                graph.human_owns_resource(action.actor, resource),
                "ownership_graph",
                INPUT_GRAPH_FACT,
            ))

    for entity in action.affects:
        items.append(AcceptedInput(
            f"affects.{entity.name}",
            entity.kind.name,
            "proposer",
            INPUT_TYPED_FACT,
        ))

    for consent in action.consents:
        items.extend(_consent_inputs(consent))

    items.sort(key=lambda i: (i.fact_key, str(i.fact_value)))
    return tuple(items)


def _consent_inputs(consent: Consent) -> list[AcceptedInput]:
    prefix = f"consent.{consent.human.name}"
    proposer = "proposer"
    fields = (
        "informed", "voluntary", "specific", "competent",
        "revocable", "coerced", "deceived",
    )
    out = [
        AcceptedInput(f"{prefix}.{f}", getattr(consent, f), proposer, INPUT_CALLER_FLAG)
        for f in fields
    ]
    if consent.operation is not None:
        out.append(AcceptedInput(
            f"{prefix}.operation",
            consent.operation.name,
            proposer,
            INPUT_CALLER_FLAG,
        ))
    return out
