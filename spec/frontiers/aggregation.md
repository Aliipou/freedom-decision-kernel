# Aggregation / Collective Ownership — the frontier where FDK is wrong

> **Research notes — open problem, not a solution.**
>
> This document is written *against* FDK, not for it. It is the hostile companion to
> [`spec/AGGREGATION.md`](../AGGREGATION.md), which is FDK's self-defense. Where that
> document says "three of six collective forms reduce cleanly and the rest are honest
> scope limits," this document argues that the "honest scope limit" framing conceals a
> **structural error**: FDK does not merely *fail to represent* collective ownership, it
> **actively makes a false empirical prediction** about it — the tragedy of the commons —
> that the single most relevant rival, **Elinor Ostrom**, spent forty years and a Nobel
> Prize empirically refuting. FDK cites Ostrom (1990) twice in
> [`COMPASS_MEASUREMENT.md`](../COMPASS_MEASUREMENT.md), both times *in support of its own
> thesis* that fuzzy boundaries are costly. It has never engaged her central finding,
> which contradicts it. That neglect is the subject of this file.

---

## 0. The charge, in one paragraph

FDK's core primitive is `Legitimate(action) ⟺ ∀ boundary b crossed: ∃
valid_consent(owner(b), action)` (`src/fdk_kernel/model.py`; `OwnershipGraph.human_owns:
dict[Entity, set[Resource]]` — *one human owner per resource, no group owner*). For any
good that **no single person owns** — a river, the atmosphere, an ocean fishery, the
radio spectrum, the internet, a national park, a language, a 100-million-person training
corpus — the predicate's universally-quantified condition `∀ boundary b crossed` ranges
over an **empty set of owned boundaries**. A universal over the empty set is *vacuously
true*. **Therefore every extraction from a commons is `Legitimate` — silently, by the
structure of the logic, with no boundary to flag and no owner to consult.** FDK's own
`LIMITATIONS.md` §2 admits this ("depleting a present-ownerless ocean / atmosphere is
invisible (ALLOW)"). What `AGGREGATION.md` will not say, and what this file insists on,
is that *vacuous-ALLOW on a depletable commons is not silence — it is a prediction*:
the prediction that commons collapse, i.e. Hardin's tragedy of the commons. **Ostrom
showed that prediction is empirically false for thousands of real commons.** A theory
whose structure predicts a phenomenon that does not occur is not "out of scope." It is
wrong on that phenomenon.

---

## 1. The problem stated rigorously

### 1.1 No owner ⇒ no boundary ⇒ the gate is silent

The kernel decides one thing: for each boundary an action crosses, is there valid
consent from that boundary's owner? Three quantities must be defined for the gate to
speak:

1. **the boundary** `b` (a `Resource` with a `BoundaryKind`),
2. **the owner** `owner(b)` (a single `Entity` via `human_owns`),
3. **the consent** `valid_consent(owner(b), action)`.

For a true commons, **(2) is undefined**. `human_owns` is a function from one `Entity` to
a set of `Resource`s; there is no key whose value contains "the high seas." So either:

- **(a)** the resource is simply *absent* from every owner's set ⇒ the action "crosses no
  owned boundary" ⇒ `∀ b ∈ ∅` is vacuously satisfied ⇒ **ALLOW**; or
- **(b)** the resource is modelled as `UNOWNED`/no-claimant ⇒ the gate has nothing to
  bind consent to ⇒ FDK's research layer returns `representable_in_v1 = False` and
  **defers to a human** — i.e. the kernel goes *silent* and answers nothing.

Both branches are failures. (a) is a false ALLOW (the tragedy). (b) is an abstention: the
single most consequential class of decisions in actual political life — fisheries quotas,
carbon budgets, spectrum allocation, watershed governance, pandemic airspace — is exactly
the class FDK cannot decide. A decision procedure that is silent on the commons is silent
on most of collective human survival.

### 1.2 The free-rider / public-good collapse (the *other* half)

The commons has a structural twin: the **public good** (non-excludable *and*
non-rival on the supply side — a lighthouse, clean air, herd immunity, a sea wall,
national defense, basic research). FDK can fund a public good only one way: obtain a
*valid_consent* (voluntary payment) from **every** beneficiary (`UNANIMOUS_GROUP` in
`AGGREGATION.md`). But the defining property of a public good is that consumption cannot
be withheld from non-payers. So the dominant strategy for each beneficiary is to **refuse
to pay and consume anyway** — the free-rider. Under FDK's gate, forcing the free-rider to
pay is `coerces`/`confiscates` ⇒ DENIED. Therefore:

> **The free-rider theorem against FDK.** For any public good with ≥1 rational
> free-rider, the only FDK-legitimate funding (unanimous voluntary payment) is
> unavailable, and the only available funding (compelled contribution) is FDK-illegitimate.
> Hence **no depletable commons and no non-trivial public good has an FDK-legitimate
> provision path.** Lighthouses, vaccines herd-immunity, flood defense, clean air,
> fundamental science, and national defense are each either un-provided or provided only
> by an act FDK condemns.

This is not a corner case. It is the entire domain of *collective action* — the domain
Mancur Olson (*The Logic of Collective Action*, 1965) proved is generically
under-provided by voluntary means, and the domain Ostrom proved is nonetheless *often*
provided by neither market nor state. FDK has a theory of the first impossibility (Olson)
baked into its gate and **no representation at all** of Ostrom's escape from it.

### 1.3 The deeper claim: a commons is not "ownerless," it is *differently* owned

The fatal modelling assumption is that ownership is a *function* `Entity → set[Resource]`:
total, single-valued, exclusive. Real commons are governed by **bundles of overlapping,
non-exclusive use-rights** — what the property-law literature (Schlager & Ostrom 1992)
decomposes into *access, withdrawal, management, exclusion, and alienation*, held by
*different and overlapping sets of people*. A Maine lobsterman has withdrawal rights in a
harbor-gang territory but not exclusion or alienation rights; the gang collectively holds
exclusion; no one holds alienation. **FDK's `OwnershipGraph` cannot express a single one
of these decompositions.** It has exactly one relation (`human_owns`) collapsing all five
rights into one all-or-nothing token. The commons is invisible to FDK not because it is
ownerless but because FDK's ontology of ownership is too coarse to see the way it is
owned. *That* is the representational error, and it is upstream of every case below.

---

## 2. Catalogue of 25+ real, documented cases

For each: the real institution, then **how FDK fails to represent the owner**, then **what
real institutions actually do**. Cases marked **[O]** are commons Ostrom or her
collaborators studied directly; the rest are the adjacent commons the same logic reaches.

### A. Ostrom's directly-studied common-pool resources

**1. Törbel, Swiss alpine commons (grazing, forest, irrigation) [O].**
Studied by Ostrom (*Governing the Commons*, 1990, ch. 3) from Netting's fieldwork. A
village charter dated **1517** still governs alpine summer pasture: "no citizen could
send more cows to the alp than he could feed during the winter" (the *wintering rule*),
enforced by local officials, with the meadows held in **private** parcels but the high
alp held in **common**. Survived ~700 years without depletion or privatization.
*FDK failure:* the alp has no single `owner`; the wintering rule is a *management* right
held collectively with no alienation right anywhere — unrepresentable in `human_owns`.
FDK would read each grazing act as vacuous-ALLOW and predict overgrazing. *Reality:* a
boundaried, monitored, sanctioned, centuries-stable commons.

**2. Japanese *iriai* common forests/mountains (Hirano, Nagaike, Yamanoka) [O].**
Ostrom 1990, ch. 3 (from McKean's work). Thousands of villages governed *iriai-chi*
(common land) for fuel, fodder, thatch since the Tokugawa era via *kumi* (work groups),
detailed seasonal opening dates, graduated fines, and *detectives* (hired monitors).
*FDK failure:* the forest's withdrawal rights are time-rationed and person-rationed by a
village assembly that is not an `Entity` owning a `Resource`. No reduction to a single
owner exists. *Reality:* documented multi-century sustainability.

**3. Spanish *huerta* irrigation — Valencia, Murcia, Orihuela, Alicante [O].**
Ostrom 1990, ch. 3. The **Tribunal de las Aguas** of Valencia meets every Thursday at the
cathedral's Apostles' Door and has adjudicated water disputes for **over 1,000 years** —
oral, public, with no written record and no appeal. Water is apportioned by *turn*
proportional to land, monitored by elected *síndicos*, with graduated sanctions for theft.
*FDK failure:* the river's flow has no owner; the right is a proportional *turn*, not a
consent from a title-holder. FDK cannot encode "your share is a rotation position," and a
diversion above one's turn is theft-from-no-one to the gate. *Reality:* a millennium of
low-conflict allocation under a customary court.

**4. Murcia/Orihuela contrast and the Spanish *huertas* generally [O].**
Same chapter — Ostrom used the *variation among* huertas (different rules, different
success) as evidence that **institutional design**, not the mere fact of common
ownership, predicts outcomes. *FDK failure:* FDK has one verdict for all of them
(vacuous-ALLOW), so it cannot represent the very variation that is Ostrom's central
explanatory variable.

**5. Philippine *zanjera* irrigation associations [O].**
Ostrom 1990, ch. 3 (from Siy). Farmer-built communal irrigation with *atar* shares,
seasonal labor obligations bundled to water rights, and contracts (*biang ti daga*) by
which landless members earn shares through construction labor. *FDK failure:* the share
*is* a bundled right-plus-duty; FDK's `Consent` has no representation for "a withdrawal
right contingent on a discharged labor obligation." *Reality:* robust farmer-governed
systems, often outperforming state-built canals.

**6. Maine lobster fisheries / harbor gangs [O].**
Acheson, *The Lobster Gangs of Maine* (1988); Ostrom's later work cites it as a textbook
common-pool success. Informal **harbor gangs** control entry to fishing territories;
"perambulators" enforce boundaries by cutting the trap-lines of outsiders; the
state-legal trap limits and the v-notch conservation norm (sparing egg-bearing females)
are co-managed. The Maine lobster stock has *risen* for decades while other fisheries
collapsed. *FDK failure:* the territory is owned by no person and the *exclusion* right is
held by an informal gang with no legal title; line-cutting is coercion against a
non-owner to the gate. FDK would ALLOW unlimited entry and predict collapse. *Reality:*
the canonical empirical counterexample to Hardin — a thriving fishery under common
governance.

**7. Turkish inshore fisheries — Alanya [O].**
Ostrom 1990, ch. 1, the opening exemplar. Local fishers devised a **lottery-rotation**
system: named fishing locations are assigned by drawn lots and rotated daily through the
season so every boat cycles through good and bad spots, eliminating the race-to-fish.
*FDK failure:* the right *is* the rotation slot; there is no owner of "fishing location 7"
and no consent to transfer. FDK cannot encode a self-organized lottery. *Reality:*
conflict and over-effort eliminated by a fisher-designed rule with no state and no
privatization.

**8. Groundwater basins of Southern California — Raymond, West, Central basins [O].**
Ostrom's own dissertation (1965) and 1990 ch. 4. Pumpers facing saltwater intrusion built
**polycentric** institutions — mutual water associations, negotiated court settlements
("the Raymond Basin judgment"), and special districts — to cap extraction without a single
owner or a state seizure. *FDK failure:* an aquifer is the paradigm non-excludable
fugitive resource; FDK has no owner for the basin and would ALLOW each pump. *Reality:*
negotiated, litigated, polycentric self-limitation — Ostrom's model case for
*self-governance through nested institutions*.

### B. Global / planetary commons

**9. The atmosphere as a carbon sink.**
A non-excludable, rival sink with finite assimilative capacity. No owner. *FDK failure:*
every tonne of CO₂ emitted crosses no owned boundary ⇒ vacuous-ALLOW ⇒ FDK structurally
*predicts* unlimited emission. It cannot represent a carbon budget, a cap, or a price.
*Reality:* the Montreal Protocol (ozone — a genuine success), the Kyoto/Paris architecture
(cap-and-trade, NDCs), and the IPCC budget — all *create* a quasi-property in emissions
where none existed, exactly the move FDK cannot make.

**10. The ozone layer / Montreal Protocol.**
The clearest success of treating a global commons as governable: universal ratification,
phased CFC bans, a multilateral fund for the global South. *FDK failure:* the ozone layer
has no owner; a CFC release violates no consent. FDK would ALLOW it. *Reality:* binding
collective restraint with no world-state and no privatization — Ostrom's design principles
operating at planetary scale.

**11. High-seas fisheries (beyond EEZs).**
The textbook open-access resource: bluefin tuna, Patagonian toothfish, North Atlantic cod
(collapsed 1992). *FDK failure:* no owner of the stock ⇒ vacuous-ALLOW ⇒ FDK predicts the
collapse *and licenses it*. *Reality:* RFMOs (regional fisheries management organizations),
ITQs (individual transferable quotas — a *partial* enclosure that often works), the BBNJ
High Seas Treaty (2023). The cod collapse is where FDK's prediction came true *because the
governance Ostrom describes was absent* — proving the prediction is contingent on
institutions, not structural.

**12. Deep-seabed minerals / "common heritage of mankind."**
UNCLOS Part XI declares the seabed beyond national jurisdiction the *common heritage of
mankind*, administered by the International Seabed Authority. *FDK failure:* "mankind" is
not an `Entity`; "common heritage" is the precise legal concept FDK's ontology forbids.
*Reality:* a treaty body licenses and taxes extraction on behalf of an un-representable
collective.

**13. Antarctica (Antarctic Treaty System).**
Sovereignty claims frozen; mining banned (Madrid Protocol); governed by consensus of
consultative parties. *FDK failure:* a continent owned by no one and explicitly *kept*
ownerless by treaty — the opposite of FDK's "enclose it as someone's property" remedy.

**14. Outer space / geostationary orbit / orbital debris.**
Outer Space Treaty (1967): space is "the province of all mankind," non-appropriable.
Orbital slots and debris are a rival commons. *FDK failure:* no owner of an orbit ⇒
ALLOW every launch ⇒ predict Kessler-syndrome collapse. *Reality:* ITU slot coordination,
debris-mitigation guidelines — commons governance, not property.

### C. Infrastructure and knowledge commons

**15. The radio spectrum.**
Non-excludable by physics, rival by interference. *FDK failure:* no owner; a broadcast
crosses no boundary. *Reality:* this is Coase's (1959) famous case — he argued for
*creating* property rights (auctioned licenses), and the FCC did. But spectrum *commons*
(Wi-Fi, ISM bands) also work without property, by protocol-level etiquette. FDK can
represent the auctioned-license version *only after* a state has manufactured the title —
i.e. FDK depends on exactly the collective act it cannot itself legitimize.

**16. The internet backbone / TCP-IP / peering.**
No one owns "the internet." It runs on voluntary peering agreements, IETF
rough-consensus standards (RFCs), and the commons of routing. *FDK failure:* the network
is a `COMMONS_NONEXCLUDABLE` in FDK's own taxonomy — invisible. *Reality:* a
forty-year-old self-governing commons of bilateral contracts and a standards body with no
owner and no coercive power. Possibly the largest functioning commons in history, and FDK
can say nothing about it.

**17. Open-source software (Linux, the Apache ecosystem).**
A non-rival knowledge commons under copyleft (GPL) or permissive licenses, maintained by
distributed volunteers and firms. *FDK failure:* a codebase contributed-to by 20,000
people has no single owner; the GPL is a *use-right grant to everyone* conditioned on
reciprocity — the inverse of single-owner consent. FDK cannot represent "owned by all,
modifiable by all, appropriable-exclusively by none." *Reality:* the copyleft license is
a deliberately engineered *anti*-enclosure commons that has produced the world's
dominant server, mobile, and cloud infrastructure. (Note: Linus Torvalds and the GPL also
illustrate Ostrom's "graduated sanctions" and "nested enterprises" — maintainers, forks,
foundations.)

**18. Wikipedia.**
A knowledge commons authored by millions, owned (as a trademark/servers) by a foundation
but *substantively* governed by editorial consensus, policies, and elected arbitration.
*FDK failure:* the *article* has no owner; every edit crosses a boundary owned by no one.
*Reality:* one of the most-used knowledge resources on Earth, governed by exactly the
graduated, monitored, nested rule-system Ostrom describes — and FDK predicts it should
have been vandalized into uselessness (vacuous-ALLOW on every edit).

**19. Scientific knowledge / the public-domain research commons.**
Cumulative, non-rival, built on prior results. *FDK failure:* no owner of "the body of
genetics knowledge"; FDK can only see the patented enclosures, not the commons they draw
on. *Reality:* the Mertonian norms of open science — a normative commons.

### D. Land, indigenous, and customary tenure

**20. Indigenous communal land tenure (e.g. Aboriginal Australian native title; Native
American tribal trust land; many African customary systems).**
Land held by a clan, band, or nation with overlapping use-rights, sacred-site duties, and
inalienability. *FDK failure:* *Mabo v Queensland* (1992) recognized native title as a
*communal, inalienable* right — the precise combination (community holder + no alienation
right) that `human_owns` cannot express. Reducing it to a `CHARTERED_ENTITY` (a trust)
*destroys the thing*: it converts an inalienable communal right into a corporate asset,
the very "enclosure" that historically dispossessed indigenous peoples. **FDK's only
representable reduction is itself a form of the colonial harm.** *Reality:* sui generis
legal categories (native title, tribal trust) built precisely to *resist* the
single-owner model.

**21. English/European historical commons and the Enclosure movement.**
Manorial commons (pasture, pannage, turbary, estovers) governed by manor courts for
centuries, then enclosed by Acts of Parliament (1604–1914). *FDK failure:* the commoner's
right of pasture was a real, defensible use-right held by no single owner; FDK sees only
the post-enclosure freehold. **FDK is structurally a theory of the enclosers** — it can
only recognize the commons after it has been converted into private title, which is the
historical act of dispossession E.P. Thompson and the Hammonds documented. This is the
sharpest political charge against FDK: its ontology *is* the enclosure.

**22. Acequia irrigation commons of New Mexico / Andean *comunidades*.**
Community ditch associations (*acequias*) with elected *mayordomos*, shared maintenance
(*la limpia*), and water as a communal right attached to the land. State-recognized as
political subdivisions. *FDK failure:* water-as-communal-right is unrepresentable; the
maintenance duty bundled to the right is unrepresentable. *Reality:* a living commons,
legally protected *as* a commons.

### E. Money, sovereign assets, and data

**23. Sovereign wealth funds (Norway's GPFG, Alaska Permanent Fund).**
A nation's oil rents held in trust and paid out (Alaska's Permanent Fund Dividend is a
literal per-capita commons dividend). *FDK failure:* who owns Norway's $1.6T fund? Not the
state-as-`Entity` in any FDK-legitimate sense (the citizens did not each consent to its
formation), not each citizen (no one can withdraw their share). It is a `MAJORITY_COLLECTIVE`
asset FDK marks *not representable*. *Reality:* a functioning collective endowment — and
Alaska's dividend is the closest real-world model of "the commons pays everyone," which
FDK cannot legitimize.

**24. National parks and protected areas (Yellowstone, the NPS commons).**
Held "in trust for the people," non-excludable in principle, congestion-rival in fact. *FDK
failure:* "the people" is not an `Entity`; an entry permit is not a consent from an owner.
*Reality:* trust governance, permits, carrying-capacity quotas — commons management.

**25. Collective / derivative data and the training corpus.**
A model trained on 100M+ people's text/images. FDK's own model has *one `subject` per
`Resource`* — there is no representable holder of "the collective informational value of
everyone's data." *FDK failure:* admitted in `LIMITATIONS.md` §2 — "a model trained on a
billion people has no representable owner." *Reality:* data trusts, data cooperatives
(e.g. Salus.coop, MIDATA), collective-bargaining proposals for data labor — all attempts
to construct a commons holder FDK cannot represent. **This is the case closest to FDK's
own AI mission, and FDK is blind to it.**

**26. Language and culture as a commons.**
A language is owned by no one, sustained by every speaker, depletable (endangered
languages), and extendable (neologisms). *FDK failure:* there is no owner of English; using
a word crosses no boundary; a corporation trademarking a common word *encloses* a piece of
the commons and FDK can only see the trademark, not the loss. *Reality:* language
academies, public-domain norms, anti-genericide trademark limits — weak commons governance
of an un-ownable good.

**27. Herd immunity / public health (a bonus public-good case).**
Immunity is non-excludable and produced by individual vaccination. *FDK failure:* the
free-rider (decline the small personal risk, enjoy the herd) is FDK-legitimate; compelling
vaccination is `coerces` ⇒ DENIED. FDK structurally licenses the anti-vaccine free-rider
and forbids the only known provision mechanism. *Reality:* mandates, school requirements —
coercion FDK condemns, sustaining a public good FDK cannot otherwise provide.

> **Tally:** 27 cases; 8 are commons Ostrom or her direct collaborators studied
> ([O]: Törbel, *iriai*, Valencia/Murcia *huerta*, *zanjera*, Maine lobster, Alanya,
> California groundwater). In **every** case the failure is the same shape: FDK has no
> owner for the boundary, so it either ALLOWs the extraction (predicting collapse) or
> abstains — and in every [O] case the real institution **succeeded** where FDK predicts
> failure.

---

## 3. Where FDK is wrong or cannot represent — brutally

### 3.1 FDK does not "decline to decide" the commons — it *mis-decides* it

`AGGREGATION.md` frames `COMMONS_NONEXCLUDABLE` as `representable_in_v1 = False`, a
*declared gap*. This is a rhetorical softening of a hard fact. Branch (a) of §1.1 —
resource simply absent from every owner's set — is the *default* behavior of the actual
`OwnershipGraph`, and it does not abstain: it **returns ALLOW** by vacuous quantification.
Abstention only happens if a human has already classified the resource as `UNOWNED` in the
research layer, which is not the kernel and not automatic. So the *kernel's* native answer
to "may I empty this ownerless aquifer / fishery / atmosphere?" is **yes**. That is a
verdict, and it is the wrong one. Calling it a "scope limit" obscures that the in-scope,
default behavior is a false permission.

### 3.2 The structural prediction FDK makes — and Ostrom refutes

Make FDK's implicit prediction explicit. Take any depletable common-pool resource R with N
appropriators, no single owner, and individually-legitimate withdrawal:

- For each appropriator i, withdrawing crosses no owned boundary ⇒ `Legitimate` ⇒ ALLOW.
- The sum of N legitimate withdrawals exceeds R's regeneration ⇒ depletion.
- FDK offers no legitimate restraint (any cap binds non-consenting appropriators ⇒
  `coerces`/`confiscates` ⇒ DENIED).

**This is Hardin's "Tragedy of the Commons" (1968) reproduced as a theorem of FDK's
structure.** FDK does not cite Hardin, but it *is* Hardin: rational individual use +
no property + no coercion ⇒ ruin, with privatization or state-Leviathan as the only exits.
Hardin himself wrote: "Freedom in a commons brings ruin to all." FDK's gate makes that the
literal output.

**Ostrom's life work is the refutation of exactly this.** *Governing the Commons* (1990)
and the Workshop's thousands of cases (the IFRI and NIIS databases, the "commons
literature" she synthesized) establish, empirically:

1. Real appropriators in real commons **frequently do not** deplete the resource.
2. They sustain it for **centuries** (Törbel since 1517; Valencia for a millennium).
3. They do so via **neither** Hardin's exits — **not** privatization, **not** an external
   state Leviathan — but **self-organized, self-governed institutions**.
4. Hardin's model assumed *no communication, no monitoring, no rule-making* among
   appropriators — assumptions that are **false** of actual communities.

> FDK's gate hard-codes Hardin's false assumptions. It has no representation for
> communication, monitoring, graduated sanctions, or rule-making among the appropriators —
> the precise variables that, Ostrom showed, *determine whether the tragedy occurs*. FDK
> therefore predicts a phenomenon (commons collapse) that the dominant empirical research
> program in the field demonstrates is **contingent and frequently avoided**. **A theory
> that structurally predicts the falsified general case is wrong on the commons — not
> "scope-limited."** The 2009 Nobel Prize in Economics was awarded for this refutation.
> FDK cites the refuter in a footnote and adopts the refuted prediction in its core.

### 3.3 FDK can only see a commons *after* it has been destroyed-as-a-commons

The only two FDK-representable fates of a commons are:

- **enclosure** → `CHARTERED_ENTITY` / `human_owns` (convert to private title), or
- **state seizure** → `MAJORITY_COLLECTIVE` (which FDK then *denies* as confiscation).

These are **Hardin's two horns**, and FDK inherits both: privatize or Leviathan. Ostrom's
entire contribution is the **third option** — a self-governing commons that is neither —
and it is the one option FDK's ontology cannot hold. This is not a missing feature; it is
a *commitment*. Because `human_owns` is a single-valued exclusive function, the moment you
make a commons representable you have already enclosed it. **FDK's ontology of ownership is
the act of enclosure** (§2 case 21). Politically, this makes FDK structurally the theory of
the encloser and the dispossessor, however libertarian-benevolent its intent.

### 3.4 The free-rider half is equally fatal and equally one-sided

FDK proudly DENIES the tax (`MAJORITY_COLLECTIVE`) as confiscation. But the symmetric cost
is never tallied: **every public good with a rational free-rider is un-providable under
FDK** (§1.2, §2 case 27). FDK's "honest minority position on taxation" is presented as a
falsifiable divergence; restated, it is: *FDK cannot fund lighthouses, vaccines, flood
defense, clean air, basic science, or national defense without committing an act it
condemns.* That is not a minority position on a policy question. It is a coverage gap over
the entire theory of collective action, asymmetrically hidden behind the word "divergence."

### 3.5 The ontology error, named

The root defect (`§1.3`): FDK collapses the **bundle of rights** (access, withdrawal,
management, exclusion, alienation — Schlager & Ostrom 1992) into one all-or-nothing token
`human_owns`. Every commons in §2 is constituted by *splitting* that bundle across
overlapping holders. FDK literally cannot write down "you may withdraw but not exclude,
the gang may exclude but not alienate, no one may alienate." Until the ownership relation
is a *typed bundle over possibly-overlapping subjects*, no honest commons reduction is
even expressible — and adding that is not a feature, it is a new primitive, i.e. a new
axiom (`FREEZE.md` §5). **The freeze that protects FDK's integrity is the same freeze that
forecloses ever representing the commons.**

---

## 4. Engagement with the rivals

### 4.1 Elinor Ostrom — the core engagement (the rival FDK most neglected)

Ostrom's **8 design principles** for long-enduring common-pool-resource institutions
(*Governing the Commons*, 1990, Table 3.1) are the empirical answer to the question FDK
cannot even pose. For each, what it is and **why FDK cannot represent it**:

| # | Ostrom design principle | What it requires | Why FDK cannot represent it |
|---|---|---|---|
| 1 | **Clearly defined boundaries** | who may withdraw, and the resource's edge | FDK *agrees* here (it cites this!) — but FDK's boundary is *single-owner title*, not *defined membership in a commons*. FDK has the word, not the concept. |
| 2 | **Congruence: rules fit local conditions; benefits ∝ costs** | proportional, place-specific appropriation/provision rules | FDK has one global rule (consent-of-owner); it cannot localize or proportion. |
| 3 | **Collective-choice arrangements** | those affected by rules can *modify* them | FDK's axioms are *frozen*; appropriators cannot be modeled as making their own rules. This is the deepest clash: Ostrom's commons are *self-legislating*; FDK's gate is fixed law. |
| 4 | **Monitoring** | monitors who watch the resource, accountable to users | FDK reads `coerced`/`deceived` as *attested booleans* (`LIMITATIONS.md` §3); it has no monitoring primitive at all. |
| 5 | **Graduated sanctions** | escalating penalties for violations | FDK is binary (DENY/ALLOW). It has no graduated anything. The Maine line-cutters, the *iriai* fines, the Valencia penalties — all unrepresentable. |
| 6 | **Conflict-resolution mechanisms** | cheap, fast, local arbitration (the Tribunal de las Aguas) | FDK *defers to a human* but specifies no institution; it has no model of a standing dispute forum. |
| 7 | **Minimal recognition of rights to organize** | external authorities don't override local self-governance | FDK structurally *denies* the right to organize a binding collective (every collective rule binds dissenters ⇒ DENY). It is the external authority that overrides. |
| 8 | **Nested enterprises** (for large systems) | polycentric layers (Ostrom's "polycentricity") | FDK is flat and single-owner; it has no nesting, no polycentric layering. |

**The verdict of the engagement:** Ostrom's principles are a *positive, empirically
validated theory of legitimate collective ownership* — exactly the object FDK declares
unrepresentable. Of the 8, FDK can represent **zero** in a non-trivial sense (it shares
the *word* "boundaries" but not the concept). Ostrom did not merely find counterexamples;
she found the *mechanism* (self-governance under these 8 conditions) that FDK's structure
denies can exist. FDK's neglect of Ostrom is therefore not an oversight of citation but a
**substantive blindness**: the most-validated rival theory of the exact frontier FDK is
stuck on, and FDK never engaged it.

> Note on charity to FDK: one might say Ostrom describes *institutions* (policy) while FDK
> decides *legitimacy*, and the two layers are orthogonal — FDK could sit *under* an
> Ostromian institution that has already constructed single-owner consents. But this
> rescue fails: the Ostromian institution's defining acts (binding the dissenting minority
> to a graduated sanction, monitoring without per-act consent, modifying the rules) are
> each acts FDK's gate would **DENY** as coercion/confiscation if asked to legitimize them.
> FDK cannot sit under an Ostrom commons because it would rule the commons' own
> constitution illegitimate.

### 4.2 Arrow's impossibility theorem

Arrow (1951): no social-welfare function aggregates individual preference orderings into a
collective ordering while satisfying unrestricted domain, Pareto, independence of
irrelevant alternatives, and non-dictatorship. `AGGREGATION.md` claims FDK *sidesteps*
Arrow by "aggregating nothing." **True, but the sidestep is the bug, not the feature.**
Arrow's theorem is a constraint on *how hard collective choice is*, not a license to
refuse collective choice. By aggregating nothing, FDK does not *solve* the aggregation
problem; it **abdicates the entire domain Arrow's theorem is about** (any binding social
choice — budgets, quotas, carbon caps). A theory that escapes an impossibility theorem by
never doing the thing the theorem constrains has not transcended the problem; it has left
the field. Ostrom's commons make binding collective choices *every day* (the Valencia turn
order, the Alanya lottery) — they are *living refutations* that collective choice is
hopeless, and they do it without a global social-welfare ordering, by *local rule-craft*.
The lesson Arrow + Ostrom jointly teach is: *you cannot get a universal aggregation rule
(Arrow), but you can get workable local ones (Ostrom).* FDK takes the first half as
permission to do neither.

### 4.3 Sen's Paretian-liberal paradox

Sen (1970): there is no social decision function that is simultaneously Pareto-efficient
and grants each individual a *minimal liberal right* (a decisive say over at least one
personal pair of alternatives) over unrestricted domain. This is *directly* a theorem
about FDK, because FDK **is** a minimal-liberty machine: it makes each owner decisive over
their own boundary. Sen proves that a society of such decisive individual rights can be
forced into Pareto-*inferior* outcomes. **FDK is the impaled horn of Sen's paradox**: it
chooses minimal liberty absolutely and therefore must accept Pareto-dominated outcomes —
which, in the commons, is precisely the tragedy (everyone individually exercising their
liberty to withdraw, ending Pareto-inferior to a coordinated cap they cannot
FDK-legitimately impose). Sen's own resolution — that individuals may *voluntarily
acknowledge* that their rights ought to defer in some pairs — is an Ostromian
collective-choice arrangement (principle 3), which FDK cannot represent. So Sen does not
let FDK off; Sen *names the exact welfare loss* FDK incurs and points at the Ostromian
exit FDK cannot take.

### 4.4 The anticommons (Heller)

Heller's "Tragedy of the Anticommons" (1998): when **too many** owners each hold a right
to *exclude* (and none holds an effective use-right), the resource is **underused** —
Moscow storefronts empty while kiosks crowd the sidewalk; biomedical patent thickets block
research; fragmented land titles block assembly. This is the *mirror* failure of FDK, and
arguably the more damning one, because FDK's gate **maximizes exclusion rights** — every
owner is absolutely decisive, every boundary crossing needs consent. **FDK is an
anticommons engine.** Any project requiring assembly of many consents (a watershed
restoration, a transmission line across many parcels, a vaccine pool with many patent
holders, a building requiring every neighbor's sign-off) is, under FDK, hostage to any
single hold-out — the `UNANIMOUS_GROUP` reduction *is* the anticommons. FDK's proud
hold-out veto (the lighthouse hold-out, §1.2) is celebrated as principled when it is, by
Heller's analysis, a recipe for systematic underuse and gridlock. Ostrom and Heller
together bracket FDK: it overshoots into tragedy on the commons (no exclusion where some is
needed) *and* into anticommons gridlock on assembly (all exclusion where some must yield).

### 4.5 Coase

Coase (1960, *The Problem of Social Cost*): with well-defined rights and **zero
transaction costs**, parties bargain to an efficient outcome regardless of the initial
rights allocation. FDK is *Coasean in spirit* — define the boundary, let owners
consent/trade. But Coase's *actual* argument cuts against FDK twice. **First**, Coase
(1959, spectrum; 1974, lighthouse) showed the relevant question is the *comparative
institutional* one — markets, firms, and governments are alternative coordinating
institutions, and which is efficient depends on transaction costs. FDK admits only one
institution (bilateral owner-consent) and so cannot ask Coase's own question. **Second**,
the entire force of post-Coasean economics (Williamson, and Ostrom herself — her Nobel was
shared with Williamson on *economic governance*) is that **transaction costs are not
zero**, and that *commons and hierarchies exist precisely because* bilateral
consent-bargaining is too costly for many goods. The commons is an *institutional response
to transaction costs* that the pure-consent model cannot generate. So Coase, read fully,
is not FDK's ally but the origin of the comparative-institutions tradition (Ostrom,
Williamson) that explains why the single-owner-consent world FDK assumes is the exception,
not the rule.

---

## 5. Open sub-problems and what counts as progress

### 5.1 The criterion for progress

> **A theory of collective ownership counts as progress only if it threads between two
> failures that are both easy and both wrong:**
>
> - **"No one owns it, so anything goes"** — the vacuous-ALLOW tragedy FDK currently
>   commits. (Hardin's freedom-in-a-commons-brings-ruin.)
> - **"The state owns it, so confiscation is fine"** — the Leviathan/`MAJORITY_COLLECTIVE`
>   horn, where a majority or sovereign binds dissenters and FDK rightly smells
>   confiscation.
>
> Progress is a representation of the **third thing** Ostrom documented empirically: a
> *self-governing commons* that is legitimate without being either a single private title
> or a coercive state seizure. The test of any proposal is: **can it represent Törbel,
> Valencia, Alanya, and Maine lobster as legitimate — and still DENY the genocide, the
> slavery, and the majority-vote confiscation that FDK currently denies?** Anything that
> legitimizes the commons by also legitimizing the tax-by-bare-majority has failed; so has
> anything that protects against confiscation by also condemning the Valencia water court.

### 5.2 Concrete open sub-problems

1. **The bundle-of-rights primitive.** Replace `human_owns: Entity → set[Resource]` with a
   typed relation over *(right ∈ {access, withdrawal, management, exclusion, alienation},
   subject(s), resource)* allowing overlap and partial holdings (Schlager–Ostrom 1992).
   *Open:* does this stay decidable and freeze-able, or does it reintroduce the aggregation
   problem inside the ownership relation?

2. **Self-legislating boundaries (the Ostrom-principle-3 problem).** A commons' rules are
   *made by the appropriators* and bind them *by their own ongoing membership*, not by
   per-act consent. Can FDK represent "consent to the constitution" as a revocable
   membership (exit-right preserved) distinct from "consent to each act" — *without*
   collapsing into majority-confiscation when a member dissents but does not exit? The
   exit-right (`removes_exit_right` in the model) may be the hinge: a commons rule is
   legitimate iff every member retains a real exit. **This is the most promising thread**
   and connects to the existing `EXIT_RIGHT` boundary kind.

3. **The free-rider / public-good provision problem.** Is there *any* FDK-legitimate
   provision of a non-excludable public good with a rational free-rider, short of unanimous
   payment? Candidates to investigate: assurance contracts (Schelling) / dominant-assurance
   contracts (Tabarrok), club goods (Buchanan), and Lindahl pricing — all attempts to make
   public-good funding *individually voluntary*. Do any reduce to FDK's consent primitive?

4. **The anticommons / hold-out problem (Heller).** The dual of (3): when assembly needs
   many consents, what disciplines the hold-out *without* confiscation? Liability rules vs
   property rules (Calabresi–Melamed 1972), eminent domain with compensation — can a
   *compensated, exit-preserving* taking ever be FDK-legitimate, or is that the camel's
   nose of the tax?

5. **Monitoring and graduated sanctions (Ostrom principles 4–5).** FDK's binary gate and
   attested-boolean consent (`LIMITATIONS.md` §3) cannot model monitoring or graduation.
   Is legitimacy genuinely binary, or does a real theory of commons require a *graduated*
   legitimacy — and if so, does that destroy FDK's claim to be a crisp predicate?

6. **The enclosure asymmetry.** FDK can represent the post-enclosure freehold but not the
   pre-enclosure commons, so it cannot even *describe* the harm of enclosure (§3.3, case
   21). A theory that cannot represent what was lost cannot adjudicate dispossession. Open:
   can the bundle primitive (1) represent the commoner's lost use-right well enough to make
   enclosure visible as a *taking*?

7. **The data/training-corpus commons (case 25).** Closest to FDK's own AI mission. Is the
   collective informational value of a population's data a commons (Ostromian) or a public
   good (Olsonian), and which design — data trust, data cooperative, collective bargaining —
   reduces to a representable holder? FDK currently has *one subject per resource* and is
   structurally blind to the collective surplus that is the entire value of training data.

### 5.3 The honest bottom line

FDK's `AGGREGATION.md` ends "three of six forms reduce; three do not, and saying so plainly
is the contribution." The hostile correction: **the three that "do not reduce" are not
three exotic edge forms — they are the commons, the public good, and the unowned-collective,
i.e. most of the goods on which collective human life depends.** And FDK does not merely
fail to represent them; on the depletable commons its native verdict is a *false ALLOW* that
reproduces a prediction (the tragedy of the commons) which the field's Nobel-winning
empirical program (Ostrom) has refuted across thousands of cases. The contribution of *this*
document is to refuse the word "scope limit" for that, and to name it: **on collective
ownership, FDK is not silent — it is wrong, in the specific direction Elinor Ostrom proved
wrong, and FDK has never engaged her.**

---

*Hostile research notes. No verdict, no kernel change, no reduction claimed. The point is
to locate the error, not to repair it.*

*Theory under examination: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust
(CC BY 4.0). Engineering: Ali Pourrahim. This critique is independent of both.*

*Key sources engaged: Ostrom, Governing the Commons (1990) and the Workshop CPR corpus;
Schlager & Ostrom, "Property-Rights Regimes and Natural Resources" (1992); Hardin, "The
Tragedy of the Commons" (1968); Arrow, Social Choice and Individual Values (1951); Sen,
"The Impossibility of a Paretian Liberal" (1970); Heller, "The Tragedy of the Anticommons"
(1998); Coase, "The Problem of Social Cost" (1960); Olson, The Logic of Collective Action
(1965); Acheson, The Lobster Gangs of Maine (1988); Calabresi & Melamed (1972).*
