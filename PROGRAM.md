# Freedom AI Decision Kernel — Research & Engineering Program

> The hard problem is no longer Rust or Lean. It is turning a philosophical book
> into a **computable decision theory**: defining justice, coercion, deception,
> consent, guidance, and the desired order precisely enough for a machine to
> reason over them. This document organizes that work.

## The honest split

- **Engineering maturity: high.** AuthGate (verified Rust TCB) + this FDK
  (legitimacy gate, compass, justice, guidance, AuthGate bridge; hardened, typed,
  tested) cover the *structural* axioms A1–A7, consent validity, the forbidden
  set, and the permissibility conjunction. These are real.
- **Theoretical maturity: low.** The **semantic leaf-predicates** (`coerced?`,
  `deceived?`) and the **Mahdavi-compass measures** (`CoercionScore`,
  `ExitOptions`, `DependencyIndex`, `VoluntaryOrderIncrease`) are named in the
  theory but **not yet measurable**. Conflict resolution between competing rights
  has **no formula yet**. The superiority thesis vs RLHF/Constitutional-AI is
  **unproven**.

"1000 elites" is not headcount — it is the set of **disciplines** this needs.
Parallel labor cannot fix an incoherent definition; coherence comes first, then
parallelism. The tracks below are how a real team would be organized.

## Discipline tracks (the "team")

| Track | Owns | Why |
|---|---|---|
| **Property-law & jurisprudence** | The Rights Ontology (Person, Organization, Asset, Contract, Institution, Claim, Obligation, Delegation, Conflict) | The book's core is property rights; lawyers already formalize claims/obligations |
| **Analytic philosophy / deontic logic** | Axiom consistency, consent theory, the meaning of "justice within rights" | Keeps the formal system Gödel-consistent and non-dialectical |
| **Economics & mechanism design** | `DependencyIndex`, `ExitOptions`, `VoluntaryOrder`, market simulations | Coercion ≈ foreclosed exit + concentrated dependence — economics measures this |
| **Social-choice theory** | Conflict resolution (two owners, ownership vs privacy vs contract) | Aggregating competing legitimate claims is its native problem |
| **Formal methods / logic programming** | Inference engine (Datalog/ASP), consistency proofs (Lean/TLA+) | Turns "Permit/Deny" into "why", provably |
| **ML / NLP** | The semantic frontier: detecting `coerced`/`deceived`/manipulation from content | These are the only inherently statistical predicates; everything else stays symbolic |
| **Measurement / metrology** | Operationalizing the compass dimensions into validated metrics | "If you can't measure it, the compass is a slogan, not an algorithm" |
| **Multi-agent systems** | Stage-8 simulation worlds; stability, deadlock, abuse | Tests the theory before it touches anything real |
| **AI safety / alignment** | Comparative evaluation vs RLHF / Constitutional AI / rule-based governance | Stage-9 validation; the actual scientific claim |
| **HCI / cognitive science** | The Guidance Request Protocol (machine → human clarification) | "Contradiction → clarification" needs a real human-in-the-loop design |

## The nine stages (sequenced, with dependencies and honest status)

| # | Stage | Deliverable | Grounded in | Status today |
|---|---|---|---|---|
| 1 | **Formal Specification** | Every concept → a typed signature with `DEFINED/PARTIAL/OPEN` status | THEORY.md A1–A7, consent, compass | **STARTED** — see [`spec/FORMAL_SPEC.md`](spec/FORMAL_SPEC.md) |
| 2 | **Rights Ontology** | Person/Org/Asset/Contract/Institution/Claim/Obligation/Delegation/Conflict types + relations | THEORY.md "Rights Ontology" (Prolog) | Thin (Human/Machine/Resource in `fdk/model.py`); needs expansion |
| 3 | **Inference engine** | "why forbidden" = the set of violated axioms, derived not asserted | THEORY.md `permissible(A)` conjunction | Primitive: `check_legitimacy` returns `violated_axioms`; not a real engine |
| 4 | **Conflict resolution** | A protocol/criterion for competing legitimate claims | THEORY.md `if_conflict_then_clarify/request_guidance` | **OPEN — hardest gap.** Protocol named, no resolution formula |
| 5 | **Guidance engine** | Guidance Request Protocol: detect missing info → ask human → verify rule | THEORY.md GuidanceFunction | `fdk/guidance.py` produces requests; rule-verification loop missing |
| 6 | **Mahdavi compass (measured)** | Validated metrics for the five compass dimensions | THEORY.md MahdaviCompass | Scores *given* deltas; **who computes the deltas is OPEN** |
| 7 | **Planner** | `State+Goal+Constraints+Rights+Compass → candidates → eval → decision` | The book's chain | `fdk/pipeline.py` is the spine; candidate *generation* + ranking-in-loop missing |
| 8 | **Simulation** | Small worlds (marketplace: agents, resources, contracts, consent) | — | Not built |
| 9 | **Comparative research** | Empirical + formal: does it beat RLHF / CAI / rule-based? | THEORY.md comparison table | **Unproven — the actual scientific claim** |

## Five-year compression (honest, not a promise)

- **Y1** — Formal spec, ontology, inference engine.
- **Y2** — Conflict resolution, consent theory, guidance theory.
- **Y3** — Mahdavi compass measurement, simulator.
- **Y4** — Planner (the Decision Kernel proper).
- **Y5** — Comparative research, academic validation.

## The one risk that matters

The project's risk is **not** weak engineering. It is believing the book converts
directly into code. The hard work from here is **defining justice, coercion,
deception, consent, guidance, and the desired order precisely enough for a machine
to reason over** — and *measuring* them. That is what decides whether the Theory
of Freedom becomes a real decision paradigm or stays a philosophical framework.

## Attribution

- **Theory** — نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
- **Engineering** — Ali Pourrahim. The two are kept separate, always.
