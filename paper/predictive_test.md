# Is the Reversibility Index New? Incremental Predictive Validity vs. the Lock-In Literature

*The philosophical contest is closed (H1 collapsed). H2 — "FDK measures reversibility" —
is not yet a theory; it is a re-description. This paper concedes the three weaknesses that
make it so, audits whether "reversibility" is even new (it is mostly not — including a
1974 result that may already *be* H2), and converts H2 into a falsifiable claim with a
named dependent variable: **does FDK's reversibility score have incremental predictive
validity over the existing lock-in / optionality / path-dependence indices?** That is the
one question left, and argument cannot settle it — only data can.*

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Draft for hostile review.*

---

## 0. Three conceded weaknesses (the critique is correct)

1. **Reversibility is probably not new.** "FDK measures reversibility" invites the
   referee's immediate reply: *don't optionality, switching costs, path dependence,
   resilience, flexibility, and real options already do that?* FDK may have fallen out of
   *Freedom Theory* straight into *Existing Lock-In Literature* — not by being wrong, but by
   not being novel.
2. **The 2×2 is necessary, not sufficient.** Populating all four corners of
   legitimacy×reversibility shows only that reversibility is **not collinear** with
   legitimacy. It does **not** show reversibility is a *fundamental, independent* variable —
   cost, time, complexity, and scale would each produce the same 2×2 against legitimacy.
   Non-collinearity is table stakes, not a result. I overstated it.
3. **No dependent variable ⇒ no theory.** A science says *"if reversibility is low, then **X**
   occurs."* H2 currently says only *"FDK measures reversibility."* Without a measurable X,
   it is a re-description wearing a lab coat.

All three are right, and together they set the only bar that now matters.

## 1. The corrected standard: incremental predictive validity

A variable earns independent status not by a 2×2 but by **predicting a real outcome better
than the existing variables, after controlling for them.** Formally: regress an outcome X on
the established predictors (switching-cost indices, concentration, path-dependence proxies,
quasi-option value); add FDK-reversibility; does it buy a robust **ΔR² > 0**? If not, FDK is
*absorbed* — a rename of variables already in use. If yes, it is a genuinely new instrument.
Everything below serves this test.

## 2. The novelty audit — is "reversibility" already measured? (mostly yes)

Honest positioning against each neighbour:

- **Quasi-option value — Arrow & Fisher (1974); Henry (1974). The most dangerous neighbour.**
  Quasi-option value is *literally the value of not making an irreversible decision under
  uncertainty* — the worth of keeping options open. This is H2's core idea, formalised in
  environmental economics **fifty years ago**, and generalised by **Dixit & Pindyck,
  *Investment Under Uncertainty* (1994)** into real-options theory. If FDK's "reversibility"
  is quasi-option value re-discovered, that is the *exact* analogue of the Pettit hit in
  philosophy: a precise, named, prior occupant of the chair.
- **Switching costs / lock-in (IO economics; Farrell & Klemperer).** Measures the cost to
  change supplier/standard; firm- and market-level. Large overlap with FDK's "cost of exit."
- **Path dependence (David's QWERTY; Arthur; Pierson).** Increasing-returns lock-in; an
  *ex-post, historical, system-level* account. FDK is *ex-ante and per-action* — a real but
  narrow difference of timing and grain.
- **Resilience / robustness (Holling; engineering).** Capacity to absorb shocks and recover;
  related to but distinct from reversibility (recover-from-shock ≠ undo-a-specific-change).
- **Antifragility / optionality (Taleb).** Informal kin of real options.

**Audit verdict:** reversibility-as-a-variable is **thoroughly pre-existing**, and
quasi-option value is a near-exact prior formalisation. FDK's *only* candidate margin is a
**specific operationalisation**: a *computable, consent/ownership-graph-indexed,
per-boundary-crossing, ex-ante* reversibility score usable as an authorisation gate — i.e.
reversibility measured at the **micro level of an individual action with named owners**,
where quasi-option value and switching costs operate at the **macro level of assets,
markets, and institutions**. That micro/consent-indexed operationalisation *may* be
unoccupied. It may also be nothing more than "switching-cost analysis applied to a consent
graph." **Unsettled — and settled only by §3, not by more argument.**

## 3. The decisive experiment (what converts H2 from re-description to theory)

Name the dependent variable, the controls, and the discriminating result.

**Dependent variables (measurable X — pick per domain):**
- *Digital:* protocol/platform abandonment or collapse; user churn after lock-in events.
- *Political:* constitutional-crisis incidence; reform-blockage; secession/breakup events.
- *Economic:* currency-union exit-stress and breakups; firm/standard failure under shock.
- *Social:* institutional dissolution; mass-disaffiliation; revolt.

**Controls (the established predictors FDK must beat):** switching-cost index; market
concentration (HHI); path-dependence proxies (age, increasing-returns intensity);
quasi-option-value / real-options proxies; size and wealth.

**The FDK predictor:** the consent-indexed, per-boundary reversibility score (to be defined
precisely — see §4).

**Discriminating hypothesis (H2, finally a theory):**
> *FDK-reversibility has robust incremental predictive validity (ΔR² > 0, out-of-sample,
> across domains) for these failure/lock-in outcomes, after controlling for switching costs,
> concentration, path-dependence, and quasi-option value.*
>
> **Absorbed if** ΔR² ≈ 0 — FDK predicts nothing the existing indices don't → it is a
> **rename**, and should be retired into that literature with thanks. **Alive if** ΔR² > 0
> robustly — then, for the first time, FDK is a genuinely new, useful micro-level instrument,
> and the interesting claim is finally on the table.

This is the entire remaining question. Note what it is **not**: it is not philosophy, not a
proof, not another case. It is fieldwork — building the metric and running it against real
corpora — and **it cannot be done from the armchair**, which is the honest boundary of what
this whole analytic program can reach.

## 4. The one constructive prerequisite: define the metric (the only thing left to *build*)

Before the experiment can run, FDK-reversibility must be a *number*, not a verdict. The
minimal definition the program already implies: for an action `a` over a consent/ownership
graph, score each boundary it crosses by **(i)** whether the crossing is revocable, **(ii)**
by whom (the affected owner, or only the counterparty), **(iii)** at what cost, and **(iv)**
within what time — then aggregate to a per-action reversibility index in [0,1]. *That* object
is computable, is genuinely micro-level and consent-indexed (its candidate margin over
macro quasi-option value), and is the single artifact worth building next — not as
philosophy, but as the measurement instrument whose predictive validity §3 tests. It is also
the natural extension of the existing engineering kernel (which already walks a consent graph
and checks revocability), so it is buildable, and it is the *only* "more code" this project
should now write — and only because it is the apparatus of the experiment, not another layer.

## 5. The honest probability table (matching the referee's)

| Claim | Probability |
|---|---|
| FDK is a new paradigm of freedom | **low** |
| FDK is a re-statement of Pettit | **medium** |
| FDK is a computable lock-in / reversibility index | **defensible** |
| …that is a *genuinely novel* independent instrument (beats quasi-option value etc.) | **unproven — rests entirely on ΔR²** |
| **The one open question** | **does it add predictive power the existing indices lack?** |

## 6. Verdict

The project most likely **walked out of philosophy defeated** (H1 dead; reversibility
pre-formalised as quasi-option value) **and may yet be alive as an engineering-institutional
metric** — but *only* if the consent-indexed, micro-level reversibility score predicts
real-world lock-in and failure better than the indices that already exist. The real test is
no longer a philosophical argument; it is an **empirical comparison with the lock-in,
optionality, and path-dependence literatures.** If FDK shows no advantage there, the whole
project reduces to a **rename** of quasi-option value and switching costs. If it shows an
advantage, then — for the first time in this entire program — there is a genuinely
interesting claim on the table, in the right field, with the experiment that proves it.

The next move is not another paper and not another philosopher. It is: **build the metric
(§4), get the corpora, and run §3.** Until ΔR² is measured, the honest status is
*"defensible candidate index, novelty unproven, most-likely-absorbed."* That is exactly as
far as argument can carry it, and it is where argument should stop.

*Draft for hostile review. Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah
Doust (CC BY 4.0). Engineering context: Ali Pourrahim. The remaining question is empirical
(incremental predictive validity), not philosophical; quasi-option value (Arrow–Fisher–Henry,
1974) is the prior occupant H2 must out-predict. Companion: [`hidden_variable.md`](hidden_variable.md).*
