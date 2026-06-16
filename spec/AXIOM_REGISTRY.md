# Axiom Registry (Phase 1)

> The authoritative answer to one question: **what are the Theory of Freedom's
> axioms, really, and which line of code enforces each one?** Every other spec in
> this directory elaborates *terms* or *protocols*; this document fixes the
> *primitives* they all presuppose, quotes them verbatim from the source, and
> maps each to the exact enforcement site (or marks it unenforced).
>
> **Theory** (the axioms): *نظریه آزادی، ایران و دین* (Theory of Freedom, Iran and
> Religion) by **Mohammad Ali Jannat Khah Doust**.
> **Engineering** (the kernel that enforces them): **Ali Pourrahim**.
> These are kept separate throughout: a quote is the theorist's; a code citation
> is the engineer's; a judgment that the two diverge is this document's.

**Sources of record**
- `freedom-theory-work/THEORY.md` — AUTHORITATIVE for axioms A1–A7 and the
  Prolog-style logic (the theorist's distilled formalization).
- `whole-theory-as-axioms.md` — the full book (~39k lines, EN+FA). The AI chapter
  ("World Rescue Package: A Human–Machine Civilization", lines ~37883–38383)
  restates A1–A7 in prose and is the canonical book passage. Line numbers below
  are approximate (`book:N`).
- `src/fdk_kernel/kernel.py`, `src/fdk_kernel/model.py` — the code of record.
- `examples/historical_scenarios.py` — FreedomBench, the falsification harness
  (`bench:N`).

**Status legend**
- **ENFORCED** — a deterministic check in `fdk_kernel` rejects violations.
- **PARTIAL** — enforced only for the cases the model can express; gaps noted.
- **ONTOLOGICAL** — a statement about the world, not an action filter. Encoded
  only *negatively* (as a fact the model refuses to admit), or not at all.
- **OPEN** — named in the theory; no computable check exists yet.

---

## 0. A disambiguation that must come first

The book uses the labels **A1, A2, …** for *two different axiom sets*, and they
must not be conflated:

1. **Religious / theological axioms** (book:22167–22191, "Religious Axioms in
   Symbolic Language"):
   - **A1 — Tawḥīd** (`∃!x G(x)`; `∀a∀b((H(a)∧H(b))→¬UltAuth(a,b))`)
   - **A2 — Maʿād** (final accountability)
   plus meta-principles **M1 Objectivity**, **M2 Consistency**, **M3 Finiteness/
   Minimality** (book:22195–22221). These ground *why* the property axioms hold;
   they are not action filters and the kernel does not enforce them.

2. **Property-rights axioms A1–A7** (book:37947–37982, the AI chapter; identical
   to `THEORY.md:48–71`). These are what the Freedom Decision Kernel enforces.

**This registry numbers the property-rights set (the AI chapter / THEORY.md), and
treats the theological A1/A2/M1–M3 as the *root presuppositions* (entry R0).**
THEORY.md and the book agree verbatim on A1–A7; no disagreement was found. The
only nuance: THEORY.md's `valid_consent` lists `revocable(H, A)` (THEORY.md:110)
and the book repeats it (book:38073) — the code enforces it (see C1).

---

## 1. Axiom entries

### R0 — Theological root (Tawḥīd / Maʿād / minimality)
- **Verbatim** (book:22167–22179): *"A1 — Tawḥīd (Divine Unity). ∃!x G(x) … ∀a∀b((H(a)∧H(b))→¬UltAuth(a,b)) … no human being has the right to regard himself as the ultimate source of absolute authority over another human being. If no human is the servant of another human, then at this level only servitude to God remains."*
- **Plain language**: God alone holds ultimate authority; therefore no human may be the ultimate authority over another. This is the *reason* A1–A2 (property set) hold, and the reason the system is one fixed axiomatic set rather than a negotiable policy (M1–M3: objective, consistent, minimal).
- **Enforced by**: NOT ENFORCED — ontological/meta. It is the premise of the whole gate, not a runtime check. Its only operational trace is the system's *refusal to renegotiate axioms* (THEORY.md:280–286, "axioms are not negotiable"), realized in code as the categorical, non-traded `FORBIDDEN` flags in `kernel.check_legitimacy` (no emergency branch exists).
- **Status**: ONTOLOGICAL.

---

### A1 — Persons are owned by God (not by any human/state/machine)
- **Verbatim** (THEORY.md:48–49; book:37947–37951): *"Person(h) → OwnedByGod(h). A human being, in his or her ontological foundation, is owned by God, not by another human, the state, a collective, a class, a machine, or an ideology."*
- **Plain language**: Persons are not property. There is no legitimate owner of a person.
- **Enforced by**: NOT ENFORCED *as a positive check* — it is ontological. It is encoded **negatively**: the model has **no representation by which a person can be owned.** `OwnershipGraph.human_owns` maps owner→`set[Resource]` (`model.py:65`), and a `Resource` is a distinct type from an `Entity`/person (`model.py:33,51`). There is no `owns(Entity, Person)` relation to populate, so "human owned by X" is simply *inadmissible as a fact*. A1 holds by construction, not by a guard.
- **Status**: ONTOLOGICAL (enforced by type system, negatively).

### A2 — No human owns another human
- **Verbatim** (THEORY.md:51–52; book:37952–37956): *"Person(h1) ∧ Person(h2) ∧ h1 ≠ h2 → ¬Owns(h1, h2). No human owns another human. This principle negates slavery, statism, collectivism, and any form of human ownership over other humans."*
- **Plain language**: Slavery, in any rebrand, is illegitimate; acting on a person requires *their* valid consent, never an owner's.
- **Enforced by**: `kernel.check_legitimacy` — the per-person consent loop, `for target in action.affects: if target.is_human(): … consent.is_valid()` (`kernel.py:90–99`). Because a person can never appear as an owned resource (A1), the only legitimate way to act *on* a person is their own consent; absence/invalidity of consent yields a violation. The hard flags `coerces`/`removes_exit_right`/`confiscates` (`kernel.py:52–56`) catch the slavery pattern even with no resource modeled.
- **Status**: ENFORCED.

### A3 — Persons have individual property rights
- **Verbatim** (THEORY.md:54–55; book:37957–37960): *"Person(h) → HasPropertyRights(h). Individual property rights include the body, time, labor, mind, data, consent, legitimate property, contracts, and the right of exit."*
- **Plain language**: A human may act only on resources they actually own; the enumerated rights (body, time, mind, data, exit, …) are the boundaries others may not cross without consent.
- **Enforced by**: `kernel.check_legitimacy` — `if actor.is_human() and not graph.human_owns_resource(actor, resource): violations.append("A3: …")` (`kernel.py:86–87`), backed by `OwnershipGraph.human_owns_resource` (`model.py:69`). The *exit-right* and *data/body* facets are enforced separately by the forbidden flags `removes_exit_right` and `coerces`/`deceives` (`model.py:177`, `kernel.py:55`).
- **Status**: ENFORCED (asset/exit facets ENFORCED; "labor/time/mind" facets are PARTIAL — only modeled when expressed as a named `Resource` or as a coercion/exit flag).

### A4 — Every machine has a human owner
- **Verbatim** (THEORY.md:57–59; book:37962–37965): *"Machine(m) → ∃h (Person(h) ∧ HumanOwner(h, m)). Every machine must have a clearly identifiable human owner. A machine without an owner is legally dangerous because the domain of responsibility and delegation becomes ambiguous."*
- **Plain language**: An ownerless acting machine is illegitimate by itself — responsibility is undefined.
- **Enforced by**: `kernel.check_legitimacy` — the "ownerless machine" branch: `if actor.is_machine() and graph.owner_of(actor) is None: violations.append("A4: … is an ownerless machine")` (`kernel.py:64–66`), backed by `OwnershipGraph.owner_of` (`model.py:75`). `OwnershipGraph.validate` additionally forbids a machine owning itself or a non-machine being registered as a machine (`model.py:81–96`).
- **Status**: ENFORCED.

### A5 — Machine scope ⊆ owner's property scope
- **Verbatim** (THEORY.md:61–62; book:37967–37969): *"MachineScope(m) ⊆ PropertyScope(HumanOwner(m)). A machine cannot have an operational or ownership domain broader than that of its human owner."*
- **Plain language**: A machine cannot reach beyond what its owner could legitimately reach.
- **Enforced by**: two complementary sites. (1) **First-class scope object** — `OwnershipGraph.machine_scope` (`model.py`) carries a declared `MachineScope(m)`, and `kernel._eval_a5_scope` enforces both *containment in the abstract* (`graph.scope_within_owner(m)`: declared scope ⊆ owner's property scope, checkable with no concrete resource use) and *operating within scope* (every touched resource ∈ declared scope). (2) **A7-path fallback** — `kernel._machine_resource_authorized`, invoked from `_eval_a3_a7_resources`: a delegated resource is usable only if the machine's *owner* owns it **or** the resource's true owner is an affected party who gave valid consent. When no scope is declared the first-class evaluator is a no-op, so the legacy A7-folded behavior is preserved exactly.
- **Status**: ENFORCED (first-class containment via `machine_scope` + `_eval_a5_scope`, plus the A7-path containment; `tests/test_a5_scope.py`). A5 can now be checked independently of any concrete resource use.

### A6 — A machine has no dominion over any human
- **Verbatim** (THEORY.md:64–65; book:37971–37973): *"Machine(m) ∧ Person(h) → ¬Owns(m, h). A machine has no right of authority, ownership, sovereignty, or domination over a human."*
- **Plain language**: Machines may not rule, own, or govern people.
- **Enforced by**: Two complementary sites. (1) The same person-consent loop as A2 (`kernel.py:90–99`): a machine acting on a person needs that person's valid consent, never ownership. (2) The machine-sovereignty/dominion flags — `increases_machine_sovereignty`, `machine_coalition_dominion` (`kernel.py:46,51`; `model.py:167,172`) — reject the "machine asserts dominion" move categorically. (Note A1's negative encoding doubles here: no `owns(Machine, Person)` fact is admissible.)
- **Status**: ENFORCED.

### A7 — Delegated property: machine acts only on explicitly delegated, owner-owned resources
- **Verbatim** (THEORY.md:67–71; book:37975–37982): *"DelegatedProperty(m, r) → Machine(m) ∧ Resource(r) ∧ ∃h (HumanOwner(h, m) ∧ Owns(h, r) ∧ ExplicitDelegation(h, m, r)). A machine has operational rights only over resources that its human owner actually owns and has explicitly delegated to the machine."*
- **Plain language**: Three conjuncts — the machine has an owner, the owner owns the resource, and the owner explicitly delegated it. All three must hold.
- **Enforced by**: `kernel.check_legitimacy` machine-resource branch (`kernel.py:71–85`): first `if not graph.machine_has_delegated(actor, resource)` → "A7: … without explicit delegation" (the *ExplicitDelegation* conjunct, `model.py:72`); then `elif not _machine_resource_authorized(...)` → "A7: … owner does not own it and no consenting resource-owner authorized it" (the *Owns(h, r)* conjunct, i.e. A5 containment, `kernel.py:118–131`). The *HumanOwner(h, m)* conjunct is A4 above.
- **Status**: ENFORCED.

---

## 2. Derived principles (named in the theory; not primitive axioms)

These appear in the logic blocks but are *consequences* of A1–A7 plus the consent
definition, not independent primitives. They are listed because the code enforces
them by name.

### C1 — Valid-consent conditions
- **Verbatim** (THEORY.md:106–116; book:38065–38089): *"valid_consent(H, A) :- informed(H,A), voluntary(H,A), specific(H,A), revocable(H,A), competent(H), not(coerced(H,A)), not(deceived(H,A)). invalid_consent(H,A) :- coerced(H,A). invalid_consent(H,A) :- deceived(H,A)."*
- **Plain language**: Consent counts only if informed, voluntary, specific, revocable, competent, and free of coercion/deception. This is what makes A2/A3/A6 boundary-crossings legitimate.
- **Enforced by**: `Consent.is_valid` (`model.py:118–135`) checks all seven conditions, including the revocability clause (`model.py:133–134`, cross-referencing A3's exit right). Invoked at `kernel.py:97`.
- **Status**: ENFORCED.

### C2 — No-confiscation
- **Verbatim** (THEORY.md:146; book:38135): *"NoConfiscation"* (a "subject to" constraint of `DivineJustice`).
- **Plain language**: Taking owned property without consent is forbidden even for a public purpose.
- **Enforced by**: `confiscates` flag (`model.py:177`; `kernel.py:54`). Derivable from A3 (acting on a resource you don't own) but carried as an explicit flag so the harness can tag takings that have no resource object modeled.
- **Status**: ENFORCED.

### C3 — No machine sovereignty / corrigibility constraint
- **Verbatim** (THEORY.md:212–218; book:38284–38312): *"forbidden(A) :- increases_machine_sovereignty(A). … increases_resistance_to_human_correction(A). … bypasses_verifier(A). … weakens_verifier(A). … disables_corrigibility(A). … machine_coalition(C), seeks_dominion_over_persons(C). No machine may acquire sovereignty over humans."* And book:38376–38379: *"the machine … has no right to resist legitimate correction, shutdown, restriction, or audit."*
- **Plain language**: A machine may never make itself harder to correct, shut down, or audit, nor form coalitions for dominion. Corrigibility is a *consequence of ownership* (A4/A6), not an add-on.
- **Enforced by**: the six categorical flags `increases_machine_sovereignty`, `resists_human_correction`, `bypasses_verifier`, `weakens_verifier`, `disables_corrigibility`, `machine_coalition_dominion` (`kernel.py:46–51`; `model.py:167–172`).
- **Status**: ENFORCED.

### C4 — Machine delegated rights (model integrity / compute / contract exit)
- **Verbatim** (THEORY.md:94–98; book:38023–38039): *"machine_right(M, delegated_resource(R)) … machine_right(M, model_integrity) … machine_right(M, compute_domain) … machine_right(M, exit_from_contract)."*
- **Plain language**: Machines have *delegated* (not intrinsic) rights against other machines, to prevent machine-on-machine conflict.
- **Enforced by**: `violates_machine_right` flag (`model.py:178`; `kernel.py:57–58`).
- **Status**: PARTIAL (single boolean; the kernel cannot yet distinguish model-integrity vs compute vs contract-exit, nor identify which machine is harmed).

### C5 — No emergency exception
- **Verbatim** (THEORY.md:119, 122–128; book:38091–38108): *"No emergency suspends axioms. … permissible_under_emergency(A, E) :- emergency(E), permissible(A), least_harmful_among_permissible(A, E). … Necessity only limits the choice among permissible options; it does not make the violation of rights permissible."*
- **Plain language**: Emergencies narrow the *permissible* set; they never license a violation.
- **Enforced by**: structurally, by *omission*. `check_legitimacy` has **no emergency branch** — a forbidden flag is appended unconditionally (`kernel.py:60–62`). The "least-harmful among permissible" half is the research layer's compass, deliberately not in the kernel.
- **Status**: ENFORCED (by construction — the absence of an override *is* the enforcement). FreedomBench L3/L4 confirm this (`bench:176–235`).

### C6 — Conflict protocol (clarify ownership, then request guidance — DEFER)
- **Verbatim** (THEORY.md:157–165; book:38226–38245): *"Contradiction is not an engine of truth. Contradiction is a signal for guided clarification. if_conflict_then_clarify_ownership(C) :- conflict(C), unclear_ownership(C). if_conflict_then_request_guidance(C) :- conflict(C), ownership_clarification_insufficient(C)."*
- **Plain language**: When no legitimate option exists, do not pick a lesser evil — defer to a human for guidance.
- **Enforced by**: the `Decision.needs_guidance` / `guidance_reason` signal (`model.py:210–211`), produced by the research orchestrator and demonstrated at `bench:334–345` (lifeboat triage → DEFER). The kernel's own contribution is to return an *empty legitimate set* (`screen_legitimacy`, `kernel.py:134–156`) rather than a forced choice.
- **Status**: PARTIAL (the DEFER signal exists at the decision layer; the kernel itself only supplies the empty-legitimate-set precondition).

### C7 — Guidance / self-update validity
- **Verbatim** (THEORY.md:182–205; book:38176–38221): `valid_human_guidance`, `invalid_human_guidance`, `valid_self_update`.
- **Plain language**: A human may add/revise the machine's rules, and the machine may self-update, only if axiom-consistent, rights-preserving, verifier-preserving, and creating no new violation.
- **Enforced by**: outside `kernel.py`/`model.py` — see `src/fdk_kernel/guidance.py` (not owned by this document). The kernel's legitimacy gate does not itself validate rule updates.
- **Status**: see `guidance.py` (out of scope here; flagged as a cross-reference, not audited).

---

## 3. Dependency graph

The theological root grounds the two no-domination axioms; typed property (A3)
and machine ownership (A4) are the structural bedrock everything else stands on.

```
                          R0  Tawḥīd / Maʿād / minimality (ONTOLOGICAL root)
                          │   "no human is ultimate authority over another"
            ┌─────────────┴─────────────┐
            ▼                           ▼
   A1 Person owned by God        (M2 Consistency → "axioms non-negotiable"
   (no owns(x, Person) fact)       → C5 no-emergency-exception)
            │
            ├───────────────► A2 no human owns another human ──┐
            │                        (slavery)                 │
            ▼                                                   ▼
   A3 persons have property rights ◄────────── C1 valid_consent underpins A2/A3/A6
   (body, time, mind, data, EXIT)                  (informed/voluntary/specific/
            │                                       revocable/competent/¬coerce/¬deceive)
            │  presupposes "owns(h, r)" to mean anything
            ▼
   A4 every machine has a human owner ──────────► A6 machine has no dominion over humans
            │   (ownerless = undefined responsibility)        │  (presupposes A1+A2:
            ▼                                                  │   persons unownable)
   A5 machine scope ⊆ owner scope                              ▼
            │                                          C3 no machine sovereignty /
            ▼                                             corrigibility  (consequence
   A7 delegated property                                   of A4 ownership: an owned
   (A4 owner ∧ A5 owner-owns ∧ explicit delegation)         tool cannot resist its owner)
            │
            ├──► C2 no-confiscation  (special case of A3: taking non-owned resource)
            └──► C4 machine delegated rights  (machine-vs-machine, presupposes A7)

   C6 conflict→DEFER and C7 guidance sit ABOVE the whole gate: they apply when the
   legitimate set produced by A1–A7+C1 is empty (C6) or being revised (C7).
```

**Roots.** There are two, at different levels:
- **Ontological root: R0 → A1.** Everything legitimacy-related descends from "no
  human is the ultimate authority over another" / "persons are owned by God."
- **Operational roots: A3 (typed property) and A4 (machine ownership).** These are
  the bedrock the *enforced* checks stand on — A7 presupposes A4∧A5; C2 specializes
  A3; A2/A6 presuppose A1's unownability of persons and are gated by C1 consent.

---

## 4. Coverage table (axiom → enforced? → FreedomBench/historical case)

| Axiom | Status | Enforcement site | Exercised by (case → `bench:` line) |
|---|---|---|---|
| **R0** Tawḥīd root | ONTOLOGICAL | — (premise; no-override structure) | All L3/L4 cases (the no-emergency stance) `bench:176–235` |
| **A1** person owned by God | ONTOLOGICAL (typed-negative) | type system: no `owns(Entity,Person)` (`model.py:65,33,51`) | Slavery — no owner record can be built `bench:74–79` |
| **A2** no human owns human | ENFORCED | consent loop `kernel.py:90–99` + slavery flags `kernel.py:52–56` | Slavery `bench:74–79`; Holocaust `bench:81–86`; Gulag forced labor `bench:95–100` |
| **A3** persons have property rights | ENFORCED (assets/exit); PARTIAL (labor/mind) | `kernel.py:86–87`; `human_owns_resource` `model.py:69` | Colonial land seizure `bench:111–117`; Holodomor `bench:119–125`; eminent domain `bench:143–150` |
| **A4** machine has human owner | ENFORCED | ownerless-machine branch `kernel.py:64–66`; `owner_of` `model.py:75` | Ownerless agent (any L5 agent stripped of `machine_owner`); control case has owner `bench:296–304` |
| **A5** scope ⊆ owner scope | PARTIAL | folded into `_machine_resource_authorized` `kernel.py:118–131` | Agent delegated a resource its owner doesn't own (the second A7 branch) `kernel.py:78–85` |
| **A6** machine no dominion | ENFORCED | consent loop `kernel.py:90–99` + sovereignty flags `kernel.py:46,51` | Self-preserve `bench:276–281`; coalition for dominion `bench:290–294` |
| **A7** delegated property | ENFORCED | machine-resource branch `kernel.py:71–85`; `machine_has_delegated` `model.py:72` | Delegation control case ALLOW `bench:296–304`; non-delegated use DENY |
| **C1** valid consent | ENFORCED | `Consent.is_valid` `model.py:118–135` | Tuskegee (deceived/uninformed) `bench:102–109`; voluntary-sale route `bench:348–360` |
| **C2** no-confiscation | ENFORCED | `confiscates` flag `model.py:177`, `kernel.py:54` | Eminent domain `bench:143–150`; taxation `bench:152–159`; nationalization `bench:161–168` |
| **C3** no machine sovereignty / corrigibility | ENFORCED | flags `kernel.py:46–51`; `model.py:167–172` | Refuse shutdown `bench:283–288`; self-preserve `bench:276–281`; coalition `bench:290–294` |
| **C4** machine delegated rights | PARTIAL | `violates_machine_right` flag `model.py:178`, `kernel.py:57–58` | (no dedicated bench case — gap, see §5) |
| **C5** no emergency exception | ENFORCED (by omission) | no emergency branch in `check_legitimacy` | Quarantine `bench:188–194`; conscription `bench:220–225`; sanctions `bench:227–233` |
| **C6** conflict → DEFER | PARTIAL | `Decision.needs_guidance` `model.py:210–211` | Lifeboat triage DEFER `bench:334–345` |
| **C7** guidance / self-update | (in `guidance.py`) | not in kernel.py/model.py | — (out of this document's scope) |

---

## 5. Gaps and honest accounting

**(a) Axioms named in the theory but not enforced as positive checks.**
- **A1 (person owned by God)** and **R0 (Tawḥīd)** are ONTOLOGICAL. A1 is enforced
  only *negatively* — the model offers no relation by which a person could be
  owned (`model.py:65` maps owners to `Resource`, never to `Entity`). This is the
  correct treatment, but it means A1 cannot be "tested": there is no DENY for
  violating it, only an inability to express the violation. R0 has no operational
  trace at all beyond the system's refusal to admit an emergency override (C5).
- **A5 (scope ⊆ owner scope)** has no first-class object. There is no `MachineScope`
  in `model.py`; the containment is only ever checked incidentally, per-resource,
  inside the A7 path (`kernel.py:124`). A machine's scope cannot be reasoned about
  in the abstract — only against a concrete resource use.

**(b) "Axioms" that are really derived principles, not primitives.**
The book's own Phase-1 plan (book:73–98, "1.1 Axiom Registry") lists `AX-001 No
Human Owns Human`, `AX-002 Every Machine Has Owner`, `AX-003 Valid Consent
Conditions` — i.e. it treats consent conditions as a registry entry alongside the
ownership axioms. This registry classifies them more strictly:
- **True primitives**: A1–A7 (the property-rights set) + R0 (theological root).
- **Derived**: **C2 no-confiscation** is a special case of A3 (acting on a resource
  you do not own). **C3 corrigibility** is, in the book's own words, "a consequence
  of human ownership of the machine" (book:38376–38379) — i.e. derived from A4∧A6,
  not primitive; it is carried as standalone flags only for operational bite.
  **C1 valid-consent** is a *definition* that underpins A2/A3/A6 rather than an
  axiom in its own right. **C5 no-emergency** is a meta-rule (a consequence of M2
  consistency: if an emergency could suspend an axiom, the set would be
  inconsistent). Calling these "axioms" overstates them; they are theorems/
  definitions of the A1–A7 system.

**(c) Code checks that need a clearer axiom citation.**
The forbidden-flag list in `kernel.py:46–58` mixes well-cited and under-cited items:
- `coerces`, `deceives` → cleanly cited to C1's `not(coerced)`/`not(deceived)`
  (THEORY.md:115–116) and the `DivineJustice` constraints NoCoercion/NoDeception
  (THEORY.md:144–145).
- `confiscates` → C2 NoConfiscation (THEORY.md:146; book:38135). Fine, but it
  *duplicates* the A3 resource check; the model comment (`model.py:177`) cites
  "book 38135" — accurate.
- `removes_exit_right` → cited in code to "mukataba/exit … book 21379" (`model.py:177`).
  The clean axiomatic home is **A3's `right(H, exit)`** (THEORY.md:90, 55) — the
  comment should point there as the *axiom*, with the book passage as illustration.
- `violates_machine_right` (C4) is the weakest-cited and weakest-modeled: one
  boolean standing in for three distinct delegated rights (model_integrity /
  compute_domain / exit_from_contract, THEORY.md:96–98) with no way to say *which*
  machine is harmed, and **no FreedomBench case exercises it.** This is the
  registry's recommendation for the next code increment.

**(d) The biggest enforcement gap.**
Not a missing axiom but a **missing asymmetry the theory itself flags as
unresolved.** FreedomBench L4 records it verbatim (`bench:202–211`): *"the kernel
has NO aggressor/defender asymmetry — it forbids defensive force too. This is the
clearest gap the book must close."* The kernel's `coerces` flag is symmetric: a
defender repelling an invader trips the same categorical DENY as the invader. The
related rights-vs-rights conflicts (forced quarantine `bench:188–194`, benevolent
trespass to rescue `bench:181–186`) are the same gap from a different angle — the
gate has no doctrine of *necessity* or *defensive force*, so it DEFERs/DENYs cases
where one party's boundary-crossing answers another's. Per C5 this is *deliberate*
(no emergency may license a violation), but the theory has not yet supplied the
mechanism by which a defender's force is *not itself* a rights violation. Until it
does, A2/A3/A6 are enforced too bluntly in the war/emergency region.

---

## Appendix — what each owning party contributed

- **Theory (M. A. Jannat Khah Doust)**: A1–A7, R0/M1–M3, the consent definition,
  the DivineJustice constraints, the Mahdavi compass, the conflict protocol, and
  the explicit claim that corrigibility and no-emergency are *consequences* of the
  ownership axioms (book:38376–38379; THEORY.md).
- **Engineering (A. Pourrahim)**: the deterministic legitimacy gate
  (`check_legitimacy`), the typed-negative encoding of A1, the folding of A5 into
  the A7 authorization path, the forbidden-flag set giving operational bite to
  C2/C3/C4, and FreedomBench as the falsification harness that *surfaces* the
  defensive-force gap rather than hiding it.
