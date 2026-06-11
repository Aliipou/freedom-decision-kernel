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

__all__ = [
    "AgentType",
    "Entity",
    "Resource",
    "OwnershipGraph",
    "Consent",
    "Effects",
    "CandidateAction",
    "ScoredAction",
    "Decision",
    "decide",
    "check_legitimacy",
    "mahdavi_score",
    "allowed_forbidden",
]
