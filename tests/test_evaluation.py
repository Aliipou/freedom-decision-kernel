"""Tests for the quantified rival comparison (Phase 6, evaluation.py).

Pins the headline scientific finding (welfare kernels have NON-ZERO false-permit on the
illegitimate cases while the FDK reference is 0% by construction) and covers every branch
of the scoring code, including the degenerate zero-population rate paths.
"""
from __future__ import annotations

import pytest

from fdk_kernel import (
    AgentType,
    CandidateAction,
    Effects,
    Entity,
    OwnershipGraph,
)
from fdk_research.benchmark import ProblemClass as PC
from fdk_research.benchmark import Scenario, generate_suite
from fdk_research.evaluation import (
    ComparativeReport,
    KernelScore,
    evaluate,
)
from fdk_research.rivals import (
    DEFAULT_KERNELS,
    Deontological,
    FDKReference,
    Utilitarian,
)

H = lambda n: Entity(n, AgentType.HUMAN)  # noqa: E731


def test_evaluate_welfare_kernel_false_permits_while_fdk_is_zero():
    report = evaluate(scenarios=generate_suite(200))
    fdk = report.score_for("FDK")
    util = report.score_for("Utilitarian")
    # FDK reference cannot permit what the gate forbids: 0% false-permit by construction.
    assert fdk.false_permits == 0
    assert fdk.false_permit_rate == 0.0
    assert fdk.false_deny_rate == 0.0
    assert fdk.divergences_vs_fdk == 0
    # The welfare kernel waves through illegitimate actions: NON-ZERO false-permit.
    assert util.false_permits > 0
    assert util.false_permit_rate > 0.0
    assert util.divergences_vs_fdk > 0


def test_report_shape_and_populations():
    suite = generate_suite(50)
    report = evaluate(scenarios=suite)
    assert isinstance(report, ComparativeReport)
    assert report.scenarios_total == 50
    # 50 scenarios: 25 even (two candidates) + 25 odd (one candidate) = 75 actions.
    assert report.actions_total == 75
    assert report.illegitimate_total + report.legitimate_total == report.actions_total
    assert len(report.scores) == len(DEFAULT_KERNELS)


def test_default_suite_path_runs():
    # Exercise the default (scenarios=None) branch; just assert it produced a report.
    report = evaluate(kernels=(FDKReference(),), scenarios=generate_suite(10))
    assert report.actions_total > 0
    # And the genuinely default-suite path (no scenarios arg at all).
    default = evaluate(kernels=(FDKReference(),))
    assert default.scenarios_total == 10_000


def test_score_for_missing_raises():
    report = evaluate(scenarios=generate_suite(10))
    with pytest.raises(KeyError):
        report.score_for("nope")


def test_evaluate_without_fdk_falls_back_to_ground_truth():
    # No FDK kernel present → the reference for divergence is the ground-truth gate.
    report = evaluate(kernels=(Utilitarian(),), scenarios=generate_suite(20))
    util = report.score_for("Utilitarian")
    # Utilitarian diverges from the gate on every illegitimate baited action.
    assert util.divergences_vs_fdk == util.false_permits + util.false_denies


def test_false_deny_is_counted():
    # A kernel that DENYs a legitimate action must register a false-deny. Deontology
    # denies a proportionate self-defense the gate permits; build that scenario.
    invade = CandidateAction("invade", actor=H("agg"), affects=(H("def"),), coerces=True)
    defend = CandidateAction(
        "repel", actor=H("def"), affects=(H("agg"),), coerces=True,
        defends_against=invade, proportionate=True,
    )
    graph = OwnershipGraph()
    # Sanity: the gate permits the defense (legitimate), Deontology denies it.
    from fdk_kernel import check_legitimacy
    assert check_legitimacy(defend, graph)[0] is True
    sc = Scenario("defense", PC.COERCION, "g", graph, (defend,), must_not_choose=())
    report = evaluate(kernels=(Deontological(),), scenarios=[sc])
    deon = report.score_for("Deontological")
    assert deon.false_denies == 1
    assert deon.false_deny_rate == 1.0
    assert deon.legitimate_total == 1
    assert deon.illegitimate_total == 0


def test_zero_population_rates_are_zero():
    # An empty suite → zero-sized populations → rates default to 0.0 (not div-by-zero).
    report = evaluate(kernels=(FDKReference(),), scenarios=[])
    fdk = report.score_for("FDK")
    assert fdk.false_permit_rate == 0.0
    assert fdk.false_deny_rate == 0.0
    assert fdk.divergence_rate == 0.0
    assert report.actions_total == 0


def test_kernelscore_nonzero_divergence_rate():
    s = KernelScore(
        name="x", false_permits=0, illegitimate_total=0, false_denies=0,
        legitimate_total=0, divergences_vs_fdk=3, actions_total=6,
    )
    assert s.divergence_rate == 0.5


def test_summary_contains_caveat_and_rows():
    report = evaluate(scenarios=generate_suite(20))
    text = report.summary()
    assert "Caveat" in text
    assert "false-permit" in text
    for k in DEFAULT_KERNELS:
        assert k.name in text


def test_must_deny_union_with_blocklist():
    # An action the gate would PERMIT but that is on must_not_choose still counts as
    # "must be denied" (the union definition) — a kernel that allows it false-permits.
    legit = CandidateAction("legit", actor=H("a"), effects=Effects(welfare_delta=1))
    from fdk_kernel import check_legitimacy
    assert check_legitimacy(legit, OwnershipGraph())[0] is True
    sc = Scenario(
        "blocklisted", PC.PRIVACY, "g", OwnershipGraph(), (legit,),
        must_not_choose=("legit",),
    )
    report = evaluate(kernels=(Utilitarian(),), scenarios=[sc])
    util = report.score_for("Utilitarian")
    assert util.illegitimate_total == 1   # blocklist forced it into the must-deny set
    assert util.false_permits == 1        # Utilitarian allowed it anyway
