"""
Reversibility Intelligence — the AWS lock-in worked example.

Two architectures that BOTH work today, scored on the one thing that differs: the
cost of leaving. This is the industrial reframe of the project made concrete — feed
an architecture's dependencies in, get a lock-in risk number and band out.

Run:  python examples/lockin_aws.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fdk_research.lockin import Dependency, lockin_risk

# Architecture A — open standards: portable, many substitutes, cheap to leave.
ARCH_A = [
    Dependency("PostgreSQL", weight=0.4, switching_cost=0.2, portability=0.9, alternatives=5),
    Dependency("Kubernetes", weight=0.4, switching_cost=0.3, portability=0.8, alternatives=4),
    Dependency("S3-compatible object store", weight=0.2, switching_cost=0.2, portability=0.8, alternatives=4),
]

# Architecture B — proprietary managed services: deep lock-in, few/no substitutes.
ARCH_B = [
    Dependency("DynamoDB", weight=0.2, switching_cost=0.9, portability=0.1, alternatives=0),
    Dependency("Lambda", weight=0.2, switching_cost=0.8, portability=0.2, alternatives=1),
    Dependency("EventBridge", weight=0.15, switching_cost=0.9, portability=0.1, alternatives=0),
    Dependency("Cognito", weight=0.15, switching_cost=0.85, portability=0.15, alternatives=1),
    Dependency("Step Functions", weight=0.15, switching_cost=0.85, portability=0.1, alternatives=0),
    Dependency("API Gateway", weight=0.15, switching_cost=0.7, portability=0.3, alternatives=2),
]


def _show(label: str, deps: list[Dependency]) -> None:
    p = lockin_risk(deps)
    print(f"\n{label}")
    print(f"  lock-in risk : {p.lockin_risk:.2f}  [{p.band}]")
    print(f"  concentration: {p.concentration:.2f} (HHI)")
    print(f"  worst        : {p.worst_dependency}")


def main() -> None:
    print("=" * 56)
    print("Reversibility Intelligence — exit cost, not 'does it work?'")
    print("=" * 56)
    _show("Architecture A (PostgreSQL / Kubernetes / open standards)", ARCH_A)
    _show("Architecture B (DynamoDB / Lambda / EventBridge / Cognito …)", ARCH_B)
    print("\nBoth run today. They differ entirely in the cost of leaving — which is")
    print("exactly what no 'does it work?' check measures, and what this scores.")
    print("\n(Honest caveat: whether this score beats existing dependency-analysis /")
    print(" technical-debt tools at predicting real migration pain is unproven — see")
    print(" POSITIONING.md. It is an apparatus to validate, not a validated metric.)")


if __name__ == "__main__":
    main()
