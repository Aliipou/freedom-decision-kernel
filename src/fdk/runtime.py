"""
FreedomRuntime (Phase 10) — the full runtime loop.

The book's runtime pipeline (38416-38438) is:

    Observe → Reason (propose) → Decide (legitimacy) → Verify (compass) →
    Authorize (AuthGate) → Execute → Audit

This wires it end to end on the kernel's own pieces: the planner does
Decide+Verify+Authorize (Generate/Filter/Rank/Choose with the CHOOSE defer rules),
an audit context is attached to every executed decision, and execution is a
swappable port. It supersedes the MVP `pipeline.py` (which took the *first*
legitimate action) with the planner's compass-ranked choice.

Nothing here weakens the gate: a deferred decision never executes, and a chosen
action is the kernel's already-verified, ranked, authorized best option.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from fdk.audit import AuditContext, build_audit_context
from fdk.guidance import GuidanceRequest
from fdk.model import CandidateAction, Decision, OwnershipGraph
from fdk.planner import EnforcementPort, ProposerPort, plan

Executor = Callable[[CandidateAction], object]


@dataclass(frozen=True)
class RuntimeResult:
    """The outcome of one runtime step."""

    decision: Decision | GuidanceRequest
    deferred: bool            # True iff the kernel deferred to the human owner
    executed: bool            # True iff the chosen action ran to completion
    output: object | None     # the executor's output, if it ran
    audit: AuditContext | None  # ownership/consent/justification for a chosen action


class FreedomRuntime:
    """Runs the full loop for a goal: plan → (defer | audit → execute → audit)."""

    def __init__(
        self,
        graph: OwnershipGraph,
        *,
        enforcement: EnforcementPort | None = None,
        executor: Executor | None = None,
    ) -> None:
        self._graph = graph
        self._enforcement = enforcement
        self._executor = executor

    def step(self, goal: str, proposer: ProposerPort) -> RuntimeResult:
        # Reason + Decide + Verify + Authorize (the planner does all four).
        result = plan(goal, proposer, self._graph, enforcement=self._enforcement)

        # Defer: the kernel found no legitimate/authorized/clear action.
        if isinstance(result, GuidanceRequest):
            return RuntimeResult(result, deferred=True, executed=False, output=None, audit=None)

        chosen = result.chosen
        if chosen is None:  # pragma: no cover - plan() never returns a chosen-less Decision
            return RuntimeResult(result, deferred=True, executed=False, output=None, audit=None)

        # Audit the decision (book 38534) — recorded whether or not it executes.
        audit = build_audit_context(chosen, self._graph, "permitted by the Freedom kernel")

        # No executor wired: decide-only mode (the chosen action is returned to the caller).
        if self._executor is None:
            return RuntimeResult(result, deferred=False, executed=False, output=None, audit=audit)

        # Execute. A failed tool is a halt, not a crash.
        try:
            output = self._executor(chosen)
        except Exception:
            return RuntimeResult(result, deferred=False, executed=False, output=None, audit=audit)
        return RuntimeResult(result, deferred=False, executed=True, output=output, audit=audit)
