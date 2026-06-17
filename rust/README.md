# rust — parity port of the frozen kernel (Layer 10)

A Rust port of the **frozen v1.0** legitimacy kernel (`src/lib.rs`), mirroring
`formal/Fdk.lean` and `src/fdk_kernel/kernel.py`. It now covers the **full gate**, in
two layers:

1. The **categorical core** — the 11 forbidden flags, the defensive-asymmetry excusal
   of coercion/exit-removal, and the valid-consent gate, over a flat boolean `Action`
   (`forbidden_fires` / `legitimate`).
2. The **consent/ownership path** — `check_legitimacy(action, graph)` over the richer
   `CandidateAction` / `OwnershipGraph` / `Op` lattice: A4 owner check, A3/A5/A7
   resource authorization (owner-bound), A2/A6 consent on affected humans with the
   defensive-asymmetry exception for the aggressor, and the `defends_against`
   recursion with a cycle guard. This mirrors `kernel.check_legitimacy` evaluator for
   evaluator, including the stable violation-string order.

The safety theorems are re-checked as `#[cfg(test)]` unit tests across both layers
(no-slavery, no-sovereignty, defense-never-excuses-confiscation, no-action-without-
consent, unowned-resource-denied, machine-undelegated-denied, op-lattice
READ-vs-TRANSFER, proportionate-defense-allowed, a clean consenting action, + a parity
table) — **17 tests, all pass**.

## Honest scope

- This is a **parity port of the FULL gate** (categorical core + consent/ownership
  path). The compass/ranking and the audit/capability machinery are out of scope by
  design — they live in the research layer and in AuthGate, respectively.
- **Rust ⇔ Python equivalence is tested** (the shared safety theorems + a parity
  table), **not proved**. A verified `#![forbid(unsafe_code)]` TCB and a machine-checked
  refinement to the Lean model remain open — the goal is TCB parity with AuthGate's
  verified Rust core.

## Build

The repo path `D:\جافکری\` is non-ASCII, which breaks the MSVC toolchain on object
files, and git-bash's coreutils `link` shadows MSVC `link.exe`. Build with the **GNU**
toolchain (TDM-GCC) and an ASCII target dir:

```
export PATH="/c/TDM-GCC-64/bin:$PATH"
cd rust
CARGO_TARGET_DIR=C:/fdkrustgnu cargo +stable-x86_64-pc-windows-gnu test
```

On Linux CI (the `rust` job in `.github/workflows/ci.yml`) the default toolchain works
directly — `cargo test` in `rust/`.

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Engineering: Ali Pourrahim.*
