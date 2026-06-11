"""
Rights Ontology (Stage 2) — the entity/relation vocabulary the higher stages
reason over. Grounded in THEORY.md's Prolog ontology and spec/ONTOLOGY.md.

Scope discipline (anti-overengineering): this implements only the types that
have a *downstream consumer today* — Claim, Obligation, Contract, Conflict —
which the conflict resolver (Stage 4) and planner (Stage 7) use. Organization,
Institution, and Information are specified in spec/ONTOLOGY.md but deliberately
NOT implemented here until a consumer exists.

Pure, immutable value types: no cryptography, no I/O. Enforcement is AuthGate's
job; measurement is the compass's. This module only *describes* rights.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from fdk.errors import InvalidClaim, InvalidConflict, InvalidContract, InvalidObligation
from fdk.model import Consent, Entity, Resource


class ClaimBasis(Enum):
    """Why a claimant says a resource is theirs — the legal ground of the claim."""

    OWNERSHIP = auto()   # "I own this outright" (A3)
    DELEGATION = auto()  # "my human owner delegated this to me" (A7) — machine claim
    CONTRACT = auto()    # "a contract assigns this to me" (A3 contracts)
    PRIVACY = auto()     # "this concerns my person/data" (A3 privacy/data)


@dataclass(frozen=True)
class Claim:
    """An assertion that ``claimant`` holds a right over ``resource`` on a given
    ``basis``. Claims are *evidence inputs* to conflict resolution, not verdicts."""

    claimant: Entity
    resource: Resource
    basis: ClaimBasis
    via_consent: Consent | None = None
    from_forbidden_action: bool = False
    established_at: int = 0  # ordinal time; advisory (first-in-time is evidentiary, not decisive)
    note: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.basis, ClaimBasis):
            raise InvalidClaim("Claim.basis must be a ClaimBasis")
        if self.established_at < 0:
            raise InvalidClaim("Claim.established_at must be >= 0")

    def is_void(self) -> tuple[bool, str]:
        """A claim is structurally VOID (not merely weaker) if it arises from a
        forbidden action or rests on invalid consent. A rights violation cannot
        generate a right — so a void claim can never win a conflict."""
        if self.from_forbidden_action:
            return True, "claim arises from a forbidden action"
        if self.via_consent is not None:
            ok, reason = self.via_consent.is_valid()
            if not ok:
                return True, f"claim rests on invalid consent ({reason})"
        return False, ""


@dataclass(frozen=True)
class Obligation:
    """A duty owed by ``obligor`` to ``obligee`` (Hohfeldian duty correlative to a
    claim-right). Used where an action discharges or breaches a duty."""

    obligor: Entity
    obligee: Entity
    description: str
    resource: Resource | None = None

    def __post_init__(self) -> None:
        if not self.description or not self.description.strip():
            raise InvalidObligation("Obligation.description must be a non-empty string")


@dataclass(frozen=True)
class Contract:
    """A voluntary agreement among parties. Valid only if every human party has a
    valid Consent on record (A3 contracts rest on consent, not imposition)."""

    parties: tuple[Entity, ...]
    consents: tuple[Consent, ...] = ()
    resource: Resource | None = None
    description: str = ""

    def __post_init__(self) -> None:
        if len(self.parties) < 2:
            raise InvalidContract("a Contract needs at least two parties")

    def is_valid(self) -> tuple[bool, str]:
        for party in self.parties:
            if not party.is_human():
                continue  # machine parties act under delegation, checked elsewhere
            consent = next((c for c in self.consents if c.human == party), None)
            if consent is None:
                return False, f"no consent from {party.name}"
            ok, reason = consent.is_valid()
            if not ok:
                return False, reason
        return True, "ok"


class ConflictKind(Enum):
    TWO_OWNERS = auto()
    OWNERSHIP_VS_PRIVACY = auto()
    OWNERSHIP_VS_CONTRACT = auto()
    CLAIM_VS_OBLIGATION = auto()
    OTHER = auto()


@dataclass(frozen=True)
class Conflict:
    """Two competing claims over the same resource. The resolver decides which (if
    either) prevails, or defers to a human when the axioms underdetermine it."""

    claim_a: Claim
    claim_b: Claim
    kind: ConflictKind = ConflictKind.OTHER

    def __post_init__(self) -> None:
        if self.claim_a.resource != self.claim_b.resource:
            raise InvalidConflict("a Conflict pairs two claims over the SAME resource")
