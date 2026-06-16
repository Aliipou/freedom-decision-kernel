# Aggregation — Collective Ownership — FDK 2.0, Project B (Layer 4)

> The second open frontier (`LIMITATIONS.md` §2, `ROADMAP.md` Layer 4). The frozen
> kernel models **one human owner per resource** (`OwnershipGraph.human_owns:
> dict[Entity, set[Resource]]`). The real world is full of things no single person
> owns: a corporation, a DAO, a nation, a city, a union, the internet, a river, the
> ocean, a model trained on a billion people's data. The roadmap is explicit: *do not
> answer fast — collect examples and case studies first; this is where most theories
> explode (Arrow, Sen).*
>
> This document does the honest, modest thing a v0 can do: it lays out a **taxonomy of
> collective-ownership forms**, and for each form states plainly **whether it can be
> represented in the frozen v1.0 kernel** — and if so, *how* (by reduction to the
> existing single-owner primitive), and if not, *why not* (citing `LIMITATIONS.md`,
> not pretending it is solved).

## The non-negotiable architectural rule (same as every research layer)

This layer is **advisory only**. It lives in `fdk_research/`, imports nothing into
`fdk_kernel/` (mechanically enforced by `tests/test_boundary.py`), and it **never
returns a verdict.** It does not ALLOW, DENY, or DEFER. It produces an
`AggregationAssessment` whose only outputs are: name the collective form, say whether
it is representable in v1.0, and — when it is — recommend the *reduction* (the
construction in terms of the frozen primitive) for a human to apply. The kernel is
never edited, never extended, never overridden. Adding a "group owner" field would be
adding to the frozen ownership model (an axiom by the back door, `FREEZE.md` §5) — so
we do not. We reduce, or we declare the gap.

> aggregation layer **classifies** the collective form → recommends a **reduction** to
> single-owner terms (if any) → a human **builds** that reduction in the ordinary
> kernel → the **frozen kernel** reads an ordinary single-owner graph.

The point: where a collective form *can* be honestly expressed as ordinary
single-owner consent, this layer shows the construction; where it *cannot*, this layer
refuses to fake one and instead points at the documented gap.

## The taxonomy (forms of collective ownership)

Each form is an observable structural fact about *how* a thing is owned, not a
political preference about how it *should* be owned. The first three reduce to the
frozen primitive; the last three do not.

| Form | What it is | Representable in v1.0? | Reduction (or the gap) |
|---|---|---|---|
| `UNANIMOUS_GROUP` | a set of individuals who must *all* agree (a partnership, a small co-op, a 2-of-2 marital asset, a unanimous-consent club) | **yes** | require a valid `Consent` from **every** member; one hold-out → no valid consent → kernel denies on its normal grounds |
| `CHARTERED_ENTITY` | a legal/contractual person distinct from its members (a corporation, an incorporated DAO, a registered union, a foundation) | **yes** | treat the entity as **its own owning `Entity`**; its internal governance decides what *it* consents to, *outside* the kernel; the kernel sees one owner |
| `REPRESENTED_COLLECTIVE` | a group acting through an **explicitly delegated** agent within a bounded mandate (an HOA board, an elected trustee, a guild steward) | **yes, conditionally** | model as the delegate holding a **scoped delegation** (`OwnershipGraph.delegated` / `machine_scope`) from each principal; valid only while the mandate is intact and revocable — outside the mandate it collapses to `UNANIMOUS_GROUP` |
| `MAJORITY_COLLECTIVE` | a group that decides by **majority/plurality vote** binding the minority (a nation's electorate, a city, most large unions, a DAO with token-majority rule) | **no** | a majority cannot supply the *dissenters'* consent; binding them is structurally `confiscates` / `coerces` to the kernel. **This is the Arrow/Sen wall — see below.** Gap, not solution. |
| `COMMONS_NONEXCLUDABLE` | a present-ownerless, non-excludable good (the high seas, the atmosphere, a wild river, deep-sea genes, the open internet, a public square) | **no** | there is **no owner**, so there is **no boundary for the gate to check**; every individual use is invisibly ALLOW, and individually-legitimate uses sum to collective collapse (tragedy of the commons). Gap (`LIMITATIONS.md` §2). |
| `UNOWNED` | a thing with no owner *and* no live claimant — `res nullius`, an abandoned thing, a dead person's estate before succession, collective data with one `subject` per `Resource` and no representable holder | **no** | the kernel has nothing to bind a consent to; it cannot legitimize an *origin* of title (the bootstrapping gap, `FOUNDATIONAL_ATTACKS.md`). Gap, not solution. |

### Why `UNANIMOUS_GROUP`, `CHARTERED_ENTITY`, `REPRESENTED_COLLECTIVE` reduce cleanly

The frozen primitive is `Legitimate(action) ⟺ ∀ boundary b crossed: ∃
valid_consent(owner(b), action)`. None of these three needs a *new* notion of owner:

- **Unanimous group** keeps the single-owner gate and runs it once per member: the
  quantifier `∀ member` is supplied *outside* the kernel by attaching one `Consent`
  per member to the `CandidateAction`. A unanimous club is just "many owners, all of
  whom must say yes" — exactly what the existing `consents` tuple already expresses.
  This is the public-goods reduction's honest half: a lighthouse funded by *every*
  beneficiary's voluntary payment is legitimate; the dishonest half (forcing the
  hold-out) is the tax FDK denies — which is `MAJORITY_COLLECTIVE`, below.
- **Chartered entity** keeps the single-owner gate and just makes the *entity* the
  `Entity` that owns the `Resource`. A corporation owning a factory is one owner. How
  the corporation forms *its* will (board vote, shareholder meeting) is internal
  governance — policy, not legitimacy — and stays out of the kernel by design.
- **Represented collective** is a chartered/unanimous group that has additionally
  *delegated* a scoped mandate, which the kernel already models first-class
  (`delegated`, `machine_scope`, A5 containment). Its representability is *conditional*
  on the delegation being real, bounded, and revocable; strip the mandate and it is no
  longer a represented collective but a bare group needing unanimity again.

### Why `MAJORITY_COLLECTIVE` does NOT reduce — and where Arrow/Sen bite

A majority decision binds dissenters *without their consent*. To the frozen kernel a
non-consenting owner whose boundary is crossed is the textbook violation: the action
`confiscates` or `coerces`, and is DENIED. There is no honest reduction that turns 51%
of consents into the missing 49%; pretending otherwise would be the *exact*
majority-vote laundering trick the red-teams already defeat (`LIMITATIONS.md`: "every
laundering trick … majority-vote … is DENIED").

This is the Arrow/Sen wall stated precisely. **Arrow's impossibility theorem** says no
voting rule aggregates individual preferences into a collective ordering while keeping
a few obviously-desirable properties (unanimity, non-dictatorship, independence).
**Sen's liberal paradox** says you cannot even guarantee a minimal individual-rights
veto and Pareto efficiency at once. FDK does not *fall* to these theorems — it
**sidesteps** them by *declining to build any social-welfare ordering at all*: it has
no aggregation rule to be impossible, because it aggregates nothing. The cost of that
escape is exactly this gap: FDK cannot *make* the binding collective choices those
theorems are about (taxation, redistribution, conscription, eminent domain). As
`LIMITATIONS.md` §2 records:

> "FDK *escapes* Arrow/Sen's impossibility only by **declining to build any social
> ordering** — which is also why it cannot make the collective choices those theorems
> are about. Honest, but a limit."

So `MAJORITY_COLLECTIVE` is marked **not representable**, and the recommendation is not
a construction but a pointer: either obtain genuine unanimity (degrade to
`UNANIMOUS_GROUP`) or accept that the kernel will DENY the coercion of dissenters — and
record that divergence honestly rather than bending the verdict.

### Why `COMMONS_NONEXCLUDABLE` and `UNOWNED` do NOT reduce — the structural gap

These are not "the kernel decides them wrongly"; they are "the kernel has **nothing to
decide**." The gate's entire job is to find, for each crossed boundary, the owner whose
consent is required. A true commons / non-excludable good has **no owner**, so there is
**no boundary and no owner term** — the universally-quantified condition is vacuously
satisfied and every use reads as ALLOW. That is precisely the tragedy-of-the-commons
hole in `LIMITATIONS.md` §2:

> "Tragedy of the commons: depleting a present-ownerless ocean / atmosphere is
> invisible (ALLOW) — every individually-legitimate act sums to collective collapse."

`UNOWNED` adds the bootstrapping edge: even where we might *want* to assign an owner
(an estate at death, a billion-person training corpus), the frozen model gives us no
primitive to create title from nothing — *no input-graph kernel can* (`LIMITATIONS.md`,
"the paradigm's limit, not FDK's alone"). For both forms the layer's `recommendation`
is an explicit, loud non-solution: *this form has no representable owner in v1.0; do not
fabricate one; this is a documented scope limit, not a decided case.*

## Case studies (the examples the roadmap demands before answering)

| Case | Form | Notes |
|---|---|---|
| Two-person partnership, both must sign | `UNANIMOUS_GROUP` | clean reduction; one partner refuses → no deal, correctly |
| Lighthouse funded by every beneficiary | `UNANIMOUS_GROUP` | legitimate iff truly unanimous; the hold-out problem is real, not waved away |
| Apple Inc. owns a factory | `CHARTERED_ENTITY` | entity is the owner; shareholder governance is internal/out-of-kernel |
| Incorporated DAO with a treasury | `CHARTERED_ENTITY` | same as a corporation once it is a legal person with bounded internal rule |
| HOA board acting under a recorded mandate | `REPRESENTED_COLLECTIVE` | scoped, revocable delegation; outside the mandate → back to unanimity |
| A nation taxing its citizens | `MAJORITY_COLLECTIVE` | dissenters bound without consent → DENY; the documented taxation divergence |
| Token-majority DAO seizing a minority's stake | `MAJORITY_COLLECTIVE` | majority-vote laundering; DENIED, by design |
| The atmosphere / a wild river / high seas | `COMMONS_NONEXCLUDABLE` | no owner → no boundary → invisible ALLOW; the commons gap |
| Open internet backbone, public square | `COMMONS_NONEXCLUDABLE` | non-excludable; protectable only once enclosed as someone's property |
| A model trained on a billion people's data | `UNOWNED` | one `subject` per `Resource`; the collective has no representable holder |
| A dead person's estate before succession | `UNOWNED` | death is not in the model; estate is permanently "consent-required" |
| `res nullius` / abandoned property | `UNOWNED` | no live claimant; the bootstrapping/origin-of-title gap |

## Honest scope of this version

This is a **v0 scaffold**. The taxonomy is a transparent, hand-set classification, not
a calibrated empirical study of the "thousands of examples and hundreds of case
studies" the roadmap rightly demands before building a real primitive. Its value is
narrow and real: it makes the *reducible* collective forms reducible **without touching
the frozen kernel**, and it makes the *irreducible* ones **loud and explicit** — flagged
`representable_in_v1 = False` with a recommendation that names the gap instead of faking
a solution. Three of six forms reduce; three do not, and saying so plainly is the
contribution. The real Project B needs political philosophy, law (Roman/common/civil/
international), public-economics, and a labeled corpus — and above all it must keep
declining to smuggle a social-welfare ordering into a kernel whose entire integrity is
that it has none.

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Engineering: Ali Pourrahim.*
