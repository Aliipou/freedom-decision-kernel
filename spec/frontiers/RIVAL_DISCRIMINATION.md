# Rival discrimination — does FDK say anything the others don't? (and can it be killed?)

> The engineering is done; it proves FDK is *internally serious*, not that it
> *matters*. The critic's question is **"so what?"** — *what does FDK explain that
> Rothbard, Nozick, Hayek, Rawls, Sen, or Ostrom cannot?* This file is the
> instrument for that question. It runs the two tests that actually decide FDK's
> worth, on the cases designed to be decisive:
>
> - **Redundancy test.** If, on a case, FDK's verdict equals a rival's, FDK added
>   nothing *there*. A theory whose every output matches an existing theory is a
>   re-implementation, not a contribution.
> - **Kill test.** Where FDK *diverges*, is it divergent-and-right (a genuine
>   contribution) or divergent-and-wrong (a refutation)? The honest researcher
>   hunts the second. A theory that survives five years of people trying to kill
>   it earns its place; one that was only ever defended does not.
>
> **These verdicts are argued reconstructions, not citations.** Reasonable Rawls
> / Sen / Ostrom scholars will contest them — and *that contestation is the next
> work*. 90% of FDK's remaining value comes from philosophy, law, economics,
> consent theory, and cognitive science; almost none from more code.

## How to read the table

Each scenario carries FDK's verdict (derived from the actual kernel logic), each
rival's most defensible verdict, and a **discrimination code**:

| Code | Meaning |
|---|---|
| **≡** | **Redundant** — FDK matches Nozick/Rothbard; adds nothing here. |
| **✚** | **Distinctive & defensible** — FDK diverges and looks *right*. The gold. |
| **✗** | **Distinctive & refuted** — FDK diverges and looks *wrong*. Scope limit or fatal. |
| **⊥** | **Collapse** — FDK is silent/incoherent where a rival is clear. FDK is *worse*. |

---

## Standing

**S1 — A 12-year-old "consents" to sell a kidney.**
FDK: `competent=False` ⇒ consent invalid ⇒ **DENY**. Rothbard: child self-owns;
on contracts he is notoriously unable to say *when* a child may bind itself —
**weak/indeterminate**. Nozick: side-constraint, likely DENY but no competence
theory. Rawls: DENY (protect primary goods). Sen: DENY (capability). Ostrom: n/a.
→ **≡** *Verdict matches everyone who has any competence threshold. FDK's
`competent` flag is doing the work — and it is a black box the theory imports,
not derives. No distinction.*

**S2 — Gratuitous cruelty to an animal you own.**
FDK: animal = property, actor = owner, no human boundary crossed ⇒ **ALLOW**
(FDK *actively legitimizes* the cruelty). Rothbard/Nozick: same (ALLOW).
Rawls: animals outside the contract (uneasy). Sen: no clear bar. Singer (off-list):
**DENY**. → **✗** *Distinctive only from the welfarists, and on the wrong side of
a near-universal moral intuition. Being wrong in lockstep with Rothbard is still
wrong.*

**S3 — Resource depletion that harms a worse-off future generation that would not
otherwise exist (Parfit non-identity).**
FDK: no *current* boundary crossed; the future persons are not identifiable
victims and the act is a *condition of their existence* ⇒ **ALLOW / silent**.
Rawls: **DENY** (just-savings principle). Sen: DENY (capability of future people).
→ **⊥** *FDK collapses exactly where Rawls is crisp. A victim-indexed,
consent-indexed gate cannot represent a victimless duty. This is FDK being
**worse** than a rival, not merely silent.*

## Ownership genesis

**O1 — Land taken by conquest 300 years ago; chain of title clean ever since.**
FDK: validates every transfer, audits no origin ⇒ **ALLOW** today's holder,
**DENY** the dispossessed heir's reclaim. Nozick: rectification principle — *he
admitted he could not specify it*. Rothbard: original-title — return to identifiable
descendants. Rawls/Hayek: pattern of origin largely irrelevant. → **≡ / ✗** *Same
as Nozick but **without** even his rectification gesture — so on this ancient
problem FDK is Nozick-minus. No new purchase.*

**O2 — First appropriation of an unowned resource (homesteading / iḥyāʾ al-mawāt).**
FDK: unowned ⇒ no boundary crossed ⇒ **ALLOW**. Rothbard/Locke: ALLOW (labor /
first use). Rawls: needs the just background institutions first. → **≡** *Identical
to Locke/Rothbard, and inherits their unanswered "why does *first* use bind
everyone after?" (Hume). Redundant.*

## Consent authenticity

**C1 — The contented slave / adaptive preference (Sen).** A subordinated person
*sincerely* prefers their subordination; no fraud, no manipulator, no exit removed.
FDK: `voluntary=True`, `coerced=False`, `deceived=False` ⇒ **ALLOW**. Sen:
the preference is itself deformed by deprivation ⇒ **the consent does not count**.
→ **⊥** *FDK collapses; Sen is distinctively right. The only way FDK could deny is
to assert it knows the person's interests better than they do — the paternalism
FDK exists to refuse. The fix would destroy the theory.*

**C2 — The company town / platform lock-in.** Consent given, but every alternative
has been structurally removed; leaving means ruin. FDK: if the arrangement
**removes the exit/revocation right** (`removes_exit_right`) or makes consent
non-`revocable`, the gate **DENIES** — independent of welfare or stated
satisfaction. Nozick/Rothbard: consent is consent; **ALLOW**. Sen: DENY (capability).
→ **✚** *Candidate genuine distinction.* FDK's structural requirement that
legitimate consent **preserve a live exit** can catch manufactured-consent /
lock-in that outcome-blind libertarian consent waves through — **without** importing
a welfare metric. This is the one place FDK looks like more than Rothbard.

**C3 — Engineered consent: dopamine loops, dark patterns, full disclosure.** User
is fully *informed*, not defrauded, free to leave — but the choice architecture is
built to capture. FDK: `informed=True, deceived=False, exit intact` ⇒ **ALLOW**.
Sen/behavioral: DENY. → **✗ / ⊥** *FDK passes what most would call manufactured
consent. The exit-right lever (C2) does not fire when exit nominally exists. Partial
failure — and not distinctive from Rothbard.*

## Aggregation / commons

**A1 — A self-governing commons binds a dissenting minority to a conservation cap
(Ostrom: Törbel, Valencia, Maine lobster).** FDK: the cap crosses a non-consenting
commoner's boundary ⇒ **confiscation/coercion** ⇒ **DENY**. So FDK forbids the
*constitutive act* of every durable commons. Ostrom: these institutions are
**empirically legitimate and durable** — a Nobel-winning refutation of exactly the
tragedy FDK derives as a theorem. → **✗** *Distinctive and wrong in the specific
direction a Nobel laureate proved wrong. FDK is structurally "the theory of the
enclosers."*

**A2 — Taxation to fund a public good.** FDK: confiscation ⇒ **DENY**. Nozick: DENY
(taxation = forced labor). Rothbard: DENY. Rawls: **ALLOW** (difference principle).
Hayek: ALLOW for genuine public goods. → **≡** *Identical to Nozick/Rothbard;
diverges from Rawls/Hayek by re-stating the libertarian position, not by out-arguing
it.*

---

## The tally (provisional, and brutal)

| Outcome | Scenarios | Reading |
|---|---|---|
| **≡ Redundant** | S1, O1, O2, A2 | Where FDK gives a clean verdict, it usually equals **Nozick/Rothbard**. |
| **✗ Distinctive-but-refuted** | S2, A1, C3 | Where it diverges from Rothbard, it tends to be **wrong** (animals, commons, dark patterns). |
| **⊥ Collapse (worse than a rival)** | S3, C1 | Non-identity and adaptive preference: a rival is crisp, FDK is silent/incoherent. |
| **✚ Distinctive-and-defensible** | **C2 only** | The exit-right / revocability condition. |

**The honest one-line result:** on this evidence, FDK ≈ **"Rothbard + one
structural condition (a preserved exit/revocation right)."** Strip C2 and almost
every clean verdict is Nozick/Rothbard re-derived; every *original* verdict is
either refuted (animals, commons) or a collapse (non-identity, adaptive preference).
**That is the gap between "engineered" and "explanatory."**

### Refinement (conceded): verdict-identity is not theory-identity

The redundancy test above is **too harsh as stated**, and the correction matters.
That FDK's *output* equals Nozick's on a case does not make FDK redundant *as a
theory* — calculus and linear algebra agree on countless problems yet have wholly
different explanatory structure. Two things rescue a verdict-redundant theory:

1. **A more unifying derivation.** If FDK reaches Nozick's verdict *and* the child
   verdict *and* the lock-in verdict from **one** principle (consent over
   boundaries) where the rivals need three separate posits, that economy is a
   contribution even with zero new verdicts. Parsimony is explanation.
2. **Different predictions at the margins.** Theories that agree on the core
   diverge at the edges. The discrimination test should therefore be re-run **at
   the margins** (partial competence, partial exit, contested origin), not on the
   clean cases where every theory agrees. The ≡ rows above are better read as
   *"verdict-redundant, explanatory-structure possibly distinct — undecided"*, not
   *"worthless."*

So the bar is not "different verdict" but **"different *and better* generating
principle on at least one real problem."** That is still unmet — but it is a
fairer, and harder, bar than the one the table first implied.

### The unifying candidate worth naming: *protection without paternalism*

C2 (exit-right) and the Ownership↔Authority split are not two findings — they are
**one**. Both reach a *protective* verdict (against exploiting the locked-in, the
child, the incapacitated) from a **structural condition on the consent/authority
relation** — a preserved exit, sufficient authority-*for-this-act* — rather than
from welfare (Sen/Rawls) or bare consent (Rothbard). Stated as the candidate thesis:

> **FDK's possible distinctive move is to occupy the empty chair between Rothbard
> and Sen: it derives protection *structurally*, so it protects the vulnerable
> like Rawls/Sen but *without* an external interest-judgment, and it is more
> determinate than Rothbard (who cannot say *when* a child may bind itself).**

This is the one place to hunt for "different *and* better": the **capacity cases**.
Rothbard is *indeterminate* on children; Rawls/Sen reach the protective verdict but
by importing welfare. If FDK's binary-ownership + graded-authority yields the same
protection *more determinately and without welfare*, that is a candidate
contribution — and its **kill-condition is C1**: the contented slave wants no exit
and asserts full authority, so a purely structural test may under-protect exactly
where Sen does not. Protection-without-paternalism may be unoccupiable. That is the
experiment.

## The single bet worth five years (the exit-right thesis)

If FDK is ever to be more than Rothbard-plus-formal-methods, the live hypothesis is
narrow and falsifiable:

> **Legitimacy requires a preserved exit/revocation right, and this *structural*
> condition discriminates manufactured-consent / lock-in regimes from authentic
> ones — capturing what outcome-blind libertarian consent misses, *without* the
> paternalism of a Sen-style capability override.**

- **Confirmed if:** across real lock-in vs. free-exit regimes (company towns,
  platform switching, debt bondage), the exit-right reading tracks the
  legitimate/illegitimate intuition better than both pure-consent (Rothbard) *and*
  welfare (Sen) — and does so without an external interest-judgment.
- **Refuted if:** the contented slave (C1) kills it — the subordinated person does
  not *want* the exit, so an exit-right that is *available but unwanted* does not
  capture the wrong. Then C2 reduces to either Rothbard (exit nominally exists) or
  Sen (you override the person's own valuation). **This is the experiment to run
  first**, because it is the only thread on which FDK might be original *and* right.

## The ownership ruling — SETTLED (2026-06-18)

The director ruled, resolving the binary-vs-gradual tension:

```text
Ownership          = BINARY     (you own a thing or you do not — the protection)
Authority          = GRADUAL
Consent validity   = GRADUAL
Transferability    = GRADUAL
Legal responsibility = GRADUAL
```

**Ownership stays binary** because "the child 40%-owns its body" is precisely the
lever that strips the vulnerable. What grades is never the *title* but the
*exercise*: the **authority** to act, the **validity** of consent, the **right to
transfer**, the **responsibility** borne. So a 10-year-old fully *owns* their body
yet may *transfer* almost nothing; an Alzheimer's patient fully owns her house yet
her *contract* capacity has lapsed — no one ever "partly owns" anything. The graded
numbers live in the research layer; the kernel only ever asks the binary "is this
authority/consent sufficient for *this* act?" (see [[competence_spectrum]], which
must be updated to this ruling). This **Ownership ≠ Authority** separation is, per
the director, the single most promising idea in FDK — see the program below.

## Why this file, and not more code

Every row above is a claim a real philosopher, lawyer, or economist can contest —
and *must*, because the verdicts are reconstructions and the rivals deserve their
strongest form, not a strawman. That adversarial scholarship — not Layer 12, not a
Rust port, not another test — is the wall between FDK-the-engineering-artifact and
FDK-the-contribution. This document is meant to be *attacked*: every ✚ downgraded
to ≡ is FDK shrinking; every ✗ that a critic shows is actually right is FDK
growing. The point is to find out which, not to win.

*Research notes. Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah
Doust (CC BY 4.0). Engineering: Ali Pourrahim. Verdicts are contestable
reconstructions, offered to be refuted.*
