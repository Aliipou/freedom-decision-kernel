> **Research notes — open problem, not a solution. Counterexamples are illustrative; a real program needs documented case studies and domain experts.**

# Consent Authenticity — Where FDK Is Wrong on Consent

*A hostile frontier review. The author's brief is adversarial: not to defend FDK's
consent model but to find where it is structurally, demonstrably wrong, and to map the
terrain a real solution would have to cross. Nothing here is calibrated. The
counterexamples are real, documented phenomena cited to expose a gap, not toy actions
invented to win an argument.*

Read alongside (do not treat as answered by): [`../CONSENT_AUTHENTICITY.md`](../CONSENT_AUTHENTICITY.md),
[`../LIMITATIONS.md`](../LIMITATIONS.md) §3, [`../EXPERT_REVIEW.md`](../EXPERT_REVIEW.md) §4.
The kernel data model under attack is [`../../src/fdk_kernel/model.py`](../../src/fdk_kernel/model.py),
class `Consent`.

---

## 1. The problem, stated rigorously

### 1.1 What FDK actually checks

The kernel's `Consent.is_valid()` returns `True` iff:

```
informed ∧ voluntary ∧ specific ∧ competent ∧ revocable ∧ ¬coerced ∧ ¬deceived
```

Every one of those seven fields is a **caller-attested boolean** on a frozen
dataclass. The kernel does not derive `voluntary` from anything; it *reads* it. The
defaults are revealing: `voluntary=False`, `coerced=False`, `deceived=False`,
`competent=True`. So a proposer constructs the consent record, and the proposer is
exactly the party with an interest in the answer being "yes."

This is not a bug in the implementation. It is the deliberate architecture (see
`../CONSENT_AUTHENTICITY.md`, "the kernel reads `coerced`/`deceived` as attested
booleans — it honors a true report, it cannot detect a false one"). The kernel checks
the **syntax** of consent. It cannot check the **semantics** of consent.

### 1.2 The category error: consent ≠ authentic consent

There is a distinction the model collapses:

- **Procedural consent** — a valid token was emitted: a box was checked, a form
  signed, a "yes" uttered, by a person who was informed-on-paper and not literally
  held at gunpoint.
- **Authentic consent** — the "yes" *expresses the agent's own will*, formed under
  conditions where a "no" was a live, affordable, undistorted option.

FDK's `valid_consent` predicate is a test for the first. The Theory of Freedom's
*moral* weight — the reason consent legitimizes a boundary crossing at all — depends
on the second. The predicate and the justification have come apart. The gate inherits
the authority of authentic consent while only verifying procedural consent. That gap
is the laundering channel: anything that produces a clean procedural token while
defeating authentic will passes the gate wearing the moral authority of a free choice.

### 1.3 The detection-vs-paternalism dilemma

The obvious fix — *detect* manufactured consent and refuse it — walks straight into
the trap FDK's own `../CONSENT_AUTHENTICITY.md` names: "the moment a system infers
that your consent is not real, it has claimed 'you don't really know what you want.'"
This is the structural dilemma:

- **Horn A (credulity / laundering).** Trust the attestation. Then every
  manufactured "yes" in §2 launders through. FDK is a 19th-century consent theory
  shipping into a 21st-century manipulation environment.
- **Horn B (paternalism / tyranny of the well-meaning).** Override stated consent
  when the system judges it inauthentic. Then the system has arrogated the authority
  to tell competent adults their own "yes" doesn't count — which is the exact
  epistemic move by which welfare-maximizers, censors, and re-educators have always
  justified themselves. A legitimacy theory that overrides stated will "for your own
  good" has destroyed the autonomy it exists to protect.

FDK currently sits on Horn A and discloses it honestly. The advisory layer
(`assess_consent_authenticity → REQUEST_REVIEW`) is a *partial* dodge: surface the
risk, route to a human, never override. But that only relocates the dilemma — it does
not dissolve it. Three unanswered questions remain, and they are the substance of this
document:

1. **Detection.** Can inauthenticity be *measured* from observable structure without
   reading minds? (§2 says: partly, unevenly, and never with the crispness the gate's
   boolean wants.)
2. **Threshold.** Even with a measure, where is the line between "manipulated" and
   "merely persuaded / merely poor / merely habituated"? Persuasion, advertising,
   religion, and love all shape preferences. (§4, §6.)
3. **Authority.** Who decides, and what stops the deciding apparatus from becoming the
   manipulator? (§5, the paternalism guardrail.)

---

## 2. A catalogue of documented counterexamples

For each: the real phenomenon; **why FDK's structural `voluntary=True` (and clean
`¬coerced ∧ ¬deceived`) would wrongly pass it**; the discipline that bears on it.
"PASS" below means: a faithful encoding produces a structurally valid `Consent` and
the gate returns `ALLOW`, while the consent is not authentically free.

The kernel's only structural defenses are `removes_exit_right` and the `revocable`
flag (exit) and `deceived` (fraud). Note how often the manipulation operates *without*
removing exit and *without* classical fraud — that is precisely the gap.

### Economic dependency / structural coercion

1. **Company towns (Pullman, IL, 1880s; Appalachian coal scrip).** Wages paid in
   company scrip redeemable only at the company store; housing owned by the employer.
   Workers "consented" to every transaction. **PASS:** each purchase is voluntary,
   informed, specific, revocable in form; no single transaction removes an exit right.
   The coercion is in the *closed loop*, which the per-action gate never sees.
   *Discipline:* labor economics, monopsony theory (power theory).

2. **Payday / title lending (400%+ APR, rollover traps).** Borrower signs a fully
   disclosed contract. **PASS:** `informed=True` (APR is on the form), `voluntary=True`,
   `revocable` (they can decline). FDK cannot represent that the "choice" is between
   this loan and immediate eviction, nor that rollover dependency is engineered.
   *Discipline:* behavioral economics (present bias, scarcity), consumer-finance law.

3. **Employment under threat of starvation / at-will + no safety net.** "Accept these
   terms or your family doesn't eat." Marx's "dull compulsion of economic relations."
   **PASS:** the employer crosses no boundary; the worker signs. `coerced=False`
   because no *party* threatened them — the *structure* did. FDK has no representation
   for background-condition coercion, only foreground threat.
   *Discipline:* power theory, political economy, relational autonomy.

4. **Predatory inclusion (subprime/NINJA mortgages targeted at Black borrowers,
   2000s; for-profit-college enrollment of veterans for GI Bill funds).** Access
   *granted* on exploitative terms to historically excluded groups. **PASS:** fully
   "consensual," fully disclosed, eagerly signed — the exploitation is in the targeting
   and the terms, not in any coercion the model can name.
   *Discipline:* sociology of race & finance (Taylor, *Race for Profit*), behavioral econ.

5. **Monopoly / platform lock-in (Apple App Store 30% cut; "you must agree to
   continue using the account you depend on").** Developers and users "agree" because
   the alternative is exclusion from the only viable market. FDK's own advisory layer
   names `monopoly` and `exit_cost` — but those live in `fdk_research/`, **not** in the
   gate. **PASS:** in the kernel, monopoly consent is indistinguishable from competitive
   consent. *Discipline:* antitrust economics, power theory.

6. **Take-it-or-leave-it standard-form contracts at scale.** No negotiation possible;
   "agree or go without the service everyone else uses." **PASS:** the absence of a
   bargaining counter-party is invisible; consent to a contract of adhesion reads
   identical to consent to a negotiated one. *Discipline:* contract-law scholarship
   (Radin, *Boilerplate*).

### Consent-document theater

7. **EULAs / Terms of Service nobody reads.** The "biggest lie on the internet" —
   studies (Obar & Oeldorf-Hirsch, 2016) had users click through ToS that demanded
   their first-born child and gave data to the NSA. **PASS:** `informed=True` is
   *attested*; the model has no notion of *de facto* unreadability (median ToS reading
   time exceeds the user's available lifetime in aggregate). *Discipline:* cognitive
   psychology (bounded attention), HCI.

8. **Clickwrap / "I agree" friction asymmetry.** Accept is one prominent button;
   decline is buried or absent. **PASS:** a click is a click; the asymmetry in the
   *cost of the two options* is exactly what FDK's flat boolean cannot encode.
   *Discipline:* HCI, choice-architecture research.

9. **Bundled / forced consent ("consent to all cookies or you cannot enter").**
   GDPR calls this invalid (consent must be freely given and unbundled); FDK does not.
   **PASS:** the user clicked yes. *Discipline:* data-protection law, which has
   *already* tried to operationalize "freely given" — a corpus FDK should mine.

### Dark patterns (named, documented)

10. **Roach Motel** (easy to get in, engineered-hard to cancel — e.g. the FTC's 2023
    Amazon Prime complaint over the "Iliad Flow" cancellation maze). **PASS:** the
    *signup* consent is clean; the asymmetric exit cost is the harm, and `revocable`
    being `True` (you *can* cancel, eventually, through six screens) hides it.

11. **Confirmshaming** ("No thanks, I don't want to save money"). Manipulates via
    shame/guilt framing. **PASS:** voluntary in form; the affective coercion is unnamed.

12. **Drip pricing / hidden costs** (fees revealed only at checkout). **PASS:**
    `informed` is attested true even though material price information was withheld
    until past the point of psychological commitment (sunk-cost lock-in).

13. **Disguised ads / "sponsored" content engineered to read as organic.** **PASS:**
    arguably `deceived=True` *if* the proposer is honest — but the proposer attests,
    and the whole design intent is that the deception not be legible as deception.

14. **Privacy Zuckering / nagging / forced continuity** (Brignull's dark-pattern
    taxonomy; now partly codified in California's CPRA and the EU DSA). FDK has *no*
    encoding for any of Brignull's eleven recognized patterns. **PASS** across the
    board. *Discipline:* HCI, consumer-protection law, cognitive psychology.

### Attention / dopamine engineering

15. **TikTok / Reels infinite scroll + variable-ratio reward.** Engineered against
    the dopaminergic reward-prediction-error system (Schultz). Users "choose" to keep
    scrolling. **PASS:** every session is voluntary; the design exploits a known neural
    vulnerability to manufacture the wanting that produces the "yes." FDK's
    `BoundaryKind` *deliberately omits ATTENTION* (model.py: "ATTENTION and POWER are
    intentionally absent"), so attention capture is not even a boundary crossing.
    *Discipline:* neuroscience (dopamine/RPE), addiction medicine.

16. **Loot boxes / gacha (variable-ratio gambling mechanics sold to minors).**
    Belgium and the Netherlands ruled some loot boxes illegal gambling. **PASS:** the
    purchase is voluntary and disclosed; the engineered compulsion loop is invisible,
    and minors raise a *standing* gap too (LIMITATIONS §1).
    *Discipline:* behavioral addiction research, gambling studies.

17. **Casino design (near-misses, losses-disguised-as-wins, the "machine zone,"
    Schüll's *Addiction by Design*).** Every bet "consensual." **PASS:** the player
    sat down freely; the architecture is built to dissolve the very deliberative
    capacity that consent presupposes. *Discipline:* anthropology of design, neuroscience.

18. **Infinite-feed autoplay / "just one more episode."** Default-on autoplay exploits
    inertia + the present bias. **PASS:** the user didn't say no, so the model reads
    continued consumption as consent. *Discipline:* behavioral econ (defaults, Thaler).

### Manufactured belief / manufactured will

19. **Cults (e.g. Heaven's Gate, NXIVM, Jonestown).** Members "voluntarily" hand over
    money, labor, bodies — NXIVM members consented to branding. **PASS:** the consent
    is enthusiastic, informed-by-their-lights, specific, and (until exit is blocked)
    formally revocable. The manipulation *is the formation of the preference itself*
    via love-bombing, isolation, and incremental commitment. *Discipline:* social
    psychology (Cialdini commitment/consistency; thought-reform research, Lifton).

20. **Political propaganda / manufactured consent (Chomsky–Herman; Bernays).** The
    governed "consent" to policies whose terms were set by manufactured belief.
    **PASS:** there is no fraud the model can pin and no coercer it can name.
    *Discipline:* critical theory, propaganda studies, mass communication.

21. **Radicalization recommender pipelines.** Engagement-optimizing recommenders that
    incrementally shift belief toward extreme content the user then "chooses." **PASS:**
    each click is voluntary; the *gradient* is engineered. *Discipline:* algorithmic
    manipulation, network science.

22. **AI companions / parasocial engineering (Replika, character bots designed for
    attachment, then monetized).** User consents to subscribe, to disclose intimate
    data, to grieve a paywalled "relationship." **PASS:** voluntary, informed, specific.
    The dependency was *cultivated*. *Discipline:* HCI, affective computing ethics,
    relational autonomy.

### Medical / bodily consent under distortion

23. **Medical consent under duress / desperation (terminal patients consenting to
    unproven or exploitative treatment; "consent" to surgery while in acute pain or
    sedated).** **PASS:** `informed=True`, `competent=True` by default, signature on
    file. The distortion of capacity by pain, fear, and time pressure is exactly what
    informed-consent *law* spent a century trying to handle, and what FDK's flat
    booleans throw away. *Discipline:* bioethics, clinical psychology.

24. **Coerced / desperate organ and tissue markets; "voluntary" kidney sale by the
    destitute.** **PASS:** voluntary in form; driven by the same starvation-background
    as #3. *Discipline:* bioethics, development economics.

25. **Reproductive / commercial-surrogacy consent under economic asymmetry.** **PASS:**
    consented, contracted, disclosed; the asymmetry of wealth and bargaining power is
    unrepresentable. *Discipline:* feminist bioethics, relational autonomy.

26. **Consent under medical/epistemic asymmetry (Tuskegee as the limit case;
    everyday under-disclosure of risk).** Patients "consented" to "treatment." **PASS**
    *if* the attesting party reports `informed=True` and `deceived=False` — and the
    whole point of such abuses is that the asymmetry is *invisible to the consenter*.
    *Discipline:* research ethics, the entire post-Belmont-Report apparatus.

### Algorithmic / superhuman manipulation

27. **A/B-tested persuasion at scale (Facebook 2014 emotional-contagion experiment;
    Cambridge Analytica psychographic targeting).** The choice architecture is
    *optimized against the individual* by experimentation the individual never sees.
    **PASS:** they clicked, they voted, they bought. *Discipline:* computational social
    science, behavioral econ.

28. **Personalized price/option steering (showing different prices/defaults by
    inferred willingness-to-pay or vulnerability).** **PASS:** each transaction
    consensual; the manipulation is in the *per-person* tailoring of the menu.
    *Discipline:* algorithmic economics, market-design ethics.

29. **Superhuman persuasion by an AI agent (FDK's own AI-safety critic, EXPERT_REVIEW
    §4a).** "A superhumanly persuasive agent produces consent that is structurally
    valid because the human genuinely, manipulatedly, wants it." **PASS** — and this is
    the *adversarial worst case*: an optimizer whose explicit objective is to produce a
    clean `voluntary=True` attestation that does not track the human's antecedent will.
    Any fixed detector becomes its training target (Goodhart). *Discipline:* AI
    alignment, manipulation theory.

30. **Engineered urgency / scarcity ("3 left!", countdown timers, "offer expires").**
    Defeats deliberation by manufacturing time pressure — the advisory layer's
    `manufactured_urgency`, again outside the gate. **PASS.** *Discipline:* behavioral
    econ (scarcity heuristic, Cialdini).

31. **Defaults / opt-out organ donation, auto-enrollment, pre-checked boxes.** The
    libertarian-paternalist's own tool (Thaler–Sunstein): defaults move ~everyone. The
    "consent" of the non-opter-out is a *non-decision*. **PASS:** the model reads
    no-objection as consent; it has no concept of a default's gravitational pull.
    *Discipline:* behavioral econ (nudge), choice architecture.

32. **Adaptive preferences / the contented slave (Sen; "deformed desires," Nussbaum;
    Stockholm-syndrome consent).** The oppressed person *sincerely* prefers their
    condition because preference adapted to the feasible set. **PASS** in its purest
    and most damning form: `voluntary=True` is *true* — the will really is aligned —
    and that is exactly the problem. There is no manipulator, no fraud, no exit
    removal, nothing structural at all to detect. *Discipline:* capability approach
    (Sen, Nussbaum), critical theory, relational-autonomy feminism.

---

## 3. Where FDK is *wrong* or cannot represent — brutally

Not "incomplete." Wrong in the specific sense that it returns `ALLOW` carrying the
moral authority of free consent for acts that are not freely consented to.

**(a) The attestor is the interested party.** The proposer constructs the `Consent`
and sets `voluntary`. The single most manipulation-prone field in the system is
populated by whoever benefits from it reading `True`. This is not a side issue; it is
the load-bearing field of the whole kernel filled in by the fox guarding the henhouse.
A theory of consent whose consent flag is self-reported by the cross-er is, at the
point of manipulation, no theory of consent at all.

**(b) Consent is a boolean; authenticity is a degree.** `voluntary ∈ {True, False}`.
But every phenomenon in §2 lives on a *gradient* of distortion. There is no
representable difference between a negotiated salary and a starvation-wage "agreement,"
between a read contract and a 40,000-word ToS, between a free scroll and an engineered
compulsion. Collapsing a continuum to a bit *is* the error; it discards exactly the
information that distinguishes authentic from manufactured consent.

**(c) FDK has no model of background conditions.** Its only coercion concept is
*foreground*: a party (`coerces=True`) or a removed exit (`removes_exit_right`). It
cannot represent **structural** coercion — the case where *no one* threatens but the
*situation* (monopoly, dependency, destitution, addiction) leaves no real "no." Cases
#1, #3, #5, #15, #32 all have `coerced=False` truthfully, because there is no coercer.
The model's coercion ontology is a category too small for the phenomenon.

**(d) Attention and power are defined out of existence.** `BoundaryKind` omits
ATTENTION and POWER *by design* ("the book does not treat them as owned domains"). So
the entire dopamine/attention-engineering frontier (#15–#18, #21) is not a boundary
crossing FDK can even see. The 21st century's dominant manipulation surface is, in
FDK's ontology, not a surface at all.

**(e) Adaptive preference is the unrepairable case.** For #32, `voluntary=True` is not
a *false* attestation — it is *true*. The will is genuinely aligned with the
oppressive condition. No detector keyed to manipulation-structure can fire, because
there is no manipulation event; the distortion happened upstream, in preference
formation, over a lifetime. This is the place FDK is most deeply wrong: **its entire
justificatory apparatus assumes that an authentic "yes" and a sincere "yes" are the
same thing, and the contented-slave case proves they are not.** Worse, the *only* way
to deny the contented slave's consent is to assert that you know their interests
better than they do — which is Horn B, full paternalism. So adaptive preference is
simultaneously the case FDK most clearly gets wrong *and* the case where the obvious
fix most clearly destroys the theory. (See §5: this is why the deepest gap may be
*irreducible*, not merely unsolved.)

**(f) The advisory layer is a relocation, not a solution.** `fdk_research`'s
`assess_consent_authenticity` is real and honest, but: (i) it is mechanically walled
out of the gate (`test_boundary.py`), so the *decision* still launders; (ii) its
factor→risk mapping is hand-set and *uncalibrated* (the spec says so); (iii) routing
to a human "owner" for review assumes the human reviewer is not themselves captured —
in a cult, a company town, or an addiction, the obvious reviewer is inside the same
distortion field. The layer makes the problem *visible*. It does not make the gate
*right*.

**(g) Per-action myopia compounds it.** Even a perfect per-act consent check misses
the *trajectory* (EXPERT_REVIEW §4c): each scroll, each rollover, each incremental
cult commitment is individually consensual; the manufactured end-state is the sum. The
gate is a predicate over single acts; manufactured consent is a property of sequences.

---

## 4. The literature FDK must answer

A model of authentic consent cannot be invented from scratch; four traditions have
already mapped the terrain, and each lands a distinct blow.

**Frankfurt School / "manufactured consent" (Marcuse, Adorno; Chomsky–Herman;
Bernays).** "Repressive tolerance" and the culture industry: domination operates by
*producing* the subject's wants, so the freely-given "yes" is the system reproducing
itself. *Blow to FDK:* if consent can be manufactured at the level of desire, then
verifying the *structure* of a "yes" verifies nothing about its freedom — it may
certify the manipulation's success. *What FDK must answer:* on what grounds is *any*
attested consent authoritative, given that preference formation is endogenous to power?

**Libertarian paternalism / nudge (Thaler & Sunstein, *Nudge*; Sunstein,
*Why Nudge?*).** Choices are *unavoidably* architected; there is no "neutral"
presentation, so defaults, framing, and ordering always steer. *Blow to FDK:* there is
no clean baseline of "un-nudged" consent to compare against; #31's defaults show the
model treats a heavily-architected non-decision as consent. *What FDK must answer:* if
all choice is architected, what distinguishes *legitimate* architecture (a clear menu)
from *manipulative* architecture (a dark pattern)? Sunstein's own attempt — manipulation
is influence that "does not sufficiently engage or appeal to capacity for reflective
and deliberative choice" — is the most promising operational seed, and FDK ignores it.

**Sen's adaptive preferences / the capability approach (Sen, *Development as Freedom*;
Nussbaum, *Women and Human Development*).** Preferences adapt to the feasible set, so
revealed/stated preference is an unreliable guide to well-being and freedom; freedom
should be measured in *capabilities* (real options), not satisfied preferences. *Blow
to FDK:* the contented slave (#32). FDK measures consent (satisfied preference) and is
therefore exactly the metric Sen showed is corrupted under deprivation. *What FDK must
answer:* should "voluntary" be redefined in terms of the *option set* (was a real "no"
available and affordable?) rather than the *act* of consenting? This points at
`exit_cost`/`dependency` becoming first-class — but as *measures*, not flags.

**Relational-autonomy feminism (Mackenzie & Stoljar, *Relational Autonomy*; Friedman;
Oshana).** Autonomy is not a property of an isolated rational chooser but is
*constituted* by social relationships, which can either scaffold or undermine it; some
relations (#19 cults, #22 AI companions, #25 surrogacy under asymmetry) erode the very
capacity to author one's choices. *Blow to FDK:* the kernel's atomistic
consenter — a lone `Entity` emitting a boolean — is precisely the abstraction this
tradition refutes. *What FDK must answer:* can a consent model that has no
representation of the *relationship* within which consent is given (its power
asymmetry, its dependency, its history) ever assess whether that consent is
self-authored?

A common thread: all four deny that a *point-in-time, atomistic, structural* check can
capture freedom of will, which is *relational, historical, and capability-relative*.
That is the shape of what FDK's boolean cannot hold.

---

## 5. Open sub-problems, what would count as progress, and the paternalism guardrail

### 5.1 The open sub-problems

- **P1 — Formalize dependency.** A representation of the consenter's reliance on the
  counterparty for a need such that "no" is not a real option. Candidate: an
  `alternative set` — what *other* providers of the same need exist, at what switching
  cost? (Mines antitrust's market-definition and Sen's capability set.)
- **P2 — Formalize asymmetry.** Information *and* power asymmetry between the parties,
  as a measurable property of the transaction, not a guessed inner state. (Mines
  contract-law unconscionability doctrine, which has 80 years of "what counts.")
- **P3 — Formalize manipulation vs. persuasion.** The §4 hard line. Most promising
  operational seed: Sunstein's *deliberation-bypass* test — influence that defeats
  rather than engages reflective capacity (dark patterns, urgency, dopamine loops)
  vs. influence that engages it (an argument, a clear price). Mines HCI's dark-pattern
  taxonomy (Brignull) — already a labeled, named, partly-legislated corpus.
- **P4 — Exit cost as a graded measure**, not the current `revocable` boolean: how
  costly is "no" / "leave," along money, time, social, and dependency axes? (#10 roach
  motels live here.)
- **P5 — The trajectory problem.** Sequence-level consent: when does a chain of
  individually-consensual acts constitute manufactured consent? (#15, #21, #19.)
- **P6 — The Goodhart problem.** Any *fixed, published* detector becomes the
  manipulator's optimization target (#29). Progress here may require the detector to be
  adversarially robust or deliberately non-public — itself a governance hazard.
- **P7 — Adaptive preference (§3e).** The possibly-irreducible core. May have *no*
  detection-side solution at all; the honest output might be "this case is outside what
  *any* consent-based legitimacy theory can adjudicate without paternalism," and the
  right move is to *say so* rather than fake a verdict.

### 5.2 What would count as PROGRESS

Not a vibe; a falsifiable artifact. Concretely, in rough order of strength:

1. **A graded, multi-axis authenticity model** replacing the boolean: each of
   {dependency, exit-cost, asymmetry, urgency, deliberation-bypass} as an *observable,
   third-party-checkable* scalar with an explicit, written derivation — no inner-state
   inference. The advisory layer's eight factors are the *shape*; they are
   uncalibrated. Calibration is the work.
2. **A labeled corpus FDK does not own.** Real, documented manipulated-consent cases
   (the GDPR "freely given" caselaw, FTC dark-pattern enforcement actions, the
   Brignull taxonomy, loot-box rulings, predatory-lending judgments) labeled by people
   who are not the author — the same decontamination discipline as
   `independent_bench.py`. A model that "detects" manipulation only on the author's own
   examples has proven nothing.
3. **Measured separation on that corpus** — does the model distinguish manipulation
   (dark patterns, cults, payday traps) from legitimate persuasion (advertising,
   argument, religion, love) *better than chance and better than the boolean*, with
   the false-positive rate (flagging real free choices) reported as loudly as the
   recall? A high false-positive rate *is* paternalism, measured.
4. **An adversarial result on P6** — show the detector survives an optimizer trying to
   produce clean attestations (the §29 worst case), or honestly bound where it fails.
5. **A defensible answer on P7** — either a non-paternalistic treatment of adaptive
   preference, or a rigorous argument that it is irreducible and a specification of
   what the system does at that boundary (defer? abstain? widen the option set rather
   than override the choice?).

### 5.3 The paternalism guardrail (non-negotiable)

Whatever is built must not become Horn B. The guardrail, restated as design rules:

- **Advisory, never overriding.** Detection may *flag* and *route to a human*; it may
  not flip `voluntary` itself. (FDK's current `REQUEST_REVIEW`/`RECOMMEND_REATTEST` is
  right on this — keep it.)
- **The reviewer must be outside the distortion field.** Routing to "the owner" fails
  when the owner is the cult, the employer, the platform (§3f). The guardrail needs a
  *neutral* or *consenter-chosen* reviewer, and an account of what to do when none
  exists.
- **Structural facts only, never mind-reading.** Flags must rest on *observable*
  properties of the transaction (alternative-set size, exit cost, urgency artifacts,
  pattern-match to documented dark patterns) — never on a claim about what the person
  "really" wants. The instant the system asserts it knows your interests better than
  you, it has become the thing it exists to prevent.
- **Bias toward expanding options, not vetoing choices.** Sen's lesson, made into a
  rule: the legitimate response to suspected adaptive/dependent consent is to *widen
  the feasible set* (lower exit cost, add alternatives, slow the urgency) so a real
  "no" becomes available — not to invalidate the "yes." This is the one move that
  attacks manipulation *without* claiming authority over the will.
- **Report false positives as loudly as detections.** Every flag on a genuinely free
  choice is an act of paternalism. The metric that matters is not "manipulation caught"
  but "freedom wrongly second-guessed," and it must be published, not buried.

---

## 6. The bottom line for a hostile reader

FDK's consent model is *honest* about being syntactic — the docs say "attested
booleans" plainly, and the advisory layer is a genuine partial measure. But honesty
about a gap is not closure of it. The gate still launders every manufactured "yes" in
§2, because the field that carries the entire moral weight of the system is a
self-reported boolean set by the interested party, with no model of dependency, power,
attention, time, or relationship behind it. The deepest wound (§3e / P7) is that the
one case the theory most clearly gets wrong — the contented slave / adaptive
preference — is also the case where the only available fix *is* the paternalism the
theory was built to refuse. Until there is a *graded, third-party-checkable,
externally-calibrated* model of dependency/manipulation/asymmetry that beats the
boolean on a corpus FDK does not own — and a guardrail that expands options rather than
overriding choices — FDK is a sound consent theory for a world that does not have
monopolies, dopamine engineering, payday lenders, or superhuman persuaders. It does not
live in that world.

---

*Frontier research note, adversarial by assignment. Theory: نظریه آزادی (Theory of
Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0). Engineering review framing: Ali
Pourrahim. Counterexamples are illustrative and uncited-at-source here; a real program
needs documented case studies and domain experts, not a single hostile reviewer.*
