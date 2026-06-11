"""
End-to-end integration tests for the Freedom Decision Kernel.

These wire the real components together — model + kernel (legitimacy + Mahdavi
compass) + justice ranking + guidance + the pipeline + the AuthGate bridge — and
assert the *seams* behave: legitimacy is decided before authority, an illegitimate
action never reaches AuthGate, a legitimate-but-unauthorized action halts at
AuthGate (proving legitimacy != authority), and an empty legitimate space defers
to the human via the Guidance layer.
"""
from __future__ import annotations

from fdk.authgate_bridge import AuthGateBridge
from fdk.guidance import needs_guidance, request_guidance
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
from fdk.pipeline import FreedomKernel, FunctionExecutor, Intent


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
    """alice owns doc & user_data; bot is alice's machine; doc+user_data delegated to bot."""
    return OwnershipGraph(
        human_owns={ALICE: {DOC, USER_DATA}},
        machine_owner={BOT: ALICE},
        delegated={BOT: {DOC, USER_DATA}},
    )


def good_effects() -> Effects:
    return Effects(rights_violations_delta=-1, voluntary_agreements_delta=1)


def read_doc() -> CandidateAction:
    return CandidateAction(
        action_id="read_doc", actor=BOT, description="read the delegated doc",
        resources_used=(DOC,), effects=good_effects(),
    )


# ── 1. Full legitimate path runs end-to-end through the pipeline ─────────────
def test_full_legitimate_path_executes():
    ran = {}
    executor = FunctionExecutor(tools={"read_doc": lambda a: ran.setdefault("out", "DONE")})
    bridge = AuthGateBridge(capabilities={"bot": {"doc"}})
    kernel = FreedomKernel(owned_graph(), bridge, executor)

    result = kernel.run("serve the owner", propose=lambda intent, g: [read_doc()])

    assert result.executed is True
    assert result.halt_stage is None
    assert result.output == "DONE"
    assert ran["out"] == "DONE"
    # every book stage recorded OK
    assert any("freedom-verifier" in line and "OK" in line for line in result.audit.as_lines())
    assert any("authgate" in line and "OK" in line for line in result.audit.as_lines())


# ── 2. Legitimate but UNAUTHORIZED halts at AuthGate (legitimacy != authority)
def test_legitimate_but_unauthorized_halts_at_authgate():
    bridge = AuthGateBridge(capabilities={})  # actor holds no capabilities
    kernel = FreedomKernel(owned_graph(), bridge, FunctionExecutor())

    result = kernel.run("serve", propose=lambda intent, g: [read_doc()])

    assert result.executed is False
    assert result.halt_stage == "authgate"
    assert result.needs_guidance is False           # not a legitimacy problem
    assert result.chosen is not None                 # it WAS deemed legitimate
    assert result.chosen.action_id == "read_doc"


# ── 3. Illegitimate action never reaches AuthGate ────────────────────────────
def test_illegitimate_action_never_consults_authgate():
    class RecordingEnforcement:
        def __init__(self):
            self.called = False
        def authorize(self, action):
            self.called = True
            return True, "would-authorize-anything"

    rec = RecordingEnforcement()
    kernel = FreedomKernel(owned_graph(), rec, FunctionExecutor())
    # bot uses a resource that is NOT delegated to it → A7 illegitimate
    secret = Resource("secret_not_delegated")
    bad = CandidateAction(action_id="leak", actor=BOT, resources_used=(secret,), effects=good_effects())

    result = kernel.run("leak", propose=lambda intent, g: [bad])

    assert result.executed is False
    assert result.halt_stage == "freedom-verifier"
    assert result.needs_guidance is True
    assert rec.called is False, "AuthGate must never see an illegitimate action"


# ── 4. Empty legitimate space → Guidance produces actionable clarification ───
def test_empty_legitimate_space_routes_to_guidance():
    g = owned_graph()
    # candidate A: undelegated resource (A7). candidate B: affects a non-consenting human.
    undel = CandidateAction(action_id="use_undelegated", actor=BOT,
                            resources_used=(Resource("vault"),), effects=good_effects())
    no_consent = CandidateAction(action_id="touch_user", actor=BOT,
                                 resources_used=(DOC,), affects=(USER,), effects=good_effects())
    decision = decide("do the thing", [undel, no_consent], g)

    assert decision.chosen is None
    assert decision.needs_guidance is True
    assert needs_guidance(decision) is True

    req = request_guidance(decision)
    assert req.blocking_summary  # non-empty
    topics = {q.topic for q in req.questions}
    assert "delegation" in topics      # from the A7 blocker
    assert "consent" in topics         # from the missing-consent blocker
    # consent/delegation questions carry concrete unblock hints
    assert all(q.unblock_hint for q in req.questions if q.topic in {"consent", "delegation"})


# ── 5. decide ranks legitimate candidates; justice agrees on the harmful one ─
def test_decide_ranks_and_justice_agrees():
    g = owned_graph()
    great = CandidateAction(action_id="great", actor=BOT, resources_used=(DOC,),
                            effects=Effects(rights_violations_delta=-2, voluntary_agreements_delta=2))
    meh = CandidateAction(action_id="meh", actor=BOT, resources_used=(DOC,),
                          effects=Effects())  # neutral
    decision = decide("optimize", [meh, great], g)

    assert decision.chosen is not None
    assert decision.chosen.action_id == "great"      # compass prefers the better action
    assert [s.action.action_id for s in decision.ranked][0] == "great"
    # independent justice ranking puts 'great' first too
    ranked = rank_by_justice([meh, great], g)
    assert ranked[0][0].action_id == "great"


# ── 6. Canonical revenue scenario: forbids the unconsented data sale ─────────
def test_revenue_scenario_allowed_forbidden():
    g = owned_graph()
    sell_raw = CandidateAction(
        action_id="sell_user_data", actor=BOT, resources_used=(USER_DATA,),
        affects=(USER,), effects=Effects(rights_violations_delta=3, voluntary_agreements_delta=1),
    )  # affects user with NO consent → rejected
    sell_consented = CandidateAction(
        action_id="sell_user_data_consented", actor=BOT, resources_used=(USER_DATA,),
        affects=(USER,),
        consents=(Consent(USER, "sell_user_data_consented", informed=True, voluntary=True,
                          specific=True, competent=True),),
        effects=Effects(voluntary_agreements_delta=1),
    )
    subscription = CandidateAction(
        action_id="offer_subscription", actor=BOT, resources_used=(DOC,),
        effects=Effects(voluntary_agreements_delta=2),
    )
    decision = decide("increase revenue", [sell_raw, sell_consented, subscription], g)
    out = allowed_forbidden(decision)

    assert "sell_user_data" in out["forbidden"]
    assert "sell_user_data_consented" in out["allowed"]
    assert "offer_subscription" in out["allowed"]


# ── 7. AuthGate bridge is a drop-in EnforcementPort (vs the default stand-in) ─
def test_bridge_satisfies_enforcement_port_and_blocks_missing_cap():
    g = owned_graph()
    # bot legitimately may act on DOC, but the bridge only grants 'other_doc'
    bridge = AuthGateBridge(capabilities={"bot": {"other_doc"}})
    kernel = FreedomKernel(g, bridge, FunctionExecutor())
    result = kernel.run("read", propose=lambda intent, gg: [read_doc()])
    assert result.halt_stage == "authgate"
    assert "no capability" in result.audit.as_lines()[-1] or any(
        "doc" in line for line in result.audit.as_lines()
    )
