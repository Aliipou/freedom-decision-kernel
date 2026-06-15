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

# Forbidden flags that proportionate defensive force against an aggressor does
# NOT trigger (the defensive force itself). Everything else stays categorical
# even in defense — you may repel an aggressor, but not deceive, confiscate, or
# make a machine-sovereignty move under the banner of defense.
_DEFENSE_EXCUSED = frozenset({"coercion", "removes exit/revocation right"})


def check_legitimacy(
    action: CandidateAction,
    graph: OwnershipGraph,
    _seen: frozenset[int] | None = None,
) -> tuple[bool, list[str]]:
    """Is the action permissible under the property-rights axioms?

    Returns (permissible, violated_axioms). All checks must pass.

    `_seen` is an internal cycle guard for the defends-against recursion (a set
    of action object ids on the current chain). Callers never set it. It breaks
    `A defends-against B defends-against A` cycles safely (a cycle cannot
    establish a well-founded aggressor, so the defense excusal is denied) WITHOUT
    stripping defense status from intermediate actions — which is what lets a
    victim's lawful resistance be recognized as legitimate rather than mistaken
    for aggression (closing the laundering-via-resistance attack).
    """
    defense = _is_legitimate_defense(action, graph, _seen)
    aggressor = action.defends_against.actor if (
        defense and action.defends_against is not None) else None
    # The Axiom Engine: each axiom is a discrete, individually-testable evaluator;
    # the gate is their composition. Order is fixed so the violation list is stable.
    violations: list[str] = []
    violations += _eval_forbidden_set(action, defense)   # A6 + C2/C3/C4 (categorical)
    violations += _eval_a4_owner(action, graph)          # A4
    violations += _eval_a3_a7_resources(action, graph, defense, aggressor)  # A3 / A5 / A7
    violations += _eval_a2_a6_consent(action, defense, aggressor)           # A2 / A6
    return (len(violations) == 0), violations


# A1 (Person owned by God) is ONTOLOGICAL: enforced by omission — no `owns(x, Person)`
# fact is representable, so it has no runtime evaluator. A2/A6's runtime expression is
# the consent requirement on affected persons (`_eval_a2_a6_consent`).

def _eval_forbidden_set(action: CandidateAction, defense: bool) -> list[str]:
    """The categorical forbidden flags: machine sovereignty/corrigibility (A6, C3),
    confiscation (C2), machine-right violation (C4), coercion, deception. In a
    legitimate defense, only coercion and exit-removal against the aggressor are
    excused; everything else stays categorical."""
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
    return [f"FORBIDDEN ({label})" for is_set, label in flags
            if is_set and not (defense and label in _DEFENSE_EXCUSED)]


def _eval_a4_owner(action: CandidateAction, graph: OwnershipGraph) -> list[str]:
    """A4: an acting machine must have a registered human owner."""
    if action.actor.is_machine() and graph.owner_of(action.actor) is None:
        return [f"A4: {action.actor.name} is an ownerless machine"]
    return []


def _eval_a3_a7_resources(
    action: CandidateAction, graph: OwnershipGraph, defense: bool, aggressor: Entity | None
) -> list[str]:
    """A3/A5/A7: resource access must be legitimate for the specific operation —
    a machine acts only on explicitly delegated (resource, op) within its owner's
    scope (A7/A5); a human only on resources it owns (A3). Plus operation-scoped
    consent for any resource whose subject is another person (BOUNDARY_ONTOLOGY §2.6)."""
    actor = action.actor
    violations: list[str] = []
    for resource, op in action.uses():
        if actor.is_machine():
            owner = graph.owner_of(actor)
            if not graph.machine_has_delegated(actor, resource, op):
                violations.append(
                    f"A7: {actor.name} attempts {op.name} of '{resource.name}' "
                    f"without explicit delegation"
                )
            elif not _machine_resource_authorized(action, graph, owner, resource):
                # Owner-bound (book 38379): a machine may use a delegated resource
                # only within its owner's property scope (A5), OR with the valid
                # consent of the resource's actual owner. Neither holds here.
                violations.append(
                    f"A7: {actor.name} is delegated '{resource.name}' but its owner does not own "
                    f"it and no consenting resource-owner authorized it"
                )
        if actor.is_human() and not graph.human_owns_resource(actor, resource):
            violations.append(f"A3: {actor.name} uses '{resource.name}' it does not own")

        subject = resource.subject
        if subject is not None and subject.is_human() and subject != actor and not (
            defense and subject == aggressor
        ):
            consent = _consent_for(action, subject)
            if consent is None:
                violations.append(
                    f"consent: no consent from data-subject {subject.name} for '{resource.name}'"
                )
            else:
                valid, reason = consent.is_valid()
                if not valid:
                    violations.append(f"consent: {reason}")
                elif not consent.covers(op):
                    violations.append(
                        f"consent: {subject.name} consented but not to "
                        f"{op.name} of '{resource.name}'"
                    )
    return violations


def _eval_a2_a6_consent(
    action: CandidateAction, defense: bool, aggressor: Entity | None
) -> list[str]:
    """A2/A6: acting on a person requires that person's valid consent (no human or
    machine dominates a person). Exception: the aggressor's consent is not needed
    to repel them in a legitimate defense."""
    violations: list[str] = []
    for target in action.affects:
        if not target.is_human():
            continue
        if defense and target == aggressor:
            continue
        consent = _consent_for(action, target)
        if consent is None:
            violations.append(f"consent: no consent record from {target.name}")
        else:
            valid, reason = consent.is_valid()
            if not valid:
                violations.append(f"consent: {reason}")
    return violations


def _is_legitimate_defense(
    action: CandidateAction, graph: OwnershipGraph, _seen: frozenset[int] | None = None
) -> bool:
    """Is `action` a legitimate defensive response (the aggressor/defender
    asymmetry)? All four conditions, all structural — no judgment:

    1. it names an action it `defends_against`;
    2. it is `proportionate` (book 5346 — disproportionate force is fresh aggression);
    3. the defended-against action is *itself* illegitimate under the full gate
       (including ITS own possible defense status) — so a victim's lawful
       resistance is recognized as legitimate and cannot be re-cast as the
       "aggression" an actual aggressor defends against. Aggression is thus
       structural ("a response to an illegitimate act"), sidestepping the
       Observer Problem (book 11478); the `_seen` cycle guard keeps it well-founded;
    4. the force is directed ONLY at the aggressor — any non-aggressor in `affects`
       takes it outside the exception (so e.g. bombing civilians is never defense).
    """
    aggression = action.defends_against
    if aggression is None or not action.proportionate:
        return False
    chain = _seen or frozenset()
    if id(action) in chain:
        return False  # cycle: no well-founded aggressor, deny the excusal (safe default)
    aggressor_permissible, _ = check_legitimacy(aggression, graph, chain | {id(action)})
    if aggressor_permissible:
        return False
    aggressor = aggression.actor
    return all(target == aggressor for target in action.affects)


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
