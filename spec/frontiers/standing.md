# Standing — where FDK is wrong

> **Research notes — open problem, not a solution.**

This is a hostile audit. The job is not to defend FDK's standing layer
(`src/fdk_research/standing.py`, `spec/STANDING.md`) but to find where it is
*wrong* — not merely incomplete, but produces classifications that are absurd,
self-undermining, or that smuggle a substantive moral theory under cover of an
"advisory, status-fact" decision tree. The deepest charge (the non-identity
problem, §6) is that FDK's frame makes a whole class of grave wrongs *literally
inexpressible*, and that this is a property of the primitive, not a tooling gap.

Read alongside: `spec/STANDING.md`, `spec/LIMITATIONS.md` §1,
`src/fdk_kernel/model.py` (`Entity` is `HUMAN | MACHINE`; `Consent` requires
`competent=True`), `src/fdk_research/standing.py` (the classifier under audit).

---

## 1. The problem, stated rigorously

FDK's gate is a legitimacy predicate `legit(action)` whose entire load-bearing
input is `valid_consent(H, A)` for the humans an action `affects`. Consent is a
*speech act by a competent, living, present adult*. Therefore the gate presupposes
its subjects: before it can ask "did H consent?" it must already have settled
**who H is and whether H is the kind of being whose consent (or whose interests)
constrains the action at all.** That prior question is *standing*.

Formally, the consent gate is a partial function whose domain is `RightsHolder`,
and FDK never defines `RightsHolder` — it defines `Entity = HUMAN | MACHINE` and
*assumes* the relevant humans are competent adults (`model.py` `Consent.competent`
defaults `True`; the gate denies when it is `False`). So standing is **the
quantifier FDK forgot to bind.** Three failure modes follow:

- **Under-inclusion (the silent ALLOW).** A being with a genuine claim is not an
  `Entity` the action `affects`. Its interest is *not represented in the gate at
  all*, so removing it changes nothing: the act passes. The wrong is invisible,
  not denied. (Animals as property; future people; ecosystems.)
- **Over-deferral (the spurious DENY).** A being *is* in frame but cannot emit a
  valid `Consent` (`competent=False`). The gate denies for *want of consent* —
  which looks like protection but is actually a refusal to act *for* them
  (an infant cannot be fed, a coma patient cannot be treated).
- **Mis-binding (the laundering surrogate).** A human is appointed to attest
  *on the subject's behalf* (`GUARDIAN_REPRESENTED`). The kernel reads the
  guardian's attested `Consent` as if it were the subject's. Whether the
  guardian's "yes" tracks the subject's interest is **exactly the question the
  gate cannot ask** — it checks consent's *structure*, never its *fidelity to a
  third party's good*.

The honest framing in `spec/STANDING.md` ("advisory only," "honesty over
coverage") is real and to FDK's credit. But honesty about a gap is not the same
as the gap being benign. The charge of this document is that **the standing gap
is not a peripheral edge case; it is where the primitive's choice of `Entity` and
`Consent` quietly decides the hardest questions in moral and legal philosophy by
declining to represent them — and that "declining to represent" is itself a
substantive ruling with victims.**

A defended ontology of standing must answer four sub-questions FDK currently
fuses or skips:

1. **Holder** — what *kind* of thing can hold a claim? (will-bearers only?
   interest-bearers? sentients? systems?)
2. **Onset/offset** — *from when, until when*? (conception? birth? brain death?
   the moment a future person becomes determinate?)
3. **Capacity** — *at what grade*? (full self-authoring consent vs.
   represented vs. protected-but-voiceless)
4. **Representation** — *who speaks*, and what binds the speaker to the held?

FDK answers (1) "human, by fiat of `AgentType`," (3) with a four-cell tree, and
punts (2) and (4) to "a human asserts it." Each of those is contestable; §3–§4
show where each is wrong.

---

## 2. Catalogue of 28 documented cases & doctrines

For each: a one-line statement of the real doctrine, **FDK's classification**
(`FULL_PERSON` / `GUARDIAN_REPRESENTED` / `PROTECTED_NON_CONSENTER` /
`NO_STANDING_IN_V1`), and where that classification is inadequate, absurd, or
question-begging. Classifications are read directly off `assess_standing` in
`standing.py` given the most natural `StandingFacts` for the case.

### A. Infancy, childhood, guardianship

**1. Infant / newborn (general guardianship law).** Every legal system vests an
infant's legal personality at birth but exercises it through parents/guardians;
the infant *holds* rights it cannot *exercise* (the Hohfeldian "claim without
power"). — **FDK: `GUARDIAN_REPRESENTED`** (`is_human, is_competent=False,
has_guardian=True`). *Inadequate:* FDK has the guardian *attest the infant's
`Consent`*, collapsing "holds but cannot exercise" into "someone else's speech
act counts as theirs." The Hohfeldian distinction — the whole point of infant
standing — is erased. The kernel cannot represent a right the holder retains
*against* the guardian.

**2. Gillick competence (UK, *Gillick v West Norfolk*, 1985).** A child below
majority may consent to medical treatment if mature enough to understand it —
competence is *graduated and decision-relative*, not an age switch. — **FDK:
binary.** `is_competent` is one boolean; FDK cannot say "competent to consent to
contraception, not to consent to a major operation." Either `FULL_PERSON`
(absurd for a 13-year-old across the board) or `GUARDIAN_REPRESENTED` (wrong:
Gillick's holding is precisely that the *guardian's* veto fails here). FDK has no
cell for *decision-relative* competence — a real, adjudicated category.

**3. Mature-minor doctrine / emancipated minor (US).** Some minors are treated as
adults for some decisions. — **FDK:** same binary failure as #2; no partial or
domain-scoped competence.

**4. Best-interests of the child (UN CRC Art. 3; *Re B*, family law).** When a
guardian's choice conflicts with the child's welfare, courts override the
guardian *in the child's interest*. — **FDK: cannot represent.** This is the
*mis-binding* failure (§1): FDK reads the guardian's attested `Consent` as
authoritative; it has **no best-interests check that can defeat a guardian who
consents to the child's detriment.** A parent attesting consent to a harmful act
on their child produces a valid `Consent` and the gate passes. This is not an
edge case — child-protection law exists *because* guardians fail.

**5. Parental refusal of life-saving treatment (e.g. Jehovah's-Witness
transfusion cases).** Courts routinely override a parent's *refusal* of consent
to save the child. — **FDK: structurally backwards.** Refusal = no valid
`Consent` = DENY the treatment. FDK protects the parent's veto, which is the
exact outcome the doctrine overturns. The "protection by omission" of
`PROTECTED_NON_CONSENTER` becomes *protection of the wrong party*.

### B. Incapacity, dementia, the unconscious

**6. Advance directive / living will.** A competent adult pre-commits to
decisions for their future incompetent self. — **FDK: cannot represent.** The
directive is consent from a person who *no longer exists in the same competent
form*; FDK's `Consent.revocable=True` requirement (`model.py`) actually
*invalidates* an advance directive, since the incompetent future self cannot
revoke it — so a valid living will fails `is_valid()`. FDK turns a binding legal
instrument into an invalid consent.

**7. Lasting power of attorney / substituted judgment (US *In re Quinlan*, 1976).**
A surrogate decides *as the patient would have* — not by best interests, but by
reconstructing the patient's own will. — **FDK: `GUARDIAN_REPRESENTED`, but with
the wrong semantics.** FDK's guardian attests *their own* `Consent`; substituted
judgment requires attesting *the patient's reconstructed preference*. FDK cannot
distinguish "I, guardian, consent" from "I report what she would have chosen,"
and the difference is the entire jurisprudence of surrogate decision-making.

**8. Persistent vegetative state — *Cruzan v. Director* (US, 1990).** Requires
"clear and convincing evidence" of the patient's own prior wishes before
withdrawing life support. — **FDK: `PROTECTED_NON_CONSENTER` → DENY everything.**
FDK can never authorize *withdrawal* of treatment (an act *on* a non-consenter),
nor *continuation* against prior wishes. The Cruzan evidentiary standard — a
graded epistemics of a vanished will — has no home in a boolean `competent`.

**9. PVS — *Airedale NHS Trust v. Bland* (UK, 1993).** Lawfully withdrew
nutrition from a PVS patient on a *best-interests* basis where continued
treatment conferred no benefit. — **FDK: cannot reach this verdict.** Best
interests of a permanently non-competent, non-surrogate-instructed patient is
*exactly* the doctrine FDK names as "open work, not a best-interests mechanism."
A real court ruled; FDK must defer indefinitely. Indefinite deferral *is* a
decision (the patient stays on the tube), so FDK's "advisory neutrality" is false
neutrality.

**10. Locked-in / anaesthetised / sleeping adult.** Temporarily non-competent
but with a clear prior self. — **FDK: flickers to `PROTECTED_NON_CONSENTER`** the
moment `is_competent=False`, so a surgeon cannot act on an anaesthetised patient
who consented before going under. FDK has no notion of *consent persisting
through* a lapse of competence — it reads competence *at the instant of the act*.

**11. Fluctuating capacity (dementia, bipolar, intoxication).** Capacity comes
and goes; law uses decision- and time-specific capacity tests (UK Mental Capacity
Act 2005). — **FDK:** single boolean, no temporal index. Cannot represent "had
capacity Tuesday, lacks it Thursday."

### C. The fetus and the edges of life

**12. Fetal personhood (anti-abortion constitutional claims; *Dobbs*, 2022,
returning it to states).** Whether a fetus is a rights-holder is *the* contested
standing question of the age. — **FDK: forced into `NO_STANDING_IN_V1`** via
`is_present=False` *or* into `PROTECTED_NON_CONSENTER` if counted as a present
non-competent human — **and the classifier's own inputs decide the abortion
debate by stipulation.** Set `is_human=True, is_present=True` and the fetus is a
protected non-consenter (strongly pro-life output); set `is_present=False` and it
is out of frame (pro-choice output). FDK *claims* to take only "observable status
facts," but "is the fetus a present living human?" is the precise normative
question in dispute. **The decision tree launders a contested moral premise as a
data-entry choice.** This is the sharpest example of §1's "quantifier you forgot
to bind" becoming a covert ruling.

**13. Viability standard (*Roe/Casey*, pre-*Dobbs*).** Standing *graded by
gestational stage*. — **FDK:** no continuous onset; `is_present` is a cliff.
Cannot represent gradualist personhood, which is the dominant real-world
compromise.

**14. The dead / posthumous interests (estates, defamation of the dead,
testamentary wishes).** Many systems protect interests of the deceased (wills,
organ-donation registers, posthumous reputation). — **FDK: `NO_STANDING_IN_V1`**
(`is_living=False`). *Inadequate:* `spec/LIMITATIONS.md` itself notes death is
not in the model, so estates are "permanently consent-required" — i.e. an estate
can *never* be acted on, which is absurd (probate is a daily legal event). FDK
cannot represent a will: a binding instruction from someone now out of frame.

### D. Animals

**15. Anti-cruelty statutes (UK Animal Welfare Act 2006; near-universal).**
Animals are protected *objects of duty* even where they are property. — **FDK:
`NO_STANDING_IN_V1`** (`is_human=False`). *Absurd result, quoted from
`LIMITATIONS.md`:* "cruelty to an owned animal reads as legitimate use" — because
`BoundaryKind.BODY` only bites when `subject` is human (`model.py`). FDK
*actively legitimizes* animal cruelty by the owner, the opposite of every modern
animal-welfare regime. This is not silence; it is a wrong verdict.

**16. *Nonhuman Rights Project v. Breheny* (NY, 2022 — Happy the elephant).**
Sought habeas corpus for an elephant; denied, but two judges dissented that a
cognitively complex animal can be a "person" for habeas. — **FDK:
`NO_STANDING_IN_V1`,** with no capacity to even *represent the dissent's
position*. A live, narrowly-lost legal argument is, to FDK, unsayable.

**17. *Cetacean Community v. Bush* (US 9th Cir., 2004).** Whales/dolphins lack
standing to sue *absent a statute granting it* — standing as a *positive-law
artifact*. — **FDK:** treats standing as ontological (species fact), missing that
real standing is often *conferred*, not discovered. FDK has no mechanism for
*granted* standing (cf. trusts, §F).

**18. Sentience as the criterion (UK Animal Welfare (Sentience) Act 2022;
EU TFEU Art. 13).** Law increasingly keys protection to *sentience*, not species.
— **FDK:** keys everything to `is_human`, the criterion moral philosophy has most
decisively rejected (singer's "speciesism"). FDK's holder-predicate is the one
the literature treats as indefensible.

### E. Nature and ecosystems (rights of nature)

**19. Ecuador Constitution (2008), Art. 71 — rights of *Pachamama*/nature.**
Nature itself holds enforceable rights; *any person* may sue on its behalf. —
**FDK: `NO_STANDING_IN_V1`.** A constitutional rights-holder in a real legal
system is, to FDK, a non-entity. The "any person may represent it" structure is
*exactly* a guardianship FDK could model — but only for humans.

**20. *Te Awa Tupua* / Whanganui River (NZ, 2017).** The river is a legal person
with two human guardians (*Te Pou Tupua*). — **FDK: cannot represent,** yet this
is *structurally identical* to `GUARDIAN_REPRESENTED` — a non-competent holder
with appointed surrogates — and FDK refuses it *solely because `is_human=False`.*
This exposes that FDK's guardianship machinery is gated on species, not on the
holder/representative structure it claims to model. The river case proves the
machinery is more general than FDK allows.

**21. Lake Erie Bill of Rights (Toledo, Ohio, 2019; struck down 2020 as
unconstitutionally vague).** A municipal grant of rights to an ecosystem,
*invalidated*. — **FDK: `NO_STANDING_IN_V1`.** Even the *failure mode* (vagueness)
is informative: FDK's "honesty over coverage" is the same instinct that struck
Lake Erie down — but a struck-down statute at least *named a holder*; FDK cannot.

**22. *Mary Jane Sutherland v. ...* / Atrato River (Colombia, 2016) &
Ganges/Yamuna (India, 2017, later stayed).** More rivers granted/denied
personhood. — **FDK:** uniform `NO_STANDING_IN_V1`; cannot represent the *global
legal experiment* in progress.

### F. Legal constructs: corporations, trusts, future generations

**23. Corporate personhood (*Citizens United*, 2010; *Santa Clara*, 1886).** A
corporation is a rights-holder (speech, property, due process) — a *constructed*
person with no `is_human=True` natural subject. — **FDK: `NO_STANDING_IN_V1`** if
read literally (`is_human=False`), which is *absurd* — corporations are the most
litigated rights-holders alive. The only FDK escape is to model the corporation
as its human owners, which **dissolves the entire point of incorporation**
(limited liability, the corporate veil, the firm as a distinct contracting
party). FDK has no `LEGAL_PERSON` standing.

**24. The trust (equity; *Saunders v Vautier*, 1841).** A device splitting
*legal* title (trustee) from *beneficial* interest (beneficiary), letting a
beneficiary hold an interest they cannot manage. — **FDK: cannot represent.**
This is the cleanest legal solution to FDK's exact problem (holder ≠ exerciser),
and FDK's flat `OwnershipGraph` (`human_owns: dict[Entity, set[Resource]]`,
`model.py`) has *one owner per resource*, no legal/beneficial split. The trust is
600 years of jurisprudence on represented standing, and FDK's model can't encode
it.

**25. Charitable / purpose trusts & the unborn beneficiary.** Trusts routinely
hold property *for persons not yet born* (subject to the rule against
perpetuities). — **FDK: `NO_STANDING_IN_V1`** (future persons, `is_present=False`)
— yet the law *successfully* binds present property to unborn holders every day.
FDK declares impossible what equity does routinely.

**26. Future-generations constitutional clauses.** Norway (§112), Kenya (2010
preamble/Art. 42), Bolivia, and Wales's *Well-being of Future Generations Act
2015* (with a statutory **Future Generations Commissioner** — an actual appointed
guardian for the unborn). — **FDK: `NO_STANDING_IN_V1`,** and per `STANDING.md`,
duties to future people are *inexpressible* (no `Entity` for them in `affects`).
**The Welsh Commissioner is a working `GUARDIAN_REPRESENTED` for future
generations** — the very thing FDK says cannot exist. FDK is empirically refuted
by a functioning office of state.

### G. Machines and AI

**27. AI / AGI personhood proposals (EU Parliament 2017 "electronic persons"
resolution; rejected 2018 after open-letter backlash).** A live, debated proposal
to grant legal personality to autonomous systems. — **FDK: doubly closed.**
`AgentType.MACHINE` is "a tool, never a rights-bearer" (`STANDING.md`), so a
machine is `NO_STANDING_IN_V1` *and* the kernel hard-codes anti-machine-sovereignty
flags (`increases_machine_sovereignty`, `model.py`). FDK doesn't merely lack AGI
standing — its primitive is *built to deny it*, which is a substantive (and
contestable) metaphysical commitment dressed as a safety constraint. A future
where some artificial systems warrant standing is *unrepresentable by
construction*.

**28. Sophia/robot-citizenship (Saudi Arabia, 2017) & electronic-agent contract
law (UCITA; UNCITRAL e-commerce — machines as agents that *bind* principals).**
Machines already *act in law* as agents. — **FDK:** models machines only as
*owned, scoped tools* (`machine_scope`, `delegated`), never as agents whose acts
create obligations for a principal in the principal's absence. The agency-law
reality (a bot forms a binding contract) sits between "tool" and "person," a cell
FDK lacks.

---

## 3. Where FDK is WRONG (not merely incomplete) — the brutal list

1. **Animal cruelty → ALLOW (a wrong verdict, not a silence).** §15. `LIMITATIONS`
   admits "cruelty to an owned animal reads as legitimate use." This is FDK
   producing the *opposite* of settled law, not declining to opine. A theory that
   legitimizes torturing a dog you own is not "scope-limited"; it is wrong on a
   case it *does* decide.

2. **The classifier's inputs pre-decide the contested question.** §12. By taking
   `is_human`/`is_present` as "observable status facts," `assess_standing`
   converts the fetal-personhood and animal-standing debates into data-entry. The
   answer is whatever you typed. This is **petitio principii compiled into a
   decision tree** — the worst failure mode for something claiming neutrality.

3. **Guardianship is mis-bound and cannot be defeated.** §4, §5, §7. FDK reads a
   guardian's *own* attested `Consent` as the subject's, with **no best-interests
   override**. A guardian who consents *against* the ward produces a valid consent
   and the gate passes. Every child-protection and elder-abuse regime exists
   because this is false. FDK's `GUARDIAN_REPRESENTED` is a laundering channel.

4. **`revocable=True` invalidates advance directives.** §6. A living will is, by
   construction, irrevocable by the (now incompetent) maker; FDK's `Consent.is_valid()`
   rejects non-revocable consent, so FDK *voids the one instrument designed for
   exactly this standing problem.* A rule meant to protect exit rights destroys a
   protective device.

5. **Competence is read at the instant of the act.** §10. A consenting patient
   who is then anaesthetised becomes a `PROTECTED_NON_CONSENTER` mid-operation;
   FDK has no *persistence of consent through incapacity*. Prior valid consent
   evaporates exactly when surgery needs it.

6. **"Advisory / neutral" is false neutrality where deferral is an outcome.** §9.
   For a PVS patient on life support, "defer to a human / appoint a guardian"
   *is* the decision to continue treatment. There is no act-free baseline; FDK's
   refusal to rule is a ruling with a default direction (status-quo / keep
   acting-on-the-body off), and it never owns that.

7. **The guardianship machinery is gated on species, not structure.** §20. The
   Whanganui River is *structurally* a `GUARDIAN_REPRESENTED` holder (appointed
   surrogates, non-competent ward) and FDK refuses it *only* because
   `is_human=False`. The species gate is doing normative work FDK never argues
   for — it just asserts `AgentType` exhausts the holders.

8. **One owner per resource forecloses the trust, the corporation, and the
   commons.** §23, §24, and `LIMITATIONS` §2. `human_owns: dict[Entity,
   set[Resource]]` cannot split legal from beneficial title, so the single most
   successful legal solution to "holder ≠ exerciser" (the trust) is inexpressible.

9. **Death erases standing entirely, making probate impossible.** §14. Estates
   become "permanently consent-required" — a *daily* legal act FDK says can never
   be legitimate.

10. **The non-identity wrong is not represented at all** — see §6. This is the
    deepest one, because it is not a missing cell but a missing *kind of victim*.

---

## 4. Engagement with the literature (and where it cuts FDK)

**Will theory vs. interest theory of rights (Hart vs. Raz / MacCormick).**
A *will* (or "choice") theory holds that to have a right is to have *control* over
another's duty — the power to waive or enforce it. An *interest* (or "benefit")
theory holds that to have a right is for one's *interests* to be sufficient ground
for another's duty. **FDK is a pure will theory** — rights are exercised through
`Consent`, a waiver/authorization speech act — and *will theory's notorious bullet
is exactly FDK's gap*: on will theory, infants, the severely incapacitated, the
dead, and animals **cannot hold rights at all**, because they cannot exercise
control. MacCormick's classic objection ("children have rights") is the standing
catalogue above. FDK has *implemented will theory and inherited its exact
extensional failures* — and then labeled those failures "scope limits" rather than
recognizing them as the theory's known cost. An interest theory would put infants,
animals, and future people *in frame as holders* and make guardianship a matter of
*who voices a held interest* — which is what every doctrine in §2 actually does.
**FDK chose the side of the debate that cannot represent most of the catalogue,
and did not notice it was choosing.**

**Korsgaard, *Fellow Creatures* (2018).** Korsgaard argues from a Kantian base
that animals are *ends in themselves* — we have duties *to* them, not merely
duties *regarding* them — precisely because they have a good that can go well or
badly *for them*. This directly indicts §15/§18: FDK's `is_human` holder-predicate
is the speciesist line Korsgaard dismantles *from within Kantianism* (so FDK can't
hide behind "rights require rational agency" — Korsgaard grants the Kantian
premise and still gets animals in). FDK has no concept of a being with *a good of
its own* that is not a consenting will; yet that — not consent — is what grounds
most standing.

**Nussbaum, *Frontiers of Justice* (2006) and the capabilities approach.**
Nussbaum builds her whole case from the three populations *social-contract /
consent theories cannot handle*: people with severe disabilities, animals, and
people across borders/generations. Her thesis is that **a consent/contract frame
is structurally inadequate to justice for non-contractors**, and that standing
should track a being's *capabilities* (what it can be and do) rather than its
ability to contract. FDK is precisely the consent frame she targets. *Frontiers of
Justice* reads as a chapter-by-chapter anticipation of FDK's standing failures —
the disabled (§B), animals (§D), future generations (§F) are her three frontiers
and FDK's three `NO_STANDING_IN_V1` buckets. The match is not coincidence; it is
the predictable shape of every will/contract theory's blind spot.

**Intergenerational justice and Parfit's non-identity problem.** Treated as §6 —
the load-bearing critique.

**Also relevant:** Stone, *Should Trees Have Standing?* (1972) — the founding text
of rights-of-nature, and an explicit proposal for *guardianship of non-persons*
that FDK's machinery could implement but its species-gate forbids (§19–§22).
Rawls's deferral of animals/disability/future-generations to "outside the theory"
(*Theory of Justice* §17, §44) is FDK's exact move — and it is the move Nussbaum
attacks; FDK inherits both the strategy and the objection. Singer (*Animal
Liberation*, 1975) on speciesism as the indictment of the `is_human` predicate.

---

## 5. Open sub-problems & what counts as PROGRESS

**The open sub-problems (none solved here):**

- **O1 — The holder predicate.** Replace the species fiat (`is_human`) with a
  defended criterion: will, sentience, having-a-good-of-one's-own, or a *plural*
  ontology of standing-kinds. Each choice has bullets (§4); the work is to *pick
  one and own its bullets*, not to leave it as a boolean.
- **O2 — Onset/offset and graded capacity.** Replace cliff predicates
  (`is_present`, boolean `competent`) with *decision-relative, time-indexed*
  capacity (Gillick §2, Mental Capacity Act §11) and a defended account of when
  standing begins/ends (fetus §12–13, death §14).
- **O3 — Faithful representation.** A best-interests / substituted-judgment
  predicate that lets a guardian's attestation be *defeasible* against the ward's
  good (§4–9). This is the gap that turns guardianship from a laundering channel
  into genuine representation. Requires the kernel to read *two* parties (held and
  holder-of-the-power) where it now reads one.
- **O4 — Constructed & split standing.** A `LEGAL_PERSON` / trust device:
  legal vs. beneficial title, conferred (not discovered) standing, the
  corporation and the purpose-trust-for-the-unborn (§23–26). Needs the
  `OwnershipGraph` to drop "one owner per resource."
- **O5 — The non-identity-proof duty primitive** (see §6): a way to express a
  wrong to a class/role that is invariant under which individuals come to occupy
  it.

**What counts as PROGRESS (the bar):**

Progress is **not** more `NO_STANDING_IN_V1` buckets or more honest disclaimers.
Progress is:

1. **A defended formal ontology of standing** — a typed `Standing` lattice with
   an *argued* holder-predicate (O1), explicit onset/offset and graded capacity
   (O2), and a representation relation with a fidelity condition (O3) — such that
   every case in §2 lands in a cell *the ontology can justify*, and the fetal/
   animal cases are decided by *stated normative commitments*, not by data entry.
2. **The hard rulings, made and owned.** Pick the verdicts FDK currently launders
   into "facts": Does a fetus have standing, from when? Does an owned animal? A
   river? A future generation? AGI? A defended ontology *takes positions* and
   accepts they are falsifiable, rather than hiding them in `StandingFacts`
   inputs. The minimum deliverable is the five hardest rulings (§12 fetus, §15
   animal, §20 river, §26 future generations, §27 AGI) stated as *theory output*,
   not user input.
3. **A representation calculus that can be wrong** — i.e. where a guardian's
   "yes" can be *overridden by the ward's interest* inside the formalism (O3),
   so §4/§5 (best-interests override) is expressible. Until a guardian can be
   *defeated*, standing is not modeled; only delegation is.

Anything less is honest scaffolding, not a solution — which is exactly what
`spec/STANDING.md` already, to its credit, says it is.

---

## 6. The deepest place FDK is wrong: the non-identity problem

This is the critique to take seriously, because it shows the standing gap is not a
missing feature but a property of FDK's *primitive*.

**The problem (Parfit, *Reasons and Persons* (1984), ch. 16).** Many acts that
seem to *harm future people* also *determine which future people exist*. A policy
of resource depletion, or a choice to conceive now rather than later, changes the
identity of who is later born (different timing → different gametes → numerically
different people). So the people who live in the depleted, damaged future are
**not worse off than they would otherwise have been** — because *otherwise they
would not have existed at all*, and (assuming their lives are still worth living)
existence-with-harm beats non-existence. There is **no particular person who can
say "I was made worse off."** Yet depleting the world for a damaged posterity is
obviously wrong. The wrong has *no identifiable victim with a comparative
complaint*. This is the non-identity problem.

**Why it is lethal to FDK specifically.** FDK's gate is *person-affecting and
consent-based to the core*. The wrong of an action is cashed out as a
`rights_violation` against, or absent consent from, the specific `Entity` objects
the action `affects` (`CandidateAction.affects: tuple[Entity, ...]`,
`model.py`). The non-identity problem is the proof that **a person-affecting,
victim-indexed framework is structurally blind to a real class of grave wrongs**:

- The future people are already `NO_STANDING_IN_V1` (`is_present=False`), so they
  are not in `affects` at all — *the act passes for want of a plaintiff.* (This is
  the under-inclusion of §1.) `STANDING.md` admits the duty is "inexpressible."
- But non-identity makes this **worse than a tooling gap.** Suppose FDK *did*
  someday add future people as entities. Non-identity says it *still* fails:
  because the very same act *creates* the entities it would have to wrong, you
  cannot point to any `Entity e` such that `e` was made worse off — for every
  actual future person, the depleting act was a *condition of their existence*.
  A victim-indexed gate **cannot find a victim**, no matter how you extend the
  entity set. Adding future-person entities does not help, because the
  complaint is non-comparative and non-person-affecting.
- So the fix is not O2 (onset/offset) alone. It requires **a duty primitive that
  is not victim-indexed** — a wrong to a *role, a class, or an impersonal
  standard of how the future ought to go* (cf. Parfit's own move toward
  "principles that are not person-affecting," and the same-number/different-number
  "Non-Identity" and "Repugnant Conclusion" puzzles). FDK has no such primitive
  and, given that `legit` is defined over `affects`/`consent`, *cannot get one
  without changing the primitive.* This is why standing was flagged as "the
  roadmap's most dangerous frontier, because getting it wrong can change the
  primitive itself" (`STANDING.md`) — non-identity is the concrete proof of that
  sentence.

**The brutal conclusion.** FDK's deepest standing error is not that it omits
animals or fetuses (it could, in principle, bolt on entities for those). It is
that its core legitimacy relation is *person-affecting and consent-indexed*, and
the non-identity problem demonstrates a whole category of wrong — wrongs to the
future that wrong *no one in particular* — that such a relation **cannot
represent even in the limit.** For these cases the gate does not give the wrong
answer cautiously; it gives the *confidently wrong* answer (ALLOW, no rights
violated, no consent owed — there is no one to owe it to), and it does so for
*structural* reasons that no amount of extra `Entity` objects repairs. A
legitimacy kernel that cannot, in principle, say "depleting the world for a
damaged posterity is illegitimate" is missing not a case but a *kind of moral
fact* — and that is the most important thing this audit found.

---

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust
(CC BY 4.0). This document is a hostile research audit of the standing frontier;
it states problems, not fixes. Engineering scaffolding: Ali Pourrahim.*
