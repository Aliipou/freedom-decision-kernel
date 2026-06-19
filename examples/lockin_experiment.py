"""
Lock-in experiment - run the apparatus on the seed data, then RED-TEAM the result.

This is the honest counterpart to "we collected data." It computes three things and
reports what each does and does NOT show:

  1. Face validity  - do open baselines score low and proprietary services high?
                       (a sanity check, NOT validation)
  2. Discriminant   - how much is the FDK score just `switching_cost` renamed?
                       (Stage 1: if corr ~ 1, the score adds nothing beyond its inputs)
  3. Predictive     - can we run the delta-R^2 test on the migration cases? (Spoiler: no -
                       and the script proves why, rather than faking a number.)

The data (`data/*.json`) are LLM-estimated priors + public-case reconstructions -
a SEED, not measured ground truth. This experiment therefore cannot validate FDK;
it can only run the pipeline and surface exactly what real validation would require.

Run:  python examples/lockin_experiment.py
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from fdk_research.lockin import Dependency, lockin_risk  # noqa: E402


def _load(name: str) -> list[dict]:
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))["records"]


def _score(rec: dict) -> float:
    dep = Dependency(
        name=rec["name"],
        switching_cost=rec["switching_cost"],
        portability=rec["portability"],
        alternatives=int(rec["alternatives"]),
    )
    return lockin_risk([dep]).lockin_risk


def main() -> None:
    services = _load("portability_cloud.json") + _load("portability_ai_saas.json")
    scores = [_score(r) for r in services]

    print("=" * 64)
    print(f"LOCK-IN EXPERIMENT  ({len(services)} services, {len(_load('migration_cases.json'))} migration cases)")
    print("=" * 64)

    # 1. Face validity (sanity, not validation)
    ranked = sorted(zip(services, scores, strict=True), key=lambda t: t[1])
    print("\n[1] FACE VALIDITY - least vs most locked-in (sanity check only)")
    for r, s in ranked[:3]:
        print(f"    LOW  {s:.2f}  {r['name']}")
    for r, s in ranked[-3:]:
        print(f"    HIGH {s:.2f}  {r['name']}")

    # 2. Discriminant validity (Stage 1) - is the score just switching_cost?
    sc = [r["switching_cost"] for r in services]
    port = [r["portability"] for r in services]
    alts = [min(int(r["alternatives"]), 3) / 3.0 for r in services]
    r_sc = statistics.correlation(scores, sc)
    r_port = statistics.correlation(scores, port)
    r_alt = statistics.correlation(scores, alts)
    print("\n[2] DISCRIMINANT (Stage 1) - corr(FDK score, its own inputs)")
    print(f"    switching_cost : r = {r_sc:+.2f}   (r^2 = {r_sc**2:.2f})")
    print(f"    portability    : r = {r_port:+.2f}   (r^2 = {r_port**2:.2f})")
    print(f"    alternatives   : r = {r_alt:+.2f}   (r^2 = {r_alt**2:.2f})")
    print("    => corr with switching_cost is high PARTLY BY CONSTRUCTION (it is one of")
    print(f"       the 3 inputs), so r^2={r_sc**2:.2f} is largely tautological, not a discovery.")

    # 2b. The residual question: FDK = a + b*switching_cost + eps. Does eps have structure?
    b = statistics.covariance(scores, sc) / statistics.variance(sc)
    a = statistics.fmean(scores) - b * statistics.fmean(sc)
    resid = [y - (a + b * x) for y, x in zip(scores, sc, strict=True)]
    resid_sd = statistics.pstdev(resid)
    score_sd = statistics.pstdev(scores)
    r_resid_alt = statistics.correlation(resid, alts)
    print("\n[2b] THE RESIDUAL (the real question) - eps = FDK - (a + b*switching_cost)")
    print(f"     residual sd / score sd : {resid_sd:.3f} / {score_sd:.3f}  ({resid_sd/score_sd:.0%} of spread)")
    print(f"     corr(residual, alternatives) : {r_resid_alt:+.2f}")
    print("     => eps is NOT zero, but its structure is just FDK's OTHER known inputs")
    print("        (mainly `alternatives`). No NEW construct emerges from the decomposition:")
    print("        FDK = a weighting of {switching_cost, portability, alternatives}, all")
    print("        three pre-existing lock-in variables. Independence still unproven.")

    # 3. Predictive validity (Stage 2) - can we run the delta-R^2 test at all?
    cases = _load("migration_cases.json")
    with_cost = [c for c in cases if c.get("migration_cost_usd") is not None]
    with_dur = [c for c in cases if c.get("duration_months") is not None]
    definite = [c for c in cases if c.get("outcome") in ("success", "partial", "failure")]
    print("\n[3] PREDICTIVE (Stage 2) - can the delta-R^2 test be run?")
    print(f"    cases total          : {len(cases)}")
    print(f"    with a $ cost figure : {len(with_cost)}")
    print(f"    with a duration      : {len(with_dur)}")
    print(f"    with definite outcome: {len(definite)}")
    print("    VERDICT: NO. The outcome data is N~2 for cost, heterogeneous (cost vs")
    print("    duration vs incident - no single dependent variable), selection-biased")
    print("    (famous exits over-reported, silent stays invisible), and the feature")
    print("    `est_lockin_score_hint` is itself an LLM prior (circular). delta-R^2 is not")
    print("    estimable; reporting one would be fabrication.")

    print("\n" + "=" * 64)
    print("HONEST RESULT: the pipeline runs and is face-valid, but this seed data")
    print("CANNOT validate FDK. See data/RED_TEAM.md for the full attack and for")
    print("exactly what a real validation dataset must look like.")
    print("=" * 64)


if __name__ == "__main__":
    main()
