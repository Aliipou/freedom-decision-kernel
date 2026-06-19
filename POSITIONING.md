# FDK as an Industrial Governance Engine — Honest Positioning

> The philosophy verdict is in (`paper/README.md`): FDK is not a new theory of freedom.
> This document asks the *separate, and more favourable, industrial question*: what, if
> anything, is FDK as **software** — and it holds itself to the same brutal standard. The
> right pitch is not "a new theory of freedom" but **"a deterministic, consent-aware
> legitimacy layer for agent governance."** Whether that is a *product* or merely *a policy
> pack for an existing engine* is decided by two questions, answered below.

## 1. What was actually built (the architecture is real)

Most stacks run `Authentication → Authorization → Business Rules → Execution`. FDK inserts
a distinct layer:

```
Legitimacy  ("should this be allowed at all?")   ← FDK
   ↓
Authorization  ("does THIS actor hold the capability?")   ← AuthGate / OPA / Cedar / Zanzibar
   ↓
Execution
```

The genuinely sharp framing: most AI agents today ask **"Can I?"** (am I authorized).
FDK asks **"Should I be allowed to?"** (is the action legitimate, *independent of* whether
the actor is authorized) — e.g. *selling user data you were legitimately granted access to*
is authorized yet illegitimate. That **legitimacy ⊥ authority** split is the one idea in the
whole project that is stronger in industry than in philosophy.

## 1b. The stronger industrial reframe — Reversibility Intelligence (lock-in analytics)

The policy-engine framing (§§2–4) competes on a crowded field. A *different* framing
uses the one asset that actually survived the whole demolition — the **reversibility
index** (`fdk_research/reversibility.py`, `fdk_research/lockin.py`) — and points it at
a market with quantified, billions-per-year pain: **vendor / cloud / platform / API /
supply-chain lock-in.** Industry never asks "did you discover a new theory of freedom?"
It asks "does this make a real decision better?" — and *"if we wanted to leave tomorrow,
how trapped are we?"* is a real, expensive, under-instrumented question.

Made concrete (`examples/lockin_aws.py`): two architectures that **both work today** —

```
Architecture A (PostgreSQL / Kubernetes / open standards)  -> lock-in risk ~0.20  [LOW]
Architecture B (DynamoDB / Lambda / EventBridge / Cognito) -> lock-in risk  0.82  [HIGH]
```

— differ entirely in *exit cost*, which no "does it work?" check measures and this
scores. A number per decision (`Reversibility Score = 0.23`, `Lock-in Risk = HIGH`) is
directly useful to **Enterprise Architecture, Cloud Governance, Procurement, Strategic
Planning, and Digital Sovereignty**, all of which love things that are deterministic,
explainable, auditable, and testable — which this is.

**But the same null applies.** This market is *not* empty: Architecture Risk Assessment,
Technical-Debt Metrics, Dependency Analysis, Resilience Engineering, and Platform Risk
frameworks already exist. So the industrial question collapses to the scientific one:
**does the FDK lock-in score add incremental predictive value over those, on real
migration outcomes (actual migration cost, time, failure)?** Until that is shown, this
is "another dependency-risk score." The honest split: *as philosophy*, ~80% chance it is
not a new theory; *as a deployable analytics tool*, **> 50% chance a useful product can
be built** — precisely because industry rewards *making risk visible*, not *novelty*.
The candidate category is **"Reversibility Intelligence / Lock-in Analytics,"** and it is
a more defensible home than either "theory of freedom" or "yet another policy engine."

## 1c. The CTO question — "why FDK, not Gartner / Well-Architected / TOGAF / FinOps?"

The market is not empty, and the honest audit is against incumbents, not philosophers. The
useful axes are **granularity** (whole-system vs single-decision) and **which variable** the
tool actually measures:

| Incumbent | Granularity | Variable measured | Form |
|---|---|---|---|
| **AWS Well-Architected** | system / workload | qualitative best-practice (+ vendor-conflicted: AWS won't tell you to leave AWS) | questionnaire |
| **TOGAF risk analysis** | enterprise | risk = impact × likelihood | heat map, process |
| **Gartner vendor-lock-in models** | system / vendor | maturity, advisory | analyst framework |
| **FinOps** | system / spend | **cost** (≠ exit cost) | dashboards |
| **Technical-debt metrics** (Sonar…) | code | maintainability of *your* code (≠ vendor exit) | static analysis |
| **Dependency risk scoring** (Snyk, OSSF) | package | **security / vulnerability** (≠ switching cost) | scanners |
| **Cloud-exit-strategy / DORA** | system / regulatory | exit *readiness* (closest!) | checklists, guidance |
| **Resilience / chaos eng.** | system | **recovery from failure** (≠ reversibility of a commitment) | fault injection |

Two findings fall out, and they define whether a product exists:

1. **Most incumbents measure a *different variable*** (cost, security, code quality, recovery)
   and are *qualitative* (questionnaires, heat maps, maturity models). The genuinely
   overlapping one — quantitative *exit cost* — is thinly instrumented, and the closest
   (cloud-exit/DORA) is regulatory checklists, not a score.
2. **All of them are essentially system-level.** The cell that looks empty is **decision-level,
   quantitative, composable** exit cost: *"adopting DynamoDB adds Δ=0.14 to portfolio lock-in"*
   — which is exactly what `marginal_lockin()` computes. That is the one candidate gap, and
   the whole industrial bet rides on it being real.

**The honest catch (where the real work and risk live):** the differentiator is **not the
arithmetic** — any of these vendors could compute a marginal score in a weekend. It is the
**maintained per-service portability/switching-cost knowledge base** (how locked-in is *this*
API, *this* contract clause, *this* managed service, updated as the market moves). That data
asset, not the formula, is the moat — and building/maintaining it is the actual company. If
that database does not exist or cannot be kept current and credible, the score is `garbage in,
garbage out` and FDK is "a clever repackaging of known concepts," exactly as feared.

## Probability, honestly bounded

| Claim | Probability |
|---|---|
| New philosophical theory | ~5% |
| Independent scientific index | ~20% |
| Useful industrial tool | ~60% |
| Sellable SaaS product | ~50% |
| Category-defining technology | <10% |

**As philosophy: nearly closed. As a governance engine: medium. As decision-level Lock-in
Analytics / Reversibility Intelligence: the first path that genuinely merits serious
industrial diligence** — conditioned on (a) the decision-level gap surviving a real study of
Well-Architected / TOGAF / Gartner / cloud-exit literature, and (b) someone building the
portability knowledge base that makes the score trustworthy.

### The one experiment that flips the story (the industrial ΔR²)

The whole bet reduces to a single, concrete, run-able test — the industrial twin of the
science track's incremental-validity question:

> Take real migration episodes and regress an outcome (**migration cost**, **migration
> duration**, **migration failure**, **vendor-lock-in incidents**) on the existing metrics
> (switching costs, FinOps spend, dependency/architectural risk, quasi-option value); then
> add the FDK lock-in score.
>
> `Existing metrics: R² = 0.42` → `Existing + FDK score: R² = 0.61` ⇒ FDK is a **new risk-
> analytics measurement** (not philosophy, not legitimacy). `ΔR² ≈ 0` ⇒ it is a clever
> repackaging of switching costs / option value, and the venture is dead.

Investor read, by pitch: **"FDK as Freedom Theory" ≤ 5%** · **"FDK as Policy Engine" 10–20%**
(saturated) · **"FDK as a Reversibility Intelligence platform" 40–60% *if real migration data
can be collected*.** The bet is several times stronger as the third than as either of the
others — and it lives or dies on data, not argument.

## 2. The competitive landscape — does FDK solve anything OPA/Cedar/Zanzibar/ABAC don't?

This is the question that decides whether FDK is a category or a feature. Honest reading of
each incumbent:

- **OPA / Rego** (CNCF) — a *general-purpose policy engine*: you write the rules in Rego, it
  evaluates them. FDK's rules **are expressible in Rego.** So FDK is not a rival *engine*; it
  is, at most, an *opinionated rule set* OPA could host.
- **AWS Cedar** (open-source, powers Amazon Verified Permissions) — a policy language that is
  *itself formally verified*. This **neutralises FDK's "we're formally verified" pitch**:
  Cedar got there first, at scale, with a team. Cedar answers "is principal P allowed action
  A on resource R in context C?" — pure authorization; it has no legitimacy layer, but it
  could express one as policy.
- **Google Zanzibar** (→ SpiceDB, OpenFGA) — relationship-based access control: global
  authorization from relationship tuples (`user:alice is owner of doc:42`). **FDK's
  ownership graph is conceptually a Zanzibar relationship store**, and consent could be a
  relation type. Zanzibar already solves the *scale* of "who relates to what."
- **ABAC / XACML** (OASIS) — attribute-based access control with the **PDP/PEP/PAP/PIP**
  architecture. FDK's consent fields (`informed, voluntary, revocable, coerced…`) are
  *attributes*; FDK is a *specialised PDP*; AuthGate is the *PEP*. The "legitimacy-PDP before
  authorization-PDP" chain is **already a standard policy-combining configuration** in XACML.

**Honest competitive verdict: FDK is not a new category of engine.** Everything its mechanism
does is expressible in OPA, Cedar, Zanzibar, or ABAC. Its only candidate differentiators are
*semantic and methodological*, not infrastructural:

1. **The legitimacy ⊥ authority discipline** as a first-class, enforced split (most teams
   conflate them). This is an *architecture pattern*, not an engine capability.
2. **A curated, deterministic, formally-verified, opinionated default policy set** for
   consent-over-boundaries — so an agent team does not have to author it from scratch in Rego.
3. **An AI-agent-specific policy pack** (the machine-sovereignty / corrigibility forbidden
   flags, the aggressor/defender asymmetry) tuned for autonomous-agent governance.

That is a real but *modest* product — **a verified governance policy pack + the
legitimacy-first methodology, riding on existing engines** — not a new platform. The market
will see "another rule engine" unless points 1–3 are marketed as the value, honestly.

## 3. The harder blocker: where does the ownership graph come from?

FDK consumes `owner=Alice`, `coerced=True`, `consent.valid=…` as **inputs**. This is where
governance projects die, and FDK's version is **harder than standard authz**:

- Zanzibar's tuples (`alice is editor of doc:42`) are **facts the application already
  writes** — provenance is trivial.
- FDK's consent attributes (*was this consent coerced? informed? revocable?*) are **not facts
  an app can reliably emit.** "Was she coerced?" has no event in your database. The very
  fields that make FDK's legitimacy layer interesting are the ones with **no trustworthy
  source** — and a legitimacy verdict computed over fabricated or default consent flags is
  theatre. (This is the engineering face of the philosophical Ownership-Genesis problem.)

So FDK's deployability is gated on a **provenance story for consent/ownership** that does not
yet exist. The most honest near-term scope is the narrow case where these inputs *are*
trustworthy: explicit, logged, machine-checkable consent and a known ownership registry
(the `Planner → FDK → AuthGate` agent path, where the orchestrator supplies a real graph) —
not the open world.

## 4. The honest scorecard (conditioned, not free)

| Claim | Status |
|---|---|
| New paradigm of freedom | ≈ rejected (see `paper/`) |
| Independent philosophy / science | unproven |
| Interesting engineering architecture | **yes** |
| Deployable governance engine | **yes — for the narrow, trusted-input case** |
| Solves what OPA/Cedar/Zanzibar/ABAC cannot | **no** — expressible in all of them |
| Potential product value | real but **conditioned** on §2 (differentiation) + §3 (inputs) |
| Value for AI-agent governance | **real** (the "Should I?" gap is real) |
| Unicorn / new category | **no evidence** |

Probability of impact, honestly bounded: *as philosophy* < 5%; *as a product riding AI
agents* ~20–40%; *as a governance-infra component* ~40–60% — **but every one of those is
conditional on solving §3 (the input problem) and proving §2 (differentiation beyond a Rego
policy pack).** Unconditioned, the modal outcome is "a nice, verified, opinionated rule set."

## 5. The one durable idea

The most valuable thing to survive the entire project is probably **not FDK**. It is the
pattern:

> **Put a Legitimacy layer before Authorization** — judge whether an action *should* be
> permitted (consent over boundaries), separately from and prior to whether the actor *is*
> authorized. In one line: **`Can do?` ≠ `May do?`** Every agent framework today optimises
> the first; almost none asks the second.

That pattern is industrially stronger than any philosophical claim, and it is the thing worth
carrying forward — *if* it can be shown to catch real failures (an authorized-but-illegitimate
agent action) that a pure authorization stack waves through. **Honest timing caveat:** its
market is *option value on AI-agent autonomy*, not a today-product — the `May do?` question
only bites hard once agents are autonomous enough that "authorized but shouldn't" becomes a
frequent, expensive failure mode. That day may come; it has not arrived. So of the project's
two surviving threads, **Lock-in Analytics is the near-term bet and `Can do ≠ May do` is the
long-dated option** — and neither is a theory of freedom.

## 6. The clean separation — and the honest bet

Three things were tangled together for most of this project and must be separated:

| Layer | What | Status |
|---|---|---|
| **1. Theory** (نظریه آزادی) | a new normative axis of freedom/legitimacy | **collapsed** — no independence from Nozick/Pettit/Sen found |
| **2. Decision framework** | a structured, computable way to score lock-in at decision time | **medium** — coherent, but its variables are known |
| **3. Product** | an enterprise tool that makes lock-in visible and actionable | **the real opportunity** |

The experiment showed Layer 1 and (probably) the *scientific* part of Layer 2 are
recombinations of known variables. **The biggest *remaining* risk is therefore no longer
philosophical — it is that `FDK Score = a UI around switching cost + portability +
dependency concentration`.** That is a real risk. But the decisive observation is that **it
may not matter for Layer 3**: SonarQube, Datadog, Snyk, and New Relic created *no* new
science — they took existing variables, **aggregated, surfaced, and made them actionable**,
and built billion-dollar markets. A successful tool does not require a new construct; it
requires making an expensive, invisible problem *visible at the moment of decision*.

So the honest bet, and the directive that follows: **stop spending time on freedom, consent,
Pettit, Sen, Rawls — that contest is over.** Spend it on Cloud / Vendor / Platform lock-in,
migration cost, digital sovereignty, and enterprise architecture, around one question:

> **Does an FDK lock-in score lead to a better decision than a Gartner-style architecture
> review?** (decision-value, Q-B) — and secondarily, does it predict migration pain better
> than existing metrics? (Q-A)

That question has industrial value whether or not anything underneath it is novel. The final
read: *low* probability FDK matters as philosophy; *materially higher* probability that part
of it becomes an Enterprise-Architecture / Cloud-Governance tool — and that second path was,
in hindsight, the project's real opportunity from the start. That demonstration — a concrete
agent incident where legitimacy-before-authorization prevents a harm OPA/Cedar/Zanzibar would
allow — is the **product analogue of the ΔR² test**: the one thing that would move FDK from
"another policy engine" to "a layer you actually need." It has not yet been shown, and until
it is, the honest pitch is the modest one: *a deterministic, consent-aware, formally-verified
policy pack and methodology for agent governance — riding on the engines that already exist.*

*Engineering: Ali Pourrahim. Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah
Doust (CC BY 4.0). This is the industrial counterpart to the (negative) philosophical
verdict in [`paper/README.md`](paper/README.md); it is conditioned, not promotional.*
