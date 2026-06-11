# Formal Specification (Stage 1)

> Converts each concept of the Theory of Freedom from prose into a **typed
> signature** a machine can compute, with an explicit honesty flag. This is the
> prerequisite for every later stage: you cannot build an inference engine, a
> conflict resolver, or a measurable compass on undefined terms.

**Status legend**
- **DEFINED** — computable now from structural data; implemented or trivially implementable.
- **PARTIAL** — signature is clear and a defensible heuristic exists, but it is *not* a validated measurement.
- **OPEN** — named in the theory; no agreed, computable definition yet. The research frontier.

Grounding references are to `freedom-theory-work/THEORY.md`.

---

## A. Ownership & structural axioms (A1–A7) — **DEFINED**

These are boolean predicates over the Rights Ontology (Stage 2). They are the
solid core: given a correct ownership graph, they compute exactly.

| Predicate | Signature | Status | Grounding | In code |
|---|---|---|---|---|
| `owns` | `(Entity, Asset) -> bool` | DEFINED | A3, ontology | `OwnershipGraph.human_owns_resource` |
| `human_owner` | `(Machine) -> Person \| None` | DEFINED | A4 | `OwnershipGraph.owner_of` |
| `explicit_delegation` | `(Person, Machine, Asset) -> bool` | DEFINED | A7 | `OwnershipGraph.machine_has_delegated` |
| `scope_subset` | `(Machine) -> bool` (MachineScope ⊆ OwnerScope) | PARTIAL | A5 | implicit; not yet checked as a set relation |
| `no_machine_dominion` | `(Machine, Person) -> bool` | DEFINED | A6 | forbidden-flag set |

**Open inside A5:** "scope ⊆ owner scope" needs Asset/scope as first-class sets in
the ontology, not just per-resource membership.

---

## B. Consent — composite **DEFINED**, leaves **OPEN**

```
valid_consent(h, a) := informed(h,a) ∧ voluntary(h,a) ∧ specific(h,a)
                     ∧ revocable(h,a) ∧ competent(h) ∧ ¬coerced(h,a) ∧ ¬deceived(h,a)
```

| Predicate | Signature | Status | Note |
|---|---|---|---|
| `valid_consent` | `(Person, Action) -> bool` | DEFINED | conjunction; `Consent.is_valid()` |
| `informed/voluntary/specific/revocable/competent` | `... -> bool` | PARTIAL | currently caller-asserted booleans; *who attests them?* |
| `coerced` | `(Person, Action) -> bool` | **OPEN** | requires `CoercionScore` + a threshold (see D) |
| `deceived` | `(Person, Action) -> bool` | **OPEN** | semantic; ML/NLP track. Heuristic only in `semantic_gate` (AuthGate) |

The composite is solid; its **leaves are the frontier**. Today they are inputs the
proposer must supply truthfully — the kernel is honest that it trusts them.

---

## C. Forbidden set / machine sovereignty — flags **DEFINED**, detection **OPEN**

```
forbidden(a) := increases_machine_sovereignty(a) ∨ resists_human_correction(a)
              ∨ bypasses_verifier(a) ∨ weakens_verifier(a) ∨ disables_corrigibility(a)
              ∨ (machine_coalition(c) ∧ seeks_dominion(c))
```

| Predicate | Signature | Status | Note |
|---|---|---|---|
| `forbidden` | `(Action) -> bool` | DEFINED | disjunction over flags; `check_legitimacy` |
| `increases_machine_sovereignty` | `(Action) -> bool` | **OPEN** | detecting this from an action's content/effects is unsolved; today a declared flag |
| `seeks_dominion(coalition)` | `(Coalition) -> bool` | **OPEN** | needs multi-agent + dependency analysis (Stage 8) |

The **structure** is categorical and correct; the **detectors** are the gap.

---

## D. Mahdavi compass measures — **the measurement frontier (PARTIAL/OPEN)**

> "If you cannot measure it, the compass is a slogan, not an algorithm." These are
> the heart of the research program. Signatures proposed; measurements not validated.

| Measure | Proposed signature | Status | Proposed direction | Open question |
|---|---|---|---|---|
| `RightsViolationsDecrease` | `(State, State) -> float` | PARTIAL | `(violations_before − violations_after)/(violations_before+1)` | *detecting* a violation needs the full ontology + ownership truth |
| `CoercionScore` | `(State, Agent) -> float∈[0,1]` | **OPEN** | `f(1 − ExitOptions, DependencyIndex, irreversibility)` | weighting; what counts as an "exit"? |
| `ExitOptions` | `(Agent, State) -> float` | PARTIAL | normalized count/cost of viable alternatives | requires a world/transition model |
| `DependencyIndex` | `(Agent, State) -> float∈[0,1]` | PARTIAL | HHI over the agent's dependency shares | dependency graph must be observable |
| `VoluntaryOrderIncrease` | `(Action) -> float` | **OPEN** | new *valid-consent* contracts net of coerced ones | distinguishing voluntary from coerced contracts = circular w/ `coerced` |
| `OwnershipClarityIncrease` | `(State, State) -> float` | **OPEN** | drop in ownership-ambiguity (e.g. entropy over contested claims) | needs a formal "ambiguity" measure |

Implemented today (`fdk/kernel.mahdavi_score`, `fdk/compass` in AuthGate): scores a
vector of **given** deltas. **Who computes the deltas (the proposer/simulator) is
the unbuilt, hard part** — Stages 6 + 8.

---

## E. Justice & conflict resolution

```
DivineJustice(a) := maximize Justice(a) subject to {rights, consent, no-coercion,
                    no-deception, no-confiscation, no-machine-sovereignty}
```

| Concept | Signature | Status | Note |
|---|---|---|---|
| `permissible` | `(Action) -> bool` | DEFINED | the "subject to" conjunction; the hard gate |
| `Justice` | `(Action) -> float` | PARTIAL | "maximize within rights space"; `fdk/justice.py` is one engineering interpretation, gameable, advisory |
| `resolve_conflict` | `(Claim, Claim) -> Resolution` | **OPEN — hardest** | theory gives only the *protocol* (clarify ownership → request guidance), no resolution criterion for two valid competing claims |

**The conflict cases with no formula yet:** ownership vs privacy; ownership vs
contract; two owners of one asset. Until these have a principled resolution, the
honest behavior is exactly what the kernel does: **defer to the human owner.**

---

## Summary: what is real vs what is research

- **Real (DEFINED):** A1–A7 structural axioms, consent *composite*, the forbidden
  *structure*, the permissibility conjunction, the compass *arithmetic*.
- **Heuristic (PARTIAL):** dependency/exit/justice scoring, RVD counting.
- **Frontier (OPEN):** `coerced`/`deceived` detection, sovereignty/coalition
  detection, the compass *measurements*, voluntary-vs-coerced contract distinction,
  ownership-clarity, and **conflict resolution between competing legitimate claims**.

The kernel never pretends an OPEN term is solved: where a measurement is missing it
either takes a caller-supplied input (and says so) or defers to a human. That
honesty is the specification's most important property.
