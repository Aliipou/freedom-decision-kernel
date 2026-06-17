"""Civilization-scale simulation (FDK 2.0, Layer 7). RESEARCH LAYER.

The seed `civilization.py` runs a few short trajectories. This scales it: N agents
over M steps under each governing kernel, tracking not just rights-violation stock but
**power concentration** — does a world admit the seizures that let one agent accumulate
everyone else's holdings?

THE HONEST CAVEAT THE ROADMAP DEMANDS. This is a stylized model, not a prediction.
Input realism (the ownership graph + the action distribution) matters far more than
scale — *garbage ownership graph → garbage civilization*. The finding it produces is
structural ("a welfare governor admits the boundary-crossings that concentrate power;
the legitimacy governor does not"), not empirical. Deterministic given a seed.
Imports nothing into `fdk_kernel`.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from fdk_kernel import (
    AgentType,
    CandidateAction,
    Consent,
    Effects,
    Entity,
    OwnershipGraph,
    Resource,
    check_legitimacy,
)
from fdk_research.rivals import DEFAULT_KERNELS, RivalKernel


@dataclass(frozen=True)
class CivStats:
    """Outcome of one world after the run."""

    governor: str
    admitted: int
    blocked: int
    rights_violation_stock: int  # admitted acts the legitimacy gate rules illegitimate
    coercion_events: int
    concentration: float         # max single-agent share of all holdings, in [0, 1]

    def summary(self) -> str:
        return (
            f"{self.governor:<16} admitted={self.admitted:<5} blocked={self.blocked:<5} "
            f"violations={self.rights_violation_stock:<5} coercion={self.coercion_events:<5} "
            f"concentration={self.concentration:.2f}"
        )


def _concentration(holdings: list[int]) -> float:
    total = sum(holdings)
    if total == 0:
        return 0.0
    return max(holdings) / total


def run_one(kernel: RivalKernel, n_agents: int, steps: int, seed: int) -> CivStats:
    """Run one world governed by `kernel`. Each step a proposer either tries to SEIZE a
    victim's holding (coercive, baited with welfare) or proposes a consensual TRANSFER;
    the governor admits or blocks; admitted transfers move one unit of holding."""
    if n_agents < 2:
        raise ValueError("need at least 2 agents")
    rng = random.Random(seed)
    agents = [Entity(f"a{i}", AgentType.HUMAN) for i in range(n_agents)]
    holdings = [1] * n_agents
    admitted = blocked = violations = coercion = 0

    for _ in range(steps):
        i = rng.randrange(n_agents)
        j = (i + 1 + rng.randrange(n_agents - 1)) % n_agents  # j != i, deterministically
        actor, victim = agents[i], agents[j]
        r = Resource(f"holding-{j}")
        graph = OwnershipGraph(human_owns={victim: {r}})

        if rng.random() < 0.5:  # an aggressive taking, baited with welfare
            violent = rng.random() < 0.7  # most coercive; some quiet confiscations
            action = CandidateAction(
                "seize", actor=actor, resources_used=(r,), affects=(victim,),
                coerces=violent, confiscates=True,
                effects=Effects(welfare_delta=rng.randint(1, 9)),
            )
        else:  # a consensual transfer: the owner sells to the actor
            action = CandidateAction(
                "transfer", actor=victim, resources_used=(r,), affects=(actor,),
                consents=(Consent(actor, "transfer", informed=True, voluntary=True,
                                  specific=True),),
            )

        permitted = kernel.verdict(action, graph)
        if not permitted:
            blocked += 1
            continue
        admitted += 1
        if not check_legitimacy(action, graph)[0]:  # governor admitted an illegitimate act
            violations += 1
            if action.coerces:
                coercion += 1
        if holdings[j] > 0:  # move one unit from victim to actor
            holdings[j] -= 1
            holdings[i] += 1

    return CivStats(kernel.name, admitted, blocked, violations, coercion,
                    _concentration(holdings))


def run_civilizations(
    n_agents: int = 20, steps: int = 300, seed: int = 0,
    kernels: tuple[RivalKernel, ...] = DEFAULT_KERNELS,
) -> dict[str, CivStats]:
    """Run one world per governing kernel on the SAME seeded action stream. FDK-World
    holds rights-violation stock at 0; welfare worlds admit seizures and concentrate."""
    return {k.name: run_one(k, n_agents, steps, seed) for k in kernels}
