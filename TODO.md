# FDK — TODO (current → target)

> Grounded in `New Text Document (2.1).md` (the strategic mandate), the director's
> 10-phase program (mapped honestly in [`spec/PROGRAM_STATUS.md`](spec/PROGRAM_STATUS.md)),
> and the actual code in `src/fdk_kernel/` + `src/fdk_research/`. This is **not** a
> "build 400 new things" list — the project is over-built, not under-built. The
> high-value moves remaining *remove* a degree of freedom or *scale* an existing
> asset; almost none add a new kernel mechanism.
>
> Status: `[x]` done · `[~]` partial · `[ ]` not started · `[!]` blocked
>
> Repos: AuthGate = github.com/Aliipou/authgate-kernel ·
> FDK = github.com/Aliipou/freedom-decision-kernel
>
> Pipeline: `Goal → Planner(research) → candidates → FDK kernel(legitimacy) → AuthGate(authority) → IO`

---

## Current state (post-split)

- The epistemic split **shipped**. The flat `src/fdk/` package is gone; code now
  lives in two import-isolated packages: **`src/fdk_kernel/`** (deterministic,
  non-semantic gate — `model`, `kernel`, `errors`, `audit`, `guidance` hard-defer,
  `authgate_bridge`) and **`src/fdk_research/`** (optimization, simulation, rivals,
  benchmark, conflict, federation, ontology, necessity, guidance-resolution).
- `kernel.py` has the correct two-stage shape — **legitimacy hard gate → Mahdavi
  compass** — and the compass (`mahdavi_score`, the `_W_*` weights) now lives in
  `fdk_research/compass.py`, *not* in the kernel. The gate returns the legitimate
  set; ranking is layered on top in `fdk_research/decision.py`.
- The golden rule is **mechanically enforced**: `tests/test_boundary.py` (static AST
  walk + dynamic import check) fails if `fdk_kernel` imports anything from
  `fdk_research`. This is the epistemic boundary as a test, not a convention.
- **~299 tests** collected (`pytest --co`), 100% statement+branch coverage,
  `mypy --strict` + `ruff` clean, CI across Python 3.11–3.13. FreedomBench 47/47.
  *(The README's "272" is stale — the real number is higher; trust `pytest --co`.)*
- The primitive is **locked** ([`spec/CORE_PRIMITIVE.md`](spec/CORE_PRIMITIVE.md)):
  a two-valued legitimacy predicate, with `FreedomDelta` demoted to the research
  layer. Free-will and aggression were *collapsed into* it (subtractive wins), not
  added beside it.

**Director-phase shorthand** (full table in `spec/PROGRAM_STATUS.md`): Phases
**1, 2, 3, 8, 9 DONE**; Phases **4, 5, 6, 7 PARTIAL**; Phase **10 NOT-STARTED**.

---

## P0 — Establish the epistemic boundary  ✅ DONE

- [x] Create two import-isolated packages: `src/fdk_kernel/` and `src/fdk_research/`.
- [x] Move kernel-grade modules into `fdk_kernel/`: `model`, `kernel` (legitimacy
      gate only), `errors`, `audit`, `authgate_bridge`, and the hard-defer trigger
      (`guidance.py`).
- [x] Move research modules into `fdk_research/`: `planner`, `simulator`, `justice`,
      `benchmark`, `compass_measure`, `federation`, `conflict`, `ontology`,
      guidance *resolution* (`guidance_resolution.py`, `guidance_engine.py`).
- [x] Pull `mahdavi_score` and the `_W_*` weights OUT of `kernel.py` into
      `fdk_research/compass.py`. The kernel returns the legitimate set; ranking is a
      research concern layered on top (`fdk_research/decision.py`).
- [x] Split `__init__.py`: kernel exports only the legitimacy surface; research
      exports separately. No flat re-export of everything.
- [x] **Enforcement test** (`tests/test_boundary.py`): assert `fdk_kernel` imports
      nothing from `fdk_research`. This test *is* the golden rule, mechanized (T9).

## P1 — Lock the single core primitive  ✅ DONE

- [x] Write `spec/CORE_PRIMITIVE.md` fixing the kernel primitive as a **legitimacy
      predicate**, not a scalar:
      `Legitimate(action) ⟺ ∀ boundary b crossed: ∃ valid_consent(owner(b), action)`
      — with `valid_consent ⟺ informed ∧ voluntary ∧ specific ∧ revocable ∧ competent`.
- [x] Record that `FreedomDelta` is the **research-layer** primitive (optimization
      over the already-legitimate set), so `Legitimacy → Optimization` ordering holds.
- [x] Make `check_legitimacy`'s structure boundary-enumeration → consent-coverage
      (per-axiom evaluators A2–A7 + categorical forbidden set), primitive made visible.
- [x] **Bonus, subtractive:** collapse aggression (`spec/CONFLICT_LOGIC.md`) and
      free-will (`spec/FREE_WILL_PROPERTY_UNIFICATION.md`) *into* the predicate —
      proving no separate engine is needed (`tests/test_free_will_property.py`).

## P2 — Minimal-kernel hardening  ✅ DONE

- [x] `explanation`: trace only — violated + satisfied axioms + ownership/consent
      chain, no scoring in the kernel trace (`spec/EXPLANATION_TRACE.md`, `audit.py`).
- [x] Determinism + "no-semantics" tests: kernel decision depends only on structural
      facts, not free-text; same world → same `Decision` (`tests/test_kernel.py`,
      `tests/test_theorems.py::T6` welfare-independence).
- [x] Confirm hard-defer path: empty legitimate set → `needs_guidance=True`, never a
      silent deny (`guidance.py`, `tests/test_guidance.py`).

---

## P3 — Research layer  — PARTIAL (the spine shipped; scale is the gap)

- [~] FreedomBench (**Phase 5**): spec + format + validator + suites shipped
      ([`spec/FREEDOMBENCH.md`](spec/FREEDOMBENCH.md), `fdk_research/benchmark.py`,
      `examples/historical_scenarios.py` — 8 levels, 47 curated cases).
  - [ ] **Scale to the director's target: 10k+ historical + 10k+ AI-governance.**
        Currently ~47 curated. Needs curated 100→500→1k growth, per-candidate
        `expected_axioms`, and the AI-governance suite built out. *Largest gap by
        volume; this is the named most-important asset.*
- [~] Rival kernels (**Phase 6**): `RivalKernel` protocol + stylized Utilitarian /
      Rawlsian / Deontological + `compare`/`divergences` shipped
      (`fdk_research/rivals.py`, `examples/rival_comparison.py`).
  - [ ] **Real baselines:** `ConstitutionalAIKernel` and `RLHFKernel` as *actual*
        models (RLHF is a documented stub today), run on a held-out FreedomBench
        split. Until then, the comparison shows divergence *structure*, not a
        validated head-to-head.
- [~] World simulator (**Phase 10 seed**): `FreedomSim` single-trajectory stepper +
      safety-invariant assertion shipped (`fdk_research/simulator.py`).
  - [ ] **Agent-civilization run:** millions of scenarios, FDK-World vs Rawls-World
        vs Utilitarian-World — stability, freedom produced, power concentration.
        Gated on FreedomBench scale + real rivals.
- [x] Justice / compass metric layer exists (`fdk_research/compass.py`,
      `compass_measure.py`, `justice.py`) — advisory, uncalibrated, correctly labeled.

## P4 — Formal + scientific validation  — PARTIAL (executable proofs done; tool-grade ahead)

- [x] Executable safety theorems (**Phase 7, this-env form**): T1–T9 in
      [`spec/THEOREMS.md`](spec/THEOREMS.md), each bound to a Hypothesis property test
      (No Legitimate Slavery, machine-cannot-gain-sovereignty, consent-revocation
      safety, delegation soundness, welfare-independence, defensive asymmetry,
      necessity-no-exception, kernel/research boundary). CI-gated at 100% coverage.
- [ ] **Lean 4** proofs of T1–T5 over a formal kernel model. Blocked on freezing the
      primitive (close, not final — the model moved during conflict-logic /
      operations / welfare) + an actual Lean port. No `.lean` artifact yet.
- [ ] **TLA+** decision state machine + safety invariants; actually run TLC. No
      `.tla` artifact yet.
- [ ] Comparative evaluation with a real statistical + reproducibility framework
      (false-permit / false-deny / adversarial), once real rivals (P3) exist.

## P5 — Frozen-kernel refinements  — open, gated on the freeze

- [ ] **A5 as a first-class scope object.** Today scope ⊆ owner scope is folded into
      the A7 per-resource path; there is no standalone `MachineScope` set, so A5
      can't be checked in the abstract (`spec/AXIOM_REGISTRY.md` §5).
- [ ] **Rust port** of the frozen minimal kernel, for TCB parity with AuthGate's
      verified core (`README.md` §Next). Gated on the proof-grade freeze.
- [ ] **Theory-author rulings** (not engineering — log + request): the
      present-vs-foreseeable boundary scope (`CORE_PRIMITIVE.md` §6) and first-mover
      initiation under the Observer Problem (`CONFLICT_LOGIC.md` §4). Both are
      refinements of a locked primitive, not searches for one.

---

## Explicitly deferred (do NOT build yet — anti-scope-explosion)

SDKs (Rust/Go/Java/TS — except the single Rust port of the *frozen* kernel above),
gRPC/OpenAPI, policy/scenario/governance languages, distributed federation protocol,
on-chain registries, distributed governance. These are real but premature until the
primitive is *proof-grade frozen* and FreedomBench shows reproducible superiority
against **real** rivals on a held-out split. Revisit only after P3/P4 produce a
result worth shipping. The kernel stays deterministic, fully testable, and
non-semantic; if a proposed feature can live in `fdk_research/`, it does not belong
in `fdk_kernel/` (`tests/test_boundary.py` enforces this).
