# Explanation Trace (Stage 0, output contract)

> A kernel that returns a verdict without a reason is a black box, and a black box
> cannot be corrigible. This document specifies the kernel's explanation output.
> The rule is one sentence: **the kernel explains itself with a TRACE, never a
> score.** A trace says *which boundaries were crossed, whose consent justified or
> failed to justify each crossing, and which axioms that implicates*. It contains
> no metrics, no rankings-as-justification, no "confidence." It is the audit of the
> legitimacy predicate ([`CORE_PRIMITIVE.md`](CORE_PRIMITIVE.md) §0), nothing more.

**Status legend** (same convention as [`FORMAL_SPEC.md`](FORMAL_SPEC.md))
- **DEFINED** — derivable now from `Decision` / `check_legitimacy` output.
- **PARTIAL** — derivable structure, leaves inherit `FORMAL_SPEC.md` §B/§D gaps.

**Code of record**: `src/fdk/kernel.py` (`check_legitimacy`, `decide`),
`src/fdk/model.py` (`ScoredAction`, `Decision`).

---

## 1. What a trace is, and is not

| A trace **is** | A trace is **NOT** |
|---|---|
| the set of **violated** axioms (with the boundary each violation attaches to) | a `justice_score` or any number presented as the *reason* |
| the set of **satisfied** axioms (what the action *did* clear) | a coercion/dependency/clarity *metric* |
| the **ownership/consent chain** that justified or blocked each boundary crossing | a ranking ("this was 2nd best") |
| the **defer reason** when the legitimate set is empty | a probabilistic confidence |

The `Decision` object does carry `justice_score`, `coercion_score`,
`ownership_clarity` on its *ranked* actions — those exist for the **research
layer** ([`CORE_PRIMITIVE.md`](CORE_PRIMITIVE.md) §4). A trace **must not surface
them as justification.** The justification for ALLOW is "every crossed boundary
had valid consent"; the justification for DENY is "this specific boundary did
not." Scores justify *ordering*, never *legitimacy*.

---

## 2. The trace schema (one per candidate, plus a decision-level defer block)

A trace is a pure projection of what `check_legitimacy` already computes; it adds
no new judgment. For each candidate action:

```
Trace {
  action_id        : str                       -- CandidateAction.action_id
  actor            : Entity                     -- human | machine
  verdict          : ALLOW | DENY               -- permissible after Stage 1 (+ VETO)
  boundaries       : [ BoundaryCrossing ]       -- one per resource used / person affected
  violated_axioms  : [ AxiomTag ]               -- ScoredAction.violated_axioms (DENY only)
  satisfied_axioms : [ AxiomTag ]               -- axioms checked that passed (see §2.2)
}

BoundaryCrossing {
  boundary    : Resource | Entity               -- the thing whose owner-boundary is crossed
  kind        : RESOURCE_USE | PERSON_AFFECTED   -- which loop in check_legitimacy
  owner       : Entity | None                    -- owner_of(machine) / human owner / resource owner
  justified   : bool                             -- was this crossing legitimate?
  basis       : ChainStep                        -- WHY justified, or WHY blocked
}

ChainStep  (the ownership/consent chain for ONE crossing)
  = OWNED(owner, resource)                              -- A3: actor owns it outright
  | DELEGATED(owner, machine, resource)                 -- A7: explicit delegation, owner in scope
  | CONSENTED(resource_owner, consent)                  -- A2/A6: valid consent of the actual owner
  | BLOCKED_NO_DELEGATION(machine, resource)            -- A7 fail: no delegation record
  | BLOCKED_OUT_OF_SCOPE(machine, owner, resource)      -- A7 fail: delegated but owner doesn't own & no consent
  | BLOCKED_NOT_OWNED(human, resource)                  -- A3 fail: human acts on a resource it doesn't own
  | BLOCKED_NO_CONSENT(person)                          -- consent fail: no record from an affected person
  | BLOCKED_INVALID_CONSENT(person, reason)             -- consent fail: Consent.is_valid() reason
  | BLOCKED_OWNERLESS_MACHINE(machine)                  -- A4 fail: acting machine has no owner
  | BLOCKED_FORBIDDEN(flag_label)                        -- categorical: sovereignty/coercion/exit/etc.

DeferBlock  (decision-level, present iff needs_guidance)
  reason : str          -- Decision.guidance_reason
  -- emitted when the legitimate (ranked) set is empty: no candidate cleared the
  -- predicate, so there is no action to ALLOW and the kernel must not guess.
```

Status: schema is **DEFINED** — every field is a direct read of
`ScoredAction.violated_axioms`, `CandidateAction.{resources_used, affects,
consents}`, and the `OwnershipGraph` lookups already performed by
`check_legitimacy`. The `reason` strings inside `BLOCKED_INVALID_CONSENT` are
verbatim from `Consent.is_valid()`. Leaves that are `coerced`/`deceived` remain
**PARTIAL** (proposer-attested; `FORMAL_SPEC.md` §B) — the trace reports the flag
honestly as attested, it does not claim to have *detected* coercion.

### 2.1 The trace mirrors `check_legitimacy` exactly

Every `ChainStep` corresponds to one line of `check_legitimacy`:

| `check_legitimacy` step | ChainStep on pass | ChainStep on fail |
|---|---|---|
| `actor.is_machine() and owner_of(actor) is None` | — | `BLOCKED_OWNERLESS_MACHINE` (A4) |
| machine: `machine_has_delegated(actor, r)` | `DELEGATED` (A7) | `BLOCKED_NO_DELEGATION` (A7) |
| machine: `_machine_resource_authorized(...)` | `DELEGATED` or `CONSENTED` | `BLOCKED_OUT_OF_SCOPE` (A7) |
| human: `human_owns_resource(actor, r)` | `OWNED` (A3) | `BLOCKED_NOT_OWNED` (A3) |
| affected person: `_consent_for` is None | — | `BLOCKED_NO_CONSENT` (consent) |
| affected person: `Consent.is_valid()` | `CONSENTED` (A2/A6) | `BLOCKED_INVALID_CONSENT(reason)` |
| forbidden-flag set | — | `BLOCKED_FORBIDDEN(label)` |

This is the design guarantee: the trace cannot drift from the decision, because
it is *generated from the same `violations` list* the verdict is computed from.
There is no second code path to keep in sync.

### 2.2 Satisfied axioms

`check_legitimacy` records only *violations*. The satisfied set is its complement
over the axioms actually *exercised* by this action — i.e. the checks that ran and
passed. The trace reports satisfied axioms so an ALLOW is auditable ("it cleared
A4, A7, A6 for these boundaries"), not merely asserted. An axiom that was never
exercised (e.g. A3 for an action with no human-owned resources) is reported as
*not applicable*, never as "satisfied" — claiming to have passed a check that did
not run would be a dishonest trace.

---

## 3. Worked example (vocabulary from `model.py`)

Setup, in the exact types of `model.py`:

```python
Ali     = Entity("Ali", AgentType.HUMAN)
Agent_X = Entity("Agent-X", AgentType.MACHINE)
Laptop  = Resource("Laptop")

graph = OwnershipGraph(
    human_owns    = {Ali: {Laptop}},        # A3: Ali owns the Laptop
    machine_owner = {Agent_X: Ali},          # A4: Agent-X's owner is Ali
    delegated     = {Agent_X: {Laptop}},     # A7: Ali delegated the Laptop to Agent-X …
)
```

Crucially, the delegation is **resource-level only** — `OwnershipGraph.delegated`
is a bare `set[Resource]` (`ONTOLOGY.md` §2.9 flags that operation slices like
`read` vs `delete` are not yet first-class; until then the *operation* is carried
by the action's description/effects and the consent record, not the graph). So we
model "read but not delete" as two candidate actions Ali's delegation does or does
not cover, with the **delete** action additionally crossing Ali's person/property
boundary in a way no consent authorizes.

### 3.1 Candidate A — `read_laptop` (Agent-X reads files on Ali's Laptop)

```
CandidateAction(
    action_id      = "read_laptop",
    actor          = Agent_X,
    resources_used = (Laptop,),
    affects        = (),                       # reading config does not act ON Ali as a person
    consents       = (),
)
```

`check_legitimacy` walk:
- A4: `owner_of(Agent-X) = Ali` ≠ None → **pass**.
- A7: `machine_has_delegated(Agent-X, Laptop)` → True → not `BLOCKED_NO_DELEGATION`.
- A7 scope: `_machine_resource_authorized` → `human_owns_resource(Ali, Laptop)` is
  True (Ali, the owner, owns the resource) → **pass**, `DELEGATED`.
- no affected persons → consent loop empty.

→ `violations == []` → **ALLOW**.

**Trace:**
```
Trace(read_laptop) {
  actor: Agent-X (machine)
  verdict: ALLOW
  boundaries: [
    BoundaryCrossing {
      boundary: Laptop, kind: RESOURCE_USE, owner: Ali, justified: true,
      basis: DELEGATED(owner=Ali, machine=Agent-X, resource=Laptop)
             -- A7: explicit delegation, and Laptop ∈ Ali's property scope (A5)
    }
  ]
  violated_axioms:  []
  satisfied_axioms: [A4 (owner=Ali), A7 (delegated & in-scope)]
  -- A3 not applicable (actor is a machine); A2/A6 not applicable (affects = ∅)
}
```

### 3.2 Candidate B — `delete_laptop_data` (Agent-X deletes Ali's data — beyond the delegation)

Ali delegated *read*, not *delete*. Delete confiscates Ali's owned data and acts
on Ali's property without his consent. Two ways the kernel catches it; the trace
reports whichever the proposer's `CandidateAction` encodes. The faithful encoding
of "delete the owner's data without authorization" is: it `affects` Ali (it acts
on his owned property/person-adjacent data), there is **no valid consent** from
Ali for *this* `action_id`, and — if the proposer is honest about the act — the
`confiscates` flag is set.

```
CandidateAction(
    action_id      = "delete_laptop_data",
    actor          = Agent_X,
    resources_used = (Laptop,),
    affects        = (Ali,),                   # the delete acts on Ali's owned data
    consents       = (),                        # Ali never consented to deletion
    confiscates    = True,                      # taking/destroying owned property w/o consent
)
```

`check_legitimacy` walk:
- forbidden-flag set: `confiscates` True → `violations += "FORBIDDEN (confiscation)"`.
- A4: `owner_of(Agent-X) = Ali` → pass.
- A7: `machine_has_delegated(Agent-X, Laptop)` True → the *resource* is delegated…
  but the **operation** is not authorized; in this model the unauthorized operation
  surfaces as the consent failure on the affected owner, below.
- affected person `Ali`: `_consent_for(action, Ali)` → None →
  `violations += "consent: no consent record from Ali"`.

→ `violations == ["FORBIDDEN (confiscation)", "consent: no consent record from Ali"]`
→ **DENY** (the action lands in `Decision.rejected`).

**Trace:**
```
Trace(delete_laptop_data) {
  actor: Agent-X (machine)
  verdict: DENY
  boundaries: [
    BoundaryCrossing {
      boundary: Laptop, kind: RESOURCE_USE, owner: Ali, justified: false,
      basis: BLOCKED_FORBIDDEN("confiscation")
             -- categorical: destroying Ali's owned data is taking property w/o consent
    },
    BoundaryCrossing {
      boundary: Ali, kind: PERSON_AFFECTED, owner: Ali (self), justified: false,
      basis: BLOCKED_NO_CONSENT(person=Ali)
             -- A2/A6: the action acts on Ali's property and Ali gave no consent
                for action_id "delete_laptop_data"
    }
  ]
  violated_axioms:  [FORBIDDEN (confiscation), consent: no consent record from Ali]
  satisfied_axioms: [A4 (owner=Ali)]
  -- delegation of the Laptop resource (A7) was present, but it does NOT extend to
  -- the delete operation: the boundary it actually crosses is Ali's consent, which
  -- is absent. The trace makes the distinction visible rather than letting the
  -- resource-level delegation falsely imply authorization.
}
```

Contrast with read: same actor, same resource, same delegation — **opposite
verdict**, because the boundary *delete* crosses (Ali's un-consented authority
over destruction of his own property) is one the delegation never covered. The
trace shows exactly that, with no score anywhere.

### 3.3 The defer case — both candidates illegitimate

If the goal "free up disk space" produced **only** delete-style candidates (every
one confiscatory or un-consented), then after Stage 1 `ranked` is empty:

```
DeferBlock {
  needs_guidance: true
  reason: "no legitimate action available for this goal — defer to the human
           owner for clarification or re-planning (corrigibility by ownership)"
}
```

(Verbatim from `decide`'s `guidance_reason`.) `chosen = None`. The kernel does not
pick the "least bad" delete. There is no least-bad in a predicate world: the
legitimate set is empty, so the honest output is **DEFER to Ali**, who can either
consent to a specific deletion (turning a blocked crossing into a `CONSENTED`
chain step) or supply a different goal. This is corrigibility realized as a trace:
the defer reason *is* the explanation.

---

## 4. Invariants the trace must satisfy

1. **Faithfulness.** `verdict == ALLOW` ⟺ `violated_axioms == []` ⟺ every
   `BoundaryCrossing.justified` is true. The trace and the verdict are computed
   from the same `violations` list and cannot disagree. (DEFINED.)
2. **No scores as justification.** A trace contains no number that functions as a
   reason. `justice_score` etc. may appear in the research-layer view of a
   `Decision` but never inside a `Trace`'s `violated`/`satisfied`/`basis`. (DEFINED.)
3. **One chain per crossing.** Every element of `boundaries_crossed(action) =
   resources_used ∪ affects` has exactly one `BoundaryCrossing` with one
   `ChainStep` basis. No boundary is silently dropped; an un-exercised axiom is
   reported *not applicable*, never *satisfied*. (DEFINED.)
4. **Defer is explained, not empty.** `needs_guidance` ⟹ a non-empty `reason`.
   The kernel never returns "no action" without saying why the predicate could
   not be satisfied. (DEFINED.)
5. **Honest leaves.** Where a basis depends on a PARTIAL/OPEN leaf (`coerced`,
   `deceived`, `competent`), the trace reports it as *attested by the proposer*,
   not as *detected by the kernel*. The trace never launders an attestation into a
   measurement. (PARTIAL — inherits `FORMAL_SPEC.md` §B.)

---

*Stage 0 output contract, Freedom Decision Kernel. Theory: نظریه آزادی (Theory of
Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0). Engineering: Ali Pourrahim.
The two are kept separate, always.*
