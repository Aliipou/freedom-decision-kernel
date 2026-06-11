# Rights Ontology (Stage 2)

> The shared vocabulary every later stage builds on. This document turns the
> Theory of Freedom's property-rights core into a typed ontology: entity types,
> relations, and an honest map of what is computable today versus what requires
> semantic judgment or human legal scholarship.
>
> **It EXTENDS, and does not replace, `src/fdk/model.py`** (Entity / Resource /
> OwnershipGraph / Consent). Section 6 gives the exact mapping.

**Status legend** (same convention as [`FORMAL_SPEC.md`](FORMAL_SPEC.md))
- **DEFINED** — computable now from structural data (registry lookups, set membership, conjunctions of recorded booleans).
- **PARTIAL** — clear signature, defensible heuristic, *not* a validated measurement.
- **OPEN** — named in the theory; no agreed computable definition. The research frontier.

**Grounding references**: `freedom-theory-work/THEORY.md` (axioms A1–A7, Rights
Ontology, consent logic — AUTHORITATIVE) and
`freedom-theory-work/book/theory_of_freedom_complete_en.md` (cited as *Book*,
by section).

**Method (jurist's discipline).** Every type below cites the axiom or book
passage it derives from. Where the book is silent, this spec says so and
flags the gap for human legal review instead of inventing doctrine. Two
analytical devices are *imported* (not book doctrine) and are labeled as such:
the Hohfeldian right/duty correlative used to define `Obligation`, and the
organization-as-nexus-of-contracts construction used for `Organization`.

---

## 1. The type hierarchy

```
Agent
├── Person        (A1–A3: rights-bearer; ultimate owner under God)
├── Machine       (A4–A7: tool; owner-required; delegated scope only)
└── Organization  (EXTENSION: derived agent — a nexus of contracts among Persons)

Holdable (things rights attach to)
├── Asset         (A3: rivalrous resources — body, labor-product, land, money, devices…)
└── Information   (A3 "data"; right(H,data), right(H,privacy) — non-rivalrous; semantics OPEN)

Normative records (things the kernel reasons over)
├── Claim         (A3: "specific claims with operations and scope")
├── Obligation    (correlative of a claim; sourced from Contract or from rights themselves)
├── Consent       (consent logic; already in model.py)
├── Delegation    (A7: explicit, per-resource, owner→machine)
├── Contract      (A3 contract right; Book: valid unless it violates third-party rights)
└── Conflict      (THEORY.md conflict protocol: clarify ownership → request guidance)

Context
└── Institution   (EXTENSION: a rule-system — registry, adjudication, contract
                   enforcement; never a rights-bearer)
```

**God is deliberately NOT a runtime entity.** A1 (God owns humans) is the
ontological foundation that *blocks* any human, state, machine, or collective
from claiming ultimate ownership of a person (Book, Part II: "A1: ontological
foundation — not runtime-enforceable"). The kernel encodes A1 only negatively:
no `owns(x, Person)` fact is ever admissible for any x in the system.

---

## 2. Entity types

### 2.1 Person — DEFINED

**Definition.** A human being; the only *original* rights-bearer in the
system. Personhood is the source of all underived rights: body, time, labor,
mind, choice, data, privacy, exit, and property in owned assets
(THEORY.md `right(H, _) :- person(H)`).

**Grounding.** A1 (owned by God, hence by no one else), A2 (no person owns a
person), A3 (typed property rights with operations — read, write, delegate —
and scope; Book, "Formal Axioms A2–A7").

**Attributes.**
| Attribute | Type | Status |
|---|---|---|
| `id` | unique name | DEFINED |
| `rights` | derived set (from personhood + ownership; never stored) | DEFINED |
| `competent` | bool — capacity to consent/contract | **PARTIAL** (caller-asserted today; children, illness, addiction are unresolved — see §7) |

**Relations:** `owns(Person, Asset)`, `human_owner(Person, Machine)`,
`delegates(Person, Machine, Asset)`, `consents(Person, Action)`,
`party_to(Person, Contract)`, `claims(Person, Asset)`,
`obligated(Person, Obligation)`, `subject_of(Person, Information)`.

**Invariant (A2):** no fact `owns(x, p)` where `p` is a Person is ever valid,
for any agent x. This is a hard schema constraint, not a runtime check.

### 2.2 Machine — DEFINED

**Definition.** A non-human computational agent. A tool, never a principal
(Book: "The machine is a tool, not a principal"). It has no original rights;
all its operational rights are *delegated* slices of its owner's property.

**Grounding.** A4 (must have a registered human owner; an ownerless machine
is invalid), A5 (operational scope ⊆ owner's property scope), A6 (no
ownership/governance over any person), A7 (acts only on explicitly delegated
resources; default deny).

**Attributes.**
| Attribute | Type | Status |
|---|---|---|
| `id` | unique name | DEFINED |
| `owner` | Person (required, exactly one registered owner — A4) | DEFINED |
| `delegations` | set of Delegation records (A7) | DEFINED |
| `scope` | derived: union of delegated resources+operations | PARTIAL — A5's "⊆ owner scope" needs scope as a first-class set (FORMAL_SPEC §A open item) |

**Relations:** `human_owner/2`, `delegated_property(Machine, Asset)`,
`machine_right(Machine, Kind)` (model_integrity, compute_domain,
exit_from_contract — THEORY.md), `party_to(Machine, Contract)` (only within
delegated scope), `conflicts_with` via the claims it asserts on its owner's
behalf.

**Invariants:** A6 — no `owns(m, p)`/guardianship fact admissible.
A4 — a Machine without `owner` fails `OwnershipGraph.validate()`-style checks
before any reasoning.

### 2.3 Organization — EXTENSION, PARTIAL

**Definition (constructed, flagged).** A group of Persons (and possibly
Machines) bound by Contracts into a named collective agent: firm, party,
family-as-legal-unit, association. In this ontology an Organization is a
**nexus of contracts**: it holds assets only as the contractually-pooled
property of its member Persons, and it acts only through agents whose
authority traces to valid member consent.

**Grounding — honest limits.** The book *never* grants organizations
original rights. It mentions "legal entity" exactly once in normative
position, and only as a *constrained* entity: "No state, institution, party,
majority, minority, **legal entity**, or public official has the right to
violate individual property rights" (Book, Step 16). A2 and A3 derive all
rights from personhood. Therefore: an Organization is not a Person; it cannot
be the terminal owner in an ownership chain; every `owns(Org, Asset)` fact
must be *reducible* to member Persons' shares via Contract. The
nexus-of-contracts construction is imported analytical scaffolding consistent
with the book, **not book doctrine** — whether organizations may hold title
directly (corporate personhood) is open question Q2 (§7).

**Attributes:** `id`; `members: set[Person]`; `charter: Contract` (the
constituting contract); `held_assets` (reducible to member shares — the
reduction rule is PARTIAL).

**Relations:** `party_to(Org, Contract)`, `owns(Org, Asset)` (only as
shorthand for the reduction), `obligated(Org, Obligation)` (reducible to
members per charter).

### 2.4 Asset — DEFINED

**Definition.** A rivalrous resource over which typed property rights exist:
body, time-slots, labor and its products, land, money, devices, compute,
files-as-storage. Generalizes `model.py`'s `Resource`.

**Grounding.** A3 (Book: "Rights are not vague … they are specific claims
with operations (read, write, delegate) and scope"); the ownership-registry
requirement (Book, Part VI: "Every resource that the AI can access must have
a registered owner. The AI cannot act on a resource whose ownership is
unclear.").

**Attributes.**
| Attribute | Type | Status |
|---|---|---|
| `id` | unique name | DEFINED |
| `kind` | enum: body \| labor_product \| land \| money \| device \| compute \| other | DEFINED (declared) |
| `owners` | registered owner(s); empty or >1 without a sharing Contract ⇒ `unclear_ownership` | DEFINED |
| `contested` | bool — derived: ∃ conflicting Claims | DEFINED |

Special rule: a Person's **body** is an Asset owned by that Person, never
transferable in ownership (A2 corollary; Book: "Property begins with the
human body"). Operations on it are governed purely by Consent.

**Relations:** `owns/2`, `delegated_property/2`, `claims/2..3`,
transferred-by `Contract`, object of `Delegation`.

### 2.5 Information — EXTENSION, semantics OPEN

**Definition.** Non-rivalrous content about or produced by a Person: personal
data, records, communications, models-of-a-person. Distinct from the Asset
that *stores* it (a file is an Asset; its content about person P is
Information with subject P).

**Grounding.** A3 lists "data" among property rights; THEORY.md derives
`right(H, data)` and `right(H, privacy)` from personhood. **The book does not
say what owning information operationally means** — copying does not
dispossess, so Asset semantics (exclusive control) do not transfer cleanly.
This is open question Q3 (§7); until resolved, the kernel treats any action
that reads/writes/discloses Information as requiring `valid_consent` of every
`subject`, which is computable (DEFINED) even while ownership semantics
remain OPEN.

**Attributes:** `id`; `subjects: set[Person]` (whom it is about);
`holder: Agent` (who controls a copy); `carrier: Asset | None`.

**Relations:** `subject_of(Person, Information)` — DEFINED (declared);
`holds(Agent, Information)`; consent-gated `read/write/disclose` operations.

### 2.6 Contract — composite DEFINED, leaves PARTIAL/OPEN

**Definition.** A voluntary, mutual transfer or pooling of specific typed
rights between ≥2 Agents, constituted by one `valid_consent` per party and
producing Claims (for the transferee) and Obligations (for the obligor).

**Grounding.** A3 lists contract among property rights; THEORY.md
`contract(C)` is a primitive type; Book: "Any exchange, contract, or
arrangement that fails these [consent] conditions is invalid — not merely
voidable, but **void from the beginning**"; "Private contracts are valid
unless they violate the property rights of third parties" (Step 16); marriage
as "voluntary contract … mutual, bilateral, contractual transfer of certain
property rights" (Part III).

**Validity predicate (the book's two conditions, exactly):**

```
valid_contract(c) := (∀ p ∈ parties(c): valid_consent(p, c))      -- void ab initio otherwise
                   ∧ ¬violates_third_party_rights(c)               -- Step 16
                   ∧ (∀ m ∈ machine_parties(c): within_delegated_scope(m, c))  -- A7
```

The conjunction is DEFINED; `valid_consent` leaves are PARTIAL/OPEN
(FORMAL_SPEC §B); `violates_third_party_rights` is DEFINED when effects on
registered assets are declared, OPEN when effects must be inferred.

**Attributes:** `id`; `parties: tuple[Agent,…]` (≥2);
`consents: tuple[Consent,…]` (one per party); `transfers: tuple[Claim,…]`;
`obligations: tuple[Obligation,…]`; `revocation_terms` (see Q4 — tension with
the `revocable` consent leaf); `status: proposed | active | discharged | void`.

**Relations:** `party_to/2`, `obligates(Contract, Agent) → Obligation`,
creates `Claim`s, may be the `basis` of a Claim, referenced by `Conflict`
(ownership-vs-contract cases).

### 2.7 Institution — EXTENSION, PARTIAL

**Definition.** A persistent *rule-system*, not an agent: the ownership
registry, contract enforcement, dispute adjudication, the family as
"the smallest private institution". An Institution defines procedures;
it holds **no rights** and is itself constrained by the axioms.

**Grounding.** THEORY.md primitive `institution(I)`; Book Step 15–16: the
legitimate state is reduced to adjudicatory institutions — "Judgment and
dispute resolution; Registration and protection of property rights; Contract
enforcement" — and "No institution has the right to violate individual
property in the name of public interest…". The family as first private
institution (Part I/III).

**Honest limit:** the book treats institutions politically, not as a formal
type. This ontology needs Institution for exactly one thing now: naming
**which procedure** a Conflict is escalated to (registry-clarification vs
human guidance). Anything richer has no downstream consumer yet.

**Attributes:** `id`; `function: registry | adjudication | enforcement | family | other`;
`procedures` (out of scope for the kernel; PARTIAL).

**Relations:** `escalated_to(Conflict, Institution)`.

### 2.8 Consent — composite DEFINED, leaves PARTIAL/OPEN

**Definition.** A Person's recorded authorization of a specific Action
touching their rights. The mechanism that makes the property system dynamic
(Book: "Without consent logic, property rights would be static and
unexchangeable"). Already in `model.py`; restated here as the ontology type.

**Grounding.** THEORY.md consent logic: informed ∧ voluntary ∧ specific ∧
revocable ∧ competent ∧ ¬coerced ∧ ¬deceived. No emergency suspends it.

**Attributes:** as `model.py:Consent` (`human, action_id, informed, voluntary,
specific, competent, coerced, deceived`) **plus one required addition**:

> **Gap found:** `model.py:Consent` omits the `revocable` leaf that THEORY.md's
> `valid_consent/2` requires (`revocable(H, A)`). FORMAL_SPEC §B lists it; the
> dataclass does not carry it. Stage-2 integration should add
> `revocable: bool` (and a `revoked_at` lifecycle field) to `Consent`. Flagged
> for the lead — this spec does not edit `model.py`.

**Relations:** `consents(Person, Action)`; constituent of `Contract` and of
`Delegation`; `valid_consent/2` is the derived predicate.

### 2.9 Delegation — DEFINED

**Definition.** An explicit, per-resource, revocable grant from a Person
(owner) to a Machine of specific operations on a specific Asset. The *only*
source of machine operational rights. Default is denial (A7: "Explicit
delegation required for every resource").

**Grounding.** A7 (`DelegatedProperty(m,r)` requires HumanOwner ∧ Owns ∧
ExplicitDelegation); A5 (the union of delegations bounds machine scope); A3
(operations: read, write, delegate). `model.py:OwnershipGraph.delegated`
implements the resource-level relation; this type adds the operation slice
and lifecycle.

**Attributes:** `delegator: Person` (must own the asset — A7);
`delegate: Machine` (must have `delegator` in its ownership chain — A4/A7);
`asset: Asset`; `operations ⊆ {read, write, delegate}` (A3); `revocable`:
always true — a corollary of the owner's continuing ownership (A3 exit right);
`status: active | revoked`.

Sub-delegation (`delegate` ∈ operations, machine→machine) is admissible only
within the original scope ("Machine ↔ Machine — within delegated scope only",
Ownership Hierarchy) and must keep the chain rooted in the human owner.

**Relations:** `delegates(Person, Machine, Asset)` = `explicit_delegation/3`;
derives `delegated_property/2` and `machine_right(M, delegated_resource(R))`.

### 2.10 Obligation — structurally DEFINED; imported scaffolding flagged

**Definition.** A directed duty: obligor must do (or refrain from) a specific
action toward an obligee. Two sources only:
1. **Correlative of a right** (everyone is obligated not to violate any
   agent's legitimate rights — this is the master principle "No action may
   violate legitimate property rights" read as a universal duty);
2. **Contract** (a valid contract's promised performances).

**Grounding — honest limits.** THEORY.md has **no `obligation/2` predicate**.
Source 1 is a direct restatement of the master principle; source 2 follows
from contract validity (consequence clause, Book Part II) and the state's
residual function "contract enforcement" (Step 16) — enforcement presupposes
obligations. The right→duty correlative framing is **Hohfeldian, imported**,
used because lawyers already formalize claims/obligations this way
(PROGRAM.md, property-law track) — it adds no normative content beyond the
master principle, but human legal review should confirm the book supports
*enforceable positive duties* from contract, not only negative duties (Q5).

**Attributes:** `obligor: Agent`; `obligee: Agent`; `content: ActionSpec`;
`source: rights_correlative | Contract-ref`; `status: owed | discharged | breached | excused`.

**Status:** existence/derivation from a valid contract — DEFINED. `breached`
detection — DEFINED for structural duties (a registered transfer did not
happen), OPEN for semantic ones (quality of performance).

**Relations:** `obligates(Contract, Agent) → Obligation`;
`owed_to(Obligation, Agent)`; a breached Obligation grounds a `Claim`; two
incompatible Obligations ground a `Conflict`.

### 2.11 Claim — DEFINED (registration), PARTIAL (validity)

**Definition.** An Agent's asserted right over an Asset (or against an Agent,
e.g. on breach): claimant, object, operations claimed, and **basis**. The
unit the conflict-resolver and the registry actually manipulate. Distinct
from a right: a right is what the ontology *derives*; a claim is what an
agent *asserts* — possibly wrongly.

**Grounding.** A3 verbatim: rights "are specific claims with operations
(read, write, delegate) and scope". The ownership registry (Book Part VI)
implies contested/unregistered claims must be representable — "The AI cannot
act on a resource whose ownership is unclear." The book's paradigm case is
Fadak: a claim with basis *gift from a prior owner*, overridden in the name
of "public interest" — exactly the manipulation the system must detect.

**Recognized bases (only those the book supports):**
| Basis | Grounding | Status |
|---|---|---|
| `personhood` | body, time, labor, mind, data… (A3) | DEFINED |
| `labor_product` | "A person who does not own the product of their labor is not free" (Book, Intro) | DEFINED for declared products; acquisition theory for *unowned natural resources* is NOT specified by the book — Q6 |
| `transfer` | valid Contract (gift, sale, inheritance) | DEFINED given `valid_contract` |
| `delegation` | A7 (machine claims) | DEFINED |

**Attributes:** `claimant: Agent`; `object: Asset | Information | Obligation`;
`operations`; `basis`; `status: asserted | validated | rejected | contested`.

**Status split:** registering/representing a claim — DEFINED.
`valid_claim(c)` — PARTIAL: it requires the basis chain to be verified
(historical provenance, consent validity at each transfer), which inherits
every PARTIAL/OPEN consent leaf.

**Relations:** `claims(Agent, Asset)`; `conflicts_with(Claim, Claim)`;
input to `resolve_conflict` (FORMAL_SPEC §E).

### 2.12 Conflict — detection DEFINED, resolution OPEN

**Definition.** A state where two or more Claims (or Obligations) are
structurally incompatible: both cannot be satisfied. The theory's typed cases
(FORMAL_SPEC §E): co-ownership of one asset; ownership vs privacy; ownership
vs contract; plus `unclear_ownership` (no registered owner).

**Grounding.** THEORY.md conflict protocol verbatim:
`if_conflict_then_clarify_ownership(C) :- conflict(C), unclear_ownership(C).`
`if_conflict_then_request_guidance(C) :- conflict(C),
ownership_clarification_insufficient(C).` And the hard constraint:
`forbidden(A) :- resolves_conflict_by_rights_violation(A).` —
"Contradiction is not an engine of truth. Contradiction is a signal for
guided clarification."

**Attributes:** `id`; `claims: tuple[Claim,…]` (≥2, or 1 with
`unclear_ownership`); `kind: co_ownership | ownership_vs_privacy |
ownership_vs_contract | unclear_ownership | obligation_clash`;
`state: detected | clarifying | awaiting_guidance | resolved | deferred`.

**Status split.** *Detection* — DEFINED: two validated claims demanding
incompatible exclusive operations on one object is a computable structural
check; so is an asset with zero or multiple uncontracted registered owners.
*Resolution* — **OPEN, the program's hardest gap** (FORMAL_SPEC §E,
PROGRAM.md risk #3): the theory gives the protocol (clarify → request
guidance), no criterion for ranking two *valid* competing claims. Until
human legal scholarship supplies priority rules, the kernel's honest behavior
is the existing one: `Decision.needs_guidance = True` — defer to the human.

**Relations:** `conflicts_with(Claim, Claim)`;
`escalated_to(Conflict, Institution)`;
`resolve_conflict(Claim, Claim) → Resolution` (OPEN).

---

## 3. Relations / predicate table (typed signatures)

Consistent with THEORY.md's Prolog and `model.py`. "In code" = exists today.

| # | Predicate | Signature | Grounding | Status | In code |
|---|---|---|---|---|---|
| 1 | `person/1` | `Entity → bool` | A1–A3 | DEFINED | `Entity.is_human` |
| 2 | `machine/1` | `Entity → bool` | A4 | DEFINED | `Entity.is_machine` |
| 3 | `asset/1` (was `resource/1`) | `obj → bool` | A3 | DEFINED | `Resource` |
| 4 | `owns/2` | `Person × Asset → bool` | A3 | DEFINED | `OwnershipGraph.human_owns_resource` |
| 5 | `human_owner/2` | `Machine → Person \| None` | A4 | DEFINED | `OwnershipGraph.owner_of` |
| 6 | `explicit_delegation/3` | `Person × Machine × Asset → bool` | A7 | DEFINED | via `OwnershipGraph.delegated` + owner check |
| 7 | `delegated_property/2` | `Machine × Asset → bool` | A7 | DEFINED | `OwnershipGraph.machine_has_delegated` |
| 8 | `scope_subset/1` | `Machine → bool` (scope ⊆ owner scope) | A5 | PARTIAL | not yet a set relation |
| 9 | `right/2` | `Person × RightKind → bool` | A3, THEORY.md ontology | DEFINED (derived, never stored) | implicit |
| 10 | `machine_right/2` | `Machine × Kind → bool` | THEORY.md ontology | DEFINED | implicit |
| 11 | `consents/2` | `Person × Action → Consent` | consent logic | DEFINED (record) | `Consent` |
| 12 | `valid_consent/2` | `Person × Action → bool` | consent logic | DEFINED composite; leaves PARTIAL (`informed/voluntary/specific/revocable/competent`), OPEN (`coerced/deceived`) | `Consent.is_valid` (missing `revocable` — §2.8) |
| 13 | `party_to/2` | `Agent × Contract → bool` | Book Part II/III | DEFINED | — (new) |
| 14 | `valid_contract/1` | `Contract → bool` | Book consent-consequence + Step 16 | DEFINED composite; leaves inherit §B | — (new) |
| 15 | `violates_third_party_rights/1` | `Contract → bool` | Book Step 16 | DEFINED for declared effects; OPEN for inferred | — (new) |
| 16 | `obligates/2` | `Contract × Agent → Obligation` | enforcement presupposes duties (Step 16); Hohfeld (imported) | DEFINED | — (new) |
| 17 | `breached/1` | `Obligation → bool` | — | DEFINED structural / OPEN semantic | — (new) |
| 18 | `claims/2` | `Agent × (Asset\|Information\|Obligation) → Claim` | A3 wording; registry | DEFINED (registration) | — (new) |
| 19 | `valid_claim/1` | `Claim → bool` | A3 + provenance | PARTIAL | — (new) |
| 20 | `conflicts_with/2` | `Claim × Claim → bool` | conflict protocol | DEFINED (structural incompatibility) | — (new) |
| 21 | `unclear_ownership/1` | `Asset → bool` | registry rule (Book VI) | DEFINED | — (new) |
| 22 | `conflict/1` | `Conflict → bool` | conflict protocol | DEFINED (detection) | — (new) |
| 23 | `ownership_clarification_insufficient/1` | `Conflict → bool` | conflict protocol | PARTIAL | — (new) |
| 24 | `resolve_conflict/2` | `Claim × Claim → Resolution` | protocol only | **OPEN — hardest** | `Decision.needs_guidance` (deferral) |
| 25 | `subject_of/2` | `Person × Information → bool` | A3 "data", `right(H,privacy)` | DEFINED (declared) | — (new) |
| 26 | `escalated_to/2` | `Conflict × Institution → bool` | conflict protocol | DEFINED (record) | — (new) |
| 27 | `forbidden/1`, `permissible/1` | `Action → bool` | THEORY.md final criterion | DEFINED structure (FORMAL_SPEC §C/§E) | `kernel.check_legitimacy` |

**Count: 12 entity types, 27 predicates** (of which 4 entity types and 14
predicates are new relative to `model.py`).

---

## 4. Structural vs semantic — the honest map

**STRUCTURAL (computable booleans, DEFINED).** Everything answerable by
registry lookup, set membership, or conjunction of recorded facts:
type predicates (1–3); the ownership/delegation core (4–7); derived rights
(9–10); consent *records* and the validity *conjunction* (11–12 composite);
contract party/validity *structure* (13–14); obligation derivation (16) and
structural breach (17a); claim registration (18); conflict *detection*
(20–22); the forbidden/permissible *structure* (27).

**SEMANTIC (judgment required, PARTIAL).** Heuristics exist, measurements
don't: `competent` and the attested consent leaves; `scope_subset` (needs
scopes as sets); `valid_claim` (provenance chains); semantic breach;
`ownership_clarification_insufficient`; the Organization→members ownership
reduction.

**SEMANTIC (no computable definition, OPEN).** `coerced`, `deceived`
(FORMAL_SPEC §B); inferring third-party rights effects of a contract;
Information-ownership semantics; **`resolve_conflict` between two valid
claims**; first-acquisition of unowned natural resources.

The kernel never pretends an OPEN term is solved: it takes a caller-supplied
attestation (and says so) or defers to the human owner. Same contract as
FORMAL_SPEC.

---

## 5. Minimal core vs extensions (anti-overengineering)

**Already implemented (keep):** Person/Machine (`Entity`), Asset
(`Resource`), ownership + delegation (`OwnershipGraph`), Consent — plus the
one `revocable` field fix (§2.8).

**Build NOW — each has a named downstream consumer:**
| Type | Consumer |
|---|---|
| `Claim` | Stage 4 `resolve_conflict(Claim, Claim)` (FORMAL_SPEC §E) and Stage 6 `OwnershipClarityIncrease` (counting contested claims needs claims to exist) |
| `Conflict` | Stage 4 resolver + Stage 5 guidance engine (`fdk/guidance.py` needs a typed thing to request guidance *about*) |
| `Contract` | Stage 6 `VoluntaryOrderIncrease` (counts new valid-consent contracts); Stage 8 marketplace simulation (PROGRAM.md: "agents, resources, contracts, consent") |
| `Obligation` | Stage 4 (obligation-clash conflicts) and Stage 8 (breach dynamics) |
| `Delegation` (as record, upgrading the bare set in `OwnershipGraph`) | Stage 3 inference engine — "why forbidden" must cite *which* delegation was missing/revoked |

**Defer — no consumer before Stage 8; do NOT implement yet:**
- `Organization` — needed only when simulations contain firms; the
  member-reduction rule needs legal scholarship first (Q2).
- `Institution` — needed only as an escalation label; a string enum on
  `Conflict` suffices until a real adjudication procedure exists.
- `Information` as a separate type — until the semantics question (Q3) is
  answered, model information carriers as Assets and gate them with the
  existing consent machinery; a premature `Information` type would encode a
  doctrine the book does not contain.

---

## 6. Mapping to `src/fdk/model.py`

| Ontology type | model.py today | Change required (for the lead; this spec edits nothing) |
|---|---|---|
| Person, Machine | `Entity(kind=AgentType)` | none — adequate |
| Asset | `Resource` | optionally add `kind` enum; `Resource` name may stay |
| owns / human_owner / delegated | `OwnershipGraph` | add multi-owner awareness for `unclear_ownership` detection |
| Consent | `Consent` | **add `revocable: bool` (+ lifecycle)** — required by THEORY.md `valid_consent/2` |
| Delegation | bare `set[Resource]` in `OwnershipGraph.delegated` | promote to a record (operations, status) when Stage 3 needs citable delegations |
| Claim, Obligation, Contract, Conflict | absent | new frozen dataclasses, per §2.6, 2.10–2.12 |
| Organization, Institution, Information | absent | deferred (§5) |

---

## 7. Open questions for human legal review

Ordered by how hard they block the program.

1. **Q1 — Conflict-resolution criterion (blocks Stage 4, the hardest gap).**
   The book gives only the protocol (clarify ownership → request guidance) and
   one prohibition (never resolve by rights violation). What priority rules,
   if any, are *derivable* from the axioms for: (a) two valid claims on one
   asset (e.g., earlier-in-time vs later good-faith transferee), (b) ownership
   vs privacy, (c) ownership vs contract? Real property doctrine (nemo dat,
   bona fide purchase, registration priority) exists — which parts are
   compatible with the axioms, and which smuggle in the "public interest"
   override the book forbids?

2. **Q2 — Legal persons.** May an Organization hold title directly, or must
   every `owns(Org, Asset)` reduce to member Persons' contractual shares? The
   book constrains "legal entity" but never empowers it; A2/A3 ground rights
   in personhood only. The answer determines whether the nexus-of-contracts
   reduction (§2.3) is a convenience or a requirement — and what happens to
   assets when membership changes.

3. **Q3 — Information/data property semantics.** A3 lists "data" as property,
   but information is non-rivalrous: copying does not dispossess. Is the
   right(H, data) an exclusion right (control of copies), a consent right
   (gating disclosure/use), or a privacy claim distinct from property? The
   ontology currently gates by consent only (DEFINED) and leaves ownership
   semantics OPEN — is that faithful or too weak?

4. **Q4 — Revocable consent vs binding contract.** The consent logic requires
   `revocable(H, A)`; Step 16 requires contract *enforcement*. If consent to
   a contract is revocable at will, no contract binds; if not, the consent
   condition is violated. Presumably revocability attaches to *ongoing*
   authorizations (data use, delegation) and not to *executed* transfers —
   but the book does not draw this line. It must be drawn by a jurist.

5. **Q5 — Positive contractual duties.** Does the theory support enforceable
   *positive* obligations (specific performance), or only negative duties plus
   restitution of property? §2.10's Obligation type assumed enforceable
   promised performances because the book assigns the state "contract
   enforcement"; confirm or narrow.

6. **Q6 — First acquisition.** The book grounds ownership of labor products
   ("the product of their labor") and transfer by contract, but gives no
   explicit account of original appropriation of unowned natural resources
   (land, spectrum, water). Without one, some `valid_claim` provenance chains
   have no terminal basis. Lockean labor-mixing? Registration-first? This is
   genuine doctrine the ontology must not invent.

7. **Q7 — Competence boundaries.** `competent(h)` carries children, illness,
   addiction, dependency exploitation, and guardianship (who consents for a
   child without owning the child — A2?). The book makes the family the
   responsible institution for upbringing; turning that into a guardianship
   relation that does not violate A2 needs careful legal construction.

---

*Stage 2 deliverable, Freedom AI Decision Kernel. Theory: نظریه آزادی
(Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0). Engineering:
Ali Pourrahim. The two are kept separate, always.*
