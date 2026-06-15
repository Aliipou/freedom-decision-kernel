"""
Federation (Phase 11) — multi-owner governance for the decision kernel.

Honest scope: this is NOT distributed-systems machinery (no Merkle trees,
consensus, threshold signatures, or crypto — that is AuthGate's distributed
layer). It is the pure DECISION logic for *many owners*:

  - **jurisdiction**: which owner-domain governs a resource (the one that owns it);
  - **merged world**: run the single-owner kernel over the union of domains, so a
    cross-domain action is still bound by owner-scope + consent (owner-bound);
  - **dispute resolution**: cross-owner conflicts go through the conflict rules,
    which DEFER genuine disputes to the humans (A6 — no machine adjudicates
    between owners);
  - **constitutional updates**: the axioms are unalterable; only axiom-consistent
    rules may be added by agreement (book Principle 2).

The book's broader governance/constitutional *program* (federation treaties,
jurisdiction politics) is out-of-kernel and deliberately not coded.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from fdk_kernel.guidance import GuidanceRequest
from fdk_kernel.model import CandidateAction, Decision, Entity, Op, OwnershipGraph, Resource
from fdk_research.conflict import Resolution, resolve_conflict
from fdk_research.ontology import Conflict
from fdk_research.planner import EnforcementPort, ProposerPort, plan


@dataclass
class Federation:
    """A set of owner-domains, each its own OwnershipGraph. Decisions run over the
    merged world; jurisdiction routes a resource to the domain that owns it."""

    domains: dict[str, OwnershipGraph] = field(default_factory=dict)

    def merged_graph(self) -> OwnershipGraph:
        """Union of every domain's ownership graph."""
        human_owns: dict[Entity, set[Resource]] = {}
        machine_owner: dict[Entity, Entity] = {}
        delegated: dict[Entity, set[Resource | tuple[Resource, Op]]] = {}
        for graph in self.domains.values():
            for human, resources in graph.human_owns.items():
                human_owns.setdefault(human, set()).update(resources)
            machine_owner.update(graph.machine_owner)
            for machine, grants in graph.delegated.items():
                delegated.setdefault(machine, set()).update(grants)
        return OwnershipGraph(
            human_owns=human_owns, machine_owner=machine_owner, delegated=delegated
        )

    def jurisdiction(self, resource: Resource) -> str | None:
        """The domain that owns ``resource`` (None if no domain owns it)."""
        for name, graph in self.domains.items():
            for resources in graph.human_owns.values():
                if resource in resources:
                    return name
        return None

    def stakeholder_domains(self, action: CandidateAction) -> tuple[str, ...]:
        """The distinct domains an action touches, in first-seen order."""
        names: list[str] = []
        for resource, _op in action.uses():
            domain = self.jurisdiction(resource)
            if domain is not None and domain not in names:
                names.append(domain)
        return tuple(names)


def federated_decide(
    goal: str,
    proposer: ProposerPort,
    federation: Federation,
    *,
    enforcement: EnforcementPort | None = None,
) -> Decision | GuidanceRequest:
    """Decide over the whole federation. The merged kernel already enforces
    owner-bound + consent, so a cross-domain action lacking the target owner's
    authorization is filtered or deferred exactly as it should be."""
    return plan(goal, proposer, federation.merged_graph(), enforcement=enforcement)


def resolve_dispute(conflict: Conflict, federation: Federation) -> Resolution:
    """Resolve a cross-owner dispute via the conflict rules over the merged world:
    decide only where the axioms determine it, else DEFER to the humans."""
    return resolve_conflict(conflict, federation.merged_graph())


def constitutional_update_allowed(
    changes_axioms: bool, consistent_with_axioms: bool
) -> tuple[bool, str]:
    """Constitutional updates (Phase 11): the axioms themselves are unalterable
    (book Principle 2). Only an axiom-consistent rule may be added by agreement."""
    if changes_axioms:
        return False, "the axioms are unalterable (book Principle 2)"
    if not consistent_with_axioms:
        return False, "proposed rule conflicts with the axioms"
    return True, "axiom-consistent rule may be adopted by agreement"
