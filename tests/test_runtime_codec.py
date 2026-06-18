"""
Wire-codec + sidecar tests — the JSON boundary of the policy engine, including
the worked "delete the customer database" example from PRODUCTION_READINESS.md.
"""
from __future__ import annotations

import json

import pytest

from fdk_kernel import AgentType, Op
from fdk_runtime import PolicyEngine, Verdict, decode_request
from fdk_runtime.codec import CodecError
from fdk_runtime.sidecar import handle_decide

FIXED_CLOCK = lambda: "2026-01-01T00:00:00+00:00"  # noqa: E731


def _delete_db_request(*, with_consent: bool) -> dict:
    consents = []
    if with_consent:
        consents = [{
            "human": "alice", "action_id": "del-1", "informed": True,
            "voluntary": True, "specific": True, "operation": "DELETE",
        }]
    return {
        "action": {
            "action_id": "del-1",
            "actor": {"name": "agent-7", "machine": True},
            "description": "delete the customers table",
            "resources": [
                {"name": "customers", "kind": "DATA", "op": "DELETE", "subject": "alice"}
            ],
            "affects": ["alice"],
            "consents": consents,
        },
        "graph": {
            "human_owns": {"alice": [{"name": "customers", "kind": "DATA", "subject": "alice"}]},
            "machine_owner": {"agent-7": "alice"},
            "delegated": {
                "agent-7": [
                    {"name": "customers", "kind": "DATA", "subject": "alice", "op": "DELETE"}
                ]
            },
        },
    }


# --- decode -----------------------------------------------------------------

def test_decode_builds_typed_action_and_graph():
    action, graph = decode_request(_delete_db_request(with_consent=True))
    assert action.action_id == "del-1"
    assert action.actor.kind is AgentType.MACHINE
    (resource, op), = action.uses()
    assert resource.name == "customers" and op is Op.DELETE
    assert resource.subject is not None and resource.subject.name == "alice"
    assert graph.machine_owner[action.actor].name == "alice"


def test_decoded_delete_without_consent_is_denied():
    action, graph = decode_request(_delete_db_request(with_consent=False))
    decision = PolicyEngine(clock=FIXED_CLOCK).evaluate(action, graph)
    assert decision.verdict is Verdict.DENY


def test_decoded_delete_with_consent_is_allowed():
    action, graph = decode_request(_delete_db_request(with_consent=True))
    decision = PolicyEngine(clock=FIXED_CLOCK).evaluate(action, graph)
    assert decision.verdict is Verdict.ALLOW


def test_missing_action_raises_codec_error():
    with pytest.raises(CodecError):
        decode_request({"graph": {}})


def test_unknown_op_raises_codec_error():
    bad = _delete_db_request(with_consent=False)
    bad["action"]["resources"][0]["op"] = "NUKE"
    with pytest.raises(CodecError):
        decode_request(bad)


def test_empty_graph_defaults_when_absent():
    action, graph = decode_request({"action": {
        "action_id": "x", "actor": {"name": "alice", "machine": False},
    }})
    assert action.action_id == "x"
    assert graph.human_owns == {}


# --- sidecar handler (pure, no sockets) -------------------------------------

def test_sidecar_decides_valid_request():
    engine = PolicyEngine(clock=FIXED_CLOCK)
    body = json.dumps(_delete_db_request(with_consent=True)).encode("utf-8")
    status, decision = handle_decide(engine, body)
    assert status == 200
    assert decision["verdict"] == "ALLOW"


def test_sidecar_denies_without_consent():
    engine = PolicyEngine(clock=FIXED_CLOCK)
    body = json.dumps(_delete_db_request(with_consent=False)).encode("utf-8")
    status, decision = handle_decide(engine, body)
    assert status == 200
    assert decision["verdict"] == "DENY"


def test_sidecar_bad_json_fails_closed_to_deny_400():
    engine = PolicyEngine(clock=FIXED_CLOCK)
    status, decision = handle_decide(engine, b"{not json")
    assert status == 400
    assert decision["verdict"] == "DENY"
    assert decision["fail_closed"] is True


def test_sidecar_malformed_payload_fails_closed():
    engine = PolicyEngine(clock=FIXED_CLOCK)
    status, decision = handle_decide(engine, json.dumps({"graph": {}}).encode("utf-8"))
    assert status == 400
    assert decision["verdict"] == "DENY"


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
