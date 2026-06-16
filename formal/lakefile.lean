import Lake
open Lake DSL

package «fdk» where
  -- pure Lean 4 core, no mathlib (fast, self-contained build)

lean_lib «Fdk» where
  -- the formalized kernel core + the proved safety theorems
