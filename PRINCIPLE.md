# The Authority Principle

> No entity — human, AI agent, robot, or quantum computer — can **create or expand
> authority merely by possessing information or compute**. Authority is granted only
> through explicit, auditable, attenuable rules.

This is the one principle that unifies the whole ecosystem. Every project is an
instance of it; no domain (banking, robotics, energy, medical, …) is part of the core.

## Formal statement

Let authority be an element of a lattice `(A, ⊑)` where `a ⊑ b` means "a grants no
more than b". `DENY` is the bottom `⊥`; a full grant is the top.

- **grant(actor, capability)** — the *only* operation that can raise authority. It is
  explicit, signed, auditable, revocable. It is **not** a runtime composition; it is an
  issuance.
- **compose(base, k₁…kₙ)** — every runtime combination of a base authority with any
  number of *constraint inputs* (legitimacy, fairness, safety, privacy, legal, budget,
  risk, environmental, human-approval, …).

**Axiom — No Amplification.** For all base authority `a` and all constraint inputs
`k₁…kₙ`:  `compose(a, k₁,…,kₙ) ⊑ a`.

Information and compute enter the system **only** as constraint inputs — they can
produce evidence that *narrows*, never an issuance that *grants*. Therefore neither
information nor compute can amplify authority.

- **Corollary — Attenuation.** Delegation only narrows: `delegate(a) ⊑ a`.
- **Corollary — Default-deny.** Absent an explicit grant, authority is `⊥` (DENY).

## Proof status across the ecosystem (honest)

| Claim | Where | Status |
|---|---|---|
| `compose` is monotone non-increasing (No Amplification) | `fdk_kernel/authority_algebra.py` | **proven exhaustively** (narrow_only, fdk_cannot_grant, bounded_by_ceiling, idempotent, order_independent) + `tests/test_principle.py` |
| delegation attenuation | AuthGate (Rust) | Lean theorems (anti-monotone) + Kani `prop_attenuation` |
| default-deny | AuthGate (ownerless/no-claim → DENY) + boundary-guard (`default: deny`) | enforced + tested |
| the architecture itself gains no un-granted coupling | boundary-guard | CI-enforced |

## How it unifies the projects

- **AuthGate** — the *grant + verify* side (authority origin and check).
- **FDK** — the *narrowing* side (constraints; proven it can only narrow).
- **boundary-guard** — the principle applied to *architecture* (no module gains
  authority/coupling it was not granted).
- **crypto-inventory** — the principle's *crypto corollary*: a broken algorithm may
  prove identity falsely, but identity must never, by itself, grant authority — so
  authority must not rest on cryptography alone.

Domains are **consumers** of this principle, not new cores. The core knows nothing of
any domain.

## What this is NOT

Not a claim that the ecosystem is built or adopted. The principle is formal and
*partly* proven; turning it into infrastructure needs years of industrial validation
and adoption — not more architecture. Authority-by-policy is **complementary** to
strong (post-quantum) cryptography, not a replacement for it.
