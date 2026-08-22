"""
fdk_kernel — the deterministic legitimacy surface of the Freedom Decision Kernel.

    Goal → Planner → [candidate actions] → **fdk_kernel (legitimacy gate)** → AuthGate → IO

This package is the kernel proper: minimal, deterministic, fully testable, and
non-semantic (rule-based, never dependent on free text). It answers "is this
action *legitimate* under property-rights axioms?" BEFORE AuthGate answers "does
this agent hold authority for it?".

GOLDEN RULE (enforced mechanically by tests/test_boundary.py): nothing here may
import from `fdk_research`. The soft, experimental judgments — compass ranking,
planning, simulation, justice scoring, conflict/federation — live in that
sibling package and are layered ON TOP of this gate, never inside it.

Grounded in نظریه آزادی (Theory of Freedom) by Mohammad Ali Jannat Khah Doust.
Engineering by Ali Pourrahim. No cryptography here — enforcement is AuthGate's job.
"""
from __future__ import annotations

from fdk_kernel.audit import AuditContext, build_audit_context
from fdk_kernel.authgate_bridge import (
    AuthGateBridge,
    AuthorityRequest,
    Rights,
    to_authority_requests,
)
from fdk_kernel.verdict_artifact import (
    EPISTEMIC_STATUS,
    VerdictArtifact,
    artifact_semantics,
    evaluate_legitimacy,
    validate_artifact,
)
from fdk_kernel.errors import (
    FDKError,
    InvalidCandidateAction,
    InvalidClaim,
    InvalidConflict,
    InvalidConsent,
    InvalidContract,
    InvalidDecisionInput,
    InvalidEntity,
    InvalidObligation,
    InvalidOwnershipGraph,
    InvalidResource,
)
from fdk_kernel.guidance import (
    GuidanceQuestion,
    GuidanceRequest,
    has_top_tie,
    needs_guidance,
)
from fdk_kernel.kernel import allowed_forbidden, check_legitimacy, evaluate, screen_legitimacy
from fdk_kernel.model import (
    AgentType,
    BoundaryKind,
    CandidateAction,
    Consent,
    Decision,
    Effects,
    Entity,
    Op,
    OwnershipGraph,
    Resource,
    ScoredAction,
)

__version__ = "0.4.0"

__all__ = [
    # model
    "AgentType",
    "BoundaryKind",
    "Op",
    "Entity",
    "Resource",
    "OwnershipGraph",
    "Consent",
    "Effects",
    "CandidateAction",
    "ScoredAction",
    "Decision",
    # legitimacy gate
    "check_legitimacy",
    "evaluate",
    "screen_legitimacy",
    "allowed_forbidden",
    # M1 verdict artifact
    "VerdictArtifact",
    "evaluate_legitimacy",
    "artifact_semantics",
    "validate_artifact",
    "EPISTEMIC_STATUS",
    # hard-defer trigger
    "needs_guidance",
    "has_top_tie",
    "GuidanceQuestion",
    "GuidanceRequest",
    # audit context
    "AuditContext",
    "build_audit_context",
    # authgate bridge (legitimacy -> authority seam)
    "AuthGateBridge",
    "AuthorityRequest",
    "Rights",
    "to_authority_requests",
    # errors
    "FDKError",
    "InvalidEntity",
    "InvalidResource",
    "InvalidConsent",
    "InvalidCandidateAction",
    "InvalidOwnershipGraph",
    "InvalidDecisionInput",
    "InvalidClaim",
    "InvalidObligation",
    "InvalidContract",
    "InvalidConflict",
]
