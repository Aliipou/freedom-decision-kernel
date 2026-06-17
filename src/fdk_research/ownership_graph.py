"""Real ownership graph — advisory layer (FDK 2.0, Layer 6). RESEARCH LAYER.

The kernel's biggest hidden assumption: it reads an `OwnershipGraph` as *given and
correct*. The real world does not hand you a correct ownership graph — it hands you
contested titles, chains that bottom out in conquest, tokens that are not the asset
(NFTs), models trained on a billion people's data, estates of the dead, and "owners"
of rivers and air. Garbage ownership graph in → garbage verdict out, no matter how
sound the kernel.

This module does NOT solve ownership. It does the honest, achievable thing: given the
*evidence* about a title, it assesses **how much the kernel may rely on it**, and
flags the cases — above all FORCED origins (the bootstrapping gap of
`spec/FOUNDATIONAL_ATTACKS.md`) — where relying on the graph would launder an
injustice the gate cannot relitigate. It is advisory only: it returns no ALLOW/DENY,
mutates nothing, never builds or edits an `OwnershipGraph`, and routes contested
titles to a human / legal process. See `spec/OWNERSHIP_GRAPH.md`. Imports nothing into
`fdk_kernel` (`tests/test_boundary.py`).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OriginKind(Enum):
    """How a claimed title came to be — the question the kernel cannot ask."""

    ORIGINAL_ACQUISITION = "original-acquisition"   # first creation / homesteading
    CONSENSUAL_TRANSFER = "consensual-transfer"     # a voluntary chain of title
    FORCED_ORIGIN = "forced-origin"                 # descends from theft / conquest
    CONTESTED = "contested"                         # multiple live claimants
    UNPROVEN = "unproven"                           # no chain of title available


class Reliance(Enum):
    """The only outputs — all about how a HUMAN should treat the title before
    feeding it to the kernel. None is a legitimacy verdict."""

    RELY = "rely"                      # sound enough to use as kernel input
    RELY_WITH_NOTE = "rely-with-note"  # usable but carry the caveat
    DO_NOT_RELY = "do-not-rely"        # contested/forced/unproven → resolve first


@dataclass(frozen=True)
class TitleClaim:
    """The evidence about one claimed title. Supplied by a human/registry, not the
    kernel (the kernel's `OwnershipGraph` has no provenance field at all)."""

    resource: str
    claimant: str
    origin: OriginKind
    provenance_depth: int = 0               # number of verified transfer links
    cryptographically_verifiable: bool = False  # e.g. an on-chain UTXO
    competing_claims: int = 0               # live rival claimants

    def __post_init__(self) -> None:
        if self.provenance_depth < 0 or self.competing_claims < 0:
            raise ValueError("provenance_depth and competing_claims must be >= 0")


@dataclass(frozen=True)
class TitleAssessment:
    reliance: Reliance
    bootstrapping_flag: bool  # origin descends from an act the gate cannot relitigate
    rationale: str
    recommendation: str


def assess_title(claim: TitleClaim) -> TitleAssessment:
    """How much may the kernel rely on this title? Pure, deterministic, advisory —
    never a legitimacy verdict, never mutates anything."""
    # FORCED origin is the bootstrapping gap made concrete: the kernel would protect
    # the current holder of stolen/conquered title exactly as a clean one.
    if claim.origin is OriginKind.FORCED_ORIGIN:
        return TitleAssessment(
            Reliance.DO_NOT_RELY, bootstrapping_flag=True,
            rationale=f"'{claim.resource}' title descends from theft/conquest; the "
                      "kernel cannot legitimize its origin and would launder it.",
            recommendation="Do NOT feed as a settled owner. Route to a "
                           "historical-rectification / legal process first.",
        )

    # Live disputes: there is no single owner to bind a consent to.
    if claim.origin is OriginKind.CONTESTED or claim.competing_claims > 0:
        return TitleAssessment(
            Reliance.DO_NOT_RELY, bootstrapping_flag=False,
            rationale=f"'{claim.resource}' has {max(claim.competing_claims, 1)} live "
                      "competing claim(s); ownership is unsettled.",
            recommendation="Resolve the dispute (court / arbitration / Aggregation "
                           "layer) before the kernel treats anyone as the owner.",
        )

    # No chain of title at all.
    if claim.origin is OriginKind.UNPROVEN:
        return TitleAssessment(
            Reliance.DO_NOT_RELY, bootstrapping_flag=False,
            rationale=f"'{claim.resource}' has no provable chain of title.",
            recommendation="Establish provenance before relying on the claim.",
        )

    # Cryptographically verifiable consensual transfer (e.g. on-chain) — strongest.
    if claim.cryptographically_verifiable and claim.origin in (
        OriginKind.CONSENSUAL_TRANSFER, OriginKind.ORIGINAL_ACQUISITION
    ):
        return TitleAssessment(
            Reliance.RELY, bootstrapping_flag=False,
            rationale=f"'{claim.resource}' title is cryptographically verifiable with "
                      "a consensual/original origin.",
            recommendation="Reliable as kernel input. (Note: on-chain proves the "
                           "TOKEN's provenance, not that the token IS the off-chain asset.)",
        )

    # A (non-crypto) consensual chain — usable, but no chain proves its own first link.
    if claim.origin is OriginKind.CONSENSUAL_TRANSFER:
        return TitleAssessment(
            Reliance.RELY_WITH_NOTE, bootstrapping_flag=False,
            rationale=f"'{claim.resource}' rests on a consensual chain of "
                      f"{claim.provenance_depth} verified link(s), but the chain's ROOT "
                      "origin is unaudited — no chain proves its own first link.",
            recommendation="Usable; record that the origin question stays open.",
        )

    # Original acquisition with no rivals — usable, but the doctrine itself is a
    # theory-author question (what counts as legitimate first appropriation?).
    return TitleAssessment(
        Reliance.RELY_WITH_NOTE, bootstrapping_flag=False,
        rationale=f"'{claim.resource}' rests on original acquisition with no live "
                  "rival; but 'what is legitimate first appropriation' is unsettled.",
        recommendation="Usable; record that original-acquisition legitimacy is a "
                       "theory-author ruling, not established here.",
    )


def reliable_for_kernel(claim: TitleClaim) -> bool:
    """Convenience: may the kernel treat this title as a settled owner at all?
    True for RELY / RELY_WITH_NOTE, False for DO_NOT_RELY. Advisory, not a verdict."""
    return assess_title(claim).reliance is not Reliance.DO_NOT_RELY
