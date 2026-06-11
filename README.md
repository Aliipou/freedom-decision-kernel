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

## Relationship to the other repos

- **Theory** — نظریه آزادی (Theory of Freedom) by **Mohammad Ali Jannat Khah
  Doust** (CC BY 4.0). Axioms A1–A7, consent logic, Mahdavi compass. This kernel
  is a faithful engineering encoding of that theory's decision layer.
- **AuthGate** — the capability/enforcement kernel (Ali Pourrahim). The
  downstream authority check. Untouched by this project.

Engineering: **Ali Pourrahim**. Theory: **Jannat Khah Doust**. The two
attributions are kept separate.

## Status

Early MVP. Single-agent, synchronous, deterministic core with the worked revenue
example and a test suite. Not production-hardened; not externally reviewed.
