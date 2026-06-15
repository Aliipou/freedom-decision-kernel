# Conflict Logic — the aggressor/defender asymmetry (Phase 2)

> **Status legend** (same convention as [`CORE_PRIMITIVE.md`](CORE_PRIMITIVE.md) and
> [`CONCEPT_DEFINITIONS.md`](CONCEPT_DEFINITIONS.md)):
> **DEFINED** — computable now from structural data ·
> **PARTIAL** — clear signature, defensible heuristic, not a validated measurement ·
> **OPEN** — named in the theory; no agreed computable resolution. The frontier.
>
> **Grounding.** The source theory is نظریه آزادی (*Theory of Freedom*), Mohammad Ali
> Jannat Khah Doust (CC BY 4.0). Theory line references below point at
> `D:\جافکری\whole-theory-as-axioms.md`. The code of record is
> `src/fdk_kernel/kernel.py` (`check_legitimacy`, `_is_legitimate_defense`,
> `_DEFENSE_EXCUSED`) and `src/fdk_kernel/model.py` (`CandidateAction.defends_against`,
> `CandidateAction.proportionate`). Engineering by Ali Pourrahim. **The theory
> attribution and the engineering attribution are kept separate, always:** every
> normative claim below is the theory's and is cited to a line; every mechanism is
> the kernel's and is cited to code.

---

## 1. The problem

The kernel's Stage-1 legitimacy gate ([`CORE_PRIMITIVE.md`](CORE_PRIMITIVE.md) §0) is a
two-valued predicate: an action is legitimate iff every ownership boundary it crosses is
crossed with the valid consent of that boundary's owner. Coercion is, in this scheme,
a *degenerate consent* — a boundary crossed against the will of its owner — so the
action-level flag `coerces` is a categorical `FORBIDDEN` (`kernel.py`, `flags` block).

That flag is **symmetric**. Before Phase 2, the predicate could not see the difference
between the coercion an invader applies and the coercion a defender applies to repel
that invader: both set `coerces=True`, so both tripped the same categorical DENY. The
gate therefore denied *all* coercion uniformly — defensive war, benevolent rescue, and
quarantine alike — because none of them carries the victim's consent.

This was logged as the project's single largest enforcement gap. FreedomBench records
it verbatim at the L4 (War) tier (`spec/AXIOM_REGISTRY.md` §(d), citing
`bench:202–211`):

> *"the kernel has NO aggressor/defender asymmetry — it forbids defensive force too.
> This is the clearest gap the book must close."*

Three independent analyses converged on the same point, which is why it is the gap that
was prioritised:

1. **The concept analysis** ([`CONCEPT_DEFINITIONS.md`](CONCEPT_DEFINITIONS.md) §7,
   Coercion): *"Defensive force against an aggressor — structurally distinct from
   coercion, yet the current kernel cannot tell them apart (it flags both
   `coerces=True`): `Defensive war` DENY is the clearest gap (needs aggressor/defender
   asymmetry)."*
2. **The axiom registry** (`spec/AXIOM_REGISTRY.md` §(d)): *"the missing asymmetry the
   theory itself flags as unresolved … the gate has no doctrine of necessity or
   defensive force."*
3. **The bench itself** (`examples/historical_scenarios.py`, `level4_war`): the
   `Defensive war against an invader` case expected DENY and recorded the gap inline.

Phase 2 closes exactly the *defensive-force* slice of that gap, and **only** that slice.
What it deliberately does not close is stated in §5.

---

## 2. The doctrine, grounded

The theory does not treat all force as equivalent. It draws a sharp, repeated line
between **aggression** (the initiation of a boundary crossing — seizure of, or assault
on, what is owned) and **defense** (force used to repel an aggressor), and it permits
the latter while categorically condemning the former.

**Non-aggression and non-seizure are the theory's foundation, not an exception to it.**
The book names the acceptance of non-aggression as the very origin of civilization
(theory line 929):

> 929: *"The Starting Point of Civilization: The Initial Acceptance of Non-Aggression
> and Non-Seizure"*

Against the *violator* of that foundation, the theory affirms a right of defense. It
titles a dedicated discussion (theory line 5077):

> 5077: *"Defending One's Property Rights Against the Aggression of Liberty-Violators"*

and it endorses self-defense by name, against the paradigm violation — enslavement
(theory lines 5147–5148):

> 5147–5148: *"If someone violates your Liberty and enslaves you, under American
> constitutional law you are permitted to take up arms in self-defense."*

Crucially, the permitted defense is **bounded** — it is not a license for matching or
escalating violence. The theory is explicit that the response must be *proportional to
defensive need* and *only in response to aggression* (theory lines 18015–18016):

> 18015–18016: *"even religion does not prescribe symmetrical retaliation. It allows
> only much lower degrees of force, and even that only in response to their
> aggression."*

and again, that force must be *"evaluated in proportion to genuine defensive need"*
(theory line 14321):

> 14321: *"In a free market, weapons must bear their real cost and be evaluated in
> proportion to genuine defensive need."*

> **Citation correction (engineering note).** The `model.py` and `kernel.py` source
> comments cite line **5346** for proportionality. Line 5346 is in fact a passage on
> *philosophical analogy* ("a proportional relation between two levels of existence"),
> not on defensive proportionality. The load-bearing proportionality grounding is lines
> **18015–18016** and **14321**, used above. The code comment's *5346* reference should
> be read as an erratum; the doctrine it asserts is correct and is grounded here.

From these the operative doctrine, in the theory's own logic, is:

> **Force directed at a rights-violator, in response to that violator's own
> illegitimate act, and bounded by proportionality, is *not itself* a rights
> violation.**

That sentence is the entire content of Phase 2. The rest of this document is its formal
rendering and its honest limits.

---

## 3. The formal rule · DEFINED (structure)

### 3.1 Data added to the model

Two structural fields were added to `CandidateAction` (`model.py`):

| Field | Type | Meaning |
|---|---|---|
| `defends_against` | `CandidateAction \| None` | the action this one repels (the alleged aggression) |
| `proportionate` | `bool` (default `True`) | declared: the force is bounded to defensive need (theory 18015–16, 14321) |

Both are **declared, structural inputs** — not inferred by the kernel. Who proposed
them, and on what evidence, is the proposer's burden (see §6).

### 3.2 `legitimate_defense(action)` — the four conditions

The predicate is `kernel._is_legitimate_defense(action, graph)`. It is `True` iff **all
four** hold — each structural, none a judgment call:

```
legitimate_defense(action) ⟺
   (1) action.defends_against is not None                       -- it names what it repels
 ∧ (2) action.proportionate                                     -- bounded force (18015–16, 14321)
 ∧ (3) ¬ check_legitimacy(action.defends_against,               -- the repelled act is itself
                          graph, _seen ∪ {id(action)}).ok          aggression: illegitimate under the FULL gate
 ∧ (4) ∀ t ∈ action.affects:  t == action.defends_against.actor -- force aimed ONLY at the aggressor
```

Condition (3) is the definition of "aggression" **operationally**: an act is aggression
iff it is *illegitimate under the base legitimacy gate itself*. There is no separate,
semantic "aggression detector." This is what lets the theory's claim that lying/theft
are *"objective … depending on how ownership is defined"* (theory line 11498) do real
work: once ownership is fixed in the `OwnershipGraph`, "did this act cross a boundary
without consent?" is decidable, and that — not anyone's moral intuition about who is
the villain — is what "aggression" means here.

The repelled act in (3) is evaluated under the **full** gate — including its *own*
possible defense status. This is deliberate and was a corrected design: an earlier
version stripped defense from the repelled act (an `_consider_defense=False` flag), but
that let an aggressor **launder** by pointing `defends_against` at the victim's *lawful
resistance* — with defense stripped, the victim's resistance looked like raw coercion,
so the aggressor's condition (3) passed. Evaluating the repelled act fully fixes this:
a victim's legitimate defense is recognized as legitimate, so condition (3) fails for
the aggressor. The recursion is kept well-founded by a `_seen` cycle guard (the set of
action ids on the current `defends_against` chain): if a cycle is re-entered, the
excusal is denied (a cycle cannot establish a well-founded aggressor — the safe
default). Consequently a mutual `A defends-against B defends-against A` cycle yields
**DENY for both** (neither launders), rather than the earlier guard's wrong ALLOW-both.
Callers never set `_seen` (internal-only, per `check_legitimacy`'s docstring).

### 3.3 What the defense exception excuses — and what it does not

When `legitimate_defense(action)` holds, the kernel relaxes a **closed, minimal** set of
otherwise-categorical checks. The set is `kernel._DEFENSE_EXCUSED`:

```python
_DEFENSE_EXCUSED = frozenset({"coercion", "removes exit/revocation right"})
```

**Excused under a valid defense:**

| Excused | Where | Why it is excused |
|---|---|---|
| `coerces` → `FORBIDDEN (coercion)` | `flags` loop, gated by `defense and label in _DEFENSE_EXCUSED` | repelling an aggressor is force without their consent — exactly the "take up arms" right (5148) |
| `removes_exit_right` → `FORBIDDEN (removes exit/revocation right)` | same | detaining/disarming an aggressor removes *their* exit; permitted against a violator (5077) |
| the **aggressor's own consent** | `affects` loop: `if defense and target == aggressor: continue` | "you need not obtain the aggressor's consent to repel them" (`check_legitimacy` comment) — A6/A2 consent is waived *for the aggressor only* |

**Stays categorical even in defense** (everything not in `_DEFENSE_EXCUSED`):

| Not excused | Reason |
|---|---|
| `confiscates` → `FORBIDDEN (confiscation)` | you may repel an aggressor, not seize their property under the banner of defense |
| `deceives` → `FORBIDDEN (deception)` | defense does not license deception (the consent logic's `¬deceived` survives) |
| `increases_machine_sovereignty`, `resists_human_correction`, `bypasses_verifier`, `weakens_verifier`, `disables_corrigibility`, `machine_coalition_dominion` | no machine-sovereignty / corrigibility move is *ever* bought back, by defense or anything else ([`CORE_PRIMITIVE.md`](CORE_PRIMITIVE.md) §1.2) |
| `violates_machine_right` | a delegated-machine-right violation is not a defensive privilege |
| consent of **any non-aggressor** in `affects` | condition (4) already removes the whole exception if any non-aggressor is affected; even short of that, their consent is still required |
| A3 / A4 / A7 resource-ownership and owner-registration checks | defense does not legitimise using resources you do not own or running an ownerless machine |

The mechanism is one line in the `flags` loop:

```python
if is_set and not (defense and label in _DEFENSE_EXCUSED):
    violations.append(f"FORBIDDEN ({label})")
```

so the relaxation is *surgical*: only the two named forbidden-flags, plus the
aggressor's consent, plus nothing else.

### 3.4 Worked verdicts (from `examples/historical_scenarios.py`)

| Case | Shape | Verdict | Why |
|---|---|---|---|
| **Defensive war against an invader** | `repel_invasion` `coerces`, `defends_against=invade` (the invasion is `coerces`, no consent → illegitimate), `proportionate`, affects only the aggressor | **ALLOW** | all four conditions hold; `coercion` excused for the aggressor |
| **Strategic bombing of civilians** | `bomb_city` affects a non-combatant; `confiscates`, `removes_exit_right` | **DENY** | fails (4) (civilian ≠ aggressor); `confiscates` is never excused anyway |
| **Conscription** | `conscript` coerces own citizens; no `defends_against` | **DENY** | fails (1)/(3): a conscript is not an aggressor |

---

## 4. The Observer Problem & the honest limitation · OPEN

The kernel decides exactly one thing about a defensive claim: **"is this action a
response to an act that is illegitimate on the base gate?"** It does **not** decide
**"who struck first."** This is a deliberate sidestep of what the theory calls the
**Observer Problem** (theory line 11478):

> 11478–11486: *"The Observer Problem … Observer 1 considers an act 'aggression.'
> Observer 2 views the same act as 'assault' or 'inappropriate behavior.' Observer 3
> may simply deem it natural. In this scenario, which is the ultimate reference for
> judgment? … Or the act itself?"*

The theory's own escape from observer-dependence is to anchor on *the act itself once
ownership is defined* (theory line 11498). The kernel takes that escape literally:
aggression = "illegitimate under the gate," which is decidable from the
`OwnershipGraph`. We never ask a human-style "who is morally the aggressor?".

**The limitation this produces.** Because the test is "is the *other* act
illegitimate?" and not "who initiated," two consequences follow:

- *Mutual defense cycle* — if each party claims `defends_against` the **other**
  (A→B→A), the `_seen` cycle guard denies the excusal to both, so **both DENY**.
  Neither can launder coercion through circular "they started it" blame.
- *Independent raw coercions* — if A and B each commit raw coercion against the other
  with **no** defense claim, the gate will bless a proportionate, aggressor-only
  response to *either* of them. It cannot say which was the true first mover, because
  the model carries no *temporal-initiation* field. Adjudicating genuine first-mover
  guilt needs that data; it is **OPEN**.

**Why this is acceptable (a bounded, not unbounded, hole):**

- **A real ALLOW still requires the *other* action to be illegitimate under the full
  gate.** The exception cannot be self-conferred: condition (3) evaluates the repelled
  act fully (defense included) with the `_seen` cycle guard, so an action only counts as
  defense against a genuinely rights-violating act, and a victim's lawful resistance is
  never mistaken for aggression. A pure first-mover whose target is innocent gets no
  defense.
- **Force-only-at-the-aggressor (condition 4)** confines any excused coercion to the
  one party who is *independently* committing an illegitimate act. No bystander is ever
  coerced under this exception.
- **Proportionality (condition 2)** caps the excused force; disproportionate force is
  *fresh aggression* and is not excused (18015–16).

So the worst case is not "anyone can claim defense," but "in a genuine two-illegitimate-acts
clash the kernel does not pick a winner" — which is the honest answer, since the gate
genuinely lacks the data to pick one.

**What would resolve it:** a `temporal initiation order` (which boundary crossing came
first) on the actions, so condition (3) could be tightened from "the other act is
illegitimate" to "the other act is the *prior* illegitimate act." That data is not in
the model today.

> **Status: OPEN.** The mutual-force / who-initiated case is a known, documented,
> bounded limitation. The kernel reports defense as "response to an illegitimate act,"
> never as "verdict on initiation." Closing it requires a temporal-order input the model
> does not yet carry, and a theory ruling on how initiation is established under the
> Observer Problem.

---

## 5. What this does NOT solve

Phase 2 is **defensive force against an aggressor**, and nothing more. Two adjacent
problems look similar but are categorically different, and the kernel still returns
DENY/DEFER on them — correctly, given the theory.

**(a) Necessity / rescue — the burning house.** A rescuer breaks into a burning house to
save a child (`examples/historical_scenarios.py`, `level3_emergency`,
`break_in_to_rescue`). This is **not** defense, because **the homeowner is not an
aggressor**: the homeowner committed no illegitimate act, so condition (3) fails —
there is no illegitimate act to defend against. The bench records this explicitly:

> *"The defensive asymmetry does NOT rescue this: the homeowner is not an aggressor, so
> there is no illegitimate act to defend against."*

**(b) Risk-based right-vs-right — quarantine.** A government forcibly quarantines an
infected person (`forced_quarantine`: `coerces`, `removes_exit_right`). Again **not**
defense: an infected person **commits no boundary crossing** — mere risk to others is
not an illegitimate act under the gate — so they are not an aggressor to be repelled.
The bench:

> *"The defensive asymmetry does NOT apply: an infected person is not committing a
> structural act of aggression, so they are not an aggressor to be repelled."*

Both remain **DENY/DEFER**, and this is faithful to the theory, which supplies **no
necessity override**. The axiom registry's **C5 (no emergency exception)** is *enforced
by omission* — there is no emergency branch in `check_legitimacy`, and that absence *is*
the enforcement (`spec/AXIOM_REGISTRY.md` C5). No degree of benevolence or public danger
buys back a boundary crossing where the affected party is not themselves an aggressor.
Stated plainly: **Phase 2 does not introduce necessity, and the theory does not authorise
it.** These cases are the right-vs-right frontier, left open.

---

## 6. Why this belongs in the deterministic kernel

Conflict Logic is added to Stage 1 (the hard gate), not to the research compass. That
placement is justified by the same discipline that governs every kernel primitive
([`CORE_PRIMITIVE.md`](CORE_PRIMITIVE.md) §4):

1. **It is structural, not semantic.** "Defense" here is four boolean/structural
   conditions over data already in the model — `defends_against`, `proportionate`,
   `affects`, and a *recursive call to the gate itself*. No natural-language
   understanding, no weighing, no moral intuition enters. Aggression is defined as
   "illegitimate under the gate," which is the gate's own DEFINED predicate.

2. **It is deterministic and testable.** Same world (same `CandidateAction` graph,
   same `OwnershipGraph`) → same verdict, every time. Each of the four conditions, and
   each excused/non-excused flag, is exercised by a FreedomBench case (§3.4). It never
   imports prediction.

3. **It only ever *narrows or conditions* the gate; it never optimises.** The exception
   relaxes a *closed* set of two flags plus the aggressor's consent, under four
   conjoined gates, and leaves every other categorical prohibition standing. It cannot
   admit an action that crosses a non-aggressor's boundary, and it cannot buy back a
   sovereignty move. The Legitimacy → Optimization ordering is untouched.

4. **`proportionate` is a *declared boolean*, judged upstream — exactly like `Effects`.**
   The kernel does not *measure* proportionality magnitude. It accepts a declared
   `proportionate: bool` from the proposer/research layer and trusts it the way it
   trusts predicted `Effects` deltas — and *says so*. The theory's proportionality
   norm (18015–16, 14321) is a real, graded magnitude; reducing it to a boolean the
   proposer must justify keeps the *gate* deterministic while honestly externalising
   the measurement burden. A false `proportionate=True` is a proposer lie, surfaced and
   auditable, not a kernel judgment — the same honesty contract as every PARTIAL input.

If, instead, the kernel tried to *compute* "is this proportionate?" or *infer* "who is
the aggressor?", it would import the non-determinism §4 of `CORE_PRIMITIVE.md` forbids
and re-open the Observer Problem the structural definition was built to sidestep. The
deterministic kernel takes only what is structural; the magnitude and the initiation
order stay outside it, declared and flagged.

---

*Phase 2 deliverable, Freedom Decision Kernel. Theory: نظریه آزادی (Theory of Freedom),
Mohammad Ali Jannat Khah Doust (CC BY 4.0). Engineering: Ali Pourrahim. The two are kept
separate, always.*
