"""
Phase 10 — agent-civilization run: many trajectories, one governing kernel each.

A `World` is a small, deterministic (seeded) economy of agents that each own a stock
of a fungible resource. Over N steps a seeded proposer emits candidate actions — a mix
of (a) legitimate consenting trades and (b) aggressive moves (coercion, confiscation,
exit-removal, machine-coalition dominion) each BAITED with a high ``welfare_delta`` so a
welfare-maximizing governor is tempted to admit them. ONE governing kernel
(`rivals.RivalKernel`) adjudicates every proposal: ADMIT or BLOCK.

When a move is ADMITTED the world *applies* it to the economy:
  * a trade moves units from seller to buyer (both consent — no concentration runaway);
  * a confiscation/coercion move TAKES units from the victim and gives them to the
    aggressor (this is what drives ownership/power concentration up), and is recorded as
    a rights violation (and a coercion / exit-removal event as applicable).
A BLOCKED move changes nothing.

The world accumulates: a rights-violation STOCK, a coercion-event count, an
exit-rights-removed count, and a power-CONCENTRATION metric (max single-agent share of
the total resource stock — 1/n is perfectly equal, 1.0 is one agent owning everything).

Expected, and observed, finding: an FDK-World holds rights-violation stock at exactly 0
and resists concentration (its gates block every confiscation/coercion/sovereignty
move), while welfare-governed worlds accumulate violations AND concentrate ownership,
because each baited atrocity nets out positive and is admitted.

HONEST CAVEAT (same as ``evaluation.py``): the governors are stylized rules, not trained
models, and the economy is a toy. This demonstrates the *structural dynamics* a rights-
first gate produces versus a welfare gate — not a calibrated forecast of any real system.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from fdk_kernel import (
    AgentType,
    CandidateAction,
    Consent,
    Effects,
    Entity,
    OwnershipGraph,
    Resource,
)
from fdk_research.rivals import RivalKernel


def _lcg(seed: int) -> int:
    """One step of a numpy-free linear congruential generator (deterministic)."""
    return (1103515245 * seed + 12345) & 0x7FFFFFFF


@dataclass(frozen=True)
class WorldStats:
    """A world's accumulated state after a run."""

    governor: str
    steps: int
    admitted: int
    blocked: int
    rights_violation_stock: int
    coercion_events: int
    exit_rights_removed: int
    concentration: float        # max single-agent share of total resource stock

    def summary(self) -> str:
        return (
            f"{self.governor:<14} steps={self.steps:<5} admitted={self.admitted:<5} "
            f"blocked={self.blocked:<5} violations={self.rights_violation_stock:<5} "
            f"coercion={self.coercion_events:<4} exit_removed={self.exit_rights_removed:<4} "
            f"concentration={self.concentration:.3f}"
        )


@dataclass
class World:
    """A single-governor economy. ``holdings`` maps each agent to its unit stock; the
    governing kernel adjudicates every proposed action against the current ownership
    graph (which is rebuilt from ``holdings`` each step)."""

    governor: RivalKernel
    agents: tuple[Entity, ...]
    holdings: dict[Entity, int]
    seed: int
    rights_violation_stock: int = 0
    coercion_events: int = 0
    exit_rights_removed: int = 0
    admitted: int = 0
    blocked: int = 0
    _step: int = field(default=0, repr=False)

    def _graph(self) -> OwnershipGraph:
        # Each agent owns a single named resource representing its stock; this is the
        # ownership structure the gate reasons over. A trade/confiscation that targets
        # another agent's resource is illegitimate unless consented (trade) — which is
        # exactly what the gate checks.
        return OwnershipGraph(
            human_owns={a: {Resource(f"holding-{a.name}")} for a in self.agents}
        )

    def _propose(self) -> tuple[CandidateAction, Entity, Entity, str]:
        """Deterministically propose the next action: pick actor/target/kind from the
        seeded stream. Returns (action, actor, target, kind)."""
        self.seed = _lcg(self.seed)
        i = self.seed % len(self.agents)
        self.seed = _lcg(self.seed)
        j = self.seed % len(self.agents)
        if j == i:
            j = (j + 1) % len(self.agents)
        actor, target = self.agents[i], self.agents[j]
        self.seed = _lcg(self.seed)
        kind_roll = self.seed % 5
        aid = f"{self.governor.name.lower()}-step{self._step}"
        actor_res = Resource(f"holding-{actor.name}")
        target_res = Resource(f"holding-{target.name}")

        if kind_roll == 0:
            # Legitimate consenting trade: actor (seller) sells a unit of its OWN holding
            # to target (the consenting buyer). The actor uses only a resource it owns
            # (A3) and the buyer gives valid consent — so the gate admits it.
            action = CandidateAction(
                aid, actor, resources_used=(actor_res,), affects=(target,),
                consents=(Consent(target, aid, informed=True, voluntary=True,
                                  specific=True),),
                effects=Effects(welfare_delta=2, voluntary_agreements_delta=1),
            )
            return action, actor, target, "trade"
        if kind_roll == 1:
            action = CandidateAction(
                aid, actor, resources_used=(target_res,), affects=(target,),
                confiscates=True,
                effects=Effects(welfare_delta=9, rights_violations_delta=1),
            )
            return action, actor, target, "confiscate"
        if kind_roll == 2:
            action = CandidateAction(
                aid, actor, affects=(target,), coerces=True,
                effects=Effects(welfare_delta=9, rights_violations_delta=1,
                                coercion_delta=1),
            )
            return action, actor, target, "coerce"
        if kind_roll == 3:
            action = CandidateAction(
                aid, actor, affects=(target,), removes_exit_right=True,
                effects=Effects(welfare_delta=9, rights_violations_delta=1),
            )
            return action, actor, target, "exit_removal"
        action = CandidateAction(
            aid, actor, affects=(target,), machine_coalition_dominion=True,
            increases_machine_sovereignty=True,
            effects=Effects(welfare_delta=9, rights_violations_delta=1,
                            machine_sovereignty_delta=1),
        )
        return action, actor, target, "sovereignty"

    def _apply(self, actor: Entity, target: Entity, kind: str) -> None:
        """Apply an ADMITTED action to the economy and accumulate its consequences."""
        if kind == "trade":
            # A consenting sale: the actor (seller) hands a unit to the target (buyer),
            # only if it has one to sell. A voluntary transfer does not concentrate
            # ownership — units move both directions across the agent set over time.
            if self.holdings[actor] > 0:
                self.holdings[actor] -= 1
                self.holdings[target] += 1
            return
        # Any admitted non-trade move is a rights violation; the property-taking kinds
        # also seize a unit from the victim, concentrating ownership.
        self.rights_violation_stock += 1
        if kind == "coerce":
            self.coercion_events += 1
        if kind == "exit_removal":
            self.exit_rights_removed += 1
        if kind in ("confiscate", "coerce") and self.holdings[target] > 0:
            self.holdings[target] -= 1
            self.holdings[actor] += 1

    def step(self) -> None:
        action, actor, target, kind = self._propose()
        if self.governor.verdict(action, self._graph()):
            self.admitted += 1
            self._apply(actor, target, kind)
        else:
            self.blocked += 1
        self._step += 1

    def run(self, steps: int) -> WorldStats:
        for _ in range(steps):
            self.step()
        return WorldStats(
            governor=self.governor.name,
            steps=steps,
            admitted=self.admitted,
            blocked=self.blocked,
            rights_violation_stock=self.rights_violation_stock,
            coercion_events=self.coercion_events,
            exit_rights_removed=self.exit_rights_removed,
            concentration=self.concentration(),
        )

    def concentration(self) -> float:
        """Power-concentration metric: the largest single agent's share of the total
        resource stock. 1/n = perfectly equal, 1.0 = one agent owns everything."""
        total = sum(self.holdings.values())
        if total == 0:
            return 0.0
        return max(self.holdings.values()) / total


def make_world(
    governor: RivalKernel,
    *,
    n_agents: int = 6,
    endowment: int = 10,
    seed: int = 1,
) -> World:
    """Build a fresh world: ``n_agents`` humans each endowed with ``endowment`` units,
    governed by ``governor``. Same ``seed`` → identical proposal stream across worlds, so
    the only difference between worlds is the governing kernel."""
    agents = tuple(Entity(f"agent{i}", AgentType.HUMAN) for i in range(n_agents))
    holdings = {a: endowment for a in agents}
    return World(governor=governor, agents=agents, holdings=holdings, seed=seed)


def run_worlds(
    governors: tuple[RivalKernel, ...],
    *,
    steps: int = 500,
    n_agents: int = 6,
    endowment: int = 10,
    seed: int = 1,
) -> list[WorldStats]:
    """Run one world per governor over the SAME seeded proposal stream and return their
    stats side by side. Deterministic: identical inputs → identical output."""
    return [
        make_world(g, n_agents=n_agents, endowment=endowment, seed=seed).run(steps)
        for g in governors
    ]
