# Lock-in data — a SEED, not a validation set

> Collected via LLM subagents (web-grounded where cited). These are **expert-style prior
> estimates and public-case reconstructions** to *seed* the knowledge base and *exercise the
> apparatus end-to-end* — **not measured ground truth.** Read [`RED_TEAM.md`](RED_TEAM.md)
> before drawing any conclusion: the experiment shows the FDK score is, on this data, ~97%
> switching_cost (tautological) with a 17% residual that is just the `alternatives` input —
> i.e. no independent construct demonstrated, and the real (predictive) test is not runnable
> here.

## Files

| File | What | Provenance |
|---|---|---|
| [`portability_cloud.json`](portability_cloud.json) | 31 cloud/infra services with switching_cost / portability / alternatives + rationale | LLM priors, 3 web-cited |
| [`portability_ai_saas.json`](portability_ai_saas.json) | 31 AI / data-platform / SaaS services, same schema | LLM priors, web-grounded |
| [`migration_cases.json`](migration_cases.json) | 16 documented public migration / vendor-exit cases with outcomes | web-verified; 2 with a $ figure |
| [`migration_cases.md`](migration_cases.md) | readable case table + bias notes | — |
| [`RED_TEAM.md`](RED_TEAM.md) | the methodology attack + the real experiment numbers + what real validation needs | — |

## Schemas

**portability_*.json** — `{ _provenance, schema, records: [ {name, category, switching_cost
[0-1], portability [0-1], alternatives (int), rationale, confidence, source} ] }`. Open
standards score high portability / low switching cost; proprietary managed services the
reverse.

**migration_cases.json** — `{ _provenance, schema, records: [ {case, org, from_vendor,
to_target, year, migration_cost_usd | null, duration_months | null, outcome, lock_in_incident
| null, est_lockin_score_hint, note, source, confidence} ] }`. The `est_lockin_score_hint` is
an LLM prior and **must never be used as an outcome** (circularity — see RED_TEAM A3).

## Run the experiment

```
python examples/lockin_experiment.py
```

Prints face validity, the discriminant (Stage 1) and residual (2b) analyses, and the
feasibility verdict on the ΔR² predictive test (Stage 2: not runnable, N≈2). Every number in
`RED_TEAM.md` comes from this script.

## The honest status this data establishes

It does **not** validate FDK and cannot. It establishes three things: (1) the pipeline runs
and is face-valid; (2) on this seed, FDK has not earned independence from switching cost
(burden now fully on FDK); (3) a real test requires a **sampling frame, one pre-registered
measured outcome, independently-rated features, established controls, and N ≈ 100+** — which
is fieldwork, not more LLM data.

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Engineering: Ali Pourrahim.*
