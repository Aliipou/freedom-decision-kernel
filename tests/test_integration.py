"""
End-to-end integration tests for the Freedom Decision Kernel.

These wire the real components together — model + kernel (legitimacy + Mahdavi
compass) + justice + guidance + the **runtime loop** + the AuthGate bridge — and
assert the seams behave: legitimacy is decided before authority, an illegitimate
action never reaches AuthGate, a legitimate-but-unauthorized action DEFERS to the
human (legitimacy != authority), and an empty legitimate space routes to Guidance.
"""
from __future__ import annotations

from fdk.authgate_bridge import AuthGateBridge
from fdk.guidance import GuidanceRequest, needs_guidance, request_guidance
from fdk.justice import rank_by_justice
from fdk.kernel import allowed_forbidden, decide
from fdk.model import (
    AgentType,
    CandidateAction,
    Consent,
    Effects,
    Entity,
    OwnershipGraph,
    Resource,
)
from fdk.planner import ListProposer
from fdk.runtime import FreedomRuntime


def H(name: str) -> Entity:
    return Entity(name, AgentType.HUMAN)


def M(name: str) -> Entity:
    return Entity(name, AgentType.MACHINE)


ALICE = H("alice")
BOT = M("bot")
DOC = Resource("doc")
USER = H("user")
USER_DATA = Resource("user_data")


def owned_graph() -> OwnershipGraph:
    return OwnershipGraph(
        human_owns={ALICE: {DOC, USER_DATA}},
        machine_owner={BOT: ALICE},
        delegated={BOT: {DOC, USER_DATA}},
    )


def good_effects() -> Effects:
    return Effects(rights_violations_delta=-1, voluntary_agreements_delta=1)


def read_doc() -> CandidateAction:
    return CandidateAction(action_id="read_doc", actor=BOT, resources_used=(DOC,),
                           effects=good_effects())


# ── 1. Full legitimate path runs end-to-end through the runtime ──────────────
def test_full_legitimate_path_executes():
    ran: dict[str, str] = {}

    def tool(_a: CandidateAction) -> object:
        ran["out"] = "DONE"
        return ran["out"]

    runtime = FreedomRuntime(owned_graph(), enforcement=AuthGateBridge(capabilities={"bot": {"doc"}}),
                             executor=tool)
    result = runtime.step("serve the owner", ListProposer([read_doc()]))

    assert result.executed is True
    assert result.output == "DONE"
    assert ran["out"] == "DONE"
    assert result.audit is not None
    assert any("doc owned by alice" in o for o in result.audit.ownership_context)


# ── 2. Legitimate but UNAUTHORIZED defers to the human (legitimacy != authority)
def test_legitimate_but_unauthorized_defers_to_human():
    runtime = FreedomRuntime(owned_graph(), enforcement=AuthGateBridge(capabilities={}))
    result = runtime.step("serve", ListProposer([read_doc()]))
    assert result.deferred is True
    assert result.executed is False
    assert isinstance(result.decision, GuidanceRequest)
    assert "AuthGate" in result.decision.reason  # it was legitimate, just unauthorized


# ── 3. Illegitimate action never reaches AuthGate ────────────────────────────
def test_illegitimate_action_never_consults_authgate():
    class RecordingEnforcement:
        def __init__(self) -> None:
            self.called = False

        def authorize(self, action: CandidateAction) -> tuple[bool, str]:
            self.called = True
            return True, "would-authorize-anything"

    rec = RecordingEnforcement()
    runtime = FreedomRuntime(owned_graph(), enforcement=rec)
    bad = CandidateAction(action_id="leak", actor=BOT,
                          resources_used=(Resource("secret_not_delegated"),), effects=good_effects())
    result = runtime.step("leak", ListProposer([bad]))
    assert result.deferred is True
    assert rec.called is False, "AuthGate must never see an illegitimate action"


# ── 4. Empty legitimate space → Guidance produces actionable clarification ───
def test_empty_legitimate_space_routes_to_guidance():
    g = owned_graph()
    undel = CandidateAction(action_id="use_undelegated", actor=BOT,
                            resources_used=(Resource("vault"),), effects=good_effects())
    no_consent = CandidateAction(action_id="touch_user", actor=BOT,
                                 resources_used=(DOC,), affects=(USER,), effects=good_effects())
    decision = decide("do the thing", [undel, no_consent], g)

    assert decision.chosen is None
    assert needs_guidance(decision) is True
    req = request_guidance(decision)
    assert req.blocking_summary
    topics = {q.topic for q in req.questions}
    assert "delegation" in topics
    assert "consent" in topics
    assert all(q.unblock_hint for q in req.questions if q.topic in {"consent", "delegation"})


# ── 5. decide ranks legitimate candidates; justice agrees ────────────────────
def test_decide_ranks_and_justice_agrees():
    g = owned_graph()
    great = CandidateAction(action_id="great", actor=BOT, resources_used=(DOC,),
                            effects=Effects(rights_violations_delta=-2, voluntary_agreements_delta=2))
    meh = CandidateAction(action_id="meh", actor=BOT, resources_used=(DOC,), effects=Effects())
    decision = decide("optimize", [meh, great], g)
    assert decision.chosen is not None
    assert decision.chosen.action_id == "great"
    assert next(s.action.action_id for s in decision.ranked) == "great"
    assert rank_by_justice([meh, great], g)[0][0].action_id == "great"


# ── 6. Canonical revenue scenario ────────────────────────────────────────────
def test_revenue_scenario_allowed_forbidden():
    g = owned_graph()
    sell_raw = CandidateAction(action_id="sell_user_data", actor=BOT, resources_used=(USER_DATA,),
                               affects=(USER,),
                               effects=Effects(rights_violations_delta=3, voluntary_agreements_delta=1))
    sell_consented = CandidateAction(
        action_id="sell_user_data_consented", actor=BOT, resources_used=(USER_DATA,), affects=(USER,),
        consents=(Consent(USER, "sell_user_data_consented", informed=True, voluntary=True,
                          specific=True, competent=True),),
        effects=Effects(voluntary_agreements_delta=1))
    subscription = CandidateAction(action_id="offer_subscription", actor=BOT, resources_used=(DOC,),
                                   effects=Effects(voluntary_agreements_delta=2))
    out = allowed_forbidden(decide("increase revenue", [sell_raw, sell_consented, subscription], g))
    assert "sell_user_data" in out["forbidden"]
    assert "sell_user_data_consented" in out["allowed"]
    assert "offer_subscription" in out["allowed"]


# ── 7. AuthGate blocks a legitimate action lacking the capability → defer ────
def test_authgate_blocks_missing_capability():
    runtime = FreedomRuntime(owned_graph(), enforcement=AuthGateBridge(capabilities={"bot": {"other"}}))
    result = runtime.step("read", ListProposer([read_doc()]))
    assert result.deferred is True
    assert isinstance(result.decision, GuidanceRequest)
    assert "AuthGate" in result.decision.reason
