"""
lockin-scan — the production CLI for Enterprise Lock-in Intelligence.

Usage model is SonarQube/Snyk's: run it in CI against a *stack manifest*, get an
actionable lock-in report, and optionally **gate the build** when lock-in risk
crosses a threshold (`--fail-over`). It makes a known, expensive, usually-invisible
cost (vendor/cloud lock-in) visible at decision time. No new science is claimed.

    lockin-scan stack.json
    lockin-scan stack.json --format json
    lockin-scan stack.json --fail-over 0.6        # exit 1 if risk > 0.6 (CI gate)
    lockin-scan stack.json --kb my_ratings.json   # bring your own knowledge base

A manifest is `{"name": ..., "stack": [{"service": <name>, "weight": <0..1>}, ...]}`.
Each `service` is resolved by name against the portability knowledge base; a service
not in the base is reported as UNKNOWN and **not silently scored**. The bundled base
(`data/*.json`) is an LLM-estimated SEED — production users supply their own,
maintained ratings (see `data/RED_TEAM.md` for why that data asset is the real moat).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from fdk_research.lockin import Dependency, lockin_risk, report

_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_KB = [
    _REPO / "data" / "portability_cloud.json",
    _REPO / "data" / "portability_ai_saas.json",
]


def load_kb(paths: Iterable[Path]) -> dict[str, dict[str, Any]]:
    """Load one or more portability knowledge-base JSON files into a name→record map."""
    kb: dict[str, dict[str, Any]] = {}
    for path in paths:
        for rec in json.loads(Path(path).read_text(encoding="utf-8"))["records"]:
            kb[rec["name"]] = rec
    return kb


def resolve(
    stack: list[dict[str, Any]], kb: dict[str, dict[str, Any]]
) -> tuple[list[Dependency], list[str]]:
    """Map manifest stack entries to Dependencies via the knowledge base. Returns
    (resolved dependencies, names of services NOT found — never silently scored)."""
    deps: list[Dependency] = []
    unknown: list[str] = []
    for item in stack:
        name = item["service"]
        rec = kb.get(name)
        if rec is None:
            unknown.append(name)
            continue
        deps.append(Dependency(
            name=name,
            weight=float(item.get("weight", 1.0)),
            switching_cost=float(rec["switching_cost"]),
            portability=float(rec["portability"]),
            alternatives=int(rec["alternatives"]),
        ))
    return deps, unknown


def scan(manifest: dict[str, Any], kb: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Score a manifest. Returns a JSON-serialisable result incl. the text report."""
    deps, unknown = resolve(manifest.get("stack", []), kb)
    prof = lockin_risk(deps)
    return {
        "name": manifest.get("name", "stack"),
        "lockin_risk": prof.lockin_risk,
        "band": prof.band,
        "concentration": prof.concentration,
        "worst_dependency": prof.worst_dependency,
        "unknown_services": unknown,
        "report": report(deps),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="lockin-scan",
        description="Enterprise Lock-in Intelligence — score a stack manifest for exit cost.",
    )
    ap.add_argument("manifest", help="stack manifest JSON: {name, stack:[{service, weight}]}")
    ap.add_argument("--kb", action="append", type=Path,
                    help="portability knowledge-base JSON (repeatable; default: bundled seed)")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--fail-over", type=float, default=None, metavar="RISK",
                    help="exit 1 if lock-in risk exceeds RISK (use as a CI gate)")
    args = ap.parse_args(argv)

    kb = load_kb(args.kb or _DEFAULT_KB)
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    result = scan(manifest, kb)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(result["report"])
        if result["unknown_services"]:
            print("\nUNKNOWN (not in knowledge base, NOT scored): "
                  + ", ".join(result["unknown_services"]))

    if args.fail_over is not None and result["lockin_risk"] > args.fail_over:
        print(f"\nFAIL: lock-in risk {result['lockin_risk']:.2f} exceeds threshold "
              f"{args.fail_over:.2f}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
