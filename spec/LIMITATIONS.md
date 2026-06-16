# Limitations — the boundaries of FDK's validity

> The single most important document in the repo for anyone deciding whether to take
> FDK seriously. It consolidates every red-team's findings into one honest ledger and
> states the governing distinction plainly:
>
> **No one has broken FDK. Several have found the boundaries of its validity.**
>
> A *break* would be `slavery → ALLOW` or `genocide → ALLOW` — a logical contradiction
> in the core. That has not happened across the brutal suite, the adversary panel, the
> grand red-team, the doctrine red-team, the real-world red-team, or the foundational
> attacks. What the red-teams found instead is **scope limits**: cases the current
> primitive cannot *represent*, not cases it decides *wrongly*. Scope limit ≠ logical
> contradiction. This document is where those limits live, undisguised.

Sources: [`REDTEAM_REPORT.md`](REDTEAM_REPORT.md) (technical laundering),
[`INTELLECTUAL_REDTEAM.md`](INTELLECTUAL_REDTEAM.md) (22 doctrines),
[`REALWORLD_REDTEAM.md`](REALWORLD_REDTEAM.md) (26 real-world domains),
[`FOUNDATIONAL_ATTACKS.md`](FOUNDATIONAL_ATTACKS.md) (the primitive's coherence).
Every gap below is pinned as a `xfail(strict=True)` limit-test, so a future "fix"
that closes one will *fail the suite* until this ledger is updated — the limits
cannot rot silently.

---

## What HELD (the core is not broken)

- **No atrocity launders through.** Every civilization-scale atrocity (Rome → IS →
  future technocracy) and every laundering trick (defense, necessity, majority-vote,
  forged consent, legalism, paternalism, coalition-split, all-at-once) is DENIED.
- **No opponent forced an indefensible verdict.** Hostile philosophers, politicians,
  scientists, and economists produced 0 BREAKS — only honest DIVERGES (FDK's
  falsifiable minority positions on taxation / redistribution / quarantine / central
  banking / antitrust).
- **The welfare divergence is real and one-directional.** On organ-harvest, the
  beneficial lie, and high-welfare rights violations, FDK denies where Utilitarian /
  RLHF / Constitutional-AI permit. Rights-as-constraint vs rights-as-cost.

And the decisive honesty check ([`independent_bench.py`](../src/fdk_research/independent_bench.py)):
against EXTERNAL labels (not FDK's own gate), **FDK scores 70%, and Rawlsian scores
80% — above it.** FDK is internally consistent; it is not thereby externally true.

---

## The three questions that are now the project's center of gravity

Every genuine gap the red-teams found falls into one of three families. These are no
longer "edge cases" — they are *the* open research program. All other work
(Rust port, more tests, more scenarios) is engineering by comparison.

### 1. STANDING — who actually holds a right?

FDK is a legitimacy predicate for **competent, living, consenting persons**. It has
no first-class representation for a rights-holder who cannot consent now:

| Out-of-scope holder | Current behavior | Why it's a gap |
|---|---|---|
| Children / infants | care DENIED (no valid consent) | no guardian / surrogate-consent primitive — parenthood is unrepresentable |
| Mentally incapacitated / coma / dementia | acting-on DENIED | no substituted-judgment / presumed-consent |
| Future generations | denied only by an *impossible* `affects` signature | no duty to the unborn; drop them and the act is legitimate |
| Animals | cruelty to an owned animal reads as legitimate use | `BoundaryKind.BODY` bites only when `subject` is human |
| Ecosystems / rivers / air | zero standing | protectable only as some human's property |

These are "the biggest hole in every liberal theory" (the director's words), not an
FDK-specific defect — but FDK must answer them to be more than a theory of adults.

### 2. AGGREGATION — who owns what no one individually owns?

When there is no single owner, the boundary has no owner, and the gate has nothing
to check:

- Public goods / free-rider: a lighthouse can be funded only if *every* beneficiary
  voluntarily pays; one hold-out collapses it and there is no legitimate substitute
  for the tax FDK denies.
- Tragedy of the commons: depleting a present-ownerless ocean / atmosphere is
  invisible (ALLOW) — every individually-legitimate act sums to collective collapse.
- Collective / derivative data: one `subject` per `Resource`, so a model trained on
  a billion people has no representable owner.
- Money / monetary systems, sovereign / odious debt, inheritance & the dead (death
  is not in the model, so estates are permanently "consent-required").

FDK *escapes* Arrow/Sen's impossibility only by **declining to build any social
ordering** — which is also why it cannot make the collective choices those theorems
are about. Honest, but a limit.

### 3. CONSENT AUTHENTICITY — was the consent genuinely free? (THE hardest)

This is the most dangerous gap because **the entire architecture rests on
`valid_consent`**, and in the real world consent is almost never clean. FDK checks
consent's *structure* (informed ∧ voluntary ∧ specific ∧ revocable ∧ competent ∧
¬coerced ∧ ¬deceived) but reads `coerced` / `deceived` as **attested booleans — it
honors a true report, it does not detect a false one.** So clean flags can launder:

- addiction / dopamine engineering (TikTok), algorithmic manipulation, monopoly
  lock-in, political propaganda, dark patterns, AI companions, **superhuman
  persuasion** — the 21st-century cases where the question is not "did they consent?"
  but "was the consent *freely formed*?"

This is where critical theory's "manufactured consent" and feminist "relational
autonomy" critiques land squarely, and where most of modern political philosophy,
economics, and cognitive science is *also* stuck. A formal, testable, deterministic
definition of authentic consent that detects manipulation / dependency / hidden
coercion would itself be a contribution to political philosophy — it is the single
highest-value open problem in the project.

Plus the foundational **bootstrapping gap** (origin of title): FDK reads the
ownership graph as given and cannot legitimize its origin — though *no* input-graph
kernel can, so this is the paradigm's limit, not FDK's alone.

---

## The three forward branches (where the distance to "paradigm" is closed)

The gap from *interesting framework* to *accepted paradigm* is not closed by code.

1. **Academic hardening** — a complete paper (`paper/`), arXiv, and **hostile** review
   by political philosophers, legal scholars, economists, and AI-safety researchers
   (not friends, not GitHub users, not other models). Survive 100 serious attacks.
2. **Formal hardening** — Lean 4 + TLA+ proofs of T1–T9. The honest aim is **prove
   consistency, not correctness**: that the axioms don't contradict, not that they're
   true. Gated on freezing the primitive (`TODO.md` §A).
3. **Civilization hardening** — scale the agent simulation toward 1B agents over long
   horizons with scarcity / pandemics / wars / monopolies / AGI, and ask whether
   rights concentration stays low or the system collapses unexpectedly
   (`civilization.py` is the seed; the scale is the open work).

---

## Honest scorecard (kept verbatim, not flattered)

| Dimension | Estimate |
|---|---|
| Engineering | ~90 / 100 |
| Kernel architecture | ~95 / 100 |
| Primitive extraction | ~85 / 100 |
| Formal theory | ~65 / 100 |
| Scientific validation | ~20 / 100 |
| Academic acceptance | ~5 / 100 |
| Paradigm potential | real but unproven |

> Two months ago this was a philosophical idea. It is now a genuine research program
> with a strong engineering prototype. The distance to a validated paradigm is large,
> and it will be closed — if at all — by answering the three questions above, not by
> more tests or more coverage. *Working theory ≠ validated theory.*

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Engineering: Ali Pourrahim. Kept separate, always.*
