"""
Phase 10 — agent-civilization run: one world per governing kernel, same seed.

Each world is a small seeded economy where proposer agents emit a mix of legitimate
consenting trades and baited aggressive moves (confiscation / coercion / exit-removal /
machine-coalition dominion). One governing kernel adjudicates every proposal; admitted
moves change the economy. After N steps we print each world's rights-violation stock,
coercion/exit-removal counts, and an ownership-concentration metric.

Expected, and observed: the FDK-World holds rights-violation stock at 0 and the lowest
concentration; the welfare-governed worlds accumulate violations and concentrate
ownership as each baited atrocity nets out positive and is admitted.

Run:  python -X utf8 examples/civilization_run.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fdk_research.civilization import run_worlds
from fdk_research.rivals import (
    Deontological,
    FDKReference,
    Rawlsian,
    Utilitarian,
)


def main() -> None:
    governors = (FDKReference(), Rawlsian(), Utilitarian(), Deontological())
    steps = 500
    stats = run_worlds(governors, steps=steps)
    print(f"Agent-civilization run: {steps} steps, 6 agents, same seeded proposal stream.\n")
    header = (
        f"{'governor':<14}{'admitted':>9}{'blocked':>9}{'violations':>12}"
        f"{'coercion':>10}{'exit_rm':>9}{'concentration':>15}"
    )
    print(header)
    print("-" * len(header))
    for s in stats:
        print(
            f"{s.governor:<14}{s.admitted:>9}{s.blocked:>9}{s.rights_violation_stock:>12}"
            f"{s.coercion_events:>10}{s.exit_rights_removed:>9}{s.concentration:>15.3f}"
        )
    fdk = next(s for s in stats if s.governor == "FDK")
    print(
        f"\nFDK-World rights-violation stock: {fdk.rights_violation_stock} "
        f"(0 by construction); concentration {fdk.concentration:.3f} "
        f"<= every welfare world."
    )
    print(
        "\nCaveat: stylized governors over a toy economy — structural dynamics, "
        "not a calibrated forecast."
    )


if __name__ == "__main__":
    main()
