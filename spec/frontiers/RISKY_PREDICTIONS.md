# Risky predictions — the bridge from framework to science

> A consistent, formally-checked, internally-elegant theory is still only a *philosophical-
> logical framework* until it sticks its neck out: *if FDK's account of legitimacy is right,
> we should observe Y (and NOT Z) in the world.* This is the single thing FDK most lacks —
> more than Lean, Rust, or another test. Stated below, per program, as falsifiable claims
> with what would confirm and what would refute them. **None has been tested.** They are
> commitments, not results — and each is stated so that *FDK losing* is a possible, publish-
> able outcome.

A prediction earns its place only if it could come out against FDK. Each is paired with the
data domain that could decide it and the observation that would falsify it.

## P1 — Authentic Consent
**Claim.** Regimes whose consent is *engineered* (company towns, platform lock-in, dopamine
loops, debt traps) produce measurably **lower exit and mobility** than regimes of authentic
consent — *even where stated satisfaction is equal or higher.*
**Test domain.** Labor mobility / churn / switching data across high- vs. low-lock-in
markets; migration out of company towns vs. comparable free-labor towns; app-uninstall and
account-deletion rates under dark-pattern vs. clean designs.
**Refuted if.** Engineered-consent regimes show exit/mobility indistinguishable from
authentic ones at equal satisfaction — i.e. the "manufactured vs. free" distinction has no
behavioral signature, and FDK is chasing a difference that does not exist.

## P2 — Ownership Genesis
**Claim.** Property regimes with **contested origins and no rectification mechanism** are
more long-run unstable (more expropriation, revolution, title litigation) than either
clean-origin regimes *or* those with an active rectification process.
**Test domain.** Cross-national: post-colonial land disputes, post-communist restitution
outcomes, indigenous title litigation rates, expropriation events vs. origin-contestedness.
**Refuted if.** Origin-contestedness does not predict instability once wealth and institutions
are controlled — i.e. forgetting the origin is *stable*, and FDK's worry about genesis is
moot in practice.

## P3 — Commons / Aggregation
**Claim (the one FDK is most likely to LOSE).** Commons that satisfy Ostrom's design
principles are both more **durable** AND more **consent-like** (lower coerced participation)
than open-access *and* state-confiscated regimes.
**Test domain.** Ostrom's own dataset + successors: irrigation, fisheries, forests, data
cooperatives — durability vs. governance type, with a coercion/exit measure.
**Refuted if.** Durable Ostromian commons are *not* more consent-like — i.e. their success
runs precisely on the non-consensual, minority-binding mechanisms FDK denies. This would
confirm the `aggregation.md` finding that FDK is the wrong lens for the commons.

## P4 — AI Legitimacy (the nearest-term, most decisive)
**Claim.** Agents gated **legitimacy-before-optimization** resist a *class* of
reward-hacking / manipulation failures that welfare-gated (reward-shaped) agents do not, **at
equal capability**, and this shows up on a held-out agent benchmark.
**Test domain.** A controlled agent eval: same base model, one variant with a categorical
legitimacy gate, one with a soft-penalty reward, on tasks seeded with reward-hack
temptations and manufactured-consent bait.
**Refuted if.** The reward-shaped agent matches the legitimacy-gated one — i.e. the
distinction is constrained-RL by another name (the `ai_legitimacy.md` collapse outcome).
*This is the single experiment most worth running: it is concrete, near-term, and decisive.*

## P5 — The core thesis (Standing-bounded)
**Claim.** Across a corpus of contested cases, FDK's *provenance* reading predicts the
majority human "legitimate/illegitimate" intuition on **boundary-crossing-without-consent**
cases better than a *welfare* reading — **but only within its frame** (competent adult
persons), and it predicts *worse* outside it (children, future generations, commons).
**Test domain.** A blind, multi-tradition annotated benchmark (`external_bench.py` is the
apparatus); FDK vs. welfarist baselines on agreement-with-consensus, split by in-frame vs.
out-of-frame.
**Refuted if.** FDK does no better than welfare *even in-frame* — then the provenance reading
buys nothing. (Note: the persona simulation already warns κ is low on contested cases, so the
test must be designed around disagreement, not a single key — see `layer11_persona_panel.py`.)

---

## The discipline this encodes

Two of these (P3, P4) are *designed* so FDK can lose, and one (P3) the current theory looks
likely to lose. That is the point. A program that only makes predictions it is sure to win is
doing apologetics, not science. The next decade's most valuable single act is not another
module — it is **running P4** (a real agent eval) and **engaging P3's data** (Ostrom's
corpus), and reporting the result whichever way it falls.

*Research notes. Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust
(CC BY 4.0). Engineering: Ali Pourrahim.*
