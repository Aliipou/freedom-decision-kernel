"""
Justice engine for the Freedom Decision Kernel (FDK).

The Theory of Freedom frames the telos as

    DivineJustice(a) := maximize Justice(a)  subject to  rights constraints

The "subject to" clause is the hard gate — ``fdk.kernel.check_legitimacy`` —
and it is NOT re-implemented or weakened here. This module implements only the
"maximize Justice(a)" clause: an advisory, transparent, deterministic ranking
of actions that have *already* been judged permissible.

HONESTY NOTE (read before relying on this number). This module is an
*engineering interpretation* of the book's "Justice" clause. The theory
specifies rights-non-violation as the telos; it does NOT hand us a closed-form
Justice function, and no scalar formula can claim the book's authority. The
choices made here — the weights, the worst-off-first emphasis, the decision to
attribute the whole predicted harm to a single non-consenting party when the
model cannot apportion it — are defensible engineering judgments, documented
as named constants below, and nothing more. The output is ranking *advice*
among permissible actions, never a new hard gate.

Interpretation implemented:

1. Aggregate term — fewer predicted rights violations and less coercion is
   better; more voluntary agreement is better (the same sign conventions as
   the Mahdavi compass in ``fdk.kernel``).

2. Worst-off term ("the most-affected party counts most") — if any affected
   *human* did not give VALID consent (no consent record, or an invalid one:
   coerced, deceived, uninformed, involuntary, unspecific, incompetent), then
   the largest single harm that could fall on that person is penalised more
   heavily than any aggregate gain. Because ``Effects`` is an aggregate (the
   model does not apportion harm per person), we make the conservative
   worst-case assumption that the entire predicted harm
   (positive rights_violations_delta + positive coercion_delta) could land on
   one non-consenting human. Erring toward the worst-off is the point.

3. The ``OwnershipGraph`` parameter is part of the contract so that future,
   finer-grained per-party harm attribution (who owns what is harmed) can be
   added without an interface change. The current formula does not read it;
   we say so rather than pretend otherwise.

Pure functions over ``fdk.model`` types: no cryptography, no I/O, no
randomness, no hidden state. Same input → same output, always.
"""
from __future__ import annotations

from dataclasses import dataclass

from fdk.model import CandidateAction, Effects, Entity, OwnershipGraph

# ---------------------------------------------------------------------------
# Weights (the *whole* formula — no magic numbers elsewhere).
#
# The aggregate weights deliberately echo the Mahdavi-compass weights in
# fdk.kernel so the two stages do not quietly disagree about what matters.
# ---------------------------------------------------------------------------

#: Weight per predicted rights violation (aggregate term, harm → negative).
W_RIGHTS_VIOLATION = 2.0

#: Weight per unit of predicted coercion (aggregate term, harm → negative).
W_COERCION = 1.5

#: Weight per new voluntary agreement (aggregate term, gain → positive).
W_VOLUNTARY_AGREEMENT = 1.0

#: Weight on the worst-off term. Deliberately LARGER than every aggregate
#: weight above, so that one unit of harm falling on a non-consenting person
#: outweighs one unit of any aggregate gain — worst-off-first, by construction.
W_WORST_OFF = 4.0


@dataclass(frozen=True)
class JusticeScore:
    """Result of scoring one action. Higher ``score`` = more just (advisory).

    ``worst_off_delta`` is the harm attributed to the most-affected
    non-consenting human (0 when everyone affected gave valid consent, or
    when no positive harm is predicted). ``rationale`` is a deterministic,
    human-readable account of how the number was produced.
    """

    score: float
    worst_off_delta: int
    rationale: str


def _has_valid_consent(action: CandidateAction, human: Entity) -> bool:
    """True iff *human* has a consent record on *action* that is valid per
    Consent.is_valid() (the model's own A4-grade test — not re-derived here)."""
    for consent in action.consents:
        if consent.human == human:
            valid, _reason = consent.is_valid()
            return valid
    return False


def _non_consenting_affected_humans(action: CandidateAction) -> list[Entity]:
    """The affected humans who did NOT give valid consent (machines excluded:
    the theory's consent logic protects persons)."""
    return [
        target
        for target in action.affects
        if target.is_human() and not _has_valid_consent(action, target)
    ]


def _positive_harm(effects: Effects) -> int:
    """The total predicted *harm* in an action's effects: only the bad-direction
    components count (positive rights-violation and coercion deltas).
    Improvements (negative deltas) are credited in the aggregate term instead."""
    return max(0, effects.rights_violations_delta) + max(0, effects.coercion_delta)


def justice_score(action: CandidateAction, graph: OwnershipGraph) -> JusticeScore:
    """Score how well a *permissible* action serves universal non-violation of
    rights, with the worst-off (non-consenting, most-harmed) party weighted
    most heavily.

    Formula (all weights are the module-level named constants):

        aggregate = - W_RIGHTS_VIOLATION     * rights_violations_delta
                    - W_COERCION             * coercion_delta
                    + W_VOLUNTARY_AGREEMENT  * voluntary_agreements_delta

        worst_off_delta = positive_harm(effects)   if any affected human lacks
                                                    valid consent, else 0
            where positive_harm = max(0, rights_violations_delta)
                                + max(0, coercion_delta)

        score = aggregate - W_WORST_OFF * worst_off_delta

    ``graph`` is accepted for interface stability (future per-party harm
    attribution); the current formula does not depend on it — see the module
    docstring. Advisory only: the hard gate remains check_legitimacy.
    """
    effects = action.effects

    aggregate = (
        -W_RIGHTS_VIOLATION * effects.rights_violations_delta
        - W_COERCION * effects.coercion_delta
        + W_VOLUNTARY_AGREEMENT * effects.voluntary_agreements_delta
    )

    non_consenting = _non_consenting_affected_humans(action)
    worst_off_delta = _positive_harm(effects) if non_consenting else 0

    score = aggregate - W_WORST_OFF * worst_off_delta

    if non_consenting and worst_off_delta > 0:
        names = ", ".join(sorted(e.name for e in non_consenting))
        worst_part = (
            f"worst-off penalty {W_WORST_OFF}*{worst_off_delta} "
            f"(harm may fall entirely on non-consenting: {names})"
        )
    elif non_consenting:
        names = ", ".join(sorted(e.name for e in non_consenting))
        worst_part = f"no predicted harm, but non-consenting affected: {names}"
    else:
        worst_part = "all affected humans gave valid consent (worst-off term 0)"

    rationale = (
        f"justice={score:+.1f}: aggregate {aggregate:+.1f} "
        f"(rights {effects.rights_violations_delta:+d}, "
        f"coercion {effects.coercion_delta:+d}, "
        f"voluntary {effects.voluntary_agreements_delta:+d}); {worst_part}"
    )
    return JusticeScore(score=score, worst_off_delta=worst_off_delta, rationale=rationale)


def rank_by_justice(
    actions: list[CandidateAction], graph: OwnershipGraph
) -> list[tuple[CandidateAction, JusticeScore]]:
    """Rank actions best-first by justice_score. Deterministic: ties are broken
    by ``action_id`` (ascending), so the same input list — in any order —
    always yields the same ranking. Advisory ranking only; legitimacy
    screening is the kernel's job and is not performed here."""
    scored = [(action, justice_score(action, graph)) for action in actions]
    scored.sort(key=lambda pair: (-pair[1].score, pair[0].action_id))
    return scored
