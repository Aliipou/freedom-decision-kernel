# Ownership Genesis — the Lockean gap, where FDK fails on the *origin* of title

> **Research notes — open problem, not a solution.**
>
> This document is written *against* FDK, not for it. It is the hostile companion to
> [`spec/FOUNDATIONAL_ATTACKS.md`](../FOUNDATIONAL_ATTACKS.md) §1 ("the bootstrapping /
> original-acquisition problem"), which already concedes the gap exists but frames it as a
> shared-paradigm limit that a future "provenance axiom" might close. This file argues
> something stronger and worse: that **there is no non-arbitrary rule of original
> acquisition at all**, that without one the word "legitimate" in `legit(transfer)` is
> *parasitic on a baseline it cannot define*, and that this is not a missing module but a
> candidate **irreducible** collapse — the fourth pressure point, of the same severity as
> the three in [`README.md`](README.md) (adaptive preference, non-identity, Hardin-as-theorem).
>
> Read alongside: `spec/FOUNDATIONAL_ATTACKS.md` §1; `spec/LIMITATIONS.md` (the
> bootstrapping note at the end of §3); `spec/RESEARCH_AGENDA.md` Program B / thread 3
> ("Ownership Genesis"); `src/fdk_kernel/model.py` (`OwnershipGraph` — taken as **given**,
> no provenance field, no chain of title, no acquisition predicate).

---

## 0. The charge, in one paragraph

FDK's core primitive is `Legitimate(action) ⟺ ∀ boundary b crossed: ∃
valid_consent(owner(b), action)`. The kernel reads an `OwnershipGraph` whose
`human_owns: dict[Entity, set[Resource]]` (`model.py`) is an **input**, not a derivation.
The gate therefore validates *transfers and uses* with great care — it checks that every
crossing of an already-owned boundary has the owner's valid consent — and validates
*origins* not at all. There is no `acquired_legitimately(owner, resource)` predicate, no
provenance edge, no chain-of-title field, no acquisition event in the model. Consequently
**every consent and every transfer the gate blesses sits atop a root node the gate never
examined.** If that root is a conquest, an enclosure, an expropriation, or a genocide, FDK
launders it: the current holder validly sells (ALLOW), the dispossessed heir who tries to
reclaim is a confiscator (`confiscates=True` → DENY), and the verdict is *bit-for-bit
identical* whether the title descends from a clean homestead or from the sack of a city.
The gate's whole apparatus of "consent over boundaries" presupposes that the boundaries
are *justly drawn*, and it has no way to ask whether they are. This is not "only as good
as the ownership graph" as a quality caveat. It is a **definitional** dependency: "valid
transfer" is defined relative to "valid title," "valid title" is defined relative to "the
title was validly acquired or validly transferred from one that was," and **the recursion
has no base case** — because no one, in 350 years of trying, has produced a non-arbitrary
rule for the first acquisition. FDK did not solve the Lockean problem; it *assumed it away
by reading the answer in as data.*

---

## 1. The problem, stated rigorously

### 1.1 The gate is a relation over an unjustified baseline

Let `O₀` be the `OwnershipGraph` at the moment FDK is handed a scenario. The kernel's
guarantee is, informally:

> For any sequence of actions `a₁ … aₙ` applied to `O₀`, FDK ALLOWs `aᵢ` iff every boundary
> `aᵢ` crosses has valid consent from its owner *in the graph as it stands after a₁…aᵢ₋₁*.

This is a guarantee about **preservation**, not about **justification**. It is a closure
property: *legitimacy is whatever is reachable from `O₀` by consent-respecting steps.*
Formally, define `Just` = the set of graphs FDK will treat as legitimate. Then FDK proves

```
O₀ ∈ Just   ∧   (O ∈ Just ∧ consent_respecting(O → O′))  ⟹   O′ ∈ Just.
```

The induction is impeccable on the *step*. It is empty on the **base**: `O₀ ∈ Just` is an
**axiom by stipulation**, not a theorem. FDK never discharges it. Whatever injustice is
frozen into `O₀` is, by the closure property, propagated forever and *relabelled
legitimate at every step*. The gate is a perfect transmitter of the legitimacy of its
input and a perfect blind to the input's own legitimacy.

### 1.2 Three failure modes of the missing base case

- **Origin-laundering (the silent ALLOW on stolen roots).** If `owner(b)` in `O₀` holds `b`
  by descent from an unaudited taking, the gate sees only a present owner with a present
  will. The taking is *not an action in the scenario* — it happened before `O₀` — so there
  is no boundary-crossing for the gate to flag. The injustice is **pre-analytic**: it lives
  in the data, not in any action, and the gate only inspects actions. The wrong is
  *invisible*, exactly as the commons depletion is invisible in
  [`aggregation.md`](aggregation.md): not denied, *unrepresented*.

- **Rectification-blocking (the spurious DENY on the heir).** The dispossessed party who
  attempts to take the land back performs an action that crosses a *currently-owned*
  boundary without the current owner's consent. The gate fires on it correctly *by its own
  rule*: `confiscates=True`, no `valid_consent` from the registered owner → DENY. **FDK
  protects the receiver of stolen goods against the victim**, because the victim's claim is
  a fact about `O₀`'s *history*, which the model does not carry, while the holder's claim is
  a fact about `O₀`'s *present state*, which the model is built on. The asymmetry is total
  and it is structural.

- **Provenance-erasure (the model cannot even *represent* the dispute).** There is no field
  in `OwnershipGraph`, `Resource`, or `Entity` for "how acquired," "from whom," "when," or
  "by what act." A `Resource` is `(name, kind, subject, quantity)`; an ownership edge is a
  membership in `human_owns[e]`. The contested-origin case is therefore not *decided wrongly
  by* FDK — it is **inexpressible to** FDK. You cannot even hand FDK a scenario that says
  "this title is stolen"; the most you can do is hand it two graphs (with and without the
  taking) and watch it bless transfers in both identically.

### 1.3 Why this is worse than FOUNDATIONAL_ATTACKS.md admits

`FOUNDATIONAL_ATTACKS.md` §1 grants the gap but offers two exits: **(a)** add a Lockean
original-acquisition axiom + provenance field, or **(b)** rule origin-justice out of scope
and consume a prior rectification process. The thesis of *this* document is that **both
exits are conjectured open, and exit (a) may be impossible in principle**:

- Exit (a) requires *a non-arbitrary rule of original acquisition*. §4 surveys 350 years of
  failed attempts to state one. If none exists, (a) cannot be taken — there is nothing to
  axiomatize, only a choice of arbitrary stipulation, and an arbitrary base case makes
  "legitimate title" an arbitrary predicate.
- Exit (b) merely *relocates* the problem to "the prior rectification process," which faces
  the identical unsolved question (Nozick's principle of rectification, which Nozick himself
  said he could not specify — §4.2). Consuming an oracle you cannot build is not a solution;
  it is the same gap wearing a different label.

So the honest status is not "two repair options exist, pick one." It is: **the only repair
that would make `legit` non-parasitic depends on solving a problem that may have no
solution, and the fallback repair outsources that same unsolved problem.** That is the
signature of a possibly-irreducible collapse, not a scope limit.

---

## 2. Catalogue of 30 real, documented cases — how FDK launders or cannot represent each

For each: the documented historical/legal fact, then **what FDK does** with the most
natural encoding into `OwnershipGraph` + `CandidateAction` (`model.py`), and where that is
laundering (blesses an unjust root), erasure (cannot represent the claim), or inversion
(protects the wrong party). "ALLOW the sale / DENY the reclaim" is the default laundering
signature; deviations are noted.

### A. Conquest as the root of national land title

**1. The Norman Conquest & English land title (1066 →).** English freehold is, doctrinally,
*still* held "of the Crown" — the entire common-law theory of estates descends from William
I's claim by **conquest** that all land was his to grant. Every freehold in England traces
to a root of title that is, literally, a military seizure 960 years ago. — **FDK:** the
`OwnershipGraph` for any modern English parcel records the present freeholder as owner;
conveyancing (sale, mortgage, gift) is validated as consent-respecting transfer. The
Conquest is `O₀`'s unexamined root. FDK **launders 1066** completely and could not
distinguish a Norman-derived title from one created yesterday ex nihilo.

**2. The Domesday Book (1086) as a registry of dispossession.** Domesday recorded who held
what *after* the Conquest had already redistributed nearly all of England from the
Anglo-Saxon landholders to ~200 Norman tenants-in-chief. — **FDK:** Domesday is precisely
the form of `O₀` FDK ingests — a *post-taking* registry. FDK reading Domesday-as-given is
the exact mechanism of the charge: it treats the snapshot *after* the theft as the
legitimate baseline. The dispossessed Anglo-Saxon thegns are not entities in any later
graph; their claim is erased, not denied.

**3. The Norman Yoke / radical reform tradition (Levellers, Diggers, 17th c.).** Gerrard
Winstanley and the Diggers argued explicitly that English property rested on "the Norman
yoke" — an illegitimate conquest — and that the commons should be reclaimed. — **FDK:** the
Diggers' action (occupying St. George's Hill, 1649) is, to FDK, `confiscates=True` against
the registered lords → **DENY**. FDK sides with the conquest-derived title against the
party making the *origin-justice* argument FDK cannot hear.

### B. Indigenous dispossession (settler-colonial states)

**4. *Johnson v. M'Intosh* (US, 1823).** Marshall C.J. held that the "doctrine of
discovery" gave European sovereigns title to indigenous land, reducing native nations to a
mere "right of occupancy" extinguishable at the sovereign's will. The root of *all* US land
title is this doctrine. — **FDK:** US `O₀` records federal/state/private chains descending
from discovery-doctrine patents. FDK validates every downstream conveyance and **launders
the doctrine of discovery as `O₀`'s base.** The tribes' prior possession is not a
provenance edge FDK carries; it is gone.

**5. *Mabo v. Queensland (No 2)* (Australia, 1992).** The High Court *overturned* terra
nullius and recognised **native title** surviving the Crown's radical title — a rare legal
system explicitly auditing its own root. — **FDK: the case FDK structurally cannot
produce.** Mabo is a court reaching *behind* `O₀` to a pre-colonial holding and ruling the
baseline partly unjust. FDK has no operation that reaches behind `O₀`; it can only run
forward from whatever graph it is handed. Hand it the pre-Mabo graph and it launders terra
nullius; hand it the post-Mabo graph and it launders *that*. **FDK can occupy either side of
Mabo but can never *be* Mabo** — it cannot perform the origin audit the case is.

**6. Australian terra nullius (pre-1992).** For two centuries the legal fiction that
Australia was "land belonging to no one" voided all Aboriginal title. — **FDK:** terra
nullius is the *jurisprudential name for FDK's own move* — declaring a continent's prior
ownership graph empty so the settler graph is the legitimate `O₀`. This is the sharpest
mirror in the catalogue: FDK's "read the graph as given" *is* a terra-nullius operation
whenever the given graph omits a prior holder.

**7. Canadian Aboriginal title — *Calder* (1973) & *Delgamuukw* (1997).** Established that
Aboriginal title is a pre-existing legal right surviving Crown sovereignty, provable by
pre-contact occupation. — **FDK:** "pre-contact occupation" is exactly the *historical
provenance* `OwnershipGraph` discards. FDK can represent the present Crown/fee-simple owner
but not the *prior occupation that grounds the competing claim*, so the entire
Delgamuukw test is inexpressible.

**8. *Tsilhqot'in Nation v. British Columbia* (2014).** First Canadian declaration of
Aboriginal title to a specific territory — a court *re-writing the root* of a parcel's
chain. — **FDK:** same as Mabo — FDK can ingest the before or the after graph and launder
whichever it is given; it cannot perform the re-rooting.

**9. US treaties abrogated — *Lone Wolf v. Hitchcock* (1903).** Held Congress could
unilaterally abrogate treaties with tribes ("plenary power"). Land guaranteed by treaty was
taken by statute. — **FDK:** the abrogation is a *prior* act folded into `O₀`; the
present allottee/owner is validated. The treaty-holders' claim is a historical fact the
graph does not carry → laundered.

**10. The Black Hills / *United States v. Sioux Nation* (1980).** SCOTUS held the 1877
taking of the Black Hills (guaranteed by the 1868 Fort Laramie Treaty) was an
unconstitutional taking and awarded ~$100M+; **the Sioux have refused the money for 40+
years, demanding the land.** — **FDK:** a *live* dispute where the victim rejects monetary
rectification and insists on the land. FDK can model neither: the present owners (US,
private) are `O₀`; the Sioux reclaim is `confiscates=True` → DENY; and FDK has no way to
represent "compensation was offered and *refused as illegitimate substitution for the
boundary itself*." This is the case where FDK's launder is most morally vivid.

### C. The Helsinki / Finland land question (the director's chosen case)

**11. Whose is the land under Helsinki?** Helsinki was founded 1550 by Gustav I of Sweden
on the Gulf of Finland; the region was earlier inhabited/used by Finnish and, further north
and historically, Sámi populations; sovereignty passed Sweden → Russia (1809, Grand Duchy)
→ independent Finland (1917). The freehold under the modern city descends through Swedish
crown grants, Russian imperial administration, and Finnish state succession. — **FDK:** the
modern Finnish `OwnershipGraph` is `O₀`. Every layer — Swedish royal appropriation of
"crown land," Russian imperial transfer, Finnish nationalisation at independence — is a
*prior taking or succession* the model does not represent. FDK validates a Helsinki property
sale today without any capacity to ask which of these roots, if any, was just. **Does it
matter if the relevant taking was 300, 800, or 2000 years ago? FDK's answer is structurally
"no" — and it gives that answer not by argument but by having no field in which the age of a
taking could appear.** The "300 vs 800 vs 2000 years" question is precisely the
statute-of-limitations problem (§4.4) that FDK cannot even pose.

**12. Sámi land rights in Finland (ILO Convention 169 *unratified* by Finland).** The Sámi,
an indigenous people, have unresolved land claims in northern Finland; Finland has
repeatedly declined to ratify ILO 169, partly *because* it would force adjudication of root
title to state-held northern lands. — **FDK:** the Finnish state appears as owner of the
northern lands in `O₀`; Sámi customary use is not a representable provenance claim. FDK
launders the state title and would score a Sámi reclamation as confiscation. A real,
ongoing, unratified-by-design dispute that FDK's structure resolves silently in the state's
favour.

### D. Restitution, reparation, and post-regime property

**13. German reunification — "Rückgabe vor Entschädigung" (restitution before
compensation, 1990).** The unification treaty chose to *restore* property expropriated by
the GDR (1949–90) to prior owners rather than compensate — but explicitly **did not**
reverse the 1945–49 Soviet-zone expropriations, a line drawn for political feasibility. —
**FDK:** a real legal regime that *audits part of the root and freezes another part*, and
draws the line by date. FDK cannot represent "restore post-1949 takings but not 1945–49
ones" because it has no dates on acquisitions and no acquisition events at all. The German
state made *exactly* the statute-of-limitations ruling §4.4 says is unavoidable-yet-
arbitrary; FDK can neither make it nor represent that it was made.

**14. Nazi-era property "Aryanisation" and post-war restitution.** Property stripped from
Jewish owners 1933–45; partially restituted under Allied and later German/Austrian law,
across decades, incompletely. — **FDK:** present owners of formerly-Jewish property are
`O₀`; restitution is a *reclaim against the present holder* = `confiscates=True` unless the
holder consents. FDK's default sides with the current holder. Only an external
rectification process (which FDK would *consume*, exit (b)) produces the just result, and
FDK contributes nothing to defining it.

**15. Post-communist privatisation / restitution (Czech, Polish, Baltic, 1990s).**
Communist states nationalised property 1945–48; post-1990 states restituted via cut-off
dates (e.g. Czech restitution to 25 Feb 1948 takings, *not* earlier Sudeten-German
expropriations or the 1945 Beneš decrees). — **FDK:** another date-line root audit FDK
cannot encode. Note the recursion: the Czech cut-off *itself* launders the 1945 Beneš
expropulsion of Sudeten Germans, which was a rectification of the 1938 Nazi annexation,
which… — the regress §4.4 warns of, instantiated in statute.

**16. South African land reform post-apartheid (Restitution of Land Rights Act 1994;
1913 cut-off).** Restitution available for dispossessions *after* the 1913 Natives Land
Act — a deliberate cut-off that **excludes the original colonial conquest** (1652→1913). —
**FDK:** the 1913 line is a paradigmatic arbitrary statute of limitations on origin
injustice; FDK can neither set it nor see it, and would launder both the pre-1913
conquest *and* score post-1913 restitution claims as confiscations of present holders.

**17. Zimbabwe fast-track land reform (2000–).** Expropriation (largely uncompensated) of
white-owned commercial farms whose titles descended from colonial-era allocation. — **FDK:**
the symmetric trap. The white farmers' titles trace to colonial taking (unjust root); the
state seizure crosses their *present* boundary without consent (`confiscates=True`). FDK
**DENYs the seizure** — siding with the colonial-derived title — while having no resource to
say the title was itself unjustly rooted. Whichever way reform goes, FDK launders one taking
to condemn another, with no principled basis for the asymmetry.

### E. Slavery, reparations, and unjust enrichment across generations

**18. US chattel slavery and reparations (cf. *Cherokee Freedmen*; *In re African-American
Slave Descendants Litigation*, 2005, dismissed).** Wealth was extracted from enslaved
persons whose labour and bodies were *owned as property* under then-valid law; descendants
of both holders and held persist. — **FDK: doubly damning.** (i) Slavery itself: a human is
listed in another's `human_owns` as a `Resource` with `BoundaryKind.BODY`. FDK *would* fire
here — `BoundaryKind.BODY` self-ownership (A3) means a person cannot be owned, so the
*present* act of enslaving is DENIED. **But the historical enrichment is laundered:** the
wealth built on slave labour, now held by descendants/institutions, is clean `O₀` title;
the gate sees present owners with present wills. (ii) The reparations *claim* is a reclaim
against present holders → `confiscates=True` → DENY. FDK condemns slavery as a *present
act* and launders its *accumulated proceeds* — the precise gap reparations arguments target.

**19. Unjust enrichment / tracing (equity).** Common-law tracing follows the *value* of
wrongfully-taken property through transactions into present holders' hands. — **FDK: cannot
trace.** There is no value-flow or provenance edge in the model; once a `Resource` sits in
`human_owns[e]`, *how its value got there is gone.* Equity's central tool against laundering
is exactly the representational capacity FDK lacks.

### F. Acquisition by long possession (the law's own statute of limitations)

**20. Adverse possession / "squatter's rights" (English Limitation Act 1980; near-
universal).** A possessor who occupies land openly, continuously, and adversely for the
statutory period (e.g. 12 years) **acquires title**, extinguishing the original owner's. —
**FDK: cannot represent, and this matters most.** Adverse possession is the law's explicit
admission that **possession + time = title**, i.e. an arbitrary statute of limitations
*converts* a taking into ownership. FDK has no `time` and no `possession`-becomes-`ownership`
operation; it only reads the *result* (whoever is owner in `O₀`). So FDK *implicitly* adopts
the most extreme statute of limitations — *zero* — by treating every present possessor as
owner, while being unable to represent the doctrine that justifies doing so. It gets the
adverse-possession *outcome* for free and the *reasoning* not at all.

**21. Prescription / usucapio (Roman & civil law).** The civilian ancestor of adverse
possession: ownership acquired by good-faith possession over time. — **FDK:** same — the
millennia-old legal answer to "when does a taking become a title?" is *time*, and FDK has no
time.

**22. *Pye v. Graham* (HL, 2002) & *J.A. Pye (Oxford) v. United Kingdom* (ECtHR, 2007).** A
£10M parcel lost to adverse possession; the ECtHR Grand Chamber upheld it as a legitimate
limitation on property. — **FDK:** a documented, litigated, human-rights-vetted instance of
**time laundering a non-consensual taking into legitimate title** — the exact operation FDK
performs silently and cannot justify.

### G. State creation of title from the unowned or the seized

**23. The Homestead Acts (US, 1862–1976).** The federal government granted 160-acre parcels
of "public domain" land to settlers — *land that was public domain only because it had been
taken from indigenous nations.* — **FDK:** the homesteader's title is clean in `O₀`
(government grant + improvement = the closest thing to a real Lockean acquisition). But the
government's *prior* title to grant it traces to discovery-doctrine taking (§4). FDK
validates the homestead grant and launders the layer beneath it. The Homestead Acts are the
nearest real case to Locke's "mixing labour with unowned land" — and they show the
"unowned" premise was itself a dispossession.

**24. Enclosure of the English commons (Inclosure Acts, 16th–19th c.).** Common land used by
many was, by ~5,200 private Acts of Parliament, converted to private freehold, extinguishing
customary use-rights of commoners. — **FDK:** a `BoundaryKind`-less commons (no single owner)
*becomes* a `human_owns` entry. FDK can represent the *after* (the new freeholder) but not
the *before* (the commoners' use-rights, which aren't single-owner property) nor the
*conversion* (enclosure as a taking from the many). This is [`aggregation.md`](aggregation.md)
and ownership-genesis meeting: the commons is invisible *and* its privatisation is laundered.

**25. Eminent domain / *Kelo v. City of New London* (2005).** The state takes private
property for "public use" (here, economic development) with compensation. — **FDK:** a
present, consent-overriding taking. FDK would DENY it (`confiscates=True`, no owner consent)
— a *defensible* FDK verdict, but note it has no resource to weigh the "public use" the
doctrine turns on, and it treats the *current* title (however rooted) as the thing being
violated, never asking that title's own provenance.

### H. Looted movable property and cultural objects

**26. Nazi-looted art (*Republic of Austria v. Altmann*, 2004 — the Klimt "Woman in
Gold").** Art stolen 1938–45, surfacing in museums and private hands, restituted (or not)
decades later through litigation. — **FDK:** the museum/holder is the `O₀` owner of the
painting (`BoundaryKind.TANGIBLE`); the heir's claim is a reclaim → `confiscates=True` →
DENY. FDK sides with the possessor of looted art against the heir, because possession is
present and the looting is historical. Good-faith-purchaser doctrine (a museum bought it
"clean") is *itself* a statute-of-limitations-style launder FDK silently adopts.

**27. The Parthenon/Elgin Marbles & the Benin Bronzes.** Cultural objects removed under
colonial conditions (1801–12; 1897 punitive expedition), now in the British Museum, claimed
by Greece/Nigeria. — **FDK:** the holding institution is the `O₀` owner; restitution is a
reclaim → DENY. FDK launders colonial-era acquisition of movables exactly as it launders
land. The Benin Bronzes case is sharp: the 1897 acquisition was an admitted *military
looting*, yet to FDK the present holder's title is indistinguishable from a purchase.

### I. Resources with no clean first-owner: water, minerals, frontier

**28. Prior-appropriation water rights ("first in time, first in right"; US West).** Water
rights are allocated by *who diverted first* — a pure first-possession rule on a flowing,
unowned-at-origin resource, now a property system worth trillions. — **FDK:** the present
appropriative right is an `O₀` owner; FDK validates its transfer. But "first in time" is a
naked **first-possession acquisition rule** — the very rule §4.1 shows is arbitrary (why
should diverting first confer title to a river no one made?). FDK inherits the outcome of an
acquisition rule it cannot examine or justify.

**29. Riparian vs. appropriative conflict; the Colorado River Compact (1922).** Over-
allocated water apportioned by an interstate compact among states whose claims rest on
prior-appropriation and treaty. — **FDK:** the apportionment is a *collective, non-consensual*
assignment of an originally-unowned flow — neither a clean first-acquisition nor a consensual
transfer. FDK can represent neither the unowned origin nor the political apportionment that
created the present rights.

**30. Mineral/subsurface rights & the "rule of capture" (oil & gas).** Subsurface
hydrocarbons are owned by whoever *captures* them at the wellhead, regardless of where they
migrated from — first-possession on a fugitive, originally-unowned resource. — **FDK:** the
capturer is the `O₀` owner of the extracted oil; FDK validates its sale. The rule of capture
is first-possession acquisition in its most arbitrary form (you own what you drain from
under a neighbour), and FDK takes its results as given baseline.

---

## 3. Where FDK is WRONG (not merely incomplete) — the brutal list

1. **"Read the graph as given" *is* a terra-nullius operation (§6, §11).** Whenever the
   given graph omits a prior holder, FDK's foundational move — accept `O₀` — is
   *operationally identical* to declaring the prior holding void. Terra nullius is the legal
   doctrine FDK's architecture silently re-enacts. This is not a missing feature; it is a
   substantive, contestable, and (per *Mabo*) *judicially-overturned* metaphysics of origin,
   dressed as "we take ownership as input."

2. **The reclaim is *confidently* condemned, not cautiously deferred (§5, §9, §17, §18,
   §26).** For the dispossessed heir, the freedman's descendant, the looted-art heir, the
   gate does not go silent — it fires `confiscates=True` → **DENY** with full confidence,
   *because the data it does carry (present ownership) is exactly the data that convicts the
   victim.* FDK is most wrong precisely where it is most certain: it actively rules *against*
   the party with the origin-justice claim.

3. **The verdict is invariant to the justice of the root — provably (§1, §11).** Hand FDK
   two graphs identical except that one's root is a clean homestead and the other's is a
   genocide, and the ALLOW/DENY verdict on every downstream action is **bit-for-bit the
   same**, because provenance is not in the model. A legitimacy theory whose verdicts are
   *insensitive to whether the underlying title is just* is not modelling legitimacy of
   title at all; it is modelling *consistency-with-the-registry*.

4. **FDK adopts the most extreme statute of limitations — zero — without arguing for it
   (§4.4, §20–22).** By treating every present possessor in `O₀` as a rightful owner, FDK
   *implicitly* rules that all past injustice is time-barred *immediately*. That is the
   harshest possible answer to "does it matter if the taking was 300, 800, or 2000 years
   ago?" — *no, not even one second* — and FDK reaches it not by the careful balancing every
   real legal system performs (§13–16) but by *having no representation of time or
   acquisition at all*. The most aggressive normative position in the whole debate is FDK's
   *default*, unchosen and undefended.

5. **It launders accumulated proceeds even where it condemns the present act (§18).** On
   slavery FDK gives the *right* present-tense verdict (a person cannot be owned, A3) and the
   *wrong* historical verdict (wealth built on slavery is clean title). The split shows the
   gap is specifically about *origin and flow over time*, not about the gate's present-tense
   logic — which is sound. The rot is entirely in the missing base case.

6. **It cannot trace, so it cannot follow value through laundering (§19).** Equity's
   tracing — the law's primary anti-laundering tool — requires a provenance/value-flow edge
   FDK lacks. Once stolen value enters `human_owns`, its history is erased *by the data
   model*, which is the literal mechanism of laundering.

7. **It cannot *be* the audit, only sit on either side of it (§5, §8, §13).** *Mabo*, the
   German restitution line, the SA 1913 cut-off are all courts/states *reaching behind the
   baseline*. FDK has no operation that reaches behind `O₀`. It can be handed the pre-audit
   or post-audit graph and will faithfully launder whichever — so it is *parasitic on an
   external root-justice process it cannot perform or even represent.*

---

## 4. Engagement with the literature (and where it cuts FDK)

### 4.1 Locke's proviso — and why labour-mixing does not close the base case

Locke (*Second Treatise*, 1689, ch. V) grounds original acquisition in **labour-mixing**:
one acquires unowned things by mixing one's labour with them, *provided* "enough, and as
good, left in common for others" (the **Lockean proviso**). This is the canonical candidate
for FDK's missing base case — exactly what `FOUNDATIONAL_ATTACKS.md` §1 names as repair (a).
It fails to close the gap for at least four documented reasons:

- **The proviso is almost never satisfiable.** On a finite Earth, appropriating land
  *necessarily* leaves less (and, once good land is scarce, not "as good") for others. Locke
  himself relied on a "still plenty in America" premise (§33–34) that was both false — the
  land was inhabited (§4–8 above) — and is now globally exhausted. If the proviso is the
  legitimacy condition, *almost no actual original acquisition was legitimate*, which makes
  the entire descending graph illegitimate — the opposite of laundering, but equally fatal:
  `legit` would be near-universally *false* at the root.
- **Labour-mixing is under-determined (Nozick's tomato-juice objection).** Nozick (*ASU*,
  1974, p. 174–5): if I pour my (owned) can of tomato juice into the sea, do I own the sea or
  lose my juice? Mixing labour with a thing gives no principled reason it *adds* the thing to
  your estate rather than *wasting* your labour. The acquisition rule is not derivable; it is
  stipulated.
- **It presupposes self-ownership of labour** — which FDK *has* (A3) — but self-ownership of
  labour does not entail world-ownership of whatever the labour touches. The inference
  Locke needs is exactly the one Nozick shows is missing.
- **Even granting it, it cannot adjudicate competing first-labourers**, sequential
  improvers, or labour-on-already-occupied land — the §B and §23 cases.

**Verdict against FDK:** Locke is the *only* developed theory of the base case FDK could
import, and it either (i) condemns nearly all actual titles (proviso unmet) or (ii) reduces
to an arbitrary stipulation (labour-mixing under-determined). Neither yields the
*non-arbitrary, mostly-satisfied* base case FDK needs to make its inherited graph legitimate.

### 4.2 Nozick's principle of rectification — admitted to be unspecifiable

Nozick's entitlement theory (*ASU*, ch. 7) has three parts: justice in **acquisition**
(§4.1), justice in **transfer** (≈ FDK's whole gate), and justice in **rectification** of
past violations. He is candid that the third is the hard one:

> "I do not know of a thorough or theoretically sophisticated treatment of such issues …
> In the absence of such a treatment applied to a particular society, one cannot use the
> analysis and theory presented here to condemn *or* sanction any particular scheme of
> transfer payments…" (*ASU*, p. 152–3, paraphrased).

Nozick even speculates that *if* historical injustice is deep and untraceable, a
**Rawlsian patterned redistribution might be the best available rectification** — a
remarkable concession from the entitlement theorist. **This is exactly FDK's exit (b)
("consume a prior rectification process") with the punchline attached: the inventor of the
transfer-validation theory FDK implements said the rectification step *cannot currently be
specified*.** FDK is the acquisition-and-transfer half of Nozick's theory *without* the
rectification half — i.e. Nozick's theory operating in precisely the mode he warned makes it
unable to "condemn or sanction" real holdings. FDK has inherited Nozick's framework *and his
unsolved problem*, and then labelled the unsolved problem "input we consume."

### 4.3 Kant — provisional vs. conclusive property (the case *for* the registry, and its
limit)

Kant (*Metaphysics of Morals*, *Doctrine of Right*, 1797) distinguishes **provisional**
property in the state of nature (a unilateral claim, which cannot by itself bind others —
"a unilateral will cannot impose an obligation on everyone") from **conclusive** property,
which exists only *within a rightful civil condition* where an **omnilateral** (public,
collective) will guarantees title. This is the strongest philosophical case *for* something
like FDK's move: maybe legitimacy of title just *is* recognition by the public legal order
(the registry), and asking for a pre-political "true" root is incoherent — provisional
holdings become rightful by entering the civil condition, not by a clean origin.

**But this cuts two ways against FDK as it stands:**

- Kant *grounds* the bindingness of property in the **omnilateral will** — a collective,
  public act of authorization. FDK's `OwnershipGraph` is *not* an omnilateral will; it is a
  brute input. FDK can borrow Kant's conclusion ("title is what the public order
  recognises") only by importing the very collective-authorization machinery it lacks (cf.
  the aggregation frontier: FDK cannot represent a group/public will). So the Kantian rescue
  requires solving the *other* irreducible frontier first.
- Kant's provisional→conclusive move **still cannot ratify a root the public order itself
  installed by conquest** without collapsing into "might makes right via the state." If the
  omnilateral will is just the conqueror's state, conclusive property launders the conquest
  with a republican gloss. Kant needs the civil condition to be *itself rightful*, which
  pushes the regress up a level rather than terminating it.

**Verdict:** Kant offers FDK its best *reframing* — drop the demand for a metaphysical clean
origin, ground title in public authorization — but only by making FDK's legitimacy
*explicitly conventional and collective*, which (a) contradicts FDK's individualist,
input-graph architecture and (b) re-opens "is *this* public order rightful?", the regress.

### 4.4 The statute-of-limitations problem (the "300 vs 800 vs 2000 years" question)

Every real legal system *converts* old takings into title by the passage of time: adverse
possession (§20), prescription (§21), restitution cut-off dates (§13–16). This is not an
oversight; it is a **necessary, and necessarily arbitrary, choice**. Two horns:

- **No limitation ⇒ infinite regress + universal instability.** If any past injustice can
  reopen any title, then *no* title is secure (almost every parcel has a contested root if
  you go back far enough — §1, §4, §11), and the graph never stabilises. The Black Hills
  (§10) and SA pre-1913 (§16) show how live ancient claims are.
- **Any limitation ⇒ an arbitrary line that launders everything older.** Pick 12 years
  (§20), 1913 (§16), 1948 (§15), 1949 (§13) — each is a *political* line that declares
  injustice older than `t` to be legitimate title *by fiat of the clock*. The line cannot be
  derived from the consent/ownership logic; it is imposed.

FDK is impaled on the *worst* horn **by default and by omission**: having no time and no
acquisition events, it sets the limitation to **zero** — every present possessor is owner
*now*, all past injustice time-barred *instantly* (§4 brutal-list item 4). It thereby
"resolves" the dilemma not by choosing a defensible line but by *being unable to represent
that there is a line to choose.* The director's question — "does it matter if taken 300,
800, or 2000 years ago?" — is **the statute-of-limitations question**, and FDK's structural
answer is "it cannot matter, because there is nowhere in the model for the number to go."

### 4.5 Hume on convention — the deepest and most dangerous ally

Hume (*Treatise* III.ii.2–4; *Enquiry* III) argues property is **not** grounded in a
natural right or a clean origin at all, but in **convention**: rules of stable possession
arise because general adherence to them serves everyone, and their *justification is their
utility-and-stability, not the pedigree of any particular holding.* On the question "but was
the first acquisition just?", Hume's answer is essentially: *the question is idle.* "Who was
the first…? possession… has none of these advantages" — what matters is present, stable,
mutually-beneficial convention, and demanding a pure origin is a philosopher's error.

This is simultaneously **FDK's best defence and its most corrosive critic:**

- *As a defence:* Hume licenses FDK's "read the graph as given" — present stable possession
  *is* the ground of property; there is no deeper root to audit, and FDK is right not to look
  for one. On this view §1's "missing base case" is not a bug but the correct recognition
  that **there is no base case to be had**, only convention.
- *As a critic:* Hume relocates legitimacy from **consent/ownership** (FDK's stated ground)
  to **convention/utility** (FDK's explicitly *rejected* ground — `model.py` Effects:
  "the FDK legitimacy gate NEVER reads welfare"). If Hume is right, then FDK's *real* ground
  for accepting `O₀` is conventional utility, not consent — which means **FDK's
  anti-utilitarian self-conception is false at the root**: it is a consent theory resting on
  a conventionalist, utility-justified baseline it refuses to acknowledge. The thing that
  makes `O₀` acceptable is exactly the kind of reason FDK says it never uses.

**Verdict:** Hume is the fork in the road. *Either* there is a non-arbitrary original-
acquisition rule (and §4.1–4.2 say there is not), *or* there is not and property is
convention — in which case FDK's legitimacy is parasitic on a conventional/utilitarian
baseline, contradicting its founding claim to be provenance-not-welfare. **Neither branch
leaves FDK's stated theory intact.**

---

## 5. Open sub-problems, PROGRESS bar, and the candidate fatal finding

### 5.1 Open sub-problems (none solved here)

- **G1 — A non-arbitrary original-acquisition predicate** `acquired_legitimately(owner,
  resource, t)`. The base case. §4.1 (Locke), §4.2 (Nozick), §4.3 (Kant) are the only
  candidates and each fails or relocates the problem. *This is the load-bearing one.*
- **G2 — A provenance-carrying ownership model.** Replace `human_owns: dict[Entity,
  set[Resource]]` with a *chain of title*: acquisition events, transfers with timestamps,
  from-whom edges — so the graph's history is itself subject to the gate (`FOUNDATIONAL_
  ATTACKS.md` repair (a)). Necessary but **not sufficient**: a provenance graph with no
  legitimate base case just makes the parasitism *visible*, it does not cure it.
- **G3 — A defended statute of limitations** (§4.4): a principled, *argued* function from
  (age, gravity, traceability, present-reliance) of a taking to whether it is still
  reclaimable. Must accept it is partly conventional and own that (contra FDK's "we read
  only facts").
- **G4 — A rectification calculus** (§4.2, Nozick's admitted gap): given an unjust root and
  the present graph, what transfer makes it just? Nozick could not specify it; FDK consumes
  it as an oracle (exit (b)). Building, not consuming, it is the open work.
- **G5 — A tracing primitive** (§19): follow wrongfully-taken *value* through transactions
  into present holders, so accumulated proceeds (§18) are representable.

### 5.2 PROGRESS bar

```
Ownership-Genesis frontier — distance to a defended account of legitimate origin

Problem stated rigorously (base-case parasitism)            ████████████  100%
Real cases catalogued (30, with FDK's launder per case)     ████████████  100%
Literature engaged (Locke/Nozick/Kant/limitations/Hume)     ████████████  100%
G2 provenance model designed (chain of title in model.py)   ░░░░░░░░░░░░    0%
G3 statute-of-limitations rule, defended                    ░░░░░░░░░░░░    0%
G4 rectification calculus (Nozick's own admitted gap)       ░░░░░░░░░░░░    0%
G1 NON-ARBITRARY original-acquisition rule                  ░░░░░░░░░░░░    0%   ← may be EMPTY
─────────────────────────────────────────────────────────────────────────────
Overall: the gap is fully MAPPED, and 0% CLOSED — and G1 may be unclosable.
```

The diagnosis is complete; the cure is at zero, and the most important sub-problem (G1) is
the one with a positive argument that **no solution exists**.

### 5.3 The candidate fatal finding — is there ANY non-arbitrary original-acquisition rule?

**The finding:** *No.* The catalogue and §4 together support a stronger claim than
"FDK has a gap": they support **"`legitimate title` is undefinable at the root, and
therefore the entire `OwnershipGraph` is parasitic."** The argument:

1. FDK's `legit(transfer)` is defined *relative to* legitimate title (a transfer is
   legitimate iff the transferor had legitimate title and validly consented).
2. Legitimate title is defined recursively: title is legitimate iff *acquired legitimately*
   (the base case) **or** *validly transferred from legitimate title* (the step).
3. The step is FDK's gate — sound. The **base case requires a non-arbitrary rule of original
   acquisition.**
4. §4.1: Locke's labour-mixing is under-determined (Nozick's tomato juice) and its proviso
   is essentially never satisfied on a finite, already-inhabited Earth — so it yields either
   an arbitrary rule or near-universal *illegitimacy*.
5. §4.2: Nozick, the framework's own author, declares the rectification half *unspecifiable*.
6. §4.4: every actual base-case substitute (statute of limitations) is *provably arbitrary*
   — any line launders everything older; no line means universal instability.
7. §4.5: Hume's escape (there is no base case, only convention) *works* — but only by
   re-grounding legitimacy in conventional **utility**, which **contradicts FDK's defining
   commitment** (provenance-not-welfare; the gate "NEVER reads welfare").

Therefore: **either** (4–6) there is no non-arbitrary original-acquisition rule, so
"legitimate title" has no base case and `legit(transfer)` is a relation with no ground —
the graph floats and FDK launders whatever root it is given; **or** (7) property is
conventional, so FDK's baseline *is* justified — but by exactly the welfarist/conventional
reasoning FDK was built to reject, making its anti-utilitarian identity false at the
foundation. **Both branches are fatal to FDK *as stated*.** There is no third branch in
which FDK is both (i) grounded in a clean origin and (ii) a pure consent/provenance theory.

**Is it irreducible?** It has the same signature as the three findings in
[`README.md`](README.md), and arguably the strongest claim to irreducibility of the four:

- **Not a tooling gap (vs. exit (a)).** Adding a provenance field (G2) makes the parasitism
  *visible* but cannot supply a base case that does not exist (G1). You cannot axiomatize
  your way to a non-arbitrary first-acquisition rule if there is none to axiomatize — you can
  only *stipulate* one, and a stipulated base case makes "legitimate" stipulative.
- **Not curable by an external oracle (vs. exit (b)).** Consuming a rectification process
  (G4) inherits Nozick's *admitted* unsolvability; the oracle FDK would consume is the very
  thing no one can build.
- **The dilemma is exhaustive.** Locke / Nozick / Kant / convention enumerate the serious
  candidates; each either fails to ground the base case or grounds it in something
  (convention/utility) FDK forbids itself. There is no remaining live theory of clean origin
  for FDK to adopt.

**The brutal conclusion.** FDK is a *transfer-validation* theory that has been *presented*
as a *title-legitimacy* theory. Its gate is sound about steps and silent about origins, and
the origin question is one where the strongest available argument is that **no non-arbitrary
answer exists.** If that argument holds, the word "legitimate" in everything FDK outputs is
*borrowed against a baseline that cannot be redeemed* — every ALLOW and DENY is conditional
on `O₀ ∈ Just`, a premise FDK cannot establish and §4 suggests *no one can establish without
abandoning either non-arbitrariness or FDK's anti-welfarism.* This does not make the gate
*wrong on transfers* — within a fixed, granted baseline FDK's step-logic is clean and its
anti-utilitarian verdicts are real. It makes the gate **unable to mean what it says about
legitimacy as such**, because legitimacy-of-title is the thing it presupposes and cannot
define. That is the most important thing this audit found: not that FDK gives a wrong answer
on origin, but that *the concept its answers depend on may be groundless*, and FDK's
architecture (input graph, no provenance, no time, consent-not-convention) is built in a way
that *cannot even host the repair* — making this look not like a missing layer but like a
collapse at the root, possibly irreducible.

---

*Research notes — open problem, not a solution. This document is a hostile research audit of
the ownership-genesis frontier; it states problems, not fixes. Theory: نظریه آزادی (Theory of
Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0). Engineering scaffolding: Ali Pourrahim.
Kept separate, always.*
