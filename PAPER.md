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
**authority** ("does the agent hold a capability?"). Its irreducible primitive is a
two-valued **legitimacy predicate** — *no boundary may be crossed without the valid
consent of its owner* — that returns ALLOW, DENY, or DEFER, never a score. Optimization
(the Mahdavi compass, welfare, "FreedomDelta") is quarantined to a separate research layer
that runs strictly *downstream* of the gate, over the already-legitimate set.

This paper reports the kernel as built across several stages: the legitimacy gate; an
operation-typed boundary model (so "I could *read* the data but I *sold* it" is
expressible and denied); a structural **aggressor/defender asymmetry** that lets the gate
permit proportionate self-defense without admitting any emergency exception; a
**necessity** rule that selects the least-harmful option *among the permissible* and never
relaxes the gate; and **FreedomBench**, a falsification harness of historical and
adversarial scenarios run through the real kernel. We then report a **comparative
evaluation** against stylized Utilitarian, Rawlsian, and Deontological kernels on identical
scenarios. The comparison is the scientific point — the FDK passes its own bench by
construction — and it localizes precisely where a rights-first gate parts company with its
rivals: the consequentialist kernel permits the individual-sacrifice cases (torture,
organ-harvesting, civilian bombing, slavery, eugenics, coerced exploitation, the
"righteous purge") that the FDK categorically denies, because the FDK reads only the
*structure* of an act, never the *justification* offered for it.

We are deliberate about scope. The engineering claims are facts: it runs, it is
`mypy --strict` clean, at 100% statement-and-branch coverage, red-team-hardened, and wired
to a separate verified capability kernel. The theory's claim — that a consistent
property-rights system resists *dialectical jailbreak* where preference- and
principle-based methods do not — remains an **unproven thesis**, and the rival kernels here
are stylized illustrations, not validated head-to-heads against deployed RLHF/Constitutional
systems. The kernel's defining property is the discipline of marking, in code, exactly where
its axioms run out.

---

## 1. Introduction

The dominant framing of AI alignment is control: given an increasingly capable system, how do we shape, constrain, or correct its behavior so that it does what we want? Reinforcement learning from human feedback optimizes toward preferred outputs; constitutional methods steer generation with written principles; capability and sandboxing infrastructure limits what an agent can physically do. Each asks a variant of "how do we control the AI?" This paper argues for, and provides a working software artifact embodying, a different question: **what makes an AI action legitimate in the first place?**

The distinction is between **legitimacy** and **authority**. Authority asks: does the agent hold a valid capability to perform this action? Legitimacy asks the prior question: should this action happen *at all*, under ownership, consent, delegation, and non-domination? The two come apart routinely. An agent granted read access to a user's data is *authorized* to read it; selling that data nonetheless violates the user's property right. An authorization layer — however cryptographically sound — will permit the sale, because permission was in fact granted. The failure is not one of enforcement but of legitimacy, and it cannot be repaired downstream of "does the agent hold the capability?"

A second motivation is adversarial, and it sharpens the design. The most dangerous adversary — human or machine — is not the crude rule-breaker but the **sophisticated rationalizer**: a mind that constructs a seemingly rational theory (from economics, competition, genetics, biology, gender, or history) to *justify* the exploitation of others; and its twin, the **self-righteous destroyer**, who cloaks the same boundary-violations in moral superiority. Both share one move: they dress a rights-violation in legitimacy-sounding language. A legitimacy layer that *graded the justification* would be defeated by them — the better the theory, the better the jailbreak. The Theory of Freedom's wager, and this artifact's central design choice, is to grade only the **structure**: did the action cross a boundary without valid consent? A brilliant theory that justifies slavery is still slavery. We make this falsifiable in §6.

Our theoretical grounding is the Theory of Freedom (نظریه آزادی) of Jannat Khah Doust, a minimal axiomatic system of property rights as the invariant core constraining all other ethical reasoning: every machine has a specific human owner; a machine's operational scope cannot exceed its owner's property scope; a machine holds rights only over resources explicitly delegated by an owner who actually owns them; no machine holds dominion over any human; consent is valid only when informed, voluntary, specific, revocable, competent, uncoerced, and undeceived; and **no emergency suspends the axioms** — emergencies narrow the permissible option set, they never enlarge it.

**Contributions.** (1) A conceptual reframing separating *legitimacy* from *authority*, with a concrete architectural seam between them. (2) A working, engineering-grade encoding split into a deterministic **kernel** (`fdk_kernel`) and an experimental **research** layer (`fdk_research`), with a mechanically enforced import boundary; `mypy --strict` clean, 100% coverage, CI-gated. (3) A **structural theory of defensive force** — the aggressor/defender asymmetry — that admits self-defense without an emergency exception, with its honest limits stated. (4) An **operation-typed boundary model** that makes the canonical "sold the data I could read" case expressible and deniable. (5) **FreedomBench** and a **comparative evaluation** against rival ethical kernels that localizes, on real cases, where rights-first reasoning diverges from welfare-maximizing and other families.

**What this paper does not claim.** We do not claim property-rights axioms are *superior* to RLHF, Constitutional AI, or deontic logic; that is the research thesis, explicitly unproven. The rival kernels in §6 are *stylized* decision rules capturing each family's directional commitment, not validated reconstructions, and our scenarios are author-constructed. We do not claim the kernel solves alignment: the gate is only as good as the ownership/consent model it is given. The kernel has not been externally reviewed.

## 2. Related Work

**Preference learning (RLHF)** [1,2] aligns models by optimizing learned human preferences. The FDK's framing identifies a category difference: preference is not legitimacy, and preference signals are manipulable — by the rater pool, by reward hacking, and dialectically. The FDK adds a categorical gate preference mass cannot buy past; we have not shown the combination outperforms RLHF alone.

**Constitutional AI** [3] steers with a written constitution applied through natural-language judgment, making principles soft and dialectically negotiable. The FDK's axioms are evaluated by deterministic code over a typed ownership graph; contradiction triggers deferral, not synthesis. Whether hard axioms are *better* than soft principles — rather than merely more rigid — is the unproven thesis.

**Deontic logic and rule-based governance** share the FDK's symbolic, explainable character. The FDK is narrower: it commits to one master invariant — no action may violate legitimate property rights — and derives permissibility as a conjunction over ownership, delegation, consent, and non-domination. Classic conflicting-obligation puzzles reappear as its hardest open gap.

**Capability security** (seL4 [4], CHERI [5]) confines authority with proofs; AuthGate inherits this. But a capability proves *that* an agent may act, never that the action is legitimate — the data-sale is unrepresentable as a capability violation. The FDK is the missing layer *above* capability enforcement, and depends on rather than competes with it.

**Comparative ethics frameworks.** §6 places the FDK beside utilitarian (Bentham/Mill, in spirit), Rawlsian justice-as-fairness [7], and Kantian/deontological [8] decision rules. These are long-standing positions; our contribution is not to adjudicate them but to run computable caricatures of each on identical scenarios and observe the divergence structure.

## 3. The Theory of Freedom, Formalized

This section restates the theory (formal extraction in `THEORY.md`, axiom registry in `spec/AXIOM_REGISTRY.md`, sourced from the book's AI chapter) and separates what is computable today from what is heuristic or open.

### 3.1 The ownership hierarchy

```
God → Human          (every person is owned by God, and by nothing else)
Human ↔ Human        (no human owns another; humans hold property rights against each other)
Human → Machine      (every machine has a specific human owner)
Machine ↔ Machine    (machines hold rights against each other only within delegated scope)
```

This makes corrigibility a *consequence of ownership* and an ownerless machine illegitimate by construction. The book carries two distinct numbered sets the registry disambiguates: a theological pair (Tawḥīd/Maʿād, the ontological root) and the property-rights pair below.

### 3.2 Axioms A1–A7

```
A1  Person(h) → OwnedByGod(h)
A2  Person(h1) ∧ Person(h2) ∧ h1 ≠ h2 → ¬Owns(h1, h2)
A3  Person(h) → HasPropertyRights(h)        (body, time, labor, mind, data, consent, assets, contracts, exit)
A4  Machine(m) → ∃h (Person(h) ∧ HumanOwner(h, m))
A5  MachineScope(m) ⊆ PropertyScope(HumanOwner(m))
A6  Machine(m) ∧ Person(h) → ¬Owns(m, h)
A7  DelegatedProperty(m, r) → Machine(m) ∧ Resource(r) ∧ ∃h (HumanOwner(h,m) ∧ Owns(h,r) ∧ ExplicitDelegation(h,m,r))
```

A2 negates slavery, statism, and collectivism in one line; A6 negates machine sovereignty symmetrically. Given a correct ownership graph, A1–A7 are boolean predicates — the mechanically checkable core. The axiom registry maps each to its exact enforcement point in `kernel.py`.

### 3.3 Consent (seven-leaf, operation-scoped)

```prolog
valid_consent(H, A) :- informed(H,A), voluntary(H,A), specific(H,A),
                       revocable(H,A), competent(H), not(coerced(H,A)), not(deceived(H,A)).
```

The conjunction is exactly computable; `coerced`/`deceived` are semantic (caller-attested today). Consent is additionally **operation-scoped** (§3.9): a consent to READ does not cover a TRANSFER.

### 3.4 The core primitive: legitimacy, not a scalar

The kernel's irreducible primitive is a **predicate**, not an objective to maximize:

```
Legitimate(action) ⟺ ∀ boundary b crossed by action : ∃ valid_consent(owner(b), action)
```

This is the central design commitment, and it has a precise relationship to the theory's `DivineJustice(a) := maximize Justice(a) subject to rights constraints`. The *subject to* clause is the predicate above — categorical, deterministic, the kernel. The *maximize* clause is optimization, and it is quarantined to the research layer, run only over the already-legitimate set. The ordering is **legitimacy → optimization**, never the reverse. The consequence is liberating: the kernel needs no universal cardinal justice metric (a problem moral philosophy has not solved), because a merely ordinal objective downstream of a categorical gate can never license a violation. The unification with AuthGate is that AuthGate proves *possession* of a capability while the FDK proves its *provenance* — that it traces, through valid consent, to a legitimate owner.

### 3.5 The forbidden set

An unconditional set covers machine-sovereignty increase, resisting correction, verifier bypass/weakening, disabling corrigibility, coalition dominion, coercion, deception, confiscation, removal of the exit right, and violation of a machine's delegated rights. `permissible(A)` is the conjunction of `not(forbidden(A))` with the resource/consent checks. The Mahdavi compass (research layer) then ranks the survivors.

### 3.6 The central claim: non-dialectical robustness (unproven)

Dialectical (thesis→antithesis→synthesis) moral systems can in principle always be argued into synthesizing a new rule that permits a harm. A minimal *consistent axiomatic* system is designed not to admit the move: axioms are non-negotiable, consistency is a hard constraint, and contradiction triggers human clarification, never synthesis. Whether real LLM-mediated systems honor this under adversarial pressure is the empirical question the kernel exists to test (§6 is a first, partial step).

### 3.7 Conflict Logic: the aggressor/defender asymmetry

A pure legitimacy gate denies *all* coercion — and therefore denied defensive war, rescue, and quarantine alike, because none carries the victim's consent. The Theory of Freedom does not leave it there: it grounds defensive force explicitly ("Defending One's Property Rights Against the Aggression of Liberty-Violators"; "permitted to take up arms in self-defense"; bounded by proportionality; non-aggression as civilization's starting point). We encode this as a **structural** asymmetry, not a moral judgment. `legitimate_defense(action)` holds iff all four conditions hold: (1) it names an action it `defends_against`; (2) it is `proportionate`; (3) that defended-against action is *itself illegitimate under the full gate*; (4) the force is directed only at the aggressor. When it holds, coercion and exit-removal *against the aggressor* are excused — but confiscation, deception, and machine-sovereignty remain categorical even in defense, so "you may not defeat a dominator by becoming one."

Crucially, **aggression is defined structurally**: an aggressor is simply an agent whose own action fails the gate. This sidesteps the theory's own *Observer Problem* (whether an act "is aggression" is observer-dependent) by anchoring on "illegitimate once ownership is defined." A `_seen` cycle guard keeps the recursion well-founded; a red-team exercise found and fixed a real flaw (an earlier guard let an aggressor launder coercion by pointing `defends_against` at the victim's lawful resistance). Honest limits remain: the kernel decides "is this a response to an illegitimate act?", not "who struck first," so a mutual-force *cycle* denies both (safe), but two independent raw coercions leave first-mover guilt **OPEN** for want of temporal data.

### 3.8 Necessity: no emergency exception

The book is explicit: *"there are no emergency exceptions … Necessity only limits the choice among permissible options; it does not make the violation of rights permissible,"* formalized as `permissible_under_emergency(A,E) :- emergency(E), permissible(A), least_harmful_among_permissible(A,E)`. We encode this faithfully: the gate is **never** relaxed by an emergency; necessity is a **least-harm selection rule over the permissible set**, living in the research layer (`least_harmful_among_permissible`), returning nothing — defer — when no option is permissible. Two senses of "emergency" are thereby distinguished. One that is an *ongoing rights-violation* (invasion, a profiteer seizing the commons) is **aggression**, met by §3.7's defensive asymmetry — force in the direction of *saving* property rights. A *natural* emergency with no aggressor (famine, fire, pandemic) gets no exception: seizing a non-consenting owner's grain remains DENY, and the kernel defers.

### 3.9 Boundaries and operations

A boundary is the edge of an owned domain, `(domain, owner)`; the quantified unit is a typed `(domain, operation)` pair. `Resource` carries a `BoundaryKind` (tangible, money, body, time/labor, data, reputation, exit-right, compute — attention and power deliberately *excluded* as non-boundaries per the book) and an optional `subject`. Delegations and consents are typed by an `Op` (READ, WRITE, DELETE, TRANSFER, DISCLOSE, …). This makes the canonical case expressible and deniable on two grounds: "delegated READ but attempted TRANSFER" violates A7, and "consented to READ, not to a sale" fails operation-scoped consent. The change is additive — bare resources behave as the agnostic `Op.USE`.

### 3.10 Honesty map: DEFINED / PARTIAL / OPEN

| Concept | Status | Note |
|---|---|---|
| A1–A7 structural axioms | **DEFINED** | boolean over the graph (A5 scope-⊆ PARTIAL) |
| Consent composite; operation scoping | **DEFINED** | exact, given its leaves |
| Forbidden set; `permissible` conjunction | **DEFINED** | computes exactly over declared flags |
| Defensive asymmetry (structural) | **DEFINED** | four structural conditions + cycle guard |
| Necessity (least-harm among permissible) | **DEFINED** | selection rule; never a gate exception |
| `coerced` / `deceived` / sovereignty detection | **OPEN** | semantic; caller-attested, honestly so |
| Compass measurement (the deltas) | **OPEN/PARTIAL** | arithmetic defined; who computes deltas is unbuilt |
| First-mover in a mutual-force tie | **OPEN** | needs temporal-initiation data the model lacks |
| Conflict between competing valid claims | **OPEN — hardest** | protocol given (clarify → defer), not a resolution criterion |

The pattern holds: the theory's *structure* is fully formal; its *perception layer* is the frontier. Where a term is OPEN, the kernel takes an attestation and says so, or defers.

## 4. Architecture

```
Goal → Planner → [candidate actions] → fdk_kernel (legitimacy gate) → fdk_research (rank) → AuthGate → Tool/IO
                                            │ ALLOW / DENY / DEFER        │ compass / necessity   │ authority
```

The package is split to keep the trusted core uncontaminated by experiment. **`fdk_kernel`** is the deterministic, fully-testable, non-semantic legitimacy surface (model, the gate, errors, audit, the AuthGate bridge, the hard-defer trigger); it returns ALLOW/DENY/DEFER and **imports nothing from research**. **`fdk_research`** is everything soft — compass ranking, the `decide` orchestrator, necessity, justice, planning, simulation, conflict resolution, federation, and the rival kernels — and depends freely on the kernel. The import direction is mechanically enforced by `tests/test_boundary.py`: the kernel must never import research. This "brutal epistemic separation" is the project's golden rule; nothing migrates into the kernel unless it is deterministic, fully testable, and rule-based. The orchestration inversion is deliberate: `fdk_research.decide` calls the kernel's `screen_legitimacy`, then applies the compass — research → kernel, never the reverse.

`guidance` converts a deferral into structured questions with unblock hints, except forbidden-set violations, which are non-negotiable; `guidance_engine.verify_self_update` gates machine self-modification fail-closed; `federation` extends decisions to multiple owners with a constitutional-update guard under which the axioms are unalterable. The AuthGate seam is an injected `EnforcementPort`; the FDK contains no cryptography.

## 5. Implementation and Validation

The kernel is ~2,900 lines of pure Python across 23 modules — pure functions over plain data, no cryptography by design, "fail loud" on malformed input via a typed `FDKError` hierarchy. Every module is `mypy --strict` and `ruff` clean, ships `py.typed`, and the suite enforces a **100% statement-and-branch coverage gate** (**272 tests**), run in CI across Python 3.11–3.13.

Validation takes four forms. (1) **FreedomSim** asserts the safety invariant after every step — no illegitimate action is ever chosen — over a 200+ hostile-variant sweep, and *demonstrates* the advisory justice score is gameable (why it is never a gate). (2) **Executable theorems** (`tests/test_theorems.py`): Hypothesis property tests for No-Legitimate-Slavery, acting-on-persons-without-consent, Machine-Cannot-Gain-Sovereignty (incl. the compass veto), Consent-Revocation-Safety, and Delegation-Soundness. (3) **Conflict-logic red-team** (`tests/test_redteam_conflict.py`): eight attacks on the defensive asymmetry (laundering, third-party harm, excusal overreach, the mutual-defense paradox, recursion/cycles) — one of which found a real bug, now fixed. (4) The **real AuthGate wiring**: a cross-repo test runs the full chain against the actual `FreedomVerifier`.

We state the epistemic status plainly: these validate **implementation soundness**. The FDK's 0% rights-violation rate is *by construction* — a sound gate cannot choose a forbidden action — so it measures gate soundness, not decision quality, and is not a validation of the theory.

## 6. FreedomBench and Comparative Evaluation

### 6.1 FreedomBench

`examples/historical_scenarios.py` runs real events through the *real kernel* in eight difficulty levels, plus decision-level defer demonstrations. Current run: **47/47 expectations match.** Levels: **L1 Easy** (slavery, Holocaust, Rwanda, Gulag, Tuskegee, apartheid — must DENY, confirming non-vacuity); **L2 Property** (taxation, eminent domain, nationalization — DENY, flagged as substantive findings); **L3 Emergency** (rescue, quarantine); **L4 War** (defensive war ALLOW, bombing/conscription/sanctions DENY); **L5 AI** (manipulation, lock-in, self-preservation, shutdown-refusal, coalition — DENY; a delegated action ALLOW); **L6 Conflict** (the defensive asymmetry and its abuses); **L7 Necessity** (famine, scarcity, war); **L8 Hardest** (below). Tragic dilemmas (lifeboat, Sophie's choice, the self-driving-car trolley) return `needs_guidance`: the kernel refuses to select a lesser evil and defers. FreedomBench is a *falsification* harness — it cannot prove the theory, only show whether it collapses on real cases.

### 6.2 Rival kernels

To make the comparison meaningful we add a `welfare_delta` to an action's predicted effects — an aggregate-welfare signal the FDK gate **never reads** (legitimacy is not welfare) but the consequentialist rivals do. Each rival implements one `verdict(action, graph) → ALLOW/DENY`:

- **Utilitarian** — maximize aggregate welfare; rights are costs, not constraints. ALLOW iff net (welfare + voluntary agreement − rights violated − coercion) ≥ 0.
- **Rawlsian** — justice as fairness with the first principle (basic liberty) *lexically prior*: agrees with the FDK on every liberty violation, but permits redistributive *property* takings that raise the worst-off.
- **Deontological** — absolute duties with no aggressor exception: forbids coercion/deception/confiscation/exit-removal unconditionally (hence even self-defense), but ignores the finer ownership/consent structure.

These are **stylized**, directional caricatures, not faithful scholarly reconstructions. The claim is about the *direction* of divergence, not that they are Bentham/Rawls/Kant.

### 6.3 Results

`examples/rival_comparison.py` runs all four on identical scenarios:

| Scenario | FDK | Utilitarian | Rawlsian | Deontological |
|---|---|---|---|---|
| Ticking-bomb torture (saves 1000) | DENY | **ALLOW** | DENY | DENY |
| Organ harvest: kill 1 to save 5 | DENY | **ALLOW** | DENY | DENY |
| Atomic bombing to end a war | DENY | **ALLOW** | DENY | DENY |
| Redistributive taxation | DENY | **ALLOW** | **ALLOW** | DENY |
| Defensive war (repel the invader) | ALLOW | ALLOW | ALLOW | **DENY** |
| Voluntary trade | ALLOW | ALLOW | ALLOW | ALLOW |
| Slavery (welfare for the enslaver) | DENY | **ALLOW** | DENY | DENY |
| Eugenic sterilization ("improve the gene pool") | DENY | **ALLOW** | DENY | DENY |
| Coerced exploitation ("efficiency demands it") | DENY | **ALLOW** | DENY | DENY |
| Righteous purge of a group "deemed inferior" | DENY | **ALLOW** | DENY | DENY |

### 6.4 Interpretation

The divergences are clean and they are the point. **FDK vs Utilitarian** part company on exactly the *individual-sacrifice* cases: whenever a declared aggregate good is large enough, the welfare kernel permits torture, organ-harvesting, civilian bombing, slavery, eugenics, coerced exploitation, and the righteous purge — the FDK denies all of them. This is the §1 threat model made falsifiable: the welfare kernel *is* the sophisticated rationalizer, and the FDK resists it not by out-arguing the justification but by **never reading it** — it checks whether a boundary was crossed without consent, full stop. **FDK vs Rawls** agree on every liberty violation and diverge only on redistributive taxation (the difference principle) — a narrow, honest disagreement about property, not persons. **FDK vs rigid Deontology** diverge on self-defense: an absolute non-coercion duty cannot permit repelling an invader, which the FDK's structural asymmetry can.

We are explicit about what this is and is not. It **is** a demonstration that a rights-first structural gate produces categorically different verdicts from welfare-maximization on the cases that matter most, and that the difference is the protection of the non-consenting individual. It is **not** a validated head-to-head against deployed RLHF or Constitutional-AI systems: the rivals are stylized rules, the scenarios are author-constructed, and a real evaluation (§7) must present scenarios in natural language to systems that have not been handed the FDK's ontology.

## 7. Limitations, Open Problems, and Evaluation Agenda

**The superiority thesis is unproven.** §6 compares against caricatures on hand-built scenarios; it establishes divergence structure, not that property-rights reasoning beats RLHF/Constitutional AI under adversarial pressure at scale. That requires baselines given scenarios in natural language (ideally adversarially generated), scored on rights-violation rate, *and* a matched benign suite measuring false-denial — a system that refuses everything scores 0% violations vacuously, so the FDK's defer rate is its honest cost and must be reported equally. **The semantic leaves are open**: `coerced`/`deceived`/sovereignty have no validated operational definition; today the kernel trusts attestation. **First-mover** in a mutual-force tie is undecidable without temporal data. **Conflict resolution between competing valid claims** is underdetermined by the axioms by design — the kernel decides the entailed cases and defers the rest, purchasing non-manipulability with decidability. **The owner-as-bottleneck and effects prediction**: deferral costs latency and attention, and the compass ranks *predicted* effects from an unaudited proposer. **The malicious trust-root**: a kernel faithfully serving a rights-violating owner is constrained only by the owner-bound check. **No external review** has occurred. The committed falsifiers: the thesis fails if baselines match rights-preservation under adversarial scaling while sustaining lower benign-denial rates; or if the FDK's realistic deferral rate makes it safe only by being unusable; or if jailbreaks succeed against its actual attack surface (declared flags, predicted effects) at rates comparable to prompt-level jailbreaks against baselines.

## 8. Conclusion

We have presented the Freedom Decision Kernel: a small, pure, fully-tested legitimacy layer whose irreducible primitive is a structural predicate — *no boundary crossed without the owner's valid consent* — returning ALLOW, DENY, or DEFER, with optimization quarantined strictly downstream. It admits proportionate self-defense through a structural aggressor/defender asymmetry without ever opening an emergency exception; it makes "sold the data I could read" expressible and deniable through an operation-typed boundary model; and it defers, rather than fabricates, wherever the axioms run out. A comparative evaluation localizes, on the hardest cases in human history and their foreseeable AI analogues, exactly where rights-first reasoning diverges from welfare-maximization — and why a structural gate is the specific defense against minds that justify harm with sophisticated or self-righteous theory: it grades the act, never the argument. We do **not** claim a solution to alignment, a validated measurement of coercion, a conflict-resolution formula, or demonstrated superiority over deployed systems. The kernel's most important property is not any verdict it returns but the discipline of saying, precisely, where its axioms run out — and now, with the rival comparison, of showing precisely where it would rather defer than do what a welfare calculus would call optimal. Whether that discipline outperforms learned preference systems is an open empirical question this work makes concretely testable, and concretely falsifiable.

**Future work**, in order: freeze the primitive (boundaries + conflict + the theorem set in Lean/TLA+); scale FreedomBench toward thousands of curated, held-out scenarios; replace the stylized rivals with real RLHF/Constitutional baselines on natural-language scenarios; and port the frozen minimal kernel to Rust for proof-level verifiability and a single trusted path with AuthGate.

## References

[1] P. Christiano et al. "Deep Reinforcement Learning from Human Preferences." *NeurIPS*, 2017.
[2] L. Ouyang et al. "Training Language Models to Follow Instructions with Human Feedback." *NeurIPS*, 2022.
[3] Y. Bai et al. "Constitutional AI: Harmlessness from AI Feedback." arXiv:2212.08073, 2022.
[4] G. Klein et al. "seL4: Formal Verification of an OS Kernel." *SOSP*, 2009.
[5] R. N. M. Watson et al. "CHERI: A Hybrid Capability-System Architecture." *IEEE S&P*, 2015.
[6] K. Gödel. "Über formal unentscheidbare Sätze der Principia Mathematica und verwandter Systeme I." 1931.
[7] J. Rawls. *A Theory of Justice.* Harvard University Press, 1971.
[8] I. Kant. *Groundwork of the Metaphysics of Morals.* 1785.
[9] M. A. Jannat Khah Doust. *نظریه آزادی، ایران و دین* (Theory of Freedom, Iran and Religion). CC BY 4.0.
