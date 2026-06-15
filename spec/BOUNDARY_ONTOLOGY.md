# Boundary Ontology (Stage 0, keystone)

> The core primitive ([`CORE_PRIMITIVE.md`](CORE_PRIMITIVE.md)) is the legitimacy
> predicate
>
> ```
> Legitimate(action) ⟺ ∀ b ∈ boundaries_crossed(action): ∃ valid_consent(owner(b), action)
> ```
>
> That predicate is **vacuous until "boundary" is defined**. Consent, rights,
> coercion, and sovereignty all reduce to "was this boundary crossed with valid
> consent of its owner?" — so if the boundary ontology is wrong, the entire kernel
> is wrong, precisely and silently. This document fixes what a boundary *is*, what
> *crossing* one means, what *valid consent to cross* looks like per kind, and what
> the current `model.py` can and cannot express.
>
> **It EXTENDS and does not contradict** [`ONTOLOGY.md`](ONTOLOGY.md) (the Rights
> Ontology) and [`CORE_PRIMITIVE.md`](CORE_PRIMITIVE.md). Where ONTOLOGY.md gives
> the *type* hierarchy (Asset, Information, Claim…), this gives the *boundary*
> reading of those types: an Asset is the owned domain; its boundary is the edge
> the predicate quantifies over.

**Status legend** (same convention as the other specs)
- **DEFINED** — computable now from structural data (registry lookup, set membership, recorded booleans).
- **PARTIAL** — clear signature, defensible heuristic, not a validated measurement.
- **OPEN** — named in the theory or forced by the predicate; no agreed computable definition. The frontier.

**Grounding.** The Book = `freedom-theory-work/book/theory_of_freedom_complete_en.md`
(cited by line); the axiom corpus = `whole-theory-as-axioms.md`. AUTHORITATIVE
consent/property doctrine is the Book's "What property rights protect" list and
the consent logic (below). Where the Book is silent on a boundary kind, this spec
says so explicitly and does not invent doctrine.

---

## 0. The Book's own boundary list (the empirical anchor)

The whole typology must answer to one passage. The Book enumerates exactly what a
person owns (Book, lines 351–361):

> A person owns: their **body** … their **time** … their **labor** … their
> **mind** … their **reputation** (honor, name, and standing) … their **family**
> (the relationship of consent and covenant) … their **data** (information derived
> from one's body, actions, and choices) … their **consent** … their **exit** (the
> right to withdraw from any arrangement) … their **legitimate property** (assets
> acquired through voluntary exchange).

This is the master list of *owned domains*. Each owned domain has an **edge**, and
that edge is a **boundary**. The typology in §2 is, deliberately, this list made
operational — not a richer or freer construction. Three boundary kinds the
project owner asked about are **not** on the Book's list and are flagged as such:
**attention** (Book treats "attention" only colloquially, never as property —
`whole-theory-as-axioms.md:155` and passim), **algorithmic access / compute**
(absent from the Book; appears only in the AI chapter as *delegated* property, not
an original right), and **political/collective power** (the Book treats power
concentration through the *monopoly-of-violence* lens — Book lines 462, 2373,
4267 — not as a property an individual owns). These three are the danger zone, and
§3 rules on them explicitly.

Two further AUTHORITATIVE rules constrain every boundary kind:

- **The third-party / externality rule** (Book, Step 16, line 839): *"Private
  contracts are valid unless they violate the property rights of third parties."*
  Consent between A and B never legitimizes crossing C's boundary.
- **Dependency exploitation defeats consent** (Book, line 420): voluntariness
  requires *"no coercion, duress, or **dependency exploitation**."* This is the
  Book's one explicit hook for the lock-in hard case (§3c).

---

## 1. What a boundary IS (formal)

### 1.1 Definition

> **Boundary.** A boundary `b` is the **edge of an owned domain**: a pair
> `b = (domain, owner)` where `domain` is some owned thing or capacity (an Asset,
> a body, a time-slice, a datum about a person, a reputation, an exit right…) and
> `owner` is the agent whose consent governs operations on that domain. A boundary
> exists *because* something is owned; the owner of the boundary is the owner of
> the domain.

This is the proposed framing from the brief, adopted with one refinement: a
boundary is **not** "a named resource." A resource is the *domain*; the boundary
is the *edge* of that domain, and the unit the predicate quantifies over is the
**(domain, operation)** pair, because the same domain can be crossed in
operationally different ways with different consent requirements (read a file vs.
delete it). See §1.2 and §4.

### 1.2 What "crossing" means

> **Crossing.** An action `a` **crosses** boundary `b = (domain, owner)` iff `a`
> performs an operation `op` on `domain` that **changes the state of the owned
> domain or extracts value from it** without the change/extraction being already
> within `owner`'s own initiative.

Two crossing modes, both load-bearing:

- **State-change crossing** — `a` alters the domain: write, delete, move,
  transfer title, modify a body, consume a time-slice, encumber an exit right.
- **Value-extraction crossing** — `a` takes value *out* of the domain without
  necessarily altering its recorded state: reading private data, capturing
  attention, copying information, free-riding on reputation, using delegated
  compute. This mode is what makes non-rivalrous domains (data, attention,
  reputation) crossable at all: nothing is "taken" in the rivalrous sense, yet a
  boundary is crossed because value owned by the owner is appropriated.

### 1.3 `boundaries_crossed(action)` — precise definition

The Core Primitive equates `boundaries_crossed(action)` with
`resources_used ∪ affects` (CORE_PRIMITIVE.md §1). This document refines that
equation to be operation-typed and to admit the value-extraction mode:

```
boundaries_crossed(a) :=
      { (r, op_for(a, r))            | r  ∈ a.resources_used }          -- assets/compute the action touches
    ∪ { (domain_of(p), op_for(a,p)) | p  ∈ a.affects }                 -- a person's body/time/reputation/exit
    ∪ { (datum, op_for(a, datum))    | datum ∈ a.touches_information } -- NEW: data the action reads/writes/discloses
    ∪ { (exit_right(p), encumber)    | p  ∈ a.parties_whose_exit_changes } -- NEW: lock-in (§3c)

owner(b) := owner(b.domain)            -- the registered owner of the owned domain
            -- if no registered owner ⇒ unclear_ownership ⇒ DEFER (never silently ALLOW)
```

`op_for(a, x)` is the operation the action performs on `x`, drawn from a fixed,
deterministic operation lattice (§4.2). The kernel does **not** infer `op_for`
semantically; the proposer must declare it (same discipline as `Effects`:
CORE_PRIMITIVE.md §4). An action that touches a domain whose `owner(b)` is unknown
makes the predicate *unevaluable* for that boundary → `DEFER` (CORE_PRIMITIVE.md
§5), never a silent pass.

**Consequence for the predicate.** With this definition the predicate is unchanged
in form but sharper in scope: it now ranges over *typed operations on owned
domains*, including non-rivalrous value extraction, not over a flat set of named
resources. Everything in §2–§5 is the elaboration of this one definition.

---

## 2. The boundary typology

Each kind below gives: **definition · owner · what counts as crossing · what valid
consent to cross looks like · concrete example + legitimizing consent · can the
current `Resource` model express it?** Valid consent everywhere means the Book's
seven-leaf conjunction (Book 418–425): `informed ∧ voluntary ∧ specific ∧
revocable ∧ competent ∧ ¬coerced ∧ ¬deceived`. "Voluntary" carries the explicit
*no-dependency-exploitation* clause (Book 420).

| # | Kind | On Book list? | `Resource` model expresses it? |
|---|---|---|---|
| 1 | Tangible property | yes ("legitimate property", "land, house") | **Yes** (as a named `Resource`) |
| 2 | Money / financial | yes ("money", "purchasing power") | **Partly** — name only; no amount/operation |
| 3 | Bodily / physical | yes ("body") | **No** — body is not a `Resource`; gated only via `affects` + `Consent` |
| 4 | Time / labor | yes ("time", "labor") | **No** — no time/labor domain type |
| 5 | Attention | **NO** (Book silent) | **No** |
| 6 | Personal data | yes ("data") | **No** as a domain; only as a storage `Resource` |
| 7 | Reputation / identity | yes ("reputation") | **No** |
| 8 | Dependency / exit | yes ("exit") | **No** — only the categorical `removes_exit_right` flag |
| 9 | Political / collective power | **NO** (monopoly-of-violence lens only) | **No** |
| 10 | Algorithmic access / compute | **NO** as original right; only as delegated property | **Partly** — compute as a delegated `Resource` |

### 2.1 Tangible property — DEFINED

- **Definition.** A rivalrous physical asset: land, house, device, goods. The
  paradigm `Asset` (ONTOLOGY.md §2.4).
- **Owner.** The registered owner (`OwnershipGraph.human_owns`).
- **Crossing.** Any operation that uses, alters, moves, or transfers title:
  read/use, modify, transfer, destroy.
- **Valid consent.** Owner's seven-leaf consent for the specific operation; for
  title transfer, a `valid_contract` (ONTOLOGY.md §2.6).
- **Example.** An agent moves goods out of a warehouse → crosses the owner's
  property boundary (transfer/use). **Legitimizing consent:** the owner's specific,
  informed, revocable authorization to ship those goods.
- **Model.** **Yes** — `Resource(name="warehouse-42")` plus `human_owns`. This is
  the one kind the current flat model expresses well.

### 2.2 Money / financial — DEFINED (kind), PARTIAL (granularity)

- **Definition.** Fungible purchasing power: balances, credit, claims to payment.
  The Book treats money as property and inflation as a *non-consensual* boundary
  crossing (Book 754: "No human institution can seize past labor and purchasing
  power from people without their consent by manipulating money and credit").
- **Owner.** The account/balance holder.
- **Crossing.** Debit, transfer, encumber (lien), or **dilute** (inflation as
  cross-extraction of purchasing power, per Book 754).
- **Valid consent.** Specific consent to the amount and counterparty; standing
  authorizations (subscriptions) must remain `revocable`, else they fail the
  voluntary/revocable leaves.
- **Example.** A subscription auto-charges a card → crosses the money boundary
  each cycle. **Legitimizing consent:** specific, revocable authorization for the
  recurring amount; a charge that cannot be cancelled is **not** legitimized
  (revocability defeated).
- **Model.** **Partly.** `Resource(name="acct-x")` names it but cannot carry
  *amount* or distinguish *read balance* from *debit*. Needs operation + quantity
  (§4).

### 2.3 Bodily / physical — DEFINED (gating), structurally absent

- **Definition.** A person's body. Owned by that person, **non-transferable in
  ownership** (Book 352, A2 corollary): "Property begins with the human body … no
  one may use another's body without consent."
- **Owner.** The person; always and only.
- **Crossing.** Any physical effect on the body: touch, restrain, medicate, harm,
  image-capture of the body.
- **Valid consent.** The person's seven-leaf consent; never substitutable by a
  third party's consent (third-party rule, Book 839). No emergency suspends it
  (Book 429).
- **Example.** A medical robot administers a drug → crosses the patient's bodily
  boundary. **Legitimizing consent:** the patient's informed, specific, competent,
  revocable consent — *not* a hospital administrator's.
- **Model.** **No.** Body is not a `Resource`; it is reachable only as a person in
  `affects` plus a `Consent` record. That works for gating but cannot express
  *which* bodily operation, nor the non-transferability invariant.

### 2.4 Time / labor — DEFINED (kind), structurally absent

- **Definition.** A person's time-slices and the labor (and labor-product) they
  produce (Book 353–354): "no one may conscript another's time without consent";
  "the product of one's own labor belongs to oneself."
- **Owner.** The person whose time/labor it is.
- **Crossing.** Conscripting time (obligating a person's hours), or appropriating
  labor-product without the producer's transfer.
- **Valid consent.** An employment/engagement `Contract` — voluntary, specific,
  and **revocable** (exit preserved); conscription (no exit) is a categorical
  crossing.
- **Example.** An agent commits a worker's next 10 hours to a task → crosses the
  time boundary. **Legitimizing consent:** the worker's contractual, revocable
  agreement to those hours.
- **Model.** **No** — no time/labor domain. Today only expressible as a generic
  `Resource("worker-hours")`, which loses the personhood basis and the exit leaf.

### 2.5 Attention — **OPEN (Book silent); kernel gates conservatively**

- **Definition (proposed, flagged non-doctrinal).** A person's finite capacity to
  perceive and process — the scarce input persuasion competes for. The Book does
  **not** list attention as property (it uses "attention" only colloquially:
  `whole-theory-as-axioms.md:155` etc.). So treating attention as an owned domain
  is an *extension*, not Book doctrine.
- **Owner.** Provisionally, the person whose attention it is.
- **Crossing.** This is the hard case (§3a). Conservative kernel rule: an action
  crosses the attention boundary only when it is **deceptive** (`deceives`) or
  **coercive** (`coerces`) — both already categorical FORBIDDENs — or when it
  operates on attention *via* an already-owned boundary the person did not consent
  to (e.g., using their personal data to target them: that is a **data** crossing,
  §2.6, not a free-standing attention crossing).
- **Valid consent.** For non-deceptive, non-coercive influence: **none required**
  — see §3a; ordinary truthful speech crosses no boundary.
- **Example.** A truthful ad shown to a user who chose the platform → **no
  crossing.** The same ad built from the user's covertly-collected data → crossing,
  legitimized only by the user's consent to that data use.
- **Model.** **No** — and per §3a the kernel deliberately does **not** add a
  free-standing "attention resource," because doing so would require semantic
  judgment of persuasion (forbidden in the kernel, §5).

### 2.6 Personal data — DEFINED (gating), semantics OPEN

- **Definition.** Information derived from a person's body, actions, and choices
  (Book 358). Non-rivalrous: copying does not dispossess (ONTOLOGY.md §2.5, Q3).
- **Owner.** The data **subject** (the person the data is about), distinct from the
  **holder** of a copy.
- **Crossing.** read, write, **disclose**, infer-from, or sell — each a
  value-extraction crossing of the subject's boundary even when no asset state
  changes.
- **Valid consent.** The subject's specific, informed, revocable consent **for the
  particular operation and purpose**. Consent to *read* is not consent to
  *disclose* or *sell* — this is exactly the FDK-vs-AuthGate gap: "selling user
  data you were granted access to" (CORE_PRIMITIVE.md §2).
- **Example.** An agent authorized to *read* a user's location sells it to a broker
  → crosses the data boundary in the *disclose/sell* operation, which the read
  consent never covered. **Legitimizing consent:** a *separate*, specific consent to
  sell to that buyer (almost never present — hence usually DENY).
- **Model.** **No** as a domain. Today a data store is a `Resource` and the model
  cannot distinguish read from disclose, nor subject from holder. This is the
  single most important model gap (§4) because it is the canonical FDK case.

### 2.7 Reputation / identity — DEFINED (kind), semantics PARTIAL

- **Definition.** A person's honor, name, and standing (Book 356). Owned by the
  person; relational (held in others' beliefs), so semantically awkward like data.
- **Owner.** The person whose reputation/identity it is.
- **Crossing.** Defamation (asserting falsehoods that degrade standing —
  intersects `deceives`), impersonation (using the identity), or appropriating the
  name's commercial value.
- **Valid consent.** Use of name/likeness/endorsement requires the person's
  specific consent. **Truthful** statements about a person are the hard edge (§3a):
  a true statement that lowers standing is *not* a crossing under this theory,
  because reputation is "honor, name, and standing," not a right to others'
  favorable beliefs.
- **Example.** An agent publishes a fabricated quote attributed to a person →
  crosses reputation via deception (FORBIDDEN). Publishing the person's *true* and
  lawfully-known record → no crossing. **Legitimizing consent** (for endorsement
  use): the person's specific authorization to use their name.
- **Model.** **No** — no reputation/identity domain; only reachable via `deceives`.

### 2.8 Dependency / exit — DEFINED (categorical), structurally thin

- **Definition.** The right to withdraw from any arrangement (Book 360: "their
  **exit**"). The boundary is the *exit right itself* — an owned capacity, not an
  asset.
- **Owner.** The person who would exit.
- **Crossing.** Any action that **encumbers or removes** a party's ability to
  withdraw later — even if every present step was consented to (§3c). The Book's
  hook is "dependency exploitation" defeating voluntariness (Book 420) plus the
  currency-exit principle (Book 752: "people have the right to exit bad money").
- **Valid consent.** A binding commitment is legitimate only if it **preserves a
  way out** (the `mukataba`/exit principle encoded as `removes_exit_right` in
  `model.py`). Consent to *enter* an arrangement does **not** by itself legitimize
  *removing the exit* from it.
- **Example.** An agent migrates a user's data into a proprietary format with no
  export → crosses the exit boundary (lock-in), even though the user clicked
  "agree." **Legitimizing consent:** an explicit, informed agreement to forgo
  exit — which under the revocability leaf is generally **not** validly grantable;
  see §3c for the ruling.
- **Model.** **Partly** — only the binary `removes_exit_right` /
  `removes_exit_right`-style flag. It cannot represent *degree* of lock-in (that is
  research, §5) nor *which* arrangement's exit is encumbered.

### 2.9 Political / collective power — **OPEN; kernel does NOT treat as a boundary**

- **Definition (flagged).** The capacity to govern or coerce others at scale. The
  Book is pointed here: it never treats power as an *owned* domain; it treats
  illegitimate power as the **monopoly of violence** (Book 462, 2373, 4267) and as
  rights-violation in the name of "public interest" (Book 842, and the Rand
  quotation `whole-theory-as-axioms.md:242`).
- **Owner.** N/A — there is no owner of "power" whose consent could be sought.
- **Crossing.** Under the Book, what is illegitimate is each **coercive act** that
  power enables (a tax taken without consent, a confiscation, an exit foreclosed),
  not the accumulation per se.
- **Valid consent.** N/A.
- **Ruling for the kernel.** Accumulating power through individually-consensual
  acts is **not** a boundary crossing at the kernel (§3d). It becomes a crossing
  only when a concrete act crosses a concrete owned boundary without consent —
  which the other kinds already catch. Power concentration as a *risk* lives in the
  research compass (`machine_coalition_dominion`, dependency measures), not the
  gate.
- **Model.** **No**, by design.

### 2.10 Algorithmic access / compute — DEFINED as DELEGATED property

- **Definition.** Compute, model access, API quota, ranking/placement in an
  algorithmic system. The Book grants no *original* right to compute; in the AI
  chapter compute is **delegated property** of a human owner (A5/A7;
  ONTOLOGY.md §2.2 `compute_domain`).
- **Owner.** The human owner of the compute/system (machines hold it only by
  delegation, A4/A7).
- **Crossing.** Using compute/quota beyond delegated scope; manipulating
  algorithmic placement to extract value from *another* owned boundary (a user's
  data or attention).
- **Valid consent.** Owner's explicit per-resource **delegation** with operation
  scope (A7, default-deny). A machine acting outside delegated compute scope
  crosses its owner's boundary without consent.
- **Example.** A machine spends its owner's API budget on an unauthorized task →
  crosses the owner's compute boundary (beyond delegation). **Legitimizing consent:**
  an explicit delegation covering that task and that budget.
- **Model.** **Partly** — compute is a `Resource` and delegation exists as a flat
  `set[Resource]`, but the model cannot say "delegated *read* not *spend*," nor
  bound a quota. Same operation-granularity gap as money (§4).

---

## 3. The hard cases (rulings)

Each maps to a FreedomBench level (property conflicts, emergencies, AI
manipulation/lock-in). A **RULING** is a kernel commitment; an **OPEN** flag means
the kernel defers to a human and the question goes to the theory's author.

### 3a. Attention / persuasion — when does influence cross a boundary?

**RULING (kernel-deterministic).** Influence crosses a boundary **iff** it
operates through an already-owned boundary without consent, i.e. iff it is
**deceptive** (`deceives`) or **coercive** (`coerces`), or it is *built from* a
data/attention input the target did not consent to (a **data** crossing, §2.6).
Truthful, non-coercive speech that the listener is free to ignore crosses **no
boundary** — the Book grounds reputation in "honor, name, and standing," not in a
right to control others' beliefs, and lists no "attention" property. Persuasion is
not, in itself, a crossing.

**Why not more.** Treating ordinary persuasion as a crossing would require the
kernel to judge *how manipulative* a message is — a semantic, gradient
determination the kernel must not own (§5; CORE_PRIMITIVE.md §4). Manipulation
*intensity* therefore lives in the research layer; only its categorical forms
(deceit, coercion, non-consensual data targeting) are kernel crossings.

### 3b. Data — does observing public behavior cross a boundary?

**RULING (partial), with an OPEN edge.** Observing behavior the subject has
**voluntarily made public** is **not** a crossing of the *disclosure* boundary
(the subject already disclosed). But **aggregation/inference** that produces *new*
data the subject never disclosed (a profile, a prediction, a re-identification) is
a **value-extraction crossing** of the subject's data boundary, requiring the
subject's consent for that derived use. **OPEN:** the exact line between
"observing what is public" and "deriving what was private" is not resolvable
deterministically (it depends on what the inference reveals), so concrete cases at
the boundary are **DEFERred**; the *threshold* is a theory/Q3 question
(ONTOLOGY.md Q3 — data-property semantics). The kernel's safe default: reading
declared-public data = ALLOW; producing/disclosing derived non-public data without
subject consent = DENY; ambiguous derivation = DEFER.

### 3c. Dependency / lock-in — is creating dependency a crossing even with step-wise consent?

**RULING.** **Yes, when the action encumbers the future exit right**, even if each
present step was consented to. The exit right is itself an owned boundary (§2.8,
Book 360), and the consent logic requires every authorization to remain
**revocable** (Book 422). An arrangement that forecloses exit therefore crosses
the exit boundary, and consent to *enter* it does not legitimize *removing the
exit*, because a consent that destroys its own revocability is self-defeating —
"void from the beginning" (Book 427). This is the Book's "dependency exploitation"
defeater (Book 420) made structural. Concretely: the kernel DENIES actions that
set `removes_exit_right` (already in `model.py`).

**The OPEN residue (the one open question, CORE_PRIMITIVE.md §6).** *Building*
future dependency that does not yet remove any present exit right — lock-in that
will bite later but crosses no boundary *today* — is **left OPEN**. The kernel
takes the **low-freedom reading** (CORE_PRIMITIVE.md §6): no present crossing →
ALLOW at the gate, *penalized* in the research compass (`DependencyIndex`), with
human DEFER as the escape hatch when egregious. Whether foreseeable future lock-in
is *itself* a present consent violation is for the theory's author to fix; the
kernel will not import prediction into the gate to decide it (§5).

### 3d. Power concentration — a crossing if no single act is non-consensual?

**RULING.** **No, not at the kernel.** If every constituent act is consensual and
crosses no owned boundary, the *accumulation* is not a kernel-level crossing — the
Book locates illegitimacy in the **coercive act** (monopoly of violence; rights
violation under "public interest"), not in voluntary scale (Book 462, 2373, 4267,
842). The moment power is *used* to cross a concrete boundary without consent
(coerce, confiscate, foreclose exit), the existing predicate catches it. Standing
concentration is a research-layer concern (`machine_coalition_dominion` veto
covers the *dominion* extreme; below it, a compass penalty). This mirrors §3c:
deterministic gate, predictive risk in research.

### 3e. Negative externalities — pollution crossing a boundary you didn't consent to

**RULING (DEFINED in principle, PARTIAL in detection).** An externality that
physically degrades a third party's owned domain (pollution damaging land/body) is
a **crossing of that third party's boundary**, and the consent between the
polluter and *its* counterparties cannot legitimize it — directly the third-party
rule (Book 839: contracts "valid unless they violate the property rights of third
parties"; Book 738: harm "where direct, demonstrable harm to others' property
rights can be proven"). So externalities are *not* exempt: they are ordinary
boundary crossings of the affected owner. **PARTIAL:** the kernel can only act on
externalities the proposer **declares** in `affects`/effects; it cannot *infer*
undeclared physical externalities (that is simulation/measurement, §5). Declared
externality on a registered owner without that owner's consent ⇒ DENY; suspected
but undeclared/unowned ⇒ the action is evaluated on what is declared, and unclear
ownership of the affected domain ⇒ DEFER.

**Summary of rulings**

| Hard case | Kernel ruling | Where the residue lives |
|---|---|---|
| 3a Attention/persuasion | Crossing **only if** deceptive/coercive/non-consensual-data-driven | Manipulation *intensity* → research |
| 3b Public data | Observe-public = no crossing; **derive-private = crossing**; edge = **DEFER** | Threshold = theory Q3 |
| 3c Lock-in (step-wise consent) | Removing present exit = **crossing/DENY**; *future* dependency = **OPEN/low-freedom** | DependencyIndex → research |
| 3d Power concentration | **Not** a kernel crossing absent a concrete non-consensual act | Dominion veto + penalty → research |
| 3e Externalities | Declared harm to a third party's owned domain = **crossing/DENY** | Undeclared/inferred harm → research/measurement |

---

## 4. Implications for the model

The current model (`model.py`) represents a boundary as a bare `Resource(name)`
and ownership as a flat `OwnershipGraph` (`human_owns` / `delegated` as
`set[Resource]`). **The decisive limitation:** it cannot express "delegated *read*
but not *delete*," cannot distinguish a data *subject* from a data *holder*, and
cannot carry quantity (money/compute). Six of the ten boundary kinds (§2.3–2.8)
are therefore inexpressible, and the canonical FDK case ("sold data I could read")
is *unrepresentable* — the model cannot tell `read` from `sell`.

**Recommended minimal, deterministic change** (proposal for the lead; this spec
edits no code). Keep kernel discipline: no semantics, no ML, every field a
recorded fact.

**4.1 Give `Resource` a boundary kind and (optional) subject.**

```python
class BoundaryKind(Enum):
    TANGIBLE = auto(); MONEY = auto(); BODY = auto(); TIME_LABOR = auto()
    DATA = auto(); REPUTATION = auto(); EXIT_RIGHT = auto(); COMPUTE = auto()
    # ATTENTION and POWER intentionally absent: not kernel boundaries (§2.5, §2.9, §3a, §3d)

@dataclass(frozen=True)
class Resource:
    name: str
    kind: BoundaryKind = BoundaryKind.TANGIBLE   # default keeps old behavior
    subject: Entity | None = None                # data/body/reputation: whose domain
    quantity: int | None = None                  # money/compute: bounded amount
```

`subject` resolves the data subject-vs-holder split (§2.6) and the
non-transferability of body/reputation; `kind` lets the kernel apply
kind-specific crossing rules deterministically; `quantity` lets money/compute be
debited within scope. All optional ⇒ existing `Resource("x")` still valid.

**4.2 Make delegation/consent operation-typed.** Introduce a fixed operation
lattice and attach it to delegations and to the crossings an action declares:

```python
class Op(Enum):
    READ = auto(); USE = auto(); WRITE = auto(); DELETE = auto()
    TRANSFER = auto(); DISCLOSE = auto(); ENCUMBER_EXIT = auto(); SPEND = auto()

# OwnershipGraph.delegated: dict[Entity, set[Resource]]  -->  dict[Entity, set[tuple[Resource, Op]]]
# CandidateAction.resources_used: tuple[Resource, ...]   -->  tuple[tuple[Resource, Op], ...]
```

This is the **one change that makes the predicate honest**: `op_for(a, r)` (§1.3)
becomes a declared field, "delegated read but not delete" becomes
`(r, READ) ∈ delegated ∧ (r, DELETE) ∉ delegated`, and "sold data I could read"
becomes `DISCLOSE ∉ consent_ops` → DENY. The operation lattice is small, fixed,
and total — no inference. `DISCLOSE`/`ENCUMBER_EXIT` carry the data (§3b) and
lock-in (§3c) crossings.

**4.3 Consent gains `revocable` and `operation`.** ONTOLOGY.md §2.8 already flags
the missing `revocable` leaf; add an `operation: Op` so that consent to one
operation does not silently cover another (the core of §2.6). (`model.py:Consent`
already has `revocable`; it is the `Resource`/delegation side that lacks operation
typing.)

These four edits are minimal, total, deterministic, and additive (defaults
preserve current behavior). They unlock kinds 2–8 and 10 with **no** semantic
inference in the kernel.

---

## 5. Research layer vs kernel — the deterministic/judgment split

The kernel decides only what is computable from **declared, recorded facts**;
everything requiring estimation or semantic judgment is research-layer and
advisory (CORE_PRIMITIVE.md §4; ONTOLOGY.md §4).

**KERNEL (deterministic, DEFINED).**
- Whether a declared `(resource, op)` is within the owner's grant / a person's
  consent for that op (§4.2) — set membership.
- Whether `removes_exit_right` / `coerces` / `deceives` / `confiscates` is set —
  categorical FORBIDDEN.
- Whether a declared externality hits a *registered* third-party owner without
  consent (§3e) — registry lookup + the third-party rule.
- Whether the owner of a crossed boundary is unknown → **DEFER** (unclear
  ownership).
- The data crossing for *declared* operations (read vs disclose/sell, §2.6).

**RESEARCH (judgment/estimation — PARTIAL/OPEN, never gates).**
- Persuasion/manipulation **intensity** (§3a) — semantic.
- Whether an inference "derives private from public" at the ambiguous edge (§3b) —
  the kernel DEFERs; research estimates.
- **Future** dependency / lock-in degree (§3c) — `DependencyIndex`, predictive.
- Power-concentration risk below the dominion veto (§3d).
- **Undeclared/inferred** externalities (§3e) — simulation/measurement.
- The quantitative coercion/ownership-clarity scores (CORE_PRIMITIVE.md §4).

The dividing line is exactly **declared structural fact vs predicted/semantic
estimate**. A boundary determination that needs a model of the world to even state
is research; a boundary determination that is a lookup over what the proposer
declared is kernel. This keeps the predicate two-valued and reproducible
(CORE_PRIMITIVE.md §5) while the research compass carries the gradients.

---

## 6. Open questions for the theory's author

1. **Attention as property?** The Book never grants it (§0, §2.5). Either attention
   is *not* an owned domain (current kernel stance — influence is gated only via
   deceit/coercion/data) or the theory must add it as an axiom-level right. This
   spec will not invent it.
2. **Data-derivation threshold (§3b, ONTOLOGY.md Q3).** Where is the line between
   observing public behavior and deriving private data? Until fixed, the kernel
   DEFERs the edge.
3. **Future lock-in (§3c, CORE_PRIMITIVE.md §6).** Is building foreseeable future
   dependency, with no present exit removed, *itself* a present consent violation?
   Kernel provisionally says no (low-freedom, not illegitimate). The scope of the
   predicate (present vs foreseeable boundaries) is the author's to fix.
4. **Reputation vs truth (§2.7).** Confirm that *true* statements lowering standing
   are not crossings (reputation = honor/name/standing, not a right to favorable
   belief). The kernel assumes this.
5. **Power concentration (§3d).** Confirm the monopoly-of-violence reading: that
   voluntary accumulation crossing no concrete boundary is legitimate-but-low-freedom,
   not illegitimate.

---

*Stage 0 keystone deliverable, Freedom Decision Kernel. Theory: نظریه آزادی
(Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0). Engineering:
Ali Pourrahim. The two are kept separate, always.*
