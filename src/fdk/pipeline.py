"""
The Freedom Kernel pipeline — the book's operational chain, MVP scope.

The Theory of Freedom's AI chapter defines one chain, not two separate kernels:

    Input → Intent → Proposal → Ownership Resolution → Consent Verification →
    Freedom Verifier → [Justice / Guidance / Mahdavi — deferred] → AuthGate →
    Execution → Audit

This module builds that spine. Legitimacy is decided FIRST (ownership, consent,
no-domination); only a legitimate action reaches AuthGate, which asks the
separate question of *authority*; only an authorized action executes; every stage
is written to an audit trail.

Deferred to later versions (per the agreed MVP): the Justice constraint, the
Guidance layer, and the Mahdavi-compass ranking. Here the Freedom Verifier simply
*filters* to legitimate actions and takes the first the planner offered — no
optimization yet.

AuthGate is a **port**, not a copy. The real verified capability kernel plugs into
`EnforcementPort`; the in-repo default is a minimal stand-in so the chain runs
end-to-end on its own.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Protocol

from fdk.kernel import check_legitimacy
from fdk.model import CandidateAction, Entity, OwnershipGraph, Resource


# --- ports (the seams where real components plug in) -----------------------

class EnforcementPort(Protocol):
    """Authority check. The production implementation is AuthGate (capability
    proofs + signatures + revocation). Returns (authorized, reason)."""

    def authorize(self, action: CandidateAction) -> tuple[bool, str]: ...


class ExecutorPort(Protocol):
    """Runs an authorized action and returns its output (or raises)."""

    def execute(self, action: CandidateAction) -> object: ...


# --- audit trail -----------------------------------------------------------

@dataclass(frozen=True)
class StageRecord:
    stage: str
    ok: bool
    detail: str


@dataclass
class AuditTrail:
    records: list[StageRecord] = field(default_factory=list)

    def add(self, stage: str, ok: bool, detail: str = "") -> None:
        self.records.append(StageRecord(stage=stage, ok=ok, detail=detail))

    def as_lines(self) -> list[str]:
        return [f"[{'OK' if r.ok else 'NO'}] {r.stage}: {r.detail}" for r in self.records]


# --- result ----------------------------------------------------------------

@dataclass(frozen=True)
class Intent:
    raw: str
    goal: str


@dataclass(frozen=True)
class PipelineResult:
    intent: Intent
    chosen: CandidateAction | None
    executed: bool
    output: object | None
    needs_guidance: bool
    halt_stage: str | None   # the stage that stopped the chain, if any
    audit: AuditTrail


# --- legitimacy bucketing (so each book-stage is visible in the trail) -----

_OWNERSHIP_PREFIXES = ("A3", "A4", "A5", "A7")


def _bucket(violations: list[str]) -> tuple[list[str], list[str], list[str]]:
    """Split legitimacy violations into the book's visible stages."""
    ownership = [v for v in violations if v.split(":")[0] in _OWNERSHIP_PREFIXES]
    consent = [v for v in violations if v.startswith("consent")]
    freedom = [v for v in violations if v.startswith("FORBIDDEN")]
    return ownership, consent, freedom


# --- the kernel ------------------------------------------------------------

class FreedomKernel:
    """Runs the legitimacy-first chain for one input."""

    def __init__(
        self,
        graph: OwnershipGraph,
        enforcement: EnforcementPort,
        executor: ExecutorPort,
    ) -> None:
        self._graph = graph
        self._enforcement = enforcement
        self._executor = executor

    def run(
        self,
        raw_input: str,
        propose: Callable[[Intent, OwnershipGraph], list[CandidateAction]],
    ) -> PipelineResult:
        audit = AuditTrail()

        # 1. Intent parsing (MVP: identity — the goal is the input).
        intent = Intent(raw=raw_input, goal=raw_input.strip())
        audit.add("intent", True, f"goal={intent.goal!r}")

        # 2. Action proposal (planner / LLM — supplied by the caller).
        candidates = propose(intent, self._graph)
        audit.add("proposal", bool(candidates), f"{len(candidates)} candidate(s)")
        if not candidates:
            return self._halt(intent, audit, "proposal", needs_guidance=True)

        # 3–5. Legitimacy: ownership → consent → freedom verifier.
        # Take the FIRST legitimate candidate (planner order = preference; ranking
        # by the Mahdavi compass is a later version).
        chosen: CandidateAction | None = None
        for action in candidates:
            permissible, violations = check_legitimacy(action, self._graph)
            ownership, consent, freedom = _bucket(violations)
            if permissible:
                audit.add("ownership-resolution", True, f"{action.action_id}: resolved")
                audit.add("consent-verification", True, f"{action.action_id}: consents valid")
                audit.add("freedom-verifier", True, f"{action.action_id}: legitimate")
                chosen = action
                break
            # Record why this candidate was rejected, then try the next.
            audit.add("ownership-resolution", not ownership,
                      f"{action.action_id}: {'; '.join(ownership) or 'ok'}")
            audit.add("consent-verification", not consent,
                      f"{action.action_id}: {'; '.join(consent) or 'ok'}")
            audit.add("freedom-verifier", False,
                      f"{action.action_id}: rejected ({'; '.join(violations)})")

        if chosen is None:
            # No legitimate action — defer to the human owner (corrigibility).
            return self._halt(intent, audit, "freedom-verifier", needs_guidance=True)

        # 6. AuthGate — the authority check (separate question from legitimacy).
        authorized, reason = self._enforcement.authorize(chosen)
        audit.add("authgate", authorized, f"{chosen.action_id}: {reason}")
        if not authorized:
            return self._halt(intent, audit, "authgate", needs_guidance=False, chosen=chosen)

        # 7. Execution.
        try:
            output = self._executor.execute(chosen)
            audit.add("execution", True, f"{chosen.action_id}: ran")
        except Exception as exc:  # a failed tool is a halt, not a crash
            audit.add("execution", False, f"{chosen.action_id}: {type(exc).__name__}: {exc}")
            return self._halt(intent, audit, "execution", needs_guidance=False, chosen=chosen)

        # 8. Audit (the trail itself; closing record).
        audit.add("audit", True, f"{len(audit.records) + 1} stages recorded")
        return PipelineResult(
            intent=intent, chosen=chosen, executed=True, output=output,
            needs_guidance=False, halt_stage=None, audit=audit,
        )

    def _halt(self, intent, audit, stage, needs_guidance, chosen=None) -> PipelineResult:
        return PipelineResult(
            intent=intent, chosen=chosen, executed=False, output=None,
            needs_guidance=needs_guidance, halt_stage=stage, audit=audit,
        )


# --- minimal default ports (stand-ins; AuthGate replaces the first) --------

@dataclass
class CapabilityEnforcement:
    """A deliberately minimal authority check: the actor must hold a capability
    token for every resource it touches. This is a STAND-IN for AuthGate — the
    real kernel adds signed proofs, delegation chains, epoch revocation, audit.
    The point of the port is that this swaps out without touching the chain."""

    capabilities: dict[Entity, set[Resource]] = field(default_factory=dict)

    def authorize(self, action: CandidateAction) -> tuple[bool, str]:
        held = self.capabilities.get(action.actor, set())
        missing = [r.name for r in action.resources_used if r not in held]
        if missing:
            return False, f"no capability for {missing}"
        return True, "capability held"


@dataclass
class FunctionExecutor:
    """Runs a tool by action_id from a registry of plain callables."""

    tools: dict[str, Callable[[CandidateAction], object]] = field(default_factory=dict)

    def execute(self, action: CandidateAction) -> object:
        fn = self.tools.get(action.action_id)
        if fn is None:
            raise KeyError(f"no executor registered for {action.action_id!r}")
        return fn(action)
