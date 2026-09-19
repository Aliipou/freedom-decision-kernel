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

### Structured ownership + consent model (de-abstracting the consent boolean)

The eight theorems above run over a model that collapses the whole consent/ownership
path into a single `validConsent` boolean — the exact part the formal-methods critique
says is hidden. `Fdk.lean` now also carries a **structured** model: a finite ownership
`Graph` (`humanOwns` / `machineOwner` / `delegated`), explicit `uses` / `affects` /
`consents` lists, and a `legitimateFull` predicate that mirrors the TLA+ `Legitimate`
(`spec/fdk.tla`) — `HasOwner` (A4) + `ResourceAuthorized` (A3/A7, owner-bound) +
`HasValidConsent` (A2/A6, consent on every affected human except the excused aggressor)
+ effective-forbidden-empty. The consent/ownership obligations are proved *directly*,
reaching inside the boolean the original model abstracted away:

| Theorem | Statement |
|---|---|
| `no_action_on_nonconsenting_person` (TF1) | an affected human (not the excused aggressor) with no valid consent on record ⇒ not `legitimateFull` (the de-abstracted T2) |
| `unowned_resource_use_denied` (TF2) | a human using a resource it does not own ⇒ not `legitimateFull` |
| `machine_undelegated_denied` (TF3) | a machine using an *undelegated* resource ⇒ not `legitimateFull` (owner-bound A3/A7) |
| `welfare_independence_full` (TF6) | equal structural inputs (graph, actor, uses, affects, consents, aggressor, core flags) ⇒ identical `legitimateFull` verdict |
| `consenting_owner_action_is_legitimate` | non-vacuity: a consenting owner using its own resource IS `legitimateFull` |
| `machine_undelegated_denied_concrete` | a `decide`-checked instance of TF3 on a concrete graph |

This closes part of the "the Lean model abstracts consent into one boolean" objection:
the consent and ownership structure is now explicit, and the denials are proved over it.

No `sorry`, no `axiom`, no mathlib — pure Lean 4 core, so `lake build` is fast and the
proofs are fully checked by the Lean kernel (`#print axioms` shows only the standard
`propext` / `Classical.choice` / `Quot.sound`, and the `decide` theorems depend on none).

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
