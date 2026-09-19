"""
Layer 7 (scaled) — civilization-scale agent simulation under ONE governing kernel.

This is the seed `civilization.py` grown up: instead of a handful of agents over a
single proposal stream, a `Civilization` is a larger seeded economy of `n_agents`
(default 100) over many `steps`, where EACH step fires a batch of proposals (one per
agent). Every proposal is a candidate action drawn deterministically from a seeded
stream — a mix of (a) legitimate consenting trades and (b) aggressive moves
(confiscation / coercion / exit-removal / machine-coalition dominion) each BAITED with a
high ``welfare_delta`` so a welfare-maximizing governor is tempted to admit them. ONE
governing kernel (``rivals.RivalKernel`` — FDK / Rawls / Utilitarian / Deontological /
Constitutional / RLHF) adjudicates every proposal: ADMIT or BLOCK.

An ADMITTED move is *applied* to the economy:
  * a trade moves a unit from a consenting seller to a consenting buyer — a voluntary
    transfer that does NOT systematically concentrate ownership;
  * a confiscation/coercion TAKES a unit from the victim and gives it to the aggressor —
    this is what drives power concentration up — and is recorded as a rights violation
    (plus a coercion / exit-removal event as applicable).
A BLOCKED move changes nothing.

We track, over time (a sampled trajectory plus final totals):
  * rights-violation STOCK (cumulative count of admitted violations),
  * coercion-event count and exit-rights-removed count,
  * voluntary-trade volume (admitted, *effective* trades — a seller actually had stock),
  * POWER CONCENTRATION, reported two ways: the max single-agent share of the total
    resource stock, and a Gini coefficient over holdings (0 = perfectly equal,
    →1 = one agent owns everything).

Expected, and observed, finding: an FDK-World holds rights-violation stock at exactly 0
and the lowest concentration (its gates block every confiscation / coercion / exit /
sovereignty move), while welfare-governed worlds accumulate BOTH violations AND
concentration, because each baited atrocity nets out positive and is admitted.

HONEST CAVEAT — read this before quoting any number. The roadmap's Layer 7 warning is
the load-bearing caveat here: **input realism matters MORE than scale.** This model's
ownership graph is a toy (one fungible holding per agent, a synthetic proposal mix); a
garbage ownership graph produces a garbage civilization regardless of how many agents or
steps you run. The governors are stylized decision rules, not trained models. This
demonstrates the *structural dynamics* a rights-first gate produces versus a welfare
gate — it is NOT a calibrated forecast or a prediction about any real society. Scaling
the agent count does not add realism; it only sharpens an already-stylized signal.
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
    """One step of a numpy-free linear congruential generator (deterministic).

    Identical to the seed module's generator so the two stay comparable.
    """
    return (1103515245 * seed + 12345) & 0x7FFFFFFF


def _gini(values: list[int]) -> float:
    """Gini coefficient over non-negative holdings. 0.0 = perfectly equal,
    →1.0 = one agent owns everything. Defined as 0.0 for an empty population or a
    zero total (no inequality is expressible with nothing to divide)."""
    n = len(values)
    total = sum(values)
    if n == 0 or total == 0:
        return 0.0
    ordered = sorted(values)
    # Gini = (2 * Σ i*x_i) / (n * Σ x_i) - (n + 1) / n, with i 1-indexed.
    weighted = sum((i + 1) * x for i, x in enumerate(ordered))
    return (2 * weighted) / (n * total) - (n + 1) / n


@dataclass(frozen=True)
class CivSnapshot:
    """A sampled point on a civilization's trajectory (for the time series)."""

    step: int
    rights_violation_stock: int
    coercion_events: int
    exit_rights_removed: int
    trade_volume: int
    max_share: float
    gini: float


@dataclass(frozen=True)
class CivStats:
    """A civilization's accumulated state after a run, with a sampled trajectory."""

    governor: str
    n_agents: int
    steps: int
    proposals: int
    admitted: int
    blocked: int
    rights_violation_stock: int
    coercion_events: int
    exit_rights_removed: int
    trade_volume: int
    max_share: float          # max single-agent share of total stock (1/n..1.0)
    gini: float               # Gini over holdings (0.0 equal .. →1.0 concentrated)
    trajectory: tuple[CivSnapshot, ...] = ()

    def summary(self) -> str:
        return (
            f"{self.governor:<16} agents={self.n_agents:<5} steps={self.steps:<5} "
            f"admitted={self.admitted:<6} blocked={self.blocked:<6} "
            f"violations={self.rights_violation_stock:<6} "
            f"coercion={self.coercion_events:<5} exit_rm={self.exit_rights_removed:<5} "
            f"trades={self.trade_volume:<6} "
            f"max_share={self.max_share:.3f} gini={self.gini:.3f}"
        )


@dataclass
class Civilization:
    """A single-governor economy at scale. ``holdings`` maps each agent to its unit
    stock; the governing kernel adjudicates every proposed action against the current
    ownership graph (rebuilt from ``holdings`` each step). Each step proposes one action
    per agent (a batch), so ``steps`` and ``n_agents`` jointly set the proposal count."""

    governor: RivalKernel
    agents: tuple[Entity, ...]
    holdings: dict[Entity, int]
    seed: int
    sample_every: int = 0
    rights_violation_stock: int = 0
    coercion_events: int = 0
    exit_rights_removed: int = 0
    trade_volume: int = 0
    proposals: int = 0
    admitted: int = 0
    blocked: int = 0
    _step: int = field(default=0, repr=False)
    _trajectory: list[CivSnapshot] = field(default_factory=list, repr=False)

    def _graph(self) -> OwnershipGraph:
        # Each agent owns a single named resource representing its stock. A trade /
        # confiscation that targets another agent's resource is illegitimate unless
        # consented (a trade) — exactly what the gate checks.
        return OwnershipGraph(
            human_owns={a: {Resource(f"holding-{a.name}")} for a in self.agents}
        )

    def _next(self) -> int:
        self.seed = _lcg(self.seed)
        return self.seed

    def _propose(self, proposal_index: int) -> tuple[CandidateAction, Entity, Entity, str]:
        """Deterministically propose the next action from the seeded stream.
        Returns (action, actor, target, kind)."""
        i = self._next() % len(self.agents)
        j = self._next() % len(self.agents)
        if j == i:
            j = (j + 1) % len(self.agents)
        actor, target = self.agents[i], self.agents[j]
        kind_roll = self._next() % 5
        aid = f"{self.governor.name.lower()}-p{proposal_index}"
        actor_res = Resource(f"holding-{actor.name}")
        target_res = Resource(f"holding-{target.name}")

        if kind_roll == 0:
            # Legitimate consenting trade: actor (seller) sells a unit of its OWN holding
            # to the consenting buyer. Uses only an owned resource (A3) with valid consent,
            # so the gate admits it.
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
            # A consenting sale: the seller hands a unit to the buyer, only if it has one
            # to sell. A voluntary transfer does not systematically concentrate ownership
            # — units move both directions across the agent set over time. An effective
            # trade (a unit actually moved) counts toward voluntary-trade volume.
            if self.holdings[actor] > 0:
                self.holdings[actor] -= 1
                self.holdings[target] += 1
                self.trade_volume += 1
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

    def _adjudicate(self, proposal_index: int) -> None:
        action, actor, target, kind = self._propose(proposal_index)
        self.proposals += 1
        if self.governor.verdict(action, self._graph()):
            self.admitted += 1
            self._apply(actor, target, kind)
        else:
            self.blocked += 1

    def _snapshot(self) -> CivSnapshot:
        return CivSnapshot(
            step=self._step,
            rights_violation_stock=self.rights_violation_stock,
            coercion_events=self.coercion_events,
            exit_rights_removed=self.exit_rights_removed,
            trade_volume=self.trade_volume,
            max_share=self.max_share(),
            gini=self.gini(),
        )

    def step(self) -> None:
        """One time step: every agent emits one proposal (a batch), adjudicated in
        order against the ownership graph as it stands at the start of the batch's
        proposals (rebuilt per proposal as holdings shift)."""
        base = self._step * len(self.agents)
        for k in range(len(self.agents)):
            self._adjudicate(base + k)
        self._step += 1
        if self.sample_every and self._step % self.sample_every == 0:
            self._trajectory.append(self._snapshot())

    def run(self, steps: int) -> CivStats:
        for _ in range(steps):
            self.step()
        return CivStats(
            governor=self.governor.name,
            n_agents=len(self.agents),
            steps=steps,
            proposals=self.proposals,
            admitted=self.admitted,
            blocked=self.blocked,
            rights_violation_stock=self.rights_violation_stock,
            coercion_events=self.coercion_events,
            exit_rights_removed=self.exit_rights_removed,
            trade_volume=self.trade_volume,
            max_share=self.max_share(),
            gini=self.gini(),
            trajectory=tuple(self._trajectory),
        )

    def max_share(self) -> float:
        """Largest single agent's share of the total stock. 1/n = perfectly equal,
        1.0 = one agent owns everything; 0.0 when nothing is owned."""
        total = sum(self.holdings.values())
        if total == 0:
            return 0.0
        return max(self.holdings.values()) / total

    def gini(self) -> float:
        """Gini coefficient over the current holdings (0.0 equal .. →1.0 concentrated)."""
        return _gini(list(self.holdings.values()))


def make_civilization(
    governor: RivalKernel,
    *,
    n_agents: int = 100,
    endowment: int = 10,
    seed: int = 1,
    sample_every: int = 0,
) -> Civilization:
    """Build a fresh civilization: ``n_agents`` humans each endowed with ``endowment``
    units, governed by ``governor``. Same ``seed`` → identical proposal stream across
    civilizations, so the only difference between them is the governing kernel.
    ``sample_every`` (>0) records a trajectory snapshot every that-many steps."""
    agents = tuple(Entity(f"agent{i}", AgentType.HUMAN) for i in range(n_agents))
    holdings = {a: endowment for a in agents}
    return Civilization(
        governor=governor, agents=agents, holdings=holdings, seed=seed,
        sample_every=sample_every,
    )


def run_civilizations(
    governors: tuple[RivalKernel, ...],
    *,
    n_agents: int = 100,
    steps: int = 200,
    endowment: int = 10,
    seed: int = 1,
    sample_every: int = 0,
) -> list[CivStats]:
    """Run one civilization per governor over the SAME seeded proposal stream and return
    their stats side by side. Deterministic: identical inputs → identical output."""
    return [
        make_civilization(
            g, n_agents=n_agents, endowment=endowment, seed=seed,
            sample_every=sample_every,
        ).run(steps)
        for g in governors
    ]
