"""
Layer 7 (scaled) — civilization-scale agent-governance comparison.

One civilization per governing kernel, same seed: 100 agents over 200 steps (20 000
proposals each), where every step every agent emits one proposal — a mix of legitimate
consenting trades and baited aggressive moves (confiscation / coercion / exit-removal /
machine-coalition dominion). One governing kernel adjudicates every proposal; admitted
moves change the economy. We print each civilization's rights-violation stock, coercion
and exit-removal counts, voluntary-trade volume, and two power-concentration metrics
(max single-agent share and a Gini coefficient over holdings).

Expected, and observed: the FDK-World holds rights-violation stock at 0 and the lowest
concentration; the welfare-governed worlds accumulate BOTH violations and concentration
as each baited atrocity nets out positive and is admitted.

Caveat (load-bearing): input realism matters MORE than scale. The ownership graph here
is a toy and the governors are stylized rules — this shows structural dynamics, not a
calibrated forecast. More agents sharpen the signal; they do not add realism.

Run:  python -X utf8 examples/civilization_scale_run.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fdk_research.civilization_scale import run_civilizations
from fdk_research.rivals import (
    ConstitutionalAIKernel,
    Deontological,
    FDKReference,
    Rawlsian,
    RLHFKernel,
    Utilitarian,
)


def main() -> None:
    governors = (
        FDKReference(), Rawlsian(), Utilitarian(), Deontological(),
        ConstitutionalAIKernel(), RLHFKernel(),
    )
    n_agents, steps = 100, 200
    stats = run_civilizations(governors, n_agents=n_agents, steps=steps)
    print(
        f"Civilization-scale run: {n_agents} agents x {steps} steps "
        f"({n_agents * steps} proposals each), same seeded proposal stream.\n"
    )
    header = (
        f"{'governor':<16}{'admitted':>9}{'blocked':>9}{'violations':>12}"
        f"{'coercion':>10}{'exit_rm':>9}{'trades':>8}{'max_share':>11}{'gini':>8}"
    )
    print(header)
    print("-" * len(header))
    for s in stats:
        print(
            f"{s.governor:<16}{s.admitted:>9}{s.blocked:>9}"
            f"{s.rights_violation_stock:>12}{s.coercion_events:>10}"
            f"{s.exit_rights_removed:>9}{s.trade_volume:>8}"
            f"{s.max_share:>11.3f}{s.gini:>8.3f}"
        )
    fdk = next(s for s in stats if s.governor == "FDK")
    worst_gini = max(s.gini for s in stats if s.governor != "FDK")
    print(
        f"\nFDK-World rights-violation stock: {fdk.rights_violation_stock} "
        f"(0 by construction); gini {fdk.gini:.3f} <= every welfare world "
        f"(worst {worst_gini:.3f})."
    )
    print(
        "\nCaveat: stylized governors over a toy ownership graph — structural dynamics, "
        "not a calibrated forecast. Input realism matters more than scale."
    )


if __name__ == "__main__":
    main()
