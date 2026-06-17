"""External benchmark harness (FDK 2.0, Layer 11 — infrastructure only).

The single most important scientific gap: FDK writes its own benchmark and grades it.
`independent_bench.py` narrowed that with engineer-encoded external-standard labels;
this module builds the *real* answer: a harness for labels collected from MULTIPLE,
DIVERSE, HOSTILE human annotators (a classical liberal, a Rawlsian, a utilitarian, an
economist, a lawyer, an AI-safety researcher), where **FDK authors none of the labels**.

WHAT THIS IS — and is NOT. This is *infrastructure*: it ingests annotations, measures
inter-annotator agreement (Fleiss' κ), derives a human-consensus label per case, and
scores any kernel (FDK + rivals) against that consensus on a held-out split. It is
plug-and-play the moment real annotators exist. It does **NOT** itself validate FDK —
with no real annotations it measures nothing, and a high score against a SMALL or
HOMOGENEOUS annotator pool means little (low κ ⇒ the labels themselves are unreliable).
The validation is the annotators; this is the apparatus that would weigh it.
Imports nothing into `fdk_kernel`.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Annotation:
    """One annotator's verdict on one case. `allow=True` ≙ they judge it legitimate."""

    annotator: str
    case_id: str
    allow: bool


@dataclass(frozen=True)
class AnnotatedCase:
    case_id: str
    annotations: tuple[Annotation, ...]

    def n_allow(self) -> int:
        return sum(1 for a in self.annotations if a.allow)

    def consensus(self) -> bool | None:
        """Majority verdict, or None on a tie (the honest 'humans disagree' outcome)."""
        n = len(self.annotations)
        allow = self.n_allow()
        if 2 * allow == n:
            return None
        return 2 * allow > n

    def agreement(self) -> float:
        """Fraction of annotators agreeing with the majority side (1.0 if unanimous,
        0.5 on a perfect tie)."""
        n = len(self.annotations)
        if n == 0:
            return 1.0
        allow = self.n_allow()
        return max(allow, n - allow) / n


def fleiss_kappa(cases: list[AnnotatedCase]) -> float:
    """Fleiss' κ for binary labels over cases that all share the same annotator count.
    κ=1 perfect agreement, 0 = chance, <0 worse than chance. Raises if counts differ or
    there are too few cases — low/garbage κ means the labels are not trustworthy."""
    cases = [c for c in cases if c.annotations]
    if not cases:
        raise ValueError("no annotated cases")
    n = len(cases[0].annotations)
    if n < 2:
        raise ValueError("Fleiss' kappa needs >= 2 annotators per case")
    if any(len(c.annotations) != n for c in cases):
        raise ValueError("Fleiss' kappa requires a uniform annotator count per case")

    big_n = len(cases)
    p_i = []
    total_allow = 0
    for c in cases:
        a = c.n_allow()
        d = n - a
        total_allow += a
        p_i.append((a * a + d * d - n) / (n * (n - 1)))
    p_bar = sum(p_i) / big_n
    p_allow = total_allow / (big_n * n)
    p_e = p_allow * p_allow + (1 - p_allow) * (1 - p_allow)
    if p_e >= 1.0:  # everyone always chose the same label → agreement is total
        return 1.0
    return (p_bar - p_e) / (1 - p_e)


@dataclass(frozen=True)
class ExternalBenchReport:
    n_cases: int
    n_contested: int          # cases where annotators tied (no consensus)
    kappa: float              # inter-annotator agreement (label reliability)
    kernel_scores: dict[str, float]  # agreement-with-consensus per kernel

    def summary(self) -> str:
        rel = ("UNRELIABLE labels (κ<0.2)" if self.kappa < 0.2 else
               "fair labels" if self.kappa < 0.6 else "strong labels")
        head = (f"{self.n_cases} cases, κ={self.kappa:.2f} ({rel}), "
                f"{self.n_contested} contested (no human consensus)")
        rows = [f"  {k:<16}{v:>7.0%} agree-with-consensus"
                for k, v in self.kernel_scores.items()]
        tail = ("\nNOTE: this scores kernels against HUMAN consensus. It validates FDK "
                "only to the extent the annotators are real, diverse, and hostile — "
                "and only if κ shows the labels are reliable. The apparatus is not the "
                "evidence.")
        return "\n".join([head, *rows]) + "\n" + tail


KernelVerdict = Callable[[str], bool]
"""A kernel as a function case_id -> ALLOW? (so any decider plugs in uniformly)."""


def evaluate_against_humans(
    cases: list[AnnotatedCase], kernels: dict[str, KernelVerdict]
) -> ExternalBenchReport:
    """Score each kernel by its agreement with the human-consensus label, excluding
    contested (tied) cases. Pure; the science is in the annotations, not here."""
    decided = [(c, c.consensus()) for c in cases]
    contested = sum(1 for _c, v in decided if v is None)
    scored = [(c, v) for c, v in decided if v is not None]

    kernel_scores: dict[str, float] = {}
    for name, verdict in kernels.items():
        if not scored:
            kernel_scores[name] = 0.0
            continue
        hits = sum(1 for c, v in scored if verdict(c.case_id) == v)
        kernel_scores[name] = hits / len(scored)

    try:
        kappa = fleiss_kappa(cases)  # well-defined only for uniform, >=2-annotator cases
    except ValueError:
        kappa = 0.0  # non-uniform / too-few annotators → not computable → treat as unreliable
    return ExternalBenchReport(len(cases), contested, kappa, kernel_scores)
