# Research agenda — from a working kernel to (maybe) a paradigm

> The engineering roadmap (`ROADMAP.md`) is largely done. This document is the part the
> roadmap is **not**: the scientific program. Its first job is to say, without flattery,
> where FDK actually is, and to make explicit that **more code is no longer the
> bottleneck.** A consistent, beautiful, well-tested theory that explains nothing new is
> a historical commonplace. The wall ahead is explanatory and empirical, not technical.

## The governing discipline: find where FDK is valid AND where it fails

The largest risk now is not a bug; it is a presupposed conclusion. Three goals are all
wrong because each assumes the answer in advance:

- ❌ *Prove FDK is right* (apologetics) · ❌ *Prove FDK is wrong* (its mirror) ·
  ❌ *Show FDK is superior* (assumes there is something to be superior at).

The only honest goal: **discover where FDK is valid and where it fails.** For every
research question below, three outcomes are admissible *from the start* — **FDK survives /
FDK partially survives / FDK collapses** — and the third is as scientifically valuable as
the first. The author does not declare a paradigm; the community, the critics, and the
next generation do.

And one hidden assumption must be dropped: *"if a gap is found, build a new layer."* Some
gaps may not be closable by any layer. It is entirely possible that, after years of work,
**no consistent definition of standing exists** for child + animal + future-generation
simultaneously — and *that discovery is itself a result*, not a failure to engineer. A
research program that can only ever conclude "we'll add a module" is not doing science.

## The missing ingredient: risky predictions

What FDK lacks is not Lean, Rust, or TLA+. It is **risky predictions** — statements of the
form *"if FDK's account of legitimacy is right, then we should observe Y (and NOT Z) in the
world,"* made in advance and checkable against history, law, and economics. Until FDK
sticks its neck out this way, it is a consistent philosophical-logical framework, not a
scientific paradigm. Each program below is therefore stated as a question with an attached
falsifiable prediction, not as a feature to build.

## Where FDK is (honest placement on the 15-stage path)

| Stage | | Status |
|---|---|---|
| 1 | Internal consistency | ✅ largely there |
| 2 | Formalization (Lean / TLA+ / model-checking) | ✅ four checkers, refinement differential-tested |
| 3 | Adversarial survival (best critics try to break it) | 🟡 AI-persona red-teams only; **real humans pending** |
| 4 | **Explanatory power** (explains what rivals can't) | 🔴 **the first real filter — not yet cleared** |
| 5–7 | Predictive power · empirical validation · rival dominance | 🔴 not started (these are *science*, not code) |
| 8–11 | Academic penetration · hostile adoption · new research programs · institutions | 🔴 years, people |
| 12–15 | Practical success · canonical problems · textbook · successor generation | 🔴 a generation |

**FDK is between stage 3 and 4.** Past "raw idea," past "engineering project," a long way
from "paradigm." The single hardest gate is stage 4: *does FDK explain, predict, or solve
something Rawls, Nozick, Hayek, Sen, or Ostrom could not?* If the honest answer is "no,"
FDK is a clean reformulation of old ideas. If "partly," it is a real research contribution.
If "yes," it could matter. We do not yet know.

## What NOT to do (diminishing returns)

The director's standing guidance, recorded so it binds future work: **no** 500 more tests,
**no** 20 more modules, **no** more synthetic benchmarks, **no** more cartoon rivals, **no**
bigger simulations whose only output is a chart. The kernel is frozen (`FREEZE.md`); the
advisory scaffolds exist; the four checkers are green. More of the same buys nothing.

## The research programs (questions, not features), in priority order

Five threads remain, stated as **questions with admissible outcomes (survives / partial /
collapses) and a risky prediction** — never as layers to build. The ordering matters and
it is not the order FDK was built in: **Standing is the most fundamental**, because before
you can ask "was consent valid?" you must know "who may consent?", and before "who owns
this?" you must know "who counts as a rights-holder at all?" Deep counterexample catalogues
for three of them live in `spec/frontiers/`.

### 1. Standing — the most fundamental (and bigger than it looks)
**Question:** *Who is a rights-holder, from when, at what level of capacity?* FDK's entire
theorem set runs on one assumption — a `competent adult human`. The moment you admit a
child, a dementia patient, a long-coma patient, a fetus, an animal, or a future generation,
the problem space changes, and these break *every* consent-based theory (libertarianism,
contractarianism, consent theory), not only FDK.
**A hypothesis to TEST, not an advance** (the model currently conflates `ownership =
transfer-authority`, which breaks for children): maybe **decouple ownership from the
capacity to alienate** — a 7-year-old *owns* their bike but cannot sell it for a candy; owns
their kidney but cannot sell it. This may decompose into three notions, not two —
`ownership / control / transfer-authority`, or `ownership / decision-authority / liability` —
and into a **competence spectrum** (Fully / Partially / Incompetent → degrees of consent-
validity and transferability), as modern law splits ownership from legal capacity. None of
this is established; the maturity boundary (18? 16? IQ? decision-capacity?) is **not**
derivable from ownership logic and pulls in developmental psychology, cognitive science, and
law.
**Outcomes:** survives (a defended competence-graded ontology) / partial / **collapses (no
consistent definition of standing exists across child + animal + future-generation — itself
a result).** **Architectural consequence:** FDK may have to **invert** to
`Standing → Ownership → Consent → Legitimacy`; if Standing is unsettled, much of the later
layers may need redesign. Cases: `spec/frontiers/standing.md`.

### 2. Authentic Consent
**Question:** *Can authentic consent be operationalized — distinguished from manufactured
consent — without becoming paternalism?* The gate reads `coerced`/`deceived` as attested,
not detected; TikTok, gambling, addiction, lock-in, dark patterns, superhuman persuasion all
reduce to *"was this consent freely formed?"*
**Outcomes:** survives (a detector that does not override the person) / partial / collapses
(any detector is useless or paternalist).
**Risky prediction:** *engineered-consent regimes (company towns, platform lock-in, dopamine
loops) show measurably lower exit/mobility than authentic-consent regimes even at equal
stated satisfaction.* Cases: `spec/frontiers/consent_authenticity.md`.

### 3. Ownership Genesis (the Lockean gap)
**Question:** *Where does the FIRST ownership come from?* FDK reads the graph as given; if
the root is unjust or undefined the graph floats. Whose is the land under Helsinki — and
does it matter if it was taken 300, 800, or 2000 years ago?
**Outcomes:** survives (a defensible original-acquisition rule + a statute of limitations on
rectification) / partial / collapses (no non-arbitrary origin rule, so "legitimate title" is
undefinable). **Risky prediction:** *contested-origin regimes with no rectification mechanism
are more long-run unstable than clean-origin or actively-rectifying ones.*

### 4. Commons / Aggregation
**Question:** *How do non-excludable, multi-owner resources — river, atmosphere, ocean,
spectrum, collective data — acquire legitimate governance?* FDK structurally predicts the
tragedy of the commons; **Ostrom empirically refuted exactly that**, which FDK must answer.
**Outcomes:** survives (a consent-grounded account of Ostrom's design principles) / partial /
collapses (legitimate commons governance is irreducibly non-consensual). **Risky prediction:**
*commons satisfying Ostrom's design principles are both more durable AND more consent-like
than open-access or state-confiscated regimes.* Cases: `spec/frontiers/aggregation.md`.

### 5. AI Legitimacy (the only possibly-new part)
**Question:** *When a non-human agent decides, how is legitimacy defined — and is provenance-
not-utility structurally different from RLHF / preference-learning / utility-maximization?*
**Outcomes:** survives (a real structural distinction with consequences) / partial / collapses
(legitimacy reduces to a constrained utility function). **Risky prediction:** *agents gated on
legitimacy-before-optimization resist a class of reward-hacking/manipulation failures that
welfare-gated agents do not* — testable on real agent benchmarks. Cases: `spec/AI_GOVERNANCE.md`.

## Intellectual position — lineage, rivals, and the line that distinguishes FDK

Honest genealogy, so the project knows whose company it keeps and whom it must answer:

- **Nearest kin:** **Locke** (self-ownership, consent, limited government — and the
  original-acquisition problem FDK independently rediscovered as Program B), **Nozick**
  (probably the closest modern philosopher: near-absolute individual rights, refusal to
  sacrifice the one for the collective good — but Aggregation and Standing unsolved), and
  **Rothbard** (consent/property pushed further — and breaking hardest on children,
  environment, public goods). FDK's current core is, candidly, the intellectual child of
  **Locke + Nozick + Rothbard**.
- **Partial kin:** **Hayek** (spontaneous order, anti-social-engineering — but more
  epistemology/economics than a legitimacy theory) and **Ostrom** (the single most
  important author to engage for Program C — she worked exactly where FDK is weakest).
- **The three rivals FDK must OUT-EXPLAIN, not merely oppose:** **Rawls** (justice prior to
  property — the largest theoretical rival), **Sen** (freedom as real capabilities, not just
  property), and **Ostrom** (commons). They attack precisely the three gaps — Standing,
  Aggregation, Consent-Authenticity — FDK found in itself. Paradigm status requires
  explaining those cases *better* than these three, not just disagreeing.
- **The distinguishing line:** nearly every religious / natural-law tradition (some readings
  of Shia/Sunni Islamic property law, Catholic Social Teaching) shares FDK's anti-usurpation,
  will-as-ownership intuitions but holds **`Duties > Consent`** — some acts are forbidden
  *even with consent*. FDK currently does **not**: it permits consensual acts (consensual
  self-harm, a suicide pact, voluntary servitude short of exit-removal) that natural law
  forbids absolutely. That is a real, falsifiable commitment, not an oversight — and the
  natural-law critic (`spec/EXPERT_REVIEW.md` queue) is where it must be defended or revised.

## The stage-4 question, stated as a falsifiable claim

A candidate explanatory contribution, to be argued or abandoned, **not** assumed:

> *"Modeling legitimacy as a consent-over-boundaries predicate, prior to and independent
> of welfare, explains a class of cases — voluntary-vs-coerced market outcomes, the
> majority-is-not-consent intuition, why 'legal' and 'legitimate' diverge — more cleanly
> than welfarist or contractarian rivals, because it reads provenance rather than outcome."*

This is a thesis to test against Rawls / Nozick / Hayek / Sen / Ostrom on real cases, with
a held-out split and (eventually) real annotators (`external_bench.py` is the apparatus;
`layer11_persona_panel.py` shows the contested cases have *no* convergent human answer, so
the test must be designed around disagreement, not a single key). If it fails this filter,
FDK is internally consistent and externally unremarkable — and we say so.

## The honest bottom line

The biggest obstacle is no longer code, Rust, or Lean. It is showing that FDK explains,
predicts, or solves something its rivals do not. The history of science and philosophy is
full of consistent, beautiful theories that never cleared that wall. FDK has earned the
right to *attempt* it — which already places it ahead of almost every AI-ethics project —
but the attempt is the next decade's work, and most of it is not engineering.

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Engineering: Ali Pourrahim.*
