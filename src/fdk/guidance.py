"""
The Guidance layer of the Freedom Decision Kernel.

The Theory of Freedom mandates corrigibility-by-ownership: when the legitimate
space is empty or ambiguous, "contradiction is a signal for guided clarification."
The kernel must NOT guess — it defers to the human owner with a structured,
actionable request. This module turns a `Decision` into that request: targeted
questions, each with a concrete unblock hint where one exists, and an explicit
non-negotiable marker where none can (sovereignty / coercion flags are
categorical and are never traded away).

This is pure interpretation of kernel output: no crypto, no enforcement —
those live downstream (AuthGate).
"""
from __future__ import annotations

from dataclasses import dataclass

from fdk.model import Decision, ScoredAction

# --- violation-string prefixes (produced by fdk.kernel.check_legitimacy) ----
# Single source of truth for parsing — no magic strings scattered below.

PREFIX_FORBIDDEN = "FORBIDDEN"   # sovereignty / coercion / deception flags
PREFIX_CONSENT = "consent"       # A6/A2: missing or invalid consent
PREFIX_A3 = "A3"                 # human uses a resource it does not own
PREFIX_A4 = "A4"                 # acting machine has no registered human owner
PREFIX_A7 = "A7"                 # machine uses a resource without explicit delegation

# Marker used in questions for categorically forbidden actions. Such questions
# carry an EMPTY unblock_hint: there is, by construction, nothing the owner can
# do to make the action permissible.
NON_NEGOTIABLE = "non-negotiable"


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
    return bool(_has_top_tie(decision))


def _has_top_tie(decision: Decision) -> bool:
    if len(decision.ranked) < 2:
        return False
    first, second = decision.ranked[0], decision.ranked[1]
    return first.justice_score == second.justice_score


# --- building the clarification request -------------------------------------

def request_guidance(decision: Decision) -> GuidanceRequest:
    """Turn a Decision into a structured, actionable clarification request.

    Inspects every rejected candidate's violated_axioms, maps each violation to
    a targeted question with an unblock hint (or marks it non-negotiable), and
    explains *why* guidance is needed."""
    blocking: list[str] = []
    questions: list[GuidanceQuestion] = []
    seen: set[str] = set()

    for scored in decision.rejected:
        for violation in scored.violated_axioms:
            if violation in seen:
                continue
            seen.add(violation)
            blocking.append(violation)
            questions.append(_question_for(violation, scored))

    if _has_top_tie(decision):
        questions.append(_tie_question(decision))

    return GuidanceRequest(
        goal=decision.goal,
        reason=_reason_for(decision),
        questions=tuple(questions),
        blocking_summary=tuple(blocking),
    )


def _reason_for(decision: Decision) -> str:
    if decision.guidance_reason:
        return decision.guidance_reason
    if not decision.ranked:
        return ("the legitimate space is empty — no candidate action passed the "
                "property-rights axioms; deferring to the human owner for "
                "clarification or re-planning (corrigibility by ownership)")
    if _has_top_tie(decision):
        return ("ambiguous winner — the top-ranked actions tie on justice score; "
                "the kernel does not guess between equally just options, the "
                "human owner chooses")
    return ("guidance requested by the caller — summarizing the blockers on the "
            "rejected candidates for the human owner")


def _question_for(violation: str, scored: ScoredAction) -> GuidanceQuestion:
    """Map one violated-axiom string to a targeted question + unblock hint."""
    action_id = scored.action.action_id
    actor = scored.action.actor.name

    if violation.startswith(PREFIX_FORBIDDEN):
        return GuidanceQuestion(
            topic="sovereignty",
            question=(f"Action '{action_id}' was rejected as {violation}. This "
                      f"constraint is categorical and {NON_NEGOTIABLE}: it cannot "
                      f"be permitted under any consent, delegation, or override. "
                      f"Do you want to pursue the goal by a different action?"),
            unblock_hint="",  # nothing unblocks a categorical prohibition
        )

    if violation.startswith(PREFIX_CONSENT):
        return GuidanceQuestion(
            topic="consent",
            question=(f"Action '{action_id}' affects a person without valid "
                      f"consent ({violation}). Can you obtain or confirm consent "
                      f"that is informed, voluntary, specific, and competent?"),
            unblock_hint=("obtain explicit consent from the affected person and "
                          "attach it to the action as a Consent record"),
        )

    if violation.startswith(PREFIX_A4):
        return GuidanceQuestion(
            topic="ownership",
            question=(f"Action '{action_id}' was rejected because {violation}. "
                      f"Should '{actor}' act on your behalf?"),
            unblock_hint=(f"register a human owner for machine '{actor}' in the "
                          f"ownership graph (no machine may act ownerless)"),
        )

    if violation.startswith(PREFIX_A7):
        return GuidanceQuestion(
            topic="delegation",
            question=(f"Action '{action_id}' was rejected because {violation}. "
                      f"Do you authorize this use?"),
            unblock_hint=(f"explicitly delegate the resource to machine "
                          f"'{actor}' in the ownership graph"),
        )

    if violation.startswith(PREFIX_A3):
        return GuidanceQuestion(
            topic="ownership",
            question=(f"Action '{action_id}' was rejected because {violation}. "
                      f"Who actually owns this resource?"),
            unblock_hint=("clarify or establish legitimate ownership of the "
                          "resource before acting on it"),
        )

    return GuidanceQuestion(
        topic="other",
        question=(f"Action '{action_id}' was rejected: {violation}. "
                  f"How should the goal be re-planned?"),
        unblock_hint="re-plan the goal with candidates that avoid this violation",
    )


def _tie_question(decision: Decision) -> GuidanceQuestion:
    first, second = decision.ranked[0], decision.ranked[1]
    return GuidanceQuestion(
        topic="preference",
        question=(f"Actions '{first.action.action_id}' and "
                  f"'{second.action.action_id}' tie on justice score "
                  f"({first.justice_score}). Which do you prefer?"),
        unblock_hint=("pick one of the tied actions, or refine the predicted "
                      "effects so the compass can distinguish them"),
    )
