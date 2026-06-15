# Program Status — the director's 10 phases vs. the repo's reality

> This document maps the scientific director's 10-phase program (and the core
> mandate) onto the **actual current state of this repository**, honestly. It is a
> status ledger, not a sales sheet: where a phase is half-built or its hardest part
> still ahead, it says so and names what is missing. Every "DONE" cites the
> concrete artifact (file path) that satisfies it; every PARTIAL/OPEN carries a
> one-line note on the gap.
>
> Companion to [`CORE_PRIMITIVE.md`](CORE_PRIMITIVE.md) (the locked primitive),
> [`THEOREMS.md`](THEOREMS.md) (what is proven, and how), and the root `README.md`
> (the public status). Where this document and the README disagree on a number, the
> repo is authoritative: a fresh `pytest --co` collects **299 tests** (the README's
> "272" is stale and lags reality).

**Status legend** (same convention as the other `spec/*.md`)
- **DONE** — a concrete, tested artifact in the repo fully satisfies the phase.
- **PARTIAL** — the spine exists and is tested, but a named, load-bearing piece is
  still missing or stylized.
- **OPEN** — named in the program; a defensible design may exist on paper, but no
  validated artifact does yet. The frontier.
- **NOT-STARTED** — no artifact, by deliberate sequencing (it is gated on an
  earlier phase).

**Grounding**: the theory is نظریه آزادی (*Theory of Freedom*), Mohammad Ali Jannat
Khah Doust (CC BY 4.0). The code of record is `src/fdk_kernel/` (deterministic gate)
and `src/fdk_research/` (experimental layer). The two attributions — theory and
engineering (Ali Pourrahim) — are kept separate, always.

---

## 0. The central question: *is the primitive locked?*

**Yes.** This is the mandate's pivot — *"DO NOT BUILD A DECISION ENGINE UNTIL YOU
HAVE BUILT A LEGITIMACY CALCULUS"* — and the project has met it. The primitive is
fixed in [`CORE_PRIMITIVE.md`](CORE_PRIMITIVE.md) as a **two-valued legitimacy
predicate, not a scalar to maximize**:

```
Legitimate(action) ⟺ ∀ b ∈ boundaries_crossed(action): ∃ valid_consent(owner(b), action)
   valid_consent ⟺ informed ∧ voluntary ∧ specific ∧ revocable ∧ competent ∧ ¬coerced ∧ ¬deceived
```

The candidate set the director named (FreedomDelta / JusticeScore / Legitimacy /
RightsPreservation) is resolved decisively: `Legitimacy` is the kernel primitive;
`FreedomDelta` (the Mahdavi compass) is demoted to a **research-layer optimization
over the already-legitimate set** (`CORE_PRIMITIVE.md` §4). The ordering
*Legitimacy → Optimization* is enforced as control flow, never reversible.

Two later results *strengthen* the lock by **subtraction** — they remove engines
rather than add them, which is the strongest evidence a primitive is real:

- [`CONFLICT_LOGIC.md`](CONFLICT_LOGIC.md) collapses *aggression* into the same
  predicate: aggression = "illegitimate under the gate," not a separate detector.
- [`FREE_WILL_PROPERTY_UNIFICATION.md`](FREE_WILL_PROPERTY_UNIFICATION.md) collapses
  *free will* into it too: a will is overridden iff its option set was built by
  crossing one of its owner's boundaries without consent. **No autonomy score, no
  coercion classifier, no free-will engine** — the property-rights test already *is*
  the free-will test (`tests/test_free_will_property.py` proves it on the unmodified
  gate).

So the 80%-of-risk discovery is, by the repo's own evidence, made and pinned. The
honest residue is a **scope** question, not a *what-is-the-primitive* question: does
the predicate range over *present* boundary crossings only, or over *foreseeable
future* dependency too (`CORE_PRIMITIVE.md` §6)? The kernel takes the present-only
reading by default and routes future-dependency to the research compass —
provisional engineering, flagged as a ruling for the theory's author, not a closed
result. **"Frozen" is not yet "frozen-for-Lean":** the model changed during
conflict-logic, operations, and welfare work, so the proof-grade freeze (Phase 7's
formal half) is close but not final (`THEOREMS.md` §Future).

---

## 1. Phase-by-phase status

| # | Director's phase | Status | Artifact(s) of record | Gap (for PARTIAL/OPEN/NOT-STARTED) |
|---|---|---|---|---|
| **1** | **Extract the theory core** — primitive-concept list; `ONTOLOGY.md` | **DONE** | [`ONTOLOGY.md`](ONTOLOGY.md) (12 entity types, 27 typed predicates, structural/semantic map), [`CONCEPT_DEFINITIONS.md`](CONCEPT_DEFINITIONS.md) (necessary/sufficient/counterexample for all 13 named primitives), [`AXIOM_REGISTRY.md`](AXIOM_REGISTRY.md) (A1–A7 verbatim → exact enforcement site), [`BOUNDARY_ONTOLOGY.md`](BOUNDARY_ONTOLOGY.md) | All director-named concepts (Person…Guidance) are covered. The "~20 pages of math from 800 pages" deliverable exists as the spec set, not a single monograph — substance present, form distributed. |
| **2** | **Extract the Primitive** — fix the ONE function before building | **DONE** | [`CORE_PRIMITIVE.md`](CORE_PRIMITIVE.md); reinforced by [`FREE_WILL_PROPERTY_UNIFICATION.md`](FREE_WILL_PROPERTY_UNIFICATION.md) and [`CONFLICT_LOGIC.md`](CONFLICT_LOGIC.md) | Primitive locked as the legitimacy predicate (see §0). Residual *scope* question (present vs. foreseeable boundaries, `CORE_PRIMITIVE.md` §6) is a theory ruling, not an open primitive choice. |
| **3** | **Build the formal logic** — `Legitimate(action)`, Boundary, Crossing, Ownership, Consent, Delegation, Sovereignty | **DONE** | `src/fdk_kernel/kernel.py` (`check_legitimacy`: per-axiom evaluators A2–A7 + categorical forbidden set + defensive asymmetry), `src/fdk_kernel/model.py` (`Entity`, `Resource`/`BoundaryKind`/`Op`, 7-condition operation-typed `Consent`, `OwnershipGraph`, `CandidateAction`); spec'd in [`FORMAL_SPEC.md`](FORMAL_SPEC.md) + the operation lattice in `BOUNDARY_ONTOLOGY.md` | A "Freedom Logic" exists and is executable. Honest residue *inside* the logic: A5 (scope ⊆ owner scope) has no first-class scope object — folded into the A7 path (`AXIOM_REGISTRY.md` A5); conflict-*resolution* between two valid claims is OPEN (`ONTOLOGY.md` §2.12). |
| **4** | **Prove the inconsistencies** — try to DESTROY the theory (slavery, taxation, quarantine, defensive war, rescue, autonomous AI) | **PARTIAL** | `examples/historical_scenarios.py` (8 levels incl. L8 "hardest": ticking-bomb torture, organ-harvest, tyrannicide, rogue-AI defense; 47/47 expectations match), `tests/test_redteam_dialectical.py`, `tests/test_redteam_conflict.py`, `tests/test_redteam.py`, `tests/test_capstone_adversarial.py`, `tests/test_book_gaps.py`, `tests/test_gaps_v2.py` | The hard cases the director named are *all run* and the theory survives them as a structural gate. But this is adversarial *testing*, not exhaustive *destruction*: the surviving open edges are documented, not closed — defensive-force first-mover adjudication (`CONFLICT_LOGIC.md` §4, no temporal data), necessity/rescue + quarantine remain DENY (no emergency exception), and `coerced`/`deceived` are attested booleans, not detected. |
| **5** | **FreedomBench** — 10000+ historical + 10000+ AI-governance cases (*the project's most important asset*) | **PARTIAL** | Spec: [`FREEDOMBENCH.md`](FREEDOMBENCH.md) (format, 5 suites, validator V1–V9, split discipline, scale plan 100→1k). Harness: `src/fdk_research/benchmark.py` (`Scenario`, `BenchmarkReport`, `run_benchmark`, `generate_suite`). Cases: `examples/historical_scenarios.py` (47 curated). | **Scale is the gap, and it is large.** ~47 curated cases exist against the director's target of 10k+10k — roughly three orders of magnitude short. The format/validator/split design is done; per-candidate `expected_axioms`, curated 100→500→1k growth, and the AI-governance suite at scale are not built. FreedomBench is the named most-important asset and is the least-complete by volume. |
| **6** | **Compare with rivals** — Rawls / Utilitarian / Constitutional / RLHF kernels on FreedomBench ("where science begins") | **PARTIAL** | `src/fdk_research/rivals.py` (`RivalKernel` protocol + `Utilitarian`, `Rawlsian`, `Deontological`, `compare`, `divergences`), `examples/rival_comparison.py` (divergence table), `tests/test_rivals.py` | The *seam* is real and the divergence structure is shown (welfare kernel ALLOWs the sacrifice atrocities FDK DENYs). But the rivals are **stylized, directional caricatures** on **author-built** scenarios. The director's `ConstitutionalAIKernel` and `RLHFKernel` are **not** implemented as real baselines (RLHF is a documented stub slot in `FREEDOMBENCH.md` §5.4); no head-to-head against a deployed LLM exists. This is "science set up," not "science concluded." |
| **7** | **Provability** — Lean / TLA+ / Coq / model-checking; theorems (No Legitimate Slavery, etc.) | **PARTIAL** | [`THEOREMS.md`](THEOREMS.md) (T1–T9: No Legitimate Slavery, no acting on persons w/o consent, machine-cannot-gain-sovereignty, consent-revocation safety, delegation soundness, welfare-independence, defensive asymmetry well-founded, necessity grants no exception, kernel/research boundary), each bound to a Hypothesis property test: `tests/test_theorems.py`, `tests/test_boundary.py`, etc. | The director's named theorems exist and are **machine-checked — but as executable property-based proofs at 100% coverage, not Lean/TLA+/Coq.** The formal-tool layer is `FUTURE` (`THEOREMS.md` §Future): it needs (a) a frozen primitive — close, not final — and (b) a Lean port / TLC run that does not yet exist. No `.lean`/`.tla` artifact is in the repo. |
| **8** | **Build the FDK Kernel** — WorldState + CandidateActions → ALLOW/DENY/DEFER; deterministic, no LLM/probability/learning | **DONE** | `src/fdk_kernel/kernel.py` (`check_legitimacy`, `screen_legitimacy`), `src/fdk_kernel/model.py` (`Decision`), `src/fdk_kernel/guidance.py` (hard-defer trigger); `src/fdk_research/decision.py` (`decide` orchestrator). `mypy --strict` + `ruff` clean; **299 tests** at 100% statement+branch coverage. | Fully deterministic ALLOW/DENY/DEFER kernel exists and is the most-complete part of the repo. (Note the director ordered this as Phase 8, *after* the calculus — the repo honors that ordering: the gate is pure-functional, reads no free-text, and `tests/test_boundary.py` mechanically forbids it importing the research layer.) |
| **9** | **Freedom Optimizer** — FreedomDelta over the already-Legitimate set; Legitimacy → Optimization, never reversed | **DONE** | `src/fdk_research/compass.py` (`mahdavi_score`), `src/fdk_research/necessity.py` (`least_harmful_among_permissible` — book's necessity rule, no gate exception), `src/fdk_research/decision.py` (compass runs *inside* the `if permissible` branch); `tests/test_necessity.py`, `tests/test_theorems.py::T6/T8` | The optimizer exists and the ordering is enforced structurally (T6 welfare-independence, T8 necessity-grants-no-exception prove the gate can't be bought). Honest residue: the compass *inputs* (`coercion_delta`, `dependency`, `ownership_ambiguity`) are PARTIAL/OPEN measures (`COMPASS_MEASUREMENT.md`) — the *ordering* is sound, the *calibration* is not, and is correctly labeled advisory. |
| **10** | **Agent Civilization** — millions of scenarios; FDK World vs Rawls vs Utilitarian: stability, freedom, power concentration | **NOT-STARTED** | Seed only: `src/fdk_research/simulator.py` (`FreedomSim` — single-trajectory stepper, asserts the safety invariant), `src/fdk_research/federation.py` (multi-owner governance); `tests/test_simulator.py`, `tests/test_federation.py` | The multi-step simulator stub exists and `FREEDOMBENCH.md` §5.5 specifies the trajectory metrics (voluntary-order index, rights-violation/coercion stock). But there is **no agent-civilization run** — no millions-of-scenarios comparison of FDK-World vs Rawls-World vs Utilitarian-World. This phase is gated on Phases 5 and 6 reaching scale and is correctly deferred. |

---

## 2. The honest frontier (what is genuinely still ahead)

Five items carry essentially all the remaining program risk that the locked
primitive did *not* retire. None is blocked on "what is the primitive"; each is
engineering-at-scale or a toolchain port:

1. **Lean/TLA+ proofs (Phase 7's formal half).** Gated on two things: the
   *proof-grade freeze* of the primitive (boundaries + conflict + welfare stopped
   moving) and an actual Lean port / TLC model. The executable theorems (T1–T9) are
   the precondition — they pin exactly what the formal proofs must establish — so
   the port is a re-expression of verified facts, not a fresh discovery
   (`THEOREMS.md` §Future). No `.lean`/`.tla` file exists yet.

2. **FreedomBench at scale (Phase 5).** ~47 curated cases → the director's
   10k historical + 10k AI-governance. This is the named most-important asset and
   the largest single gap by volume. Needs the curated 100→500→1k growth, real
   `expected_axioms` on every candidate, and the AI-governance suite built out.

3. **Real rival baselines (Phase 6).** The current rivals are stylized
   caricatures on author-built scenarios. The director's `ConstitutionalAIKernel`
   and `RLHFKernel` need to be *actual* baselines (real LLM / RLHF behavior), run
   on a held-out FreedomBench split, before the superiority claim is science rather
   than structure. The honest scope notes in `README.md` and `FREEDOMBENCH.md` §1.2
   already say the FDK's own 0% violation rate proves implementation soundness, not
   superiority — superiority is *entirely* in this comparison.

4. **Agent-civilization simulation (Phase 10).** No millions-of-scenarios
   FDK-vs-Rawls-vs-Utilitarian world run exists; only the `FreedomSim` single-
   trajectory seed and the metric spec. Gated on 2 and 3.

5. **Frontier scope rulings + Rust port (cross-cutting).** Two theory-author
   rulings remain load-bearing: the present-vs-foreseeable boundary scope
   (`CORE_PRIMITIVE.md` §6) and first-mover initiation under the Observer Problem
   (`CONFLICT_LOGIC.md` §4). On the engineering side, A5 deserves a first-class
   scope object (`AXIOM_REGISTRY.md` §5), and the frozen minimal kernel should be
   ported to Rust for TCB parity with AuthGate (`README.md` §Next). These are
   refinements of a locked primitive, not searches for one.

---

*Program-status ledger, Freedom Decision Kernel. Theory: نظریه آزادی (Theory of
Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0). Engineering: Ali Pourrahim.
The two are kept separate, always.*
