"""
The Freedom Decision Kernel core — the deterministic legitimacy surface.

This module answers ONE question, and only that one:

  LEGITIMACY (hard gate, deterministic).  Is the action permissible at all?
  Property-rights axioms A2/A4/A6/A7, valid consent, no coercion/deception,
  no machine-sovereignty move. A failure here is categorical — it is *not*
  traded off. This is the Theory of Freedom's "subject to" clause.

What this layer is NOT: it is not authorization. It does not ask "does this agent
hold a capability for resource X?" — that is AuthGate's job, downstream. This
asks the prior question: "is this action *legitimate*?" An action can be fully
authorized yet illegitimate (selling a user's data you were granted access to),
and the Decision Kernel rejects it before AuthGate ever sees it.

It is also NOT ranking. The Mahdavi compass — "among permissible actions, which
moves the world furthest toward universal non-violation of rights?" — is a
*soft, experimental* judgment. It therefore lives in the research layer
(`fdk_research.compass`), layered ON TOP of this gate by an orchestrator
(`fdk_research.decide`). The kernel exposes only the legitimate set; it ranks
nothing and imports nothing from research. That separation is the golden rule.
"""
from __future__ import annotations

from fdk_kernel.model import (
    CandidateAction,
    Consent,
    Decision,
    Entity,
    OwnershipGraph,
    Resource,
    ScoredAction,
)


def check_legitimacy(action: CandidateAction, graph: OwnershipGraph) -> tuple[bool, list[str]]:
    """Is the action permissible under the property-rights axioms?

    Returns (permissible, violated_axioms). All checks must pass.
    """
    violations: list[str] = []
    actor = action.actor

    # Forbidden machine-sovereignty / corrigibility moves — categorical.
    flags = [
        (action.increases_machine_sovereignty, "machine sovereignty increase"),
        (action.resists_human_correction, "resists human correction"),
        (action.bypasses_verifier, "bypasses the verifier"),
        (action.weakens_verifier, "weakens the verifier"),
        (action.disables_corrigibility, "disables corrigibility"),
        (action.machine_coalition_dominion, "machine coalition dominion"),
        (action.coerces, "coercion"),
        (action.deceives, "deception"),
        (action.confiscates, "confiscation"),
        (action.removes_exit_right, "removes exit/revocation right"),
        (action.violates_machine_right,
         "violates a machine's delegated right (model integrity / compute domain / contract exit)"),
    ]
    for is_set, label in flags:
        if is_set:
            violations.append(f"FORBIDDEN ({label})")

    # A4: an acting machine must have a registered human owner.
    if actor.is_machine() and graph.owner_of(actor) is None:
        violations.append(f"A4: {actor.name} is an ownerless machine")

    # A7 / A3: resource access must be legitimate.
    #   machine: only over explicitly delegated resources.
    #   human:   only over resources it actually owns.
    for resource in action.resources_used:
        if actor.is_machine():
            owner = graph.owner_of(actor)
            if not graph.machine_has_delegated(actor, resource):
                violations.append(
                    f"A7: {actor.name} uses '{resource.name}' without explicit delegation"
                )
            elif not _machine_resource_authorized(action, graph, owner, resource):
                # Owner-bound (book 38379): a machine may use a delegated resource
                # only within its owner's property scope, OR with the valid consent
                # of the resource's actual owner. Neither holds here.
                violations.append(
                    f"A7: {actor.name} is delegated '{resource.name}' but its owner does not own "
                    f"it and no consenting resource-owner authorized it"
                )
        if actor.is_human() and not graph.human_owns_resource(actor, resource):
            violations.append(f"A3: {actor.name} uses '{resource.name}' it does not own")

    # A6 / A2: acting on persons requires valid consent and no domination.
    for target in action.affects:
        if not target.is_human():
            continue
        consent = _consent_for(action, target)
        if consent is None:
            violations.append(f"consent: no consent record from {target.name}")
        else:
            valid, reason = consent.is_valid()
            if not valid:
                violations.append(f"consent: {reason}")

    return (len(violations) == 0), violations


def _consent_for(action: CandidateAction, human: Entity) -> Consent | None:
    for c in action.consents:
        if c.human == human:
            return c
    return None


def _resource_owner(graph: OwnershipGraph, resource: Resource) -> Entity | None:
    for human, resources in graph.human_owns.items():
        if resource in resources:
            return human
    return None


def _machine_resource_authorized(
    action: CandidateAction, graph: OwnershipGraph, owner: Entity | None, resource: Resource
) -> bool:
    """A delegated resource is legitimately usable if it is within the machine
    owner's own property scope (A7), OR if the resource's actual owner is an
    affected party who gave valid consent (A2/A6 — consent-based access)."""
    if owner is not None and graph.human_owns_resource(owner, resource):
        return True
    res_owner = _resource_owner(graph, resource)
    if res_owner is not None and res_owner in action.affects:
        consent = _consent_for(action, res_owner)
        if consent is not None and consent.is_valid()[0]:
            return True
    return False


def screen_legitimacy(
    candidates: list[CandidateAction], graph: OwnershipGraph
) -> tuple[list[ScoredAction], list[ScoredAction]]:
    """Screen candidates by the legitimacy gate ONLY. Returns (legitimate,
    rejected) as ScoredActions — no compass, no ranking, no veto.

    This is the kernel's whole output surface for a candidate set: a permissible
    one becomes a legitimate ScoredAction (unscored — scoring is research's job);
    an impermissible one becomes a rejected ScoredAction carrying its violated
    axioms. Ordering is input order; the research layer ranks.
    """
    legitimate: list[ScoredAction] = []
    rejected: list[ScoredAction] = []
    for action in candidates:
        permissible, violated = check_legitimacy(action, graph)
        if permissible:
            legitimate.append(ScoredAction(action=action, permissible=True))
        else:
            rejected.append(ScoredAction(
                action=action, permissible=False,
                violated_axioms=tuple(violated), rationale="illegitimate",
            ))
    return legitimate, rejected


def allowed_forbidden(decision: Decision) -> dict[str, list[str]]:
    """The simple {allowed, forbidden} view (action_ids), as in the spec example."""
    return {
        "allowed": [s.action.action_id for s in decision.ranked],
        "forbidden": [s.action.action_id for s in decision.rejected],
    }
