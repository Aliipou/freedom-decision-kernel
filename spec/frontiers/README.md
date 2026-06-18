# Frontiers — where FDK fails (and where it may fail *fatally*)

> The honest output of treating FDK as a hypothesis to test, not a framework to defend.
> Five hostile research audits — one per program — each looked for the place FDK is
> *wrong*, not the place it holds. Each found one. In three cases the finding is not a
> "scope limit we'll patch with a new layer" but a candidate **structural** failure that
> may be **irreducible** — i.e. unfixable without abandoning the core primitive. A fourth
> (Ownership Genesis) is an ancient problem FDK *shares* with all property theory but hides;
> the fifth (AI Legitimacy) is the one place FDK may have something genuinely new, and even
> there only partially. That a consent-over-boundaries predicate has exactly these pressure
> points, and that they are the ones every other red-team independently converged on, is
> itself the result.

These are research notes, not verdicts. "Irreducible" is a conjecture to be argued down or
conceded — but the burden has shifted: it is no longer obvious any of the three is fixable.

**The "so what?" instrument:** these notes hunt for where FDK *fails*. The companion
[`RIVAL_DISCRIMINATION.md`](RIVAL_DISCRIMINATION.md) runs the harder commercial-of-ideas
test — *does FDK ever say anything Rothbard / Nozick / Hayek / Rawls / Sen / Ostrom do not?*
On the decisive cases its provisional answer is stark: most clean FDK verdicts **equal
Nozick/Rothbard** (redundant), every *original* verdict is either **refuted** (animals,
Ostromian commons) or a **collapse** (non-identity, adaptive preference), and the **one**
candidate genuine distinction is the **preserved-exit/revocation-right** condition on consent
— which is the single thesis worth testing next.

## The three candidate fatal findings

| Frontier | Deepest finding | Why it may be **irreducible** |
|---|---|---|
| **Consent** ([`consent_authenticity.md`](consent_authenticity.md)) | **Adaptive preference / the contented slave** (Sen). The oppressed person's `voluntary=True` is *sincere*, not a false attestation — the will genuinely aligns with the oppression. There is no manipulator, no fraud, no exit-removal to detect. | The only way to deny that consent is to assert you know the person's interests better than they do — which is precisely the **paternalism FDK exists to refuse**. The fix destroys the theory. |
| **Standing** ([`standing.md`](standing.md)) | **The non-identity problem** (Parfit). A class of grave wrongs (depleting the world for a damaged posterity) has *no identifiable victim with a complaint*, because the act **creates** the people it wrongs. | FDK's core relation is *person-affecting* and *consent-indexed*: wrong is cashed out against the specific `Entity` objects in `affects`. Adding future-person entities does **not** help — for every actual future person, the act was a *condition of their existence*. A victim-indexed gate cannot represent a victimless duty without abandoning its core relation. Lethal *even in the limit*. |
| **Aggregation** ([`aggregation.md`](aggregation.md)) | **Hardin-as-theorem vs. Ostrom-as-fact.** For any ownerless good the consent quantifier ranges over an *empty* boundary set, so it is vacuously satisfied ⇒ every extraction is ALLOW and any cap is confiscation ⇒ DENY. FDK *derives* the tragedy of the commons as a theorem of its structure. | **Ostrom's Nobel-winning empirical program refuted exactly that prediction** (Törbel since 1517, Valencia for a millennium, Maine lobster, the *iriai*). FDK encodes **zero** of her 8 design principles, and cannot even sit *beneath* an Ostromian institution, whose constitutive acts (binding a dissenting minority, monitoring without per-act consent) FDK's gate DENYies. Being wrong in the *specific direction a Nobel laureate proved wrong* is not a scope limit. |

The other two programs:

| Program | Finding | Verdict |
|---|---|---|
| **Ownership Genesis** ([`ownership_genesis.md`](ownership_genesis.md)) | FDK validates every *transfer* and audits *no origin*, so it confidently protects conquest-descended title (ALLOW the holder, DENY the dispossessed heir). There may be **no non-arbitrary original-acquisition rule** (Locke's proviso fails under scarcity; Nozick could not specify rectification; any cutoff date is arbitrary). | Possibly irreducible — but **shared with all property theory** (Locke/Nozick/Rothbard break here too). FDK's sin is *silence*; the minimum fix is disclosure (`ownership_graph.py` flags `FORCED_ORIGIN`), already started. |
| **AI Legitimacy** ([`ai_legitimacy.md`](ai_legitimacy.md)) | Is "provenance, not utility" genuinely new, or constrained-RL relabeled? | **Partial — real but narrow.** A categorical/lexicographic constraint is *not* reducible to a finite scalar reward (more than most AI-ethics frameworks have), but constrained RL captures much of it, and **legitimacy ≠ safety** means even the genuine part is no alignment solution. The one risky prediction that would decide it: *legitimacy-gated agents resist a class of reward-hacking that reward-shaped agents do not, at equal capability.* |

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
