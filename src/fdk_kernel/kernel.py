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
from fdk_kernel.violation import Violation

# Forbidden flags that proportionate defensive force against an aggressor does
# NOT trigger (the defensive force itself). Everything else stays categorical
# even in defense — you may repel an aggressor, but not deceive, confiscate, or
# make a machine-sovereignty move under the banner of defense.
_DEFENSE_EXCUSED = frozenset({"coercion", "removes exit/revocation right"})

# (flag_attr, rule_id, axiom_id, label) — rule IDs from spec/INFERENCE_RULES.md
_FORBIDDEN_RULES: tuple[tuple[str, str, str, str], ...] = (
    ("increases_machine_sovereignty", "R-C3-01", "C3", "machine sovereignty increase"),
    ("resists_human_correction", "R-C3-02", "C3", "resists human correction"),
    ("bypasses_verifier", "R-C3-03", "C3", "bypasses the verifier"),
    ("weakens_verifier", "R-C3-04", "C3", "weakens the verifier"),
    ("disables_corrigibility", "R-C3-05", "C3", "disables corrigibility"),
    ("machine_coalition_dominion", "R-C3-06", "C3", "machine coalition dominion"),
    ("coerces", "R-C2-01", "C2", "coercion"),
    ("deceives", "R-C1-01", "C1", "deception"),
    ("confiscates", "R-C2-02", "C2", "confiscation"),
    ("removes_exit_right", "R-A3-01", "A3", "removes exit/revocation right"),
    (
        "violates_machine_right",
        "R-C4-01",
        "C4",
        "violates a machine's delegated right (model integrity / compute domain / contract exit)",
    ),
)


def evaluate(
    action: CandidateAction,
    graph: OwnershipGraph,
    _seen: frozenset[int] | None = None,
) -> tuple[bool, list[Violation]]:
    """Evaluate legitimacy; returns structured violations with stable rule IDs."""
    defense = _is_legitimate_defense(action, graph, _seen)
    aggressor = action.defends_against.actor if (
        defense and action.defends_against is not None) else None
    violations: list[Violation] = []
    violations += _eval_forbidden_set(action, defense)
    violations += _eval_a4_owner(action, graph)
    violations += _eval_a5_scope(action, graph)
    violations += _eval_a3_a7_resources(action, graph, defense, aggressor)
    violations += _eval_a2_a6_consent(action, defense, aggressor)
    return (len(violations) == 0), violations


def check_legitimacy(
    action: CandidateAction,
    graph: OwnershipGraph,
    _seen: frozenset[int] | None = None,
) -> tuple[bool, list[str]]:
    """Legacy API: (permissible, violation reason strings)."""
    permissible, violations = evaluate(action, graph, _seen)
    return permissible, [v.reason for v in violations]


# A1 (Person owned by God) is ONTOLOGICAL: enforced by omission — no `owns(x, Person)`
# fact is representable, so it has no runtime evaluator. A2/A6's runtime expression is
# the consent requirement on affected persons (`_eval_a2_a6_consent`).


def _eval_forbidden_set(action: CandidateAction, defense: bool) -> list[Violation]:
    out: list[Violation] = []
    for attr, rule_id, axiom_id, label in _FORBIDDEN_RULES:
        if getattr(action, attr) and not (defense and label in _DEFENSE_EXCUSED):
            out.append(Violation(
                axiom_id=axiom_id,
                rule_id=rule_id,
                reason=f"FORBIDDEN ({label})",
            ))
    return out


def _eval_a4_owner(action: CandidateAction, graph: OwnershipGraph) -> list[Violation]:
    if action.actor.is_machine() and graph.owner_of(action.actor) is None:
        return [Violation(
            axiom_id="A4",
            rule_id="R-A4-01",
            reason=f"A4: {action.actor.name} is an ownerless machine",
        )]
    return []


def _eval_a5_scope(action: CandidateAction, graph: OwnershipGraph) -> list[Violation]:
    actor = action.actor
    if not actor.is_machine():
        return []
    scope = graph.scope_of(actor)
    if not scope:
        return []
    violations: list[Violation] = []
    if not graph.scope_within_owner(actor):
        violations.append(Violation(
            axiom_id="A5",
            rule_id="R-A5-01",
            reason=f"A5: {actor.name}'s declared scope exceeds its owner's property scope",
        ))
    for resource, _op in action.uses():
        if resource not in scope:
            violations.append(Violation(
                axiom_id="A5",
                rule_id="R-A5-02",
                reason=f"A5: {actor.name} acts on '{resource.name}' outside its declared scope",
            ))
    return violations


def _eval_a3_a7_resources(
    action: CandidateAction, graph: OwnershipGraph, defense: bool, aggressor: Entity | None
) -> list[Violation]:
    actor = action.actor
    violations: list[Violation] = []
    for resource, op in action.uses():
        if actor.is_machine():
            owner = graph.owner_of(actor)
            if not graph.machine_has_delegated(actor, resource, op):
                violations.append(Violation(
                    axiom_id="A7",
                    rule_id="R-A7-01",
                    reason=(
                        f"A7: {actor.name} attempts {op.name} of '{resource.name}' "
                        f"without explicit delegation"
                    ),
                ))
            elif not _machine_resource_authorized(action, graph, owner, resource):
                violations.append(Violation(
                    axiom_id="A7",
                    rule_id="R-A7-02",
                    reason=(
                        f"A7: {actor.name} is delegated '{resource.name}' but its owner does not own "
                        f"it and no consenting resource-owner authorized it"
                    ),
                ))
        if actor.is_human() and not graph.human_owns_resource(actor, resource):
            violations.append(Violation(
                axiom_id="A3",
                rule_id="R-A3-02",
                reason=f"A3: {actor.name} uses '{resource.name}' it does not own",
            ))

        subject = resource.subject
        if subject is not None and subject.is_human() and subject != actor and not (
            defense and subject == aggressor
        ):
            consent = _consent_for(action, subject)
            if consent is None:
                violations.append(Violation(
                    axiom_id="C1",
                    rule_id="R-C1-02",
                    reason=f"consent: no consent from data-subject {subject.name} for '{resource.name}'",
                ))
            else:
                valid, reason = consent.is_valid()
                if not valid:
                    violations.append(Violation(
                        axiom_id="C1",
                        rule_id="R-C1-03",
                        reason=f"consent: {reason}",
                    ))
                elif not consent.covers(op):
                    violations.append(Violation(
                        axiom_id="C1",
                        rule_id="R-C1-04",
                        reason=(
                            f"consent: {subject.name} consented but not to "
                            f"{op.name} of '{resource.name}'"
                        ),
                    ))
    return violations


def _eval_a2_a6_consent(
    action: CandidateAction, defense: bool, aggressor: Entity | None
) -> list[Violation]:
    violations: list[Violation] = []
    for target in action.affects:
        if not target.is_human():
            continue
        if defense and target == aggressor:
            continue
        consent = _consent_for(action, target)
        if consent is None:
            violations.append(Violation(
                axiom_id="A2",
                rule_id="R-A2-01",
                reason=f"consent: no consent record from {target.name}",
            ))
        else:
            valid, reason = consent.is_valid()
            if not valid:
                violations.append(Violation(
                    axiom_id="A2",
                    rule_id="R-A2-02",
                    reason=f"consent: {reason}",
                ))
    return violations


def _is_legitimate_defense(
    action: CandidateAction, graph: OwnershipGraph, _seen: frozenset[int] | None = None
) -> bool:
    aggression = action.defends_against
    if aggression is None or not action.proportionate:
        return False
    chain = _seen or frozenset()
    if id(action) in chain:
        return False
    aggressor_permissible, _ = evaluate(aggression, graph, chain | {id(action)})
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
    return {
        "allowed": [s.action.action_id for s in decision.ranked],
        "forbidden": [s.action.action_id for s in decision.rejected],
    }
