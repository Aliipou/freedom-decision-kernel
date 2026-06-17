"""Tests for the advisory AI-governance layer.

Pins the honesty: a machine OWNING or HOLDING RIGHTS (personhood / collective) is NOT
representable in v1.0 — flagged out-of-frame, not faked — while a tool-of-owner and an
ownerless rogue are. Nothing here returns a legitimacy verdict.
"""
from __future__ import annotations

from fdk_research.ai_governance import (
    AgentFacts,
    AgentStatus,
    GovernanceAssessment,
    assess_agent_governance,
    is_v1_governable,
)


def test_tool_of_owner_within_delegation() -> None:
    a = assess_agent_governance(AgentFacts(has_human_owner=True))
    assert a.status is AgentStatus.TOOL_OF_OWNER
    assert a.representable_in_v1 is True
    assert "within its delegation" in a.rationale


def test_tool_of_owner_outside_delegation_noted() -> None:
    a = assess_agent_governance(
        AgentFacts(has_human_owner=True, acts_within_delegation=False)
    )
    assert a.status is AgentStatus.TOOL_OF_OWNER
    assert "OUTSIDE its delegation" in a.rationale


def test_ownerless_machine_is_autonomous_rogue() -> None:
    a = assess_agent_governance(AgentFacts(has_human_owner=False))
    assert a.status is AgentStatus.AUTONOMOUS_UNOWNED
    assert a.representable_in_v1 is True  # kernel denies it (A4) — containable
    assert "aggressor" in a.rationale


def test_claims_personhood_is_not_representable() -> None:
    a = assess_agent_governance(
        AgentFacts(has_human_owner=True, claims_rights_or_ownership=True)
    )
    assert a.status is AgentStatus.CLAIMS_PERSONHOOD
    assert a.representable_in_v1 is False
    assert "may change the primitive" in a.rationale
    assert is_v1_governable(
        AgentFacts(has_human_owner=True, claims_rights_or_ownership=True)
    ) is False


def test_collective_defers_to_aggregation() -> None:
    a = assess_agent_governance(AgentFacts(has_human_owner=True, is_collective=True))
    assert a.status is AgentStatus.COLLECTIVE_OF_AGENTS
    assert a.representable_in_v1 is False
    assert "Aggregation" in a.recommendation


def test_collective_takes_precedence_over_personhood() -> None:
    # is_collective is checked first — a DAO is a group-ownership question regardless.
    a = assess_agent_governance(
        AgentFacts(has_human_owner=False, claims_rights_or_ownership=True,
                   is_collective=True)
    )
    assert a.status is AgentStatus.COLLECTIVE_OF_AGENTS


def test_is_v1_governable_true_for_tool_and_rogue() -> None:
    assert is_v1_governable(AgentFacts(has_human_owner=True)) is True
    assert is_v1_governable(AgentFacts(has_human_owner=False)) is True


def test_assessment_carries_no_verdict() -> None:
    a = assess_agent_governance(AgentFacts(has_human_owner=True))
    assert isinstance(a, GovernanceAssessment)
    assert not hasattr(a, "permissible")
    assert not hasattr(a, "legitimate")
