"""M1 VerdictArtifact — explicit constitutional explanation (partial provenance).

Explains why the kernel produced a verdict under accepted inputs.
Does NOT establish that inputs are true. No fact provenance, authority, or signatures.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from fdk_kernel.model import CandidateAction, OwnershipGraph
from fdk_kernel.rule_registry import CONSTITUTION_VERSION, KERNEL_VERSION, SCHEMA_VERSION_M1
from fdk_kernel.violation import Violation

EPISTEMIC_STATUS = "conditional_on_accepted_inputs"


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
    verdict: str  # ALLOW | DENY (FDK kernel is binary; DEFER is research-layer)
    constitutional_basis: ConstitutionalBasis
    violations: tuple[Violation, ...]
    evaluation_context: EvaluationContext
    epistemic_status: str = EPISTEMIC_STATUS

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "artifact_id": self.artifact_id,
            "verdict": self.verdict,
            "constitutional_basis": {
                "axiom_ids": list(self.constitutional_basis.axiom_ids),
                "rule_ids": list(self.constitutional_basis.rule_ids),
            },
            "violations": [
                {
                    "axiom_id": v.axiom_id,
                    "rule_id": v.rule_id,
                    "reason": v.reason,
                }
                for v in self.violations
            ],
            "evaluation_context": {
                "kernel_version": self.evaluation_context.kernel_version,
                "constitution_version": self.evaluation_context.constitution_version,
            },
            "epistemic_status": self.epistemic_status,
        }


def artifact_semantics(artifact: VerdictArtifact) -> dict[str, Any]:
    """Semantic core for determinism tests — excludes presentation-only fields."""
    return {
        "verdict": artifact.verdict,
        "axiom_ids": list(artifact.constitutional_basis.axiom_ids),
        "rule_ids": list(artifact.constitutional_basis.rule_ids),
        "violations": [
            (v.axiom_id, v.rule_id, v.reason) for v in artifact.violations
        ],
        "kernel_version": artifact.evaluation_context.kernel_version,
        "constitution_version": artifact.evaluation_context.constitution_version,
        "epistemic_status": artifact.epistemic_status,
    }


def validate_artifact(artifact: VerdictArtifact) -> None:
    """M1 integrity: every violation references registered rules and basis."""
    from fdk_kernel.rule_registry import RULE_REGISTRY, registered_axiom_ids, registered_rule_ids

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
        spec = RULE_REGISTRY[v.rule_id]
        if spec.axiom_id != v.axiom_id:
            raise ValueError(
                f"violation {v.rule_id} axiom_id {v.axiom_id} != registry {spec.axiom_id}"
            )
        if v.axiom_id not in basis_axioms:
            raise ValueError(f"violation axiom {v.axiom_id} missing from constitutional_basis")
        if v.rule_id not in basis_rules:
            raise ValueError(f"violation rule {v.rule_id} missing from constitutional_basis")


def _artifact_id(semantics: dict[str, Any]) -> str:
    payload = json.dumps(semantics, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def build_verdict_artifact(
    action: CandidateAction,
    graph: OwnershipGraph,
    *,
    evaluation_fn,
) -> VerdictArtifact:
    """Build M1 partial artifact from an evaluation function returning (bool, violations)."""
    permissible, violations = evaluation_fn(action, graph)
    verdict = "ALLOW" if permissible else "DENY"
    vtuple = tuple(violations)
    axiom_ids = tuple(sorted({v.axiom_id for v in vtuple}))
    rule_ids = tuple(sorted({v.rule_id for v in vtuple}))
    ctx = EvaluationContext(
        kernel_version=KERNEL_VERSION,
        constitution_version=CONSTITUTION_VERSION,
    )
    basis = ConstitutionalBasis(axiom_ids=axiom_ids, rule_ids=rule_ids)
    artifact = VerdictArtifact(
        schema_version=SCHEMA_VERSION_M1,
        artifact_id="pending",
        verdict=verdict,
        constitutional_basis=basis,
        violations=vtuple,
        evaluation_context=ctx,
    )
    semantics = artifact_semantics(artifact)
    return VerdictArtifact(
        schema_version=artifact.schema_version,
        artifact_id=_artifact_id(semantics),
        verdict=artifact.verdict,
        constitutional_basis=artifact.constitutional_basis,
        violations=artifact.violations,
        evaluation_context=artifact.evaluation_context,
        epistemic_status=artifact.epistemic_status,
    )


def evaluate_legitimacy(action: CandidateAction, graph: OwnershipGraph) -> VerdictArtifact:
    """M1 entry point: evaluate action and return explicit VerdictArtifact."""
    from fdk_kernel.kernel import evaluate

    return build_verdict_artifact(action, graph, evaluation_fn=evaluate)
