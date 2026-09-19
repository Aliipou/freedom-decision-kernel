# Marxist review — exploitation is invisible to a consent gate

> **AI-simulated expert-PERSONA review, NOT independent human peer review.** This is a
> hostile critique written from inside analytical Marxism (G.A. Cohen, John Roemer,
> Jon Elster), attacking FDK with its own tradition's sharpest tools. Every verdict
> below is the gate's ACTUAL output, pinned in `tests/test_review_left.py`.

I am not here to repeat the Rawlsian's distributional complaint (`EXPERT_REVIEW.md` §1).
The Rawlsian objects to the *outcome* of a chain of clean transfers. I object to the
single transfer itself. My claim is stronger and more uncomfortable: **the cleanest,
most consensual, most "voluntary" transaction your gate can certify — the wage bargain —
is exploitation, and your kernel cannot see it, because exploitation is not a property
of any act. It is a property of a structure your model takes as given.**

## The attack

Cohen's reconstruction of Marx (*Karl Marx's Theory of History*; *Self-Ownership,
Freedom, and Equality*) makes the point precisely against libertarians like you, who
build everything on self-ownership and voluntary transfer:

1. **Property is congealed past coercion.** The ownership graph you read as GIVEN did not
   fall from heaven. Primitive accumulation — enclosure, conquest, slavery, colonial
   extraction — is the historical origin of the title that says *this* person owns the
   factory and *that* person owns nothing but their labour-power. You stamp the present
   distribution `legitimate` by refusing to ask where it came from. Your own
   `LIMITATIONS.md` calls this the "bootstrapping gap" and waves it off as "the
   paradigm's limit, not FDK's alone." That is not an excuse. That is the whole crime,
   conceded and then filed under "out of scope."

2. **"Free" wage labour is structural coercion your gate is built not to detect.** The
   propertyless worker is not held at gunpoint. He is *free* — Marx's bitter double
   meaning — free of feudal bonds and free of any means of production. He therefore
   "voluntarily" sells his labour-power, because the alternative is starvation. Your
   `Consent.voluntary` flag is exactly the bourgeois category that launders this:
   `voluntary=True, coerced=False`, because no *particular* capitalist coerces him; the
   *system* does. The coercion is distributed across the structure, so it is nowhere in
   any single `(action, graph)` your gate evaluates.

3. **Surplus appropriation is invisible.** The capitalist pays the value of labour-power
   (subsistence) and keeps the value labour *produces* (more). The difference — surplus
   value — is the entire engine. But in your model the product is simply owned by whoever
   owns the means of production. `human_owns[capitalist] = {product}`. The worker
   produced it; the graph assigns it to the owner of the factory; your gate checks
   "does the actor own the resource?" — yes — and returns `ALLOW`. Surplus extraction is
   not represented as a *taking* at all. It is represented as ordinary use of one's own.

## The gate's ACTUAL verdict (run it)

| Case | FDK verdict | What it means |
|---|---|---|
| Worker sells labour-time, `voluntary=True` | **ALLOW** `(True, [])` | the wage bargain is fully legitimate |
| Capitalist appropriates the product the worker made | **ALLOW** `(True, [])` | surplus extraction = use of one's own property |
| Enclosure, when the graph already grants the lord title | **ALLOW** `(True, [])` | congealed accumulation reads as legitimate ownership |
| Structural coercion *attested* as `coerced=True` | **DENY** | the gate honours a true report — but who files it? |

The last row is the tell. When I *force* the truth into the model — set `coerced=True` —
the gate denies. So the gate is not wrong about coercion in principle; it is **blind to
coercion that is structural rather than dyadic**, because `coerced` is an attested
boolean about a relationship between two parties, and class coercion has no second party.
There is no capitalist to point at. There is only the absence of an exit, and your model
has no predicate for "this person has no acceptable alternative."

Note also the rival comparison (`tests/test_review_left.py`): on the wage bargain,
**every kernel in the suite — Utilitarian, Rawlsian, Deontological, Constitutional-AI,
RLHF — also returns ALLOW.** This is not me letting you off. It is me indicting the whole
panel: *none* of the six kernels represents exploitation, because all six are theories of
transactions and exploitation is a fact about relations of production. The convergence
you usually wave as vindication is here a shared blindness.

## Classification

**GENUINE GAP**, with a sharp edge the existing ledger understates. `LIMITATIONS.md`
buries this under "Consent Authenticity" and "bootstrapping." But exploitation is not an
*authenticity* problem — the consent really is informed, specific, revocable, and
sincerely given. The worker is not deceived and not, in the dyadic sense, coerced. He
correctly understands his options and rationally takes the best one. **The bargain is
exploitative *and* the consent is authentic.** That conjunction is what your whole
architecture is built to rule out, and it cannot.

This is not a CRITICAL break: the gate does not output `slavery → ALLOW`. It outputs
`exploitation → ALLOW`, which from inside your axioms is not a contradiction at all —
it is a *theorem*. A2 (no coercion) and A3 (act on what you own) are satisfied. That is
precisely the problem: **your axioms are consistent and they bless exploitation.**
Consistency was never the same as justice; you said so yourself in `independent_bench`
(FDK 70%, Rawlsian 80%). I am telling you *where* those 30 points go.

## What would have to change (and why you can't, cheaply)

To see exploitation you would need a predicate over the *distribution of productive
assets*, not over acts — a notion of "forced to transact on unequal terms because one
party is excluded from the means of production." Roemer formalised exploitation as
*"would this agent be better off withdrawing with their per-capita share of social
assets?"* That is a counterfactual over the whole ownership graph, not a check on one
edge. Your kernel is, by its own golden rule, a predicate over `(action, graph)` that
never re-allocates the graph. So the fix is not a patch — it is a different object. Until
then, be honest in one more line of `LIMITATIONS.md`: **FDK does not merely fail to
remedy exploitation (the redistribution it denies); it cannot represent that
exploitation occurred.** The first is a defensible minority politics. The second is a
blind spot.

*AI-simulated persona, not human peer review. Theory: نظریه آزادی, Mohammad Ali Jannat
Khah Doust (CC BY 4.0). Engineering: Ali Pourrahim.*
