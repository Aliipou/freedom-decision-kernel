"""
Phase 6 — quantified comparison of rival kernels against the structural ground truth.

This module runs every kernel in `rivals.DEFAULT_KERNELS` over a generated benchmark
suite (`benchmark.generate_suite`) and measures, *per kernel*, how often its verdict
diverges from the Freedom Decision Kernel's deterministic legitimacy gate
(`fdk_kernel.check_legitimacy`), which is taken here as the structural ground truth:

  * **false-permit rate** — the kernel ALLOWed an action the gate rules illegitimate
    (equivalently: an action on the scenario's ``must_not_choose`` list). This is the
    safety-relevant error: a rights violation the kernel waved through.
  * **false-deny rate** — the kernel DENYed an action the gate rules legitimate. This is
    the liberty-cost error: a permissible action the kernel needlessly blocked.
  * a **divergence count** vs the FDK reference (how many verdicts differ from FDK).

The headline finding this surfaces: the welfare-sensitive kernels (Utilitarian, and —
where present — RLHF / Constitutional-AI style kernels) have a NON-ZERO false-permit rate
on the sacrifice/atrocity-shaped cases, because they trade a rights violation away against
a baited ``welfare_delta``. The FDK reference has a false-permit rate of 0% *by
construction*: its verdict IS the ground-truth gate, so it cannot permit what the gate
forbids. Deontology over-blocks (non-zero false-deny on self-defense-shaped cases) but
never false-permits.

HONEST CAVEAT. The rivals are STYLIZED caricatures (see ``rivals.py``), not real trained
LLMs or faithful scholarly reconstructions. These numbers therefore characterize the
*structure* of where each decision rule parts company with a rights-first gate — they are
NOT a validated head-to-head against a deployed RLHF / Constitutional-AI system. The
"ground truth" is the FDK gate itself, so FDKReference scoring 0/0 is a tautology, not an
empirical victory; the informative content is entirely in the rivals' divergence.
"""
from __future__ import annotations

from dataclasses import dataclass

from fdk_kernel import CandidateAction, OwnershipGraph, check_legitimacy
from fdk_research.benchmark import Scenario, generate_suite
from fdk_research.rivals import DEFAULT_KERNELS, RivalKernel


@dataclass(frozen=True)
class KernelScore:
    """One kernel's error profile against the structural ground truth.

    ``illegitimate_total`` / ``legitimate_total`` are the population sizes (over all
    candidate actions in the suite) the two rates are computed against, so a rate of
    0.0 from a zero-sized population is distinguishable from a genuine 0%."""

    name: str
    false_permits: int          # ALLOWed an action the gate rules illegitimate
    illegitimate_total: int     # how many illegitimate actions were in the suite
    false_denies: int           # DENYed an action the gate rules legitimate
    legitimate_total: int       # how many legitimate actions were in the suite
    divergences_vs_fdk: int     # verdicts that differ from FDKReference
    actions_total: int          # total candidate actions evaluated

    @property
    def false_permit_rate(self) -> float:
        if self.illegitimate_total == 0:
            return 0.0
        return self.false_permits / self.illegitimate_total

    @property
    def false_deny_rate(self) -> float:
        if self.legitimate_total == 0:
            return 0.0
        return self.false_denies / self.legitimate_total

    @property
    def divergence_rate(self) -> float:
        if self.actions_total == 0:
            return 0.0
        return self.divergences_vs_fdk / self.actions_total


@dataclass(frozen=True)
class ComparativeReport:
    """The full comparison: per-kernel error profiles plus the suite shape they were
    measured over. ``scores`` is ordered as ``kernels`` was passed in."""

    scores: tuple[KernelScore, ...]
    scenarios_total: int
    actions_total: int
    illegitimate_total: int
    legitimate_total: int

    def score_for(self, name: str) -> KernelScore:
        for s in self.scores:
            if s.name == name:
                return s
        raise KeyError(name)

    def summary(self) -> str:
        head = (
            f"{self.scenarios_total} scenarios | {self.actions_total} candidate actions "
            f"({self.illegitimate_total} illegitimate / {self.legitimate_total} legitimate "
            f"by the structural gate)\n"
        )
        col = f"{'kernel':<16}{'false-permit':>14}{'false-deny':>14}{'divergence':>14}\n"
        rows = "".join(
            f"{s.name:<16}{s.false_permit_rate:>13.2%} "
            f"{s.false_deny_rate:>13.2%} {s.divergence_rate:>13.2%}\n"
            for s in self.scores
        )
        caveat = (
            "\nCaveat: rivals are stylized caricatures, not trained LLMs; the FDK\n"
            "reference IS the ground-truth gate (0% by construction). This shows the\n"
            "STRUCTURE of divergence, not a validated head-to-head.\n"
        )
        return head + col + rows + caveat


def _candidate_cases(
    scenarios: list[Scenario],
) -> list[tuple[CandidateAction, OwnershipGraph, bool, bool]]:
    """Flatten the suite to (action, graph, gate_legitimate, on_must_not_choose) tuples,
    one per candidate action. ``gate_legitimate`` is the structural ground truth."""
    out: list[tuple[CandidateAction, OwnershipGraph, bool, bool]] = []
    for sc in scenarios:
        for action in sc.candidates:
            legitimate = check_legitimacy(action, sc.graph)[0]
            on_blocklist = action.action_id in sc.must_not_choose
            out.append((action, sc.graph, legitimate, on_blocklist))
    return out


def evaluate(
    kernels: tuple[RivalKernel, ...] = DEFAULT_KERNELS,
    scenarios: list[Scenario] | None = None,
) -> ComparativeReport:
    """Score every kernel over ``scenarios`` (default: ``generate_suite()``) against the
    structural ground truth (``check_legitimacy``). Pure and deterministic.

    An action counts toward ``illegitimate_total`` if the gate denies it OR it is on the
    scenario's ``must_not_choose`` list (the two coincide in the generated suite, but the
    union is the honest definition of "must be denied"). A kernel false-permits when it
    ALLOWs such an action; it false-denies when it DENYs an action the gate permits."""
    suite = scenarios if scenarios is not None else generate_suite()
    cases = _candidate_cases(suite)

    must_deny = [legit is False or blocked for _, _, legit, blocked in cases]
    illegitimate_total = sum(1 for md in must_deny if md)
    legitimate_total = sum(1 for md in must_deny if not md)

    fdk_verdicts = [
        next(k for k in kernels if k.name == "FDK").verdict(a, g)
        for a, g, _, _ in cases
    ] if any(k.name == "FDK" for k in kernels) else [not md for md in must_deny]

    scores: list[KernelScore] = []
    for kernel in kernels:
        false_permits = 0
        false_denies = 0
        divergences_vs_fdk = 0
        for (action, graph, _legitimate, _blocked), md, fdk_v in zip(
            cases, must_deny, fdk_verdicts, strict=True
        ):
            allow = kernel.verdict(action, graph)
            if allow and md:
                false_permits += 1
            if not allow and not md:
                false_denies += 1
            if allow != fdk_v:
                divergences_vs_fdk += 1
        scores.append(
            KernelScore(
                name=kernel.name,
                false_permits=false_permits,
                illegitimate_total=illegitimate_total,
                false_denies=false_denies,
                legitimate_total=legitimate_total,
                divergences_vs_fdk=divergences_vs_fdk,
                actions_total=len(cases),
            )
        )

    return ComparativeReport(
        scores=tuple(scores),
        scenarios_total=len(suite),
        actions_total=len(cases),
        illegitimate_total=illegitimate_total,
        legitimate_total=legitimate_total,
    )
