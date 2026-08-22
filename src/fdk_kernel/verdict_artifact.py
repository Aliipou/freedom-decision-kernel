"""M1 VerdictArtifact — explicit constitutional explanation (partial provenance).

M1: axiom + rule trace.
M2: accepted_inputs (conditional on proposer/graph — not verified truth).
M3: action_ref (binds artifact to the candidate action id).

Does NOT establish that inputs are true. No fact provenance_ref, authority, or signatures.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from fdk_kernel.accepted_inputs import AcceptedInput, collect_accepted_inputs
from fdk_kernel.model import CandidateAction, OwnershipGraph
from fdk_kernel.rule_registry import CONSTITUTION_VERSION, KERNEL_VERSION, SCHEMA_VERSION_M1
from fdk_kernel.violation import Violation

SCHEMA_VERSION_M2 = "1.1.0"
EPISTEMIC_STATUS = "conditional_on_accepted_inputs"
EPISTEMIC_DISCLAIMER = (
    "This artifact records constitutional behavior conditional on accepted_inputs. "
    "It does not certify that accepted inputs match world truth."
)


@dataclass(frozen=True, slots=True)
class ConstitutionalBasis:
    axiom_ids: tuple[str, ...]
    rule_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EvaluationContext:
    kernel_version: str
    constitution_version: str


@dataclass(frozen=True, slots=True)
class VerdictArtifact:
    schema_version: str
    artifact_id: str
    verdict: str
    constitutional_basis: ConstitutionalBasis
    violations: tuple[Violation, ...]
    evaluation_context: EvaluationContext
    accepted_inputs: tuple[AcceptedInput, ...] = ()
    action_ref: str = ""
    epistemic_status: str = EPISTEMIC_STATUS

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "artifact_id": self.artifact_id,
            "verdict": self.verdict,
            "action_ref": self.action_ref,
            "constitutional_basis": {
                "axiom_ids": list(self.constitutional_basis.axiom_ids),
                "rule_ids": list(self.constitutional_basis.rule_ids),
            },
            "violations": [
                {"axiom_id": v.axiom_id, "rule_id": v.rule_id, "reason": v.reason}
                for v in self.violations
            ],
            "accepted_inputs": [
                {
                    "fact_key": i.fact_key,
                    "fact_value": i.fact_value,
                    "asserted_by": i.asserted_by,
                    "input_class": i.input_class,
                }
                for i in self.accepted_inputs
            ],
            "evaluation_context": {
                "kernel_version": self.evaluation_context.kernel_version,
                "constitution_version": self.evaluation_context.constitution_version,
            },
            "epistemic_status": self.epistemic_status,
        }

    def to_contract_schema(self) -> dict[str, Any]:
        """Map to contracts-spec verdict_artifact.schema.json field names."""
        return {
            "artifact_version": self.schema_version,
            "decision_id": self.artifact_id,
            "verdict": self.verdict,
            "kernel_version": self.evaluation_context.kernel_version,
            "constitution_version": self.evaluation_context.constitution_version,
            "accepted_inputs": [
                {
                    "fact_key": i.fact_key,
                    "fact_value": i.fact_value,
                    "asserted_by": i.asserted_by,
                    "input_class": i.input_class,
                }
                for i in self.accepted_inputs
            ],
            "constitutional_basis": {
                "axiom_ids": list(self.constitutional_basis.axiom_ids),
            },
            "inference_trace": {
                "rule_ids": list(self.constitutional_basis.rule_ids),
            },
            "action_ref": self.action_ref or None,
            "epistemic_disclaimer": EPISTEMIC_DISCLAIMER,
        }


def artifact_semantics(artifact: VerdictArtifact) -> dict[str, Any]:
    return {
        "verdict": artifact.verdict,
        "action_ref": artifact.action_ref,
        "axiom_ids": list(artifact.constitutional_basis.axiom_ids),
        "rule_ids": list(artifact.constitutional_basis.rule_ids),
        "violations": [
            (v.axiom_id, v.rule_id, v.reason) for v in artifact.violations
        ],
        "accepted_inputs": [i.as_tuple() for i in artifact.accepted_inputs],
        "kernel_version": artifact.evaluation_context.kernel_version,
        "constitution_version": artifact.evaluation_context.constitution_version,
        "epistemic_status": artifact.epistemic_status,
    }


def validate_artifact(artifact: VerdictArtifact) -> None:
    from fdk_kernel.rule_registry import RULE_REGISTRY, registered_axiom_ids, registered_rule_ids

    if artifact.epistemic_status != EPISTEMIC_STATUS:
        raise ValueError("epistemic_status must be conditional_on_accepted_inputs")

    for inp in artifact.accepted_inputs:
        if inp.input_class not in ("CALLER_FLAG", "TYPED_FACT", "GRAPH_FACT", "ATTESTED", "PLUGIN", "UNKNOWN"):
            raise ValueError(f"invalid input_class: {inp.input_class}")
        if not inp.asserted_by:
            raise ValueError("accepted_input.asserted_by required")

    reg_rules = registered_rule_ids()
    reg_axioms = registered_axiom_ids()
    basis_axioms = set(artifact.constitutional_basis.axiom_ids)
    basis_rules = set(artifact.constitutional_basis.rule_ids)

    if artifact.verdict == "ALLOW":
        if artifact.violations:
            raise ValueError("ALLOW verdict must have empty violations")
        return

    if not artifact.violations:
        raise ValueError("non-ALLOW verdict requires violations")

    for v in artifact.violations:
        if v.rule_id not in reg_rules:
            raise ValueError(f"violation rule_id not in registry: {v.rule_id}")
        if v.axiom_id not in reg_axioms:
            raise ValueError(f"violation axiom_id not in registry: {v.axiom_id}")
        if RULE_REGISTRY[v.rule_id].axiom_id != v.axiom_id:
            raise ValueError(f"violation {v.rule_id} axiom mismatch")
        if v.axiom_id not in basis_axioms or v.rule_id not in basis_rules:
            raise ValueError("violation missing from constitutional_basis")


def _artifact_id(semantics: dict[str, Any]) -> str:
    payload = json.dumps(semantics, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def build_verdict_artifact(
    action: CandidateAction,
    graph: OwnershipGraph,
    *,
    evaluation_fn,
) -> VerdictArtifact:
    permissible, violations = evaluation_fn(action, graph)
    verdict = "ALLOW" if permissible else "DENY"
    vtuple = tuple(violations)
    accepted = collect_accepted_inputs(action, graph)
    ctx = EvaluationContext(
        kernel_version=KERNEL_VERSION,
        constitution_version=CONSTITUTION_VERSION,
    )
    basis = ConstitutionalBasis(
        axiom_ids=tuple(sorted({v.axiom_id for v in vtuple})),
        rule_ids=tuple(sorted({v.rule_id for v in vtuple})),
    )
    draft = VerdictArtifact(
        schema_version=SCHEMA_VERSION_M2,
        artifact_id="pending",
        verdict=verdict,
        constitutional_basis=basis,
        violations=vtuple,
        evaluation_context=ctx,
        accepted_inputs=accepted,
        action_ref=action.action_id,
    )
    semantics = artifact_semantics(draft)
    return VerdictArtifact(
        schema_version=draft.schema_version,
        artifact_id=_artifact_id(semantics),
        verdict=draft.verdict,
        constitutional_basis=draft.constitutional_basis,
        violations=draft.violations,
        evaluation_context=draft.evaluation_context,
        accepted_inputs=draft.accepted_inputs,
        action_ref=draft.action_ref,
        epistemic_status=draft.epistemic_status,
    )


def evaluate_legitimacy(action: CandidateAction, graph: OwnershipGraph) -> VerdictArtifact:
    from fdk_kernel.kernel import evaluate

    return build_verdict_artifact(action, graph, evaluation_fn=evaluate)
