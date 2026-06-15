"""
Planner (Stage 7) — implements spec/PLANNER.md: Generate → Filter → Rank → Choose.

This is where the Decision Kernel proper lives. It wires the existing pieces
together: a (untrusted) proposer GENERATES candidates, the legitimacy gate
FILTERS them (hard, deterministic), the Mahdavi compass RANKS the survivors, and
a small set of CHOOSE rules pick one or defer to a human.

Honest seams:
  - ProposerPort is untrusted: proposal quality bounds decision quality
    ("LLM proposes, the Freedom kernel disposes").
  - EffectsPort predicts an action's Effects. `PassthroughEffects` is the honest
    stub (trusts declared Effects); a real predictor/simulator is Stage 6/8.
  - The four CHOOSE rules: C-EMPTY/C-TIE (defer via guidance.needs_guidance),
    P-NEG (best legitimate action is compass-negative → defer, prediction
    unvalidated), C-AUTH (legitimacy != authority → walk the ranked list for the
    best AuthGate-authorized action, else defer).
"""
from __future__ import annotations

from dataclasses import replace
from typing import Protocol

from fdk_kernel.guidance import GuidanceRequest, needs_guidance
from fdk_kernel.model import CandidateAction, Decision, Effects, OwnershipGraph
from fdk_research.decision import decide
from fdk_research.guidance_resolution import request_guidance


class ProposerPort(Protocol):
    """Generates candidate actions for a goal. UNTRUSTED — anything it omits
    (resources_used, affects, forbidden flags) defeats the gate, so the gate is
    only as honest as the proposer."""

    def propose(self, goal: str, graph: OwnershipGraph) -> list[CandidateAction]: ...


class EffectsPort(Protocol):
    """Predicts an action's Effects (the compass inputs). The hard, unbuilt part
    (Stage 6/8); today the default just trusts the proposer's declared Effects."""

    def predict(self, action: CandidateAction, graph: OwnershipGraph) -> Effects: ...


class EnforcementPort(Protocol):
    """Authority check (AuthGate). Returns (authorized, reason)."""

    def authorize(self, action: CandidateAction) -> tuple[bool, str]: ...


class PassthroughEffects:
    """Honest stub EffectsPort: trusts the proposer's declared Effects. The
    ranking is only as good as those predictions — and we say so."""

    def predict(self, action: CandidateAction, graph: OwnershipGraph) -> Effects:
        return action.effects


class ListProposer:
    """Trivial ProposerPort over a fixed candidate list (for tests / wiring)."""

    def __init__(self, candidates: list[CandidateAction]) -> None:
        self._candidates = list(candidates)

    def propose(self, goal: str, graph: OwnershipGraph) -> list[CandidateAction]:
        return list(self._candidates)


def plan(
    goal: str,
    proposer: ProposerPort,
    graph: OwnershipGraph,
    *,
    effects_port: EffectsPort | None = None,
    enforcement: EnforcementPort | None = None,
) -> Decision | GuidanceRequest:
    """Run the full kernel for a goal. Returns a Decision with a chosen action,
    or a GuidanceRequest when the kernel must defer to the human owner."""
    ep: EffectsPort = effects_port if effects_port is not None else PassthroughEffects()

    # GENERATE → predict effects (passthrough = identity).
    proposed = proposer.propose(goal, graph)
    candidates = [replace(c, effects=ep.predict(c, graph)) for c in proposed]

    # FILTER + RANK (legitimacy gate + Mahdavi compass) via the kernel.
    decision = decide(goal, candidates, graph)

    # CHOOSE.
    # C-EMPTY (no legitimate option) and C-TIE (ambiguous top) → defer.
    if needs_guidance(decision):
        return request_guidance(decision)

    best = decision.ranked[0]

    # P-NEG: the best legitimate action still moves AWAY from rights non-violation.
    # The compass prediction is unvalidated, so neither act nor hard-reject — defer.
    if (best.justice_score or 0.0) < 0.0:
        deferred = replace(
            decision, chosen=None, needs_guidance=True,
            guidance_reason=(
                "the best legitimate action is compass-negative (moves away from "
                "universal rights non-violation); the prediction is unvalidated — "
                "defer to the human owner"
            ),
        )
        return request_guidance(deferred)

    # C-AUTH: legitimacy is not authority. Walk the ranked list for the best
    # AuthGate-authorized action; if none is authorized, defer.
    if enforcement is not None:
        for scored in decision.ranked:
            authorized, _reason = enforcement.authorize(scored.action)
            if authorized:
                return replace(decision, chosen=scored.action)
        deferred = replace(
            decision, chosen=None, needs_guidance=True,
            guidance_reason=(
                "every legitimate action was denied by AuthGate (no held capability); "
                "defer to the human owner to grant authority or re-plan"
            ),
        )
        return request_guidance(deferred)

    return decision
