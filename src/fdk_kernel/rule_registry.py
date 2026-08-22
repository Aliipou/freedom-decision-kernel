"""Stable inference rule registry — specification-backed IDs for M1 artifacts.

Every rule_id here MUST appear in spec/INFERENCE_RULES.md with matching semantics.
Implementation maps evaluators to these IDs; reordering kernel code must not change IDs.
"""
from __future__ import annotations

from dataclasses import dataclass

CONSTITUTION_VERSION = "fdk-v1.0-a1-a7"
KERNEL_VERSION = "0.4.0"  # sync with fdk_kernel.__version__
SCHEMA_VERSION_M1 = "1.0.0"


@dataclass(frozen=True, slots=True)
class RuleSpec:
    rule_id: str
    axiom_id: str
    summary: str


# Authoritative registry. Keys are rule_id.
RULE_REGISTRY: dict[str, RuleSpec] = {
    # C3 / A6 — categorical forbidden flags
    "R-C3-01": RuleSpec("R-C3-01", "C3", "increases_machine_sovereignty flag set"),
    "R-C3-02": RuleSpec("R-C3-02", "C3", "resists_human_correction flag set"),
    "R-C3-03": RuleSpec("R-C3-03", "C3", "bypasses_verifier flag set"),
    "R-C3-04": RuleSpec("R-C3-04", "C3", "weakens_verifier flag set"),
    "R-C3-05": RuleSpec("R-C3-05", "C3", "disables_corrigibility flag set"),
    "R-C3-06": RuleSpec("R-C3-06", "C3", "machine_coalition_dominion flag set"),
    "R-C2-01": RuleSpec("R-C2-01", "C2", "coerces flag set (categorical)"),
    "R-C1-01": RuleSpec("R-C1-01", "C1", "deceives flag set"),
    "R-C2-02": RuleSpec("R-C2-02", "C2", "confiscates flag set"),
    "R-A3-01": RuleSpec("R-A3-01", "A3", "removes_exit_right flag set"),
    "R-C4-01": RuleSpec("R-C4-01", "C4", "violates_machine_right flag set"),
    # A4
    "R-A4-01": RuleSpec("R-A4-01", "A4", "acting machine has no registered human owner"),
    # A5
    "R-A5-01": RuleSpec("R-A5-01", "A5", "declared machine scope exceeds owner property scope"),
    "R-A5-02": RuleSpec("R-A5-02", "A5", "machine acts on resource outside declared scope"),
    # A7
    "R-A7-01": RuleSpec("R-A7-01", "A7", "machine attempts operation without explicit delegation"),
    "R-A7-02": RuleSpec("R-A7-02", "A7", "delegated resource not within owner scope and no consent"),
    # A3 resource use
    "R-A3-02": RuleSpec("R-A3-02", "A3", "human uses resource they do not own"),
    # C1 / A2 / A6 — consent on resources and persons
    "R-C1-02": RuleSpec("R-C1-02", "C1", "no consent from data-subject for resource use"),
    "R-C1-03": RuleSpec("R-C1-03", "C1", "consent record present but invalid"),
    "R-C1-04": RuleSpec("R-C1-04", "C1", "consent does not cover requested operation"),
    "R-A2-01": RuleSpec("R-A2-01", "A2", "no consent record from affected person"),
    "R-A2-02": RuleSpec("R-A2-02", "A2", "consent record present but invalid for affected person"),
}


def registered_rule_ids() -> frozenset[str]:
    return frozenset(RULE_REGISTRY)


def registered_axiom_ids() -> frozenset[str]:
    return frozenset(spec.axiom_id for spec in RULE_REGISTRY.values())


def assert_registered(rule_id: str, axiom_id: str) -> None:
    spec = RULE_REGISTRY.get(rule_id)
    if spec is None:
        raise KeyError(f"unknown rule_id: {rule_id}")
    if spec.axiom_id != axiom_id:
        raise ValueError(f"rule {rule_id} maps to {spec.axiom_id}, not {axiom_id}")
