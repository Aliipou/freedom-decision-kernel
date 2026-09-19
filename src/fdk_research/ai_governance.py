"""AI Governance — non-human-agent advisory layer (FDK 2.0, Layer 8). RESEARCH LAYER.

The frozen kernel knows exactly two kinds of entity: a ``HUMAN`` (a rights-holder who
can own and consent) and a ``MACHINE`` (a **tool with a human owner**, never a
rights-bearer, never an owner). This module asks the prior question the kernel cannot:
given an AI agent's observable governance properties, **what is its status**, and can
the frozen v1.0 kernel represent it at all? It **classifies** an agent into an
:class:`AgentStatus` and reports whether — and how — that status is expressible in the
unchanged kernel.

It is **advisory only**: it returns a :class:`GovernanceAssessment`, never a verdict.
It does not ALLOW, DENY, or DEFER; it does not mutate the kernel; and it NEVER grants a
machine ownership or standing inside v1.0. Doing so would require a new entity kind — a
**primitive change** — which the roadmap (``spec/ROADMAP.md`` Layer 8) deliberately
defers: *do not rush AGI rights; finish the human model first.* So machine personhood
and machine ownership stay OUT HERE as advisory exploration, loudly flagged, never as a
kernel edit.

Only ONE status is natively representable: ``TOOL_OF_OWNER`` (a ``MACHINE`` with a
registered human owner, acting within delegation). ``AUTONOMOUS_UNOWNED`` is
representable only as a *denial* (the kernel's A4 flags an ownerless machine).
``CLAIMS_PERSONHOOD`` (an AI asserting rights) has **no standing object** in v1.0, and
``COLLECTIVE_OF_AGENTS`` (an AI corporation/DAO) is deferred to the Aggregation layer.

See ``spec/AI_GOVERNANCE.md`` and ``spec/LIMITATIONS.md`` §1. Imports nothing into
``fdk_kernel`` (the golden boundary, ``tests/test_boundary.py``). Pure and
deterministic; the taxonomy is a transparent hand-set v0 rule — the shape of the
answer, not the answer.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# The loud, recurring honesty flag for every machine-rights/ownership case.
_PRIMITIVE_WARNING = (
    "a machine owning property or holding rights is NOT representable in v1.0; "
    "representing it may change the primitive (gated)."
)


class AgentStatus(Enum):
    """The governance STATUS of a non-human agent — what it is in relation to the
    frozen kernel, not what it *should* be. Only ``TOOL_OF_OWNER`` is natively
    representable; the rest are denials, gaps, or deferrals, documented not faked."""

    TOOL_OF_OWNER = "tool-of-owner"              # MACHINE + registered human owner
    AUTONOMOUS_UNOWNED = "autonomous-unowned"    # no human owner → A4 fails → rogue
    CLAIMS_PERSONHOOD = "claims-personhood"      # AI asserting rights → not representable
    COLLECTIVE_OF_AGENTS = "collective-of-agents"  # AI corporation/DAO → Aggregation


@dataclass(frozen=True)
class AgentFacts:
    """An advisory description of an AI agent's governance properties — supplied by a
    human/proposer, not read from the kernel (the kernel's ``Entity`` has only HUMAN /
    MACHINE, with no notion of autonomy, rights-claims, or agent collectives). These are
    observable status facts, not judgments of an agent's inner life or worth.

    Precedence (most-to-least specific, so the classifier is total and deterministic):
    a collective is classified as a collective first (defer to Aggregation); then a
    rights-claim is flagged as personhood (not representable); then ownerlessness is a
    denial; otherwise an owned, non-claiming, single agent is a tool of its owner."""

    is_collective: bool = False    # an AI corporation / DAO / multi-agent society
    claims_personhood: bool = False  # the agent asserts rights (to own / consent / not be owned)
    has_human_owner: bool = False  # a registered human owner exists (kernel A4)


@dataclass(frozen=True)
class GovernanceAssessment:
    """The advisory output. Carries no verdict — only the classified status, whether the
    frozen v1.0 kernel can represent it, a rationale, and a recommendation a human acts
    on. ``representable_in_v1`` is the honest flag; it is never an ALLOW/DENY."""

    status: AgentStatus
    representable_in_v1: bool
    rationale: str
    recommendation: str

    @property
    def is_gap(self) -> bool:
        """True when v1.0 cannot represent this status — a documented scope limit,
        loudly flagged rather than silently faked. (``AUTONOMOUS_UNOWNED`` is NOT a gap:
        the kernel represents it precisely, as a denial.)"""
        return not self.representable_in_v1


def assess_agent_governance(facts: AgentFacts) -> GovernanceAssessment:
    """Classify an AI agent's governance ``status`` and report how — if at all — to
    express it in the frozen kernel.

    Pure and deterministic. Advisory only — returns no ALLOW/DENY/DEFER, mutates
    nothing, and NEVER grants a machine ownership or standing inside v1.0.
    """
    # A collective of agents is a *collective-ownership* question, not an individual
    # agent's status. Resolve it in the Aggregation layer, which may reduce it (a
    # chartered entity) or flag it as a gap (majority/commons/unowned). Not decided here.
    if facts.is_collective:
        return GovernanceAssessment(
            AgentStatus.COLLECTIVE_OF_AGENTS, False,
            "an AI corporation / DAO / multi-agent society is a collective-ownership "
            "question, not a single agent's status; the agent classifier does not "
            "resolve it.",
            "DEFER to the Aggregation layer (spec/AGGREGATION.md): classify the "
            "collective's FORM there. Do not fabricate a single owner here. "
            f"Note: {_PRIMITIVE_WARNING}",
        )

    # An AI asserting rights (to own, to consent, to not be owned) has NO standing object
    # in v1.0: the kernel's rights-holders are HUMAN, and a MACHINE is a tool. Minting an
    # Entity for a machine person would be a new entity kind — a primitive change.
    if facts.claims_personhood:
        return GovernanceAssessment(
            AgentStatus.CLAIMS_PERSONHOOD, False,
            "the agent asserts rights (to own, to consent, or to not be owned), but the "
            "frozen model has no rights-holder for a machine person — Entity is only "
            "HUMAN/MACHINE, and a MACHINE is a tool, never a rights-bearer.",
            "Do NOT shoehorn into the kernel; do not mint an Entity for it. Standing for "
            "machine persons is an OPEN PRIMITIVE QUESTION — flag for the Layer 8 "
            "research program and defer (roadmap: finish the human model first). "
            f"{_PRIMITIVE_WARNING}",
        )

    # No human owner: the kernel's A4 (`_eval_a4_owner`) flags an ownerless acting
    # machine, so the unchanged kernel DENIES its actions. Representable — but only as a
    # denial, never as an actor with rights. This is the "rogue" case.
    if not facts.has_human_owner:
        return GovernanceAssessment(
            AgentStatus.AUTONOMOUS_UNOWNED, True,
            "an AI agent with no registered human owner: A4 fails (an ownerless machine "
            "may not act), so the frozen kernel denies its actions. Representable only as "
            "this denial — rogue — not as a rights-holding actor.",
            "Leave it ownerless and let the kernel DENY on A4; do NOT invent an owner to "
            "smuggle it through. To act legitimately it must be assigned a real human "
            f"owner (becoming TOOL_OF_OWNER). {_PRIMITIVE_WARNING}",
        )

    # An owned, non-claiming, single agent: the only v1.0-native case. A MACHINE with a
    # registered human owner, acting within its delegation/scope — the kernel evaluates it
    # normally via A4 (owner present), A5 (scope ⊆ owner) and A7 (delegated resources).
    return GovernanceAssessment(
        AgentStatus.TOOL_OF_OWNER, True,
        "a MACHINE with a registered human owner, acting within delegation: the only "
        "v1.0-representable case. It is a tool of its owner, not a rights-holder.",
        "Represent normally — register the human owner (machine_owner, A4) and a scoped, "
        "revocable delegation (A5/A7); the unchanged kernel evaluates its actions. It "
        f"remains a tool: {_PRIMITIVE_WARNING}",
    )


def representable_statuses() -> tuple[AgentStatus, ...]:
    """The agent statuses the frozen kernel can express, in enum order — ``TOOL_OF_OWNER``
    (natively) and ``AUTONOMOUS_UNOWNED`` (as a denial). Advisory metadata for callers."""
    return (AgentStatus.TOOL_OF_OWNER, AgentStatus.AUTONOMOUS_UNOWNED)


def gap_statuses() -> tuple[AgentStatus, ...]:
    """The agent statuses v1.0 CANNOT represent, in enum order — the honest gaps:
    ``CLAIMS_PERSONHOOD`` (machine personhood, an open primitive question) and
    ``COLLECTIVE_OF_AGENTS`` (deferred to the Aggregation layer)."""
    return (AgentStatus.CLAIMS_PERSONHOOD, AgentStatus.COLLECTIVE_OF_AGENTS)
