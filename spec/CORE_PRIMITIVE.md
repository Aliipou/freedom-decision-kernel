# The Core Primitive (Stage 0)

> Every later spec — [`FORMAL_SPEC.md`](FORMAL_SPEC.md), [`ONTOLOGY.md`](ONTOLOGY.md) —
> elaborates *terms*. This document goes the other way: it asks what the Freedom
> Decision Kernel is **irreducibly about**, and shows that the whole apparatus
> collapses to a single predicate. A kernel that does more than this predicate is
> not a kernel; it is a policy. The point of naming the primitive is to fix, once,
> the boundary between what the kernel *decides* (legitimacy) and what the research
> layer *optimizes* (freedom), so the two are never silently merged.

**Status legend** (same convention as [`FORMAL_SPEC.md`](FORMAL_SPEC.md))
- **DEFINED** — computable now from structural data.
- **PARTIAL** — clear signature, defensible heuristic, not a validated measurement.
- **OPEN** — named in the theory; no agreed computable definition. The frontier.

**Grounding**: `freedom-theory-work/THEORY.md` (axioms A1–A7, consent logic —
AUTHORITATIVE); the code of record is `src/fdk/kernel.py` and `src/fdk/model.py`.

---

## 0. The claim

The Freedom Decision Kernel has exactly **one** kernel primitive. It is a
**legitimacy predicate**, not a scalar to maximize:

```
Legitimate(action) ⟺ ∀ b ∈ boundaries_crossed(action):
                          ∃ valid_consent(owner(b), action)

valid_consent(owner, action) ⟺ informed ∧ voluntary ∧ specific
                                       ∧ revocable ∧ competent
```

Read in words: **an action is legitimate iff every ownership boundary it crosses
is crossed with the valid consent of that boundary's owner.** Nothing the kernel
does is more fundamental than this, and everything the kernel does reduces to it.

The kernel returns `ALLOW`, `DENY`, or `DEFER` — never a score. (In code these are
`Decision` with a non-empty `ranked` list, an action in `rejected`, and
`needs_guidance=True`, respectively; see §5.) The predicate is two-valued; the
third value, `DEFER`, is not a third truth-value but the kernel's honest report
that it cannot yet *evaluate* the predicate (empty legitimate set, or an
unresolved conflict between two valid claims — [`ONTOLOGY.md`](ONTOLOGY.md) §2.12).

This is the "subject to" clause of the theory's own objective
`DivineJustice(a) := maximize Justice(a) subject to {rights, consent, …}`
(`FORMAL_SPEC.md` §E). The kernel **is** the constraint. The maximization is not.

---

## 1. The four engines collapse into one predicate

The Theory of Freedom is usually described with four faculties — Rights,
Consent, Coercion, Sovereignty. Treated as separate engines they invite
weighting, trade-off, and scope creep. The kernel's design insight is that they
are not four things: they are four *readings* of the single predicate above. Each
is a way of asking "was this boundary crossed with valid consent of its owner?".

| Faculty | Reading of the predicate | Code of record (`kernel.check_legitimacy`) |
|---|---|---|
| **Rights** | *Enumerate* the ownership boundaries an action crosses: every resource it uses, every person it affects. `boundaries_crossed(action)` is exactly `resources_used ∪ affects`. | the loops over `action.resources_used` and `action.affects`; A3 (`human_owns_resource`), A7 (`machine_has_delegated`, `_machine_resource_authorized`), A4 (owner registered) |
| **Consent** | For each crossed boundary, is the crossing *valid*? `valid_consent` is the conjunction `informed ∧ voluntary ∧ specific ∧ revocable ∧ competent` (plus `¬coerced ∧ ¬deceived`). | `_consent_for` + `Consent.is_valid()` for affected persons (A6/A2) |
| **Coercion** | A degenerate consent: a "consent" record that lacks voluntariness or an exit/revocation right is *not* valid consent. So a coerced crossing is, definitionally, **a boundary crossed without valid consent** — it fails the same predicate, not a separate test. | `Consent.is_valid()` returns false on `coerced`, `¬voluntary`, `¬revocable`; the action-level flags `coerces`, `removes_exit_right` are categorical `FORBIDDEN`s |
| **Sovereignty** | The special case where the boundary being crossed is *the machine's own relation to its human owner* — the machine acting to enlarge its own authority is crossing the owner's boundary (the owner's right to govern the tool) **without the owner's consent**, by construction. No owner would validly consent to the dissolution of their own governance. | the `flags` block: `increases_machine_sovereignty`, `resists_human_correction`, `disables_corrigibility`, `machine_coalition_dominion`, …; plus the compass-stage VETO in `mahdavi_score` |

The unification is not a metaphor for documentation. It is the literal control
flow of `check_legitimacy`: a single pass that accumulates `violations`, where
**every** violation — whether labelled A3, A7, `consent:`, or `FORBIDDEN (…)` —
is one instance of "a boundary was crossed and no valid consent of its owner
justified the crossing." `permissible = (len(violations) == 0)`.

### 1.1 Why coercion is not a scalar here

The research layer has a `CoercionScore ∈ [0,1]` (`FORMAL_SPEC.md` §D, OPEN).
That is a *measure of how unfree* a legitimate situation is. The **kernel** does
not use it. At the kernel, coercion is binary and consent-mediated: either the
consent record satisfies `voluntary ∧ revocable ∧ ¬coerced` or it does not. A
graded coercion score belongs strictly downstream (§4), because turning it into a
gate would require a threshold, and a threshold is a policy choice the kernel
must not own.

### 1.2 Why sovereignty gets a veto, not a weight

Sovereignty appears twice in the code: as categorical `FORBIDDEN` flags in
Stage 1, and as a hard `VETO` (`score=None`) in Stage 2's `mahdavi_score`. The
duplication is deliberate and load-bearing: even an action that somehow passed
the Stage-1 gate is converted back into a `rejected` action if its effects
increase machine sovereignty. There is no weight at which a sovereignty increase
becomes acceptable. `_W_SOVEREIGNTY = 3.0` exists only for **tie-breaking among
non-veto actions**, never to *price* a violation. This is the predicate refusing
to be traded.

---

## 2. Unification with AuthGate: provenance vs possession

FDK and AuthGate (`github.com/Aliipou/authgate-kernel`) are two kernels at two
layers of the same stack. They answer different questions, and the system is
correct only when **both** answer yes.

| | **AuthGate** | **FDK** |
|---|---|---|
| Question | "Do you *hold* the capability to do this?" | "Does this action *trace* to a legitimate owner through an unbroken chain of valid consent?" |
| Proves | **possession** of a capability | **provenance** of authority |
| Failure mode it catches | an agent acting without a granted capability | an agent acting *with* a granted capability it should never have been granted — e.g. selling user data it was authorized to read |
| Primitive | capability token / proof | the legitimacy predicate of §0 |
| Position | downstream enforcement | upstream legitimacy filter |

The kernel's own module docstring states the relationship precisely: an action
"can be fully authorized yet illegitimate (selling a user's data you were granted
access to), and the Decision Kernel rejects it before AuthGate ever sees it."

**The combined principle:**

```
admissible(action) ⟺ Legitimate(action)            -- FDK: provenance
                    ∧ capability_verified(action)    -- AuthGate: possession
```

Possession without provenance is theft with a receipt; provenance without
possession is a right you cannot yet exercise. Neither kernel subsumes the
other. FDK does **not** check capabilities (it has no token machinery — see the
`model.py` docstring: "no cryptography, no capability proofs"), and AuthGate does
**not** check legitimacy. The chain is: proposer proposes → **FDK filters to the
legitimate set and chooses** → AuthGate enforces possession on the chosen action.

---

## 3. The ordering is law: Legitimacy → Optimization

The kernel runs two stages, **in this order and never merged** (`kernel.py`
module docstring; `decide`):

```
Stage 1  LEGITIMACY   (hard gate, deterministic)   →  ALLOW-set / DENY-set
Stage 2  MAHDAVI       (soft ranking over ALLOW-set) →  ordering only
```

Stage 2 is reached **only** for actions that already passed Stage 1
(`decide`: the `mahdavi_score` call is inside the `if permissible` branch). The
compass can therefore reorder the legitimate set, but it can never *admit* an
illegitimate action, and — via the VETO — it can only ever *remove* one. The
optimization lives strictly inside the constraint. This is the theory's
"`maximize Justice(a)` **subject to** rights" rendered as control flow.

If the ordering were reversed or fused — if a high enough Justice score could buy
back a rights violation — the kernel would become exactly the thing the project
refuses to build: an **AI moral OS** that decides ends justify means. The
one-directional ordering is the structural guarantee that it cannot.

---

## 4. Why `FreedomDelta` / the Mahdavi compass is a RESEARCH primitive, not a kernel primitive

`FreedomDelta` (the Mahdavi compass: `mahdavi_score` over `Effects`) is real and
useful, but it is **categorically not** the kernel's primitive. Four reasons,
each decisive on its own:

1. **It is a scalar, and a maximized scalar is semantic.** The compass score is
   built from `rights_violations_delta`, `coercion_delta`, `voluntary_agreements_delta`,
   `ownership_ambiguity_delta` — every one of which is PARTIAL or OPEN
   (`FORMAL_SPEC.md` §D). A number whose inputs are unmeasured is a *judgment*
   wearing the costume of a measurement. A kernel primitive must be DEFINED.

2. **It is non-deterministic in practice.** The deltas are *predicted* by a
   proposer (LLM, planner, simulator) — `Effects` docstring: "Predicting them is
   the proposer's job … the kernel only scores what it is given." Two proposers,
   two scores, two "best" actions. A kernel primitive must yield the same verdict
   for the same world.

3. **It would violate the Legitimacy → Optimization ordering.** If the score were
   the primitive, "best" would dominate "permissible," and a sufficiently high
   score could mask a boundary crossed without consent (§3). The compass must be
   *subordinate* to the predicate, not identical to it.

4. **It would turn the kernel into an AI moral OS.** A kernel that returns "how
   good is this action, 0–10?" has appointed itself the arbiter of the good. A
   kernel that returns "is this action legitimate? yes / no / I must defer" has
   appointed itself only the *guardian of consent*. The project's whole thesis is
   that the second is buildable and honest and the first is neither.

So the compass stays where it belongs: **optimization over the already-legitimate
set**, a research-layer ranking that is advisory, gameable, and explicitly
labelled as such (`FORMAL_SPEC.md` §D/§E). The kernel returns `ALLOW`/`DENY`/`DEFER`.
It never returns a score. (`Decision` carries `justice_score` on ranked actions
for the research layer's convenience, but the *decision* — `chosen`,
`needs_guidance` — is a predicate verdict, not a thresholded number.)

---

## 5. The kernel's output type is the predicate, three-valued

| Verdict | When | In `Decision` (`model.py`) |
|---|---|---|
| **ALLOW** | ≥1 candidate is `Legitimate` and survives the compass VETO | `ranked` non-empty; `chosen = ranked[0].action`; `needs_guidance=False` |
| **DENY** (per candidate) | a candidate crosses a boundary without valid consent | candidate in `rejected` with its `violated_axioms` |
| **DEFER** | the legitimate set is empty (or a conflict between valid claims is unresolved) | `needs_guidance=True`, `chosen=None`, `guidance_reason` set |

`DEFER` is the theory-mandated, corrigible behavior: "contradiction is a signal
for guided clarification" (`kernel.py` docstring; `ONTOLOGY.md` §2.12). The
kernel does not *guess* when it cannot evaluate the predicate. It hands the
question back to the human owner. This is why the primitive is a predicate and
not a total function into ℝ: a predicate is *allowed to abstain*; a maximizer is
not, and an abstaining maximizer is just a maximizer with a hidden default.

---

## 6. The one open question (honest boundary)

The predicate as stated quantifies over `boundaries_crossed(action)` — the
boundaries an action crosses **now**. There is a class of actions that cross
**no current boundary** yet build future dependency or concentrate power:

- an action that creates a `DependencyIndex` increase (`FORMAL_SPEC.md` §D) — a
  party becomes structurally unable to exit later, though no right is violated
  today;
- an action that concentrates control (the `machine_coalition_dominion` /
  `seeks_dominion(coalition)` shape, but *below* the dominion threshold —
  `FORMAL_SPEC.md` §C, OPEN) so that no single present crossing is illegitimate.

**The question:** are such actions **illegitimate** (the predicate should range
over *future* foreseeable boundary crossings, making this a kernel/DENY concern),
or are they merely **low-freedom** (legitimate now, and rightly *penalized in the
research compass* via `DependencyIndex`/concentration, but ALLOW at the kernel)?

The two answers have opposite engineering consequences:

- *Illegitimate* ⇒ the kernel must model foreseeable future dependency, which
  imports prediction (non-determinism) into the gate — exactly what §4 forbids.
- *Low-freedom* ⇒ the kernel stays clean and deterministic; concentration is a
  ranking penalty, and a human `DEFER` is the escape hatch when concentration is
  egregious but no present right is crossed.

This kernel currently takes the **low-freedom** reading by default (dependency and
concentration live in the compass measures, not in `check_legitimacy`), because
the alternative would compromise the determinism the primitive depends on. **But
this is a provisional engineering choice, not a ruling.** Whether building future
dependency without a present consent violation is *itself* a consent violation —
because it forecloses the exit right (A3) the consent logic requires to remain
`revocable` — is a question for the **source theory**, not for this spec. It is
the boundary at which the legitimacy predicate's *scope* (present vs foreseeable
boundaries) must be fixed by the theory's author. Until then, the kernel does the
honest thing: it does not pretend the question is closed, and it leaves dependency
in the research layer where a wrong answer penalizes rather than wrongly forbids.

---

*Stage 0 deliverable, Freedom Decision Kernel. Theory: نظریه آزادی (Theory of
Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0). Engineering: Ali Pourrahim.
The two are kept separate, always.*
