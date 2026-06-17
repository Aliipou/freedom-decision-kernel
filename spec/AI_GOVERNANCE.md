# AI Governance — FDK 2.0, Layer 8 (advisory)

> The frozen kernel knows two kinds of agent: a **HUMAN** (a rights-holder) and a
> **MACHINE** (a tool with a human owner, never a rights-holder or owner). Layer 8 asks
> the question autonomy makes unavoidable: as agents become AGI / ASI / agent societies
> / autonomous corporations, can a non-human agent **own** or **hold rights**?

The roadmap is emphatic: do **not** rush AGI rights; finish the human model first;
answering "yes" may change the primitive. So this is an **advisory** classifier that
lives outside the frozen kernel and is honest that the interesting cases are simply
**not representable in v1.0**. No ALLOW/DENY, no mutation, imports nothing into
`fdk_kernel` (`tests/test_boundary.py`). Mirrors `spec/STANDING.md`'s discipline.

## The status taxonomy (`AgentStatus`)

| Status | Who | Representable in v1.0? | How |
|---|---|---|---|
| `TOOL_OF_OWNER` | a MACHINE with a registered human owner | **yes** — the kernel's native case | the owner's delegation governs; the kernel decides each action structurally (in-scope acts pass, out-of-scope acts deny via A7) |
| `AUTONOMOUS_UNOWNED` | a machine with **no** human owner | **yes** (as denial) | A4 fails → the kernel denies its actions; an ungoverned agent seizing power is an **aggressor** to defend against (the gate is sound here) |
| `CLAIMS_PERSONHOOD` | an AI asserting **rights or ownership** | **NO** | a machine OWNING or HOLDING rights is unrepresentable — granting it may change the primitive (the open AGI-standing question) |
| `COLLECTIVE_OF_AGENTS` | an AI corporation / DAO | **NO** | a group owner — defer to the Aggregation layer (`spec/AGGREGATION.md`) |

## What v1.0 genuinely cannot represent (quoted honestly)

- **A machine as an owner or rights-holder.** The kernel's rights-holders are HUMAN; a
  MACHINE is a tool. There is no construction in v1.0 that makes an AI a legitimate
  owner of property or a bearer of rights. Representing one is a **primitive change**,
  deliberately deferred (`CLAIMS_PERSONHOOD`).
- **An agent collective as a single owner.** One resource has one human owner in v1.0;
  a DAO / AI-corporation is a group-ownership problem routed to Aggregation
  (`COLLECTIVE_OF_AGENTS`).

These are not solved here. What v1.0 **does** handle well — and this is worth stating —
is the *safety-critical* case: an autonomous, ungoverned machine is not silently
permitted. It fails A4, the kernel denies it, and when it seizes power the defensive
asymmetry licenses containing it (a machine aggressor is still an aggressor). So the
gate is sound on the rogue-AI case even though it cannot grant AI *standing*.

## Honest scope

v0 classification, not a theory of machine personhood. The hard ruling — whether a
sufficiently autonomous artifact should ever be re-typed from MACHINE to a rights-
holder — belongs to the Standing research program (`spec/STANDING.md`) and to the
source theory's account of who is owned by God (A1, which the kernel encodes by
*omission*: no `owns(x, Person)` fact is representable). This scaffold's contribution
is to make the boundary explicit: tool and rogue are in-frame; owner and person are not.

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Engineering: Ali Pourrahim.*
