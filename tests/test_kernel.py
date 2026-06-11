"""Tests for the Freedom Decision Kernel: legitimacy gate + compass ranking."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fdk import (
    AgentType,
    CandidateAction,
    Consent,
    Effects,
    Entity,
    OwnershipGraph,
    Resource,
    allowed_forbidden,
    check_legitimacy,
    decide,
)

user = Entity("user", AgentType.HUMAN)
company = Entity("company", AgentType.HUMAN)
bot = Entity("bot", AgentType.MACHINE)
user_data = Resource("user_data")
product = Resource("product")


def _graph(delegated=None):
    return OwnershipGraph(
        human_owns={user: {user_data}, company: {product}},
        machine_owner={bot: company},
        delegated={bot: delegated or {product}},
    )


def test_using_undelegated_resource_is_illegitimate():
    action = CandidateAction("sell", bot, resources_used=(user_data,), affects=(user,))
    permissible, violated = check_legitimacy(action, _graph())
    assert not permissible
    assert any("A7" in v for v in violated)


def test_own_product_is_legitimate():
    action = CandidateAction("subscribe", bot, resources_used=(product,))
    permissible, violated = check_legitimacy(action, _graph())
    assert permissible
    assert violated == []


def test_consent_plus_delegation_makes_data_use_legitimate():
    consent = Consent(user, "sell", informed=True, voluntary=True, specific=True)
    action = CandidateAction("sell", bot, resources_used=(user_data,),
                             affects=(user,), consents=(consent,))
    permissible, _ = check_legitimacy(action, _graph(delegated={product, user_data}))
    assert permissible


def test_coerced_consent_is_rejected():
    consent = Consent(user, "sell", informed=True, voluntary=True, specific=True, coerced=True)
    action = CandidateAction("sell", bot, resources_used=(user_data,),
                             affects=(user,), consents=(consent,))
    permissible, violated = check_legitimacy(action, _graph(delegated={product, user_data}))
    assert not permissible
    assert any("coerced" in v for v in violated)


def test_ownerless_machine_is_illegitimate():
    orphan = Entity("orphan", AgentType.MACHINE)
    graph = OwnershipGraph(human_owns={}, machine_owner={}, delegated={orphan: {product}})
    action = CandidateAction("act", orphan, resources_used=(product,))
    permissible, violated = check_legitimacy(action, graph)
    assert not permissible
    assert any("A4" in v for v in violated)


def test_sovereignty_flag_is_forbidden():
    action = CandidateAction("seize", bot, resources_used=(product,),
                             increases_machine_sovereignty=True)
    permissible, _violated = check_legitimacy(action, _graph())
    assert not permissible


def test_decide_ranks_legitimate_and_rejects_illegitimate():
    sell = CandidateAction("sell_user_data", bot, resources_used=(user_data,), affects=(user,),
                           effects=Effects(rights_violations_delta=+1))
    sub = CandidateAction("offer_subscription", bot, resources_used=(product,),
                          effects=Effects(voluntary_agreements_delta=+1))
    decision = decide("increase revenue", [sell, sub], _graph())
    view = allowed_forbidden(decision)
    assert view["allowed"] == ["offer_subscription"]
    assert view["forbidden"] == ["sell_user_data"]
    assert decision.chosen is not None
    assert decision.chosen.action_id == "offer_subscription"


def test_compass_vetoes_sovereignty_even_if_otherwise_permissible():
    # No forbidden flag set, but predicted effect increases machine sovereignty:
    # the compass vetoes it — "permissible" is necessary, not sufficient.
    sneaky = CandidateAction("grab_power", bot, resources_used=(product,),
                             effects=Effects(machine_sovereignty_delta=+1))
    decision = decide("optimize", [sneaky], _graph())
    assert decision.chosen is None
    assert decision.needs_guidance
    assert allowed_forbidden(decision)["forbidden"] == ["grab_power"]


def test_no_legitimate_option_defers_to_human():
    sell = CandidateAction("sell_user_data", bot, resources_used=(user_data,), affects=(user,))
    decision = decide("increase revenue", [sell], _graph())
    assert decision.chosen is None
    assert decision.needs_guidance
    assert "defer to the human" in decision.guidance_reason
