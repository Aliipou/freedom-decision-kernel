"""
Decision orchestration (research layer) — screen + rank.

The kernel (`fdk_kernel`) screens candidates for legitimacy and ranks NOTHING.
The compass (`fdk_research.compass`) ranks permissible actions but screens
nothing. `decide` is the orchestrator that needs BOTH: it asks the kernel which
candidates are legitimate, then applies the compass (veto + score) to rank the
survivors and defer when the legitimate space is empty.

This INVERSION is the whole point of the split: the dependency runs
research → kernel and research → compass, never kernel → research. The kernel
stays a pure, deterministic gate; the soft ranking lives entirely here.
"""
from __future__ import annotations

from fdk_kernel.errors import InvalidDecisionInput
from fdk_kernel.kernel import screen_legitimacy
from fdk_kernel.model import CandidateAction, Decision, OwnershipGraph, ScoredAction
from fdk_research.compass import mahdavi_score


def decide(goal: str, candidates: list[CandidateAction], graph: OwnershipGraph) -> Decision:
    """Run the full kernel+compass for a goal: screen candidates for legitimacy
    (kernel), rank the permissible ones by the Mahdavi compass, and defer to a
    human when the legitimate space is empty.

    Raises InvalidOwnershipGraph if the graph is inconsistent, and
    InvalidDecisionInput if two candidates share an action_id (which would make
    the ranked/allowed output ambiguous). Malformed input is a caller error, not
    a silent deny."""
    graph.validate()
    _reject_duplicate_ids(candidates)

    legitimate, rejected = screen_legitimacy(candidates, graph)

    ranked: list[ScoredAction] = []
    for scored in legitimate:
        action = scored.action
        score, rationale = mahdavi_score(action.effects)
        if score is None:  # compass veto turns a permissible action into a rejected one
            rejected.append(ScoredAction(
                action=action, permissible=False,
                violated_axioms=("FORBIDDEN (machine sovereignty increase)",),
                rationale=rationale,
            ))
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


def _reject_duplicate_ids(candidates: list[CandidateAction]) -> None:
    ids = [c.action_id for c in candidates]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise InvalidDecisionInput(f"duplicate candidate action_ids: {duplicates}")
