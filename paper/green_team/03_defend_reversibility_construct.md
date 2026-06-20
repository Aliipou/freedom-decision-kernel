# Green Team — Defending the Reversibility Score as an Independent Construct

> **Assigned claim:** *"FDK's lock-in / reversibility score is an INDEPENDENT construct,
> not a reparameterization of `switching_cost`."*
> **Red-team verdict to overturn:** r²=0.97 with `switching_cost` (tautological, it is an
> input); the 17% residual is just `alternatives`, another known variable; no independent
> construct; needs the ΔR² test on real data.
>
> *This file mounts the strongest honest defense, then adjudicates. A failed defense
> confirms the red-team — a valid result. No manufactured evidence; every number below is
> reproduced from the seed in `data/` and the apparatus in `src/fdk_research/lockin.py`.*

---

## 1. The defense's core move: r²=0.97 is an artifact of the SEED, not of the CONSTRUCT

The red-team reads `corr(FDK, switching_cost) = +0.99` as "switching_cost is an input, so
the correlation is mechanical (BMI ≈ weight)." That analogy is too generous to the
red-team, and it hides the actual mechanism. Look at what the construct actually does
(`lockin.py:55–59`):

```
escapability = ( portability + (1 − switching_cost) + alt_score ) / 3
score = 1 − escapability
```

`switching_cost` enters with a weight of **exactly 1/3**. A variable contributing one
third of a three-term mean **cannot** mechanically produce r²=0.97 against the output.
For a 1/3-weighted input to explain 97% of the output's variance, the *other two thirds*
must be nearly collinear with it. So r²=0.97 is not "BMI ≈ weight"; it is a statement
about the **seed data's covariance structure**, and that structure is measurable:

| seed correlation | value | meaning |
|---|---|---|
| `corr(switching_cost, portability)` | **−0.959** | the two "expensive" axes move as one |
| `corr(switching_cost, alternatives)` | −0.191 | third axis nearly orthogonal |
| sd(switching_cost), sd(portability) | 0.229, 0.253 | real spread |
| **sd(alt_score)** after the clamp | **0.042** | **6× smaller — nearly constant** |

The score collapses onto `switching_cost` **because the LLM that priced the seed co-rated
`switching_cost` and `portability` as mirror images (−0.96)**, and because the third axis
was flattened to a near-constant. This is exactly the failure mode the red-team's own A2
("features are LLM priors") predicts — but the red-team then forgets it when reading A1.
You cannot simultaneously hold "the features are unreliable LLM co-ratings" (A2) **and**
"the r²=0.97 reflects the construct's true geometry" (A1). The first explains away the
second. On the seed, the construct never had three independent axes to separate; it had
**one and a half**.

## 2. The clamp is destroying the second dimension before it can show up

The red-team says the 17% residual "is just `alternatives`, another known variable" — and
treats that as damning. But look at *why* `alternatives` barely registers. The raw data is
not flat:

```
alternatives raw distribution : {2:1, 3:5, 4:12, 5:12, 6:14, 7:2, 8:8, 9:1, 10:5, 12:2}
```

Substitute counts run **2 through 12** — genuine, wide spread. Then `escapability()` applies
`min(alternatives, 3) / 3.0` (`lockin.py:58`):

```
clamped (0..3) distribution   : {2:1, 3:61}
```

**Sixty-one of sixty-two records are crushed to exactly 1.0.** The diversification / exit-
breadth axis is not absent from the world — it is annihilated by a saturating clamp inside
the apparatus. The residual is only 17% and only weakly `alternatives`-shaped **because the
formula throws the spread away before scoring.** That is an *implementation* artifact, not
evidence that the construct has no second dimension. Remove the clamp (or raise the cap to
the observed max of 12) and the `alternatives` axis recovers an order of magnitude of
variance the current score discards. The red-team measured a dimension the code had already
deleted, then concluded the dimension is small.

## 3. There genuinely IS a second axis switching_cost cannot reach: concentration (HHI)

The red-team's residual analysis runs on the **per-service** scalar, where the only inputs
are `{switching_cost, portability, alternatives}`. But the construct is not a per-service
scalar — `LockinProfile` (`lockin.py:62–80`) also carries `concentration`, the **HHI of
dependency weights across a portfolio**, reused from `compass_measure.dependency_index`.
This is a *portfolio-structural* quantity: two architectures with identical mean
`switching_cost` can have very different concentration — ten balanced dependencies vs. one
that owns 80% of the spend. `switching_cost`, a per-vendor cost, **provably cannot encode
this**; HHI is a function of the *weight vector*, orthogonal to the per-item cost axis by
construction. And `marginal_lockin()` (`lockin.py:116`) scores the **Δ of one decision
against a portfolio** — an ex-ante, per-action quantity that no static switching-cost index
yields. So the claim "FDK = switching_cost reparameterized" is **already false of the
object as built**: the experiment simply never exercised the concentration or marginal
channels, because the seed is a flat list of single services (every portfolio is N=1, so
HHI ≡ 1 and carries no variance *in this test*). Untested ≠ absent.

## 4. Where the defense is honest about its own limits

I will not overclaim. The defense above establishes three things and **not a fourth**:

- **Established:** the r²=0.97 is driven by seed collinearity (−0.96) and a saturating clamp,
  not by the construct being one-dimensional. The headline number is an artifact.
- **Established:** the construct *as built* contains axes (HHI concentration, marginal
  per-decision Δ) that `switching_cost` cannot express — so it is not a pure
  reparameterization *of switching_cost* even in principle.
- **Established:** the seed cannot test independence, because it co-rated two of three axes
  and flattened the third. "Independent on THIS seed" is **almost certainly no** — I concede
  this fully; the data physically lacks the variance to show separation.
- **NOT established:** that the surviving axes carry *independent predictive power* against a
  real outcome. That is Stage 2 (ΔR²), and §3 of `predictive_test.md` is right that it
  cannot be run on N≈2 heterogeneous, leak-prone cases. No defense can manufacture that.

The distinction the red-team blurs is the one that matters: it proved **"no separation on a
degenerate sample"** and reported it as **"no construct."** Those are different claims. A
sample with `corr(input₁, input₂) = −0.96` and a near-constant third input is *structurally
incapable* of distinguishing a one-dimensional construct from a three-dimensional one —
both fit it identically. The red-team's r²=0.97 is therefore **uninformative about
independence**, not evidence against it. That is not closure; it is an underpowered design.

## 5. The test that would actually settle it (and would have been cheap)

The red-team frames the missing test as the expensive Stage 2 ΔR² on 100+ real migration
outcomes. That is true for *predictive* independence. But *discriminant* independence —
the assigned claim — is far cheaper and was skipped:

1. **De-collinearize the seed.** Re-rate `switching_cost` and `portability` *independently*
   (different raters / different prompts / different sources), breaking the −0.96 artifact.
   If r²(FDK, switching_cost) drops well below 0.97, the construct separates and the
   red-team's headline dies on contact with non-degenerate data.
2. **Un-clamp `alternatives`** (or set the cap to the observed range). Re-measure the
   residual; if it grows and loads on diversification, the second axis is real.
3. **Use portfolios, not singletons**, so `concentration` (HHI) has variance, and regress
   `FDK` on `{switching_cost}` *alone*: the ΔR² of adding HHI + marginal is the
   discriminant-validity number — and it needs **no outcome data at all**.

None of these is the 100-case fieldwork. All three are runnable on a re-rated version of the
*existing* seed. The red-team's "needs real-world data" is true of Stage 2 but **overstated
for Stage 1** — discriminant validity can be probed now, and the fact that it has not been
is premature closure, not a verdict.

## 6. Verdict

**UNDECIDED** — for the *construct/real-data* claim. Reported loudly, because the red-team
called it CONFIRMED and that is overclosure.

The red-team is **correct on this seed**: independence is almost certainly absent in the
62-record sample — but for a reason that *vindicates the construct's geometry rather than
indicting it*. The r²=0.97 is manufactured by an LLM co-rating two of three axes at −0.96
and a clamp that crushes the third to a constant; it is an **artifact of a degenerate
sample**, not a property of the score. A sample that collinear **cannot** discriminate a
one-dimensional from a multi-dimensional construct, so the red-team's central number is
*uninformative* about the assigned claim, not *dispositive* against it. Worse, the object as
built already contains a switching-cost-orthogonal axis (HHI concentration) and an ex-ante
per-decision channel (`marginal_lockin`) that the experiment never exercised — so "pure
reparameterization of `switching_cost`" is false of the artifact even before any new data.

What the defense **cannot** overturn: independence on this seed (conceded — no), and
predictive independence (untestable here — open). What it **does** overturn: the inference
from "r²=0.97 on a degenerate sample" to "no independent construct." That inference is
premature closure. The honest status of the construct is **not "absorbed"** but **"untested
under non-degenerate conditions"** — and §5 shows that test is cheap and was skipped.

*Green Team (defense), Exit-Right/FDK program. Engineering: Ali Pourrahim. A failed defense confirms the red-team; that is a valid result.*
