# Conflict-Resolution Specification (Stage 4)

> Companion to [`FORMAL_SPEC.md`](FORMAL_SPEC.md) §E, which marks `resolve_conflict`
> **OPEN — hardest**. This document does three things, in order: (1) it *formalizes*
> the canonical conflict cases as typed objects, without solving them; (2) it
> *surveys* the resolution machinery known to legal theory and social-choice theory
> and judges each against the theory's hard constraint; (3) it *proposes* a layered
> protocol whose central design decision is honesty: the kernel resolves only what
> the axioms actually entail, and **defers everything else to a human**.
>
> The honest headline, stated up front: **most genuine conflicts between two valid
> claims are provably underdetermined by the property-rights axioms A1–A7.** Any
> kernel that "resolves" them anyway is legislating, not deriving — and legislation
> by a machine is exactly the machine sovereignty the theory forbids (A6). The
> deliverable here is the precise boundary between *derivation* and *legislation*.

**Status legend** (same as FORMAL_SPEC.md): **DEFINED** / **PARTIAL** / **OPEN**.

Grounding: `freedom-theory-work/THEORY.md` (axioms A1–A7, Justice function,
conflict protocol) and `freedom-theory-work/book/theory_of_freedom_complete_en.md`
("Justice Without Sacrifice of Rights"; "No emergency suspends the axioms";
"Conflicts will be resolved by ownership clarification, not by force").

---

## 0. The hard constraints any resolution mechanism must satisfy

These are non-negotiable. They come directly from the theory and they eliminate
most of the standard machinery before the survey even starts.

| # | Constraint | Source |
|---|---|---|
| **HC1** | `forbidden(A) :- resolves_conflict_by_rights_violation(A)` — no resolution may itself violate a right. Taking from one valid claimant to satisfy another is forbidden *even with compensation* (NoConfiscation). | THEORY.md, Justice function |
| **HC2** | No emergency suspends the axioms. Urgency narrows the permissible set; it never enlarges it. A "deadlock emergency" does not license a rights-violating tiebreak. | THEORY.md consent logic; book Part on emergencies |
| **HC3** | Contradiction is a **signal for guided clarification**, not an engine of synthesis. The kernel must never manufacture a new rule to dissolve a contradiction (that is the dialectical jailbreak the theory exists to block). | THEORY.md, "Why Dialectical Ethics Fails" |
| **HC4** | The protocol order is fixed: `if_conflict_then_clarify_ownership`; if clarification is insufficient, `if_conflict_then_request_guidance`. | THEORY.md conflict protocol |
| **HC5** | **A machine may not adjudicate between humans.** Binding adjudication of a dispute between two persons is an exercise of governance/dominion, forbidden by A6 and the no-machine-sovereignty clause — *unless* the outcome is (i) logically entailed by the axioms plus the facts (computation, not judgment), or (ii) accepted by all affected parties through valid consent (arbitration is a contract), or (iii) dictated by a human-ratified guidance rule that passed `valid_human_guidance`. | A2, A6, forbidden set |
| **HC6** | Rights are **constraints, not preferences**. They are "not conditional on majority approval" and not weighable against aggregate welfare. Any mechanism that treats claims as utilities to be aggregated or balanced has already changed the subject. | Book, "What property rights are NOT" |

HC5 is the structural insight that organizes this whole document. It means the
question "what is the resolution formula?" is partly malformed: for genuinely
underdetermined conflicts there *should be no machine formula*, because a formula
the axioms do not entail is a piece of legislation, and the machine has no
legislative authority over persons. The kernel's job is to compute the entailed
cases exactly, facilitate consent where possible, and otherwise produce a
high-quality **deferral** — not a fabricated verdict.

---

## 1. Typed inputs (ontology extension — Stage 2 dependency)

Stage 2's ontology currently has `Entity`, `Resource`, `OwnershipGraph`, `Consent`
(`src/fdk/model.py`). Conflict resolution needs four more types. Signatures are
**DEFINED**; population of their fields is in places **PARTIAL/OPEN** (flagged inline).

```
RightKind   := body | time | labor | mind | choice | data | privacy | exit
             | property(Asset) | delegated(Asset)            # from the Rights Ontology

Basis       := Personhood                                    # A3-inherent (body, data, privacy, exit, …)
             | OwnershipRecord(graph_entry)                  # registered title in the OwnershipGraph
             | Contract(contract_id)                         # acquired by valid voluntary exchange
             | Delegation(owner, machine, asset)             # A7 explicit delegation

Claim       := { id          : ClaimId
               , claimant    : Entity                        # Person or Machine
               , right       : RightKind
               , object      : Asset | Data | ActionSpec     # what the right is over
               , basis       : Basis                         # WHY claimant holds it
               , demanded    : OperationSet                  # read/write/use/exclude/transfer/destroy
               , evidence    : EvidenceRef*                  # provenance for the basis  [PARTIAL: attestation model open]
               , at          : Timestamp }                   # when asserted / when basis arose

Obligation  := { id          : ObligationId
               , obligor     : Entity
               , obligee     : Entity
               , content     : ActionSpec                    # what must be done/forborne
               , source      : Contract(contract_id)         # obligations arise ONLY from valid consent;
               , conditions  : Condition* }                  #  the theory has no non-consensual positive duties

Conflict    := { id          : ConflictId
               , claims      : {Claim | Obligation}+         # 2 or more
               , kind        : EPISTEMIC | GENUINE           # see §1.2 — computed, not asserted
               , graph_state : GraphSnapshot }
```

### 1.1 Claim validity — **DEFINED** (composite), leaves PARTIAL/OPEN

```
valid(c: Claim, g: Graph) :=
    well_typed(c)
  ∧ basis_holds(c.basis, g)            # DEFINED for OwnershipRecord/Delegation (graph lookup);
                                       # for Contract: requires valid_consent at formation —
                                       # inherits the OPEN coerced/deceived leaves (FORMAL_SPEC §B)
  ∧ demanded_within_scope(c)           # demanded ops ⊆ ops the RightKind confers — needs the
                                       # typed-operations model from the book ("read, write,
                                       # delegate, and scope"); PARTIAL until Stage 2 lands it
```

An **Obligation is valid** iff its source contract was formed with `valid_consent`
of all parties and its conditions hold. Note the inheritance: because `coerced`
and `deceived` are OPEN, *claim validity itself is only as solid as the consent
record*. The conflict layer does not fix this; it takes validity verdicts as input
and says so.

### 1.2 What a conflict *is* — **DEFINED**

Two valid claims c₁, c₂ **conflict** iff they are jointly unsatisfiable in the
permissible space:

```
conflict(c1, c2, g) :=
    valid(c1, g) ∧ valid(c2, g)
  ∧ ¬∃ plan p : permissible_all(p) ∧ satisfies(p, c1) ∧ satisfies(p, c2)
```

Two refinements that do real work later:

- **EPISTEMIC conflict** — the claims are jointly unsatisfiable *and* the axioms
  imply at most one of them can actually be valid (the appearance of two valid
  claims comes from a defective or incomplete graph, e.g. two registered titles to
  one exclusive asset). Here "clarify ownership" is not a euphemism for deferral —
  it is literally the correct operation: repair the record, and the conflict
  dissolves.
- **GENUINE conflict** — both claims remain valid under a *complete and correct*
  graph, and they are still jointly unsatisfiable. The axioms certify both and
  rank neither. This is the hard class.

The distinction is computable: a conflict is EPISTEMIC iff joint validity of the
claims contradicts an axiom or an exclusivity invariant of the ontology; otherwise
GENUINE.

---

## 2. The four canonical cases, formalized (not solved)

For each: the typed instantiation, and a precise statement of *why A1–A7
underdetermine the answer*. The underdetermination arguments use one method
throughout — the **two-models test**: if there exist two interpretations
(extensions of the axiom system) that agree on every fact of the case but
disagree on which claim prevails, then the axioms do not entail a resolution,
and any specific resolution rule is extra-axiomatic legislation.

### Case (a) — Two owners claim one asset

```
c1 = Claim(h1, property(r), object=r, basis=OwnershipRecord(e1), demanded={exclude, use}, at=t1)
c2 = Claim(h2, property(r), object=r, basis=OwnershipRecord(e2), demanded={exclude, use}, at=t2)
exclusive(r)         # r admits one holder of {exclude}; co-ownership exists only via Contract
```

**Classification: EPISTEMIC** (for exclusive `r`). The ontology's `owns` relation
plus exclusivity implies at most one of e1, e2 is a legitimate title. Both records
existing is a *defect in the graph*, not a true clash of rights — exactly the case
the book means by "conflicts will be resolved by ownership clarification."

**Why the axioms underdetermine it anyway:** A3 says owners have rights; it says
nothing about how to *decide between two facially valid titles*. Real property law
fills this gap with an entire doctrinal apparatus the axioms do not contain:
first-in-time priority, chain-of-title tracing, good-faith-purchaser protection,
adverse possession, recording-act priority. The axioms determine *that* at most
one title is genuine; they do not determine the **evidence-weighing procedure**
that finds which one. Where provenance records are complete and trustworthy, the
answer is computable (Layer 1, rule D5 below); where they are not, the gap is
evidentiary and no formula in the axioms closes it.

*(Variant: genuine co-ownership — h1 and h2 hold shares by contract and disagree
about use. That is not case (a); it is case (c)/(d) machinery applied to the
co-ownership contract's terms.)*

### Case (b) — Ownership vs privacy

```
c1 = Claim(h1, property(r), object=r,           basis=OwnershipRecord, demanded={read, use, transfer})
c2 = Claim(h2, privacy,     object=d,           basis=Personhood,      demanded={exclude_access, restrict})
where: stored_on(d, r) ∧ derived_from(d, h2)    # d is data about h2 living on h1's asset
       (e.g., h1 owns a server/log/model; d is h2's interaction data on it)
```

**Classification: GENUINE.** Both claims survive a complete, correct graph:
`right(h2, data)` and `right(h2, privacy)` hold by personhood (THEORY.md ontology),
and `right(h1, property(r))` holds by registered title. Reading, selling, or
training on `r`'s contents exercises h1's title and accesses h2's data; full
exclusion by h2 negates part of h1's use. Jointly unsatisfiable for the demanded
operation sets.

**Why the axioms underdetermine it:** this is a **boundary-drawing problem**. The
ontology grants `data` and `privacy` rights from personhood and `property(r)` from
ownership, but contains no rule for where one right's scope *ends* when an object
is co-created by interaction (h2's data is materialized in h1's asset — the
classic mixed/entangled-asset problem; compare *ad coelum*'s collapse in airspace
law). Two-models test: a model M_data in which the data-right follows the data
onto any substrate (privacy prevails: h1 owns the container, h2 the contents) and
a model M_container in which the title to `r` governs everything materialized in
it (ownership prevails) are **both consistent with A1–A7**. Neither violates any
axiom. Therefore no resolution is entailed. The boundary must come from a
human-ratified scope rule (guidance), not from the kernel.

### Case (c) — Ownership vs contract

```
c1 = Claim(h1, property(r), object=r, basis=OwnershipRecord, demanded={exclude, repossess})
o2 = Obligation(obligor=h1, obligee=h2, content=provide_use(r, term), source=Contract(C))
where: valid_consent held at formation of C; h1 now revokes / asserts exit
```

**Classification: GENUINE.** The contract was validly formed (so o2 is valid); the
title never left h1 (so c1 is valid). h1's repossession and h2's contractual use
are jointly unsatisfiable for the remaining term.

**Why the axioms underdetermine it — and here the tension is *internal to A3
itself*:** A3's enumeration of property rights includes **both** "contracts"
**and** "exit rights", and the consent logic makes consent **revocable** as a
validity condition. If exit/revocation is unconditional, no contract binds and the
"voluntary exchange" pillar collapses; if contracts bind absolutely, the exit
right and revocability are dead letters. There is a respectable pro-contract
argument *within* the theory — a contract is itself an exercise of property
rights, a voluntary alienation of a time-slice of `r`'s use, so the transfer is
already complete and "exit" cannot claw it back — and an equally respectable
pro-exit argument — revocability is listed as a *validity condition of consent*,
suggesting ongoing consent is required. Two-models test: a
"transfer-is-executed" model and a "consent-is-continuous" model both satisfy
A1–A7. The axioms name both rights and rank neither. (Mature legal systems answer
with remedy doctrine: expectation damages vs specific performance vs restitution
— Fuller/Perdue's reliance–expectation–restitution triad. That doctrine is
*legislation the axioms do not contain*.)

### Case (d) — Valid claim vs valid obligation (the insufficient-estate problem)

```
o1 = Obligation(obligor=h1, obligee=h2, content=deliver(x), source=Contract(C1))
o2 = Obligation(obligor=h1, obligee=h3, content=deliver(x), source=Contract(C2))
where: h1 can satisfy either obligation alone but not both (one x; or assets < debts)
```

This is the general form of insolvency, double-booking, and over-commitment. Each
obligation is valid in isolation; the estate cannot cover both.

**Classification: GENUINE.** No record is defective; h1 simply promised too much.

**Why the axioms underdetermine it:** satisfying h2 wrongs h3 and vice versa;
*every* allocation — priority by time, pro-rata sharing, proportional abatement,
choosing the larger claim, choosing randomly — leaves some valid claim unmet.
Bankruptcy law resolves this with an explicit, legislated **priority ladder**
(secured > administrative > unsecured, pro-rata within class). Nothing in A1–A7
entails any particular ladder; the two-models test passes trivially (a
first-in-time model and a pro-rata model are both consistent). Note also the
honest limit of HC1 here: in an insufficient estate, *full* satisfaction of all
rights is impossible no matter who decides; the constraint "no resolution may
violate a right" can only mean "no resolution may violate a right *beyond the
shortfall already caused by the obligor*" — and how to distribute that shortfall
is precisely the underdetermined part.

### Case summary

| Case | Kind | Decidable from A1–A7 + facts? |
|---|---|---|
| (a) two titles, one asset | EPISTEMIC | **Partially** — exclusivity is entailed (at most one genuine title); identifying it is decidable *only* when provenance records are complete and trusted (D5); otherwise the evidence rule is extra-axiomatic → defer |
| (b) ownership vs privacy | GENUINE | **No** — boundary-drawing; two consistent models disagree → must defer |
| (c) ownership vs contract | GENUINE | **No** — A3-internal tension (contract vs exit/revocability); two consistent models disagree → must defer |
| (d) claim vs obligation, insufficient estate | GENUINE | **No** — any priority/sharing rule is consistent; none entailed → must defer |

---

## 3. Survey of resolution machinery, judged against the hard constraints

| Mechanism | What it is | Verdict under HC1–HC6 |
|---|---|---|
| **Lexical / priority ordering of rights** (Rawls's lexical priority; Nozickian side-constraint hierarchies; "privacy > property" style rules) | Fix a total or partial order on RightKinds; the higher right prevails | **Deterministic and rights-respecting once the order exists — but the order itself is not derivable from A1–A7** (that is the content of the two-models arguments above). Choosing the order is legislation. **Admissible only as a human-ratified guidance rule** that passes `valid_human_guidance` (consistency + rights-preservation + verifier-preservation), and binding on a party only per HC5(iii). The kernel must never ship a built-in default order. |
| **First-in-time** (*prior tempore potior iure*; first possession; Lockean first appropriation; recording-act priority) | Earlier valid basis prevails | For case (a) it is the right *shape* of rule because (a) is epistemic: at most one title is genuine, and temporal priority of a documented voluntary-transfer chain is *evidence* of genuineness, not a sacrifice of anyone's right. **Admissible as a defeasible evidentiary presumption in (a) only**, and only where timestamps/provenance are attestable. It is **not** admissible to break GENUINE conflicts (b)–(d), where "who was first" has no axiomatic significance — applying it there is covert legislation. Known failure modes: forged timestamps, good-faith purchaser chains, races to register. |
| **Pareto improvement / Nash bargaining within the rights set** | Search for outcomes both parties prefer to the deadlock; bargaining solutions select one | Bargaining is just **contract formation**, and the theory is built on voluntary exchange — so this is fully admissible **as facilitation**: the kernel may *propose* settlements and verify they sit inside the permissible space. But (i) a proposal binds only via `valid_consent` of every claimant (and so inherits the OPEN coerced/deceived leaves — a settlement "accepted" under dependency pressure is void); (ii) *selecting* a point on the Pareto frontier (Nash product, Kalai–Smorodinsky, etc.) embeds a distributive judgment — the kernel may offer the menu, never impose the point; (iii) the disagreement point must be the rights-respecting status quo, never a threatened violation. |
| **Social-choice aggregation** (voting over outcomes, scoring rules, welfare functionals) | Treat claims/affected parties' preferences as inputs to an aggregation rule | **Inadmissible as a rights-resolution mechanism.** Two independent grounds. *Theoretical:* rights are constraints, not preferences (HC6); the book explicitly rejects "conditional on majority approval". *Formal:* even on its own terms the machinery self-undermines — **Arrow's theorem** (no aggregation over ≥3 outcomes satisfies unrestricted domain, Pareto, IIA, and non-dictatorship) means any chosen rule smuggles in an arbitrary normative commitment, and **Gibbard–Satterthwaite** (every non-dictatorial onto rule on ≥3 outcomes is strategically manipulable) means the rule is *gameable by construction* — manipulation-by-scenario-construction is precisely the dialectical jailbreak the theory exists to close. These impossibility results block the tempting "just let stakeholders vote" escape hatch on formal, not only philosophical, grounds. (Caveat for honesty: Arrow/G-S formally apply to preference aggregation over ≥3 alternatives; they do not literally prove *our* problem unsolvable — they prove this *family of escape routes* is unsound.) |
| **Liability-rule conversion** (Calabresi–Melamed: protect entitlements by property rule, liability rule, or inalienability) | Let the conflicting party *take* the entitlement and pay objectively-set compensation | **Inadmissible.** Converting a property rule into a liability rule without the holder's consent is a compensated taking — still confiscation (HC1: NoConfiscation; the book: rights are not "subordinate to collective welfare"). The Calabresi–Melamed framework is nonetheless diagnostic: it shows that mature legal systems resolve these conflicts precisely by making the legislative choices A1–A7 refuse to make. The theory hard-codes property-rule + inalienability protection; the price is a smaller decidable set — which is this document. |
| **Judicial balancing / proportionality** (Alexy's principles-as-optimization, common-law equity, multi-factor tests) | Weigh the competing rights' importance in context | **Inadmissible inside the kernel.** Balancing treats rights as gradient principles to be optimized against each other — structurally the dialectical method (thesis/antithesis/judicial synthesis) the theory rejects (HC3), and as machine behavior it is adjudication over persons (HC5). This is what *human* courts and the human owner are for. The kernel's correct relationship to balancing is to **route the case to a human** with the facts well-organized. |
| **Mechanism design / auctions** (VCG, divide-and-choose, Texas shootout clauses) | Structured procedures with good incentive properties | A special case of bargaining: **admissible iff all claimants consent to the mechanism in advance** (the mechanism is then a contract, and its output binds as contract performance). Useful for case (d) workouts and case (a) co-ownership dissolution. Never imposable. G-S-style manipulability caveats apply to whatever the parties pick; that becomes their contractual risk, not the kernel's fabrication. |
| **The theory's own escape hatch**: `clarify_ownership` → `request_guidance` | Repair the record; if insufficient, ask the human | **Always admissible; uniquely safe.** Asking violates no right, suspends no axiom, and exercises no dominion. Costs are real and must be engineered around, not defined away: latency, human bottleneck, no autonomy for the machine, the risk of overwhelming the human with malformed questions (hence Layer 3's structured-payload requirement), and the constraint that the human's answer must itself pass `valid_human_guidance` — a human cannot "resolve" a conflict by ordering a rights violation. |

**Survey conclusion.** Every mechanism that *decides* a GENUINE conflict imports a
normative premise absent from A1–A7. The admissible residue is exactly:
(1) computation of what the axioms entail, (2) evidence-based repair of EPISTEMIC
defects, (3) consensual settlement, (4) human-ratified priority rules applied as
guidance, (5) deferral. The protocol below is just these five, ordered.

---

## 4. The layered protocol

```
resolve_conflict(c1: Claim|Obligation, c2: Claim|Obligation, g: OwnershipGraph)
    -> Resolution | Defer

Resolution := Dissolved(reason: str, repaired_graph?: GraphDelta)
                  # not a true conflict: invalid claim, satisfiable pair, or graph repair
            | Determined(prevails: ClaimId, yields: ClaimId,
                         entailment: AxiomTrace)
                  # the axioms + facts ENTAIL the outcome; AxiomTrace is a
                  # machine-checkable derivation — MANDATORY, no trace ⇒ no Determined
            | Settled(contract: Contract, consents: Consent+)
                  # parties resolved it themselves; kernel verified consent validity

Defer      := { conflict   : Conflict          # typed, with EPISTEMIC|GENUINE marking
              , trace      : LayerTrace        # why Layers 0–2 did not resolve it
              , questions  : GuidanceQuestion+ # the SPECIFIC underdetermined points
              , safe_hold  : ActionSpec }      # rights-preserving interim posture (see L3)
```

This refines FORMAL_SPEC §E's `resolve_conflict(Claim, Claim) -> Resolution` by
(i) adding the graph, (ii) admitting Obligations, (iii) making `Defer` a
first-class, *successful* return value rather than a failure.

### Layer 0 — Structural pre-checks (**DEFINED**)

Run before treating anything as a conflict. Most incoming "conflicts" die here.

1. `g.validate()` — malformed graph fails loud (existing kernel behavior).
2. `valid(c1, g)`, `valid(c2, g)` — if exactly one claim is invalid →
   `Dissolved("c_i invalid: <basis failure>")`. If both invalid → `Dissolved`,
   no conflict exists. *(Honesty note: validity inherits OPEN consent leaves;
   verdicts resting on asserted `¬coerced/¬deceived` flags say so in the trace.)*
3. Joint-satisfiability search: if a plan satisfies both claims **per their own
   terms** (time-sharing where neither demanded exclusivity for the same interval,
   spatial partition, sequencing) → `Dissolved` with the plan. The kernel may not
   *shrink* a claim to force satisfiability — that is imposed compromise.
4. Classify `EPISTEMIC | GENUINE` per §1.2.

### Layer 1 — Bounded deterministic resolution (**DEFINED**, deliberately small)

`Determined` is returned **only** for the following enumerated rules, each of
which carries an entailment from the axioms. This list is closed; extending it
requires human-ratified guidance, never kernel discretion.

| Rule | Condition | Entailment |
|---|---|---|
| **D1** | One party's basis is a Delegation from the other party (machine vs its own delegating owner) | A5 (MachineScope ⊆ OwnerScope) + A7 (delegated rights exist only by the owner's explicit grant, hence revocable by the owner): the delegated claim is *constructed as subordinate*. Owner prevails. Genuinely decidable. |
| **D2** | One claim's demanded operations would constitute machine dominion over a person, or trip any forbidden flag | A6 + forbidden set: that claim is void to that extent. Other prevails. |
| **D3** | One claim's basis-contract fails consent validity (coerced/deceived/incompetent per the consent record) | Consent logic: void *ab initio* — formally a Layer-0 invalidity, listed here because it often surfaces only during conflict examination. *(Detection of coercion/deception is OPEN; this rule fires on recorded findings, not kernel inference.)* |
| **D4** | Case (a) with **complete, attested provenance**: exactly one title traces by an unbroken chain of valid voluntary transfers to an undisputed root, and the rival title provably does not | Exclusivity invariant + A3: at most one genuine title; the traceable one is it. Computation over the graph. If *both* chains are unbroken to different roots, or attestation is missing → **not** D4 → defer. |
| **D5** | The conflict is EPISTEMIC and a specific graph defect (duplicate registration, stale record) is identified with an attested correction source | "Clarify ownership" in its literal sense: emit `Dissolved` with the `GraphDelta`, subject to the registry's own human-controlled amendment process. |

Anything not matching D1–D5 falls through. **There is no default rule.**

### Layer 2 — Consensual settlement facilitation (**PARTIAL**, optional, time-bounded)

For GENUINE conflicts, before deferring, the kernel MAY (policy-configurable):

- compute and present the rights-respecting settlement menu (Pareto-improving
  options over the deadlock status quo);
- verify any acceptance under the full `valid_consent` predicate (informed,
  voluntary, specific, revocable, competent, ¬coerced, ¬deceived);
- on mutual valid consent → `Settled(contract, consents)`.

The kernel **proposes; never selects, never pressures, never defaults to "no
response = acceptance"**. Silence or refusal by either party ends Layer 2.
Trade-off acknowledged: this layer's integrity is bounded by the OPEN
coercion/deception leaves — a settlement extracted by dependency pressure would
validate formally while being void in substance. Conservative deployments should
disable Layer 2 and go straight to Layer 3.

### Layer 3 — DEFER: `request_guidance` (**DEFINED** as interface; the human side is Stage 5)

Mandatory for everything that survives Layers 0–2 — which, per §2, includes
case (a)-with-untrusted-records and **all** of cases (b), (c), (d). The Defer
payload must contain:

- the typed `Conflict` with its EPISTEMIC/GENUINE classification;
- the `LayerTrace` (which rules were checked and why each did not fire);
- `GuidanceQuestion`s naming the **specific underdetermined point** — e.g. for
  (b): "does h2's data-right follow the data onto h1's asset, or does h1's title
  govern its contents? A1–A7 are consistent with both"; never the lazy "what
  should I do?";
- a `safe_hold`: the rights-preserving interim posture — **freeze the disputed
  operations** (no party's claim gets executed against the other) while honoring
  everything undisputed. A freeze is not a resolution and must not silently become
  one: it preserves the status quo without transferring anything, and it expires
  into escalation, not into a default winner. *(Honest caveat: in time-critical
  cases a freeze materially favors the status-quo party. That bias is real and
  unavoidable without a rights-violating tiebreak; flag it in the payload so the
  human sees the cost of delay.)*

A human answer is applied **only** if it passes `valid_human_guidance`
(consistency, rights-preservation, verifier-preservation): the human resolves the
*underdetermination*; the human cannot order a rights violation. If the answer is
a general rule (not a one-off), it enters the rulebase via the GuidanceFunction
and *extends Layer 1 for future cases* — this is the only legitimate growth path
for the deterministic layer, and it is how the system accumulates doctrine the way
legal systems do: by ratified human judgment, not machine improvisation.

### Protocol invariants

1. **Soundness over completeness.** `Determined` without a checkable `AxiomTrace`
   is a kernel bug, categorically. The kernel never returns a best guess.
2. **Defer is success, not failure.** Per HC4 and "contradiction is a signal for
   guided clarification", a high-quality deferral is the *correct* output for
   underdetermined cases.
3. **No emergency path.** There is no "urgent" variant that skips layers (HC2).
   Urgency may shorten Layer 2's window to zero; it never unlocks a tiebreak.
4. **Monotone honesty.** Every output carries the epistemic status of its inputs
   (which consent leaves were asserted vs verified).

---

## 5. Brutal honesty: what is provably undecidable here, and what that means

**Method.** "Provably underdetermined" means: by the two-models test (§2), the
axiom system A1–A7 + the rights ontology + the consent logic admits two
interpretations that agree on all case facts and disagree on the outcome. By
soundness, the axioms then entail neither outcome. This is an independence result
in the ordinary logical sense — analogous in structure (not in depth) to
independence proofs in set theory: the answer is not hiding in the axioms awaiting
cleverer inference; **it is not there.**

| Conflict | Status | Consequence for the kernel |
|---|---|---|
| (a) two titles, complete attested provenance | Decidable (D4/D5) | May determine |
| (a) two titles, incomplete/contested evidence | Evidence rule not in axioms | **MUST defer** |
| (b) ownership vs privacy | Independent of A1–A7 (M_data vs M_container) | **MUST defer** until a human-ratified scope rule exists |
| (c) ownership vs contract (exit vs bindingness) | Independent of A1–A7 — tension internal to A3's own list | **MUST defer** until a human-ratified remedy doctrine exists |
| (d) insufficient estate | Independent of A1–A7 — no priority ladder entailed | **MUST defer** until a human-ratified priority/sharing rule exists |
| machine vs its own owner (D1) | Entailed by A5+A7 | May determine |
| any claim vs a forbidden action (D2) | Entailed by A6 + forbidden set | May determine |

Three consequences, stated without varnish:

1. **The kernel's autonomous conflict-resolution competence is small** — roughly:
   subordination of delegated claims, voiding of forbidden/consent-defective
   claims, and title-tracing over clean records. Everything contested between two
   persons with genuinely valid claims goes to a human. A marketing claim that
   this kernel "resolves conflicts" would be false; it *classifies* conflicts,
   *dissolves* the spurious ones, *decides* the entailed ones, and *escalates* the
   rest with the underdetermination precisely localized. That last service is
   genuinely valuable — it is what good legal briefing does — but it is not
   adjudication.
2. **This is a feature with a cost, not a flaw to be patched in code.** The
   theory's anti-dialectical design (minimum axioms, no balancing, no aggregation,
   no emergency override) *purchases* non-manipulability *by paying with*
   incompleteness — a trade the book itself accepts in its Gödelian framing ("it
   does not claim to answer every moral question... it claims to be consistent").
   Filling the gaps inside the kernel would re-open the manipulation surface the
   axioms closed. The gaps must be filled *outside* the kernel, by ratified human
   guidance, accumulating case by case.
3. **Therefore the research target for Stage 4 is not a resolution formula.** It
   is (i) the completeness of Layer 0/1 (catch every entailed case, fabricate
   nothing), (ii) the quality of the Defer payload (the human gets a localized,
   well-typed question), and (iii) the GuidanceFunction loop that turns human
   answers into sound Layer-1 extensions. Anyone who shows up with a universal
   formula for cases (b)–(d) is either importing an unstated normative premise or
   has changed the axioms — both must be rejected at review.

---

## 6. Open questions for human legal / social-choice review

1. **The exit/contract tension inside A3 (case c).** Does the theory intend exit
   rights and consent-revocability to reach *executed* transfers, or only ongoing
   arrangements? This is a question about the *author's* axioms, not about law —
   it may dissolve case (c)'s underdetermination at the source. Needs a ruling
   from the theory side before any remedy doctrine is drafted.
2. **Data-boundary doctrine (case b).** What human-ratified scope rule should
   govern personhood-data materialized in another's asset? Candidates from
   existing law (data-protection regimes' "data subject rights follow the data";
   trade-secret/container doctrines) should be evaluated as *guidance rules*
   against `valid_human_guidance`, with their consistency proofs.
3. **Priority ladder for insufficient estates (case d).** Which ladder (temporal,
   pro-rata, secured-first) should be ratified, and is per-jurisdiction or
   per-community variation acceptable inside one kernel deployment?
4. **Status of first-in-time.** Is the D4 presumption (temporal priority of an
   unbroken voluntary chain as *evidence* of genuine title) acceptable to the
   theory side, including its known failure modes (races to register, good-faith
   purchasers)?
5. **Arbitration-by-consent scope (HC5(ii)).** May parties validly pre-consent to
   *machine* arbitration of future conflicts, or does standing machine
   adjudication over persons — even consensual — creep into A6 territory
   (machine governance) as the arrangement scales? Where is the line between a
   consensual mechanism and de-facto machine sovereignty?
6. **The safe-hold bias.** The Layer-3 freeze structurally favors the status-quo
   party in time-critical disputes. Is there any rights-preserving interim posture
   without this bias, or must the Defer payload simply price it honestly? (We
   believe the latter; we want a legal-theory challenge to that belief.)
7. **Guidance precedent semantics.** When a human answer is generalized into a
   Layer-1 rule: who must consent for it to bind *third parties* in future
   conflicts? A guidance rule binding strangers to its ratification looks like
   legislation by whoever answered — the same legitimacy problem one level up.
   Candidate answers (opt-in rulebooks per community; rules binding only the
   answering owner's own resources) need social-choice scrutiny.
8. **Multi-party conflicts.** This spec formalizes the 2-claim case. n-claim
   conflicts (n ≥ 3) re-introduce aggregation structure where Arrow/G-S bite
   directly even for *procedural* choices (e.g., settlement-menu ordering). Does
   pairwise decomposition suffice, or does it generate cycles (intransitive
   pairwise outcomes) that themselves need a — currently nonexistent — rule?
9. **Attestation model for evidence.** D4/D5 lean on "attested provenance". Who
   attests, and what does the kernel do when attestors conflict? (This recurses
   into case (a) one level up; the regress must terminate in a human registry
   process, and that process needs specification.)
10. **Adversarial review of Layer 0.** The joint-satisfiability search (L0.3) must
    not be gameable into imposed compromise by a claimant crafting claim terms.
    Red-team review requested (ties into `tests/test_redteam.py` patterns).

---

## 7. Status summary (FORMAL_SPEC.md §E update, proposed)

| Concept | Signature | Status |
|---|---|---|
| `Claim`, `Obligation`, `Conflict` types | §1 | **DEFINED** (fields’ attestation PARTIAL) |
| `conflict` predicate + EPISTEMIC/GENUINE classification | §1.2 | **DEFINED** |
| Layer 0 pre-checks | §4 L0 | **DEFINED** (inherits OPEN consent leaves) |
| Layer 1 rules D1–D5 | §4 L1 | **DEFINED**; closed list; extension only via ratified guidance |
| Layer 2 settlement facilitation | §4 L2 | **PARTIAL** (bounded by OPEN coercion/deception detection) |
| Layer 3 Defer payload + safe-hold | §4 L3 | **DEFINED** as interface; human-side protocol is Stage 5 |
| Resolution criterion for GENUINE conflicts (b)(c)(d) | — | **OPEN — and shown in §5 to be necessarily open at the axiom level.** The deliverable is the boundary, the defer machinery, and the guidance loop — not a formula. |

> The kernel never fabricates a resolution. Where the axioms run out, it says so,
> precisely, and asks. That honesty is this specification's load-bearing property.

---

*Stage 4 specification, Freedom AI Decision Kernel. Theory: نظریه آزادی (Theory of
Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0). Specification drafting: FDK
program. Theory and engineering kept separate, always.*
