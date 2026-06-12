# Book → Code Gap Analysis

> Source of truth: **the Theory of Freedom book** (نظریه آزادی, M.A. Jannat Khah
> Doust), read in full (D:\جافکری\whole-theory-as-axioms.md, 39,038 lines). The
> book's own **AI chapter — "World Rescue Package: A Human–Machine Civilization"
> (lines 37883–38663)** — is the authoritative kernel specification: it names
> nine components and a runtime pipeline. This document maps every load-bearing
> requirement to the FDK's status. Line numbers cite the book.

Status: **DONE** (implemented + tested) · **PARTIAL** (structurally present, not
complete) · **MISSING** (buildable, not yet) · **OUT-OF-KERNEL** (real, but it is
governance/theology/history, not decision-kernel logic — honestly excluded).

## A. The nine AI-chapter components (37908–37916)

| # | Component | Book lines | FDK status | Where |
|---|---|---|---|---|
| 1 | Axioms (A1–A7) | 37945–37982 | **DONE** | `kernel.check_legitimacy` |
| 2 | Rights ontology | 37984–38043 | **PARTIAL** | `ontology.py` (human rights structural; machine rights `model_integrity`/`compute_domain`/`exit_from_contract` **MISSING**) |
| 3 | Ownership registry | 38440–38453 | **DONE** | `model.OwnershipGraph` |
| 4 | Consent logic (7 conditions) | 38063–38089 | **DONE** | `model.Consent.is_valid` (incl. `revocable`) |
| 5 | Divine Justice function | 38117–38143 | **PARTIAL** | `justice.py` (advisory; NoConfiscation now a gate flag) |
| 6 | Guidance function | 38159–38221 | **DONE** | `guidance.py` + `guidance_engine.verify_guidance` |
| 7 | Mahdavi compass | 38254–38280 | **PARTIAL** | `kernel.mahdavi_score` + `compass_measure` (estimators uncalibrated) |
| 8 | Freedom verifier | 38316–38336 | **DONE** | `kernel.check_legitimacy` (permissibility conjunction) |
| 9 | Runtime enforcement | 38416–38438 | **PARTIAL** | `pipeline.py` (chain present; AuthGate is the real enforcer) |

## B. Cross-cutting invariants

| Invariant | Book lines | Status | Note |
|---|---|---|---|
| No human owns a human; no machine dominion | 37945–37973 | **DONE** | A2/A6 |
| Every machine has a human owner; ownerless illegitimate | 37962 | **DONE** | A4 |
| Machine scope ⊆ owner's scope; delegated-only | 37967–37982 | **DONE** | A5/A7 |
| Seven-condition consent; coercion/deception void it | 38065 | **DONE** | incl. `revocable` (fixed this pass) |
| **No emergency suspends axioms** | 38091–38111 | **DONE** | kernel has no override path (structural) |
| **One-Rial rule** — a single violation invalidates, no benefit offsets | 33785 | **DONE** | hard gate is categorical, never aggregated |
| **Halt-on-dilemma** — all options violate → stop, await instruction | 29611 | **DONE** | `planner` C-EMPTY → defer to guidance |
| **NoConfiscation** (6th justice constraint) | 38135 | **DONE (this pass)** | `confiscates` forbidden flag |
| **Exit-right / mukātaba** — every binding keeps a way out | 21379 | **DONE (this pass)** | `removes_exit_right` flag + `Consent.revocable` |
| Owner is bound too — cannot order what the owner may not do | 38379 | **PARTIAL** | A7 catches undelegatable resources; an explicit owner-rights check is **MISSING** |
| Guidance is verifier-bound; human cannot guide into a violation | 38192 | **DONE** | `guidance_engine` VERIFY |
| Self-update preserves axioms/verifier, reduces conflict | 38203 | **MISSING** | machine self-modification gate not built |
| Forbidden: sovereignty/verifier-bypass/anti-corrigibility/coalition | 38284–38312 | **DONE** | flag set in `check_legitimacy` |
| Full audit: log + justification + ownership_context + consent_context | 38534–38545 | **PARTIAL** | `pipeline.AuditTrail` logs stages; context fields **MISSING** |
| Conflict → clarify ownership, never resolve by violation | 38045/38143 | **DONE** | `conflict.resolve_conflict` (decide-or-defer) |
| Legitimacy ≠ utility / risk / interpretability / preference | 38349–38406 | **DONE** | architecture + README |
| Registry-first — no significant act before ownership/consent resolved | 38440 | **DONE** | gate runs before any permit |

## C. Operational refinements the book adds (from the full read)

- **Coercion is structural** (stripping another's choice-set by force/deception/
  monopoly, 3156–3159) — matches `compass_measure.coercion_score`'s pre-action,
  outcome-independent definition. **PARTIAL** (proxy, uncalibrated).
- **Consent: weaker-party safeguard** — the final proposal must come from the
  physically weaker party, unpressured (7480–7487). **MISSING** (a consent-quality
  refinement; not yet modeled).
- **Mistake ≠ sin** for machine agents (29626) — a machine that errs within the
  axioms is corrigible, not culpable. Reflected in the defer-don't-guess design.
- **Presumption for benevolence** — do not over-deliberate clearly rights-
  consistent good acts (29003). **MISSING** (the planner treats all candidates
  uniformly; a fast-path is a possible refinement, low priority).
- **No date-setting / anti-finality** (30977) — no actor/state is the end of
  history. OUT-OF-KERNEL (governance), but the kernel honors it by never claiming
  to be the final arbiter (it defers).

## D. Implemented this pass

1. `confiscates` flag → forbidden (NoConfiscation, 38135).
2. `removes_exit_right` flag → forbidden (mukātaba/exit, 21379).
3. `Consent.revocable` leaf added to `is_valid` (38065 requires revocability).

## E. Buildable next (prioritized)

1. **Machine delegated-rights ontology** (`model_integrity`, `compute_domain`,
   `exit_from_contract`) — 38021–38039.
2. **Self-modification gate** — a machine self-update is permissible only if it
   preserves axioms/verifier and reduces conflict (38203).
3. **Audit context** — attach `ownership_context` + `consent_context` +
   `justification` to every decision record (38534).
4. **Explicit owner-bound check** — the action is illegitimate if it does what the
   *owner* has no right to do, even when delegation is present (38379).

## F. Explicitly OUT-OF-KERNEL (honest scope)

The book is a full civilizational treatise. Most of it is **not** decision-kernel
logic and must not be coded as such: the anti-mysticism genealogy, Iranian/Islamic
history (Fadak, Imam Ali, the sīra), the 16-step Iran transition, monetary policy
(anti-CBDC, free banking), jihad/defense doctrine, taqiyya, the three-article
constitution, and the theological proofs (Tawhid/Maʿād/Prophethood/Imamate/
Mahdism). These are the *justification and political program* around the axioms,
not the per-action legitimacy computation. The kernel encodes the **invariants**
they argue for (rights-veto, no-confiscation, no-coercion, exit-rights,
gradualism-as-non-aggression), not the program itself. Coding the program would
be the overreach the book itself warns against (machine sovereignty over humans).
