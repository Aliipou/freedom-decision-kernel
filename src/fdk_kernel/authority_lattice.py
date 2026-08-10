"""Formal authority lattice (FDK v2) — rights as a bounded lattice, attenuation as
monotone narrowing.

This is the *rights* side that complements `authority_algebra.py` (the *decision*
side). An authority is a set of rights; authorities form a **bounded lattice** under
subset ⊑ (meet = intersection, join = union; bottom = ∅ = DENY-all; top = all rights).

The architecture's core claim — authority is only narrowed, never amplified — is here
a theorem about this lattice: delegation/attenuation is `parent ⊓ requested`, which is
always ⊑ parent; applying constraints is a meet, which can only remove rights. There is
no operation in the lattice that *adds* a right you were not granted.

`verify_lattice()` proves the lattice laws and the narrowing theorems by exhaustive
enumeration over the powerset of a finite right-universe.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class Authority:
    rights: frozenset[str]

    @classmethod
    def of(cls, *rights: str) -> Authority:
        return cls(frozenset(rights))

    def __le__(self, other: Authority) -> bool:  # ⊑ : "grants no more than"
        return self.rights <= other.rights

    def meet(self, other: Authority) -> Authority:   # ⊓ : greatest lower bound
        return Authority(self.rights & other.rights)

    def join(self, other: Authority) -> Authority:   # ⊔ : least upper bound
        return Authority(self.rights | other.rights)


def attenuate(parent: Authority, requested: Authority) -> Authority:
    """Delegation: you receive at most what the parent holds. `parent ⊓ requested`,
    which is always ⊑ parent — you can never receive a right the parent lacked."""
    return parent.meet(requested)


def compose_constraints(base: Authority, *constraints: Authority) -> Authority:
    """Each constraint is a ceiling set of permitted rights; meet them all. Constraints
    can only remove rights, never add (the No-Amplification axiom, at the rights level)."""
    result = base
    for c in constraints:
        result = result.meet(c)
    return result


# ── exhaustive verification over a finite universe ────────────────────────────
_UNIVERSE = ("read", "write", "exec", "delegate")


def _all_authorities() -> list[Authority]:
    out: list[Authority] = []
    for r in range(len(_UNIVERSE) + 1):
        for combo in combinations(_UNIVERSE, r):
            out.append(Authority(frozenset(combo)))
    return out


_ALL = _all_authorities()
_TOP = Authority(frozenset(_UNIVERSE))
_BOTTOM = Authority(frozenset())


def _commutative() -> bool:
    return all(a.meet(b) == b.meet(a) and a.join(b) == b.join(a) for a in _ALL for b in _ALL)


def _associative() -> bool:
    return all(
        a.meet(b).meet(c) == a.meet(b.meet(c)) and a.join(b).join(c) == a.join(b.join(c))
        for a in _ALL for b in _ALL for c in _ALL
    )


def _idempotent() -> bool:
    return all(a.meet(a) == a and a.join(a) == a for a in _ALL)


def _absorption() -> bool:
    return all(a.meet(a.join(b)) == a and a.join(a.meet(b)) == a for a in _ALL for b in _ALL)


def _bounds() -> bool:
    return all(
        a.meet(_BOTTOM) == _BOTTOM and a.join(_TOP) == _TOP
        and a.meet(_TOP) == a and a.join(_BOTTOM) == a
        for a in _ALL
    )


def _attenuation_narrows() -> bool:
    return all(attenuate(p, req) <= p for p in _ALL for req in _ALL)


def _no_amplification_via_delegation() -> bool:
    # No requested authority can give you a right the parent did not hold.
    return all(attenuate(p, req).rights <= p.rights for p in _ALL for req in _ALL)


def _constraints_only_narrow() -> bool:
    return all(compose_constraints(b, c1, c2) <= b for b in _ALL for c1 in _ALL for c2 in _ALL)


_PROPERTIES = {
    "meet_join_commutative": _commutative,
    "associative": _associative,
    "idempotent": _idempotent,
    "absorption": _absorption,
    "bounded": _bounds,
    "attenuation_narrows": _attenuation_narrows,
    "no_amplification_via_delegation": _no_amplification_via_delegation,
    "constraints_only_narrow": _constraints_only_narrow,
}


def verify_lattice() -> dict[str, bool]:
    """All True == authorities form a bounded lattice and attenuation only narrows."""
    return {name: predicate() for name, predicate in _PROPERTIES.items()}
