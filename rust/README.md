# rust — parity port of the frozen kernel (Layer 10, start)

A Rust port of the **frozen v1.0** legitimacy kernel's categorical core (`src/lib.rs`),
mirroring `formal/Fdk.lean` and `src/fdk_kernel/kernel.py`: the 11 categorical forbidden
flags, the defensive-asymmetry excusal of coercion/exit-removal, and the valid-consent
gate. The same safety theorems are re-checked as `#[cfg(test)]` unit tests
(no-legitimate-slavery, no-machine-sovereignty, defense-never-excuses-confiscation,
non-vacuity, proportionate-defense-allowed, + a parity table) — **8 tests, all pass**.

## Honest scope

- This is a **parity port of the categorical core** (consent/ownership are abstracted
  into one `valid_consent` boolean, exactly as in the Lean model). It is the first step
  of Layer 10, not a full Rust kernel.
- **Rust ⇔ Python equivalence is tested** (the shared safety theorems + a parity
  table), **not proved**. A full port (the consent/ownership path, the operation
  lattice, the `defends_against` recursion) and a verified `#![forbid(unsafe_code)]`
  TCB remain open — the goal is TCB parity with AuthGate's verified Rust core.

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
