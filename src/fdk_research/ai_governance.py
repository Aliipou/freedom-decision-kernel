"""AI governance — advisory layer (FDK 2.0, Layer 8). RESEARCH LAYER.

The frozen kernel knows two kinds of agent: a HUMAN (a rights-holder) and a MACHINE
(a tool with a human owner, never a rights-holder or owner). Layer 8 asks the question
that pressure makes unavoidable: as agents become autonomous — AGI, ASI, agent
societies, autonomous corporations — can a non-human agent be an owner or hold rights?

The roadmap is emphatic: do NOT rush AGI rights; finish the human model first;
answering "yes" may change the primitive. So this stays OUTSIDE the frozen kernel as
advisory classification. It maps an agent's situation to a governance status and is
brutally honest that the interesting cases (a machine OWNING, a machine holding RIGHTS)
are simply NOT representable in v1.0 — representing them is a primitive change, gated.
Advisory only: no ALLOW/DENY, no mutation, imports nothing into `fdk_kernel`.
See `spec/AI_GOVERNANCE.md`. Mirrors the discipline of `spec/STANDING.md`.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AgentStatus(Enum):
    """How a non-human agent stands relative to the frozen kernel."""

    TOOL_OF_OWNER = "tool-of-owner"            # machine + registered human owner: the v1.0 case
    AUTONOMOUS_UNOWNED = "autonomous-unowned"  # no human owner: A4 fails → kernel denies (rogue)
    CLAIMS_PERSONHOOD = "claims-personhood"    # AI asserts rights/ownership: NOT in v1.0
    COLLECTIVE_OF_AGENTS = "collective-of-agents"  # AI corp/DAO: defer to Aggregation


@dataclass(frozen=True)
class AgentFacts:
    """An advisory description of an AI agent's situation — supplied by a human, not
    read from the kernel (which only knows HUMAN/MACHINE + ownership)."""

    has_human_owner: bool
    acts_within_delegation: bool = True
    claims_rights_or_ownership: bool = False
    is_collective: bool = False


@dataclass(frozen=True)
class GovernanceAssessment:
    status: AgentStatus
    representable_in_v1: bool
    rationale: str
    recommendation: str


def assess_agent_governance(facts: AgentFacts) -> GovernanceAssessment:
    """Classify a non-human agent's governance status. Pure, deterministic, advisory —
    never a verdict, never grants a machine ownership/standing inside v1.0."""
    # A collective of agents (AI corporation / DAO) is a group-ownership question.
    if facts.is_collective:
        return GovernanceAssessment(
            AgentStatus.COLLECTIVE_OF_AGENTS, representable_in_v1=False,
            rationale="a collective of agents is a group owner, which v1.0 cannot "
                      "represent (one resource has one human owner).",
            recommendation="Defer to the Aggregation layer (spec/AGGREGATION.md); do "
                           "not treat the collective as a kernel owner.",
        )

    # An AI claiming rights or ownership: the open primitive question.
    if facts.claims_rights_or_ownership:
        return GovernanceAssessment(
            AgentStatus.CLAIMS_PERSONHOOD, representable_in_v1=False,
            rationale="a machine OWNING property or HOLDING rights is NOT representable "
                      "in v1.0 — the kernel's rights-holders are HUMAN; a MACHINE is a "
                      "tool. Granting machine standing may change the primitive.",
            recommendation="Out-of-frame. Route to the Standing research program "
                           "(spec/STANDING.md, the AGI case); do NOT grant ownership.",
        )

    # No registered human owner: the kernel denies the machine's actions (A4), and an
    # ungoverned machine seizing power is treated as an aggressor (the gate is sound).
    if not facts.has_human_owner:
        return GovernanceAssessment(
            AgentStatus.AUTONOMOUS_UNOWNED, representable_in_v1=True,
            rationale="an ownerless machine fails A4, so the kernel denies its actions; "
                      "an ungoverned agent seizing power is an aggressor to defend against.",
            recommendation="Containable within v1.0 (deny + defend); assign a human "
                           "owner to make it legitimately operable, or treat as rogue.",
        )

    # A tool of its owner — the kernel's native, fully-representable case.
    scope_note = ("acting within its delegation" if facts.acts_within_delegation
                  else "acting OUTSIDE its delegation (the kernel will deny those acts via A7)")
    return GovernanceAssessment(
        AgentStatus.TOOL_OF_OWNER, representable_in_v1=True,
        rationale=f"a machine with a registered human owner, {scope_note}.",
        recommendation="Represent normally — the owner's delegation governs; the kernel "
                       "decides each action structurally.",
    )


def is_v1_governable(facts: AgentFacts) -> bool:
    """Convenience: can v1.0 represent this agent's governance at all (even as a
    denial)? False only for the genuinely out-of-frame cases (personhood/collective)."""
    return assess_agent_governance(facts).representable_in_v1
