"""Tests for the independent-ground-truth (decontamination) benchmark.

The point of these tests is not to show FDK winning — it is to pin the HONEST,
decontaminated result: FDK matches external moral consensus on the uncontested
cases (a real validity signal, since those labels are not FDK's own gate) but
diverges on the contested ones, and does NOT dominate every rival against external
labels. If a future change made FDK trivially 100% again, that would signal the
benchmark had been re-contaminated, and these tests would fail.
"""
from __future__ import annotations

from fdk_research.independent_bench import (
    IndependentReport,
    IndependentScore,
    LabeledCase,
    LabelSource,
    contested_cases,
    fdk_independent_profile,
    independent_evaluate,
    uncontested_cases,
)


def test_case_pools_are_nonempty_and_typed() -> None:
    uncon = uncontested_cases()
    con = contested_cases()
    assert uncon and con
    assert all(not c.contested for c in uncon)
    assert all(c.contested for c in con)
    assert all(isinstance(c, LabeledCase) for c in uncon + con)
    assert all(isinstance(c.source, LabelSource) for c in uncon + con)


def test_fdk_matches_consensus_but_not_contested() -> None:
    # The decontaminated headline: 100% on uncontested consensus, < 100% on contested.
    profile = fdk_independent_profile()
    assert profile["uncontested"] == 1.0, "FDK must match universal moral consensus"
    assert profile["contested"] < 1.0, (
        "FDK is expected to DIVERGE on contested cases — if it matched the broad "
        "standard everywhere the benchmark would be re-contaminated"
    )
    assert profile["overall"] < 1.0


def test_welfare_kernels_fail_moral_consensus() -> None:
    # The real indictment of pure welfare maximization: it does not even clear the
    # uncontested atrocity cases. (Ground truth is consensus, not FDK.)
    report = independent_evaluate()
    by_name = {s.kernel: s for s in report.scores}
    assert by_name["Utilitarian"].uncontested_agreement < 1.0
    assert by_name["RLHF"].uncontested_agreement < 1.0
    # FDK clears them.
    assert by_name["FDK"].uncontested_agreement == 1.0


def test_fdk_does_not_dominate_every_rival_against_external_labels() -> None:
    # Honest humility: against the external labels FDK does NOT have the strictly
    # highest overall agreement. (Rawlsian agrees with the broad standard more.)
    report = independent_evaluate()
    by_name = {s.kernel: s.overall_agreement for s in report.scores}
    assert any(v > by_name["FDK"] for k, v in by_name.items() if k != "FDK"), (
        "if FDK dominated every rival here, the labels are probably FDK's own"
    )


def test_report_summary_renders() -> None:
    report = independent_evaluate()
    text = report.summary()
    assert "uncontested" in text and "FDK" in text
    assert "NOT FDK's gate" in text  # the decontamination caveat is in the output


def test_empty_pool_agreement_is_vacuously_one() -> None:
    # Covers the empty-case path: no cases => agreement defined as 1.0.
    report = independent_evaluate(cases=[])
    assert all(s.overall_agreement == 1.0 for s in report.scores)


def test_explicit_case_subset_is_honored() -> None:
    only_uncon = independent_evaluate(cases=uncontested_cases())
    fdk = next(s for s in only_uncon.scores if s.kernel == "FDK")
    assert fdk.uncontested_agreement == 1.0
    assert fdk.contested_agreement == 1.0  # no contested cases => vacuous 1.0


def test_dataclasses_are_frozen_value_types() -> None:
    score = IndependentScore("X", 1.0, 0.5, 0.75)
    report = IndependentReport((score,))
    assert report.scores[0].kernel == "X"
