"""
fdk_runtime.engine — the production policy-decision facade.

This is the PRODUCT surface of FDK: a fail-closed, observable, serializable call
that turns one agent action into a single verdict — ALLOW / DENY / DEFER — with
reasons and an audit record. It composes the frozen legitimacy kernel
(`fdk_kernel.check_legitimacy`) with an optional AuthGate authority check and an
optional audit sink, in the production topology:

    Planner -> [candidate action] -> PolicyEngine.evaluate
                                        |-- legitimacy gate   (fdk_kernel)
                                        |-- authority check   (AuthGate, optional)
                                        '-- audit sink        (optional)
                                     -> ALLOW / DENY / DEFER

CARDINAL INVARIANT — fail-closed. Any malformed input, internal error, failed
graph validation, or audit-sink failure yields **DENY**, never ALLOW. An action
is ALLOWED only when every consulted check explicitly passed. No code path
returns ALLOW from an exception handler. (`tests/test_runtime_engine.py` pins
this.)

SCOPE — this layer is the *product*, deliberately separate from the research
track. It imports ONLY `fdk_kernel` (deterministic); it does NOT import
`fdk_research`. The experimental layers (Standing, Aggregation, Consent-
Authenticity, …) never gate a production decision. A policy engine for
in-frame agent actions (competent, living, consenting principals — SaaS /
agentic / enterprise) does not need the open philosophical frontiers solved;
see PRODUCTION_READINESS.md for exactly what is and is not in scope.
"""
from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from fdk_kernel import (
    AuthGateBridge,
    CandidateAction,
    Op,
    OwnershipGraph,
    check_legitimacy,
)
from fdk_kernel import __version__ as _FDK_VERSION

# An authority oracle: "may this action's actor exercise authority for it?".
# Either an AuthGateBridge (has `.authorize`) or any callable with this shape.
AuthorityFn = Callable[[CandidateAction], tuple[bool, str]]
# A defer policy: returns a human-readable reason to DEFER a *legitimate* action
# to a human (e.g. high-stakes / irreversible), or None to let it proceed.
DeferPolicy = Callable[[CandidateAction, OwnershipGraph], "str | None"]
# An audit sink: called with every emitted decision. A raising sink is treated
# as fail-closed (no un-audited ALLOW).
AuditSink = Callable[["PolicyDecision"], None]
# A clock returning an ISO-8601 timestamp string (injectable for determinism).
Clock = Callable[[], str]

_FREEZE_VERSION = "1.0"


class Verdict(StrEnum):
    """The three-valued production verdict. `str`-valued so it serializes and
    compares as its name with zero ceremony."""

    ALLOW = "ALLOW"
    DENY = "DENY"
    DEFER = "DEFER"


@dataclass(frozen=True)
class PolicyDecision:
    """One serializable, auditable decision record for a single agent action."""

    verdict: Verdict
    action_id: str
    actor: str
    reasons: tuple[str, ...] = ()
    axiom_trace: tuple[str, ...] = ()
    resources: tuple[str, ...] = ()
    authority_consulted: bool = False
    authority_ok: bool | None = None
    fail_closed: bool = False
    fdk_version: str = _FDK_VERSION
    freeze_version: str = _FREEZE_VERSION
    decided_at: str = ""

    @property
    def allowed(self) -> bool:
        """True ONLY for an explicit ALLOW — the single bit an executor should
        branch on. DEFER and DENY are both 'do not execute now'."""
        return self.verdict is Verdict.ALLOW

    def to_dict(self) -> dict[str, object]:
        return {
            "verdict": self.verdict.value,
            "action_id": self.action_id,
            "actor": self.actor,
            "reasons": list(self.reasons),
            "axiom_trace": list(self.axiom_trace),
            "resources": list(self.resources),
            "authority_consulted": self.authority_consulted,
            "authority_ok": self.authority_ok,
            "fail_closed": self.fail_closed,
            "fdk_version": self.fdk_version,
            "freeze_version": self.freeze_version,
            "decided_at": self.decided_at,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _axiom_trace(violations: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    """Extract the compact axiom/flag codes from the kernel's violation strings,
    for the PolicyDecision contract's `axiom_trace` (e.g. 'A7: …' -> 'A7',
    'FORBIDDEN (coercion)' -> 'FORBIDDEN(coercion)', 'consent: …' -> 'consent').
    Order-preserving and de-duplicated."""
    codes: list[str] = []
    for violation in violations:
        head = violation.split(":", 1)[0].strip()
        code = head.replace(" (", "(") if head.startswith("FORBIDDEN") else head
        if code and code not in codes:
            codes.append(code)
    return tuple(codes)


def _safe_str(value: object, default: str) -> str:
    """Best-effort string extraction for the fail-closed path, where `action`
    may itself be malformed. Never raises."""
    if value is None:
        return default
    try:
        text = str(value).strip()
    except Exception:
        return default
    return text or default


# Irreversible / high-stakes operations: legitimate consent does not make them
# *reversible*. The default high-stakes defer recommends a human confirm before
# the kernel's ALLOW becomes execution. Opt-in (engine default does not DEFER).
_IRREVERSIBLE_OPS = frozenset({Op.DELETE, Op.TRANSFER, Op.SPEND, Op.ENCUMBER_EXIT})


def high_stakes_defer(action: CandidateAction, _graph: OwnershipGraph) -> str | None:
    """A ready-made `DeferPolicy`: DEFER any legitimate action that performs an
    irreversible operation (DELETE / TRANSFER / SPEND / ENCUMBER_EXIT), so a
    human confirms before an agent does something it cannot take back. Pass it
    as `PolicyEngine(defer_policy=high_stakes_defer)`."""
    for resource, op in action.uses():
        if op in _IRREVERSIBLE_OPS:
            return (
                f"legitimate, but '{op.name}' on '{resource.name}' is irreversible / "
                "high-stakes — recommend human confirmation before execution"
            )
    return None


class PolicyEngine:
    """Fail-closed policy engine. Construct once (wiring authority / defer /
    audit), then call `evaluate(action, graph)` per agent action.

    * ``authority`` — an `AuthGateBridge` or any `(action) -> (ok, reason)`
      callable. When set, a legitimate action must ALSO pass authority or it is
      DENIED. When ``None``, the engine decides legitimacy only (legitimacy is
      the *prior* question; AuthGate may run as a separate downstream stage).
    * ``defer_policy`` — maps a legitimate action to a DEFER reason or None.
      Use `high_stakes_defer` for an out-of-the-box irreversible-op gate.
    * ``audit_sink`` — receives every decision. A raising sink fails closed.
    * ``clock`` — injectable ISO-timestamp source (determinism in tests).
    """

    def __init__(
        self,
        *,
        authority: AuthGateBridge | AuthorityFn | None = None,
        defer_policy: DeferPolicy | None = None,
        audit_sink: AuditSink | None = None,
        clock: Clock = _utc_now,
    ) -> None:
        self._authority = self._normalize_authority(authority)
        self._defer_policy = defer_policy
        self._audit_sink = audit_sink
        self._clock = clock

    @staticmethod
    def _normalize_authority(
        authority: AuthGateBridge | AuthorityFn | None,
    ) -> AuthorityFn | None:
        if authority is None:
            return None
        if isinstance(authority, AuthGateBridge):
            return authority.authorize
        return authority

    def evaluate(self, action: CandidateAction, graph: OwnershipGraph) -> PolicyDecision:
        """Decide one action. Returns a `PolicyDecision`; never raises."""
        try:
            decision = self._decide(action, graph)
        except Exception as exc:  # fail-closed: an error never becomes an ALLOW
            decision = self._fail_closed(action, exc, where="decision")
        decision = self._emit(action, decision)
        return decision

    def _emit(self, action: CandidateAction, decision: PolicyDecision) -> PolicyDecision:
        if self._audit_sink is None:
            return decision
        try:
            self._audit_sink(decision)
        except Exception as exc:
            # An un-auditable decision is not safe to ALLOW. Fail closed. We do
            # NOT re-emit the replacement (a raising sink would loop).
            return self._fail_closed(action, exc, where="audit sink")
        return decision

    def _decide(self, action: CandidateAction, graph: OwnershipGraph) -> PolicyDecision:
        now = self._clock()
        graph.validate()  # malformed graph -> raises -> fail-closed DENY upstream
        action_id = action.action_id
        actor = action.actor.name
        resources = tuple(resource.name for resource, _op in action.uses())

        permissible, violations = check_legitimacy(action, graph)
        if not permissible:
            return PolicyDecision(
                Verdict.DENY, action_id, actor,
                reasons=tuple(violations), axiom_trace=_axiom_trace(violations),
                resources=resources, decided_at=now,
            )

        if self._defer_policy is not None:
            reason = self._defer_policy(action, graph)
            if reason:
                return PolicyDecision(
                    Verdict.DEFER, action_id, actor,
                    reasons=(reason,), resources=resources, decided_at=now,
                )

        if self._authority is not None:
            ok, why = self._authority(action)
            if not ok:
                return PolicyDecision(
                    Verdict.DENY, action_id, actor,
                    reasons=(why,), resources=resources,
                    authority_consulted=True, authority_ok=False, decided_at=now,
                )
            return PolicyDecision(
                Verdict.ALLOW, action_id, actor,
                reasons=(why,), resources=resources,
                authority_consulted=True, authority_ok=True, decided_at=now,
            )

        return PolicyDecision(
            Verdict.ALLOW, action_id, actor,
            reasons=("legitimate under the property-rights axioms",),
            resources=resources, decided_at=now,
        )

    def _fail_closed(
        self, action: CandidateAction, exc: Exception, *, where: str
    ) -> PolicyDecision:
        action_id = _safe_str(getattr(action, "action_id", None), "<unknown>")
        actor = _safe_str(getattr(getattr(action, "actor", None), "name", None), "<unknown>")
        reason = f"fail-closed: error in {where}: {type(exc).__name__}: {exc}"
        try:
            now = self._clock()
        except Exception:
            now = ""
        return PolicyDecision(
            Verdict.DENY, action_id, actor,
            reasons=(reason,), fail_closed=True, decided_at=now,
        )


_DEFAULT_ENGINE = PolicyEngine()


def evaluate(action: CandidateAction, graph: OwnershipGraph) -> PolicyDecision:
    """Module-level convenience: decide one action with a default (legitimacy-
    only, no authority/audit) engine. For anything beyond a smoke test,
    construct a `PolicyEngine` with the wiring you need."""
    return _DEFAULT_ENGINE.evaluate(action, graph)
