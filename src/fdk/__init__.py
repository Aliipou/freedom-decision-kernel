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

from fdk.authgate_bridge import AuthGateBridge, AuthorityRequest, Rights, to_authority_requests
from fdk.errors import (
    FDKError,
    InvalidCandidateAction,
    InvalidConsent,
    InvalidDecisionInput,
    InvalidEntity,
    InvalidOwnershipGraph,
    InvalidResource,
)
from fdk.guidance import GuidanceQuestion, GuidanceRequest, needs_guidance, request_guidance
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

__version__ = "0.2.0"

__all__ = [
    # model
    "AgentType",
    # authgate bridge (legitimacy -> authority seam)
    "AuthGateBridge",
    "AuthorityRequest",
    "CandidateAction",
    "Consent",
    "Decision",
    "Effects",
    "Entity",
    # errors
    "FDKError",
    # guidance (corrigibility)
    "GuidanceQuestion",
    "GuidanceRequest",
    "InvalidCandidateAction",
    "InvalidConsent",
    "InvalidDecisionInput",
    "InvalidEntity",
    "InvalidOwnershipGraph",
    "InvalidResource",
    # justice (advisory ranking)
    "JusticeScore",
    "OwnershipGraph",
    "Resource",
    "Rights",
    "ScoredAction",
    "allowed_forbidden",
    "check_legitimacy",
    # kernel (legitimacy + compass)
    "decide",
    "justice_score",
    "mahdavi_score",
    "needs_guidance",
    "rank_by_justice",
    "request_guidance",
    "to_authority_requests",
]
