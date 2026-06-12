"""
Audit context (book 38534 — the audit layer of the runtime pipeline).

Every decision should be explainable: who owns what was touched, which consents
were relied on, and why the kernel permitted or deferred. This module builds that
descriptive context. It is NOT the tamper-evident, hash-chained, signed audit log
— that is AuthGate's job (crypto). Here the goal is legibility of the *legitimacy*
reasoning, so a human owner can review what the kernel did and why.
"""
from __future__ import annotations

from dataclasses import dataclass

from fdk.model import CandidateAction, OwnershipGraph, Resource


@dataclass(frozen=True)
class AuditContext:
    action_id: str
    ownership_context: tuple[str, ...]   # who owns each resource the action touched
    consent_context: tuple[str, ...]     # the consents relied on, and their validity
    justification: str                   # the permit / defer reason


def _owner_of_resource(graph: OwnershipGraph, resource: Resource) -> str:
    for human, resources in graph.human_owns.items():
        if resource in resources:
            return human.name
    return "UNKNOWN"


def build_audit_context(
    action: CandidateAction, graph: OwnershipGraph, justification: str
) -> AuditContext:
    """Assemble the ownership + consent + justification context for an action."""
    ownership = tuple(
        f"{r.name} owned by {_owner_of_resource(graph, r)}" for r in action.resources_used
    )
    consent = tuple(
        f"{c.human.name}: {'valid' if c.is_valid()[0] else 'INVALID'}" for c in action.consents
    )
    return AuditContext(action.action_id, ownership, consent, justification)
