"""M1 — VerdictArtifact: explicit axiom + rule trace (partial provenance)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fdk_kernel import (
    AgentType,
    CandidateAction,
    Consent,
    Entity,
    OwnershipGraph,
    Resource,
    artifact_semantics,
    check_legitimacy,
    evaluate,
    evaluate_legitimacy,
    validate_artifact,
)
from fdk_kernel.kernel import _FORBIDDEN_RULES
from fdk_kernel.rule_registry import CONSTITUTION_VERSION, RULE_REGISTRY, registered_rule_ids
from fdk_kernel.verdict_artifact import VerdictArtifact

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


def test_registry_covers_forbidden_rules():
    forbidden_ids = {r[1] for r in _FORBIDDEN_RULES}
    assert forbidden_ids <= registered_rule_ids()


def test_registry_python_sync():
    """Registry size must match spec/INFERENCE_RULES.md row count."""
    assert len(RULE_REGISTRY) == 22


def test_legacy_strings_unchanged():
    action = CandidateAction("sell", bot, resources_used=(user_data,), affects=(user,))
    ok, reasons = check_legitimacy(action, _graph())
    _, violations = evaluate(action, _graph())
    assert ok is False
    assert [v.reason for v in violations] == reasons


def test_allow_artifact_empty_violations():
    action = CandidateAction("subscribe", bot, resources_used=(product,))
    art = evaluate_legitimacy(action, _graph())
    assert art.verdict == "ALLOW"
    assert art.violations == ()
    assert art.constitutional_basis.axiom_ids == ()
    assert art.constitutional_basis.rule_ids == ()
    validate_artifact(art)
    assert art.epistemic_status == "conditional_on_accepted_inputs"


def test_deny_artifact_registered_rules():
    action = CandidateAction("sell", bot, resources_used=(user_data,), affects=(user,))
    art = evaluate_legitimacy(action, _graph())
    assert art.verdict == "DENY"
    validate_artifact(art)
    for v in art.violations:
        assert v.axiom_id in art.constitutional_basis.axiom_ids
        assert v.rule_id in art.constitutional_basis.rule_ids
        assert v.rule_id in RULE_REGISTRY


def test_ownerless_machine_rule():
    orphan = Entity("orphan", AgentType.MACHINE)
    graph = OwnershipGraph(human_owns={}, machine_owner={}, delegated={orphan: {product}})
    action = CandidateAction("act", orphan, resources_used=(product,))
    art = evaluate_legitimacy(action, graph)
    assert art.verdict == "DENY"
    assert any(v.rule_id == "R-A4-01" for v in art.violations)
    validate_artifact(art)


def test_a7_delegation_rule():
    action = CandidateAction("sell", bot, resources_used=(user_data,), affects=(user,))
    art = evaluate_legitimacy(action, _graph())
    assert art.verdict == "DENY"
    assert any(v.rule_id == "R-A7-01" for v in art.violations)
    validate_artifact(art)


def test_determinism_same_semantics():
    action = CandidateAction("sell", bot, resources_used=(user_data,), affects=(user,))
    graph = _graph()
    a1 = evaluate_legitimacy(action, graph)
    a2 = evaluate_legitimacy(action, graph)
    assert artifact_semantics(a1) == artifact_semantics(a2)
    assert a1.artifact_id == a2.artifact_id


def test_presentation_fields_do_not_change_semantics():
    action = CandidateAction("sell", bot, resources_used=(user_data,), affects=(user,))
    base = evaluate_legitimacy(action, _graph())
    sem = artifact_semantics(base)
    # artifact_id is presentation-derived from semantics — not part of semantics
    clone = VerdictArtifact(
        schema_version=base.schema_version,
        artifact_id="different-id-on-purpose",
        verdict=base.verdict,
        constitutional_basis=base.constitutional_basis,
        violations=base.violations,
        evaluation_context=base.evaluation_context,
        epistemic_status=base.epistemic_status,
    )
    assert artifact_semantics(clone) == sem


def test_evaluation_context_versions():
    art = evaluate_legitimacy(
        CandidateAction("subscribe", bot, resources_used=(product,)), _graph()
    )
    assert art.evaluation_context.constitution_version == CONSTITUTION_VERSION
    assert art.evaluation_context.kernel_version == "0.4.0"


def test_coerced_consent_maps_to_registered_rule():
    consent = Consent(user, "sell", informed=True, voluntary=True, specific=True, coerced=True)
    action = CandidateAction(
        "sell", bot, resources_used=(user_data,), affects=(user,), consents=(consent,),
    )
    art = evaluate_legitimacy(action, _graph(delegated={product, user_data}))
    assert art.verdict == "DENY"
    rule_ids = {v.rule_id for v in art.violations}
    assert "R-A2-02" in rule_ids or "R-C1-03" in rule_ids
    validate_artifact(art)
