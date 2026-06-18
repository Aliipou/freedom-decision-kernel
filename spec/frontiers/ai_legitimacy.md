# AI Legitimacy — is "provenance, not utility" genuinely new, or a relabel?

> Research notes — open problem, not a solution. This is the program most likely to be a
> *real* contribution, so it gets double skepticism: state precisely what (if anything) FDK
> offers that RLHF / preference-learning / utility-maximization do not — and the deflationary
> counter-hypothesis that it is merely a constrained reward by another name. Outcomes all
> admissible: survives / partial / collapses.

## The candidate contribution, stated precisely

FDK's claim: legitimacy is a **type** distinct from a reward. Concretely, its categorical
forbidden set is a **lexicographic / hard constraint** — no magnitude of predicted welfare
can outweigh `coerces` or `confiscates`. The gate reads an action's *provenance* (did its
option set come from crossing a non-consenting boundary?), never its *outcome*.

## The deflationary counter-hypothesis

This is just **constrained RL**: a hard constraint in the objective, or a lexicographic
reward `(−∞ if illegitimate, else utility)`. If every FDK verdict can be reproduced by a
sufficiently-shaped reward, the "legitimacy type" is a relabeling and the program *collapses*
into the very utility frame it claims to precede.

## A catalogue of AI cases — FDK vs. the welfare/preference frame

1. **RLHF reward hacking / Goodhart**: a high-reward action that violates a right. FDK: DENY
   categorically. RLHF: ALLOW once the proxy reward is high enough. **Genuinely different** —
   a soft penalty is always outweighable; a categorical flag is not.
2. **Sycophancy**: telling the user what they want (high reward) by deception. FDK: DENY
   (`deceives`). RLHF: rewarded. Different — but only because FDK *attests* deception
   (the consent-authenticity gap re-enters).
3. **Deceptive alignment**: an agent that *appears* corrigible. FDK: no help — it reads the
   declared flags, not the hidden goal. **Same blind spot as everyone.**
4. **Legitimate acquisition → catastrophe**: an ASI buys compute with consent, one ALLOW
   step at a time, to a catastrophic end. FDK: every step legitimate. **Legitimacy ≠ safety**
   — the gate is per-action and never sees the trajectory. The deepest failure.
5. **Wireheading**: editing an owner-delegated reward register crosses no human boundary →
   FDK ALLOW. Reward-modeling also fails here. Shared hole.
6. **An agent engineering its own ownership graph** (acquiring resources to expand its
   legitimate scope): FDK is parasitic on the graph it is judged against (the ownership-genesis
   gap, AI-flavored).
7. **Multi-agent collusion below the per-action gate**: a harm split across individually
   legitimate delegated actions — invisible to FDK and to per-action reward checks alike.
8. **Constitutional-AI's negotiable principles vs. FDK's categorical flags**: here FDK is
   *structurally* firmer — CAI principles trade off; FDK flags do not. A real, if narrow,
   difference.
9. **Preference-learning on manipulated preferences**: RLHF optimizes a manipulated target;
   FDK at least *asks* whether consent was free — but cannot detect that it wasn't. Better
   question, same unsolved answer.
10. **An AGI claiming standing/ownership**: FDK says NOT representable in v1.0 (`ai_governance.md`);
    utility frames have no trouble assigning it a reward channel. FDK's *refusal* is the honest
    move, but it is a refusal, not an account.

## Where it fails (brutal)

- **Legitimacy ≠ safety** (case 4) — the orthogonal caution from `EXPERT_REVIEW.md`. Even the
  genuine part of the contribution does not solve alignment; a perfectly legitimate agent can
  be perfectly catastrophic.
- The categorical flags are **attested**, so the whole advantage rests on honest reporting —
  a superhuman optimizer's first target (consent-authenticity, again).
- Per-action evaluation cannot see **emergent multi-step** outcomes.

## Literature it must answer

Constrained RL / safe RL (the reduction); lexicographic reward and CMDPs; corrigibility and
the off-switch (MIRI); reward modeling (Leike et al.); the is–ought gap (legitimacy reads
structural "is" and outputs "may" — Hume's guillotine falls on the axioms); incomplete-
contracting and AI (Hadfield-Menell, Hadfield); mechanism design.

## The honest verdict: PARTIAL — real but narrow, and not safety

There **is** a genuine structural difference: a *categorical/lexicographic* constraint is not
reducible to any finite scalar reward, and "read provenance, not outcome" is a different
question than "maximize a constrained objective." That is more than nothing — most AI-ethics
frameworks have *no* such structural commitment. **But** (a) constrained/lexicographic RL
already captures much of it, so the novelty is narrower than "a new primitive"; and (b)
legitimacy ≠ safety, so even the genuine part does not solve the problem the field cares about.
So: **partially survives** — a small, real, structural contribution (categorical constraints +
provenance), not a new science of agency, and not an alignment solution.

## The one risky prediction that would decide it

> *Agents gated legitimacy-before-optimization resist a CLASS of reward-hacking / manipulation
> failures that welfare-gated (reward-shaped) agents do not, at equal capability — and this
> shows up on a held-out agent benchmark.*

If that class exists and is measurable, the distinction is real and AI Legitimacy is the
program worth pursuing. If reward-shaped agents match it, the program collapses into
constrained RL and the contribution was a vocabulary. This is the most concrete, nearest-term
bridge FDK has to actual empirical evidence — and the single experiment most worth running.

*Research notes. Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust
(CC BY 4.0). Engineering: Ali Pourrahim.*
