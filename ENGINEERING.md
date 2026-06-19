# What this repository demonstrates (read this if you're evaluating the work, not the theory)

> Honest framing, because the theory under-delivered: the **"theory of freedom"** claim has
> largely collapsed under this project's own attacks (`paper/README.md`). What the repository
> actually demonstrates is **engineering and research discipline** — and, by the project's own
> brutal scorecard, that is its highest-value output today.

| What | Probability it's the real value |
|---|---|
| New philosophical paradigm | ~5% |
| Independent scientific theory | ~10–20% |
| Useful decision framework | ~50% |
| Lock-in analytics product | ~40–60% |
| **Showcase of systems-engineering + research discipline** | **80%+** |

## 1. Systems engineering (the discipline is the point)

- **A brutal architectural boundary, mechanically enforced.** A deterministic, non-semantic
  kernel (`src/fdk_kernel/`) and an experimental layer (`src/fdk_research/`) with a one-way
  dependency — *enforced* by a test that fails CI if the kernel ever imports research
  (`tests/test_boundary.py`, static + dynamic).
- **A frozen trusted core.** The kernel's public surface, predicate signature, and axiom
  fields are pinned by `tests/test_primitive_freeze.py` against `spec/FREEZE.md` — drift is a
  CI failure, not a code-review hope.
- **Four independent checkers of the same logic.** Python property tests (Hypothesis), **Lean 4**
  (theorems, zero `sorry`), **TLA+/TLC** model checking, and a **Rust** parity port — plus
  differential refinement tests bridging them (CompCert/seL4 style).
- **Gate discipline.** 100% line+branch coverage gate, `ruff`, `mypy --strict`, multi-version CI.
- **Fail-closed product layer.** `src/fdk_runtime/` turns the gate into a deployable policy
  engine where *every* error path (malformed input, raising oracle, raising audit sink) yields
  DENY, never ALLOW — the cardinal property of an authorization component, pinned by tests.
- **A clean cross-system seam.** FDK↔AuthGate integrate through a JSON contract
  (`PolicyDecision`), not shared code, with drift-guard tests on both sides.
- **Specification & auditability culture.** `spec/` carries the ontology, axiom registry,
  boundary definitions, and theorem ledger — every verdict traceable to a written rule.

## 2. Research discipline (the rarer skill)

The unusual thing here is not that a theory was built; it's that it was **attacked to
destruction by its own author**, in writing, with the conclusions reported in full:

- **Adversarial self-refutation.** Twelve `paper/` documents are *kill attempts* — five enemy
  dossiers (Rothbard/Nozick/Rawls/Sen/Ostrom), a reverse-discrimination test, a steelman of
  the strongest rival (Pettit), and a foundational circularity attack — not defenses.
- **Conceding one's own overclaims.** `red_team_the_verdict.md` downgrades the project's *own*
  arguments (the foundationalism papers "prove too much"; "0/61" is *none-found*, not proven;
  `r²=0.97` is **tautological**, not a discovery).
- **Refusing to name a pattern prematurely.** When a residual appeared, it was left as `ε` and
  shown to be a known variable (`alternatives`) — explicitly *not* christened "reversibility,"
  the exact error the project had made before.
- **Falsifiable framing.** The surviving claims are reduced to measurable tests (discriminant
  validity, ΔR², a residual decomposition that was actually *run* — `examples/lockin_experiment.py`)
  with the honest verdict that the data to settle them does not yet exist.

## 3. The honest takeaway

As a contribution to political philosophy, this is a *formalization of existing ideas*, not a
paradigm. As an artifact, it demonstrates: clean architecture under a hard trust boundary,
formal methods across four toolchains, fail-closed product engineering, cross-system contract
design, and — most rarely — the willingness to **falsify your own thesis and publish the
negative result**. Those are the skills of a systems engineer and an honest researcher, and
on today's evidence they are worth more than the theory that occasioned them.

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Engineering: Ali Pourrahim. The negative results are deliberate and are part of the evidence.*
