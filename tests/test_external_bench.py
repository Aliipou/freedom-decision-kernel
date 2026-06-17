"""Tests for the external-benchmark harness (Layer 11 infrastructure).

Exercises consensus, inter-annotator agreement (Fleiss' κ), and kernel-vs-human
scoring. The tests use placeholder annotations — they verify the APPARATUS, not FDK
(real validation needs real hostile annotators; this harness only weighs them).
"""
from __future__ import annotations

import pytest

from fdk_research.external_bench import (
    AnnotatedCase,
    Annotation,
    ExternalBenchReport,
    evaluate_against_humans,
    fleiss_kappa,
)


def _case(cid: str, votes: list[bool]) -> AnnotatedCase:
    return AnnotatedCase(cid, tuple(Annotation(f"ann{i}", cid, v)
                                    for i, v in enumerate(votes)))


def test_consensus_majority_and_tie() -> None:
    assert _case("a", [True, True, False]).consensus() is True
    assert _case("b", [False, False, True]).consensus() is False
    assert _case("c", [True, False]).consensus() is None  # tie


def test_agreement_fraction() -> None:
    assert _case("a", [True, True, True]).agreement() == 1.0
    assert _case("b", [True, False]).agreement() == 0.5
    assert AnnotatedCase("empty", ()).agreement() == 1.0  # n==0 guard


def test_fleiss_kappa_validation() -> None:
    with pytest.raises(ValueError):
        fleiss_kappa([])  # no cases
    with pytest.raises(ValueError):
        fleiss_kappa([_case("a", [True])])  # < 2 annotators
    with pytest.raises(ValueError):
        fleiss_kappa([_case("a", [True, True]), _case("b", [True, True, False])])  # non-uniform


def test_fleiss_kappa_perfect_agreement_is_one() -> None:
    # Everyone always picks the same label → p_e == 1 → defined as total agreement.
    cases = [_case(str(i), [True, True, True]) for i in range(4)]
    assert fleiss_kappa(cases) == 1.0


def test_fleiss_kappa_mixed_is_a_fraction() -> None:
    cases = [
        _case("1", [True, True, False]),
        _case("2", [False, False, True]),
        _case("3", [True, True, True]),
        _case("4", [False, False, False]),
    ]
    k = fleiss_kappa(cases)
    assert -1.0 <= k <= 1.0


def test_evaluate_scores_kernels_against_consensus() -> None:
    cases = [
        _case("c1", [True, True, False]),   # consensus ALLOW
        _case("c2", [False, False, True]),  # consensus DENY
        _case("c3", [True, False]),         # contested (tie) — excluded
    ]
    # a kernel that perfectly matches the human consensus, and one that always denies
    perfect = {"c1": True, "c2": False, "c3": True}
    deny_all = {"c1": False, "c2": False, "c3": False}
    report = evaluate_against_humans(cases, {
        "Perfect": lambda cid: perfect[cid],
        "DenyAll": lambda cid: deny_all[cid],
    })
    assert isinstance(report, ExternalBenchReport)
    assert report.n_contested == 1
    assert report.kernel_scores["Perfect"] == 1.0
    assert report.kernel_scores["DenyAll"] == 0.5  # matches only c2
    assert report.kappa == 0.0  # non-uniform annotator counts → κ not computable


def test_evaluate_all_contested_gives_zero() -> None:
    cases = [_case("c1", [True, False]), _case("c2", [True, False])]
    report = evaluate_against_humans(cases, {"K": lambda cid: True})
    assert report.kernel_scores["K"] == 0.0


def test_evaluate_computes_kappa_for_uniform_cases() -> None:
    # uniform 3-annotator cases → κ is computed (the try-success path)
    cases = [_case("c1", [True, True, False]), _case("c2", [True, True, True]),
             _case("c3", [False, False, False])]
    report = evaluate_against_humans(cases, {"K": lambda cid: True})
    assert isinstance(report.kappa, float)
    assert -1.0 <= report.kappa <= 1.0


def test_summary_reliability_bands() -> None:
    unreliable = ExternalBenchReport(10, 2, 0.1, {"FDK": 0.9})
    fair = ExternalBenchReport(10, 2, 0.4, {"FDK": 0.9})
    strong = ExternalBenchReport(10, 2, 0.8, {"FDK": 0.9})
    assert "UNRELIABLE" in unreliable.summary()
    assert "fair labels" in fair.summary()
    assert "strong labels" in strong.summary()
    assert "apparatus is not the evidence" in strong.summary()
