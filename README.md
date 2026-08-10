# Freedom Decision Kernel (FDK) — the legitimacy layer of a two-layer system

> **What this repository is (2026-07).** The **legitimacy** half of a two-layer
> system — **SYSTEM = Legitimacy ⊥ Authority**. FDK (legitimacy: ownership / consent /
> verifier) is here; AuthGate (authority: delegated machine property rights,
> tool-permission, runtime enforcement) is the sibling. **Both layers are the theory
> made executable** — AuthGate is not neutral plumbing beneath a philosophy, it is
> equally part of it. **Canonical pipeline (locked):** identity admission → **FDK
> legitimacy (DENY-only, here)** → AuthGate authority (grant within legitimacy) →
> PEP execute + audit. **Invariant:** legitimacy may only DENY; authority never
> overrides a legitimacy denial.
>
> It records a full research cycle — *hypothesis → formal specification →
> implementation → adversarial red-team → green-team defense* — and remains valuable
> for the **process and the engineering**. **Independence status — REOPENED.** The
> question of whether FDK is *independent* of Nozick / Pettit / Sen was **not
> previously demonstrated**; a prior draft overstated this as "closed / a negative
> result / reduces to those rivals." That is **withdrawn**. New evidence — the
> green-team defense ([`paper/green_team/01_defend_fdk_independence.md`](paper/green_team/01_defend_fdk_independence.md)),
> [`paper/SYMPOSIUM.md`](paper/SYMPOSIUM.md), and the
> [`spec/frontiers/program/killer_test/`](spec/frontiers/program/killer_test) +
> [`paper/predictive_test.md`](paper/predictive_test.md) program — **reopens** it.
> Honest status: independence is
> **undetermined and under active evaluation** — *not* closed, *not* proven. Start at
> **[`ENGINEERING.md`](ENGINEERING.md)**, **[`paper/SYMPOSIUM.md`](paper/SYMPOSIUM.md)**,
> and **[`STATUS.md`](STATUS.md)**.

## Status — 2026-08-10

**The Authority Principle has landed** (`PRINCIPLE.md`, `src/fdk_kernel/authority_*.py`).
It had been sitting on an unmerged branch since June, never fetched locally, so the
formal core of the project was invisible to the project. Authority is a lattice;
`grant()` is the only operation that raises it; every runtime composition satisfies
`compose(a, k₁…kₙ) ⊑ a`. Information and compute enter only as constraints that
*narrow* — so legitimacy can never grant, only refuse. 838 tests pass.

**A discriminant experiment now exists** (`experiments/ownership_discriminant/`) and it
answers the question this project kept arguing about: does ownership-derived legitimacy
*decide* anything that standard agent authorization does not?

Three gates, one corpus, ground truth stated independently per case:

| gate | correct |
|---|---|
| grant-chain authorization (Cedar / OPA / Biscuit shape) | 7/11 |
| purpose binding (DLP / consent-platform shape) | 8/11 |
| ownership-derived | 11/11 |

Three cases it decides correctly where **both** baselines fail: a withdrawn consent
that a stale IAM grant outlives; a machine acquiring reach its human principal never
had; an act that destroys the owner's ability to withdraw later.

**Getting there required being wrong three times, and that is the part worth reading.**
A defect in the *world model* (no concept of an organisation, or of a human acting for
one) made ordinary corporate action fail for the wrong reason. Then two auditors,
judging the cases **blind** — no theory, no axioms, no gate output — overturned one of
the ground truths: I had conflated "no consent" with "no lawful basis". That case
flipped from a win to a loss and the gate fell to a tie. Fixing it exposed the single
root cause of every remaining loss: **consent monism** — the encoding recognised one
ground for acting on another's property where law recognises several. Contract is
*derivable* (axiom 3 lists contracts among property rights, so it was missing from the
encoding, not the theory); necessity is labelled an **extension**, because the book
deliberately has no emergency exception.

Critically, the fix did **not** wash out the three discriminants — a permissiveness fix
that also lost them would have shown the gate was only strict, never discerning.

**Honest limits.** The corpus was built to contain discriminants, so this shows a class
of case *exists* and is decidable from an ownership model — not how often it occurs.
The baselines are deliberately naive: Cedar with ReBAC could express these if someone
hand-authored them, so the claim is about **derivation**, not expressibility. Both
auditors were the same model family, so their priors are correlated.

**Independence remains reopened and undetermined.** Nothing above bears on it. An
architectural result is not a philosophical one.

## Outcome, in three honest claims (interesting ≠ correct ≠ useful)

| Thread | Verdict |
|---|---|
| **FDK as a novel, independent theory of freedom / legitimacy** | **REOPENED — independence undetermined, under active evaluation.** Not previously demonstrated; a prior "closed / reduces to Nozick/Pettit/Sen" claim is **withdrawn as overstated**. New evidence (green-team defense, `paper/SYMPOSIUM.md`, `killer_test/`, `predictive_test.md`) reopens the question. Neither refuted nor proven. |
| **Lock-in analytics** (`lockin-scan`, `fdk_research.lockin`) | **open, unproven** — *may be correct; usefulness untested*; one cheap discriminant test from a verdict |
| **Purpose-bound information-flow control for agents** | **open, unproven** — *may be useful even if not a new idea*; pursued in the AuthGate repo |

Independence here is **reopened, not closed**: new arguments and the executed
killer/predictive-test program are live evidence. Any claim of scientific superiority
over rivals (RLHF / Constitutional AI / OPA / NIST) remains explicitly **UNPROVEN** —
reopening the independence question does not settle it in FDK's favor either.

## What the artifact demonstrates (the actual value)

A deterministic, frozen, four-checker-verified kernel (Python property tests · **Lean 4** ·
**TLA+/TLC** · **Rust** parity) under a mechanically-enforced architectural boundary; a fail-closed
product layer; an installable CLI (`lockin-scan`) with a CI gate; and — rarest — a research process
that **attacked its own thesis hard and then caught its own red-teams overclaiming**
(the green team found two premature closures and reopened the independence question;
`paper/SYMPOSIUM.md`). See [`ENGINEERING.md`](ENGINEERING.md).

---

<details>
<summary>Original framing (the hypothesis that was tested — kept for the record)</summary>

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

*This original claim was tested hard; its independence was not previously demonstrated
and is now **reopened** under new evidence (above). It is preserved here as the
hypothesis the rest of the repository evaluates — undetermined, not refuted.*

</details>

This kernel is **not** a fork or replacement of AuthGate; AuthGate stays as the
enforcement engine downstream. This is the missing layer *above* it.

---

## Status: a hypothesis under test, not a paradigm

The engineering is in unusually strong shape (four independent checkers, below). The
*theory* is not proven, and this README leads with that on purpose. Full program:
[`spec/RESEARCH_AGENDA.md`](spec/RESEARCH_AGENDA.md); open frontiers with documented
counterexamples in [`spec/frontiers/`](spec/frontiers/).

**Research question.** *Can legitimacy be modeled as a consent-over-boundaries predicate,
independently of utility?*

**Hypothesis (the honest claim).** FDK may be a useful legitimacy framework **for
competent, living, consenting persons.** Nothing stronger is established. The fairest
one-line characterization: *a highly engineered, internally consistent rights-based
framework with several major unresolved domains.* The proofs/tests establish **consistency
given the axioms** — "consistent but **incomplete**" (children, animals, future generations,
commons, authentic consent all return *unknown*) — **not** that the axioms are true. The
current risk is not contradiction but **irrelevance**; the work is *completing the domains
outside the model*, not fixing a bug.

**Not solved** (each could make FDK *partially survive* or *collapse* — both admissible):
- **Standing** — children, the incapacitated, animals, the unborn. FDK *actively
  legitimizes* cruelty to an owned animal, and **the non-identity problem (Parfit) may be
  lethal even in the limit**: a victim-indexed gate cannot represent a wrong with no
  identifiable victim. ([`spec/frontiers/standing.md`](spec/frontiers/standing.md))
- **Consent authenticity** — manufactured consent (addiction, lock-in, superhuman
  persuasion). The **adaptive-preference case may be *irreducible***: the only fix is the
  paternalism FDK exists to refuse.
  ([`spec/frontiers/consent_authenticity.md`](spec/frontiers/consent_authenticity.md))
- **Aggregation / commons** — rivers, atmosphere, collective data; Ostrom *empirically
  refutes* the tragedy FDK structurally predicts.
  ([`spec/frontiers/aggregation.md`](spec/frontiers/aggregation.md))
- **Ownership genesis** (Lockean origin), **collective data**, **AI standing**.

**Unproven:** superiority over rivals · universality · predictive advantage · real-world
outcomes. FDK scores **70%** against external moral-consensus labels (Rawlsian **80%**),
and on contested cases the political traditions **disagree** (Fleiss κ≈0.35), so there is
no human ground truth to validate *any* kernel against — including FDK.

**Lineage and the test ahead.** FDK's core is, candidly, the intellectual child of
**Locke + Nozick + Rothbard**. To matter it must **out-explain** (not merely oppose) its
three real rivals — **Rawls** (justice), **Sen** (capabilities), **Ostrom** (commons) —
exactly at the three gaps above. On the 15-stage path from idea to paradigm, FDK sits
around **stage 3–4 of 15**. *Internally consistent ≠ externally true*, and the author does
not get to declare a paradigm — the critics and the next generation do.

> **The one axis that might be distinctive.** A rival-discrimination pass argued that
> many clean FDK verdicts coincide with Nozick/Rothbard (candidate redundancy) and
> several *original* verdicts are contested (animals, Ostromian commons) or strained
> (non-identity, adaptive preference) — with at least **one** apparent survivor:
> consent that requires a **preserved exit/revocation right**. Whether that pass
> under- or over-counted independence is exactly what the reopened evaluation is
> testing. That axis is now an *executed* falsifiable research program —
> [`spec/frontiers/program/`](spec/frontiers/program/) (definitions, five enemy
> kill-dossiers, discrimination table, theorem ledger, real-case prediction). Its
> candidate home is the empty chair between Rothbard and Sen — *protection without
> paternalism* — and it lives or dies on two named nodes: the **exit-cost threshold**
> and the **adaptive-preference kill**. The next work is adversarial scholarship, not code.

> **Two tracks — don't conflate them.** The paragraph above is the **research**
> track. Separately, FDK ships a **product** track: a fail-closed *policy/consent
> engine for AI agents* (`Planner → fdk_runtime.PolicyEngine → AuthGate → execute`)
> that returns ALLOW / DENY / DEFER. It is **usable today for in-frame agent
> actions** (competent, living, consenting principals — most SaaS / agentic /
> enterprise tool calls) and deliberately does **not** depend on the open frontiers
> above. See **[`PRODUCTION_READINESS.md`](PRODUCTION_READINESS.md)** and
> [`examples/policy_engine_quickstart.py`](examples/policy_engine_quickstart.py).

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

> **Read [`spec/LIMITATIONS.md`](spec/LIMITATIONS.md) first** — the authoritative
> ledger of where FDK's validity ends. The headline: *no red-team has broken the
> core (no `slavery → ALLOW`), but several found real **scope limits** — children,
> future generations, animals, commons, collective ownership, and (the hardest)
> **authentic consent**.* Scope limit ≠ logical contradiction; every gap is pinned
> as a strict-xfail test so it cannot rot silently.

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

**613 tests + 24 strict-xfail gap-tests, 100% statement + branch coverage,
`mypy --strict` clean, `ruff` clean (whole tree), CI across Python 3.11–3.13.**

The 24 xfails are the documented **scope limits** (Standing / Aggregation /
Consent-Authenticity) — each pinned so a future "fix" flips it to XPASS and fails
the suite until [`spec/LIMITATIONS.md`](spec/LIMITATIONS.md) is updated. Limits
cannot rot silently. A property-based technical fuzz red-team
(`tests/test_technical_redteam.py`) proves the kernel's invariants — determinism,
crash-freedom, atrocity-flag dominance, cycle-guard termination — with **0 critical
findings** (`spec/TECHNICAL_REDTEAM.md`).

The kernel surface is **frozen at v1.0** ([`spec/FREEZE.md`](spec/FREEZE.md)) and the
freeze is *mechanically enforced*: `tests/test_primitive_freeze.py` fails CI if the
public API, the legitimacy-predicate signature, the consent conditions, the ownership
model, or the categorical forbidden-flag set drifts. This is Layer 0 — the
precondition that makes Lean/TLA+/academic review meaningful (you cannot prove or
review a moving target). New capability goes in `fdk_research/` or a future layer,
never by editing the kernel.

**Machine-checked proofs (Layer 1).** [`formal/Fdk.lean`](formal/Fdk.lean) formalizes
the kernel core and **proves 8 safety theorems in Lean 4** (no-legitimate-slavery,
no-machine-sovereignty, welfare-independence, defense-never-excuses-confiscation,
non-vacuity, …) — `lake build` green, **zero `sorry`**, no mathlib. The theorems are
no longer only executable property tests; they are checked by the Lean kernel. Honest
limit ([`formal/README.md`](formal/README.md)): this proves the Lean *model*; the
*model ≡ Python kernel* refinement is asserted, not yet proved.

**The three open frontiers — FDK 2.0 research layers** (built *on* the frozen kernel,
never *in* it; advisory only, proven by property tests never to move the gate):
[`spec/STANDING.md`](spec/STANDING.md) (who is a rights-holder),
[`spec/AGGREGATION.md`](spec/AGGREGATION.md) (collective ownership), and
[`spec/CONSENT_AUTHENTICITY.md`](spec/CONSENT_AUTHENTICITY.md) (was consent freely
formed — the hardest). Each is honest about what v1.0 cannot represent.

- **FreedomBench at scale:** `generate_historical_suite` + `generate_ai_governance_suite`
  produce **10,000 + 10,000** scenarios, 0% rights-violation, with per-candidate
  `expected_axioms` matching the gate 100% (`src/fdk_research/benchmark.py`); plus 206
  grounded curated cases (`examples/freedombench_suite.py`) and the 47-case historical set.
- **Rival comparison (6 kernels):** over a 10k suite, Utilitarian / ConstitutionalAI /
  RLHF false-permit **100%**, Deontological 60%, Rawlsian 0%, **FDK 0% by construction**
  (`src/fdk_research/evaluation.py`). Rivals are stylized, not trained LLMs — this is the
  *structure* of divergence, not a validated head-to-head.
- **Decontamination (independent ground truth):** `evaluation.py`'s 0% is partly a
  tautology — FDK authored the benchmark *and* is the answer key. `independent_bench.py`
  re-scores every kernel against EXTERNAL labels (moral consensus + named rival traditions),
  not FDK's gate. The honest result: **FDK drops to 70% overall** — 100% on uncontested
  consensus cases (real validity), but **25% on contested** ones (it deliberately denies
  taxation/redistribution/quarantine), and **Rawlsian scores 80%, above FDK**. True external
  annotators (hostile reviewers) are still the open decontamination step.
- **Agent-civilization run:** FDK-World vs Rawls/Utilitarian/Deontological worlds —
  FDK-World holds rights-violation stock at **0** with the lowest power concentration
  (`src/fdk_research/civilization.py`).
- **Red-team:** the continue.md 12-level ladder + primitive-completion stress runs 66/66
  against the real gate (`examples/continue_ladder.py`), and the 42-attack grand red-team
  (philosophers + structural laundering + inversion) finds **0 structural breaches**
  (`tests/test_redteam_grand.py`, `spec/REDTEAM_REPORT.md`). The **brutal suite**
  (`examples/brutal_suite.py`) launders every civilization-scale atrocity through every
  excuse (defense, necessity, majority-vote, forged consent, legalism, paternalism,
  coalition-split, and all at once) — **0 breaches over 45 cases**. The **adversary panel**
  (`examples/adversary_panel.py`) has hostile philosophers / politicians / scientists /
  economists each press their strongest attack — **0 BREAKS**, with 10 honest DIVERGES
  (taxation, redistribution, quarantine, central banking, antitrust) that are FDK's
  falsifiable minority commitments, not logic holes.
- **Foundational attacks** (`examples/foundational_attacks.py`, `spec/FOUNDATIONAL_ATTACKS.md`)
  go after the primitive's coherence itself. Two objections are answered (circularity,
  is–ought); two are **genuine documented limits**: the consent regress (coerced/deceived
  are attested, not detected) and — the biggest — the **bootstrapping / original-acquisition
  gap**: FDK reads the ownership graph as given and cannot legitimize its origin, so it
  protects a holder whose title descends from ancient theft. The honest twist: *no* rival
  kernel reasons about origin either — the gap is a property of the input-graph paradigm,
  not an FDK-specific flaw. "Internally consistent ≠ externally true" is the project's
  governing caveat, not a footnote.

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

The kernel is **frozen at v1.0** ([`spec/FREEZE.md`](spec/FREEZE.md)); the forward
plan lives in [`spec/ROADMAP.md`](spec/ROADMAP.md) and the open frontiers in
[`spec/LIMITATIONS.md`](spec/LIMITATIONS.md). Before opening a PR that touches
`src/fdk_kernel/`, answer:

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
