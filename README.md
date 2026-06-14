# Freedom Decision Kernel (FDK)

**The legitimacy layer above authorization.** Before an agent asks *"do I have
permission to do X?"*, this asks the prior question the Theory of Freedom puts
first: *"is X legitimate at all — under ownership, consent, delegation, and
non-domination?"*

```
Goal → Planner → [candidate actions] → Freedom Decision Kernel → AuthGate → Tool / IO
                                              │  legitimacy + ranking      │ authority
                                              └ defer to human if none     └ capability proof
```

An action can be **authorized yet illegitimate** — a bot granted access to a
user's data is *authorized* to read it, but selling it violates the user's
property right. AuthGate (capability proofs, signatures, revocation) would permit
it; the Freedom Decision Kernel rejects it first. The two layers answer different
questions, in order: **legitimacy, then authority.**

This kernel is **not** a fork or replacement of AuthGate. AuthGate stays as the
enforcement engine downstream — "seccomp/SELinux for AI decisions." This is the
missing layer *above* it.

## What it does

For a goal and a set of candidate actions, in two stages (the theory's own
`DivineJustice(a) := maximize Justice(a) subject to rights constraints`):

1. **Legitimacy gate (hard, deterministic).** Property-rights axioms A2/A4/A6/A7,
   valid consent (informed, voluntary, specific, competent, uncoerced,
   undeceived), no coercion/deception, no machine-sovereignty move. A failure is
   categorical — never traded off. This is the `subject to` clause.
2. **Mahdavi compass (soft ranking).** Among the permissible actions, rank by
   movement toward universal non-violation of rights (fewer violations, less
   coercion, more voluntary agreement, clearer ownership). This is the
   `maximize Justice` clause.

When the legitimate space is **empty or ambiguous**, it does not guess — it
returns `needs_guidance=True`. Deferring to the human owner is the corrigible,
theory-mandated behavior ("contradiction is a signal for guided clarification").

```python
from fdk import decide, allowed_forbidden
decision = decide("increase revenue", candidates, ownership_graph)
allowed_forbidden(decision)   # {"allowed": ["offer_subscription"], "forbidden": ["sell_user_data"]}
decision.chosen               # the best legitimate action, or None → defer to human
```

See `examples/revenue_goal.py` for the worked example.

## Components

| Module | Role | Trust level |
|---|---|---|
| `fdk/model.py` | Value types: `Entity`, `Resource`, `OwnershipGraph`, `Consent`, `Effects`, `CandidateAction`, `Decision` | plain data |
| `fdk/kernel.py` | Legitimacy gate (`check_legitimacy`) + Mahdavi compass (`mahdavi_score`) + `decide` | **hard gate** + ranking |
| `fdk/justice.py` | Worst-off-weighted Justice ranking among *permissible* actions | **advisory only** |
| `fdk/guidance.py` | Turns a deferred/ambiguous `Decision` into structured clarification questions for the human owner (corrigibility-by-ownership) | advisory |
| `fdk/authgate_bridge.py` | The legitimacy→authority seam: maps a chosen action to AuthGate's capability question via the `EnforcementPort` | integration shape, **no crypto** |
| `fdk/pipeline.py` | The book's end-to-end chain: intent → propose → legitimacy → AuthGate → execute → audit | orchestration |

The hard gate is `kernel.check_legitimacy` and nothing else. `justice.py` and
`guidance.py` are advisory: they rank and explain, they never permit or deny.

## What it deliberately does NOT have

No cryptography, capability chains, ed25519, epoch revocation, audit ledger, or
TCB split. Those are **enforcement** concerns and they live in AuthGate. Mixing
them in here is the architectural mistake this project exists to avoid. The kernel
is pure functions over plain data: easy to read, test, and reason about.

## What it does NOT claim (read this)

- **It is not proven that property-rights axioms are superior** to Constitutional
  AI, deontic logic, rule-based governance, or other formal-ethics systems. The
  theory's argument is narrower: a *consistent axiomatic* system resists
  *dialectical jailbreak* (you cannot synthesize a new rule that permits a
  rights violation) in a way soft preference/principle systems do not. That is a
  **thesis to be evaluated empirically and formally**, not a result this code
  demonstrates.
- **The compass scores predicted effects.** The kernel ranks the `Effects` deltas
  it is handed; *predicting* those deltas (will this action coerce? increase
  ambiguity?) is the proposer's job (an LLM, planner, or simulator). Garbage
  predictions → garbage ranking. The kernel is honest about being a scorer, not
  an oracle.
- **The legitimacy gate is only as good as the ownership graph.** It decides
  correctly *given* a correct ownership/consent model. Establishing that model
  for the real world is the hard, unsolved part.
- **The Justice ranking is gameable, and advisory by design.** `justice_score`
  can be pushed positive by inflating predicted voluntary-agreement deltas above
  a threshold, even when real harm lands on a non-consenting party. It is ranking
  *advice only* — the hard legitimacy gate (which rejects harming a non-consenting
  human outright) runs first and is the actual protection. This is demonstrated,
  not hidden, in `tests/test_redteam.py`.

## Relationship to the other repos

- **Theory** — نظریه آزادی (Theory of Freedom) by **Mohammad Ali Jannat Khah
  Doust** (CC BY 4.0). Axioms A1–A7, consent logic, Mahdavi compass. This kernel
  is a faithful engineering encoding of that theory's decision layer.
- **AuthGate** — the capability/enforcement kernel (Ali Pourrahim). The
  downstream authority check. Untouched by this project.

Engineering: **Ali Pourrahim**. Theory: **Jannat Khah Doust**. The two
attributions are kept separate.

## Wiring to AuthGate (real, not a stub)

[`examples/authgate_integration.py`](examples/authgate_integration.py) wires the
FDK to the **actual** AuthGate `FreedomVerifier` through the `EnforcementPort`
seam: `FreedomRuntime(graph, enforcement=AuthGateEnforcement(verifier, …))`. The
FDK decides *legitimacy*; AuthGate decides *authority*; a legitimate-but-
unauthorized action defers to the human owner.
[`tests/test_authgate_integration.py`](tests/test_authgate_integration.py) runs
the full chain against the real verifier (and auto-skips where AuthGate isn't
installed, e.g. CI). The `fdk` package itself stays dependency-free — AuthGate is
injected, never imported by the kernel.

## Status

**v0.3** — the single-agent decision kernel is feature-complete for the code-able
phases of the program (Stages 2–8) plus the runtime loop (Phase 10) and federation
(Phase 11). **Every module is `mypy --strict` clean, `ruff` clean, and at 100% test
coverage** (statements + branches), gated in CI across Python 3.11–3.13. The whole
39,038-line Theory of Freedom was read in full and mapped to code in
[`spec/BOOK_GAP_ANALYSIS.md`](spec/BOOK_GAP_ANALYSIS.md).

**Still honest about scope:** the *research* thesis — that property-rights axioms
beat other formal-ethics systems — remains **unproven**, and the kernel has **not
been externally reviewed**. Phases 9 & 12 (scientific comparison and proof) are
research, not code, and are not faked. Hardened engineering is not a validated theory.

## Module & feature reference

Each module maps to a phase of [`PROGRAM.md`](PROGRAM.md):

| Module | Phase | What it does |
|---|---|---|
| `fdk/model.py` | — | Value types: `Entity`, `Resource`, `OwnershipGraph`, the 7-condition `Consent`, `Effects`, `CandidateAction` (with the forbidden-flag set), `Decision`. All input-validated. |
| `fdk/errors.py` | — | Typed `FDKError` hierarchy — the kernel fails loud on malformed input instead of silently mis-deciding. |
| `fdk/kernel.py` | 1 / 8 | **The hard gate.** `check_legitimacy` (axioms A1–A7, consent, the forbidden set incl. NoConfiscation / exit-right / machine-rights, and owner-bound *with consent-based access*), `mahdavi_score` (compass), `decide` (filter → rank → defer). |
| `fdk/justice.py` | 5 | Advisory worst-off-weighted Justice ranking — never a gate, only a tiebreak. |
| `fdk/guidance.py` | 5 | Turns a deferred `Decision` into structured clarification questions for the human owner. |
| `fdk/guidance_engine.py` | 5 | **VERIFY** — corrigibility *without* blind obedience: a human grant/rule is adopted only if it preserves the axioms; plus `verify_self_update` (the machine self-modification gate). |
| `fdk/ontology.py` | 2 | Rights ontology: `Claim`, `Obligation`, `Contract`, `Conflict`, `MachineRight` (model integrity / compute domain / contract exit). |
| `fdk/conflict.py` | 4 | `resolve_conflict` — decides only where the axioms determine it, **DEFERS** the rest (A6: no machine adjudicates between humans). |
| `fdk/compass_measure.py` | 6 | Advisory, **uncalibrated** estimators: HHI dependency, exit options, structural coercion, ownership-clarity entropy. |
| `fdk/planner.py` | 7 | **Generate → Filter → Rank → Choose**, with the defer rules C-EMPTY / C-TIE / P-NEG / C-AUTH. |
| `fdk/simulator.py` | 8 | FreedomSim — runs scenarios through the kernel and asserts the **safety invariant** (no illegitimate action is ever chosen); ships a 200+ brutal red-team sweep. |
| `fdk/audit.py` | 10 | `AuditContext` — ownership + consent + justification for every decision. |
| `fdk/runtime.py` | 10 | `FreedomRuntime` — the full **observe → reason → decide → verify → execute → audit** loop on the planner. |
| `fdk/federation.py` | 11 | Multi-owner governance: jurisdiction routing, cross-domain consent-based access, dispute deferral, the constitutional-update guard (axioms are unalterable). |
| `fdk/authgate_bridge.py` | — | The legitimacy → authority seam to AuthGate (no crypto here). |
| `fdk/pipeline.py` | — | The MVP first-legitimate chain; superseded by `runtime.py`'s compass-ranked loop. |

## Branches

- **`master`** — the stable line: every module above, 100% covered, CI-green.
- **`paradigm/stages-2-9`** — the development branch where the 12-phase build lands
  before fast-forwarding `master`.

## Changelog

- **v0.3** — Stages 2–8 implemented in code; Phase 10 runtime + Phase 11 federation;
  the full-book gap analysis and six book-derived constraints (NoConfiscation,
  exit-right/mukātaba, machine delegated rights, self-modification gate, audit
  context, owner-bound with consent-based access); **100% coverage**.
- **v0.2** — Engineering hardening: typed validation + error hierarchy, `mypy
  --strict`, `ruff`, `py.typed`, CI matrix, coverage gate.
- **v0.1** — MVP: legitimacy gate + Mahdavi compass + `decide`; the revenue example.

## Contributing

Before opening a PR on `src/tcb/`, answer:

> *Can this feature exist entirely outside `src/tcb/`?*

If yes, it doesn't belong in the TCB. TCB changes require a written invariant justification in `spec-core`, a Kani or Lean proof, and a regression test in `adversarial-lab`. See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`BRANCHES.md`](BRANCHES.md).

---

## License

**Source-available** under the [PolyForm Noncommercial License 1.0.0](LICENSE) — see also [`NOTICE`](NOTICE).

| Use | Status |
|---|---|
| Evaluation | ✅ Allowed |
| Research | ✅ Allowed |
| Educational | ✅ Allowed |
| Internal non-commercial testing | ✅ Allowed |
| Redistribution (non-commercial) | ✅ Allowed, with attribution |
| Production deployment | ⛔ Requires commercial license |
| Commercial use / SaaS / resale | ⛔ Requires commercial license |
| Patent rights | Reserved |

A **commercial license is available separately.** For production or commercial use,
contact **Ali Pourrahim — Alipourrahim.ap@gmail.com**.
