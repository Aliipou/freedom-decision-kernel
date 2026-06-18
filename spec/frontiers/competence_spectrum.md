# Competence spectrum — a candidate direction for part of Standing

> Research notes — a candidate *direction*, not a solution, and explicitly **not** a defense.
> Most of the `frontiers/` docs hunt for where FDK fails. This one records the most promising
> repair for ONE cluster of the Standing problem (the *capacity* of acknowledged persons:
> children, dementia, intoxication, cognitive disability) — while being clear about the part
> it does **not** touch (whether non-persons have standing *at all*: animals, fetuses, future
> generations, the Parfit non-identity wall of `standing.md`). A direction that fixes one
> cluster and not the other is progress *and* a map of the remaining hole — both must be said.

## The core decoupling

FDK's current model collapses two different things into one `valid_consent`:

- **Ownership** — *is this resource mine?*
- **Capacity** — *am I competent to exercise/alienate it right now?*

These are distinct. A newborn **owns** their body — the parents do not own the child — yet a
five-year-old cannot sell their house, sign a lifetime contract, or consent to selling a
kidney. Modern law already splits **ownership** from **legal capacity** for exactly this
reason. FDK conflates them, so it can only say "owner / not-owner," which is too coarse for
every non-fully-competent person.

## The sharp form (and why ownership must stay BINARY)

The tempting move — make *ownership* gradual — is a trap. "Does a person with IQ in the 30th
percentile own 70% of their body? Does an Alzheimer's patient own 40% of their house?" is a
direct road to exploitation and to stripping the vulnerable of protection. So ownership stays
binary and we grade what is exercised on it — and that splits into **three** variables, not
two:

```
Ownership          = 1        (binary: a rights-holder owns a thing or does not — the protection)
Agency             ∈ [0, 1]   (can they form/exercise will over it now?)
Transfer Authority ∈ [0, 1]   (may they alienate/contract it away?)
```

| Subject | Ownership | Agency | Transfer Authority |
|---|---|---|---|
| coma patient | 100% | 0% | 0% |
| newborn | 100% | ~10% | 0% |
| young child | 100% | ~30% | ~5% |
| adolescent | 100% | ~60% | variable |
| ordinary adult | 100% | 100% | 100% |

Ownership stays absolute (the protection); agency and transfer-authority are graded. Locke and
Nozick both hold humans own themselves, yet neither concludes that *any* human in *any* mental
state can form a valid contract.

## The kernel boundary (the non-negotiable architectural rule)

The competence **number does NOT go in the kernel.** A `Competence Score ∈ [0,1]` is a
research-layer measurement (developmental psych, clinical assessment) — soft, contestable, and
*dangerous* (a lever for stripping rights). The frozen kernel only ever receives a **boolean**:
*is competence sufficient for THIS consent?* This keeps the kernel deterministic and
non-semantic (`FREEZE.md`), and quarantines the paternalism risk in a separable, auditable
layer — exactly the discipline `CONSENT_AUTHENTICITY.md` demands.

## The Consent Matrix — consent is not one thing

Different acts demand different minimum competence; the threshold rises with stakes and
irreversibility:

| Act | Minimum competence |
|---|---|
| eat an ice cream | low |
| choose today's clothes | low |
| choose a school | medium |
| sign a financial contract | high |
| marry | very high |
| sell a bodily organ | maximum |

```
valid_consent(person, act)  ⟺  Competence(person) ≥ Threshold(act)
```

So a child's consent *suffices* for the candy and *fails* for the kidney — with the same binary
ownership throughout. (Honest snag, recorded in §open-questions: `Threshold(act)` re-imports a
stakes/harm judgment the gate otherwise refuses; that tension is real, not waved away.)

## Ownership ≠ contract capacity, illustrated

| Stage | Body ownership | Property ownership | Contract / transfer capacity |
|---|---|---|---|
| newborn | 100% | 100% | ~0% |
| age 5 | 100% | 100% | ~5% (small consensual acts) |
| age 10 | 100% | 100% | ~20% |
| age 15 | 100% | 100% | ~60% |
| 18+ competent | 100% | 100% | 100% |

Ownership is flat at 100%; only capacity ramps. **Age is only a proxy** — a mature 16-year-old
may exceed a cognitively-declining 40-year-old — so the real variable is a `Competence Score`,
and the legal age-line is an administrable approximation of it.

## How it would change the kernel (a hypothesis, gated on the freeze)

The frozen v1.0 `Consent` is a conjunction of seven booleans, one of which is `competent`.
The proposal replaces that boolean with a **graded** competence and makes consent-validity (and
the *transferability* of a given right) a function of competence × stakes — so a child's
consent suffices for buying candy but not for selling an organ; a guardian acts only within a
**defeasible**, best-interests-bounded scope (closing the `standing.md` finding that guardian
consent is currently an un-defeasible laundering channel). This **changes the primitive** —
hence it is FDK 2.0 research, not a v1.0 patch.

## What this does NOT solve (the honest boundary)

Competence grading helps only beings who *could in principle consent* at some competence level.
It does **nothing** for:

- **Animals / ecosystems** — the question is not "what is their competence?" but "are they
  rights-holders at all?" (the *interest* vs. *will* theory of rights). Competence is the
  wrong axis.
- **Fetuses / future generations** — and especially **Parfit's non-identity problem**
  (`standing.md`): a graded competence does not give a victim to a victimless wrong. That
  failure stands untouched, and may be irreducible.

So this direction would convert Standing from *one* hard problem into *two* clearer ones — a
**capacity** sub-problem (plausibly tractable via the spectrum) and a **standing-of-non-persons**
sub-problem (possibly fatal). Splitting a problem into a solvable half and a possibly-unsolvable
half is itself a result.

## The open questions (so this stays a direction, not a claim)

1. **Where is the threshold, and who measures it?** A competence score invites the very
   paternalism FDK exists to refuse — *"you are only 0.4 competent, so your yes does not
   count"* is the contented-slave problem (`consent_authenticity.md`) wearing a lab coat.
2. **Stakes-scaling**: how does required competence rise with irreversibility (candy vs.
   kidney)? This re-imports a welfare/harm judgment the gate claims to avoid.
3. **Abuse**: any capacity test is a lever for stripping rights from the inconvenient.

This is the highest-theoretical-payoff open direction (it touches both Standing and Consent-
Authenticity, the two hardest frontiers) — and it is recorded here as a *hypothesis to test*,
with its own failure modes named, not as a fix to celebrate.

*Research notes. Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust
(CC BY 4.0). Engineering: Ali Pourrahim.*
