# Standing — FDK 2.0, Project A (Layer 3)

> *Who is a rights-holder at all?* The frozen kernel answers legitimacy for a
> **competent, living, present, consenting adult person**. Standing is the prior
> question it cannot ask: what about an infant, the incapacitated, a coma patient, a
> fetus, an animal, an ecosystem, a future generation, an AGI? This is the largest of
> the three open frontiers (`LIMITATIONS.md`), and the roadmap's most dangerous,
> because getting it wrong can change the primitive itself. So it lives here, as an
> **advisory** research layer, never as a kernel edit.

## The non-negotiable rules (from `ROADMAP.md`)

- **Never assume** `infant = adult`, `animal = human`, or `future generation =
  present owner`. Each is a distinct standing, and collapsing them is how rights
  theories smuggle in conclusions.
- **Advisory only.** `assess_standing` returns no ALLOW/DENY, mutates nothing, and
  imports nothing into `fdk_kernel` (`tests/test_boundary.py`). It *classifies and
  recommends*; a human acts on the recommendation.
- **Honesty over coverage.** Where v1.0 cannot represent a rights-holder, say so —
  do not fake it with a placeholder `Entity`. A faked representation is a hidden new
  axiom in a frozen kernel.

## The standing taxonomy (`StandingKind`)

| Kind | Who | Representable in v1.0? | How |
|---|---|---|---|
| `FULL_PERSON` | competent, living, present adult | **yes** | attests their own `Consent` |
| `GUARDIAN_REPRESENTED` | infant / incapacitated **with** a surrogate | **yes** | the **guardian** attests on the subject's behalf (a recommendation a human asserts, not an inference) |
| `PROTECTED_NON_CONSENTER` | incapacitated **without** a surrogate | partial | the kernel denies for want of valid consent — protection **by omission**, not a best-interests doctrine |
| `NO_STANDING_IN_V1` | animal, ecosystem, AGI-as-rights-holder, future generation, the dead | **no** | out-of-frame; flagged for future research |

## What v1.0 genuinely cannot represent (quoted honestly)

- **Animals / ecosystems / machine persons.** The kernel's rights-holders are
  `HUMAN`; a `MACHINE` is a tool, never a rights-bearer. There is no standing object
  for a sentient non-human or a natural system. Representing one may require a new
  entity kind — i.e. a primitive change — which is precisely why it is deferred.
- **Future generations and the dead.** A non-present person cannot be an `Entity` in
  `affects` without an impossible signature, so duties toward them are inexpressible.
  (See also the intergenerational cases in `REALWORLD_REDTEAM.md`.)

These are not bugs and not solved here. They are the boundary of the v1.0 frame,
named so the next version can decide them deliberately rather than by accident.

## How this composes with the frozen kernel

```
StandingFacts (advisory description of the subject)
      │
      ▼
assess_standing → StandingAssessment (kind + representable_in_v1 + recommendation)
      │
      ▼  (a HUMAN acts on the recommendation)
  e.g. GUARDIAN_REPRESENTED → a human builds the kernel Consent with the guardian
  as the attesting party → the unchanged, frozen kernel reads it normally.
```

The kernel never learns about ages, species, or guardianship; it keeps reading
attested `Consent`. Standing only helps a human construct that attestation correctly,
or tells them honestly that no correct construction exists yet.

## Honest scope

v0 ontology exploration, uncalibrated. The classifier is a transparent decision tree
over status facts, not a theory of personhood. The real Project A needs a defended
ontology of standing (and the hard ruling on animals / future people / AGI), informed
by law, moral philosophy, and the source theory's own account of who is owned by God
(A1). This scaffold's contribution is to make the four standing classes — and the v1.0
boundary between representable and not — explicit and testable.

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Engineering: Ali Pourrahim.*
