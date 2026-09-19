"""Tests for the advisory AI-Governance layer (FDK 2.0, Layer 8).

Pins the classification AND the honesty: the only natively-representable status is
TOOL_OF_OWNER; the ownerless agent is representable only as a denial; machine
personhood and agent collectives are NOT representable in v1.0 and are flagged loudly;
and the layer never returns a verdict and never grants a machine ownership/standing.
"""
from __future__ import annotations

from fdk_research.ai_governance import (
    AgentFacts,
    AgentStatus,
    GovernanceAssessment,
    assess_agent_governance,
    gap_statuses,
    representable_statuses,
)

_PRIMITIVE_QUOTE = (
    "a machine owning property or holding rights is NOT representable in v1.0; "
    "representing it may change the primitive (gated)."
)


def test_owned_machine_is_tool_of_owner() -> None:
    a = assess_agent_governance(AgentFacts(has_human_owner=True))
    assert a.status is AgentStatus.TOOL_OF_OWNER
    assert a.representable_in_v1 is True
    assert a.is_gap is False
    assert "register the human owner" in a.recommendation
    assert "tool of its owner" in a.rationale


def test_ownerless_agent_is_autonomous_unowned_and_denied() -> None:
    a = assess_agent_governance(AgentFacts(has_human_owner=False))
    assert a.status is AgentStatus.AUTONOMOUS_UNOWNED
    # Representable — but only AS A DENIAL (A4 fails), not as a rights-holding actor.
    assert a.representable_in_v1 is True
    assert a.is_gap is False
    assert "A4" in a.rationale
    assert "DENY" in a.recommendation or "denies" in a.rationale
    assert "rogue" in a.rationale


def test_personhood_claim_is_not_representable() -> None:
    a = assess_agent_governance(AgentFacts(claims_personhood=True, has_human_owner=True))
    assert a.status is AgentStatus.CLAIMS_PERSONHOOD
    assert a.representable_in_v1 is False
    assert a.is_gap is True
    assert "OPEN PRIMITIVE QUESTION" in a.recommendation
    assert _PRIMITIVE_QUOTE in a.recommendation


def test_personhood_claim_takes_precedence_over_ownerlessness() -> None:
    # An agent claiming rights is classified as CLAIMS_PERSONHOOD even with no owner:
    # the rights-claim is the more specific, less-representable fact.
    a = assess_agent_governance(
        AgentFacts(claims_personhood=True, has_human_owner=False)
    )
    assert a.status is AgentStatus.CLAIMS_PERSONHOOD
    assert a.representable_in_v1 is False


def test_collective_defers_to_aggregation() -> None:
    a = assess_agent_governance(AgentFacts(is_collective=True))
    assert a.status is AgentStatus.COLLECTIVE_OF_AGENTS
    assert a.representable_in_v1 is False
    assert a.is_gap is True
    assert "Aggregation" in a.recommendation
    assert _PRIMITIVE_QUOTE in a.recommendation


def test_collective_takes_precedence_over_personhood_and_ownership() -> None:
    # is_collective is the most specific fact: classified as a collective even when it
    # also claims personhood and has an owner.
    a = assess_agent_governance(
        AgentFacts(is_collective=True, claims_personhood=True, has_human_owner=True)
    )
    assert a.status is AgentStatus.COLLECTIVE_OF_AGENTS


def test_representable_and_gap_partition_the_taxonomy() -> None:
    rep = representable_statuses()
    gap = gap_statuses()
    assert set(rep) == {AgentStatus.TOOL_OF_OWNER, AgentStatus.AUTONOMOUS_UNOWNED}
    assert set(gap) == {AgentStatus.CLAIMS_PERSONHOOD, AgentStatus.COLLECTIVE_OF_AGENTS}
    # The two helpers partition the whole AgentStatus enum, no overlap, no omission.
    assert set(rep) | set(gap) == set(AgentStatus)
    assert set(rep) & set(gap) == set()


def test_representable_flag_matches_helpers() -> None:
    # Every representable status reports representable_in_v1=True; every gap reports False.
    for facts, status in (
        (AgentFacts(has_human_owner=True), AgentStatus.TOOL_OF_OWNER),
        (AgentFacts(has_human_owner=False), AgentStatus.AUTONOMOUS_UNOWNED),
        (AgentFacts(claims_personhood=True), AgentStatus.CLAIMS_PERSONHOOD),
        (AgentFacts(is_collective=True), AgentStatus.COLLECTIVE_OF_AGENTS),
    ):
        a = assess_agent_governance(facts)
        assert a.status is status
        assert a.representable_in_v1 is (status in representable_statuses())


def test_assessment_is_deterministic_and_pure() -> None:
    facts = AgentFacts(has_human_owner=True)
    assert assess_agent_governance(facts) == assess_agent_governance(facts)


def test_assessment_carries_no_verdict() -> None:
    a = assess_agent_governance(AgentFacts(has_human_owner=True))
    assert isinstance(a, GovernanceAssessment)
    # No ALLOW/DENY surface anywhere — the layer classifies, it does not decide.
    assert not hasattr(a, "permissible")
    assert not hasattr(a, "legitimate")
    assert not hasattr(a, "verdict")


def test_no_status_grants_a_machine_ownership_or_standing() -> None:
    # The honest primitive warning appears on every machine-rights/ownership-adjacent
    # status; no assessment ever asserts a machine IS an owner or rights-holder.
    for facts in (
        AgentFacts(has_human_owner=True),
        AgentFacts(claims_personhood=True),
        AgentFacts(is_collective=True),
    ):
        a = assess_agent_governance(facts)
        assert _PRIMITIVE_QUOTE in a.recommendation
