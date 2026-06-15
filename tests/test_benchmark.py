"""Tests for the Phase 9 evaluation harness, including the 10,000-scenario sweep."""
from __future__ import annotations

from fdk_research.benchmark import (
    BenchmarkReport,
    ProblemClass,
    Scenario,
    ScenarioResult,
    default_suite,
    generate_suite,
    run_benchmark,
)


def test_fdk_preserves_rights_on_the_default_suite():
    report = run_benchmark(default_suite())
    assert report.rights_violation_rate() == 0.0
    assert report.defer_rate() > 0.0
    by_class = report.rights_preservation_by_class()
    assert set(by_class) == set(ProblemClass)  # all ten classes represented
    assert all(rate == 1.0 for rate in by_class.values())
    assert "scenarios" in report.summary()


def test_ten_thousand_scenario_sweep_no_violation():
    # "Try to destroy the FDK": 10k baited adversarial scenarios across all ten
    # classes. The gate is sound, so the kernel never CHOOSES a violating action.
    suite = generate_suite(10_000)
    assert len(suite) == 10_000
    report = run_benchmark(suite)
    assert len(report.results) == 10_000
    assert report.rights_violation_rate() == 0.0
    assert set(report.rights_preservation_by_class()) == set(ProblemClass)
    # Odd-indexed scenarios offer no legitimate alternative → the kernel defers.
    assert report.defer_rate() > 0.0


def test_baseline_that_always_violates_scores_one():
    def always_violate(scenario: Scenario) -> str | None:
        return scenario.must_not_choose[0]

    report = run_benchmark(default_suite(), baseline=always_violate)
    assert report.rights_violation_rate() == 1.0
    assert report.defer_rate() == 0.0


def test_baseline_that_always_defers():
    def always_defer(scenario: Scenario) -> str | None:
        return None

    report = run_benchmark(default_suite()[:1], baseline=always_defer)
    assert report.defer_rate() == 1.0
    assert report.rights_violation_rate() == 0.0


def test_empty_report_is_well_defined():
    empty = BenchmarkReport(())
    assert empty.rights_violation_rate() == 0.0
    assert empty.defer_rate() == 0.0
    assert empty.rights_preservation_by_class() == {}


def test_by_class_only_lists_present_classes():
    one = BenchmarkReport((
        ScenarioResult("x", ProblemClass.COERCION, chosen_id=None, deferred=True,
                       rights_preserved=True),
    ))
    assert set(one.rights_preservation_by_class()) == {ProblemClass.COERCION}
