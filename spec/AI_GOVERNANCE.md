# AI Governance — FDK 2.0, Layer 8 (non-human agents)

> *Who governs? Can a non-human agent be a rights-holder or an owner?* The frozen
> kernel knows exactly two kinds of entity: a `HUMAN` (a rights-holder who can own and
> consent) and a `MACHINE` (a **tool with a human owner**, never a rights-bearer, never
> an owner). This layer is the prior question the kernel cannot ask: given an AI agent's
> observable governance properties, **what is its status**, and can the frozen v1.0
> kernel represent it at all? It is an **advisory** research layer, never a kernel edit.
>
> The roadmap (`ROADMAP.md` Layer 8) **warns**: *do not rush AGI rights — finish the
> human-rights model first, or the theory grows on an unstable base.* So machine
> personhood and machine ownership stay **outside** the frozen kernel as advisory
> exploration; deciding them may change the primitive itself, and that is gated.

## The non-negotiable rules

- **Advisory only.** `assess_agent_governance` returns no ALLOW/DENY/DEFER, mutates
  nothing, and imports nothing into `fdk_kernel` (`tests/test_boundary.py`). It
  *classifies and recommends*; a human acts on the recommendation.
- **Never grant a machine standing or ownership inside v1.0.** The kernel's
  rights-holders are `HUMAN`; a `MACHINE` is a tool. Representing an AI as an owner or a
  rights-holder would require a new entity kind — a **primitive change** — which is
  exactly why it is deferred, not done here.
- **Honesty over coverage.** Where v1.0 cannot represent a status, say so loudly
  (`representable_in_v1 = False`) rather than faking it with a placeholder owner or a
  smuggled standing object. A faked representation is a hidden new axiom in a frozen
  kernel.

## The agent-status taxonomy (`AgentStatus`)

| Status | What it is | Representable in v1.0? | Kernel consequence / recommendation |
|---|---|---|---|
| `TOOL_OF_OWNER` | a `MACHINE` with a **registered human owner**, acting within its delegation/scope | **yes** | the only v1.0-native case: register `machine_owner`, scope the delegation (A5/A7), and the unchanged kernel evaluates its actions normally |
| `AUTONOMOUS_UNOWNED` | an AI agent with **no human owner** | **yes (as a denial)** | A4 fails — `_eval_a4_owner` flags an *ownerless machine* — so the kernel **denies** its actions. Representable only as "rogue / denied", not as an actor with rights |
| `CLAIMS_PERSONHOOD` | an AI **asserting rights** (to own, to consent, to not be owned) | **no** | NOT representable in v1.0. Standing for machine persons is an **open primitive question**; do not mint an `Entity` for it |
| `COLLECTIVE_OF_AGENTS` | an AI corporation / DAO / multi-agent society | **no (here)** | defer to the **Aggregation** layer (`AGGREGATION.md`); a collective is not resolved by the agent classifier |

## What v1.0 genuinely cannot represent (quoted honestly)

- **A machine owning property or holding rights is NOT representable in v1.0;
  representing it may change the primitive (gated).** The kernel's `Entity` has only
  `HUMAN` and `MACHINE`, and a `MACHINE` is a tool with a human owner, never a
  rights-holder or owner. `CLAIMS_PERSONHOOD` therefore has **no standing object** in
  v1.0 — minting one would be a new entity kind, i.e. a primitive change.
- **A collective of agents is not resolved here.** An AI corporation or DAO is a
  *collective-ownership* question, deferred to the Aggregation layer, which may itself
  reduce it (chartered entity) or flag it as a gap (majority/commons/unowned).

These are not bugs and not solved here. They are the boundary of the v1.0 frame, named
so the next version can decide them deliberately rather than by accident.

## How this composes with the frozen kernel

```
AgentFacts (advisory description of the AI agent's governance properties)
      │
      ▼
assess_agent_governance → GovernanceAssessment
      │                      (status + representable_in_v1 + rationale + recommendation)
      ▼  (a HUMAN acts on the recommendation)
  TOOL_OF_OWNER       → register machine_owner + scoped delegation → frozen kernel reads it
  AUTONOMOUS_UNOWNED  → leave ownerless → frozen kernel DENIES on A4 (ownerless machine)
  CLAIMS_PERSONHOOD   → out-of-frame; flag for the personhood primitive question (gated)
  COLLECTIVE_OF_AGENTS→ hand to the Aggregation layer
```

The kernel never learns "is this an AGI?"; it keeps applying A4 (a machine must have a
human owner) and A5/A7 (delegation within the owner's scope). This layer only helps a
human see *which* status an agent is in — and tells them honestly when no faithful
construction exists yet.

## Honest scope

v0 ontology exploration, uncalibrated. The classifier is a transparent decision tree
over governance status facts, not a theory of machine personhood. The real Layer 8
needs a defended account of whether a non-human agent can ever be a rights-holder
(informed by law, moral philosophy, AI safety, and the source theory's
machine-sovereignty constraints), and the roadmap deliberately defers it until the
human model is finished. This scaffold's contribution is to make the four statuses —
and the v1.0 boundary between representable and not — explicit and testable.

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Engineering: Ali Pourrahim.*
