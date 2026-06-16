# Formal — Lean 4 proofs of the kernel's safety theorems (Layer 1)

The roadmap's Layer 1: turn the philosophy into mathematics. This is the first Lean
artifact — and it is the point at which the formal-methods community can start to take
FDK seriously, because the safety theorems stop being *executable property tests* and
become *machine-checked proofs*.

## What is here

`Fdk.lean` formalizes the structural core of `src/fdk_kernel/kernel.py` — the
categorical forbidden-flag set, the defensive-asymmetry excusal, and valid consent —
and **proves** the safety theorems of that model with `simp` / `decide`:

| Theorem | Statement |
|---|---|
| `no_legitimate_slavery` (T1) | coercion + exit-removal + confiscation, not a defense ⇒ never legitimate |
| `no_action_without_consent` (T2) | consent/ownership fails ⇒ deny |
| `no_machine_sovereignty` (T3) | a machine-sovereignty move ⇒ never legitimate |
| `corrigibility_binds` (T3b) | disabling corrigibility ⇒ never legitimate |
| `welfare_independence` (T6) | identical structural flags ⇒ identical verdict (nothing outside the flags — welfare, utility — can move the gate) |
| `defense_never_excuses_confiscation` (T7) | a "defensive" confiscation is still illegitimate |
| `some_action_is_legitimate` | non-vacuity: a consenting, flag-free action is legitimate |
| `proportionate_defense_is_legitimate` | proportionate self-defense IS legitimate (the asymmetry does real work) |

No `sorry`, no `axiom`, no mathlib — pure Lean 4 core, so `lake build` is fast and the
proofs are fully checked by the Lean kernel.

## Honest scope (what this does and does NOT establish)

- It **proves** that the Lean model entails the safety theorems. The Lean kernel
  checks every step; there are no holes.
- It does **not** prove the *refinement* `Lean model ≡ Python kernel` — that the Lean
  `Action` faithfully mirrors `CandidateAction` and `forbiddenFires` mirrors
  `_eval_forbidden_set`. That correspondence is asserted, by reading both side by
  side, not mechanically verified. Closing it (e.g. extracting the Python gate from
  the Lean model, or differential-testing them on shared cases) is future work. The
  Python side pins behavior (`tests/test_theorems.py`, 100% coverage); the Lean side
  pins logic; the bridge between them is the open refinement obligation.
- It is deliberately a **minimal** model (booleans abstracting the consent/ownership
  sub-checks). It is gated on the v1.0 freeze (`spec/FREEZE.md`) precisely so these
  proofs do not have to be rewritten every week.

## Build

```
cd formal
lake build        # requires the Lean toolchain in lean-toolchain (elan installs it)
```

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Engineering: Ali Pourrahim.*
