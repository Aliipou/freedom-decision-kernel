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

### Structured consent / ownership model (addresses EXPERT_REVIEW §3)

The eight theorems above run on a model where the whole consent/ownership path is one
boolean (`validConsent`). The formal-methods critic (`spec/EXPERT_REVIEW.md` §3) objects
that this "says almost nothing about the code that does the work." So `Fdk.lean` now also
carries a finite **structured** model that opens that boolean up — an ownership `Graph`
(`HasOwner`, `ResourceAuthorized`, `HasValidConsent`) and a `legitimateFull` predicate that
mirrors TLA+ `Legitimate` (`spec/fdk.tla`): owner-bound + every resource authorized +
per-person consent on every affected human (except the aggressor under a valid defense) +
effective-forbidden set empty. Resources/entities/flags are small finite enums, so every
quantifier reduces to a `List.all`/`List.any` and `simp`/`decide` close the goals.

| Theorem | Statement |
|---|---|
| `no_action_on_nonconsenting_person` | affects a human (not the defended aggressor) with no valid consent ⇒ deny (structured T2, over a real per-person consent list) |
| `unowned_resource_use_denied` | a human using a resource it does not own ⇒ deny (`ResourceAuthorized` fails) |
| `machine_undelegated_denied` | a machine using a resource it has no delegation for ⇒ deny (owner-bound A7) |
| `welfare_independence_full` | actions agreeing on every structural field get the same verdict (structured T6: no welfare/utility input) |
| `consenting_owner_action_is_legitimate` | non-vacuity: a consenting owner acting within its ownership IS legitimate (`decide` on a concrete graph) |
| `delegated_machine_action_is_legitimate` | a machine on a delegated, owner-owned resource IS legitimate (positive owner-bound delegation branch) |

Still abstracted (open Layer-1 TODO, documented in-file as a comment, **never** a `sorry`):
the operation lattice (`Op`), subject-based resource consent, and nested/recursive defense
with the `_seen` cycle guard — the same faithful-subset boundary the TLA model keeps.

No `sorry`, no `axiom`, no mathlib — pure Lean 4 core, so `lake build` is fast and the
proofs are fully checked by the Lean kernel. (`#print axioms` on the structured theorems
shows only `propext` / `Quot.sound`, never `sorryAx`.)

## Honest scope (what this does and does NOT establish)

- It **proves** that the Lean model entails the safety theorems. The Lean kernel
  checks every step; there are no holes.
- It does **not** *prove* the refinement `model ≡ Python kernel`. But that gap is no
  longer merely asserted — it is differential-tested on TWO levels:
  - `tests/test_lean_refinement.py` mirrors the Lean `forbiddenFires`/`legitimate`
    and checks the **categorical core** (all 11 flags + defensive-asymmetry excusal)
    against `check_legitimacy` over 2000+ actions — agrees bit-for-bit.
  - `tests/test_tla_refinement.py` transcribes the **full** TLA+ `Legitimate`
    predicate (HasOwner + ResourceAuthorized + HasValidConsent + defense) and checks
    the *complete* verdict — consent/ownership path included — over 3000 actions in
    the model's faithful subset. This closes the formal-methods objection that the
    categorical-only test cannot catch a consent-path bug.
  This is the standard practical bridge (CompCert uses it too): it does not *prove*
  refinement, but it *catches* the "spec correct, Python wrong" divergence a refinement
  proof exists to exclude. A full *mechanical* refinement (seL4-style) remains open.
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
