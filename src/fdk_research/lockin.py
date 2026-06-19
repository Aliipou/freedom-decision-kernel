"""
Lock-in risk scorer (Reversibility Intelligence) — fdk_research, advisory.

The industrial reframe of the project: forget "theory of freedom"; ask the question
enterprises actually pay for — *if we wanted to leave this architecture / vendor /
platform tomorrow, how trapped are we?* This module turns a portfolio of
dependencies into a **lock-in risk score** and a band (LOW / MEDIUM / HIGH), so an
architecture decision yields a number (`lockin_risk = 0.71`, `HIGH`) the way a
credit score does.

Worked use case (`examples/lockin_aws.py`): architecture A (PostgreSQL, Kubernetes,
open standards) vs B (ten proprietary managed services). Both run today; they differ
entirely in *exit cost*, and this scorer makes that difference explicit.

HONESTY (the same null as the science track). This is an *apparatus*, not a proven
instrument. It **composes existing constructs** — switching cost, viable
alternatives, data portability, dependency concentration (HHI, reused from
`compass_measure.dependency_index`). Its value over existing dependency-analysis /
technical-debt / resilience-framework tools is the open empirical question
(incremental validity). It is offered as a computable score to be *validated against
real migration outcomes*, not as a claim that lock-in is a novel variable.
"""
from __future__ import annotations

from dataclasses import dataclass

from fdk_research.compass_measure import dependency_index

# Band thresholds on the [0, 1] lock-in risk score. A modeling choice, not a result.
_MEDIUM = 1.0 / 3.0
_HIGH = 2.0 / 3.0


@dataclass(frozen=True)
class Dependency:
    """One thing an architecture depends on. All risk fields are in [0, 1] except
    `alternatives` (a count of viable substitutes, 0 = sole-source)."""

    name: str
    weight: float = 1.0          # relative importance / spend share (for concentration)
    switching_cost: float = 0.5  # 0 = free to leave, 1 = ruinous
    portability: float = 0.5     # 0 = proprietary lock, 1 = open standard / fully portable
    alternatives: int = 1        # number of viable substitutes (0 = no exit)

    def __post_init__(self) -> None:
        for field_name, value in (
            ("weight", self.weight), ("switching_cost", self.switching_cost),
            ("portability", self.portability),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be in [0, 1], got {value}")
        if self.alternatives < 0:
            raise ValueError(f"alternatives must be >= 0, got {self.alternatives}")

    def escapability(self) -> float:
        """How easy is it to leave THIS dependency, in [0, 1] (1 = trivial exit). The
        mean of portability, cheapness-to-switch, and substitute availability."""
        alt_score = min(self.alternatives, 3) / 3.0  # 0,1,2,3+ -> 0, .33, .67, 1
        return (self.portability + (1.0 - self.switching_cost) + alt_score) / 3.0


@dataclass(frozen=True)
class LockinProfile:
    """A portfolio's lock-in reading. Components exposed on purpose (do not reify the
    scalar) so the empirical work can see what drives it."""

    lockin_risk: float                      # weighted-mean per-dependency risk, [0,1]
    concentration: float                    # HHI of dependency weights, [0,1]
    worst_dependency: str                   # the single most trapping dependency
    band: str                               # LOW / MEDIUM / HIGH
    per_dependency: dict[str, float]        # name -> its individual lock-in risk

    def to_dict(self) -> dict[str, object]:
        return {
            "lockin_risk": self.lockin_risk,
            "concentration": self.concentration,
            "worst_dependency": self.worst_dependency,
            "band": self.band,
            "per_dependency": dict(self.per_dependency),
        }


def _band(risk: float) -> str:
    if risk < _MEDIUM:
        return "LOW"
    if risk < _HIGH:
        return "MEDIUM"
    return "HIGH"


def lockin_risk(dependencies: list[Dependency]) -> LockinProfile:
    """Score a portfolio of dependencies. No dependencies ⇒ nothing to be locked into
    ⇒ zero risk. Risk per dependency is 1 − escapability; the portfolio risk is the
    weight-weighted mean (equal weights if all weights are zero)."""
    if not dependencies:
        return LockinProfile(0.0, 0.0, "", "LOW", {})

    per = {d.name: 1.0 - d.escapability() for d in dependencies}
    weights = [d.weight for d in dependencies]
    total = sum(weights)
    if total <= 0.0:
        risk = sum(per.values()) / len(per)  # equal weights fallback
    else:
        risk = sum(d.weight * (1.0 - d.escapability()) for d in dependencies) / total

    worst = max(dependencies, key=lambda d: 1.0 - d.escapability()).name
    return LockinProfile(
        lockin_risk=risk,
        concentration=dependency_index(weights),
        worst_dependency=worst,
        band=_band(risk),
        per_dependency=per,
    )
