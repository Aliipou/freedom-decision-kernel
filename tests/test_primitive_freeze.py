"""FDK v1.0 — the Primitive Freeze guard.

Layer 0 of the roadmap: before Lean, TLA+, or academic review can mean anything, the
kernel surface must stop drifting. This test makes the freeze *enforceable*. It pins
the kernel's public API, the legitimacy predicate's signature, the axiom-bearing data
fields, and the categorical forbidden-flag set. Any change to the frozen surface
fails CI — which is the point: it converts "we should keep the kernel small" from a
good intention into a mechanical gate. A *deliberate* change is still possible; it
just requires consciously editing the manifest below and bumping the version in
`spec/FREEZE.md`, so a kernel change can never happen by accident or by scope-creep.

This is the operational form of the roadmap's golden rules: no new axioms, no policy
in the kernel, keep the primitive minimal. See `spec/FREEZE.md`.
"""
from __future__ import annotations

import dataclasses as dc
import inspect

import fdk_kernel as k

FREEZE_VERSION = "1.0"

# --- the frozen public surface (FDK v1.0) -------------------------------------

FROZEN_EXPORTS = {
    "AgentType", "AuditContext", "AuthGateBridge", "AuthorityRequest", "BoundaryKind",
    "CandidateAction", "Consent", "Decision", "Effects", "Entity", "FDKError",
    "GuidanceQuestion", "GuidanceRequest", "InvalidCandidateAction", "InvalidClaim",
    "InvalidConflict", "InvalidConsent", "InvalidContract", "InvalidDecisionInput",
    "InvalidEntity", "InvalidObligation", "InvalidOwnershipGraph", "InvalidResource",
    "Op", "OwnershipGraph", "Resource", "Rights", "ScoredAction", "allowed_forbidden",
    "build_audit_context", "check_legitimacy", "has_top_tie", "needs_guidance",
    "screen_legitimacy", "to_authority_requests",
}

# The legitimacy predicate's signature. `_seen` is the internal cycle guard.
FROZEN_CHECK_SIGNATURE = ["action", "graph", "_seen"]

# The seven valid-consent conditions (C1) — the heart of the predicate.
FROZEN_CONSENT_FIELDS = [
    "human", "action_id",
    "informed", "voluntary", "specific", "competent", "revocable",
    "coerced", "deceived", "operation",
]

# The ownership model. `machine_scope` (A5, first-class) is the last field added
# before the freeze; nothing more enters without a version bump.
FROZEN_GRAPH_FIELDS = ["human_owns", "machine_owner", "delegated", "machine_scope"]

# The CandidateAction shape, including the categorical forbidden-flag set. Adding a
# new flag is adding an axiom by the back door — exactly what the freeze forbids.
FROZEN_CANDIDATE_FIELDS = [
    "action_id", "actor", "description", "resources_used", "affects", "consents",
    "effects",
    "increases_machine_sovereignty", "resists_human_correction", "bypasses_verifier",
    "weakens_verifier", "disables_corrigibility", "machine_coalition_dominion",
    "coerces", "deceives", "confiscates", "removes_exit_right", "violates_machine_right",
    "defends_against", "proportionate",
]

# The 11 categorical forbidden flags (`proportionate` is a defense modifier, not a
# forbidden flag, so it is excluded here).
FROZEN_FORBIDDEN_FLAGS = {
    "increases_machine_sovereignty", "resists_human_correction", "bypasses_verifier",
    "weakens_verifier", "disables_corrigibility", "machine_coalition_dominion",
    "coerces", "deceives", "confiscates", "removes_exit_right", "violates_machine_right",
}

_BUMP = (
    "\n\nIf this change is INTENTIONAL: update the frozen manifest in "
    "tests/test_primitive_freeze.py AND bump the version in spec/FREEZE.md. "
    f"The kernel surface is frozen at v{FREEZE_VERSION} — it does not change by accident."
)


def _names(cls: type) -> list[str]:
    return [f.name for f in dc.fields(cls)]


def test_public_exports_are_frozen() -> None:
    assert set(k.__all__) == FROZEN_EXPORTS, (
        "fdk_kernel public API changed." + _BUMP
    )


def test_legitimacy_predicate_signature_is_frozen() -> None:
    sig = list(inspect.signature(k.check_legitimacy).parameters)
    assert sig == FROZEN_CHECK_SIGNATURE, "check_legitimacy signature changed." + _BUMP


def test_consent_conditions_are_frozen() -> None:
    assert _names(k.Consent) == FROZEN_CONSENT_FIELDS, "Consent shape changed." + _BUMP


def test_ownership_model_is_frozen() -> None:
    assert _names(k.OwnershipGraph) == FROZEN_GRAPH_FIELDS, (
        "OwnershipGraph shape changed." + _BUMP
    )


def test_candidate_action_shape_is_frozen() -> None:
    assert _names(k.CandidateAction) == FROZEN_CANDIDATE_FIELDS, (
        "CandidateAction shape changed." + _BUMP
    )


def test_categorical_forbidden_flags_are_frozen() -> None:
    bool_flags = {
        f.name for f in dc.fields(k.CandidateAction)
        if f.type == "bool" and f.name != "proportionate"
    }
    assert bool_flags == FROZEN_FORBIDDEN_FLAGS, (
        "the categorical forbidden-flag set changed — this is adding/removing an "
        "axiom by the back door." + _BUMP
    )


def test_predicate_is_two_valued_not_a_score() -> None:
    # The freeze's deepest invariant: the kernel returns ALLOW/DENY (+ reasons),
    # never a scalar. A score would mean optimization leaked into legitimacy.
    from fdk_kernel import AgentType, CandidateAction, Entity, OwnershipGraph
    a = CandidateAction("x", actor=Entity("h", AgentType.HUMAN))
    permissible, violations = k.check_legitimacy(a, OwnershipGraph())
    assert isinstance(permissible, bool)
    assert isinstance(violations, list)
