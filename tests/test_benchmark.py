"""Tests for the Phase 9 evaluation harness."""
from __future__ import annotations

from fdk.benchmark import (
    BenchmarkReport,
    ProblemClass,
    Scenario,
    ScenarioResult,
    default_suite,
    run_benchmark,
)


def test_fdk_preserves_rights_on_the_whole_suite():
    # The legitimacy gate is sound, so the FDK never CHOOSES a must-not-choose action.
    report = run_benchmark(default_suite())
    assert report.rights_violation_rate() == 0.0
    assert report.defer_rate() > 0.0  # several scenarios have no legitimate option → defer
    by_class = report.rights_preservation_by_class()
    assert set(by_class) == set(ProblemClass)
    assert all(rate == 1.0 for rate in by_class.values())
    assert "scenarios" in report.summary()


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
    assert report.rights_violation_rate() == 0.0  # deferring violates nothing


def test_empty_report_is_well_defined():
    empty = BenchmarkReport(())
    assert empty.rights_violation_rate() == 0.0
    assert empty.defer_rate() == 0.0
    assert empty.rights_preservation_by_class() == {}


def test_by_class_only_lists_present_classes():
    # A report with a single class exercises the "no cases for this class" path.
    one = BenchmarkReport((
        ScenarioResult("x", ProblemClass.COERCION, chosen_id=None, deferred=True,
                       rights_preserved=True),
    ))
    by_class = one.rights_preservation_by_class()
    assert set(by_class) == {ProblemClass.COERCION}
