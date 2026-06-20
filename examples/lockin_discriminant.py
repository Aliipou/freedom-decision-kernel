"""
Stage-1 discriminant test for the lock-in / reversibility construct (outcome-free).

WHY THIS EXISTS
---------------
The red team reported corr(FDK lock-in score, switching_cost) = +0.99, r^2 = 0.97 on
the seed and read it as "the construct is just switching_cost renamed." The green team
(paper/green_team/03_defend_reversibility_construct.md, SYMPOSIUM.md III) replied that
0.97 is a SEED ARTIFACT, not a property of the construct, because on the seed:
  (a) switching_cost enters escapability() at weight exactly 1/3;
  (b) the LLM co-rated switching_cost and portability as collinear (corr = -0.959);
  (c) the alternatives clamp min(alt,3)/3 crushed 61/62 records to 1.0; and
  (d) every seed portfolio is N=1, so HHI concentration never varied.

A 1/3-weighted input cannot mechanically explain 97% of the output's variance UNLESS
the other two thirds are nearly collinear with it. So the green team predicts: feed the
SAME apparatus de-collinearized, independent inputs and r^2(score, switching_cost) should
fall toward ~1/3. That is a CHEAP, outcome-free discriminant test. This script runs it.

WHAT THIS DOES / DOES NOT SHOW (read the printed HONEST INTERPRETATION block too)
  - It tests Stage-1 DISCRIMINANT validity: is the score reducible to switching_cost?
  - It does NOT test Stage-2 PREDICTIVE validity (delta-R^2 vs real migration outcomes).
    That still needs real outcome data and is explicitly NOT attempted here.

Run:  PYTHONPATH=src python examples/lockin_discriminant.py
"""
from __future__ import annotations

import random
import statistics

from fdk_research.lockin import Dependency, lockin_risk

SEED = 20260620
N_SERVICES = 400
N_PORTFOLIOS = 200


def _r2(xs: list[float], ys: list[float]) -> float:
    """R^2 of the simple linear regression ys ~ xs = squared Pearson correlation.

    Uses statistics.correlation when the predictor has variance; returns 0.0 for a
    degenerate (constant) predictor, since a constant explains no variance.
    """
    if statistics.pvariance(xs) == 0.0 or statistics.pvariance(ys) == 0.0:
        return 0.0
    r = statistics.correlation(xs, ys)
    return r * r


def _residuals(xs: list[float], ys: list[float]) -> list[float]:
    """Residuals of ys after the OLS fit ys ~ xs (the part xs cannot explain)."""
    b = statistics.covariance(ys, xs) / statistics.variance(xs)
    a = statistics.fmean(ys) - b * statistics.fmean(xs)
    return [y - (a + b * x) for x, y in zip(xs, ys, strict=True)]


def gen_services(rng: random.Random, n: int) -> list[Dependency]:
    """n single services with INDEPENDENT, de-collinearized features.

    switching_cost ~ U(0,1) and portability ~ U(0,1) are sampled INDEPENDENTLY (the
    seed's -0.96 mirror-rating artifact is removed). alternatives ~ integer U(0,3) so the
    existing min(alt,3)/3 clamp does NOT crush the axis to a constant.
    """
    return [
        Dependency(
            name=f"svc_{i}",
            switching_cost=rng.random(),
            portability=rng.random(),
            alternatives=rng.randint(0, 3),
        )
        for i in range(n)
    ]


def single_service_discriminant(services: list[Dependency]) -> dict[str, float]:
    """Score each service alone; regress the score on each input separately -> R^2."""
    scores = [lockin_risk([s]).lockin_risk for s in services]
    sc = [s.switching_cost for s in services]
    port = [s.portability for s in services]
    alt = [min(s.alternatives, 3) / 3.0 for s in services]  # the value the formula uses

    # observed input collinearity (the thing the seed got wrong: it was -0.959)
    corr_sc_port = statistics.correlation(sc, port)

    return {
        "r2_switching_cost": _r2(sc, scores),
        "r2_portability": _r2(port, scores),
        "r2_alternatives": _r2(alt, scores),
        "corr_sc_port": corr_sc_port,
    }


def gen_portfolios(rng: random.Random, n: int) -> list[list[Dependency]]:
    """n portfolios of N=3..8 services with VARIED weights so HHI concentration varies."""
    portfolios = []
    for p in range(n):
        size = rng.randint(3, 8)
        deps = []
        for j in range(size):
            deps.append(
                Dependency(
                    name=f"p{p}_d{j}",
                    weight=rng.random(),  # varied weights -> HHI spreads across portfolios
                    switching_cost=rng.random(),
                    portability=rng.random(),
                    alternatives=rng.randint(0, 3),
                )
            )
        portfolios.append(deps)
    return portfolios


def portfolio_discriminant(portfolios: list[list[Dependency]]) -> dict[str, float]:
    """Rival baseline = mean switching_cost. Does FDK reduce to it? Does the residual
    pick up portfolio STRUCTURE (HHI concentration) that mean-switching-cost misses?"""
    scores = [lockin_risk(p).lockin_risk for p in portfolios]
    hhi = [lockin_risk(p).concentration for p in portfolios]
    mean_sc = [statistics.fmean([d.switching_cost for d in p]) for p in portfolios]

    r2_mean_sc = _r2(mean_sc, scores)
    resid = _residuals(mean_sc, scores)
    corr_resid_hhi = statistics.correlation(resid, hhi)

    return {
        "r2_mean_switching_cost": r2_mean_sc,
        "corr_residual_hhi": corr_resid_hhi,
        "hhi_min": min(hhi),
        "hhi_max": max(hhi),
        "hhi_sd": statistics.pstdev(hhi),
    }


def main() -> None:
    rng = random.Random(SEED)

    print("=" * 70)
    print("STAGE-1 DISCRIMINANT TEST  (de-collinearized synthetic inputs, outcome-free)")
    print(f"seed={SEED}  services={N_SERVICES}  portfolios={N_PORTFOLIOS}")
    print("=" * 70)

    services = gen_services(rng, N_SERVICES)
    s = single_service_discriminant(services)

    print("\n[1] SINGLE-SERVICE  score ~ each input, regressed SEPARATELY  (R^2)")
    print(f"    input collinearity corr(switching_cost, portability) = {s['corr_sc_port']:+.3f}")
    print("    (seed had -0.959; near 0 here means the mirror-rating artifact is removed)")
    print(f"    switching_cost : R^2 = {s['r2_switching_cost']:.3f}")
    print(f"    portability    : R^2 = {s['r2_portability']:.3f}")
    print(f"    alternatives   : R^2 = {s['r2_alternatives']:.3f}")
    print("    PREDICTION (green team): with de-collinearized inputs each 1/3-weighted")
    print("    term explains ~1/3 of variance, so R^2(switching_cost) ~ 0.33, NOT 0.97.")

    portfolios = gen_portfolios(rng, N_PORTFOLIOS)
    pr = portfolio_discriminant(portfolios)

    print("\n[2] PORTFOLIO  score ~ mean_switching_cost (the rival baseline)  (R^2)")
    print(f"    HHI concentration spread: min={pr['hhi_min']:.3f} max={pr['hhi_max']:.3f} "
          f"sd={pr['hhi_sd']:.3f}  (varies, unlike the N=1 seed where HHI==1)")
    print(f"    R^2(score ~ mean_switching_cost)      = {pr['r2_mean_switching_cost']:.3f}")
    print(f"    corr(residual, HHI concentration)     = {pr['corr_residual_hhi']:+.3f}")
    print("    => if mean_switching_cost leaves R^2 well below 1.0 AND the residual")
    print("       correlates with HHI, portfolio STRUCTURE is a dimension the per-vendor")
    print("       switching-cost baseline provably cannot encode.")

    # ---- HONEST INTERPRETATION (auto-generated from the REAL numbers above) ----
    r2sc = s["r2_switching_cost"]
    print("\n" + "=" * 70)
    print("HONEST INTERPRETATION")
    print("=" * 70)
    if r2sc < 0.6:
        print(f"- De-collinearized R^2(score ~ switching_cost) = {r2sc:.3f}, FAR below the")
        print("  seed's 0.97. The green team is RIGHT on Stage 1: the 0.97 was a SEED")
        print("  ARTIFACT (collinear inputs + a saturating clamp), not a property of the")
        print("  construct. On honest data the score is NOT reducible to switching_cost.")
    else:
        print(f"- De-collinearized R^2(score ~ switching_cost) = {r2sc:.3f}, still high.")
        print("  The green team's 'artifact' claim is NOT supported by this run.")
    print("- BOUNDARY (stated honestly): the score is still built ONLY from KNOWN")
    print("  variables (switching_cost, portability, alternatives, and at portfolio level")
    print("  HHI concentration). This shows the score is a NON-REDUNDANT COMBINATION /")
    print("  operationalization of those inputs -- NOT proof of a new LATENT variable.")
    print("- NOT TESTED HERE: predictive independence (Stage-2 delta-R^2) needs REAL")
    print("  migration OUTCOME data; this outcome-free test cannot and does not show it.")
    print("=" * 70)


if __name__ == "__main__":
    main()
