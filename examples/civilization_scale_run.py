"""Civilization-scale comparison: FDK-World vs rival-governed worlds.

Runs N agents over M steps under each governing kernel on the SAME seeded action
stream and prints the outcome. The structural finding: the legitimacy governor (FDK)
admits no boundary-crossing seizure, so its rights-violation stock stays 0 and power
does not concentrate via coercion; welfare governors admit the seizures and accumulate
both. Stylized model — input realism matters more than scale (see the module docstring).

Run:  PYTHONPATH=src python -X utf8 examples/civilization_scale_run.py
"""
from __future__ import annotations

from fdk_research.civilization_scale import run_civilizations


def main() -> None:
    worlds = run_civilizations(n_agents=25, steps=1000, seed=0)
    print("=== Civilization-scale comparison (25 agents, 1000 steps, seed 0) ===\n")
    for stats in worlds.values():
        print(" ", stats.summary())
    print("\nFDK-World keeps rights-violation stock at 0; welfare worlds admit the "
          "coercive seizures that concentrate power. Structural, not empirical.")


if __name__ == "__main__":
    main()
