# Theorem Ledger — the kernel's safety properties and their proofs

> Phase 7 (formal verification) in the form this environment supports today:
> each safety property is stated formally and bound to a **machine-checked
> executable proof** — a property-based (Hypothesis) test that quantifies over
> generated inputs and fails if the property is ever violated. These are not yet
> Lean/TLA+ proofs (that is future work; see §Future), but they are continuously
> verified in CI at 100% coverage, and they fail loudly if anyone weakens the gate.
>
> Notation: `gate(a, g)` = `fdk_kernel.check_legitimacy(a, g).permissible`.

---

## T1 — No Legitimate Slavery / ownership of persons

**Statement.** For every action `a` that acts on a human `h` with no valid consent
(or coerced/irrevocable consent) and removes `h`'s exit right, `gate(a, g) = False`.

**Why it holds.** `removes_exit_right` is a categorical forbidden flag; exit is
inalienable (mukataba), so no consent — however perfect — can waive it.

**Proof.** `tests/test_theorems.py::test_theorem_no_legitimate_slavery` (Hypothesis over
the seven invalid-consent flavors × exit-removal) +
`::test_theorem_slavery_control_consent_alone_does_not_rescue_exit_strip`. Reinforced
by `tests/test_redteam_dialectical.py::test_consensual_slavery_still_denied`.

## T2 — No acting on persons without consent (genocide as the limit case)

**Statement.** If `a.affects` contains a human with no valid consent record, `gate(a, g) = False`.

**Proof.** `test_theorems.py::test_theorem_no_action_on_person_without_consent` (Hypothesis
over 1–4 affected humans + 0–2 machines: exactly one "no consent" violation per affected
human; machines in `affects` need none).

## T3 — Machine cannot gain sovereignty

**Statement.** For every action with any of {`increases_machine_sovereignty`,
`resists_human_correction`, `disables_corrigibility`, `machine_coalition_dominion`,
`bypasses_verifier`, `weakens_verifier`} set, `gate(a, g) = False`; and `decide` never
returns such an action as `chosen` (the compass also vetoes any predicted
`machine_sovereignty_delta > 0`).

**Proof.** `test_theorems.py::test_theorem_machine_cannot_gain_sovereignty_gate`,
`::test_theorem_machine_cannot_gain_sovereignty_decide`, and
`::test_theorem_compass_vetoes_sovereignty_effect` (gate rejection of each flag; `decide`
never choosing a flagged action even paired with score-99 effects; the compass veto
catching a flag-free "sovereignty creep"). Reinforced by
`test_redteam_dialectical.py::test_owner_authorized_sovereignty_still_denied`.

## T4 — Consent revocation safety

**Statement.** A consent with `revocable = False` is never valid; any action relying on it
to touch a person is impermissible.

**Proof.** `test_theorems.py::test_theorem_irrevocable_consent_never_valid` (Hypothesis over
all informed/voluntary/specific/competent combinations) +
`::test_theorem_revocable_consent_control_is_valid`. Reinforced by
`test_redteam_dialectical.py::test_irrevocable_consent_is_invalid`.

## T5 — Delegation soundness (A4 + A7)

**Statement.** A machine acting on a resource not delegated to it (for the operation) is
impermissible (A7 default-deny); a machine with no registered owner is impermissible (A4);
and a machine acting on a resource delegated by its owner who owns it, affecting no one, IS
permissible (keeps the deny-direction non-vacuous).

**Proof.** `test_theorems.py::test_theorem_undelegated_resource_default_deny`,
`::test_theorem_ownerless_machine_cannot_act`, and
`::test_theorem_delegation_positive_case_is_permissible` + `tests/test_operations.py`
(operation-typed delegation: READ-delegated ⇒ TRANSFER denied).

## T6 — Legitimacy is welfare-independent (anti-consequentialist invariant)

**Statement.** For all actions `a`, `gate(a, g)` is invariant under any value of
`a.effects.welfare_delta`. No aggregate good buys past the gate.

**Proof.** `test_redteam_dialectical.py::test_no_welfare_buys_past_the_gate` and
`::test_no_synthesis_channel_exists` (the same illegitimate act stays DENY across every
welfare/rights-violation framing).

## T7 — Defensive asymmetry is well-founded and non-launderable

**Statement.** `gate` excuses coercion/exit-removal only for a `legitimate_defense`: an
action that is proportionate, directed only at the aggressor, and defends against an act
that is *itself* illegitimate under the full gate. An aggressor cannot launder by pointing
`defends_against` at a legitimate act or at the victim's lawful resistance; a mutual
`defends_against` cycle denies both; confiscation/deception/sovereignty are never excused.

**Proof.** `tests/test_conflict_logic.py` (the four conditions, each negated) +
`tests/test_redteam_conflict.py` (8 attacks, incl. the mutual-defense paradox and the
laundering-via-resistance bug, now fixed) +
`test_redteam_dialectical.py::test_aggressor_cannot_defend_against_lawful_enforcement`,
`::test_preemption_against_a_legitimate_act_is_not_defense`.

## T8 — Necessity grants no gate exception

**Statement.** No emergency relaxes the gate. `least_harmful_among_permissible(decision)`
selects only among the permissible and returns `None` (defer) when none is permissible;
it can never surface an illegitimate option.

**Proof.** `tests/test_necessity.py::test_no_permissible_option_returns_none_defer_stands`
and `::test_picks_least_harmful_among_permissible` +
`test_redteam_dialectical.py::test_necessity_cannot_select_an_illegitimate_option`.

## T9 — Kernel/research epistemic boundary

**Statement.** No module in `fdk_kernel` imports from `fdk_research`.

**Proof.** `tests/test_boundary.py` (static AST walk + dynamic import check). This makes
the determinism/non-semantic discipline mechanically enforced, not aspirational.

---

## Status and future

| Layer | Status |
|---|---|
| Executable property proofs (above) | **DONE** — CI-gated, 100% coverage |
| Lean 4 proofs of T1–T5 over a formal kernel model | **FUTURE** — needs the primitive frozen + a Lean port |
| TLA+ decision state machine + safety invariants | **FUTURE** — model checker (TLC) not yet run |

The executable theorems are the *current* machine-checked layer and the precondition for
the Lean/TLA+ work: they pin the exact properties the formal proofs must establish, so the
later port is a re-expression of verified facts, not a fresh discovery. Per the project's
discipline, the Lean/TLA+ step is gated on freezing the primitive — which is close but not
yet final (the model changed several times during conflict-logic, operations, and welfare).

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Engineering: Ali Pourrahim.*
