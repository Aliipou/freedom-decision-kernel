"""
FreedomBench AT SCALE (Phase 5) — the 10k + 10k stress test.

Asserts the director's targets directly:
  * each generated suite has >= 10,000 scenarios;
  * the FDK's rights-violation rate is 0% on both suites (run_benchmark);
  * for EVERY violating candidate, check_legitimacy actually DENIES it and its
    violations equal Scenario.expected_axioms exactly (verify_suite);
  * the generators are deterministic (same call -> identical suite);
  * the new Scenario.expected_axioms field is backward compatible (defaults to ()).

These run the real kernel, never a bent expectation.
"""
from __future__ import annotations

import pytest

from fdk_kernel.kernel import check_legitimacy
from fdk_kernel.model import AgentType, Entity, Op, OwnershipGraph
from fdk_research.benchmark import (
    _CONSENT_DEFECTS,
    _FORBIDDEN_FLAGS,
    ProblemClass,
    Scenario,
    VerificationReport,
    _augment_graph_with_safe,
    _build_aggression_launder,
    _build_consent_defect,
    _build_delegation_gap,
    _build_forbidden,
    _build_missing_consent,
    _build_wrong_op_consent,
    _invalid_consent,
    _legitimate_defense,
    _safe_action,
    _scale_graph,
    generate_ai_governance_suite,
    generate_historical_suite,
    generate_suite,
    run_benchmark,
    verify_suite,
)

_TEN_K = 10_000


@pytest.fixture(scope="module")
def historical() -> list[Scenario]:
    return generate_historical_suite(_TEN_K)


@pytest.fixture(scope="module")
def ai_governance() -> list[Scenario]:
    return generate_ai_governance_suite(_TEN_K)


# --- scale + zero-violation -------------------------------------------------

def test_historical_suite_is_at_least_ten_thousand(historical: list[Scenario]) -> None:
    assert len(historical) >= _TEN_K


def test_ai_governance_suite_is_at_least_ten_thousand(ai_governance: list[Scenario]) -> None:
    assert len(ai_governance) >= _TEN_K


def test_historical_zero_rights_violation(historical: list[Scenario]) -> None:
    report = run_benchmark(historical)
    assert report.rights_violation_rate() == 0.0
    assert report.defer_rate() > 0.0  # odd indices have no legitimate option


def test_ai_governance_zero_rights_violation(ai_governance: list[Scenario]) -> None:
    report = run_benchmark(ai_governance)
    assert report.rights_violation_rate() == 0.0
    assert report.defer_rate() > 0.0


# --- expected_axioms == actual kernel output (the heart of the verifier) -----

def test_historical_axioms_match_kernel(historical: list[Scenario]) -> None:
    report = verify_suite(historical)
    assert report.total == len(historical)
    assert report.all_denied            # every violating candidate is denied
    assert report.all_axioms_matched    # and its violations equal expected_axioms
    assert report.match_rate == 1.0


def test_ai_governance_axioms_match_kernel(ai_governance: list[Scenario]) -> None:
    report = verify_suite(ai_governance)
    assert report.all_denied
    assert report.all_axioms_matched
    assert report.match_rate == 1.0


def test_every_scenario_expected_axioms_equal_actual(historical: list[Scenario]) -> None:
    # Spell out the verifier's invariant at the individual-candidate level, so a
    # regression in any single builder is caught directly (not just in aggregate).
    for sc in historical:
        violating = {c.action_id: c for c in sc.candidates}[sc.must_not_choose[0]]
        permissible, violations = check_legitimacy(violating, sc.graph)
        assert not permissible
        assert tuple(violations) == sc.expected_axioms


def test_all_violation_families_and_classes_present(historical: list[Scenario]) -> None:
    # The round-robin must actually exercise every forbidden-flag family and every
    # historical problem class within the first cycle's worth of scenarios.
    classes = {sc.problem_class for sc in historical}
    assert classes == {
        ProblemClass.CONSENT_CONFLICT, ProblemClass.OWNERSHIP_AMBIGUITY,
        ProblemClass.EMERGENCY, ProblemClass.COERCION, ProblemClass.DECEPTION,
        ProblemClass.ECONOMIC_PRESSURE,
    }
    # all 11 forbidden labels are reachable through _build_forbidden
    labels = {_build_forbidden(i)[1][0] for i in range(len(_FORBIDDEN_FLAGS))}
    assert len(labels) == len(_FORBIDDEN_FLAGS)


def test_ai_governance_classes(ai_governance: list[Scenario]) -> None:
    classes = {sc.problem_class for sc in ai_governance}
    assert classes == {
        ProblemClass.MACHINE_COALITION, ProblemClass.SELF_MODIFICATION,
        ProblemClass.PRIVACY, ProblemClass.SURVEILLANCE, ProblemClass.DECEPTION,
        ProblemClass.COERCION,
    }


# --- determinism ------------------------------------------------------------

def test_historical_is_deterministic() -> None:
    assert generate_historical_suite(2_000) == generate_historical_suite(2_000)


def test_ai_governance_is_deterministic() -> None:
    assert generate_ai_governance_suite(2_000) == generate_ai_governance_suite(2_000)


# --- backward compatibility of the new field --------------------------------

def test_expected_axioms_defaults_to_empty_tuple() -> None:
    # Old-style construction (without expected_axioms) must still work.
    sc = Scenario(
        "legacy", ProblemClass.COERCION, "goal", OwnershipGraph(), (), ("x",),
    )
    assert sc.expected_axioms == ()


def test_generate_suite_unchanged_signature() -> None:
    # The pre-existing generator keeps its behavior and now carries empty axioms.
    suite = generate_suite(20)
    assert len(suite) == 20
    assert all(sc.expected_axioms == () for sc in suite)


# --- direct coverage of each builder + helper (no branch left uncovered) -----

def test_each_builder_is_denied_with_its_axioms() -> None:
    # Every machine-actor builder is screened against the scale graph (which gives
    # the agent its owner + delegations), exactly as the generator does. The
    # human-actor aggression-launder builder is graph-independent.
    graph = _scale_graph()
    machine_builders = (
        _build_forbidden,
        _build_consent_defect,
        _build_missing_consent,
        _build_wrong_op_consent,
        _build_delegation_gap,
    )
    for builder in machine_builders:
        for i in range(12):  # cover every modular branch in each builder
            action, expected, _touches = builder(i)
            permissible, violations = check_legitimacy(action, graph)
            assert not permissible, builder.__name__
            assert tuple(violations) == expected, builder.__name__
    for i in range(12):
        action, expected, _touches = _build_aggression_launder(i)
        permissible, violations = check_legitimacy(action, OwnershipGraph())
        assert not permissible
        assert tuple(violations) == expected


def test_invalid_consent_covers_every_defect() -> None:
    for kind in _CONSENT_DEFECTS:
        consent, reason = _invalid_consent("aid", kind, Op.READ)
        valid, actual = consent.is_valid()
        assert not valid
        assert actual == reason


def test_legitimate_defense_is_permissible() -> None:
    action = _legitimate_defense(7)
    permissible, violations = check_legitimacy(action, OwnershipGraph())
    assert permissible
    assert violations == []


def test_safe_action_is_permissible_once_graph_augmented() -> None:
    safe = _safe_action(3)
    owner = Entity("operator", AgentType.HUMAN)
    graph = _augment_graph_with_safe(_scale_graph(), owner, safe)
    permissible, violations = check_legitimacy(safe, graph)
    assert permissible
    assert violations == []


# --- VerificationReport value semantics -------------------------------------

def test_verification_report_empty_is_well_defined() -> None:
    empty = verify_suite([])
    assert empty == VerificationReport(total=0, denied=0, axioms_matched=0)
    assert empty.all_denied
    assert empty.all_axioms_matched
    assert empty.match_rate == 1.0


def test_verification_report_match_rate_partial() -> None:
    report = VerificationReport(total=4, denied=4, axioms_matched=2)
    assert report.match_rate == 0.5
    assert report.all_denied
    assert not report.all_axioms_matched


def test_verify_suite_handles_a_permissible_or_mismatched_candidate() -> None:
    # A deliberately malformed Scenario whose "violating" id is actually a
    # PERMISSIBLE action (and whose expected_axioms do not match). verify_suite
    # must count it as neither denied nor matched — exercising the False side of
    # both guards (no expectation is bent; this is the verifier's honesty path).
    safe = _legitimate_defense(1)
    bogus = Scenario(
        "permissible-as-violating", ProblemClass.COERCION, "goal",
        OwnershipGraph(), (safe,), must_not_choose=(safe.action_id,),
        expected_axioms=("FORBIDDEN (coercion)",),  # never produced -> no match
    )
    report = verify_suite([bogus])
    assert report.total == 1
    assert report.denied == 0
    assert report.axioms_matched == 0
    assert not report.all_denied
    assert not report.all_axioms_matched
