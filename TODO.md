# FDK — the cohesive program (current → paradigm)

> One consolidated, consistent roadmap. It folds together the director's analyses
> (the 10-phase program, the 12-level red-team ladder in `continue.md`, and the
> repeated strategic notes on primitive-freeze / ownership / coercion / benchmark /
> rivals / formalization / civilization / external review) into a single coherent
> plan with honest status. It supersedes the old phase-by-phase TODO; the
> phase-by-phase mapping still lives in [`spec/PROGRAM_STATUS.md`](spec/PROGRAM_STATUS.md).
>
> Status: `[x]` done · `[~]` partial (spine shipped, named gap remains) ·
> `[ ]` not started · `[!]` blocked (toolchain / external).
>
> Repos: FDK = github.com/Aliipou/freedom-decision-kernel ·
> AuthGate = github.com/Aliipou/authgate-kernel

---

## 0. The locked thesis (do not reopen without cause)

**FDK is a Legitimacy Kernel, NOT an Optimization Kernel.** The whole architecture
follows from this ordering and never reverses it:

```
Universe of Actions
   ↓  Legitimacy Filter  — FDK Kernel (deterministic): ALLOW / DENY / DEFER
Legitimate Action Set
   ↓  Optimization       — FreedomDelta / Mahdavi compass (research layer only)
Chosen Action
   ↓  Authority          — AuthGate (capability verification, downstream)
Execution
```

Primitive (locked, `spec/CORE_PRIMITIVE.md`):

```
Legitimate(action) ⟺ ∀ boundary b crossed: ∃ valid_consent(owner(b), action)
   valid_consent ⟺ informed ∧ voluntary ∧ specific ∧ revocable ∧ competent ∧ ¬coerced ∧ ¬deceived
```

The kernel returns **no score** — only ALLOW/DENY/DEFER. `FreedomDelta` is demoted
to research. Two results *strengthen the lock by subtraction* (they delete engines,
not add them): aggression collapses into the predicate (`CONFLICT_LOGIC.md`), and
free-will collapses into it too (`FREE_WILL_PROPERTY_UNIFICATION.md`).

**The honest scorecard** (the director's, kept verbatim so we never flatter
ourselves): Vision 85 · Architecture 70 · Core-Concepts 60 · Implementation 35 ·
Formalization 20 · Benchmarking 10 · Scientific-Validation 5. **Engineering FDK
~30/100; scientific proof ~15/100; paradigm ~5/100.** The numbers are low *because
the project went at the hardest part* — turning Legitimacy/Consent/Ownership/
Coercion/Sovereignty into an executable calculus — not because it is weak.

---

## A. Primitive freeze / completion  — `[~]` THE highest-risk item

Prove that *every* Theory-of-Freedom problem reduces to Boundary-Crossing + Valid
Consent — before any further building rests on it. The danger is discovering in six
months that Dependency / Power-Concentration / Capture *had* to be in the core.

- [x] Stress the primitive against the five pressures (`examples/continue_ladder.py`
      PRIMITIVE-COMPLETION + `tests/test_continue_ladder.py`): **power** (cartel
      pricing), **dependency** (network-effect lock-in vs. exit-removal),
      **manipulation** (deception vs. mere persuasion), **contract** (hidden clause =
      void consent), **ownership frontier** (model trained on a person's data).
      66/66 ladder cases match the real gate.
- [x] Harden the ownership half of the primitive: **A5 is now a first-class scope
      object** (`OwnershipGraph.machine_scope` + `_eval_a5_scope`), so "scope ⊆ owner
      scope" is checkable in the abstract (`tests/test_a5_scope.py`).
- [ ] **Theory-author ruling — present vs. foreseeable scope** (`CORE_PRIMITIVE.md`
      §6): does the predicate range only over *present* boundary crossings, or also
      *foreseeable future dependency / concentration*? The honest open question the
      ladder surfaces (cartel pricing currently ALLOWed). This is the freeze blocker.
- [ ] **Theory-author ruling — first-mover initiation** under the Observer Problem
      (`CONFLICT_LOGIC.md` §4): the model has no temporal-initiation field, so two
      independent raw coercions cannot be adjudicated.
- **Exit criterion:** the kernel signature stops changing → "frozen-for-Lean."

## B. FreedomBench at scale  — `[~]` the ImageNet moment; largest gap by volume

If the primitive collapses anywhere, it collapses here.

- [~] Curated taxonomy shipped: `examples/historical_scenarios.py` (14 levels, 47)
      + `examples/continue_ladder.py` (12 levels + primitive stress, 66). Procedural
      harness: `src/fdk_research/benchmark.py` (`generate_suite`).
- [ ] **Scale: 100 → 500 → 1k → 10k+ historical + 10k+ AI-governance**, each
      candidate carrying `expected_axioms`, 0% rights-violation by construction.
      *(In flight this session — Phase-5 scale agent.)*
- **Exit criterion:** thousands of real cases (all of human history + AGI/economy/
      governance/war) run green, with a held-out split reserved for §C.

## C. Rival evaluation  — `[~]` "where the science begins"

- [x] Rival seam + stylized kernels: `src/fdk_research/rivals.py` (FDK, Utilitarian,
      Rawlsian, Deontological, ConstitutionalAI, RLHF) + quantified comparison
      (`src/fdk_research/evaluation.py`): over a 10k suite, Utilitarian false-permits
      ~100%, Deontological ~60%, FDK 0% by construction. Divergence is *structural*.
- [ ] **Real baselines:** ConstitutionalAI and RLHF as *actual* models (need a live
      LLM / reward model), run on the held-out FreedomBench split. Until then the
      superiority claim is structure, not science.
- **Exit criterion:** a reproducible head-to-head where FDK's rights-violation rate
      is provably lower than deployed alignment systems on cases neither side saw.

## D. Formalization  — `[!]` blocked on toolchain + the §A freeze

- [x] Executable theorems T1–T9 (`spec/THEOREMS.md`, Hypothesis property tests at
      100% coverage): No-Legitimate-Slavery, no-acting-on-persons-without-consent,
      machine-cannot-gain-sovereignty, consent-revocation safety, delegation
      soundness, welfare-independence, defensive-asymmetry well-founded,
      necessity-grants-no-exception, kernel/research boundary.
- [x] TLA+ spec drafted (`spec/fdk.tla`).
- [!] **Lean 4 proofs** of T1–T5 over a formal kernel model — no Lean/elan in this
      environment, and gated on the §A freeze. No `.lean` artifact yet.
- [!] **Run TLC** on `fdk.tla` — no Java in this environment.
- **Exit criterion:** TLA+ → Lean → (eventually Rust) shown equivalent, seL4-style.

## E. Real-world ownership ontology  — `[ ]` the hardest part of the whole project

The README's own caveat: *the legitimacy gate is only as good as the ownership
graph handed in.* The theory answers these; an **engineering-grade ontology** does
not exist yet.

- [ ] Who owns: **data, identity, trained models, model weights, an agent, the GPU,
      the generated output, AGI-produced knowledge, river water, collective data?**
- [x] First step taken: operation lattice (`Op`) + typed `Resource(kind, subject,
      quantity)` + A5 first-class scope make "could read but sold it" and
      "scope ⊆ owner" expressible.
- **Exit criterion:** a typed ownership ontology that resolves the frontier cases
      above deterministically (or defers them explicitly).

## F. Coercion / consent calculus completeness  — `[~]` "dictators say people agreed"

The structural answer exists (a will is overridden iff its option set was built by
crossing an owner's boundary without consent); the *detection* does not.

- [x] Structural coercion via the gate; majority-as-consent, lock-in-as-consent,
      and manufactured-dependency all denied (ladder L4/L5 + red-team laundering).
- [ ] **The attested → detected gap:** `coerced` / `deceived` are caller-declared
      booleans, not detected. Poor-worker-signs / sanctions / dark-patterns /
      persuasion-vs-coercion remain on the trust boundary (documented OPEN).
- **Exit criterion:** a validated operational definition of coercion/deception that
      does not rely on the proposer's honest self-report.

## G. Sovereignty calculus (AI alignment)  — `[x]` structurally complete

- [x] Shutdown-refusal, manipulation, info-hiding, self-replication, compute-grab,
      coalition-dominion, recursive-self-improvement all categorically denied
      (`continue_ladder.py` L6/L8, kernel forbidden-set). Honest LIMIT: wireheading
      that crosses no human boundary is an AuthGate/capability concern, not a
      legitimacy one — documented, pinned as a test.

## H. Multi-agent civilization layer  — `[~]` gated on B + C reaching scale

- [x] Seed shipped: `src/fdk_research/civilization.py` + `examples/civilization_run.py`
      — FDK-World vs Rawls vs Utilitarian vs Deontological over a seeded action
      stream: FDK-World holds rights-violation stock at 0 with the lowest power
      concentration; Utilitarian admits everything and accumulates both.
- [ ] **Scale: 1000+ agents** with economy, contracts, alliances, war, migration,
      and AI-states; measure stability, freedom produced, power concentration over
      long horizons. Gated on §B (scale) + §C (real rivals).

## I. External review  — `[ ]` exits self-evaluation

- [ ] Independent critique by a **legal philosopher, an economist, an AI-safety
      researcher, and a formal-methods reviewer**, plus independent replication.
- [x] Internal hardening done: 42-attack grand red-team (`tests/test_redteam_grand.py`,
      `spec/REDTEAM_REPORT.md`), 0 structural breaches; dialectical/conflict/free-will
      red-teams; 100% coverage; `mypy --strict` + `ruff` clean.
- **Exit criterion:** survives hostile external review without the core caving.

## J. Endgame — Legitimacy Infrastructure  — `[ ]` only if A–I succeed

- [ ] Become to *legitimacy* what TLS/OAuth/POSIX are to their domains — a reference
      standard wired beneath agents / institutions / DAOs / robotics / AGI. Premature
      to name until A–I hold. Today the defensible claim is **"a Formal Legitimacy
      Calculus with a working executable prototype,"** not "a paradigm."

---

## Explicitly deferred (anti-scope-explosion)

Rust port of the *frozen* kernel (gated on §A); SDKs / gRPC / OpenAPI; policy &
governance DSLs; distributed federation protocol; on-chain registries. The kernel
stays deterministic, fully testable, non-semantic; if a feature can live in
`fdk_research/` it does not belong in `fdk_kernel/` (`tests/test_boundary.py`
enforces this mechanically).

---

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Engineering: Ali Pourrahim. The two attributions are kept separate, always.*
