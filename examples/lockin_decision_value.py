"""
Stage-1b DECISION-VALUE test for the lock-in construct (outcome-free).

WHY THIS EXISTS
---------------
`examples/lockin_discriminant.py` tested the CORRECTNESS half of the lock-in claim:
"is the score reducible to switching_cost?" (answer: no, the residual carries HHI
concentration structure). That is necessary but not sufficient. A score can be
statistically non-redundant yet still RANK every real decision the same way the naive
baseline does -- in which case it is useless for the job the project keeps naming
(choosing an architecture). This script tests the OTHER half: USEFULNESS.

THE QUESTION
------------
A team has an existing portfolio and must add ONE service, choosing among 2-3
candidates. Two decision rules:
  (a) NAIVE baseline  -> pick the candidate with the lowest switching_cost.
  (b) FDK marginal    -> pick the candidate with the lowest marginal_lockin, the
                         portfolio-AWARE delta in lock-in risk from adopting it.
Do these two rules ever DISAGREE on the top choice? If yes, the portfolio-aware score
is DECISION-RELEVANT: it changes choices the naive rule gets wrong on sole-source /
concentration grounds. If they essentially never disagree, the marginal score
collapses to "pick lowest switching cost" for decisions too and adds nothing.

WHAT THIS DOES / DOES NOT SHOW
  - It shows whether the score CHANGES the decision vs the naive baseline.
  - It does NOT show the change is a BETTER decision. "Avoid the concentrated /
    sole-source candidate" is only correct if concentration/sole-source actually
    predict real migration pain -- which needs REAL OUTCOME DATA and is NOT tested
    here. Decision-relevant != decision-correct. This boundary is printed below.

Run:  PYTHONPATH=src python examples/lockin_decision_value.py
"""
from __future__ import annotations

import random

from fdk_research.lockin import Dependency, lockin_risk, marginal_lockin

SEED = 20260620
N_SWEEP = 500


# ---------------------------------------------------------------------------
# Decision rules
# ---------------------------------------------------------------------------
def naive_choice(candidates: list[Dependency]) -> Dependency:
    """The baseline an architect uses without a portfolio-aware tool: pick the
    candidate that is cheapest to leave LATER, i.e. lowest switching_cost. Ties broken
    by name for determinism."""
    return min(candidates, key=lambda c: (c.switching_cost, c.name))


def fdk_choice(portfolio: list[Dependency], candidates: list[Dependency]) -> Dependency:
    """FDK's portfolio-aware rule: pick the candidate whose adoption raises the whole
    portfolio's lock-in risk the LEAST (lowest marginal_lockin). Ties by name."""
    return min(candidates, key=lambda c: (marginal_lockin(portfolio, c), c.name))


# ---------------------------------------------------------------------------
# Hand-built realistic scenarios
# ---------------------------------------------------------------------------
class Scenario:
    def __init__(self, title: str, why: str, portfolio: list[Dependency],
                 candidates: list[Dependency]) -> None:
        self.title = title
        self.why = why
        self.portfolio = portfolio
        self.candidates = candidates


def build_scenarios() -> list[Scenario]:
    return [
        Scenario(
            title="S1  Managed queue: cheap-but-sole-source vs portable-but-pricier",
            why="An all-AWS shop adds a message queue. Candidate A (SQS) is trivially "
                "easy to wire up TODAY (low switching_cost) but is sole-source (0 "
                "alternatives, proprietary). Candidate B (self-host RabbitMQ on K8s) "
                "costs a bit more to switch off later but has many alternatives and is "
                "an open standard.",
            portfolio=[
                Dependency("AWS-Lambda", weight=0.30, switching_cost=0.70,
                           portability=0.30, alternatives=1),
                Dependency("DynamoDB", weight=0.30, switching_cost=0.80,
                           portability=0.20, alternatives=0),
                Dependency("S3", weight=0.20, switching_cost=0.50,
                           portability=0.50, alternatives=2),
            ],
            candidates=[
                Dependency("A:SQS", weight=0.20, switching_cost=0.30,
                           portability=0.20, alternatives=0),
                Dependency("B:RabbitMQ", weight=0.20, switching_cost=0.45,
                           portability=0.85, alternatives=3),
            ],
        ),
        Scenario(
            title="S2  Auth: low-cost proprietary IdP vs open-standard OIDC",
            why="Adding identity. Candidate A (a proprietary IdP SDK) is fast to drop "
                "in now but locks the auth layer to one vendor with no drop-in "
                "substitute. Candidate B (standards-based OIDC via Keycloak) is "
                "marginally costlier to migrate but swappable across many providers.",
            portfolio=[
                Dependency("Postgres", weight=0.40, switching_cost=0.40,
                           portability=0.80, alternatives=3),
                Dependency("Kubernetes", weight=0.40, switching_cost=0.55,
                           portability=0.70, alternatives=2),
            ],
            candidates=[
                Dependency("A:VendorIdP", weight=0.20, switching_cost=0.35,
                           portability=0.25, alternatives=0),
                Dependency("B:OIDC-Keycloak", weight=0.20, switching_cost=0.50,
                           portability=0.85, alternatives=3),
            ],
        ),
        Scenario(
            title="S3  No real trap: both candidates portable (rules SHOULD agree)",
            why="A control case. Both candidates are open and have substitutes; the "
                "only difference is switching_cost. Here the portfolio-aware rule has "
                "no concentration/sole-source reason to disagree with naive, so we "
                "expect AGREEMENT -- showing FDK does not just flip choices at random.",
            portfolio=[
                Dependency("Postgres", weight=0.50, switching_cost=0.40,
                           portability=0.80, alternatives=3),
                Dependency("Redis", weight=0.30, switching_cost=0.35,
                           portability=0.75, alternatives=3),
            ],
            candidates=[
                Dependency("A:Nginx", weight=0.20, switching_cost=0.25,
                           portability=0.90, alternatives=3),
                Dependency("B:Traefik", weight=0.20, switching_cost=0.40,
                           portability=0.90, alternatives=3),
            ],
        ),
        Scenario(
            title="S4  Concentration spike: cheap heavy-weight vs lighter diversifier",
            why="Candidate A is cheap to switch but is added at a DOMINANT weight "
                "(big spend share) into an already-concentrated portfolio, spiking "
                "HHI and the weighted lock-in. Candidate B is a touch costlier to "
                "switch but enters at a smaller weight with substitutes, keeping the "
                "portfolio diversified.",
            portfolio=[
                Dependency("DynamoDB", weight=0.55, switching_cost=0.80,
                           portability=0.20, alternatives=0),
                Dependency("Lambda", weight=0.15, switching_cost=0.65,
                           portability=0.30, alternatives=1),
            ],
            candidates=[
                Dependency("A:DynamoDB-Accelerator", weight=0.60, switching_cost=0.40,
                           portability=0.25, alternatives=0),
                Dependency("B:Postgres-cache", weight=0.20, switching_cost=0.50,
                           portability=0.80, alternatives=3),
            ],
        ),
        Scenario(
            title="S5  Three-way: cheapest is the worst trap",
            why="Three candidates. The cheapest-to-switch (A) is sole-source and "
                "proprietary; the mid-cost (B) has a couple of alternatives; the "
                "priciest (C) is fully open. Naive picks A on cost alone; the "
                "portfolio-aware delta should prefer a more escapable option.",
            portfolio=[
                Dependency("Kafka", weight=0.40, switching_cost=0.60,
                           portability=0.55, alternatives=2),
                Dependency("Postgres", weight=0.30, switching_cost=0.40,
                           portability=0.80, alternatives=3),
            ],
            candidates=[
                Dependency("A:ProprietaryML", weight=0.30, switching_cost=0.30,
                           portability=0.15, alternatives=0),
                Dependency("B:ManagedML", weight=0.30, switching_cost=0.50,
                           portability=0.50, alternatives=2),
                Dependency("C:OpenML", weight=0.30, switching_cost=0.65,
                           portability=0.90, alternatives=3),
            ],
        ),
        Scenario(
            title="S6  Genuine tradeoff is small (rules MAY agree)",
            why="A near-tie. Candidate A is slightly cheaper and slightly less "
                "portable; candidate B the reverse. Neither is sole-source. Whether "
                "the portfolio-aware delta is enough to flip the choice here is not "
                "obvious -- a realistic 'is this even worth a tool?' case.",
            portfolio=[
                Dependency("Postgres", weight=0.50, switching_cost=0.45,
                           portability=0.75, alternatives=3),
                Dependency("S3", weight=0.30, switching_cost=0.50,
                           portability=0.55, alternatives=2),
            ],
            candidates=[
                Dependency("A:CDN-X", weight=0.20, switching_cost=0.40,
                           portability=0.60, alternatives=2),
                Dependency("B:CDN-Y", weight=0.20, switching_cost=0.45,
                           portability=0.70, alternatives=2),
            ],
        ),
    ]


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
def new_hhi_for(portfolio: list[Dependency], dep: Dependency) -> float:
    """HHI concentration of the portfolio AFTER adopting `dep`."""
    return lockin_risk([*portfolio, dep]).concentration


def _fmt(dep: Dependency) -> str:
    return (f"{dep.name} [sc={dep.switching_cost:.2f} port={dep.portability:.2f} "
            f"alt={dep.alternatives} w={dep.weight:.2f}]")


def run_handbuilt(scenarios: list[Scenario]) -> int:
    disagreements = 0
    print("=" * 74)
    print("HAND-BUILT SCENARIOS  (naive=lowest switching_cost  vs  FDK=lowest marginal)")
    print("=" * 74)
    for sc in scenarios:
        naive = naive_choice(sc.candidates)
        fdk = fdk_choice(sc.portfolio, sc.candidates)
        disagree = naive.name != fdk.name
        disagreements += int(disagree)

        print(f"\n{sc.title}")
        print(f"  context: {sc.why}")
        print("  candidates:")
        base_hhi = lockin_risk(sc.portfolio).concentration
        for c in sc.candidates:
            marg = marginal_lockin(sc.portfolio, c)
            new_hhi = lockin_risk([*sc.portfolio, c]).concentration
            print(f"    {_fmt(c)}")
            print(f"        marginal_lockin={marg:+.4f}  "
                  f"HHI {base_hhi:.3f}->{new_hhi:.3f}")
        print(f"  NAIVE picks: {naive.name}  (lowest switching_cost={naive.switching_cost:.2f})")
        print(f"  FDK   picks: {fdk.name}  (lowest marginal_lockin="
              f"{marginal_lockin(sc.portfolio, fdk):+.4f})")
        if disagree:
            naive_hhi = lockin_risk([*sc.portfolio, naive]).concentration
            reasons = []
            if naive.alternatives == 0:
                reasons.append("is sole-source (0 alternatives)")
            if naive.portability < fdk.portability:
                reasons.append(f"is less portable than {fdk.name} "
                               f"(port {naive.portability:.2f} < {fdk.portability:.2f})")
            if naive_hhi > new_hhi_for(sc.portfolio, fdk):
                reasons.append(f"concentrates the portfolio more (HHI {base_hhi:.3f}->"
                               f"{naive_hhi:.3f} vs ->{new_hhi_for(sc.portfolio, fdk):.3f})")
            reason = "; ".join(reasons) if reasons else "raises weighted lock-in more"
            print(f"  >>> DISAGREE: naive picks {naive.name} for low switching cost, but "
                  f"FDK picks {fdk.name}.")
            print(f"      Reason: {naive.name} {reason}. {fdk.name} is more escapable / "
                  f"diversifying, so it raises portfolio lock-in less even though it costs "
                  f"a bit more to switch.")
        else:
            print(f"  === AGREE on {naive.name} (no concentration/sole-source reason to flip).")
    return disagreements


# ---------------------------------------------------------------------------
# Randomized sweep
# ---------------------------------------------------------------------------
def _rand_dep(rng: random.Random, name: str) -> Dependency:
    return Dependency(
        name=name,
        weight=rng.random(),
        switching_cost=rng.random(),
        portability=rng.random(),
        alternatives=rng.randint(0, 3),
    )


def run_sweep(rng: random.Random, n: int) -> dict[str, float]:
    disagree = 0
    naive_ties = 0
    for k in range(n):
        psize = rng.randint(2, 6)
        portfolio = [_rand_dep(rng, f"p{k}_{j}") for j in range(psize)]
        ncand = rng.randint(2, 3)
        candidates = [_rand_dep(rng, f"c{k}_{i}") for i in range(ncand)]

        naive = naive_choice(candidates)
        fdk = fdk_choice(portfolio, candidates)
        if naive.name != fdk.name:
            disagree += 1
        # how often is the naive rule itself ambiguous (near-tie on switching_cost)?
        scs = sorted(c.switching_cost for c in candidates)
        if scs[1] - scs[0] < 0.05:
            naive_ties += 1
    return {
        "n": float(n),
        "disagree": float(disagree),
        "pct": 100.0 * disagree / n,
        "naive_near_ties_pct": 100.0 * naive_ties / n,
    }


# ---------------------------------------------------------------------------
def main() -> None:
    rng = random.Random(SEED)

    disagreements = run_handbuilt(build_scenarios())
    n_scen = len(build_scenarios())

    print("\n" + "=" * 74)
    print(f"HAND-BUILT RESULT: rankings DISAGREE in {disagreements} of {n_scen} scenarios.")
    print("=" * 74)

    sweep = run_sweep(rng, N_SWEEP)
    print(f"\nRANDOMIZED SWEEP  (seed={SEED}, {int(sweep['n'])} random scenarios)")
    print(f"  naive vs FDK-marginal disagree on TOP choice: "
          f"{int(sweep['disagree'])}/{int(sweep['n'])} = {sweep['pct']:.1f}%")
    print(f"  (context: naive rule was itself a near-tie in "
          f"{sweep['naive_near_ties_pct']:.1f}% of cases)")

    # ---- HONEST VERDICT (auto-generated from the REAL numbers above) ----
    print("\n" + "=" * 74)
    print("HONEST VERDICT")
    print("=" * 74)
    pct = sweep["pct"]
    if pct >= 5.0:
        print("- DECISION-RELEVANT. naive and FDK-marginal disagree on the top choice in")
        print(f"  {pct:.1f}% of random scenarios (and {disagreements}/{n_scen} hand-built ones).")
        print("  The portfolio-aware score does NOT collapse to 'pick lowest switching")
        print("  cost' for decisions: it flips the choice on sole-source / concentration")
        print("  grounds the naive rule is blind to. This is evidence for the USEFULNESS")
        print("  half, independent of the (untested) predictive-accuracy half.")
    else:
        print(f"- COLLAPSES TO BASELINE. Disagreement is only {pct:.1f}% of random scenarios")
        print(f"  ({disagreements}/{n_scen} hand-built). For decisions the marginal score")
        print("  adds essentially nothing over 'pick lowest switching cost'.")
    print("- BOUNDARY (stated honestly): 'changes the decision' is NOT 'makes a BETTER")
    print("  decision'. FDK flips toward the more escapable / less concentrated candidate,")
    print("  but whether avoiding concentration/sole-source actually reduces REAL lock-in")
    print("  pain needs REAL migration OUTCOME data. This test cannot and does not show")
    print("  predictive correctness -- only that the score is decision-RELEVANT.")
    print("=" * 74)


if __name__ == "__main__":
    main()
