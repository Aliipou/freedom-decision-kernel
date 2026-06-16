# Consent Authenticity — FDK 2.0, Project C (Layer 5)

> The hardest and most important frontier (`LIMITATIONS.md`, `ROADMAP.md`). The whole
> kernel rests on `valid_consent`, yet the kernel reads `coerced` / `deceived` as
> **attested booleans** — it honors a true report, it cannot detect a false one. So a
> consent that is structurally clean but *manufactured* (addiction, dark patterns,
> monopoly dependence, superhuman persuasion) launders straight through. Closing this
> is the difference between a theory of consent for the 19th century and one for the
> 21st.
>
> This document specifies the layer that begins to address it — and, just as
> importantly, specifies exactly what it must **not** do.

## The non-negotiable architectural rule

Consent **detection must never enter the kernel.** Two reasons, both fatal if
ignored:

1. **The freeze.** The kernel is frozen at v1.0 (`FREEZE.md`); adding inferred
   consent is adding an axiom and mixing policy into the gate.
2. **Hidden paternalism — the real danger.** The moment a system *infers* that your
   consent is not real, it has claimed "you don't really know what you want." That is
   the exact move by which most ethical systems become tyrannies of the
   well-meaning. A legitimacy theory that overrides stated consent "for your own
   good" has abandoned the thing that made it legitimate.

Therefore this layer is **advisory only**. It lives in `fdk_research/`, imports
nothing into `fdk_kernel/` (mechanically enforced by `tests/test_boundary.py`), and
it **never returns a verdict.** It does not deny, it does not override. It produces a
structured *risk report* whose only outputs are: surface the concern, and route to a
**human** (the owner / the consenter themselves) for review or re-attestation.

## What it does

```
ConsentContext  (how the consent was obtained)
      │
      ▼
assess_consent_authenticity → AuthenticityReport  (risk flags + advisory severity)
      │
      ▼
recommend_action → {ACCEPT_AS_ATTESTED, REQUEST_REVIEW, RECOMMEND_REATTEST}
```

The report answers one question: *what about how this consent was obtained would make
a careful observer doubt it was freely formed?* It then **recommends** — never
imposes — that a human re-examine the attestation. If, after review, the owner judges
the consent was not voluntary, *they* set `voluntary=False` / `coerced=True` on the
`Consent`, and the **frozen kernel** does its normal structural thing. The pipeline is:

> authenticity layer **informs** the attestation → human **decides** the attestation →
> kernel **reads** the attestation.

The kernel stays pure; the human stays sovereign; the manipulation risk is made
*visible* rather than silently honored.

## The risk taxonomy (structural factors, not mind-reading)

Each factor is an observable fact about the transaction, not a guess about an inner
state — this keeps the layer honest and falsifiable rather than a license to
second-guess people.

| Factor | What it observes |
|---|---|
| `dependency` | the consenter relies on the counterparty for a need (economic / digital / emotional) such that refusal is not really open |
| `exit_cost` | how costly leaving / refusing is (a proxy for voluntariness; high exit cost ≈ the exit right is encumbered) |
| `information_asymmetry` | one side held material information the other lacked (bears on *informed*) |
| `manufactured_urgency` | artificial time pressure engineered to prevent deliberation |
| `dark_patterns` | choice architecture designed to push one option (bears on *specific* / *voluntary*) |
| `monopoly` | the counterparty was the only realistic option (no alternative to consent to) |
| `exploited_vulnerability` | a known cognitive vulnerability was targeted (addiction loops, dopamine engineering, crisis state) |
| `irrevocable` | the consent cannot be withdrawn (bears directly on `revocable`) |

## Honest scope of this version

This is a **v0 scaffold**: the factor→risk mapping is a transparent, hand-set rule,
**uncalibrated** against any dataset of real manipulated-consent cases. It is the
*shape* of the answer, not the answer. The real Project C needs behavioral economics,
neuroscience, cognitive psychology, and decision theory, and a corpus of cases
labeled by people who are not the author — exactly the same decontamination
discipline as FreedomBench (`independent_bench.py`). Until then, this layer makes the
problem *explicit and routable*, which is strictly better than the kernel's silent
"caller-attested," and it does so without taking the one step that would betray the
theory: deciding, for you, that your yes was really a no.

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Engineering: Ali Pourrahim.*
