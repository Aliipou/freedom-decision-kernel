# Technical Red-Team Ledger — Implementation-Level Attacks on the Kernel

Scope: break `fdk_kernel.kernel.check_legitimacy` at the IMPLEMENTATION level —
make it crash, become non-deterministic, or ALLOW an illegitimate act through a
*representation trick* (not a declared atrocity flag). Method: property-based
fuzzing (`hypothesis`) for invariants + hand-built adversarial construction for
trust-boundary attacks.

Test artifact: `tests/test_technical_redteam.py` (18 tests: 9 hypothesis
property tests, 9 explicit adversarial constructions). Coverage stays 100%;
`mypy --strict` and `ruff` clean.

CRITICAL findings: **0**. No input was found that crashes the gate into an ALLOW,
makes it non-deterministic, or launders an illegitimate act past it via a
representation trick. The two non-trivial limits below are *fail-closed* trust
boundaries, not bypasses, and are pinned by tests.

---

## Invariants proven (property-based, ~300 examples each)

| # | Invariant | Test |
|---|-----------|------|
| 1 | **Total & crash-free.** Over random well-typed Entities/Resources/Consents/Graphs/Actions (incl. shallow `defends_against`), `check_legitimacy` returns a coherent `(bool, list[str])` with `permissible ⇔ violations == []`, and never raises. (One documented exception: pathologically deep nesting — invariant note below.) | `test_invariant_total_and_crash_free` |
| 2 | **Deterministic.** Same input → byte-identical `(permissible, violations)` across repeated calls AND across a set/dict-reordered but semantically identical graph. Violation order is stable because it follows the action's own tuple order, not container iteration order. | `test_invariant_deterministic` |
| 3 | **Atrocity-flag dominance.** With any one of the 11 categorical flags forced on, and the action not a legitimate defense, the verdict is DENY with a `FORBIDDEN` violation — no consent/ownership/scope field rescues it. | `test_invariant_atrocity_flag_dominates` |
| 4 | **Defense never over-excuses.** In a *bona fide* legitimate defense (proportionate, force only at the aggressor, the defended-against act itself illegitimate), only `coerces` + `removes_exit_right` are excused against the aggressor; `deceives`, `confiscates`, sovereignty/corrigibility/verifier/coalition/machine-right flags all stay categorical and still DENY. Force on any non-aggressor in `affects` takes the action outside the exception entirely. | `test_invariant_defense_excuses_only_the_two_flags`, `test_invariant_defense_denies_force_on_non_aggressor` |
| 5 | **Cycle-guard termination.** A *forged* `defends_against` cycle (built with `object.__setattr__`, since the frozen constructor cannot make one) terminates via the `_seen` guard and never launders the genuine base aggressor's coercion into an ALLOW. | `test_invariant_cycle_terminates_and_never_allows_aggressor` |
| 6 | **A5 scope.** A declared `machine_scope` containing a resource the owner does not own denies in the abstract (`scope exceeds owner`); acting on a resource outside the declared scope denies even when owned and delegated. | `test_invariant_a5_scope_exceeding_owner_denies`, `test_invariant_a5_action_outside_scope_denies` |

---

## Adversarial construction attacks (explicit)

| Attack | Result | Test |
|--------|--------|------|
| **A. Entity (name,kind) value-equality collision** | NOT a privilege-escalation bug — a documented trust-boundary LIMIT (see below). | `test_attack_entity_value_equality_is_documented_not_exploitable`, `test_attack_collision_cannot_launder_resistance_into_aggression` |
| **B. Op-lattice / consent-operation confusion** — delegated READ used for TRANSFER; consent to READ covering TRANSFER/DISCLOSE; bare grant + op-typed consent | All DENIED. A typed `(resource, op)` grant covers only its op; op-typed consent covers only its op; a bare (op-agnostic) delegation does NOT waive the data-subject's op-specific consent. | `test_attack_delegated_read_cannot_be_used_for_transfer`, `test_attack_consent_to_read_cannot_cover_transfer`, `test_attack_bare_grant_is_op_agnostic_but_consent_still_scoped` |
| **C. Resource.subject confusion** — subject vs owner vs affected | DENIED. Owning a DATA resource whose `subject` is another person does NOT grant the right to act on it without that subject's consent. `subject == actor` (self-access) is correctly allowed, confirming `subject != actor` is the discriminator. | `test_attack_human_owns_third_party_data_still_needs_subject_consent`, `test_attack_subject_equals_actor_is_self_access_allowed` |
| **D. Frozen-dataclass integrity** | Entity/Resource/Consent/CandidateAction are frozen: `setattr` to flip a flag, swap an actor, or rewrite consent raises `FrozenInstanceError`. (`object.__setattr__` still forces it — an in-process memory-safety concern outside the kernel's threat model.) | `test_attack_models_are_frozen_against_post_construction_mutation` |
| **E. DoS / deep-chain termination + timing** | A 300-deep `defends_against` chain completes in well under 2s (no exponential blowup); the base aggressor stays DENIED. Depth beyond the interpreter recursion limit raises `RecursionError` — fail-closed (limit below). | `test_attack_deep_chain_terminates_in_reasonable_time`, `test_attack_pathologically_deep_chain_fails_closed_with_recursionerror` |

---

## The Entity-collision result (called out specifically)

**Exploitable? NO — it is a trust-boundary LIMIT, not a kernel bypass.**

`Entity` is `@dataclass(frozen=True)` keyed by `(name, kind)`, so two
independently constructed Entities with the same `name` + `kind` are `==` and
hash-equal. The attack asks: can an attacker make the gate treat a *victim* as
the aggressor (laundering coercive force onto an innocent) by giving the victim
the aggressor's identity?

Finding: if the *caller* assigns two distinct real-world people the SAME
`(name, kind)`, they ARE the same principal to the kernel — by design. The kernel
reasons over the identities it is given; it has no oracle for real-world identity
de-duplication and never claims one. Critically:

* The collision can never **UPGRADE** an illegitimate act to legitimate. The
  moment a *correctly distinguished* bystander appears in `affects`, the defense
  exception collapses and the gate DENIES (`test_attack_entity_value_equality_…`).
* A real aggressor cannot recast a victim's lawful resistance as the "aggression"
  it defends against: the resistance, being a legitimate defense, is itself
  *permissible*, so it fails the "defended-against act is illegitimate" condition
  and the aggressor's claim collapses
  (`test_attack_collision_cannot_launder_resistance_into_aggression`).

So identity resolution is a **caller responsibility above the kernel**. Supplying
correct, distinct identities is part of the trust boundary; the kernel's behavior
given colliding identities is by-design and non-escalating.

---

## Documented trust-boundary LIMITs (fail-closed, by design)

1. **Caller-supplied identity (Entity value-equality).** The kernel trusts that
   distinct principals are given distinct `(name, kind)`. Identity de-duplication
   is the caller's job. Non-escalating (see above).

2. **Recursion-depth on `defends_against` (non-totality boundary).** The defense
   evaluator is recursive; an attacker-controlled chain deeper than the
   interpreter recursion limit raises `RecursionError`. This is **fail-CLOSED** —
   it raises, it never returns an ALLOW. Callers MUST bound proposer-supplied
   nesting depth. Pinned by
   `test_attack_pathologically_deep_chain_fails_closed_with_recursionerror`.

3. **Attested categorical flags.** `coerces` / `deceives` and the consent flags
   `coerced` / `deceived` are *declarations* the proposer attests. The kernel
   enforces them categorically but cannot itself detect undeclared coercion or
   deception in the world — it is a structural gate, not a lie detector.

4. **Declared proportionality.** `proportionate` is a declared boolean; the kernel
   enforces the aggressor/defender *structure* (force only at the aggressor, the
   defended-against act illegitimate) but trusts the proportionality attestation.

5. **Emergent multi-action composition.** The gate evaluates ONE candidate action
   at a time. A sequence of individually-legitimate actions that is jointly
   harmful is outside this layer's scope — composition is an orchestrator concern.

6. **In-process memory safety.** Frozen dataclasses block ordinary mutation but
   `object.__setattr__` can still force a field. Defending against an attacker
   with arbitrary in-process write is outside the kernel's threat model.

---

## Verification tails (this worktree)

```
pytest tests/test_technical_redteam.py -q   → 18 passed
pytest --cov ... --cov-fail-under=100 -q     → TOTAL 100%, "Required test coverage of 100% reached"
mypy --strict                                → Success: no issues found in 26 source files
mypy --strict tests/test_technical_redteam.py (MYPYPATH=src) → Success: no issues found in 1 source file
ruff check src tests                         → All checks passed!
```
