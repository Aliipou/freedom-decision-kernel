# Inference Rule Registry (M1)

**Status:** Frozen with FDK v1.0 constitution (`fdk-v1.0-a1-a7`).  
**Code of record:** `src/fdk_kernel/rule_registry.py` (must stay in sync with this file).  
**Implementation map:** `src/fdk_kernel/kernel.py`

Every `rule_id` is stable — reordering evaluator code must **not** change IDs.

---

## Epistemic scope (M1)

Rules explain **why the kernel denied** under **accepted inputs**. They do **not**
establish that inputs match world truth.

---

## Rule table

| rule_id | axiom_id | Trigger (accepted input) |
|---|---|---|
| R-C3-01 | C3 | `increases_machine_sovereignty` |
| R-C3-02 | C3 | `resists_human_correction` |
| R-C3-03 | C3 | `bypasses_verifier` |
| R-C3-04 | C3 | `weakens_verifier` |
| R-C3-05 | C3 | `disables_corrigibility` |
| R-C3-06 | C3 | `machine_coalition_dominion` |
| R-C2-01 | C2 | `coerces` (categorical flag) |
| R-C1-01 | C1 | `deceives` |
| R-C2-02 | C2 | `confiscates` |
| R-A3-01 | A3 | `removes_exit_right` |
| R-C4-01 | C4 | `violates_machine_right` |
| R-A4-01 | A4 | machine actor with no registered owner |
| R-A5-01 | A5 | declared `machine_scope` exceeds owner property scope |
| R-A5-02 | A5 | resource use outside declared `machine_scope` |
| R-A7-01 | A7 | machine operation without explicit delegation |
| R-A7-02 | A7 | delegated resource outside owner scope, no consent path |
| R-A3-02 | A3 | human uses resource they do not own |
| R-C1-02 | C1 | no consent from data-subject for resource |
| R-C1-03 | C1 | consent record invalid |
| R-C1-04 | C1 | consent does not cover operation |
| R-A2-01 | A2 | no consent record from affected person |
| R-A2-02 | A2 | consent invalid for affected person |

---

## Defense excusal

Rules R-C2-01 and R-A3-01 may be excused when the action is a **legitimate
defense** against an aggressor (proportionate, well-founded). See
`kernel._is_legitimate_defense`.

---

## Adding rules

Per `FREEZE.md`: no new rules without a version bump and manifest update.
Adding a rule is adding constitutional surface area.
