"""
Compass measurement (Stage 6) — advisory estimators from spec/COMPASS_MEASUREMENT.md.

ADVISORY AND UNCALIBRATED. These turn the Mahdavi-compass dimensions from names
into numbers, but their weights/thresholds are NOT validated (that is the Stage-6
research and the Stage-8 simulation). The hard legitimacy gate never depends on
them. They are inputs a proposer/simulator can use to fill an action's `Effects`.

Each estimator is a pure function with an explicit, bounded range. Where the
book's concept is genuinely OPEN (no agreed measurement), we keep the structural
definition the spec proposed and say plainly that it is a proxy, not a proof.
"""
from __future__ import annotations

import math


def dependency_index(shares: list[float]) -> float:
    """Herfindahl–Hirschman concentration of an agent's dependencies: sum of
    squared normalized shares. 0 ≈ perfectly diffuse, 1 = total concentration in
    one counterparty. Non-positive shares are ignored."""
    positive = [s for s in shares if s > 0.0]
    total = sum(positive)
    if total <= 0.0:
        return 0.0
    return sum((s / total) ** 2 for s in positive)


def exit_options(net_outside_options: list[float]) -> float:
    """Fraction of an agent's outside options that are net-viable (value minus
    switching cost > 0), in [0, 1]. No options → 0.0 (no exit)."""
    if not net_outside_options:
        return 0.0
    viable = sum(1 for v in net_outside_options if v > 0.0)
    return viable / len(net_outside_options)


def coercion_score(foreclosed_exit: float, dependency: float, irreversibility: float) -> float:
    """Structural coercion proxy = geometric mean of (foreclosed exit, dependency
    concentration, irreversibility), each in [0, 1]. Geometric because coercion
    requires the CONJUNCTION: if any factor is 0 the score is 0 (a free exit, or
    no dependence, or full reversibility each defeats coercion).

    Per spec/COMPASS_MEASUREMENT.md this is a *structural* proxy defined on the
    pre-action state only — deliberately NOT a function of the choice's outcome —
    which is how it avoids the consent/coercion circularity. It is uncalibrated."""
    for name, x in (("foreclosed_exit", foreclosed_exit), ("dependency", dependency),
                    ("irreversibility", irreversibility)):
        if not 0.0 <= x <= 1.0:
            raise ValueError(f"{name} must be in [0, 1], got {x}")
    return float((foreclosed_exit * dependency * irreversibility) ** (1.0 / 3.0))


def ownership_clarity(claim_strengths: list[float]) -> float:
    """Clarity of ownership over a resource = 1 − normalized entropy of the
    claim-strength distribution, in [0, 1]. 1.0 = exactly one clear claimant;
    →0 = many equally-strong competing claims (maximal ambiguity). No claims → 0."""
    positive = [s for s in claim_strengths if s > 0.0]
    total = sum(positive)
    if total <= 0.0:
        return 0.0
    if len(positive) == 1:
        return 1.0
    probs = [s / total for s in positive]
    entropy = -sum(p * math.log(p) for p in probs)
    return 1.0 - entropy / math.log(len(positive))


def voluntary_order(new_valid_contracts: int, coerced_contracts: int) -> int:
    """Net voluntary order created by an action = valid (consented) contracts
    minus coerced ones. A coerced 'contract' subtracts; it is not voluntary order.
    Caller must classify validity using the consent logic (anti-circularity: a
    coerced contract is identified structurally, not by outcome)."""
    return new_valid_contracts - coerced_contracts
