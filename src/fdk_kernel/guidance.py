"""
The hard-defer trigger of the Freedom Decision Kernel.

The Theory of Freedom mandates corrigibility-by-ownership: when the legitimate
space is empty or ambiguous, "contradiction is a signal for guided clarification."
The kernel must NOT guess — it defers to the human owner. This module answers the
one deterministic, kernel-level question: *must* the kernel defer?

It also defines the `GuidanceQuestion` / `GuidanceRequest` value types that the
research layer fills in when it turns a deferral into an actionable clarification
request (see `fdk_research.guidance_resolution`). The types live here because a
deferral signal is a legitimacy-surface concept; the *resolution* of it (mapping
violations to advice) is experimental and lives in research.

The PREFIX_* constants name the violation-string shapes produced by
`fdk_kernel.kernel.check_legitimacy`, so the parser in research has a single
source of truth to match against.

Pure interpretation of kernel output: no crypto, no enforcement (those live
downstream in AuthGate), and — critically — no dependency on the research layer.
"""
from __future__ import annotations

from dataclasses import dataclass

from fdk_kernel.model import Decision

# --- violation-string prefixes (produced by fdk_kernel.kernel.check_legitimacy) ----
# Single source of truth for parsing — no magic strings scattered downstream.

PREFIX_FORBIDDEN = "FORBIDDEN"   # sovereignty / coercion / deception flags
PREFIX_CONSENT = "consent"       # A6/A2: missing or invalid consent
PREFIX_A3 = "A3"                 # human uses a resource it does not own
PREFIX_A4 = "A4"                 # acting machine has no registered human owner
PREFIX_A7 = "A7"                 # machine uses a resource without explicit delegation


@dataclass(frozen=True)
class GuidanceQuestion:
    topic: str
    question: str
    unblock_hint: str


@dataclass(frozen=True)
class GuidanceRequest:
    goal: str
    reason: str
    questions: tuple[GuidanceQuestion, ...]
    blocking_summary: tuple[str, ...]


# --- when must the kernel defer? --------------------------------------------

def needs_guidance(decision: Decision) -> bool:
    """True when the kernel must defer to the human owner instead of acting.

    Three triggers:
      1. The kernel itself already flagged it (decision.needs_guidance).
      2. The legitimate space is empty (nothing ranked).
      3. The top two ranked actions tie on justice score — the winner is
         ambiguous, and an ambiguous winner is not a winner. Guessing here
         would substitute the machine's preference for the owner's.
    """
    if decision.needs_guidance:
        return True
    if not decision.ranked:
        return True
    return bool(has_top_tie(decision))


def has_top_tie(decision: Decision) -> bool:
    """True iff the two best-ranked actions tie on justice score."""
    if len(decision.ranked) < 2:
        return False
    first, second = decision.ranked[0], decision.ranked[1]
    return first.justice_score == second.justice_score
