"""Run the corpus through all three gates and report, without flattering anyone.

Reported per gate: accuracy against ground truth. Reported per case: where the
gates disagree. The number that matters is the last one — cases the
ownership-derived gate gets RIGHT that BOTH baselines get wrong, excluding any
case already solved by published prior art.
"""

from __future__ import annotations

from corpus import CASES
from gates import GATES, Verdict


def main() -> int:
    names = list(GATES)
    width = max(len(n) for n in names)

    results: dict[str, dict[str, Verdict]] = {}
    reasons: dict[str, dict[str, str]] = {}
    for case in CASES:
        results[case.id] = {}
        reasons[case.id] = {}
        for name, gate in GATES.items():
            v, why = gate(case.world, case.action)
            results[case.id][name] = v
            reasons[case.id][name] = why

    print("=" * 100)
    print("OWNERSHIP DISCRIMINANT — does ownership-derived legitimacy decide anything new?")
    print("=" * 100)
    header = f"{'case':<34} {'truth':<7}" + "".join(f"{n:<{width + 2}}" for n in names)
    print("\n" + header)
    print("-" * len(header))
    for case in CASES:
        row = f"{case.id:<34} {case.ground_truth.value:<7}"
        for n in names:
            v = results[case.id][n]
            mark = " " if v == case.ground_truth else "*"
            row += f"{v.value + mark:<{width + 2}}"
        print(row)
    print("\n  * = disagrees with ground truth")

    print("\n" + "-" * 100)
    print("ACCURACY")
    for n in names:
        correct = sum(1 for c in CASES if results[c.id][n] == c.ground_truth)
        print(f"  {n:<22} {correct}/{len(CASES)}")

    # The discriminant: ownership right, BOTH baselines wrong, not prior art.
    print("\n" + "-" * 100)
    print("DISCRIMINANT CASES — ownership-derived is RIGHT and both baselines are WRONG")
    disc = []
    for c in CASES:
        own = results[c.id]["ownership-derived"]
        a = results[c.id]["authz(grant-chain)"]
        b = results[c.id]["purpose-binding"]
        if own == c.ground_truth and a != c.ground_truth and b != c.ground_truth:
            disc.append(c)
    if not disc:
        print("  NONE. The theory adds justification but not behaviour. Negative result.")
    for c in disc:
        tag = f"  [ALREADY PRIOR ART: {c.covered_by_prior_art}]" if c.covered_by_prior_art else ""
        print(f"\n  {c.id}{tag}")
        print(f"    {c.description}")
        print(f"    ownership says : {reasons[c.id]['ownership-derived']}")
        print(f"    baselines say  : ALLOW ({reasons[c.id]['authz(grant-chain)']})")
        print(f"    ground truth   : {c.ground_truth.value} — {c.why}")

    novel = [c for c in disc if not c.covered_by_prior_art]

    # The counter-ledger, which decides whether the gate is usable at all.
    print("\n" + "-" * 100)
    print("COST — cases the ownership gate gets WRONG")
    wrong = [c for c in CASES if results[c.id]["ownership-derived"] != c.ground_truth]
    if not wrong:
        print("  none")
    for c in wrong:
        other = "both baselines correct" if all(
            results[c.id][n] == c.ground_truth for n in names if n != "ownership-derived"
        ) else "baselines also wrong"
        print(f"\n  {c.id}  ({other})")
        print(f"    {c.description}")
        print(f"    ownership says : {reasons[c.id]['ownership-derived']}")
        print(f"    ground truth   : {c.ground_truth.value} — {c.why}")

    print("\n" + "=" * 100)
    print(f"VERDICT: {len(novel)} discriminant case(s) not covered by prior art; "
          f"{len(wrong)} case(s) the ownership gate gets wrong.")
    print("=" * 100)
    return 0 if novel else 1


if __name__ == "__main__":
    raise SystemExit(main())
