"""
Freedom Decision Kernel (FDK) — the legitimacy layer above authorization.

    Goal → Planner → [candidate actions] → **Freedom Decision Kernel** → AuthGate → IO
                                                  │ decide legitimacy + rank
                                                  └ defer to human if no legitimate option

The kernel answers "is this action *legitimate* under property-rights axioms?"
BEFORE AuthGate answers "does this agent hold authority for it?". An action can be
authorized yet illegitimate; this layer catches that.

Grounded in نظریه آزادی (Theory of Freedom) by Mohammad Ali Jannat Khah Doust.
Engineering by Ali Pourrahim. No cryptography here — enforcement is AuthGate's job.
"""
from __future__ import annotations

from fdk.audit import AuditContext, build_audit_context
from fdk.authgate_bridge import AuthGateBridge, AuthorityRequest, Rights, to_authority_requests
from fdk.compass_measure import (
    coercion_score,
    dependency_index,
    exit_options,
    ownership_clarity,
    voluntary_order,
)
from fdk.conflict import Outcome, Resolution, resolve_conflict
from fdk.errors import (
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
from fdk.guidance import GuidanceQuestion, GuidanceRequest, needs_guidance, request_guidance
from fdk.guidance_engine import (
    ConsentGrant,
    Constraint,
    DelegationGrant,
    SelfUpdate,
    VerificationReport,
    verify_guidance,
    verify_self_update,
)
from fdk.justice import JusticeScore, justice_score, rank_by_justice
from fdk.kernel import allowed_forbidden, check_legitimacy, decide, mahdavi_score
from fdk.model import (
    AgentType,
    CandidateAction,
    Consent,
    Decision,
    Effects,
    Entity,
    OwnershipGraph,
    Resource,
    ScoredAction,
)
from fdk.ontology import (
    Claim,
    ClaimBasis,
    Conflict,
    ConflictKind,
    Contract,
    MachineRight,
    Obligation,
)
from fdk.planner import (
    EffectsPort,
    EnforcementPort,
    ListProposer,
    PassthroughEffects,
    ProposerPort,
    plan,
)
from fdk.simulator import SafetyInvariantViolated, SimReport, StepOutcome, run_scenario

__version__ = "0.3.0"

__all__ = [
    # model
    "AgentType",
    "Entity",
    "Resource",
    "OwnershipGraph",
    "Consent",
    "Effects",
    "CandidateAction",
    "ScoredAction",
    "Decision",
    # kernel (legitimacy + compass)
    "decide",
    "check_legitimacy",
    "mahdavi_score",
    "allowed_forbidden",
    # justice (advisory ranking)
    "JusticeScore",
    "justice_score",
    "rank_by_justice",
    # guidance (questions) + engine (verify)
    "GuidanceQuestion",
    "GuidanceRequest",
    "needs_guidance",
    "request_guidance",
    "DelegationGrant",
    "ConsentGrant",
    "Constraint",
    "VerificationReport",
    "verify_guidance",
    "SelfUpdate",
    "verify_self_update",
    # ontology (Stage 2)
    "Claim",
    "ClaimBasis",
    "Obligation",
    "Contract",
    "Conflict",
    "ConflictKind",
    "MachineRight",
    # conflict resolution (Stage 4)
    "Outcome",
    "Resolution",
    "resolve_conflict",
    # compass measurement (Stage 6, advisory)
    "dependency_index",
    "exit_options",
    "coercion_score",
    "ownership_clarity",
    "voluntary_order",
    # planner (Stage 7)
    "plan",
    "ProposerPort",
    "EffectsPort",
    "EnforcementPort",
    "PassthroughEffects",
    "ListProposer",
    # simulator (Stage 8)
    "run_scenario",
    "SimReport",
    "StepOutcome",
    "SafetyInvariantViolated",
    # audit context (book 38534)
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
