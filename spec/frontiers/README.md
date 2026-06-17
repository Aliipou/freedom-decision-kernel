# Frontiers — where FDK fails (and where it may fail *fatally*)

> The honest output of treating FDK as a hypothesis to test, not a framework to defend.
> Three hostile research audits — one per frontier — each looked for the place FDK is
> *wrong*, not the place it holds. Each found one. And in each case the finding is not a
> "scope limit we'll patch with a new layer" but a candidate **structural** failure that
> may be **irreducible** — i.e. unfixable without abandoning the core primitive. That a
> consent-over-boundaries predicate has exactly three such pressure points, and that they
> are the three every other red-team independently converged on, is itself the result.

These are research notes, not verdicts. "Irreducible" is a conjecture to be argued down or
conceded — but the burden has shifted: it is no longer obvious any of the three is fixable.

## The three candidate fatal findings

| Frontier | Deepest finding | Why it may be **irreducible** |
|---|---|---|
| **Consent** ([`consent_authenticity.md`](consent_authenticity.md)) | **Adaptive preference / the contented slave** (Sen). The oppressed person's `voluntary=True` is *sincere*, not a false attestation — the will genuinely aligns with the oppression. There is no manipulator, no fraud, no exit-removal to detect. | The only way to deny that consent is to assert you know the person's interests better than they do — which is precisely the **paternalism FDK exists to refuse**. The fix destroys the theory. |
| **Standing** ([`standing.md`](standing.md)) | **The non-identity problem** (Parfit). A class of grave wrongs (depleting the world for a damaged posterity) has *no identifiable victim with a complaint*, because the act **creates** the people it wrongs. | FDK's core relation is *person-affecting* and *consent-indexed*: wrong is cashed out against the specific `Entity` objects in `affects`. Adding future-person entities does **not** help — for every actual future person, the act was a *condition of their existence*. A victim-indexed gate cannot represent a victimless duty without abandoning its core relation. Lethal *even in the limit*. |
| **Aggregation** ([`aggregation.md`](aggregation.md)) | **Hardin-as-theorem vs. Ostrom-as-fact.** For any ownerless good the consent quantifier ranges over an *empty* boundary set, so it is vacuously satisfied ⇒ every extraction is ALLOW and any cap is confiscation ⇒ DENY. FDK *derives* the tragedy of the commons as a theorem of its structure. | **Ostrom's Nobel-winning empirical program refuted exactly that prediction** (Törbel since 1517, Valencia for a millennium, Maine lobster, the *iriai*). FDK encodes **zero** of her 8 design principles, and cannot even sit *beneath* an Ostromian institution, whose constitutive acts (binding a dissenting minority, monitoring without per-act consent) FDK's gate DENYies. Being wrong in the *specific direction a Nobel laureate proved wrong* is not a scope limit. |

## What this does — and does not — mean

- It does **not** mean FDK is worthless. Its sound region — legitimacy for competent,
  living, consenting persons, prior to and independent of utility — is real, formally
  checked (Lean/TLC/Rust/Hypothesis), and its anti-utilitarian verdicts are clean.
- It **does** mean the three frontiers are not "future modules." They are open *scientific*
  questions whose honest answer might be **"FDK collapses here"** — and that answer would
  be a contribution (mapping the exact edge of a consent-based theory), not a defeat.
- It sharpens the priority the agenda already set: **Standing is most fundamental** (the
  non-identity result suggests the primitive itself may need to change), then Consent, then
  Aggregation. The Aggregation finding also names the one rival FDK most neglected and most
  needs to answer: **Ostrom**.

## The standing instruction this encodes

When the next gap is found, the first question is **not** "what layer fixes it?" It is
"**does this gap dissolve the primitive?**" Two of the three above plausibly do. A theory
mature enough to ask that question of itself — and to write the answer down even when the
answer is "we may be wrong at the root" — has done the rarer and more valuable thing.

*Research notes. Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust
(CC BY 4.0). Engineering: Ali Pourrahim.*
