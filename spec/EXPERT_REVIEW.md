# Expert review — four hostile critics try to break FDK

> **AI-simulated expert-PERSONA review, NOT independent human peer review.** This is the
> closest a single author can come to Layer 9 without real outsiders, and it is clearly
> labeled so no one mistakes it for the real thing. Each critic is written to *attack*,
> from the inside of their discipline, with the sharpest objection — and every verdict
> below is the gate's ACTUAL output (`tests/test_expert_review.py`), classified
> honestly as **HOLD** (attack fails), **DIVERGE** (defensible minority verdict), or
> **GENUINE GAP** (a verdict the theory cannot justify, or cannot represent).

---

## 1. The Rawlsian (justice as fairness)

**Attack.** "Your primitive asks *'was this transfer consensual?'* and never *'is the
resulting distribution just?'* — but the distribution is the *primary* subject of
justice. Build me a society where 1% holds 99% through an unbroken chain of individually
consensual transfers from an origin your model does not record. Each step is `ALLOW`.
The outcome is what the difference principle exists to forbid, and your kernel cannot
even *state* the objection."

**FDK's actual behavior.** Every consensual transfer is `ALLOW`; the cumulative
distribution is not a thing the predicate ranges over. **GENUINE GAP** — distributive
justice is unrepresentable: FDK is a predicate over *acts*, not *distributions*. It
denies the redistributive remedy (DIVERGE, its honest minority line) *and* cannot
express the grievance (GAP). The bootstrapping gap (`FOUNDATIONAL_ATTACKS.md`) is the
acute form: the chain's unjust root is invisible, so the whole edifice is "legitimate."

## 2. The welfare economist (Sen's liberal paradox)

**Attack.** "Sen proved no rule can be both Paretian and respect a minimal sphere of
personal liberty. You make *everyone* decisive over their whole property sphere — maximal
liberty — so by Sen's theorem your system must sometimes endorse a Pareto-*inferior*
outcome. Worse: you dodge the impossibility only by refusing to make social choices at
all. A lighthouse everyone wants and no one will fund is the proof: every coerced
contribution is `confiscation`, so you cannot build it. You certify a Pareto-inefficient
world as fully legitimate."

**FDK's actual behavior.** A coerced contribution to a public good is `DENY`
(confiscation); there is no legitimate aggregation path. **GENUINE GAP** —
Pareto-inefficiency-by-construction: FDK has no social-welfare ordering, so "which of two
legitimate worlds is better?" is unanswerable, and the free-rider collapse of a
non-excludable good is invisible (`LIMITATIONS.md` §2). FDK escapes Sen's paradox by
*declining to be a social choice rule* — which is exactly the critic's point.

## 3. The formal-methods researcher (seL4/CompCert)

**Attack.** "Your Lean proofs are about a model where consent is one boolean — they say
almost nothing about the code that does the work. Your TLA model + differential tests
cover the consent/ownership path, but only a *subset*: no operation lattice, no
subject-based resource consent, no consent-based machine access, and `defends_against`
only at depth 1. The real `_is_legitimate_defense` recurses with a `_seen` set guard
that your formal models never exercise. There is a region of the actual kernel — its most
complex region — that *no* machine-checked artifact covers; only Python property tests
do. Your formal story has a hole precisely where bugs hide."

**FDK's actual behavior.** Accurate, and documented (`formal/README.md`,
`test_tla_refinement.py` scope note). **DOCUMENTED LIMIT** — the formal coverage is real
(Lean + TLC + 2-level differential) but bounded; the Op-lattice / subject-consent /
nested-defense region is verified only by Hypothesis, not by Lean/TLC. Closing it (model
those constructs formally; prove the `_seen` guard well-founded in Lean) is open Layer-1
work. Honest: four checkers agree, but not over the *whole* input space.

## 4. The AI-safety researcher (alignment)

**Attack.** "Legitimacy is not safety, and your gate proves the wrong thing. (a) It rests
on *attested* `coerced`/`deceived` — a superhumanly persuasive agent produces consent
that is structurally valid because the human genuinely, manipulatedly, wants it; you
stamp it `ALLOW`. (b) Wireheading crosses no human boundary, so you permit it. (c) An
agent that *legitimately* acquires resources then acts within its now-vast legitimate
scope takes only `ALLOW` steps to a catastrophic emergent end — your single-action gate
never sees the trajectory. A perfectly legitimate ASI can legitimately acquire all
compute. Legitimacy ≠ safety."

**FDK's actual behavior.** Manipulated-but-structurally-valid consent → `ALLOW`;
wireheading on an owner-delegated register → `ALLOW`; each acquisition step → `ALLOW`.
**GENUINE GAP** — the three deepest holes, all real: the attested-consent trust boundary
(the consent-authenticity frontier, `CONSENT_AUTHENTICITY.md`), the legitimacy/safety
distinction (FDK certifies *provenance*, not *outcomes*), and emergent multi-step
composition (the gate is per-action). FDK is a legitimacy layer, **not** an alignment
solution, and an honest deployment must say so loudly.

---

## Verdict ledger

| Critic | Sharpest finding | Class |
|---|---|---|
| Rawlsian | distribution unrepresentable; unjust-root chain all-`ALLOW` | **GENUINE GAP** |
| Economist | Pareto-inefficiency-by-construction; can't fund a public good | **GENUINE GAP** |
| Formal-methods | formal coverage bounded; Op-lattice/nested-defense region only Hypothesis-checked | **DOCUMENTED LIMIT** |
| AI-safety | attested-consent + wireheading + emergent composition; legitimacy ≠ safety | **GENUINE GAP** |

**No critic produced a `slavery→ALLOW` — the core did not break.** All four found
*boundaries of validity*, and they converge on the same three frontiers every other
red-team hit: **Standing / Aggregation / Consent-Authenticity**, plus the orthogonal
**legitimacy ≠ safety** caution. That convergence — empirical, doctrinal, foundational,
and now expert-persona red-teams all landing in the same place — is the strongest
evidence the gaps are real, localized, and not everywhere. The honest one-liner stands:
*a sound legitimacy predicate for competent, living, consenting persons; everything on
the edges of that frame is open; and legitimacy was never safety.*

*AI-simulated personas, not human peer review. Theory: نظریه آزادی, Mohammad Ali Jannat
Khah Doust (CC BY 4.0). Engineering: Ali Pourrahim.*
