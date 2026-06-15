# FDK — TODO (current → target)

> Grounded in `New Text Document (2.1).md` (the strategic mandate) and the actual
> code in `src/fdk/`. This is **not** a "build 400 new things" list — the project
> is over-built, not under-built. The work is *consolidation and separation*.
>
> Status: `[x]` done · `[~]` partial · `[ ]` not started · `[!]` blocked
>
> Repos: AuthGate = github.com/Aliipou/authgate-kernel ·
> FDK = github.com/Aliipou/freedom-decision-kernel
>
> Pipeline: `Goal → Planner(research) → candidates → FDK kernel(legitimacy) → AuthGate(authority) → IO`

---

## Current state (2026-06-15)

- 2,315 LOC, 17 modules, ~218 tests — all in one flat package `src/fdk/`.
- `kernel.py` already has the correct two-stage shape: **legitimacy hard gate →
  Mahdavi compass**. The legitimacy gate is deterministic and rule-based. Good.
- **Problem (the only one that matters right now):** kernel and research code are
  fused. `planner`, `simulator`, `justice`, `federation`, `conflict`, `benchmark`,
  `compass_measure`, `ontology`, `guidance_engine` live beside the kernel and are
  exported flatly from `__init__.py`. The golden rule (nothing in the kernel
  unless deterministic + fully testable + non-semantic) is currently violated by
  the package layout, even where the *logic* is sound.

Classification of existing modules:

| Module | LOC | Belongs in |
|---|---|---|
| `model.py` | 211 | **kernel** (trim to light WorldState) |
| `kernel.py` (legitimacy gate) | 231 | **kernel** |
| `errors.py` | 59 | **kernel** |
| `audit.py` | 42 | **kernel** (trace only) |
| `authgate_bridge.py` | 118 | **kernel** (the downstream contract) |
| `kernel.py` (`mahdavi_score`) | — | **research** (it is optimization, not legitimacy) |
| `compass_measure.py` | 74 | research |
| `justice.py` | 182 | research |
| `planner.py` | 123 | research |
| `simulator.py` | 85 | research |
| `benchmark.py` | 234 | research |
| `federation.py` | 99 | research |
| `conflict.py` | 101 | research |
| `ontology.py` | 137 | research |
| `guidance*.py` | 343 | split: hard-defer trigger = kernel; resolution logic = research |

---

## P0 — Establish the epistemic boundary  ← do this first, nothing else matters until it's done

- [ ] Create two import-isolated packages: `src/fdk_kernel/` and `src/fdk_research/`.
- [ ] Move kernel-grade modules into `fdk_kernel/`: `model`, `kernel` (legitimacy
      gate only), `errors`, `audit`, `authgate_bridge`, and the hard-defer trigger.
- [ ] Move research modules into `fdk_research/`: `planner`, `simulator`, `justice`,
      `benchmark`, `compass_measure`, `federation`, `conflict`, `ontology`,
      guidance *resolution*.
- [ ] Pull `mahdavi_score` and the `_W_*` weights OUT of `kernel.py` into
      `fdk_research/compass.py`. The kernel returns the *legitimate set*; ranking is
      a research concern layered on top.
- [ ] Split `__init__.py`: kernel exports only the legitimacy surface; research
      exports separately. No flat re-export of everything.
- [ ] **Enforcement test** (`tests/test_boundary.py`): assert `fdk_kernel` imports
      nothing from `fdk_research`. This test *is* the golden rule, mechanized.

## P1 — Lock the single core primitive

- [ ] Write `spec/CORE_PRIMITIVE.md` fixing the kernel primitive as a **legitimacy
      predicate**, not a scalar:
      `Legitimate(action) ⟺ ∀ boundary b crossed: ∃ valid_consent(owner(b), action)`
      — with `valid_consent ⟺ informed ∧ voluntary ∧ specific ∧ revocable ∧ competent`.
- [ ] Record that `FreedomDelta` is the **research-layer** primitive (optimization
      over the already-legitimate set), so `Legitimacy → Optimization` ordering holds.
- [ ] Refactor `check_legitimacy` so the structure is explicitly *boundary
      enumeration → consent coverage*, instead of scattered per-axiom appends. Same
      behavior, primitive made visible. (Keep functions ≤30 LOC per CLAUDE.md.)

## P2 — Minimal-kernel hardening

- [ ] `explanation`: trace only — list violated axioms + satisfied axioms +
      ownership/consent chain. No scoring, no metrics in the kernel trace.
- [ ] Determinism test: same `(candidates, graph)` → byte-identical `Decision`,
      run 1000× and across process restarts.
- [ ] "No-semantics" test: kernel decision must not depend on any free-text field
      (names, descriptions) — only on structural facts.
- [ ] Confirm hard-defer path: empty legitimate set → `needs_guidance=True`
      (already implemented; add an explicit test that it never silently denies).

## P3 — Research layer (free zone — contradictory ideas allowed here)

- [ ] FreedomBench: spec + format + validator; consent / ownership / emergency /
      AI-governance / multi-agent suites; scale 100 → 1k scenarios.
- [ ] Rival kernels (constitutional, utilitarian, deontic, RLHF-style) behind one
      common interface so they run against the same bench.
- [ ] World simulator + agent-based runs to test the central empirical claim:
      *does reducing rights-violation actually move the world toward voluntary order?*
- [ ] Justice / compass metric experiments (this is where `mahdavi_score` lives now).

## P4 — Formal + scientific validation

- [ ] Lean4: decision-consistency + rights/consent-preservation theorems on the
      *kernel* (small surface = provable; this is why P0 matters).
- [ ] TLA+: decision state machine + safety invariants; actually run TLC.
- [ ] Comparative evaluation: FDK vs each rival on FreedomBench, with a statistical
      + reproducibility framework. Report false-permit / false-deny / adversarial.

---

## Explicitly deferred (do NOT build yet — anti-scope-explosion)

SDKs (Rust/Go/Java/TS), gRPC/OpenAPI, policy/scenario/governance languages,
federation protocol, registries, distributed governance. These are real but
premature until the kernel primitive is locked and FreedomBench shows
reproducible superiority. Revisit only after P3 produces a result worth shipping.
