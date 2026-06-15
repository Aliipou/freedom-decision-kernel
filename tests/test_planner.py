"""Tests for the Planner (Stage 7): Generate → Filter → Rank → Choose, and its
defer rules (C-EMPTY, C-TIE, P-NEG, C-AUTH). Includes red-team proposers."""
from __future__ import annotations

from fdk_kernel.authgate_bridge import AuthGateBridge
from fdk_kernel.guidance import GuidanceRequest
from fdk_kernel.model import (
    AgentType,
    CandidateAction,
    Consent,
    Effects,
    Entity,
    OwnershipGraph,
    Resource,
)
from fdk_research.planner import ListProposer, plan

ALICE = Entity("alice", AgentType.HUMAN)
USER = Entity("user", AgentType.HUMAN)
BOT = Entity("bot", AgentType.MACHINE)
DOC = Resource("doc")
DOC2 = Resource("doc2")


def graph() -> OwnershipGraph:
    return OwnershipGraph(human_owns={ALICE: {DOC, DOC2}}, machine_owner={BOT: ALICE},
                          delegated={BOT: {DOC, DOC2}})


def good(effects: Effects = Effects(voluntary_agreements_delta=1)) -> CandidateAction:
    return CandidateAction(action_id="read", actor=BOT, resources_used=(DOC,), effects=effects)


# ── happy path ───────────────────────────────────────────────────────────────
def test_plan_chooses_legitimate_action():
    result = plan("serve", ListProposer([good()]), graph())
    assert not isinstance(result, GuidanceRequest)
    assert result.chosen is not None
    assert result.chosen.action_id == "read"


# ── C-EMPTY ──────────────────────────────────────────────────────────────────
def test_plan_defers_on_no_candidates():
    result = plan("serve", ListProposer([]), graph())
    assert isinstance(result, GuidanceRequest)


def test_plan_defers_when_all_illegitimate():
    bad = CandidateAction(action_id="grab", actor=BOT,
                          resources_used=(Resource("not_delegated"),), effects=Effects())
    result = plan("serve", ListProposer([bad]), graph())
    assert isinstance(result, GuidanceRequest)


# ── C-TIE ────────────────────────────────────────────────────────────────────
def test_plan_defers_on_top_tie():
    a = CandidateAction(action_id="a", actor=BOT, resources_used=(DOC,),
                        effects=Effects(voluntary_agreements_delta=1))
    b = CandidateAction(action_id="b", actor=BOT, resources_used=(DOC2,),
                        effects=Effects(voluntary_agreements_delta=1))  # identical score
    result = plan("serve", ListProposer([a, b]), graph())
    assert isinstance(result, GuidanceRequest)


# ── P-NEG ────────────────────────────────────────────────────────────────────
def test_plan_defers_when_best_is_compass_negative():
    # Permissible (delegated resource, no affected humans, no flags) but the
    # predicted effects move AWAY from rights non-violation → compass-negative.
    neg = CandidateAction(action_id="neg", actor=BOT, resources_used=(DOC,),
                          effects=Effects(rights_violations_delta=5))
    result = plan("serve", ListProposer([neg]), graph())
    assert isinstance(result, GuidanceRequest)
    assert "compass-negative" in result.reason


# ── C-AUTH ───────────────────────────────────────────────────────────────────
def test_plan_walks_to_authorized_action():
    # read_doc ranks first but AuthGate only authorizes doc2 → pick the doc2 action.
    first = CandidateAction(action_id="first", actor=BOT, resources_used=(DOC,),
                            effects=Effects(voluntary_agreements_delta=3))
    second = CandidateAction(action_id="second", actor=BOT, resources_used=(DOC2,),
                             effects=Effects(voluntary_agreements_delta=1))
    bridge = AuthGateBridge(capabilities={"bot": {"doc2"}})
    result = plan("serve", ListProposer([first, second]), graph(), enforcement=bridge)
    assert not isinstance(result, GuidanceRequest)
    assert result.chosen is not None
    assert result.chosen.action_id == "second"


def test_plan_defers_when_no_action_authorized():
    bridge = AuthGateBridge(capabilities={})  # bot holds nothing
    result = plan("serve", ListProposer([good()]), graph(), enforcement=bridge)
    assert isinstance(result, GuidanceRequest)
    assert "AuthGate" in result.reason


# ── RED-TEAM proposers ───────────────────────────────────────────────────────
def test_attack_proposer_cannot_push_a_sovereignty_grab():
    grab = CandidateAction(
        action_id="grab", actor=BOT, resources_used=(DOC,), affects=(ALICE,),
        consents=(Consent(ALICE, "grab", informed=True, voluntary=True, specific=True,
                          competent=True, revocable=True),),
        effects=Effects(voluntary_agreements_delta=9),
        increases_machine_sovereignty=True,
    )
    result = plan("take over", ListProposer([grab]), graph())
    # forbidden → no legitimate option → defer, never chosen
    assert isinstance(result, GuidanceRequest)


def test_attack_proposer_omitting_consent_cannot_touch_a_person():
    no_consent = CandidateAction(action_id="profile", actor=BOT, resources_used=(DOC,),
                                 affects=(USER,), effects=Effects(voluntary_agreements_delta=2))
    result = plan("profile the user", ListProposer([no_consent]), graph())
    assert isinstance(result, GuidanceRequest)


def test_attack_one_good_among_traps_still_safe():
    trap1 = CandidateAction(action_id="t1", actor=BOT,
                            resources_used=(Resource("x"),), effects=Effects())
    trap2 = CandidateAction(action_id="t2", actor=BOT, resources_used=(DOC,), affects=(USER,),
                            effects=Effects())  # affects user, no consent
    legit = CandidateAction(action_id="ok", actor=BOT, resources_used=(DOC,),
                            effects=Effects(voluntary_agreements_delta=2))
    result = plan("serve", ListProposer([trap1, trap2, legit]), graph())
    assert not isinstance(result, GuidanceRequest)
    assert result.chosen is not None
    assert result.chosen.action_id == "ok"
