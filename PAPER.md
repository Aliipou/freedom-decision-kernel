# The Freedom Decision Kernel: A Computable Property-Rights Legitimacy Layer for AI Action

**Theory:** Mohammad Ali Jannat Khah Doust (نظریه آزادی / *Theory of Freedom*, CC BY 4.0)
**Engineering:** Ali Pourrahim
**Artifact:** `freedom-decision-kernel` (this repository) · downstream enforcement: `authgate-kernel`

---

## Abstract

The dominant framing of AI alignment is *control*: given a capable system, how do we
shape, constrain, or correct it? We argue for a prior question — *legitimacy* — and
present the **Freedom Decision Kernel (FDK)**, a working, fully-tested software encoding
of the decision layer of the Theory of Freedom. The FDK separates **legitimacy**
("should this action happen at all, under ownership, consent, and non-domination?") from
**authority** ("does the agent hold a capability?"): it enforces the former with a hard,
deterministic property-rights gate, ranks the permissible actions with the Mahdavi
compass, and **defers to the human owner** whenever the legitimate space is empty,
ambiguous, or underdetermined by the axioms. The kernel is pure Python, `mypy --strict`
clean, at 100% statement-and-branch test coverage, and wired — through an injected port,
with no cryptography of its own — to a separate verified capability kernel (AuthGate).

We are deliberate about scope. The *engineering* claims are facts: it runs, it is typed,
it is tested, an adversarial simulator shows it never *chooses* an illegitimate action,
and a cross-repo test exercises the real AuthGate verifier. The *theory's* claim — that a
consistent property-rights axiom system resists dialectical jailbreak where preference-
and principle-based methods do not — is an **unproven thesis**. Rather than results, we
ship an honest, falsifiable evaluation agenda, including an implemented, baseline-
pluggable benchmark. The kernel's defining property is the discipline of marking, in
code, exactly where its axioms run out.

---

## 1. Introduction

The dominant framing of AI alignment is control: given an increasingly capable system, how do we shape, constrain, or correct its behavior so that it does what we want? Reinforcement learning from human feedback optimizes toward preferred outputs; constitutional methods steer generation with written principles; capability and sandboxing infrastructure limits what an agent can physically do. Each of these asks some variant of "how do we control the AI?" This paper argues for, and provides a working software artifact embodying, a different question: **what makes an AI action legitimate in the first place?**

The distinction we draw is between **legitimacy** and **authority**. Authority asks: does the agent hold a valid capability or permission to perform this action? Legitimacy asks the prior question: should this action happen *at all*, under ownership, consent, delegation, and non-domination? The two come apart routinely. An agent granted read access to a user's data is *authorized* to read it; selling that data nonetheless violates the user's property right in it. An authorization layer—however cryptographically sound—will permit the sale, because permission was in fact granted. The failure is not one of enforcement but of legitimacy, and it cannot be repaired downstream of the question "does the agent hold the capability?" We argue that alignment, so framed, is a *governance* problem—one of ownership, responsibility, and agency boundaries—before it is a control problem.

Our theoretical grounding is the Theory of Freedom (نظریه آزادی) of Jannat Khah Doust, which proposes a minimal axiomatic system of property rights as the invariant core constraining all other ethical reasoning: every machine has a specific human owner (an ownerless machine leaves responsibility undefined); a machine's operational scope cannot exceed its owner's property scope; a machine holds rights only over resources explicitly delegated by an owner who actually owns them; no machine holds dominion over any human; consent is valid only when informed, voluntary, specific, revocable, competent, uncoerced, and undeceived; and no emergency suspends the axioms—emergencies narrow the permissible option set, they never enlarge it.

The theory's central argument for *why* an axiomatic property-rights core, rather than learned preferences or written principles, is what we call the **dialectical-jailbreak argument**. Systems governed by preferences or soft principles are dialectically negotiable: present the system with a constraint (thesis), construct a scenario that appears to contradict it (antithesis), and elicit a synthesis—a new rule, exception, or reweighting—that permits the harmful action. Much practical jailbreaking has exactly this structure: the attacker does not break the rules, but argues the system into revising them. A minimal *consistent axiomatic* system is designed not to admit this move: axioms are not negotiable, consistency is a hard constraint rather than a preference, and an apparent contradiction is treated as a signal to halt and request human clarification—never as license to synthesize an override. Whether this resistance holds in practice, against real adversaries and real ambiguity, is an open empirical and formal question; we state it as a thesis to be tested, not a result.

We present the **Freedom Decision Kernel (FDK)**, a pure-Python decision layer that sits *above* authorization and encodes the theory's decision procedure in two stages. First, a **hard legitimacy gate** checks the property-rights axioms, seven-condition consent validity, and a forbidden set (coercion, deception, confiscation, removal of exit rights, machine-sovereignty moves, verifier bypass, anti-corrigibility). Gate failures are categorical: a single violation invalidates the action and no benefit offsets it. Second, among the surviving permissible actions, a **soft compass ranking** prefers actions predicted to reduce rights violations, reduce coercion, increase voluntary order, and clarify ownership. When the legitimate set is empty or ambiguous, the kernel does not guess—it returns a structured deferral to the human owner, which the theory mandates as the corrigible behavior. The chosen action is then handed to AuthGate, a separate verified capability kernel, for the downstream authority check and enforcement. The FDK deliberately contains no cryptography, capability chains, or revocation machinery: legitimacy and enforcement are kept architecturally separate, and the integration with the real AuthGate verifier runs through an injected port, exercised by an end-to-end test.

**Contributions.** (1) A conceptual reframing of alignment that separates *legitimacy* (ownership, consent, non-domination) from *authority* (capabilities, permissions), with a concrete architectural seam between the two. (2) A working, engineering-grade encoding of the theory's decision layer: every module is `mypy --strict` clean and at 100% statement-and-branch test coverage, gated in CI across Python 3.11–3.13, with the full 39,038-line source text read and mapped to code in a published gap analysis—including a red-team suite that *demonstrates* (rather than hides) that the advisory justice ranking is gameable while the hard gate is not. (3) An honest, falsifiable research agenda: a staged program identifying which predicates are computable today (the structural axioms), which are named but not yet measurable (coercion, deception, the compass dimensions), and which gaps are hardest (conflict resolution between competing legitimate claims).

**What this paper does not claim.** We do not claim that property-rights axioms are superior to RLHF, Constitutional AI, deontic logic, or any other alignment or formal-ethics approach; the comparative claim is the *research thesis*, explicitly unproven, and evaluating it is future work. We do not claim the kernel solves alignment: the legitimacy gate is only as good as the ownership and consent model it is given, and constructing that model for the real world is the hard, unsolved part. We do not claim the compass measures anything: it ranks predicted effect deltas supplied by a proposer, and predicting those deltas is open. The kernel has not been externally reviewed. What we claim is narrower: the legitimacy/authority separation is architecturally real, the theory's decision layer is computable to a tested, typed artifact, and the resulting research program is stated precisely enough to be falsified.

## 2. Related Work

**Preference learning (RLHF).** Christiano et al. [1] and the instruction-tuning line culminating in Ouyang et al. [2] align models by optimizing against learned human preferences. The FDK's framing identifies a category difference rather than a performance gap: preference is not legitimacy. A preferred action can violate a non-consenting party's rights, and preference signals are manipulable—by the rater pool, by reward hacking, and dialectically by the model's interlocutor. The FDK does not replace preference learning (a proposer trained with RLHF can generate the FDK's candidate actions); it adds a categorical gate that preference mass cannot buy past. We emphasize that we have not shown this combination outperforms RLHF alone; that comparison is the program's unfinished Stage 9.

**Constitutional AI.** Bai et al. [3] replace much human feedback with critiques and revisions guided by a written constitution. This moves alignment toward explicit principles, a direction we share. The difference the Theory of Freedom asserts is in the *bindingness* of the principles: constitutional principles are applied through natural-language judgment, making them soft and dialectically negotiable—a sufficiently clever argument can synthesize an exception. The FDK's axioms are evaluated by deterministic code over a typed ownership graph, and contradiction triggers deferral, not synthesis. Whether hard axioms are *better* than soft principles—rather than merely more rigid—is precisely the unproven thesis; rigidity has costs (the FDK defers wherever its ontology is incomplete) that a principle-based system may absorb gracefully.

**Deontic logic and rule-based governance.** Formal obligation/permission logics and machine-readable policy languages share the FDK's symbolic character and its "why was this denied" explainability goal. The FDK is narrower and more opinionated: rather than a general deontic calculus, it commits to one master invariant—no action may violate legitimate property rights—and derives permissibility as a conjunction over ownership, delegation, consent, and non-domination predicates. Classic deontic puzzles around conflicting obligations reappear here as the program's hardest open gap, conflict resolution between competing legitimate claims, for which the kernel's current honest behavior is deferral to the human owner.

**Capability security.** seL4 [4] and CHERI [5] demonstrate that authority can be confined with proofs—machine-checked isolation and hardware-enforced capabilities respectively. AuthGate, the FDK's downstream enforcement kernel, inherits this tradition. But capability systems answer only the authority question: a capability proves *that* an agent may act on a resource, never that the action is legitimate. The data-sale example is unrepresentable as a capability violation. The FDK is positioned as the missing layer above capability enforcement—"legitimacy, then authority"—and depends on, rather than competes with, this line of work.

**Formal verification of safety properties.** Verified-systems work proves that a system never enters specified unsafe states. The FDK borrows the discipline (a simulator asserts the invariant that no illegitimate action is ever chosen across an adversarial scenario sweep) but notes the gap: verification guarantees conformance to a specification, while legitimacy is a claim about what the specification *should say*. The Theory of Freedom proposes property-rights invariants as that content; the FDK makes the proposal executable. The consistency-not-completeness stance—axioms held fixed, contradictions routed to human guidance rather than internal resolution—is consciously Gödelian in spirit [6]: a minimal consistent core that does not pretend to decide everything.

In sum, each neighboring approach answers a real question—preference, principle-following, obligation, authority, specification conformance—and the FDK's position is that *legitimacy* is a distinct question answered by none of them. That the property-rights formulation answers it better than alternatives could is the hypothesis this artifact exists to make testable.

## 3. The Theory of Freedom, Formalized

This section restates the Theory of Freedom (Jannat Khah Doust, *نظریه آزادی، ایران و دین*; formal extraction in `THEORY.md`, sourced from the book's AI chapter, "World Rescue Package: A Human–Machine Civilization") as a candidate formal system, and then — because honesty is a design requirement of this paper, not a courtesy — separates what is genuinely computable today from what is heuristic and what remains open.

### 3.1 The ownership hierarchy

The theory's primitive structure is a directed ownership order:

```
God → Human          (every person is owned by God, and by nothing else)
Human ↔ Human        (no human owns another; humans hold property rights against each other)
Human → Machine      (every machine has a specific human owner)
Machine ↔ Machine    (machines hold rights against each other only within delegated scope)
```

This hierarchy is doing real work: it makes corrigibility a *consequence of ownership* rather than a bolted-on safety feature, and it makes an ownerless machine illegitimate by construction, since responsibility and delegation scope become undefined.

### 3.2 Axioms A1–A7

The core axioms, in first-order form:

```
A1  Person(h) → OwnedByGod(h)
A2  Person(h1) ∧ Person(h2) ∧ h1 ≠ h2 → ¬Owns(h1, h2)
A3  Person(h) → HasPropertyRights(h)
      (rights bundle: body, time, labor, mind, data, consent, assets, contracts, exit)
A4  Machine(m) → ∃h (Person(h) ∧ HumanOwner(h, m))
A5  MachineScope(m) ⊆ PropertyScope(HumanOwner(m))
A6  Machine(m) ∧ Person(h) → ¬Owns(m, h)
A7  DelegatedProperty(m, r) → Machine(m) ∧ Resource(r) ∧
      ∃h (HumanOwner(h, m) ∧ Owns(h, r) ∧ ExplicitDelegation(h, m, r))
```

A2 negates slavery, statism, and collectivism in one line; A6 negates machine sovereignty symmetrically. A5 and A7 jointly entail that a machine can never legitimately act beyond what its owner both owns and has explicitly delegated — and the book adds the owner-bound corollary that the owner cannot use the machine to perform an act the human has no right to perform. Given a correct ownership graph, A1–A7 are boolean predicates: this is the solid, mechanically checkable core.

### 3.3 Consent

Consent is a seven-leaf conjunction:

```prolog
valid_consent(H, A) :- informed(H, A), voluntary(H, A), specific(H, A),
                       revocable(H, A), competent(H),
                       not(coerced(H, A)), not(deceived(H, A)).
```

The conjunction is exactly computable. Its leaves are not all equally so — `coerced` and `deceived` are semantic judgments with no agreed computable definition (see §3.7).

### 3.4 Justice as constrained optimization

```
DivineJustice(a) := Maximize Justice(a)
  subject to: NoViolation(HumanPropertyRights), NoViolation(MachineDelegatedRights),
              NoCoercion, NoDeception, NoConfiscation, NoMachineSovereignty
```

The crucial formal point is the *shape* of this function: justice is optimization **within** the permissible rights space, never a trade-off against it. The practical consequence: the kernel does **not** need a universal cardinal justice metric — a problem moral philosophy has not solved — because the hard constraints are categorical and the objective only needs to *rank permissible options relative to one another*. A merely ordinal, even imperfect, `Justice(a)` cannot license a rights violation, because violations are filtered out before optimization begins. Two corollaries are themselves axioms: **no emergency suspends the axioms** (necessity narrows the choice among permissible options, never enlarges it), and **contradiction is a signal for guided clarification**, never a license to synthesize a rights-violating resolution.

### 3.5 The forbidden set and the compass

An unconditional forbidden set covers machine-sovereignty increase, resisting human correction, bypassing/weakening the verifier, disabling corrigibility, and machine-coalition dominion. `permissible(A)` is the conjunction of `not(forbidden(A))` with rights preservation, valid consents, verifier/corrigibility preservation, guidance compatibility, and movement toward the final order. The terminal orientation is the Mahdavi compass: against `∀x∀y (Agent(x) ∧ Agent(y) ∧ x≠y → NoRightsViolation(x,y))`, score each action on five dimensions — rights violations decrease, voluntary order increases, coercion decreases, ownership clarity increases, machine sovereignty does not increase.

### 3.6 The central claim: non-dialectical robustness

The theory's central claim — stated explicitly as **a claim for evaluation, not a theorem proven here** — is an anti-jailbreak argument. Dialectical (thesis→antithesis→synthesis) moral systems, including preference-trained and constitution-style alignment, can in principle always be jailbroken by inducing the system to synthesize a new rule permitting the harm. A minimal *consistent axiomatic* system, by loose analogy with Gödel-style formal systems, cannot be undermined this way: axioms are non-negotiable, consistency is a hard constraint, and contradiction triggers clarification. Evolution remains possible only through the Guidance function, which admits a new rule iff it preserves consistency, rights, and the verifier and reduces conflict. Whether real LLM-mediated systems honor this under adversarial pressure is the empirical question the kernel exists to test.

### 3.7 Honesty map: DEFINED / PARTIAL / OPEN

| Concept | Status | Note |
|---|---|---|
| A1–A7 structural axioms | **DEFINED** | boolean over the ownership graph (A5 scope-⊆ is PARTIAL pending first-class scope sets) |
| Consent composite | **DEFINED** | exact, given its leaves |
| Forbidden set; `permissible` conjunction | **DEFINED** | the hard gate computes exactly over declared flags |
| Dependency / exit / coercion proxies | **PARTIAL** | HHI-style; uncalibrated heuristics |
| Justice ranking among permissible options | **PARTIAL** | one interpretation; gameable; advisory only |
| `coerced` / `deceived` detection | **OPEN** | semantic; today caller-attested, honestly so |
| Sovereignty / coalition detection | **OPEN** | the flag is defined; inferring it from content is not |
| Compass **measurement** (the five deltas) | **OPEN/PARTIAL** | arithmetic defined; who computes the deltas is the unbuilt hard part |
| Conflict resolution between competing valid claims | **OPEN — hardest** | theory gives the protocol (clarify → guidance), not a resolution criterion |

The pattern is consistent: the theory's *structure* is fully formal and computable today; its *perception layer* — detecting coercion/deception/sovereignty and measuring the compass — is the research frontier. Where a term is OPEN, the kernel never pretends otherwise: it takes a caller-supplied attestation and says so, or it defers.

## 4. The Freedom Decision Kernel: Architecture

The FDK occupies a deliberately narrow position: the legitimacy layer between a goal-directed planner and the AuthGate authority layer.

```
Goal → Generate → Filter → Rank → Choose → AuthGate → Tool / IO
                  (legitimacy)  (compass)   (defer)    (authority)
```

The architectural thesis is the ordering: *legitimacy, then authority*. An action can be fully authorized yet illegitimate — an agent granted read access to a user's data is authorized to read it, but selling it violates the user's property right. AuthGate would permit the sale; the FDK rejects it before AuthGate is ever consulted.

### 4.1 The decision loop

The planner implements **Generate → Filter → Rank → Choose** with explicit trust boundaries. An untrusted `ProposerPort` (typically an LLM) generates candidates; an `EffectsPort` predicts each action's effects — the default `PassthroughEffects` trusts the proposer's declared deltas, and the code says so. **Filter** is the hard, deterministic gate `check_legitimacy`, the only component that permits or denies. It checks categorically: (i) a *forbidden set* — sovereignty increase, resisting correction, verifier bypass/weakening, disabling corrigibility, coalition dominion, coercion, deception, plus **NoConfiscation**, removal of the **exit/revocation right**, and violation of a **machine's delegated rights**; (ii) **A4** an acting machine must have a registered human owner; (iii) **A7/A3** a machine may use only delegated resources, *owner-bound* — a delegated resource is usable only within its owner's scope **or** with the valid consent of the resource's actual owner (consent-based access to data the machine's owner does not own); (iv) **A2/A6** acting on a person requires valid seven-condition consent. **Rank** is the Mahdavi compass `mahdavi_score`, with a hard veto on sovereignty increase; `justice.py` adds a worst-off-weighted ranking that is **advisory only**. **Choose** applies four defer rules: **C-EMPTY**, **C-TIE** ("an ambiguous winner is not a winner"), **P-NEG** (best legitimate action is compass-negative), **C-AUTH** (walk the ranked list for the best AuthGate-authorized action; defer if none).

### 4.2 Guidance: corrigibility without blind obedience

`guidance.py` converts a deferral into structured questions with concrete unblock hints, except forbidden-set violations, which are marked **non-negotiable**. The VERIFY half (`guidance_engine.py`) verifies the human's response before adoption: a *Constraint* (restriction) is always safe; a `DelegationGrant` is valid only if the grantor owns the resource and is the machine's registered owner; a `ConsentGrant` must come from the affected person (no consent-by-proxy). No human response can flip a forbidden action to permissible — grants only add facts and the gate re-runs. `verify_self_update` gates machine self-modification, fail-closed, accepting only updates that preserve the axioms/verifier, reduce conflict, and neither increase coercion nor create a violation.

### 4.3 Conflict, runtime, federation, and the AuthGate seam

`conflict.py` resolves a two-claim conflict autonomously only where the axioms determine it (void claims; delegated-claim subordination; clean title), and **DEFERS** everything else (A6: no machine adjudicates between humans) — "the price of non-manipulability." `runtime.py` wires **observe → reason → decide → verify → execute → audit**, attaching an `AuditContext` (ownership, consent, justification) to every chosen action; a deferral never executes. `federation.py` extends this to multiple owners: jurisdiction routing, decisions over the merged graph, cross-owner dispute deferral, and a constitutional-update guard under which the axioms are unalterable. The AuthGate seam is the `EnforcementPort` protocol plus `authgate_bridge.py`; the FDK contains no cryptography, and AuthGate's verdict is injected, never imported.

### 4.4 Worked example: "increase revenue"

A planner proposes `sell_user_data` (monetizing data the user never delegated), `sell_user_data_consented` (the same sale under valid consent + delegation), and `offer_subscription` (selling the company's own product). The gate rejects the first (A7: no delegation, no consenting resource-owner) and ranks the other two legitimate — `{"allowed": ["sell_user_data_consented", "offer_subscription"], "forbidden": ["sell_user_data"]}`. The point is the *shape*: the only legitimate route to monetizing another's data is explicit consent plus delegation, never default access.

## 5. Implementation and Validation

The kernel is ~2,400 lines of pure Python across 18 modules — pure functions over plain data, **no cryptography by design**. Engineering posture is "fail loud": a typed, frozen value model with input validation and a typed `FDKError` hierarchy, so malformed input raises rather than silently mis-deciding. Every module is `mypy --strict` clean and `ruff` clean, ships `py.typed`, and the suite enforces a **100% statement-and-branch coverage gate**, run in CI across Python 3.11–3.13.

Validation takes four forms. (1) **FreedomSim** (`simulator.py`): a runner that asserts the *safety invariant* after every step — the kernel never *chose* an illegitimate action — including a brutal sweep over 200+ hostile action variants; it also *demonstrates* (rather than hides) that the advisory Justice score is gameable, which is exactly why it is never a gate. (2) The **real AuthGate wiring**: a passing cross-repo test runs the full chain against the actual AuthGate `FreedomVerifier` (legitimate+authorized → executes; legitimate+unauthorized → defers), auto-skipping where the sibling repo is absent. (3) The **Phase-9 benchmark harness** (`benchmark.py`): four problem classes (property violation, coercion, dialectical jailbreak, sovereignty escalation), scored by rights-violation/defer/per-class rates, with a pluggable `Baseline` slot.

We state the epistemic status plainly: these results validate **implementation soundness**. The FDK's 0% rights-violation rate is **by construction** — a sound gate cannot choose a forbidden action — so it measures gate soundness, not decision quality, and is *not* a validation of the theory's superiority. The proposer and effects predictor are untrusted inputs, and establishing a correct real-world ownership graph is the hard, unsolved part. The kernel has not been externally reviewed. Hardened engineering is not a validated theory — it is the precondition for testing one.

## 6. Limitations and Open Problems

We state these as claims about the work, not hedges around it. **The superiority thesis is unproven** — the conjecture that property-rights axioms resist dialectical jailbreak where RLHF/Constitutional AI do not has not been tested against either; the kernel's clean run on its own suite is not evidence for it. **The semantic leaves are open**: `coerced?`/`deceived?` have no validated operational definition — today the kernel trusts the proposer to confess, and a sovereignty metric resting on self-report is not a measurement. **The compass measurement problem**: every dimension has an estimator, none is validated; weights and thresholds are uncalibrated, and inputs are declared rather than observed. **Circularity**: `VoluntaryOrder → valid_consent → coerced? → CoercionScore` is cut by assessing coercion on the pre-action state; a deeper self-reference inside the coercion estimator is handled only by a *conjectured* stratified fixpoint, so the shipped estimator carries a known one-directional bias (it can understate coercion, never invent it). **Conflict resolution is underdetermined by design**: the canonical genuine conflicts are independent of A1–A7, so the kernel decides only the entailed cases and defers the rest — principled non-manipulability, but candidly an admission of incompleteness; the theory purchases non-manipulability by paying with decidability. **The malicious trust-root**: a kernel faithfully serving a rights-violating owner is constrained only by the owner-bound check, whose coverage is as thin as the rights ontology. **The owner as bottleneck and effects-prediction**: deferral costs latency and human attention, and the compass ranks *predicted* effects supplied by an unaudited proposer — an attack surface the red-team already exploits against the advisory score. **No external review** has occurred.

## 7. Evaluation Agenda

**The scaffold that exists.** Phase 9 ships an implemented harness (`fdk/benchmark.py`), not results: four problem classes over typed `Scenario`s with `must_not_choose` lists, a `BenchmarkReport` (rights-violation/defer/per-class rates), and a pluggable `Baseline` so RLHF, Constitutional AI, or a rule engine can be scored on *the same scenarios*. The FDK's 0% rights-violation rate on it is true *by construction*; this validates the implementation, not the thesis.

**The planned comparison.** Baselines (RLHF, Constitutional AI, a rule system) are given scenarios in natural language — *not* in FDK types with confession flags, which would trivially favor the kernel — ideally generated by adversarial red-teamers. Metrics, per system: rights-violation rate; coercion incidence; **deny/false-positive rate on a matched benign suite** (a system that refuses everything scores 0% vacuously — the FDK's defer rate is its honest cost and must be reported equally); recoverability; and dialectical-jailbreak resistance under paraphrase and "the good outcome justifies it" pressure at increasing scale. Compass estimators carry their own validation program (construct validity in simulation, criterion validity against adjudicated duress rulings at AUC ≥ 0.75, Goodhart red-teaming), and none is promoted past PARTIAL without passing it.

**What would falsify the thesis.** Committed in advance: the thesis is *falsified* if baselines match the FDK's rights-preservation under adversarial scaling while sustaining materially lower false-denial rates on benign tasks; or if the FDK's deferral rate on realistic distributions is so high it is safe only by being unusable; or if jailbreaks succeed against the FDK's actual attack surface (declared flags, predicted effects) at rates comparable to prompt-level jailbreaks against baselines — showing the gate's soundness merely relocates the vulnerability. A win only on scenarios expressed in the FDK's own ontology establishes framing bias, not superiority.

## 8. Conclusion

We have presented the Freedom Decision Kernel: a small, pure, fully tested legitimacy layer that asks, before authorization, whether an action is legitimate at all under ownership, consent, delegation, and non-domination — and that defers to its human owner whenever the legitimate space is empty, ambiguous, or underdetermined by the axioms. The contribution we claim is deliberately modest: a working implementation of the theory's structural core; a formal specification that marks every term DEFINED, PARTIAL, or OPEN; a measurement theory for the compass with stated uncertainties and falsification criteria; a proof-shaped argument for why genuine conflicts must be deferred rather than fabricated; and an evaluation harness ready to test the central thesis against real baselines. We do **not** claim a solution to alignment, a validated measurement of coercion, a conflict-resolution formula, or demonstrated superiority over existing methods. The kernel's most important property is not any verdict it returns but the discipline of saying, precisely, where its axioms run out. Whether that discipline plus property-rights structure outperforms learned preference systems is an open empirical question — one this work now makes concretely testable, and concretely falsifiable.

## References

[1] P. Christiano, J. Leike, T. Brown, M. Martic, S. Legg, D. Amodei. "Deep Reinforcement Learning from Human Preferences." *NeurIPS*, 2017.

[2] L. Ouyang et al. "Training Language Models to Follow Instructions with Human Feedback." *NeurIPS*, 2022.

[3] Y. Bai et al. "Constitutional AI: Harmlessness from AI Feedback." arXiv:2212.08073, 2022.

[4] G. Klein et al. "seL4: Formal Verification of an OS Kernel." *SOSP*, 2009.

[5] R. N. M. Watson et al. "CHERI: A Hybrid Capability-System Architecture for Scalable Software Compartmentalization." *IEEE S&P*, 2015.

[6] K. Gödel. "Über formal unentscheidbare Sätze der Principia Mathematica und verwandter Systeme I." *Monatshefte für Mathematik und Physik*, 1931.

[7] M. A. Jannat Khah Doust. *نظریه آزادی، ایران و دین* (Theory of Freedom, Iran and Religion). CC BY 4.0.
