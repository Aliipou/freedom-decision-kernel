"""M2/M3 — accepted_inputs and action_ref on VerdictArtifact."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fdk_kernel import (
    AgentType,
    CandidateAction,
    Entity,
    OwnershipGraph,
    Resource,
    evaluate_legitimacy,
    validate_artifact,
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


def test_m2_accepted_inputs_present():
    action = CandidateAction("sell", bot, resources_used=(user_data,), affects=(user,))
    art = evaluate_legitimacy(action, _graph())
    assert len(art.accepted_inputs) > 0
    keys = {i.fact_key for i in art.accepted_inputs}
    assert "actor.kind" in keys
    assert "coerces" in keys
    assert "delegation.user_data.USE" in keys
    for inp in art.accepted_inputs:
        assert inp.asserted_by in ("proposer", "ownership_graph")
    validate_artifact(art)


def test_m3_action_ref():
    action = CandidateAction("my-action-id", bot, resources_used=(product,))
    art = evaluate_legitimacy(action, _graph())
    assert art.action_ref == "my-action-id"


def test_to_contract_schema_m4_shape():
    action = CandidateAction("sell", bot, resources_used=(user_data,), affects=(user,))
    doc = evaluate_legitimacy(action, _graph()).to_contract_schema()
    assert doc["artifact_version"] == "1.1.0"
    assert doc["decision_id"]
    assert doc["epistemic_disclaimer"]
    assert "asserted_by" in doc["accepted_inputs"][0]
