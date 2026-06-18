"""
fdk_runtime — the production policy-engine layer of the Freedom Decision Kernel.

    Planner -> [candidate action] -> fdk_runtime.PolicyEngine -> AuthGate -> IO

This is the PRODUCT surface: a fail-closed, observable, serializable wrapper that
turns one agent action into ALLOW / DENY / DEFER, composing the frozen legitimacy
kernel with an optional authority check and audit sink. It is deliberately kept
apart from the research track and imports ONLY `fdk_kernel` (deterministic) —
never `fdk_research`. See PRODUCTION_READINESS.md for what is and is not in scope.

Grounded in نظریه آزادی (Theory of Freedom) by Mohammad Ali Jannat Khah Doust.
Engineering by Ali Pourrahim.
"""
from __future__ import annotations

from fdk_runtime.codec import CodecError, decode_request
from fdk_runtime.engine import (
    AuditSink,
    AuthorityFn,
    Clock,
    DeferPolicy,
    PolicyDecision,
    PolicyEngine,
    Verdict,
    evaluate,
    high_stakes_defer,
)
from fdk_runtime.sidecar import handle_decide, make_handler, serve

__version__ = "0.1.0"

__all__ = [
    # engine
    "PolicyEngine",
    "PolicyDecision",
    "Verdict",
    "evaluate",
    "high_stakes_defer",
    # types
    "AuthorityFn",
    "DeferPolicy",
    "AuditSink",
    "Clock",
    # codec
    "decode_request",
    "CodecError",
    # sidecar
    "handle_decide",
    "make_handler",
    "serve",
]
