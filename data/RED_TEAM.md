# Red-team — why this seed data does NOT validate FDK (and what would)

> The director's standing order: *always red-team, including the methodology, to make
> it undeniably real.* So this file attacks the data-collection + scoring pipeline as
> hard as it can, using the **actual numbers** from `examples/lockin_experiment.py`. The
> conclusion is deliberately deflationary: the experiment runs and is face-valid, but it
> **cannot** show FDK works, and pretending otherwise would be the exact fraud this whole
> project was built to avoid.

## What the experiment actually produced (real output)

```
[1] FACE VALIDITY  — open baselines low (Docker 0.05, PostgreSQL 0.07),
                     proprietary high (Salesforce 0.60, SAP 0.62, DynamoDB 0.66)
[2] DISCRIMINANT   — corr(FDK score, switching_cost) = +0.99  (r² = 0.97, tautological)
                     corr(FDK score, portability)    = −0.99  (r² = 0.97)
                     corr(FDK score, alternatives)   = −0.27  (r² = 0.07)
[2b] RESIDUAL      — ε after removing switching_cost = 17% of the score's spread;
                     corr(ε, alternatives) = −0.48  → ε is mostly the `alternatives` input
[3] PREDICTIVE     — 16 cases; $ cost figure on 2; duration on 3; ΔR² NOT estimable
```

## The statistically-correct reading (not "FDK = switching cost")

The honest inference is **not** "FDK = switching cost." It is: *FDK_score = f(switching_cost)
on this 62-record, LLM-estimated sample.* That is the **BMI ≈ weight** situation — `BMI =
f(weight, height)` gives `corr(BMI, weight) ≈ 0.95`, which is not a discovery, because weight
is an input. Here switching_cost is one of the three inputs, so r² = 0.97 is **largely
tautological**, and on a small hand-priced sample it is weak evidence either way.

The non-tautological question is the **residual ε**, and the experiment answers it: ε is
**not zero** (17% of the spread) but its structure is just FDK's **other known inputs** —
mostly `alternatives` (corr −0.48), with portability collinear to switching_cost. So **no new
construct emerges**: FDK is a weighting of `{switching_cost, portability, alternatives}`,
three pre-existing lock-in variables. **The residual must NOT be christened "reversibility"**
— that is the project's recurring error (see a pattern → give it a philosophical name →
mistake the name for reality). At this stage it is `ε`, and `ε` is, mechanically,
`alternatives` (and quite possibly a dataset artifact of how the features were co-rated).

**The three questions, answered:** (1) R² of switching_cost alone ≈ **0.97 (tautological)**;
(2) residual variance ≈ **17% of spread, = `alternatives`**; (3) does ε predict a real
outcome? **Untested — and unanswerable on N=2.** Question 3 is the whole game: negative ⇒ the
scientific case is essentially closed (a reparameterization of switching cost); positive ⇒
the first real research path. It cannot be answered without the validation dataset below.

## The attacks (each is a reason the result proves nothing about the world)

**A1 — The score has shown no independent construct (r² = 0.97, but tautological; ε = 17%,
but = `alternatives`).** The careful statement (not "FDK = switching cost"): on 62 LLM-priced
services the score is 97%-explained by `switching_cost`, *which is one of its three inputs*,
so the correlation is largely mechanical (BMI ≈ weight). The non-tautological residual is 17%
of the spread and decomposes to `alternatives` — another known lock-in variable. So FDK is a
weighting of three pre-existing variables; *Stage 1 (discriminant validity) is not yet
passed*, and the residual is **not** a new construct to be named. Whether the *combination*
beats `switching_cost` alone at predicting a real outcome is untested (see A4).

**A2 — The features are LLM priors, not measurements.** `switching_cost` and
`portability` were *estimated by language models* (web-grounded in places, but still
estimates). Feeding LLM-estimated features into a formula and admiring the output tells
you about the LLM's priors, not about reality. Garbage-resistant only if the knowledge
base is independently measured — which it is not.

**A3 — Circular ground truth.** The migration file carries `est_lockin_score_hint` — an
LLM guess at how locked-in each org was. If we "validated" the FDK score against that
hint, we would be checking whether the LLM agrees with itself. The hint must NEVER be
used as an outcome; it is excluded from the experiment for exactly this reason.

**A4 — N is fatal.** 16 cases; **2** with a dollar cost; 3 with a duration. No regression
is possible. To detect even a modest unique contribution (ΔR² ≈ 0.1, ~4 controls) at
80% power you need on the order of ~100+ cases with a *single, measured* outcome. We have
~2. Any ΔR² reported on this data would be noise dressed as evidence.

**A5 — Survivorship / availability bias.** The cases are *famous public exits* (Dropbox,
37signals, GEICO, Parler). Routine successful stays and quiet failures are invisible. A
sample selected on "was written about" cannot estimate a base rate of anything.

**A6 — Heterogeneous outcomes.** "Lock-in damage" appears as cost (Ahrefs $122M), savings
(Dropbox ~$75M), duration (30 months), price-hike incident (VMware/Broadcom), or forced
de-platforming (Parler). These are not one dependent variable; they cannot be pooled into
one regression without an arbitrary commensuration that would itself drive the result.

**A7 — Feature/outcome leakage risk.** For the cases, the same public write-up that
reports the outcome often *informs* the analyst's switching-cost estimate. Feature and
outcome are not independently sourced, so even a correlation (if N allowed one) could be
the write-up predicting itself.

**A8 — Vendor-conflicted source bias.** Some portability claims trace to vendor docs and
migration-tool marketing, which have a direction (a "DynamoDB→X" tool oversells how easy
leaving is; AWS undersells lock-in). The knowledge base inherits those slants.

## Severity

| # | Attack | Severity | Fixable by more LLM data? |
|---|---|---|---|
| A1 | score ≈ switching_cost (r²=0.97) | **fatal to novelty** | No — needs an outcome to beat the input against |
| A2 | LLM-estimated features | high | No — needs measured features |
| A3 | circular ground truth | fatal if ignored | Avoided (hint excluded) |
| A4 | N≈2 outcomes | **fatal to inference** | No — needs real cases |
| A5 | survivorship bias | high | No — needs a sampling frame |
| A6 | heterogeneous outcomes | high | Partly — pre-register one outcome |
| A7 | feature/outcome leakage | medium-high | No — independent sourcing |
| A8 | vendor-conflicted sources | medium | Partly |

**Note that none of the fatal attacks is fixed by generating more LLM data.** More
subagents, more estimated rows, more cases-from-memory would amplify A1/A2/A5, not cure
them. This is the honest ceiling of "collect data with subagents."

## What a real validation dataset must look like

1. **A sampling frame**, not a highlight reel: a defined population of migration decisions
   (e.g., all cloud-database migrations in a sector over N years), sampled to include the
   silent successes and quiet failures.
2. **One pre-registered outcome**, measured from primary records: e.g., realized migration
   cost in engineer-months, or a binary "migration abandoned within 18 months."
3. **Independently measured features**: switching cost / portability rated *before* and
   *without* knowledge of the outcome, ideally by engineers, not inferred from the same
   article that reports the result.
4. **Established controls**: switching-cost indices, spend, concentration, quasi-option
   value — so the test is *incremental* (ΔR²), the only thing that matters.
5. **N large enough** (~100+) to detect a small ΔR² and survive out-of-sample.

Only then is the question answerable: does the FDK composite beat `switching_cost` alone
at predicting real migration pain? On today's evidence the honest prior, from A1, is
**probably not** — and that prediction is itself the most useful thing this seed produced.

## Verdict

The pipeline works, the face validity is reassuring, and the data is a legitimate *seed*.
But **the experiment refutes the temptation, not the null**: it shows that FDK has not yet
earned independence from switching cost, and that the data to settle it does not exist here.
That is the undeniably-real result — a negative one, reported in full, which is the only kind
worth trusting.

## The two questions that remain (both empirical, neither philosophical)

The dead questions: *"is FDK a theory of freedom?"* (no) and *"is reversibility a new
concept?"* (almost certainly no). What is left is **not philosophy, logic, or proof — only
data**, and only two questions, because a tool can be a *new combination of known variables*
and still be worth building **if that combination does something the parts don't**:

- **Q-A — Prediction.** Does the composite predict real migration outcomes (cost, duration,
  failure) **better than its components alone** — ΔR² > 0 over `switching_cost` + `portability`
  + established controls? *Needs a real outcome dataset (≈100+, one pre-registered measured
  outcome). Not runnable here.*
- **Q-B — Decision value.** Does a CIO **decide better/faster** seeing the single FDK score
  than seeing `switching_cost` and `portability` separately? Value may live in the
  *aggregation + presentation*, not in a new variable. *Needs a human decision experiment, not
  a regression.*

If both answer **no**, FDK is, industrially as well as academically, a clever
reparameterization — done. If **either** answers yes, there is a real, defensible product
(Q-B) or even a real measurement contribution (Q-A) — *without* any new theory.

## Standing odds (director's, and the data supports them)

| Claim | Probability |
|---|---|
| FDK is academically a clever recombination of existing concepts | **80–90%** |
| A useful industrial tool/product can be built from it | **50–70%** |
| It is accepted as an independent theory in philosophy / social science | **< 20%** |

The seed data, honestly read, supports this deflationary picture over any rosier one — which
is exactly the trajectory a serious idea follows: big claim → hard attacks → remove the false
parts → a smaller, truer core remains. That core is *a decision-support score made of known
variables, whose marginal value (Q-A / Q-B) is untested.* Not a defeat; a sharper, smaller,
honest claim.

*Red-team of the lock-in data + methodology. Numbers from `examples/lockin_experiment.py`.
Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Engineering: Ali Pourrahim. Written to make the claim falsifiable, not to flatter it.*
