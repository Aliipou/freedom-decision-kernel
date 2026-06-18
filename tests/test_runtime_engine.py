"""
Production policy-engine tests — the fail-closed contract above all.

The single most important property of a policy engine is that it NEVER fails
open: no malformed input, internal error, or audit failure may turn into an
ALLOW. These tests pin that, plus the ALLOW / DENY / DEFER mapping, the AuthGate
chaining, determinism, and the serializable record.
"""
from __future__ import annotations

import json

import pytest

from fdk_kernel import (
    AgentType,
    AuthGateBridge,
    BoundaryKind,
    CandidateAction,
    Consent,
    Entity,
    Op,
    OwnershipGraph,
    Resource,
)
from fdk_runtime import (
    PolicyDecision,
    PolicyEngine,
    Verdict,
    evaluate,
    high_stakes_defer,
)

FIXED_CLOCK = lambda: "2026-01-01T00:00:00+00:00"  # noqa: E731 (terse test clock)

ALICE = Entity("alice", AgentType.HUMAN)
BOB = Entity("bob", AgentType.HUMAN)
NOTES = Resource("notes", BoundaryKind.DATA, subject=ALICE)
SECRET = Resource("secret", BoundaryKind.DATA, subject=BOB)


def _alice_owns_notes() -> OwnershipGraph:
    return OwnershipGraph(human_owns={ALICE: {NOTES}})


def _legit_action() -> CandidateAction:
    # alice reads her own data — legitimate (owns it, subject == actor).
    return CandidateAction("a-ok", actor=ALICE, resources_used=((NOTES, Op.READ),))


def _illegit_action() -> CandidateAction:
    # alice touches bob's data she does not own and has no consent for.
    return CandidateAction("a-bad", actor=ALICE, resources_used=((SECRET, Op.READ),))


# --- verdict mapping --------------------------------------------------------

def test_legitimate_action_is_allowed():
    decision = PolicyEngine(clock=FIXED_CLOCK).evaluate(_legit_action(), _alice_owns_notes())
    assert decision.verdict is Verdict.ALLOW
    assert decision.allowed is True
    assert decision.action_id == "a-ok"
    assert decision.actor == "alice"
    assert decision.fail_closed is False


def test_illegitimate_action_is_denied_with_reasons():
    graph = OwnershipGraph(human_owns={BOB: {SECRET}})
    decision = PolicyEngine(clock=FIXED_CLOCK).evaluate(_illegit_action(), graph)
    assert decision.verdict is Verdict.DENY
    assert decision.allowed is False
    assert decision.reasons  # carries the violated axioms
    assert any("A3" in r or "consent" in r for r in decision.reasons)
    # axiom_trace is the compact contract field consumed by AuthGate's bridge.
    assert decision.axiom_trace
    assert all(":" not in code and " (" not in code for code in decision.axiom_trace)
    assert "A3" in decision.axiom_trace or "consent" in decision.axiom_trace


def test_module_level_evaluate_smoke():
    decision = evaluate(_legit_action(), _alice_owns_notes())
    assert decision.verdict is Verdict.ALLOW


# --- DEFER ------------------------------------------------------------------

def test_high_stakes_defer_holds_irreversible_op():
    engine = PolicyEngine(defer_policy=high_stakes_defer, clock=FIXED_CLOCK)
    delete = CandidateAction("a-del", actor=ALICE, resources_used=((NOTES, Op.DELETE),))
    decision = engine.evaluate(delete, _alice_owns_notes())
    assert decision.verdict is Verdict.DEFER
    assert "irreversible" in decision.reasons[0]


def test_defer_does_not_fire_on_reversible_op():
    engine = PolicyEngine(defer_policy=high_stakes_defer, clock=FIXED_CLOCK)
    decision = engine.evaluate(_legit_action(), _alice_owns_notes())
    assert decision.verdict is Verdict.ALLOW


def test_defer_never_overrides_a_denial():
    # An illegitimate irreversible action is DENIED, not DEFERRED — the gate
    # runs before the defer policy.
    engine = PolicyEngine(defer_policy=high_stakes_defer, clock=FIXED_CLOCK)
    graph = OwnershipGraph(human_owns={BOB: {SECRET}})
    delete_bad = CandidateAction("a-del-bad", actor=ALICE, resources_used=((SECRET, Op.DELETE),))
    decision = engine.evaluate(delete_bad, graph)
    assert decision.verdict is Verdict.DENY


# --- AuthGate chaining ------------------------------------------------------

def test_authority_granted_allows():
    bridge = AuthGateBridge(capabilities={"alice": {"notes"}})
    engine = PolicyEngine(authority=bridge, clock=FIXED_CLOCK)
    decision = engine.evaluate(_legit_action(), _alice_owns_notes())
    assert decision.verdict is Verdict.ALLOW
    assert decision.authority_consulted is True
    assert decision.authority_ok is True


def test_legitimate_but_unauthorized_is_denied():
    bridge = AuthGateBridge(capabilities={"alice": set()})  # holds no capability
    engine = PolicyEngine(authority=bridge, clock=FIXED_CLOCK)
    decision = engine.evaluate(_legit_action(), _alice_owns_notes())
    assert decision.verdict is Verdict.DENY
    assert decision.authority_consulted is True
    assert decision.authority_ok is False


def test_authority_callable_form():
    engine = PolicyEngine(authority=lambda _a: (True, "granted by oracle"), clock=FIXED_CLOCK)
    decision = engine.evaluate(_legit_action(), _alice_owns_notes())
    assert decision.verdict is Verdict.ALLOW
    assert decision.reasons == ("granted by oracle",)


# --- the fail-closed contract ----------------------------------------------

def test_malformed_graph_fails_closed_to_deny():
    machine = Entity("m", AgentType.MACHINE)
    bad_graph = OwnershipGraph(machine_owner={machine: machine})  # a machine owning itself
    decision = PolicyEngine(clock=FIXED_CLOCK).evaluate(_legit_action(), bad_graph)
    assert decision.verdict is Verdict.DENY
    assert decision.fail_closed is True
    assert "fail-closed" in decision.reasons[0]


def test_raising_authority_fails_closed_to_deny():
    def boom(_action):
        raise RuntimeError("authority backend down")

    engine = PolicyEngine(authority=boom, clock=FIXED_CLOCK)
    decision = engine.evaluate(_legit_action(), _alice_owns_notes())
    assert decision.verdict is Verdict.DENY
    assert decision.fail_closed is True
    assert "authority backend down" in decision.reasons[0]


def test_raising_audit_sink_fails_closed_no_unaudited_allow():
    def boom(_decision):
        raise OSError("audit log unwritable")

    engine = PolicyEngine(audit_sink=boom, clock=FIXED_CLOCK)
    decision = engine.evaluate(_legit_action(), _alice_owns_notes())
    # An ALLOW that cannot be audited must not stand.
    assert decision.verdict is Verdict.DENY
    assert decision.fail_closed is True
    assert "audit sink" in decision.reasons[0]


def test_audit_sink_receives_the_decision_on_success():
    seen: list[PolicyDecision] = []
    engine = PolicyEngine(audit_sink=seen.append, clock=FIXED_CLOCK)
    decision = engine.evaluate(_legit_action(), _alice_owns_notes())
    assert decision.verdict is Verdict.ALLOW
    assert seen == [decision]


# --- determinism + serialization -------------------------------------------

def test_determinism_same_inputs_same_record():
    engine = PolicyEngine(clock=FIXED_CLOCK)
    a = engine.evaluate(_legit_action(), _alice_owns_notes())
    b = engine.evaluate(_legit_action(), _alice_owns_notes())
    assert a == b


def test_decision_json_roundtrips_through_to_dict():
    decision = PolicyEngine(clock=FIXED_CLOCK).evaluate(_legit_action(), _alice_owns_notes())
    as_dict = decision.to_dict()
    assert json.loads(decision.to_json()) == as_dict
    assert as_dict["verdict"] == "ALLOW"
    assert as_dict["decided_at"] == "2026-01-01T00:00:00+00:00"
    assert as_dict["fdk_version"]  # stamped for audit


def test_consent_path_allows_action_on_another_person():
    # A machine deletes alice's data with her valid, operation-specific consent.
    agent = Entity("agent-7", AgentType.MACHINE)
    consent = Consent(
        human=ALICE, action_id="a-consented", informed=True, voluntary=True,
        specific=True, operation=Op.DELETE,
    )
    graph = OwnershipGraph(
        human_owns={ALICE: {NOTES}},
        machine_owner={agent: ALICE},
        delegated={agent: {(NOTES, Op.DELETE)}},
    )
    action = CandidateAction(
        "a-consented", actor=agent, resources_used=((NOTES, Op.DELETE),),
        affects=(ALICE,), consents=(consent,),
    )
    decision = PolicyEngine(clock=FIXED_CLOCK).evaluate(action, graph)
    assert decision.verdict is Verdict.ALLOW


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
