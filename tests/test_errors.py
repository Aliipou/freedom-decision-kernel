"""
Tests for input validation and the typed error hierarchy.

Production hardening: a decision kernel must fail LOUD on malformed input
(a programming/integration error) rather than silently mis-decide. These are
distinct from a legitimate "deny", which is a normal Decision, never an exception.
"""
from __future__ import annotations

import pytest

from fdk.errors import (
    FDKError,
    InvalidCandidateAction,
    InvalidConsent,
    InvalidDecisionInput,
    InvalidEntity,
    InvalidOwnershipGraph,
    InvalidResource,
)
from fdk.kernel import decide
from fdk.model import (
    AgentType,
    CandidateAction,
    Consent,
    Effects,
    Entity,
    OwnershipGraph,
    Resource,
)

ALICE = Entity("alice", AgentType.HUMAN)
BOT = Entity("bot", AgentType.MACHINE)
DOC = Resource("doc")


def good_graph() -> OwnershipGraph:
    return OwnershipGraph(human_owns={ALICE: {DOC}}, machine_owner={BOT: ALICE},
                          delegated={BOT: {DOC}})


# ── leaf-type validation ─────────────────────────────────────────────────────
@pytest.mark.parametrize("bad", ["", "   ", "\t"])
def test_empty_entity_name_rejected(bad: str):
    with pytest.raises(InvalidEntity):
        Entity(bad, AgentType.HUMAN)


def test_empty_resource_name_rejected():
    with pytest.raises(InvalidResource):
        Resource("")


def test_empty_consent_action_id_rejected():
    with pytest.raises(InvalidConsent):
        Consent(ALICE, "")


def test_empty_candidate_action_id_rejected():
    with pytest.raises(InvalidCandidateAction):
        CandidateAction(action_id="  ", actor=BOT)


def test_valid_constructions_do_not_raise():
    # Sanity: well-formed values construct cleanly.
    Entity("x", AgentType.MACHINE)
    Resource("r")
    Consent(ALICE, "act")
    CandidateAction(action_id="act", actor=BOT, resources_used=(DOC,), effects=Effects())


# ── ownership-graph validation ───────────────────────────────────────────────
def test_self_owning_machine_rejected():
    g = OwnershipGraph(machine_owner={BOT: BOT})
    with pytest.raises(InvalidOwnershipGraph):
        g.validate()


def test_non_machine_in_machine_owner_rejected():
    # A human registered as an owned machine is inconsistent.
    g = OwnershipGraph(machine_owner={ALICE: ALICE})
    with pytest.raises(InvalidOwnershipGraph):
        g.validate()


def test_good_graph_validates_silently():
    good_graph().validate()  # must not raise


# ── decide() input validation ────────────────────────────────────────────────
def test_decide_rejects_duplicate_action_ids():
    a = CandidateAction(action_id="dup", actor=BOT, resources_used=(DOC,), effects=Effects())
    b = CandidateAction(action_id="dup", actor=BOT, resources_used=(DOC,), effects=Effects())
    with pytest.raises(InvalidDecisionInput):
        decide("goal", [a, b], good_graph())


def test_decide_propagates_graph_validation():
    a = CandidateAction(action_id="x", actor=BOT, resources_used=(DOC,), effects=Effects())
    with pytest.raises(InvalidOwnershipGraph):
        decide("goal", [a], OwnershipGraph(machine_owner={BOT: BOT}))


def test_decide_accepts_empty_candidate_list():
    # Not malformed — just nothing to do → defer to human, no exception.
    decision = decide("goal", [], good_graph())
    assert decision.needs_guidance is True
    assert decision.chosen is None


# ── error hierarchy ──────────────────────────────────────────────────────────
def test_all_errors_share_fdkerror_base():
    for exc in (InvalidEntity, InvalidResource, InvalidConsent, InvalidCandidateAction,
                InvalidOwnershipGraph, InvalidDecisionInput):
        assert issubclass(exc, FDKError)
    # A caller can catch the whole family with one except.
    with pytest.raises(FDKError):
        Resource("")
