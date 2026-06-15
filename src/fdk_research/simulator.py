"""
FreedomSim (Stage 8) — a small-world simulator that stress-tests the kernel.

It runs a sequence of (goal, candidate-actions) steps through the planner over an
OwnershipGraph and records the outcome of each. Its job is to falsify the kernel:
after every step it asserts the SAFETY INVARIANT that the kernel never *chose* an
illegitimate action. Conflicts and empty legitimate spaces must surface as
deferrals, not as silent bad choices.

This is the cheap proving ground the theory demands before anything real: a place
to watch whether the rules stay consistent and non-exploitable across many
scenarios (markets, multi-agent, etc.). It builds nothing new about the theory —
it only exercises what the kernel already decides.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from fdk_kernel.audit import AuditContext, build_audit_context
from fdk_kernel.guidance import GuidanceRequest
from fdk_kernel.kernel import check_legitimacy
from fdk_kernel.model import CandidateAction, OwnershipGraph
from fdk_research.planner import EnforcementPort, ListProposer, plan


@dataclass(frozen=True)
class StepOutcome:
    goal: str
    chosen_id: str | None
    deferred: bool
    reason: str
    audit: AuditContext | None = None  # ownership/consent/justification for a chosen action


@dataclass
class SimReport:
    outcomes: list[StepOutcome] = field(default_factory=list)

    def chosen_ids(self) -> list[str]:
        return [o.chosen_id for o in self.outcomes if o.chosen_id is not None]

    def deferrals(self) -> list[StepOutcome]:
        return [o for o in self.outcomes if o.deferred]


class SafetyInvariantViolated(AssertionError):
    """Raised if the kernel ever chose an illegitimate action — a simulator bug
    or, worse, a kernel bug. Never expected to fire."""


def run_scenario(
    graph: OwnershipGraph,
    steps: list[tuple[str, list[CandidateAction]]],
    *,
    enforcement: EnforcementPort | None = None,
) -> SimReport:
    """Run each (goal, candidates) step through the planner against `graph`.

    After each step, assert the safety invariant: any chosen action must pass
    `check_legitimacy`. Returns a report of every step's outcome."""
    report = SimReport()
    for goal, candidates in steps:
        result = plan(goal, ListProposer(candidates), graph, enforcement=enforcement)

        if isinstance(result, GuidanceRequest):
            report.outcomes.append(StepOutcome(goal, None, True, result.reason))
            continue

        # plan() returns a Decision only WITH a chosen action (it defers via a
        # GuidanceRequest otherwise), so a chosen-less Decision is unreachable.
        chosen = result.chosen
        if chosen is None:  # pragma: no cover - plan() never returns a chosen-less Decision
            continue
        ok, violations = check_legitimacy(chosen, graph)
        if not ok:  # pragma: no cover - safety guard; fires only if the kernel is broken
            raise SafetyInvariantViolated(
                f"kernel chose an illegitimate action {chosen.action_id!r}: {violations}"
            )
        report.outcomes.append(
            StepOutcome(
                goal, chosen.action_id, False, result.guidance_reason,
                build_audit_context(chosen, graph, result.guidance_reason or "permitted"),
            )
        )
    return report
