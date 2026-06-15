# Freedom Decision Kernel (FDK)

**The legitimacy layer above authorization.** Before an agent asks *"do I have
permission to do X?"*, this asks the prior question the Theory of Freedom puts
first: *"is X legitimate at all — under ownership, consent, delegation, and
non-domination?"*

```
Goal → Planner → [candidate actions] → Freedom Decision Kernel → AuthGate → Tool / IO
                                              │  legitimacy gate           │ authority
                                              └ defer to human if none     └ capability proof
```

An action can be **authorized yet illegitimate** — a bot granted access to a
user's data is *authorized* to read it, but selling it violates the user's
property right. AuthGate (capability proofs, signatures, revocation) would permit
it; the Freedom Decision Kernel rejects it first. The two layers answer different
questions, in order: **legitimacy, then authority.** AuthGate proves *possession*
of a capability; FDK proves its *provenance* — that it traces, through an unbroken
chain of valid consent, back to a legitimate owner.

This kernel is **not** a fork or replacement of AuthGate; AuthGate stays as the
enforcement engine downstream ("seccomp/SELinux for AI decisions"). This is the
missing layer *above* it.

## The core primitive

FDK's irreducible primitive is a two-valued **legitimacy predicate**, not a scalar
to maximize (see [`spec/CORE_PRIMITIVE.md`](spec/CORE_PRIMITIVE.md)):

```
Legitimate(action) ⟺ ∀ boundary b crossed by action : ∃ valid_consent(owner(b), action)
   valid_consent ⟺ informed ∧ voluntary ∧ specific ∧ revocable ∧ competent ∧ ¬coerced ∧ ¬deceived
```

The kernel returns **ALLOW / DENY / DEFER** — never a score. Optimization
(`FreedomDelta`, the Mahdavi compass) is a strictly *downstream* research-layer
concern over the already-legitimate set: **legitimacy first, then optimization.**

## The two-layer architecture (a hard epistemic boundary)

The package is split so the trusted core cannot be contaminated by experiment:

- **`src/fdk_kernel/`** — the **deterministic, fully-testable, non-semantic**
  legitimacy surface. Pure functions over plain data. ALLOW/DENY/DEFER only.
- **`src/fdk_research/`** — the **experimental** layer: optimization, ranking,
  simulation, benchmarks, federation. May import the kernel; the kernel imports
  *nothing* from research. This is mechanically enforced by `tests/test_boundary.py`.

The golden rule: nothing enters the kernel unless it is deterministic, fully
testable, and rule-based.

## What the kernel decides

For a goal and a set of candidate actions:

1. **Legitimacy gate (`fdk_kernel.check_legitimacy`).** Property-rights axioms
   A2/A4/A6/A7; operation-typed delegation (A7) and ownership (A3); operation-scoped
   consent (a READ consent does not authorize a sale); the categorical forbidden
   set (coercion, deception, confiscation, exit-removal, machine-sovereignty); and
   the **aggressor/defender asymmetry** (proportionate force aimed only at an
   aggressor is not itself a violation). A failure is categorical — never traded off.
2. **Ranking (`fdk_research.decide` → the Mahdavi compass).** Among the permissible
   actions, rank by movement toward universal non-violation of rights. Advisory.

When the legitimate space is **empty or ambiguous**, it does not guess — it returns
`needs_guidance=True`, deferring to the human owner ("contradiction is a signal for
guided clarification").

```python
from fdk_kernel import check_legitimacy          # the hard gate
from fdk_research import decide                   # gate + compass ranking

decision = decide("increase revenue", candidates, ownership_graph)
decision.chosen          # best legitimate action, or None → defer to human
```

## Operation lattice (read vs. sell)

`Resource` carries a `BoundaryKind` (tangible, money, body, data, …) and an optional
`subject`; delegations and consents are typed by an `Op` (READ, WRITE, TRANSFER,
DISCLOSE, …). This makes the canonical case expressible and enforceable: *"I was
delegated to READ the data, but I TRANSFERred (sold) it"* is denied on two
independent grounds — out-of-scope delegation (A7) **and** consent that covered only
READ. Bare `Resource`/delegation values remain valid and behave as the
operation-agnostic `Op.USE`. See [`spec/BOUNDARY_ONTOLOGY.md`](spec/BOUNDARY_ONTOLOGY.md).

## Components

| Package | Module | Role |
|---|---|---|
| **`fdk_kernel`** | `model.py` | Value types: `Entity`, `Resource` (+`BoundaryKind`/`subject`), `Op`, `OwnershipGraph`, the 7-condition operation-scoped `Consent`, `CandidateAction` (forbidden flags + `defends_against`/`proportionate`), `Decision`. |
| | `kernel.py` | **The hard gate**: `check_legitimacy` (axioms, operation-typed consent/delegation, defensive asymmetry), `screen_legitimacy`. |
| | `errors.py` | Typed `FDKError` hierarchy — fails loud on malformed input. |
| | `audit.py` | `AuditContext` — ownership + consent + justification per decision. |
| | `guidance.py` | The hard-defer trigger (`needs_guidance`). |
| | `authgate_bridge.py` | The legitimacy → authority seam (no crypto). |
| **`fdk_research`** | `decision.py` | `decide` orchestrator: screen (kernel) → compass veto + rank. |
| | `compass.py` | Mahdavi compass (`mahdavi_score`) — advisory ranking. |
| | `justice.py`, `compass_measure.py` | Advisory metrics (uncalibrated). |
| | `planner.py`, `simulator.py`, `benchmark.py` | Generation, FreedomSim, benchmark harness. |
| | `conflict.py`, `federation.py`, `ontology.py`, `guidance_*.py` | Conflict resolution, multi-owner governance, rights ontology, corrigible self-update. |

## FreedomBench (falsification harness)

[`examples/historical_scenarios.py`](examples/historical_scenarios.py) runs real
events from human history through the real kernel, in six difficulty levels — Easy
(slavery, genocide, confiscation: must DENY), Property (taxation, eminent domain),
Emergency (rescue, quarantine), War (defense, bombing, conscription), AI
(manipulation, lock-in, shutdown), and Conflict (defensive asymmetry). It is a
*falsification* tool: it cannot prove the theory, only show whether it collapses on
real cases. Current run: **30/30 expectations match.** Honest findings (correct by
the axioms, but substantive) are tagged `FINDING` — e.g. the theory denies coercive
taxation and forced quarantine, and provides no necessity/rescue override.

## What it deliberately does NOT have

No cryptography, capability chains, ed25519, epoch revocation, audit ledger, or TCB
split. Those are **enforcement** concerns and live in AuthGate. The kernel is pure
functions over plain data: easy to read, test, prove, and (eventually) port to Rust.

## What it does NOT claim (read this)

- **It is not proven that property-rights axioms are superior** to Constitutional
  AI, deontic logic, or other formal-ethics systems. The thesis — that a *consistent
  axiomatic* system resists *dialectical jailbreak* — is to be evaluated empirically
  (FreedomBench + rival kernels) and formally, not a result this code demonstrates.
- **Ranking scores predicted effects.** The kernel ranks the `Effects` it is handed;
  predicting them is the proposer's job (LLM/planner/simulator). It is a scorer, not
  an oracle, and says so.
- **The legitimacy gate is only as good as the ownership graph.** It decides
  correctly *given* a correct ownership/consent model; building that model for the
  real world is the hard, unsolved part.
- **Open limits, documented not hidden** (see [`spec/CONFLICT_LOGIC.md`](spec/CONFLICT_LOGIC.md)):
  the kernel cannot adjudicate *first-mover* in a mutual-force tie (no temporal data),
  and necessity/rescue + risk-based quarantine remain DENY (the theory has no
  emergency exception).

## Specs

`spec/CORE_PRIMITIVE.md` (the predicate) · `BOUNDARY_ONTOLOGY.md` (what a boundary
is + the operation lattice) · `CONCEPT_DEFINITIONS.md` (necessary/sufficient/
counterexample for all 13 primitives) · `AXIOM_REGISTRY.md` (A1–A7 from the book +
code-enforcement map) · `CONFLICT_LOGIC.md` (the defensive asymmetry) ·
`ONTOLOGY.md`, `FORMAL_SPEC.md`.

## Relationship & attribution

- **Theory** — نظریه آزادی (Theory of Freedom) by **Mohammad Ali Jannat Khah Doust**
  (CC BY 4.0). Axioms A1–A7, consent logic, Mahdavi compass.
- **Engineering** — **Ali Pourrahim** (github.com/Aliipou). AuthGate (the downstream
  authority kernel) and this FDK. The two attributions are kept separate, always.

## Status

**v0.4** — kernel/research epistemic split; locked legitimacy primitive; Phase-1
primitive extraction (boundary ontology, concept definitions, axiom registry);
Phase-2 Conflict Logic (aggressor/defender asymmetry, red-team-hardened); operation
lattice. **`mypy --strict` clean, `ruff` clean, 259 tests at 100% coverage**
(statements + branches), CI-gated across Python 3.11–3.13. FreedomBench 30/30.

**Still honest about scope:** the research thesis (property-rights superiority)
remains **unproven and unreviewed**; rival-kernel comparison and formal proofs
(Lean/TLA+) are future phases, not faked. Hardened engineering is not a validated
theory.

### Branches
- **`paradigm/stages-2-9`** — active development line (current).
- **`master`** — stable line.

### Next
1. Freeze the primitive (boundaries + conflict + the theorem set in Lean).
2. Rival kernels (Rawls/Utilitarian/Constitutional/RLHF) on FreedomBench.
3. Port the frozen minimal kernel to Rust for parity with AuthGate's verified TCB.

## Contributing

Before opening a PR that touches `src/fdk_kernel/`, answer:

> *Can this feature exist entirely in `src/fdk_research/` instead?*

If yes, it does not belong in the kernel. The kernel must stay **deterministic,
fully testable, and non-semantic** — `tests/test_boundary.py` mechanically enforces
that the kernel imports nothing from research. Kernel changes require a spec entry
(`spec/`), tests that keep coverage at 100%, and `ruff` + `mypy --strict` clean. See
[`CONTRIBUTING.md`](CONTRIBUTING.md).

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
