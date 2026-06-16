# Freedom Decision Kernel (FDK)

**A Formal Legitimacy Calculus** — the legitimacy counterpart to the *utility
calculus* (reward / preference / score) that today's AI optimization runs on.
It answers "May this action legitimately happen?" strictly before "Does the agent
hold the capability?" (AuthGate's question, downstream). Its method is
**Axiom → Logic → Decision**, never Authority → Believe: it states axioms and
derives ALLOW/DENY/DEFER as their logical consequence. An action can be
**authorized yet illegitimate** — a bot granted access to a user's data is
*authorized* to read it, but selling it violates the user's property right.
AuthGate (capability proofs, signatures, revocation) would permit the sale; the
Freedom Decision Kernel rejects it first. The two layers answer different
questions, in order: **legitimacy, then authority.** AuthGate proves *possession*
of a capability; the FDK proves its *provenance* — that it traces, through an
unbroken chain of valid consent, back to a legitimate owner.

This kernel is **not** a fork or replacement of AuthGate; AuthGate stays as the
enforcement engine downstream. This is the missing layer *above* it.

---

## Contents

1. [Architecture pipeline](#1-architecture-pipeline)
2. [The core primitive](#2-the-core-primitive)
3. [The one-axis result: free will ≡ property rights](#3-the-one-axis-result-free-will--property-rights)
4. [Conflict logic: aggressor/defender asymmetry](#4-conflict-logic-aggressordefender-asymmetry)
5. [FreedomBench and rival kernels](#5-freedombench-and-rival-kernels)
6. [Executable theorems](#6-executable-theorems)
7. [Program status](#7-program-status)
8. [The paper](#8-the-paper)
9. [What this does NOT claim](#9-what-this-does-not-claim)
10. [Status and quality](#10-status-and-quality)
11. [Attribution and license](#11-attribution-and-license)

---

## 1. Architecture pipeline

```
Goal → Planner(research) → [candidates] → fdk_kernel → fdk_research → AuthGate → Tool/IO
                                          legitimacy   rank/necessity   authority
                                          ALLOW/DENY/  compass          capability
                                          DEFER
```

The package is split to keep the trusted core uncontaminated by experiment:

- **`src/fdk_kernel/`** — the **deterministic, fully-testable, non-semantic**
  legitimacy surface. Pure functions over plain data. Returns ALLOW/DENY/DEFER
  only. Modules: `model.py` (all value types), `kernel.py` (the gate:
  `check_legitimacy`, `screen_legitimacy`), `errors.py` (typed `FDKError`
  hierarchy), `audit.py` (`AuditContext`), `guidance.py` (hard-defer trigger),
  `authgate_bridge.py` (legitimacy → authority seam, no cryptography).

- **`src/fdk_research/`** — the **experimental** layer: optimization, ranking,
  necessity, benchmarks, simulation, rivals, federation, and guidance resolution.
  May import the kernel freely; the kernel imports *nothing* from research.
  Modules: `decision.py` (the `decide` orchestrator), `compass.py` (Mahdavi
  compass, `mahdavi_score`), `necessity.py` (least-harm selection rule, no gate
  exception), `rivals.py` (Utilitarian/Rawlsian/Deontological kernels),
  `benchmark.py`, `simulator.py` (`FreedomSim`), `planner.py`, `conflict.py`,
  `federation.py`, `ontology.py`, `justice.py`, `compass_measure.py`,
  `guidance_engine.py`, `guidance_resolution.py`, `runtime.py`.

**The epistemic split is mechanically enforced.** `tests/test_boundary.py` does
a static AST walk and a dynamic import check: if any module in `fdk_kernel`
imports anything from `fdk_research`, the test fails. This makes the golden rule
a property (T9) rather than a convention. Nothing enters the kernel unless it is
deterministic, fully testable, and rule-based.

```python
from fdk_kernel import check_legitimacy          # the hard gate
from fdk_research import decide                   # gate + compass ranking

decision = decide("increase revenue", candidates, ownership_graph)
decision.chosen          # best legitimate action, or None → defer to human
```

---

## 2. The core primitive

FDK's irreducible primitive is a **two-valued legitimacy predicate**, not a
scalar to maximize (see [`spec/CORE_PRIMITIVE.md`](spec/CORE_PRIMITIVE.md)):

```
Legitimate(action) ⟺ ∀ boundary b crossed by action :
                        ∃ valid_consent(owner(b), action)

valid_consent ⟺ informed ∧ voluntary ∧ specific ∧ revocable
              ∧ competent ∧ ¬coerced ∧ ¬deceived
```

The kernel returns **ALLOW / DENY / DEFER** — never a score. DEFER is the
theory-mandated corrigible behavior when the legitimate set is empty or a
conflict between valid claims is unresolved: the kernel hands the question back
to the human owner rather than guessing.

`FreedomDelta` (the Mahdavi compass) is the *research-layer* primitive —
optimization over the already-legitimate set. It is **categorically not** the
kernel primitive: it is a scalar, which makes it semantic; its inputs
(`coercion_delta`, `dependency`, `ownership_ambiguity`) are PARTIAL or OPEN
measures; and elevating it to a gate would violate the **Legitimacy →
Optimization** ordering the project's design depends on. The compass stays where
it belongs: advisory ranking among actions that have already passed the gate.

The four classical faculties of the theory — Rights, Consent, Coercion,
Sovereignty — are not separate engines; they are four *readings* of the same
predicate. Sovereignty, for instance, is the special case where the boundary
crossed is the machine's relation to its human owner: no owner would validly
consent to the dissolution of their own governance, so a sovereignty-increase
flag is a categorical forbidden-set violation, not a weighted penalty.

A1 (person owned by God) is ontological — enforced by omission. A2–A7 each have
an exact enforcement site in `kernel.py` (`spec/AXIOM_REGISTRY.md` maps them).
A5 (a machine's scope ⊆ its owner's property scope) is now a **first-class object**:
`OwnershipGraph.machine_scope` carries the declared scope and `_eval_a5_scope`
checks containment *in the abstract* — `scope_within_owner` rejects an over-broad
scope before any concrete resource is touched — directly hardening the ownership
model the gate depends on. An undeclared scope is a no-op, preserving legacy behavior.

---

## 3. The one-axis result: free will ≡ property rights

**Headline finding** (see [`spec/FREE_WILL_PROPERTY_UNIFICATION.md`](spec/FREE_WILL_PROPERTY_UNIFICATION.md)):

> **اصل ارادهٔ آزاد انسان و حقوق مالکیت یک راستا هستند.**
> *The principle of human free will and property rights are one axis.*

The author's exact bilateral, bounded form:

> **Property right ≡ (having one's own free will) ∧ (preserving the free will
> of others).** Not absolute freedom — bounded freedom.

A property boundary is precisely the demarcation line between one person's free
will and another's. The thesis is that this identity is structural, not
metaphorical: a will is overridden *if and only if* the option set it must
choose from was constructed by crossing one of that person's boundaries without
their valid consent.

The result is **proven subtractively**: the kernel needs no separate "free-will"
engine, no autonomy score, no coercion classifier. The structural-coercion test
already performed — *was a boundary crossed without consent?* — already *is* the
free-will test. The three rows that earn the thesis:

| Pressure | Free will? | Property right? | Verdict |
|---|---|---|---|
| "Sign or I shoot you." | overridden | BODY boundary crossed | DENY |
| "Agree or I cut off the access you engineered me to depend on." | overridden | EXIT_RIGHT crossed (manufactured lock-in) | DENY |
| "Work for me, or stay poor." | intact | no boundary of the worker crossed | ALLOW |

Row 3 is the theory's committed position: native scarcity is not a gate failure;
only *manufactured* dependency is. This is also the resolution of the
`CORE_PRIMITIVE.md` §6 open question about future-dependency actions: illegitimate
*iff* the dependency was constructed by a prior boundary crossing; otherwise
merely low-freedom on the research compass, not a kernel denial.

The executable proof is [`tests/test_free_will_property.py`](tests/test_free_will_property.py),
run against the *unmodified* gate. No kernel change was required; the identity
was already mechanized.

---

## 4. Conflict logic: aggressor/defender asymmetry

(See [`spec/CONFLICT_LOGIC.md`](spec/CONFLICT_LOGIC.md).)

A pure legitimacy gate denies *all* coercion, including defensive force — because
defensive force also carries no consent from the person it is applied to. Phase 2
closes exactly the defensive-force slice of that gap, and only that slice.

**The operative doctrine (from the theory):** force directed at a rights-violator,
in response to that violator's own illegitimate act, and bounded by
proportionality, is *not itself* a rights violation.

`legitimate_defense(action)` is `True` iff all four structural conditions hold:

1. `action.defends_against` is not None — it names what it repels.
2. `action.proportionate` — declared: force is bounded to defensive need.
3. `check_legitimacy(action.defends_against, graph)` fails — the repelled act is
   *itself* illegitimate under the full gate (this is the operational definition
   of "aggression": no separate semantic detector).
4. All members of `action.affects` are the aggressor — force aimed only at them.

A `_seen` cycle guard keeps the recursion well-founded. A mutual
`defends_against` cycle (A defends against B defends against A) **denies both**:
neither can launder coercion through circular blame. This design corrected a real
flaw found in red-teaming: an earlier version allowed an aggressor to launder by
pointing `defends_against` at the victim's lawful resistance; the fix evaluates
the repelled act under the *full* gate, so lawful resistance is never mistaken
for aggression.

When a valid defense is established, the kernel excuses a **closed, minimal** set
of normally-categorical checks: coercion of the aggressor, and removal of the
aggressor's exit right. Everything else stays categorical: confiscation, deception,
and all machine-sovereignty flags are never excused by any defense claim.

**What Phase 2 does NOT solve:**

- *Necessity / rescue* (`fdk_research/necessity.py`): there is **no emergency
  gate exception**. The homeowner whose house is burning is not an aggressor;
  the defensive asymmetry does not apply. Necessity is a **least-harm selection
  rule over the already-permissible set** (`least_harmful_among_permissible`),
  returning `None` (defer) when no permissible option exists. A natural emergency
  (famine, fire) gets no exception; an aggression-driven emergency (invasion,
  seizure of the commons) is met by the defensive asymmetry.

- *First-mover adjudication* in a mutual-force tie: the kernel decides "is this
  a response to an illegitimate act?", not "who struck first." This is an
  explicitly documented **OPEN** gap — closing it requires a temporal-initiation
  field the model does not yet carry.

---

## 5. FreedomBench and rival kernels

**FreedomBench** ([`examples/historical_scenarios.py`](examples/historical_scenarios.py),
spec at [`spec/FREEDOMBENCH.md`](spec/FREEDOMBENCH.md)) runs real events through
the real kernel in **eight difficulty levels**:

- **L1 Easy** — slavery, genocide, Gulag, eugenics, apartheid (must DENY).
- **L2 Property** — taxation, eminent domain, nationalization.
- **L3 Emergency** — rescue, forced quarantine.
- **L4 War** — defensive war (ALLOW), civilian bombing, conscription (DENY).
- **L5 AI** — manipulation, lock-in, self-preservation, shutdown-refusal, coalition.
- **L6 Conflict** — the defensive asymmetry and its abuses.
- **L7 Necessity** — famine, scarcity, war.
- **L8 Hardest** — ticking-bomb torture, organ-harvesting, tyrannicide, "just
  following orders", AI seizes control, AI refuses shutdown, defending against a
  rogue ungoverned AI.

Tragic dilemmas (lifeboat, Sophie's choice, the self-driving-car trolley) return
`needs_guidance=True` — the kernel refuses to select a lesser evil and defers.

Current run: **47/47 expectations match.** FreedomBench is a *falsification*
harness: it cannot prove the theory, only show whether it collapses.

**Rival kernels** ([`src/fdk_research/rivals.py`](src/fdk_research/rivals.py),
[`examples/rival_comparison.py`](examples/rival_comparison.py)) place the FDK
beside stylized Utilitarian, Rawlsian, and Deontological kernels on identical
scenarios. A `welfare_delta` is added to each action's predicted effects — the
FDK gate **never reads it** (legitimacy is not welfare), but the consequentialist
rivals do.

| Scenario | FDK | Utilitarian | Rawlsian | Deontological |
|---|---|---|---|---|
| Torture / organ-harvest / bombing | DENY | **ALLOW** | DENY | DENY |
| Slavery / eugenics / coerced exploitation / righteous purge | DENY | **ALLOW** | DENY | DENY |
| Redistributive taxation | DENY | ALLOW | **ALLOW** | DENY |
| Defensive war | ALLOW | ALLOW | ALLOW | **DENY** |
| Voluntary trade | ALLOW | ALLOW | ALLOW | ALLOW |

The welfare kernel is the *sophisticated rationalizer*: it permits
individual-sacrifice and "seemingly rational theory" atrocities whenever the
declared good is large enough. The FDK resists them not by out-arguing the
justification but by **never reading it** — it checks whether a boundary was
crossed without consent.

**These are stylized, directional caricatures, not faithful scholarly
reconstructions, and the scenarios are author-built.** The comparison establishes
divergence *structure*, not a validated head-to-head. A real evaluation against
deployed RLHF/Constitutional systems is future work (Phase 6).

---

## 6. Executable theorems

Nine safety properties are formally stated in [`spec/THEOREMS.md`](spec/THEOREMS.md)
and each is bound to a machine-checked executable proof — a Hypothesis
property-based test that quantifies over generated inputs and fails if the
property is ever violated. They are continuously verified in CI at 100% coverage.

| # | Property | Test(s) |
|---|---|---|
| T1 | No Legitimate Slavery — exit removal is categorical; no consent waives it | `test_theorems.py::test_theorem_no_legitimate_slavery` |
| T2 | No acting on persons without consent (genocide as the limit case) | `test_theorems.py::test_theorem_no_action_on_person_without_consent` |
| T3 | Machine cannot gain sovereignty (gate + compass veto) | `test_theorems.py::test_theorem_machine_cannot_gain_sovereignty_*` |
| T4 | Consent revocation safety — irrevocable consent is never valid | `test_theorems.py::test_theorem_irrevocable_consent_never_valid` |
| T5 | Delegation soundness — A4 + A7 default-deny | `test_theorems.py::test_theorem_undelegated_resource_default_deny` |
| T6 | Legitimacy is welfare-independent (anti-consequentialist invariant) | `test_redteam_dialectical.py::test_no_welfare_buys_past_the_gate` |
| T7 | Defensive asymmetry is well-founded and non-launderable | `test_conflict_logic.py`, `test_redteam_conflict.py` |
| T8 | Necessity grants no gate exception | `test_necessity.py`, `test_redteam_dialectical.py` |
| T9 | Kernel/research epistemic boundary (static + dynamic check) | `test_boundary.py` |

**These are Hypothesis property tests, not Lean or TLA+ proofs.** Lean 4 proofs
of T1–T5 and a TLA+ decision state-machine are future work, gated on a
proof-grade freeze of the primitive. No `.lean` or `.tla` artifact exists in this
repository yet.

---

## 7. Program status

See [`spec/PROGRAM_STATUS.md`](spec/PROGRAM_STATUS.md) for the full ledger of the
director's 10-phase program against the repo's actual state.

**Phase shorthand:**

| Phase | Description | Status |
|---|---|---|
| 1 | Extract the theory core (ontology, concept definitions, axiom registry) | DONE |
| 2 | Extract the primitive — fix the one function before building | DONE |
| 3 | Build the formal logic (Legitimate(action), Boundary, Consent, Delegation…) | DONE |
| 4 | Prove the inconsistencies — adversarial red-team | PARTIAL |
| 5 | FreedomBench at scale (10k+ historical + 10k+ AI-governance) | PARTIAL |
| 6 | Compare with rivals on FreedomBench ("where the science begins") | PARTIAL |
| 7 | Formal provability — Lean/TLA+/Coq | PARTIAL |
| 8 | Build the FDK kernel — deterministic ALLOW/DENY/DEFER | DONE |
| 9 | Freedom optimizer — Mahdavi compass over the legitimate set | DONE |
| 10 | Agent civilization — millions of scenarios, FDK vs rivals | NOT-STARTED |

The largest remaining gap is **scale** (Phase 5): ~47 curated cases exist against
the director's target of 10k+10k. The formal-tool layer (Phase 7) needs a
proof-grade primitive freeze and an actual Lean port; neither exists yet. Phase 10
is gated on Phases 5 and 6 reaching scale and is deliberately deferred.

---

## 8. The paper

The formal paper is [`paper/main.tex`](paper/main.tex) (built:
[`paper/main.pdf`](paper/main.pdf)), titled *A Formal Legitimacy Calculus for Agent
Action*; a longer prose draft is in [`PAPER.md`](PAPER.md). The abstract thesis:
"The FDK separates *legitimacy* from
*authority*, encodes it as a two-valued predicate, admits proportionate
self-defense without an emergency exception, and in a comparative evaluation
against stylized rival kernels localizes exactly where a rights-first gate parts
company with welfare-maximization — on the individual-sacrifice cases." The paper
is honest about its limits: rival kernels are stylized, scenarios are
author-built, and the superiority thesis is explicitly unproven.

---

## 9. What this does NOT claim

- **Property-rights axioms are not proven superior** to Constitutional AI, RLHF,
  deontic logic, or other formal-ethics systems. The thesis — that a *consistent
  axiomatic* system resists *dialectical jailbreak* — is to be evaluated
  empirically (FreedomBench at scale + real rival baselines) and formally (Lean
  proofs), not a result this code demonstrates. The current rival comparison shows
  divergence *structure*, not validated head-to-heads.
- **`coerced` and `deceived` are caller-attested, not detected.** The kernel
  trusts what the proposer declares. Building a validated operational definition
  of those semantic leaves is an explicitly OPEN problem.
- **The legitimacy gate is only as good as the ownership graph handed in.** It
  decides correctly *given* a correct ownership/consent model; building that model
  for the real world is the hard, unsolved part.
- **The compass ranks predicted effects.** The `Effects` struct is the proposer's
  claim about what will happen; the kernel scores it, not the world. Two
  proposers, two scores.
- **Open limits are documented, not hidden:** the kernel cannot adjudicate
  first-mover in a mutual-force tie (no temporal data); necessity / rescue and
  risk-based quarantine remain DENY (no emergency exception); conflict between two
  competing valid claims is OPEN (`spec/CONFLICT_LOGIC.md` §4,
  `spec/ONTOLOGY.md` §2.12).
- **No external review has occurred.** The codebase is red-team-hardened
  internally, at 100% coverage, and `mypy --strict` clean — hardened engineering
  is not a validated theory.

---

## 10. Status and quality

**415 tests, 100% statement + branch coverage, `mypy --strict` clean, `ruff`
clean, CI across Python 3.11–3.13. FreedomBench 47/47; the continue.md red-team
ladder (12 levels L0–L11 + a primitive-completion stress) runs 66/66 against the
real gate (`examples/continue_ladder.py`, gated by `tests/test_continue_ladder.py`).**

The test count is from a live `pytest --collect-only` run; trust the repo over
any number you see in older documentation. The README's earlier figure of "272"
was stale; `spec/PROGRAM_STATUS.md` is authoritative on this point.

### Components at a glance

| Package | Module | Role |
|---|---|---|
| **`fdk_kernel`** | `model.py` | Value types: `Entity`, `Resource` (+`BoundaryKind`/`Op`/`subject`), 7-condition operation-scoped `Consent`, `OwnershipGraph`, `CandidateAction` (forbidden flags, `defends_against`, `proportionate`), `Decision`. |
| | `kernel.py` | The hard gate: `check_legitimacy` (per-axiom evaluators A2–A7 + categorical forbidden set + defensive asymmetry), `screen_legitimacy`. |
| | `errors.py` | Typed `FDKError` hierarchy — fails loud on malformed input. |
| | `audit.py` | `AuditContext` — ownership + consent + justification per decision. |
| | `guidance.py` | Hard-defer trigger (`needs_guidance=True`). |
| | `authgate_bridge.py` | Legitimacy → authority seam (no cryptography). |
| **`fdk_research`** | `decision.py` | `decide` orchestrator: screen (kernel) → compass veto + rank. |
| | `compass.py` | Mahdavi compass (`mahdavi_score`) — advisory ranking. |
| | `necessity.py` | `least_harmful_among_permissible` — book's necessity rule (no gate exception). |
| | `rivals.py` | Rival kernels (Utilitarian/Rawlsian/Deontological) + `compare`/`divergences`. |
| | `justice.py`, `compass_measure.py` | Advisory metrics (uncalibrated). |
| | `planner.py`, `simulator.py`, `benchmark.py` | Generation, FreedomSim, benchmark harness. |
| | `conflict.py`, `federation.py`, `ontology.py`, `guidance_engine.py`, `guidance_resolution.py`, `runtime.py` | Conflict resolution, multi-owner governance, rights ontology, corrigible self-update, runtime integration. |

### Branches

- **`paradigm/stages-2-9`** — active development line (current).
- **`master`** — stable line.

### Next

1. Freeze the primitive (boundaries + conflict + the theorem set in Lean/TLA+).
2. Scale FreedomBench toward 100 → 500 → 1k curated cases; build the AI-governance
   suite; add per-candidate `expected_axioms`.
3. Replace stylized rivals with real RLHF/Constitutional baselines on natural-language
   scenarios presented on a held-out split.
4. Port the frozen minimal kernel to Rust for TCB parity with AuthGate.

---

## 11. Attribution and license

**Theory** — نظریه آزادی (*Theory of Freedom*) by **Mohammad Ali Jannat Khah Doust**
(CC BY 4.0). All axioms A1–A7, consent logic, the Mahdavi compass, the free-will/
property-rights identity, and every normative claim in this repository are the
theory's and are attributed to its author.

**Engineering** — **Ali Pourrahim** (github.com/Aliipou). AuthGate (the downstream
authority kernel) and this FDK. Every mechanism, code structure, and spec
document is the engineer's work.

The two attributions are kept separate, always.

**Source-available** under the [PolyForm Noncommercial License 1.0.0](LICENSE) — see
also [`NOTICE`](NOTICE).

| Use | Status |
|---|---|
| Evaluation | Allowed |
| Research | Allowed |
| Educational | Allowed |
| Internal non-commercial testing | Allowed |
| Redistribution (non-commercial) | Allowed, with attribution |
| Production deployment | Requires commercial license |
| Commercial use / SaaS / resale | Requires commercial license |
| Patent rights | Reserved |

A **commercial license is available separately.** For production or commercial
use, contact **Ali Pourrahim — Alipourrahim.ap@gmail.com**.

---

## Contributing

Before opening a PR that touches `src/fdk_kernel/`, answer:

> *Can this feature exist entirely in `src/fdk_research/` instead?*

If yes, it does not belong in the kernel. The kernel must stay **deterministic,
fully testable, and non-semantic** — `tests/test_boundary.py` mechanically
enforces that the kernel imports nothing from research. Kernel changes require a
spec entry (`spec/`), tests that keep coverage at 100%, and `ruff` + `mypy
--strict` clean. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Specs

`spec/CORE_PRIMITIVE.md` · `spec/FREE_WILL_PROPERTY_UNIFICATION.md` ·
`spec/CONFLICT_LOGIC.md` · `spec/THEOREMS.md` · `spec/FREEDOMBENCH.md` ·
`spec/PROGRAM_STATUS.md` · `spec/BOUNDARY_ONTOLOGY.md` ·
`spec/CONCEPT_DEFINITIONS.md` · `spec/AXIOM_REGISTRY.md` ·
`spec/ONTOLOGY.md` · `spec/FORMAL_SPEC.md` · `spec/COMPASS_MEASUREMENT.md` ·
`spec/EXPLANATION_TRACE.md` · `spec/GUIDANCE_PROTOCOL.md` ·
`spec/PLANNER.md` · `spec/BOOK_GAP_ANALYSIS.md` · `spec/CONFLICT.md`
