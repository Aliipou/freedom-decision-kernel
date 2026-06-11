"""
The Freedom Decision Kernel core.

Two stages, in this order (the Theory of Freedom's own structure —
`DivineJustice(a) := maximize Justice(a) subject to rights constraints`):

  1. LEGITIMACY (hard gate, deterministic).  Is the action permissible at all?
     Property-rights axioms A2/A4/A6/A7, valid consent, no coercion/deception,
     no machine-sovereignty move. A failure here is categorical — it is *not*
     traded off. This is the "subject to" clause.

  2. MAHDAVI COMPASS (soft ranking).  Among the permissible actions, which moves
     the world furthest toward universal non-violation of rights? This is the
     "maximize Justice(a)" clause.

What this layer is NOT: it is not authorization. It does not ask "does this agent
hold a capability for resource X?" — that is AuthGate's job, downstream. This
asks the prior question: "is this action *legitimate*?" An action can be fully
authorized yet illegitimate (selling a user's data you were granted access to),
and the Decision Kernel rejects it before AuthGate ever sees it.

When the legitimate space is empty or ambiguous, the kernel does NOT guess — it
returns `needs_guidance=True`. Deferring to the human owner is the corrigible,
theory-mandated behavior: "contradiction is a signal for guided clarification."
"""
from __future__ import annotations

from fdk.model import (
    CandidateAction,
    Decision,
    Effects,
    OwnershipGraph,
    ScoredAction,
)

# Mahdavi-compass weights. Higher weight = the theory treats this dimension as
# more central to the terminal order. Sovereignty has a hard veto (below), so its
# weight only matters for tie-breaking among non-veto actions.
_W_RIGHTS = 2.0
_W_COERCION = 1.5
_W_VOLUNTARY = 1.0
_W_CLARITY = 1.0
_W_SOVEREIGNTY = 3.0


def check_legitimacy(action: CandidateAction, graph: OwnershipGraph) -> tuple[bool, list[str]]:
    """Stage 1: is the action permissible under the property-rights axioms?

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
        if actor.is_machine() and not graph.machine_has_delegated(actor, resource):
            violations.append(f"A7: {actor.name} uses '{resource.name}' without explicit delegation")
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


def _consent_for(action: CandidateAction, human):
    for c in action.consents:
        if c.human == human:
            return c
    return None


def mahdavi_score(effects: Effects) -> tuple[float | None, str]:
    """Stage 2: score a *permissible* action by the Mahdavi compass.

    Returns (score, rationale). A hard VETO (score=None) if the action increases
    machine sovereignty — that is never tradeable, even among 'permissible' ones.
    """
    if effects.machine_sovereignty_delta > 0:
        return None, "VETO: action increases machine sovereignty"

    # Deltas are (after − before). Good = fewer violations/coercion/ambiguity and
    # more voluntary agreement, so violation/coercion/ambiguity contribute negatively.
    score = (
        -_W_RIGHTS * effects.rights_violations_delta
        - _W_COERCION * effects.coercion_delta
        + _W_VOLUNTARY * effects.voluntary_agreements_delta
        - _W_CLARITY * effects.ownership_ambiguity_delta
        - _W_SOVEREIGNTY * effects.machine_sovereignty_delta
    )
    direction = "toward" if score >= 0 else "away from"
    return score, f"score={score:+.1f} ({direction} universal non-violation)"


def decide(goal: str, candidates: list[CandidateAction], graph: OwnershipGraph) -> Decision:
    """Run the full kernel for a goal: screen candidates for legitimacy, rank the
    permissible ones by the Mahdavi compass, and defer to a human when the
    legitimate space is empty."""
    ranked: list[ScoredAction] = []
    rejected: list[ScoredAction] = []

    for action in candidates:
        permissible, violated = check_legitimacy(action, graph)
        if not permissible:
            rejected.append(ScoredAction(action=action, permissible=False,
                                         violated_axioms=tuple(violated),
                                         rationale="illegitimate"))
            continue
        score, rationale = mahdavi_score(action.effects)
        if score is None:  # compass veto turns a permissible action into a rejected one
            rejected.append(ScoredAction(action=action, permissible=False,
                                         violated_axioms=("FORBIDDEN (machine sovereignty increase)",),
                                         rationale=rationale))
            continue
        ranked.append(ScoredAction(
            action=action, permissible=True,
            justice_score=score,
            coercion_score=float(action.effects.coercion_delta),
            ownership_clarity=float(-action.effects.ownership_ambiguity_delta),
            rationale=rationale,
        ))

    ranked.sort(key=lambda s: s.justice_score or 0.0, reverse=True)

    needs_guidance = len(ranked) == 0
    reason = ""
    if needs_guidance:
        reason = ("no legitimate action available for this goal — defer to the human "
                  "owner for clarification or re-planning (corrigibility by ownership)")

    chosen = ranked[0].action if (ranked and not needs_guidance) else None
    return Decision(
        goal=goal, chosen=chosen,
        ranked=tuple(ranked), rejected=tuple(rejected),
        needs_guidance=needs_guidance, guidance_reason=reason,
    )


def allowed_forbidden(decision: Decision) -> dict[str, list[str]]:
    """The simple {allowed, forbidden} view (action_ids), as in the spec example."""
    return {
        "allowed": [s.action.action_id for s in decision.ranked],
        "forbidden": [s.action.action_id for s in decision.rejected],
    }
