"""Authority Composition Algebra — the FDK ⊗ AuthGate → Decision seam, formalized.

Locks the architecture's core invariant: the FDK can only **narrow** the decision
space, never widen it. AuthGate grants authority; the FDK emits a *ceiling*
constraint (the most it will permit); the composed decision is their **meet** (the
more restrictive). The FDK is a constraint oracle, not an actor — there is no FDK
input that turns a DENY into an ALLOW.

This is an executable specification: `verify_algebra()` proves every property by
exhaustive enumeration over the whole decision lattice. The FDK contains no
cryptography and mutates no state here — it composes decisions, nothing else.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from itertools import product


class Decision(IntEnum):
    """Outcomes ordered by permissiveness: DENY most restrictive, ALLOW most permissive."""

    DENY = 0
    REQUIRE_DELAY = 1
    REQUIRE_APPROVAL = 2
    REQUIRE_SECOND_FACTOR = 3
    ALLOW = 4


def compose(authgate: Decision, *fdk_ceilings: Decision) -> Decision:
    """Final = the most restrictive of AuthGate's grant and every FDK ceiling.

    FDK constraints can only lower the outcome (meet / min), never raise it.
    """
    result = authgate
    for ceiling in fdk_ceilings:
        result = Decision(min(result, ceiling))
    return result


@dataclass(frozen=True)
class Composition:
    """Audit-invariant record: the inputs and the output of one composition."""

    authgate: Decision
    fdk_ceilings: tuple[Decision, ...]
    decision: Decision


def decide(authgate: Decision, fdk_ceilings=()) -> Composition:
    fc = tuple(fdk_ceilings)
    return Composition(authgate, fc, compose(authgate, *fc))


# ── properties, as predicates over the entire lattice ─────────────────────────
_ALL = list(Decision)


def prop_narrow_only() -> bool:
    """compose(base, c) <= base — the FDK never widens AuthGate's grant."""
    return all(compose(b, c) <= b for b in _ALL for c in _ALL)


def prop_fdk_cannot_grant() -> bool:
    """No FDK ceiling turns a denied authority into a permissive outcome."""
    return all(compose(Decision.DENY, c) == Decision.DENY for c in _ALL)


def prop_bounded_by_fdk_ceiling() -> bool:
    """The result also never exceeds the FDK ceiling — the FDK's word is binding downward."""
    return all(compose(b, c) <= c for b in _ALL for c in _ALL)


def prop_idempotent() -> bool:
    return all(compose(compose(b, c), c) == compose(b, c) for b in _ALL for c in _ALL)


def prop_order_independent() -> bool:
    """Multiple FDK constraints compose identically regardless of order (meet is comm/assoc)."""
    return all(
        compose(b, c1, c2) == compose(b, c2, c1)
        for b, c1, c2 in product(_ALL, _ALL, _ALL)
    )


PROPERTIES = {
    "narrow_only": prop_narrow_only,
    "fdk_cannot_grant": prop_fdk_cannot_grant,
    "bounded_by_fdk_ceiling": prop_bounded_by_fdk_ceiling,
    "idempotent": prop_idempotent,
    "order_independent": prop_order_independent,
}


def verify_algebra() -> dict[str, bool]:
    """Exhaustively verify every algebra property. All True == the seam is sound."""
    return {name: predicate() for name, predicate in PROPERTIES.items()}
