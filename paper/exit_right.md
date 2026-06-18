# Consent Without Exit: Is a Revocation Right a Necessary Condition of Legitimate Consent?

*A standalone working paper on the one axis where the Freedom Decision Kernel might
be distinctive. Engineering context is deliberately omitted: 100% test coverage,
machine-checked proofs, and a Rust kernel prove only that **if** the axiom is true
the system is consistent — they are silent on whether the axiom is true. This paper
asks only the second question.*

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Draft for hostile review. Every claim is offered to be refuted; the verdict reached
below is, deliberately, mostly negative.*

---

## Abstract

A consent-based theory of legitimacy says an act is permissible iff every boundary
it crosses carries the valid consent of that boundary's owner. The interesting
question is then *which* consents are valid. This paper isolates and stress-tests a
single proposed validity condition — **the Revocation Condition (RC): consent is
valid only if it preserves a real, exercisable right to withdraw (an "exit right")**
— and asks whether RC does any work that existing theories do not already do. The
strategy is adversarial: before any defence, RC is run against three cases designed
to break it — the contented slave, the contented addict, the contented cult member —
in which consent is sincere, competent, and uncoerced, and an exit is available but
*unwanted*. The finding is mostly negative and stated plainly: **RC genuinely
discriminates the cases where exit is *foreclosed* (lifetime-slavery contracts,
company towns, platform lock-in), but it cannot reach the three contented cases,
where the defect has been relocated from the availability of exit into the agent's
not-wanting it.** There, RC must either override the sincere will — importing the
very interest-judgment it was meant to avoid (collapsing into Sen) — or accept the
arrangement (collapsing into Rothbard). Worse for any claim of novelty, the
foreclosure cases that RC *does* handle are already well covered: by Mill's argument
against alienating one's liberty, by Hirschman's analysis of exit, and most exactly
by **Pettit's republican freedom as non-domination**, which arguably already *is*
the exit-right thesis, more fully developed. RC's only candidate originality is a
narrow structural claim — that the inalienability of the exit right is *constitutive
of* consent rather than justified by welfare or by a political theory of liberty —
and even that claim must survive the adaptive-preference objection it currently does
not. The honest verdict: **a genuine but small and probably already-occupied
territory, contingent on one unsolved problem.** A falsifiable empirical prediction
is offered so the thesis can lose in the world, not only on paper.

---

## 1. The question, and why it is the only one that matters here

Consider the family of theories on which legitimacy is *consent over boundaries*:
an act `a` is legitimate iff, for every property boundary `b` that `a` crosses,
the owner of `b` has given valid consent to that crossing. Call any such theory a
**consent-legitimacy** theory. Libertarian rights theory (Rothbard, Nozick) is the
paradigm case; the Freedom Decision Kernel (FDK) is a recent formalised instance.

Such a theory's entire normative content lives in the word **valid**. If "valid"
means only "sincerely uttered by a competent adult," the theory is a notational
variant of Rothbardian libertarianism and inherits all its verdicts — including the
ones most people find monstrous (a starving person "validly" sells a kidney; a
desperate worker "validly" accepts indenture). If "valid" instead imports a
substantive account of when a person's *real interests* are served, the theory
becomes a welfarist or perfectionist theory wearing consent's clothes, and loses
the anti-paternalist character that motivated it. The space between these — a
condition on validity that protects the vulnerable *without* an interest-judgment —
is the only place a consent-legitimacy theory can say something its libertarian and
welfarist rivals do not. This paper tests one candidate occupant of that space.

The axis is deliberately narrow:

> **Freedom → Consent → Authenticity → Exit Rights → Adaptive Preference**

Everything else FDK contains (standing for animals and future people, the genesis of
original title, the aggregation of persons into firms and states) is set aside. On
each of those, a companion analysis finds FDK either redundant with Nozick/Rothbard
or refuted (by Parfit on non-identity, by Ostrom on the commons). If FDK is
distinctive *and right* anywhere, it is here, or nowhere.

## 2. The thesis, stated so that it can be killed

**The Revocation Condition (RC).** A consent token `C` by a person `P` authorising an
ongoing arrangement `A` is *valid* only if, throughout `A`, `P` retains a real,
exercisable right to withdraw `C` and thereby end `P`'s future obligations under `A`.

Three clarifications fix RC's content and pre-empt cheap refutations.

1. **Exit-right ≠ exit-taken.** RC does not require that `P` *leave*; it requires
   that `P` *could*. A worker who stays at a job she is free to quit consents
   validly; the staying is consistent with RC. This is the distinction on which the
   whole thesis turns, and §3 is the test of whether it can bear the weight.

2. **"Real, exercisable" is cost-sensitive — and this is the program's open wound.**
   An exit that is nominally available but whose exercise means starvation, ruin, or
   statelessness is not a real exit. But *how much* cost defeats an exit? Any answer
   threatens to smuggle a welfare baseline back in (an exit is "too costly" relative
   to what the person needs — which is a claim about needs, not consent). Call this
   **Node G**, the exit-cost threshold. RC is *schematic* until G is closed, and G
   may not be closeable without abandoning RC's anti-welfarist point. This paper does
   not close G; it flags every place the argument leans on it.

3. **RC is offered as constitutive, not instrumental.** The interesting version of RC
   does not say "preserve exit because people are better off with it" (that is Mill
   and Sen). It says: *to consent is to exercise a standing authority over a
   boundary; an arrangement that extinguishes the authority to withdraw consent is
   not a use of that authority but its destruction, which the authority cannot
   license.* The exit right is inalienable because alienating it is conceptually a
   misuse of the very power consent is. Whether this "constitutive" reading is a real
   discovery or a verbal trick is, ultimately, the question on which novelty depends
   (§5–§6).

The target RC aims at is the **empty chair**: a verdict-structure that protects the
vulnerable like Rawls and Sen but issues from a *structural* condition on consent
rather than from a metric of well-being or a theory of the good — *protection
without paternalism*.

## 3. Three deaths before any defence

A theory should be attacked at its strongest-looking point before it is defended
anywhere. RC looks strongest on lock-in (§4); so we begin where it looks weakest.
Each case below is built to satisfy RC's letter while violating its spirit: consent
is sincere, competent, informed, uncoerced, and **a real exit exists** — the agent
simply does not want it. If RC cannot handle these, its protective verdicts in the
lock-in cases are bought entirely by the foreclosure of exit, and RC says nothing
about authenticity that bare consent does not.

### 3.1 The contented slave

`P` signs into lifetime servitude to a master and, years later, sincerely and
reflectively affirms the arrangement: she identifies with her subordination, would
re-sign, and — crucially for RC — *a real exit exists*: a standing legal right to
manumission she knows about, can afford, and declines to take. There is no fraud, no
present coercion, no removed alternative.

Does RC condemn this? Two readings, both fatal to novelty:

- **Foreclosure reading.** If the *contract itself* strips the manumission right —
  if the servitude is genuinely irrevocable — then RC condemns it (no exit
  preserved). But then this is not the contented-slave case; it is the lock-in case
  of §4 with extra colour, and RC's verdict comes from the foreclosure, not from
  anything about the slave's contentment. The hard case is the one where exit is
  *retained and unwanted*.
- **Retained-exit reading.** If the manumission right persists and `P` declines it,
  RC's letter is satisfied — exit is preserved — so **RC must say the arrangement is
  legitimate (ALLOW).** Most readers judge it illegitimate. To reach that judgment,
  RC would have to say the retained exit is somehow not "real" *for her* because her
  will has been deformed — which is precisely Sen's adaptive-preference move, an
  interest-judgment over her sincere endorsement. RC then *is* Sen, and the
  "without paternalism" claim is lost.

The classical literature already lives here. **Mill** (*On Liberty*, ch. 5) argues a
person may not sell himself into slavery, on the ground that "the principle of
freedom cannot require that he should be free not to be free" — an early statement of
an inalienability-of-liberty condition. But Mill's ground is *future freedom and
well-being*, a welfarist/teleological justification RC was trying to avoid.
**Rothbard** reaches a similar verdict by a different route — the will is inalienable,
so a slavery *contract* is unenforceable even if labour-service contracts are — and
**Nozick** notoriously goes the other way, holding that a free system must permit an
individual to sell himself into slavery. RC's verdict on the *foreclosure* version
coincides with Mill/Rothbard; on the *retained-exit* version it either coincides with
Nozick (ALLOW) or becomes Sen (DENY by interest-judgment). In none of the three does
RC occupy new ground.

### 3.2 The contented addict

`P` is addicted but *endorses* the addiction at the second order: asked whether she
wishes she did not want the drug, she says no; she has reflectively incorporated the
desire into her conception of a good life (Frankfurt's "wanton" inverted into a
willing addict). Exit — treatment, cessation — is available and refused.

RC has almost no grip here, because there is no *arrangement with a counterparty* who
removed an exit; the "lock-in" is internal. If we stretch "exit right" to mean the
psychological capacity to revise one's desires, RC collapses into the autonomy
literature it has not engaged: **Frankfurt** on second-order desires, **Gerald
Dworkin** on procedural autonomy as higher-order endorsement, **Christman** on the
historical/process conditions for autonomous preferences. On the willing-addict case,
that literature is itself divided and unresolved after fifty years; RC adds no new
instrument, and if it sides with "the endorsement is authentic, so permit," it is
Rothbard, while if it sides with "the desire was engineered, so deny," it must
specify the engineering — which is §3.3, and again not about exit.

### 3.3 The contented cult member

`P` was raised in or recruited into a high-control group; her present preferences
were *manufactured* by the group, yet are now sincerely her own; she can leave (the
door is unlocked, she has money, relatives outside) and does not want to. Here the
intuition that the arrangement is illegitimate is strongest, and RC is at its most
exposed: exit is real and unwanted, *and* the preferences' history is tainted.

This is the case that most tempts RC toward a genuine move: shift the condition from
*exit preserved now* to **exit preserved during preference-formation** — the
arrangement is illegitimate not because she cannot leave now but because the process
that produced her not-wanting-to-leave foreclosed her exit *then*. This is a real and
interesting idea. But notice what it costs: it converts RC from a clean structural
condition on present consent into a **historical-process condition on preference
formation** — which is exactly the terrain of the adaptive-preference and "manufactured
autonomy" literature (Elster's *Sour Grapes*; Nussbaum and Khader on adaptive
preferences; Pettit and the republicans on domination through preference-shaping).
RC does not solve that problem; it *joins* it, decades late, with no new tool. And the
move reintroduces the welfare/interest baseline through the back door: to say the
formative process "foreclosed exit" is to say it prevented her from coming to want
what she had reason to want — a claim about her reasons, not her consent.

### 3.4 What the three deaths show

The three cases share a structure: **sincere consent + real-but-unwanted exit.** RC
was built to need only the *availability* of exit, precisely to avoid judging what
people *want*. The contented cases are engineered to sit past availability, in the
wanting. There, RC has no structural residue to grip. It must either (i) declare the
available exit "not real for her" — an interest-judgment over her sincere will, which
is Sen and abandons the anti-paternalist charter; or (ii) permit the arrangement,
which is Rothbard. Call this **Node K** (for the *kill*). On current resources RC does
not pass Node K, and Node K is not a marginal case — it is the entire category of
manufactured, internalised consent, which is where authenticity questions actually
bite.

## 4. What RC *does* explain (the surviving core)

The three deaths are not the whole story, and honesty cuts both ways. RC earns a
genuine, if narrow, verdict on a different family of cases — those where the
arrangement **forecloses** exit rather than leaving it available-but-unwanted:

- **Voluntary lifetime-slavery contracts** (the irrevocable kind): RC denies
  enforceability structurally, because the contract purports to extinguish the very
  authority by which it was signed.
- **Company towns and debt bondage**: where wages are paid in scrip redeemable only
  on-site, or debt is engineered to grow faster than it can be repaid, exit is
  foreclosed in fact though not in form; RC denies legitimacy where bare consent
  (the worker "agreed") would permit.
- **Platform and data lock-in**: where switching costs, non-portable data, and
  network effects make leaving ruinous, RC locates the illegitimacy in the
  foreclosure, not in any welfare comparison.

On these, RC reaches the protective verdict that Rawls and Sen reach, but *without* a
welfare metric and *more determinately than Rothbard*, who must either permit them
(bare consent) or import inalienability as an unexplained exception. The candidate
contribution, stated at its most generous, is this: **the inalienability of certain
arrangements is derived from the structure of consent (you cannot consent away the
standing to withdraw consent) rather than posited as a welfare exception or a
political value.** That derivation, *if* it holds, is the only thing in FDK that is
both distinctive and plausibly correct.

The fragility is equally clear. Every verdict in this section runs through "exit is
foreclosed *in fact*," which is **Node G** — and the moment we specify how costly an
exit must be to count as foreclosed, we risk re-importing the welfare baseline whose
absence was the whole point. RC's surviving core is thus pinned between two unsolved
nodes: G (which threatens to make it welfarist) and K (which threatens to make it
either welfarist or libertarian). It survives only in the gap between them, and the
gap may be empty.

## 5. Has this already been said? (The literature, honestly)

The greatest risk to a self-taught theory is not error but *re-invention*: building,
with great effort, a house someone else finished thirty years ago. On RC the risk is
acute, and the most dangerous neighbour is one the project had not named.

- **Mill, inalienability of liberty.** *On Liberty* already grounds a no-slavery
  condition in the idea that freedom cannot license its own destruction. RC's
  "constitutive" reading is a structural restatement of Mill's point; the difference
  (Mill grounds it in future well-being, RC in the logic of consent) is real but
  thin, and a hostile reader will ask whether it is a difference at all.

- **Hirschman, *Exit, Voice, and Loyalty* (1970).** The locus classicus of exit as a
  disciplining mechanism. Hirschman is positive-economic, not a theory of legitimacy,
  so RC is not *reducible* to him — but anyone who reads RC will hear Hirschman, and
  the burden is on RC to show that "exit as legitimacy condition" adds to "exit as
  accountability mechanism."

- **Pettit and Skinner, republican freedom as non-domination.** *This is the
  decisive neighbour, and it was missing from the project's own list of rivals.*
  Republican freedom (Pettit, *Republicanism*, 1997; Skinner) defines unfreedom not
  as interference but as *domination* — being subject to another's arbitrary power,
  *even if that power is never exercised and even if one is content.* The remedy is
  not welfare but *secured standing*: institutionalised powers of exit and contestation
  that make the relationship non-arbitrary. Notice that this is, almost exactly, RC's
  "exit right preserved," generalised and given a worked political theory — and,
  critically, **republicanism already handles the contented cases that kill RC**: the
  contented slave is *dominated* (subject to arbitrary power) however content she is,
  because domination is a modal property of the relationship, not of her preferences.
  Where RC stalls at Node K because it indexes to present consent, non-domination
  indexes to the *structure of power*, and so condemns the contented slave without an
  interest-judgment — achieving the very "protection without paternalism" RC was
  reaching for, and achieving it where RC fails. The honest conclusion is stark:
  **the most defensible version of RC may already exist as a special case of
  non-domination, which does the job better.** If RC has a future, it must show what
  it adds to Pettit — and "we formalised it and put it in front of an AI authorisation
  gate" is an engineering answer, not a philosophical one.

- **Sen, Elster, Nussbaum, Khader — adaptive preferences.** The entire Node-K problem
  is a forty-year live research programme (Sen's capability critique of utility;
  Elster's *Sour Grapes*; Nussbaum's and Khader's work on adaptive preferences and
  empowerment). RC does not advance it; it *inherits* it, and inherits it on the
  unfavourable side, since RC's structural austerity is exactly what leaves it
  unable to say why an adapted preference is defective without judging the person's
  good.

- **Gerald Dworkin and Joseph Raz — autonomy.** Dworkin's *The Theory and Practice of
  Autonomy* (procedural, content-neutral, second-order endorsement) is the natural
  home for the contented-addict case and is more developed than anything RC offers.
  Raz's *The Morality of Freedom* grounds autonomy in an *adequate range of valuable
  options* — which is closer to Sen than to RC and is openly **perfectionist** (the
  options must be *valuable*), a commitment RC rejects. The tension is instructive:
  to handle the cases RC fails, the autonomy literature reaches for either process
  conditions (Dworkin) or option-value (Raz), and both are moves RC has forsworn.

- **Wertheimer — coercion and exploitation.** Wertheimer's moralised-baseline analysis
  of coercion (*Coercion*, 1987) and his account of exploitation (*Exploitation*,
  1996) are the state of the art on "consent under pressure." RC's company-town and
  debt-bondage verdicts are, in his terms, judgments about a coerced or exploitative
  baseline — and his framework already supplies the apparatus RC's Node G is missing
  (when is a "choice" set so structured that consent within it is invalid). RC risks
  being a less-developed re-statement.

The literature verdict is therefore not "RC is wrong" but something more deflating:
**RC's defensible content is largely already present** — in Mill on inalienable
liberty, in Hirschman on exit, in Wertheimer on coerced baselines, and above all in
Pettit on non-domination — and RC's *original* sliver (the constitutive-of-consent
derivation) is exactly the part that has not been shown to survive Node K, where
non-domination already succeeds.

## 6. The honest verdict

Three outcomes were admissible from the start: RC survives as a contribution, RC
partially survives, RC collapses. The evidence supports the middle, sliding toward
the third.

- **What survives.** RC gives clean, welfare-free, determinate verdicts on the
  *foreclosure* cases (irrevocable servitude, company towns, lock-in), and its
  constitutive reading — inalienability of the exit right as internal to the logic of
  consent — is a genuine candidate idea, not obviously identical to its welfarist and
  perfectionist neighbours.

- **What does not.** RC fails Node K (the three contented cases) without becoming Sen
  or Rothbard; it is schematic until Node G is closed, and closing G risks welfarism;
  and its surviving core appears to be a special, less-developed case of Pettit's
  non-domination, which handles the very cases RC cannot. The project's earlier
  internal estimate — "distinctiveness from Nozick/Rothbard ≈ 4/10; solves what rivals
  cannot ≈ 3/10" — is, if anything, generous once non-domination is on the table.

- **The success criterion, applied.** The only criterion that matters is whether an
  independent, hostile scholar — a Rawlsian, a capability theorist, a contract-law or
  autonomy specialist — would say after reading this: *"the exit-right condition
  explains something existing theories do not."* On the present argument the honest
  prediction is **no**: they would point to Pettit for the structural protection, to
  Wertheimer for the coerced baseline, to Sen/Khader for the adapted preference, and
  ask what remains. The candidate that *could* still earn a "yes" is narrow and
  specific: **a proof that the exit right's inalienability is derivable from the
  formal structure of consent alone, owing nothing to well-being, option-value, or a
  political theory of liberty — and a demonstration that this derivation handles a
  contented case that non-domination handles only by appeal to its own substantive
  conception of arbitrariness.** That is a hard, precise target. It is also the
  *only* one worth the next five years.

This is not a refutation of FDK as engineering or as a policy product; the
authorisation use-case (deny an AI agent an action whose consent has no preserved
exit) is sound and shippable regardless. It is a refutation of the easy hope that the
system's formal seriousness carries philosophical novelty with it. It does not.

## 7. A prediction, so the thesis can lose in the world

Philosophy that only re-describes cases is unfalsifiable. RC implies a worldly
prediction, stated to be refuted:

> **Across arrangements matched on stated satisfaction, those that are *exit-poor*
> (company towns, debt bondage, high-lock-in platforms, closed religious communities)
> will exhibit measurably lower realised mobility and higher coerced-stay than
> *exit-rich* arrangements — and it is the exit gap, not the satisfaction level, that
> tracks third parties' legitimacy judgments.**
>
> **Refuted if** exit-poor and exit-rich arrangements are behaviourally
> indistinguishable at equal stated satisfaction, or if legitimacy judgments track
> satisfaction rather than the exit gap. Then "exit" has no independent signature and
> RC is redescribing satisfaction.

Data domains: labour mobility and quit rates across high- vs low-lock-in markets;
account-deletion and switching rates under portable vs non-portable data regimes;
out-migration from company towns vs comparable free-labour towns; disaffiliation
rates from high-control vs low-control religious groups. The prediction's most
dangerous case is again Node K: a closed community with high satisfaction *and* low
realised exit, where RC's prediction and the contented-member intuition pull apart.

## 8. The kill condition, stated for the record

> **If, for the contented slave, the contented willing-addict, and the
> contented cult member, no structural condition on consent (as opposed to a
> judgment about the agent's interests or the value of her options) yields the
> intuitively correct verdict, then RC reduces to either Rothbard (permit) or Sen
> (deny by interest-judgment), and the Exit-Right thesis is not a distinctive
> contribution to the theory of legitimate consent.**

On the argument of §3 and §5, that antecedent currently holds. The thesis is alive
only insofar as the narrow target of §6 (a consent-internal derivation that beats
non-domination on a contented case) can be hit. Until then, the intellectually honest
description of FDK's distinctiveness is: **a careful formalisation of a libertarian
consent theory, plus one promising-but-unproven structural condition that, on present
evidence, is either redundant with non-domination or defeated by adaptive
preference.**

## 9. What an honest reviewer should be asked to do

Send this to people who want it to fail: a Pettit-school republican, a Sen/Khader
capability theorist, a Wertheimer-style contract-law scholar, a Dworkin/Christman
autonomy theorist. Ask each one question: *Does the Revocation Condition, on its
constitutive reading, explain any case that your framework does not already explain
at least as well?* If every one says no, the project has learned something true and
valuable — that its strategic asset is a product, not a paradigm — and should say so.
If even one says "yes, the contented case at the boundary of non-domination," then,
for the first time, there is a thread worth pulling.

---

### References (works engaged; positions are the author's reconstructions, not quotations)

- J. S. Mill, *On Liberty* (1859), esp. ch. 5 on the limits of voluntary self-binding.
- R. Nozick, *Anarchy, State, and Utopia* (1974): entitlement theory; permission of voluntary slavery.
- M. Rothbard, *The Ethics of Liberty* (1982): inalienability of the will; title-transfer theory.
- J. Rawls, *A Theory of Justice* (1971): the basic structure; the priority of liberty.
- A. Sen, "Equality of What?" (1980), *Development as Freedom* (1999): capabilities; adaptive preference.
- J. Elster, *Sour Grapes* (1983): adaptive preference formation.
- M. Nussbaum, *Women and Human Development* (2000); S. Khader, *Adaptive Preferences and Women's Empowerment* (2011).
- G. Dworkin, *The Theory and Practice of Autonomy* (1988): procedural, content-neutral autonomy.
- J. Raz, *The Morality of Freedom* (1986): autonomy as an adequate range of valuable options (perfectionist).
- P. Pettit, *Republicanism* (1997); Q. Skinner, *Liberty before Liberalism* (1998): freedom as non-domination.
- A. O. Hirschman, *Exit, Voice, and Loyalty* (1970).
- A. Wertheimer, *Coercion* (1987); *Exploitation* (1996).
- H. Frankfurt, "Freedom of the Will and the Concept of a Person" (1971): second-order desires.

*Draft for hostile review. Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali
Jannat Khah Doust (CC BY 4.0). Engineering context: Ali Pourrahim. The verdict is
deliberately negative; the point is to find out whether it should be.*
