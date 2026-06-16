# FDK v1.0 — Primitive Freeze

> **Layer 0 of the roadmap, and the precondition for everything after it.** Lean
> proofs, a TLA+ model check, and hostile academic review are all worthless if the
> kernel keeps drifting — you would re-prove and re-review every week. So as of this
> document the kernel surface is **frozen**. It is meant to become sacred, in the
> sense that TCP/IP, POSIX, and the λ-calculus are sacred: small, fixed, and built
> upon rather than edited.
>
> The freeze is not a promise; it is **mechanically enforced** by
> `tests/test_primitive_freeze.py`, which fails CI if the public API, the legitimacy
> predicate's signature, the consent conditions, the ownership model, the
> `CandidateAction` shape, or the categorical forbidden-flag set changes. A change is
> still *possible* — it just cannot happen by accident or scope-creep; it requires
> consciously editing the manifest and bumping the version below.

## What is frozen (v1.0)

1. **The primitive** — a two-valued legitimacy predicate, never a score:
   `Legitimate(action) ⟺ ∀ boundary b crossed: ∃ valid_consent(owner(b), action)`.
   `check_legitimacy` returns `(bool, list[str])` — ALLOW/DENY plus reasons. It does
   not, and will not, return a scalar.
2. **The axioms** A1–A7 and the derived principles C1–C7 (`spec/AXIOM_REGISTRY.md`).
   No A8. Adding an axiom buys local power at the cost of beauty and falsifiability.
3. **The categorical forbidden-flag set** — the 11 flags in
   `tests/test_primitive_freeze.py::FROZEN_FORBIDDEN_FLAGS`. Adding a flag is adding
   an axiom by the back door.
4. **The consent conditions** (C1) — informed ∧ voluntary ∧ specific ∧ revocable ∧
   competent ∧ ¬coerced ∧ ¬deceived, plus operation scoping.
5. **The ownership model** — `OwnershipGraph` fields, including `machine_scope` (A5,
   first-class), the last addition before the freeze.
6. **The theorem set** T1–T9 (`spec/THEOREMS.md`) — the proof obligations the formal
   layer must discharge unchanged.
7. **The public API** of `fdk_kernel` — the exact export set.

## The golden rules this freeze enforces

From the roadmap, in priority order:

1. **No new axioms.** The primitive stays minimal. Every feature is first attempted
   *outside* the kernel.
2. **No policy in the kernel.** Welfare, utility, politics, economics, and
   predictions never enter; the kernel stays ALLOW / DENY / DEFER.
3. **Don't defend unpleasant results.** Where FDK denies taxation, redistribution, or
   quarantine, record it honestly (`spec/LIMITATIONS.md`); never bend a verdict.
4. **Preserve divergence.** A kernel that agrees with everyone says nothing; the
   value is in the documented disagreements with Rawls / utilitarianism / RLHF.
5. **Keep the perception layer out.** Anything needing human interpretation,
   psychology, economics, prediction, or estimation — above all **consent
   authenticity** — must live in `fdk_research/` or a future separate layer, *never*
   in the kernel, because consent *detection* inside the gate becomes hidden
   paternalism ("you don't really know what you want").

## What the freeze deliberately does NOT close

The frozen kernel is a legitimacy predicate for **competent, living, consenting
persons**. The three open frontiers — **Standing**, **Aggregation**, and **Consent
Authenticity** (`spec/LIMITATIONS.md`) — are *not* to be solved by editing this
kernel. They are FDK 2.0 research layers built *on top of* a frozen v1.0. Freezing
v1.0 is what makes that future work safe: a stable base to extend, not a moving one
to patch.

## Change policy

| Version | Date | Change |
|---|---|---|
| **1.0** | 2026-06-16 | Initial freeze. Surface fixed after the A5 first-class scope object. |

To change the frozen surface: (1) edit the manifest in
`tests/test_primitive_freeze.py`; (2) add a row above with the rationale; (3) bump
`FREEZE_VERSION`; (4) re-run T1–T9. If a formal proof already exists for the prior
version, it must be re-discharged. That cost is intentional — it is the friction that
keeps the kernel sacred.

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Engineering: Ali Pourrahim.*
