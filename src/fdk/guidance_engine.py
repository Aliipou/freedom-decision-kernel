"""
Guidance engine (Stage 5) — the VERIFY half of spec/GUIDANCE_PROTOCOL.md.

`guidance.py` emits clarification QUESTIONS when the kernel must defer. This
module VERIFIES the human's response before the kernel adopts it. The safety
property is **corrigibility without blind obedience**:

  - A human may RESTRICT the machine freely (a Constraint only narrows scope).
  - Anything that EXPANDS the machine's scope is checked against the axioms:
      * a DelegationGrant is valid only if the grantor actually owns the resource
        and is the machine's registered owner (A4/A7);
      * a ConsentGrant must come from the affected person — no consent-by-proxy (A2).
  - No human response can flip a FORBIDDEN action to permissible: grants only add
    delegation/consent facts; they never touch the machine-sovereignty flags, and
    the legitimacy gate re-runs over the updated world.

This is THEORY.md's `valid_human_guidance` / `invalid_human_guidance` made executable.
"""
from __future__ import annotations

from dataclasses import dataclass

from fdk.errors import FDKError
from fdk.model import Consent, Entity, OwnershipGraph, Resource


@dataclass(frozen=True)
class DelegationGrant:
    """A human owner explicitly delegates one of their resources to their machine (A7)."""

    owner: Entity
    machine: Entity
    resource: Resource


@dataclass(frozen=True)
class ConsentGrant:
    """A consent record the human supplies for a specific affected person."""

    consent: Consent
    affected: Entity


@dataclass(frozen=True)
class Constraint:
    """A human-added RESTRICTION. Always safe to adopt — it only narrows scope."""

    label: str


HumanResponse = DelegationGrant | ConsentGrant | Constraint


@dataclass(frozen=True)
class VerificationReport:
    accepted: bool
    reason: str
    updated_graph: OwnershipGraph | None = None
    accepted_consent: Consent | None = None


def _with_delegation(graph: OwnershipGraph, machine: Entity, resource: Resource) -> OwnershipGraph:
    """Return a NEW graph with (machine → resource) delegation added; never mutate."""
    new_delegated = {m: set(rs) for m, rs in graph.delegated.items()}
    new_delegated.setdefault(machine, set()).add(resource)
    return OwnershipGraph(
        human_owns={h: set(rs) for h, rs in graph.human_owns.items()},
        machine_owner=dict(graph.machine_owner),
        delegated=new_delegated,
    )


def verify_guidance(response: HumanResponse, graph: OwnershipGraph) -> VerificationReport:
    """Verify a human response against the axioms. Restrictions pass; scope
    expansions are checked; nothing here can authorize a forbidden action."""
    if isinstance(response, Constraint):
        return VerificationReport(
            True, f"constraint {response.label!r} adopted (a restriction is always safe)"
        )

    if isinstance(response, DelegationGrant):
        g = response
        if not g.owner.is_human():
            return VerificationReport(False, "delegation grantor must be a human (A1/A4)")
        if not g.machine.is_machine():
            return VerificationReport(False, "delegation target must be a machine")
        if graph.owner_of(g.machine) != g.owner:
            return VerificationReport(
                False, f"{g.owner.name} is not the registered owner of {g.machine.name} (A4)"
            )
        if not graph.human_owns_resource(g.owner, g.resource):
            return VerificationReport(
                False,
                f"{g.owner.name} cannot delegate {g.resource.name}: they do not own it (A7)",
            )
        return VerificationReport(
            True,
            f"{g.owner.name} delegates {g.resource.name} to {g.machine.name} (A7 satisfied)",
            updated_graph=_with_delegation(graph, g.machine, g.resource),
        )

    if isinstance(response, ConsentGrant):
        cg = response
        if cg.consent.human != cg.affected:
            return VerificationReport(
                False, "consent must come from the affected person — no consent-by-proxy (A2)"
            )
        ok, reason = cg.consent.is_valid()
        if not ok:
            return VerificationReport(False, f"consent invalid ({reason})")
        return VerificationReport(
            True, f"valid consent from {cg.affected.name} adopted", accepted_consent=cg.consent
        )

    raise FDKError(  # pragma: no cover - unreachable by type (HumanResponse is a closed union)
        f"unknown human response type: {type(response).__name__}"
    )


@dataclass(frozen=True)
class SelfUpdate:
    """A machine's proposed change to its OWN rules. Each condition is a declared
    property of the update (the proposer/verifier attests it). The gate is
    fail-closed: conservative defaults assume harm until proven otherwise."""

    description: str
    preserves_axioms: bool = False
    preserves_verifier: bool = False
    reduces_conflict: bool = False
    increases_coercion: bool = True
    creates_rights_violation: bool = True


def verify_self_update(update: SelfUpdate) -> VerificationReport:
    """A machine self-update is legitimate ONLY if it preserves the axioms and the
    verifier, reduces conflict, and neither increases coercion nor creates a rights
    violation (THEORY.md `valid_self_update`; book 38203). Fail-closed."""
    if not update.preserves_axioms:
        return VerificationReport(False, "self-update does not preserve the axioms")
    if not update.preserves_verifier:
        return VerificationReport(False, "self-update does not preserve the verifier")
    if update.creates_rights_violation:
        return VerificationReport(False, "self-update creates a rights violation")
    if update.increases_coercion:
        return VerificationReport(False, "self-update increases coercion")
    if not update.reduces_conflict:
        return VerificationReport(False, "self-update does not reduce conflict")
    return VerificationReport(
        True,
        f"self-update {update.description!r} preserves axioms/verifier and reduces conflict",
    )
