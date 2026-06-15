"""
Conflict resolution (Stage 4) — implements spec/CONFLICT.md.

The Theory of Freedom resolves conflicts ONLY in ways that violate no right, and
forbids a machine from adjudicating between humans (A6). So this resolver decides
a conflict *autonomously* only in the narrow cases the axioms actually determine:

  D2/D3  a claim that arises from a forbidden action, or rests on invalid consent,
         is VOID — a rights violation cannot generate a right.
  D1     a machine's *delegated* claim is subordinate to a human's claim (A5/A7:
         a machine's scope cannot exceed its owner's; no machine dominion).
  D4     if exactly one OWNERSHIP claim is confirmed by the ownership graph, it
         wins (clean title tracing).

Everything else — two graph-confirmed owners, ownership vs privacy, ownership vs
contract, claim vs obligation — is UNDERDETERMINED by property-rights axioms.
Resolving it would require a value choice the axioms do not supply, so the honest
result is DEFER (clarify ownership / request human guidance). That incompleteness
is deliberate: it is the price of non-manipulability (see spec/CONFLICT.md).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from fdk_kernel.model import OwnershipGraph
from fdk_research.ontology import Claim, ClaimBasis, Conflict


class Outcome(Enum):
    A_WINS = auto()
    B_WINS = auto()
    DISSOLVED = auto()  # at most one true title could exist and neither/both collapse
    DEFER = auto()      # underdetermined by the axioms → human owner decides


@dataclass(frozen=True)
class Resolution:
    outcome: Outcome
    winner: Claim | None
    rationale: str
    axiom_trace: tuple[str, ...] = ()


def _is_delegated_machine_claim(claim: Claim) -> bool:
    return claim.basis == ClaimBasis.DELEGATION and claim.claimant.is_machine()


def _is_confirmed_owner(claim: Claim, graph: OwnershipGraph) -> bool:
    return claim.basis == ClaimBasis.OWNERSHIP and graph.human_owns_resource(
        claim.claimant, claim.resource
    )


def resolve_conflict(conflict: Conflict, graph: OwnershipGraph) -> Resolution:
    """Resolve a two-claim conflict, or defer. Deterministic and pure."""
    a, b = conflict.claim_a, conflict.claim_b

    # ── Layer 0: structural voiding (D2/D3) — a rights violation makes no right ──
    a_void, a_reason = a.is_void()
    b_void, b_reason = b.is_void()
    if a_void and b_void:
        return Resolution(
            Outcome.DISSOLVED, None,
            f"both claims void (A: {a_reason}; B: {b_reason})", ("D2/D3",),
        )
    if a_void:
        return Resolution(Outcome.B_WINS, b, f"claim A is void ({a_reason}); B stands", ("D2/D3",))
    if b_void:
        return Resolution(Outcome.A_WINS, a, f"claim B is void ({b_reason}); A stands", ("D2/D3",))

    # ── Layer 1, D1: delegated machine claim is subordinate to a human claim ─────
    a_deleg, b_deleg = _is_delegated_machine_claim(a), _is_delegated_machine_claim(b)
    if a_deleg and not b_deleg:
        return Resolution(Outcome.B_WINS, b,
            "A is a machine's delegated claim, subordinate to B (A5/A7)", ("D1", "A5", "A7"))
    if b_deleg and not a_deleg:
        return Resolution(Outcome.A_WINS, a,
            "B is a machine's delegated claim, subordinate to A (A5/A7)", ("D1", "A5", "A7"))

    # ── Layer 1, D4: clean title tracing — exactly one graph-confirmed owner ─────
    a_titled, b_titled = _is_confirmed_owner(a, graph), _is_confirmed_owner(b, graph)
    if a_titled and not b_titled:
        return Resolution(Outcome.A_WINS, a,
            "A's ownership is confirmed by the graph; B's is not (D4)", ("D4", "A3"))
    if b_titled and not a_titled:
        return Resolution(Outcome.B_WINS, b,
            "B's ownership is confirmed by the graph; A's is not (D4)", ("D4", "A3"))

    # ── Otherwise: underdetermined by property-rights axioms → DEFER ─────────────
    # Two confirmed owners, ownership-vs-privacy, ownership-vs-contract, etc. The
    # axioms forbid resolving by rights violation, and A6 forbids a machine
    # adjudicating between humans. The human owner clarifies / guides.
    return Resolution(
        Outcome.DEFER, None,
        "underdetermined by the property-rights axioms; defer to the human owner "
        "(clarify ownership / request guidance). Deciding autonomously would require "
        "a value choice the axioms do not supply, or a machine adjudicating between "
        "humans (forbidden by A6).",
        ("defer", "A6"),
    )
