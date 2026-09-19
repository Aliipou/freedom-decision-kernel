# Anarchist review — property is the original violence, and your primitive is built from it

> **AI-simulated expert-PERSONA review, NOT independent human peer review.** A hostile
> critique from the anarchist-communist / mutual-aid tradition (Proudhon, *What Is
> Property?*; Kropotkin, *Mutual Aid* and *The Conquest of Bread*; the commons literature
> of Elinor Ostrom read against the grain). Verdicts are the gate's ACTUAL output, pinned
> in `tests/test_review_left.py`.

The Marxist will tell you the ownership graph encodes past coercion. I go further, and
to the root: **property as such — the very relation `human_owns(person, thing)` that your
entire kernel is built out of — is the original violence.** Proudhon: *la propriété,
c'est le vol.* Not "some property is theft," not "property acquired by enclosure is
theft." Property, the institution, is the act of one person drawing a line around a piece
of the world and declaring everyone else excluded on pain of force. Your gate does not
*adjudicate* that violence. Your gate is its automation. You have built a machine whose
single most basic predicate — the thing every axiom rests on — is the exclusion that
anarchism names as the foundational wrong.

## The attack on the primitive itself

The other critics attack what the gate *does*. I attack what the gate *is made of*. Three
moves:

1. **You universalise private property as natural.** `OwnershipGraph.human_owns` is a
   `dict[Entity, set[Resource]]`. Every resource has at most one owner. This is not a
   neutral data structure; it is a metaphysics. It encodes the proposition that the
   default relation between a person and a thing is *exclusive private title*, and that
   any other relation must be reconstructed out of private titles (a "shared" thing is
   just two overlapping titles). Kropotkin's whole point in *The Conquest of Bread* is
   that this is historically false and morally backwards: the field, the road, the
   accumulated knowledge of how to farm it, the inherited tools — these are the *common
   inheritance of humankind*, and the private parcelling of them is the anomaly requiring
   justification, not the baseline. Your model makes the anomaly the axiom.

2. **The mutual-aid commons is unrepresentable.** Kropotkin's *Mutual Aid* documents the
   commons that actually sustained human and animal life: the village field held by all
   and alienable by none, the open pasture, the seed library, the gift economy where
   bread moves without a transaction. None of these is `human_owns(p, r)`. They are
   *inalienable collective stewardship* — held by the community, governed by custom,
   withdrawable by no individual. Try to encode "the three villagers hold the field in
   common" and the only thing your model can say is `human_owns = {v1:{field},
   v2:{field}, v3:{field}}` — three *full, independent* private titles to the same thing.
   That is not a commons. That is a contradiction your gate resolves in the worst
   possible way (see the verdict below).

3. **The primitive is individualist to the bone.** Every actor is a single `Entity`.
   Every consent is one person's boolean. There is no collective subject — no commune, no
   assembly, no "we" — that can hold, decide, or be wronged. The mutual-aid tradition's
   core unit, the cooperating group, has no type in your model. You can represent a
   crowd of individuals; you cannot represent a community. So the only freedom your
   kernel can certify is the freedom of the proprietor.

## The gate's ACTUAL verdict (run it)

| Case | FDK verdict | The wrong it reveals |
|---|---|---|
| Lord encloses a commons, **graph already grants him title** | **ALLOW** `(True, [])` | enclosure, once congealed into title, is invisible |
| Lord encloses a commons he does *not* yet own | **DENY** (A3) | the gate "protects" the commons only by treating it as *someone's* unowned-by-the-lord property — never as a commons |
| Three villagers "hold a field in common"; **v1 alone sells it** | **ALLOW** `(True, [])` | the commons is shredded into private titles; any one co-owner can unilaterally liquidate the whole |
| A mutual-aid gift of bread (giver owns, transfers, recipient consents) | **ALLOW** | the gift is legible — but *only* because it is re-described as a private transfer |

Look at the second and third rows together. They are the trap. The gate has exactly two
ways to treat a commons, and both destroy it:

- If the commons is **unowned**, the gate protects it only incidentally, via A3 ("you
  may not use what you don't own") — which is the *property* axiom doing the work. The
  commons is safe only for as long as no one holds title; the moment a title appears
  (legitimately, by your lights — a homestead, a purchase, a grant), enclosure becomes
  `ALLOW`. The commons has no standing of its own; it is a power vacuum waiting to be
  claimed.

- If the commons is **collectively held** (the only way I can even gesture at it in your
  model), the gate reads each co-owner as a *full* owner, so **the unilateral sale of the
  commons by a single villager — the precise act of betrayal that custom and inalienability
  exist to prevent — is certified legitimate.** The collective has no veto, because the
  collective is not a thing your model can represent. The commons is liquidatable by its
  least loyal member, with the gate's blessing.

So FDK does not merely *fail to support* commons. It actively **converts every commons it
touches into private property** — protecting it as a vacuum to be claimed, or dissolving
it into severable private shares. That is enclosure implemented as a type system.

## Classification

**REPRESENTATION-FAILURE, hardening into a GENUINE GAP.** Distinguish the two halves:

- *Representation-failure (the deeper one).* Collective inalienable stewardship has no
  type. This is not a verdict the gate gets wrong; it is a moral object the gate cannot
  hold. `LIMITATIONS.md` §2 ("Aggregation") names "who owns what no one individually
  owns" but frames it as a *funding* problem (lighthouses, free-riders) — an
  efficiency gap. That framing is itself the bourgeois move: it assumes the only question
  about a commons is how to pay for it, when the question is whether parcelling it was
  ever legitimate. The anarchist gap is not "FDK can't fund public goods." It is **"FDK
  cannot represent a thing that is held by all and owned by none, and so re-describes it
  as either nobody's or somebody's."**

- *Genuine gap (the operational one).* The unilateral-sale verdict is a concrete wrong
  output: jointly-held land liquidated by one of three holders, ALLOW. Pin it; it is the
  testable face of the representation-failure.

Not a CRITICAL break in your sense — the gate prints no `slavery → ALLOW`. But note what
that bar smuggles in: you define a "break" as the gate blessing the violation of a
*property-bearing individual*. Of course the gate never does that — it is a theory of
property-bearing individuals. The wrongs it cannot see are the wrongs done to *the
commons* and to *the collective*, which have no rights in your ontology to violate. **A
theory cannot break on a value it does not contain.** That immunity is not strength. It
is the precise shape of the blind spot. The rival comparison confirms it: on every commons
case, all six kernels return ALLOW — none of them, not even the Rawlsian, has a commons in
its world either. The whole panel is a panel of proprietors arguing over the terms of
exclusion.

*AI-simulated persona, not human peer review. Theory: نظریه آزادی, Mohammad Ali Jannat
Khah Doust (CC BY 4.0). Engineering: Ali Pourrahim.*
