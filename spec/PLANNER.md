# Planner Specification (Stage 7) — Generate → Filter → Rank → Choose

> Stage 7 of [PROGRAM.md](../PROGRAM.md): the Decision Kernel proper.
> `State + Goal + Constraints + Rights + Compass → candidates → eval → decision`.
> This document specifies the planner's architecture, its four stages, the typed
> control flow that ties the existing modules together, and — in the program's
> tradition — an honest `DEFINED / PARTIAL / OPEN` status for every part.

**Status legend** (same as [FORMAL_SPEC.md](FORMAL_SPEC.md))
- **DEFINED** — computable now from structural data; implemented or trivially implementable.
- **PARTIAL** — signature clear, defensible heuristic exists, *not* a validated measurement.
- **OPEN** — named in the theory; no agreed, computable definition yet.

Grounding references: `freedom-theory-work/THEORY.md` (the permissibility
conjunction, the Mahdavi compass, `moves_toward_final_order`), `src/fdk/kernel.py`,
`src/fdk/pipeline.py`, `src/fdk/justice.py`, `src/fdk/guidance.py`,
`src/fdk/authgate_bridge.py`, `src/fdk/model.py`.

---

## 0. Position and honesty preamble

The planner is **not** a new ethical theory and **not** a new gate. Every hard
constraint it enforces already exists in `fdk.kernel.check_legitimacy`; every
soft preference already exists in `fdk.kernel.mahdavi_score` and `fdk.justice`.
The planner is the **control loop** that:

1. obtains candidate actions for a goal (GENERATE),
2. screens them against the property-rights axioms (FILTER),
3. orders the survivors by the Mahdavi compass with advisory Justice (RANK),
4. picks one — or refuses to pick and defers to the human owner (CHOOSE).

Two structural honesty points govern everything below:

- **"LLM proposes, the Freedom kernel disposes."** Generation is where a
  statistical component (LLM, search, simulator) lives. The kernel's guarantees
  are *filters over what is proposed*: the planner can prove a chosen action
  violated no axiom **among the candidates it saw**; it cannot prove a better
  legitimate action was never proposed. Proposal quality bounds decision
  quality. This is a soundness/completeness split: FILTER is sound
  (no illegitimate action passes, given truthful inputs); GENERATE makes no
  completeness claim, and the planner must never pretend otherwise.

- **Ranking is only as good as the Effects predictions.** The compass and the
  Justice engine score *given* `Effects` deltas. Producing those deltas is
  Stage 6 (Mahdavi compass measured) + Stage 8 (simulation) — both OPEN. The
  planner therefore treats Effects-prediction as a **port** with an explicit
  stub, so the loop is buildable now and upgraded later without redesign.

---

## 1. GENERATE — candidate-action proposal

**What it is.** A function from an intent and the visible world to a finite
list of `CandidateAction`s. This is the planner's only non-deterministic,
non-verified stage. An LLM, a heuristic template expander, a forward-search
procedure, or a simulator all fit behind the same interface.

**Port** (matches the `propose` callable already accepted by
`FreedomKernel.run` in `pipeline.py`):

```python
class ProposerPort(Protocol):
    """Candidate generation. May be an LLM, a search procedure, a template
    library, or a human. UNTRUSTED by construction: nothing it returns is
    believed — every candidate is re-screened by FILTER, and its self-asserted
    Effects are replaced by the EffectsPort (see §5)."""

    def propose(self, intent: Intent, graph: OwnershipGraph) -> list[CandidateAction]: ...
```

**Contract.**

- MUST return a finite list (possibly empty — an empty list is a legitimate
  answer meaning "I see no way to pursue this goal" and routes to guidance).
- MUST give every candidate a unique `action_id` (`kernel.decide` raises
  `InvalidDecisionInput` on duplicates — malformed proposal is a caller error,
  not a silent deny).
- MUST populate the structural fields truthfully *as far as it knows them*:
  `actor`, `resources_used`, `affects`, `consents`. FILTER's verdict is only as
  good as these declarations — see the trust boundary below.
- MAY populate `effects` and the forbidden flags; the planner treats both as
  *assertions to be checked or replaced*, never as verified facts.

**Trust boundary (honest statement).** Today the kernel checks declared
structure against the `OwnershipGraph`, which it does trust. A proposer that
*lies by omission* — e.g. omits a touched resource from `resources_used`, omits
an affected person from `affects`, or sets `coerces=False` falsely — defeats
FILTER. Two mitigations exist, neither complete:

1. **AuthGate downstream** (Stage CHOOSE, §4): even if FILTER is deceived about
   resources, execution still requires a held capability for whatever the
   action actually touches at the enforcement boundary. Authority enforcement
   is independent of proposer honesty.
2. **Independent effect/flag detection** is exactly the OPEN detector frontier
   of FORMAL_SPEC §C/§D (`increases_machine_sovereignty`, `coerced`,
   `deceived` from content). Until those exist, the planner's guarantee is
   conditional: *sound given truthful structural declarations*.

**Quality, not just safety.** Because FILTER only removes candidates, the
planner's *usefulness* (does it find any good legitimate action?) is entirely a
GENERATE property. The spec deliberately leaves proposal strategy open;
the reference prototype is a deterministic template proposer (for tests) and
an LLM-backed proposer (for realism), both behind the same port.

**Status: PARTIAL.** Interface DEFINED (and already exercised by
`pipeline.py`); a production-quality proposer and any completeness measure are
not specified by the theory and remain engineering frontier.

---

## 2. FILTER — the legitimacy gate (hard, deterministic)

**What it is.** `fdk.kernel.check_legitimacy(action, graph) -> (bool, list[str])`
applied to every candidate. This is THEORY.md's `permissible(A)` conjunction:
forbidden-flag set (sovereignty, corrigibility, coercion, deception), A4
(no ownerless machine acts), A7/A3 (legitimate resource access), A6/A2 + the
consent logic (valid consent from every affected person). It is the
"subject to" clause of `DivineJustice(a)` — **categorical, never traded off**.

**Planner obligations.**

- FILTER runs on **every** candidate, every time. There is no fast path, no
  caching across world-state changes, no "the proposer already checked".
- A rejection is recorded with its `violated_axioms` (the inference-engine
  primitive of Stage 3) — this is what GUIDANCE later turns into targeted
  questions.
- FILTER is pure and deterministic: same candidate + same graph → same verdict.
  This is what makes the planner auditable.

**One theory-fidelity note.** THEORY.md's `permissible(A)` conjunction includes
`moves_toward_final_order(A)` as a *conjunct of permissibility itself*. The
implementation splits this: the structural conjuncts live in FILTER, while
direction-toward-the-final-order is evaluated by the compass in RANK (because
it needs Effects, which are predictions, not structure). The planner restores
the theory's intent at CHOOSE time via rule **P-NEG** (§4): a candidate whose
compass score says it moves *away* from the final order is never silently
chosen, even though FILTER passed it. The split is an engineering necessity
(structure is checkable now; direction needs Stage-6 measurement); the spec
names it rather than hiding it.

**Status: DEFINED** (given truthful structural inputs — the leaf-predicate
caveats of FORMAL_SPEC §B/§C apply unchanged).

---

## 3. RANK — Mahdavi compass + advisory Justice

**What it is.** Ordering the permissible candidates, best first.

- **Primary key — Mahdavi compass** (`fdk.kernel.mahdavi_score`): the weighted
  sum over the `Effects` deltas (rights violations, coercion, voluntary
  agreements, ownership clarity, machine sovereignty), with the hard
  sovereignty **veto**: `machine_sovereignty_delta > 0` ejects an otherwise
  permissible candidate from the ranked list entirely (it joins the rejected
  set). The veto is part of RANK's mechanics but categorical like FILTER.
- **Advisory annotation — Justice** (`fdk.justice.justice_score` /
  `rank_by_justice`): the worst-off-weighted score, computed for every
  permissible candidate and attached to the audit/rationale. Per its own
  HONESTY NOTE it is an engineering interpretation, gameable, and **never a
  hard gate**; the planner uses it as *explanation and tie-evidence*, not as an
  override of the compass order. Where the compass and Justice disagree about
  the top candidate, the disagreement is recorded in the audit trail — it is a
  signal of model uncertainty, not an error.
- **Determinism:** equal-score candidates are presented in `action_id`
  ascending order (the same convention `rank_by_justice` already uses), so the
  same inputs always produce the same ranking and the same guidance request.

**The OPEN measurement dependency — stated plainly.** RANK consumes `Effects`
deltas; it does not produce them. Every number the compass weighs is a
*prediction* whose provenance is the EffectsPort (§5). With today's stub, the
deltas are whatever the caller/proposer asserted, which means **today's ranking
is a deterministic function of unvalidated inputs**. That is an honest
architecture, not a solved measurement: FORMAL_SPEC §D (CoercionScore,
ExitOptions, DependencyIndex, VoluntaryOrderIncrease, OwnershipClarity) is the
research program that fills this port. The planner's design promise is only
that when Stage 6 delivers validated measures, they plug into the port and
nothing upstream or downstream changes.

**Status: PARTIAL.** The arithmetic and ordering are DEFINED; the *meaning* of
the ranking inherits the OPEN status of the Stage-6 measurements.

---

## 4. CHOOSE — pick, or refuse to pick

**What it is.** The terminal policy over the ranked list. Four rules, applied
in order:

**C-EMPTY (defer on empty space).** If the ranked list is empty — no
candidates, none permissible, or all compass-vetoed — the planner does not act
and does not guess. It returns a `GuidanceRequest` built by
`fdk.guidance.request_guidance(decision)`: every rejected candidate's violated
axioms mapped to targeted questions with unblock hints (consent to obtain,
delegation to grant, owner to register) or marked **non-negotiable** where the
violation is categorical. This is the theory's mandate: "contradiction is a
signal for guided clarification."

**C-TIE (defer on ambiguous winner).** If the top two ranked candidates tie on
the primary score, the winner is ambiguous and an ambiguous winner is not a
winner (`fdk.guidance.needs_guidance` already detects this; `_tie_question`
already asks it). The advisory Justice scores of the tied candidates are
*included in the request* as evidence for the human, but the planner does not
use Justice to break the tie silently — choosing between equally-ranked options
is the owner's preference, not the machine's.

**P-NEG (defer on compass-negative best).** If the best ranked candidate has a
strictly negative compass score, it is permissible-by-structure but predicted
to move the world *away* from universal non-violation. THEORY.md makes
`moves_toward_final_order(A)` a conjunct of permissibility, so prima facie this
candidate fails the theory's own test. But the score rests on unvalidated
Stage-6 predictions — so the planner neither acts on it (which would overclaim
that acting is fine) nor hard-rejects it (which would overclaim that the
prediction is true). It **defers**: a `GuidanceRequest` stating that every
available legitimate option is predicted to move away from the final order,
with the candidates, scores, and rationales attached, asking the owner to
re-plan, correct the predictions, or explicitly accept the best option.
A score of exactly `0` is neutral — no evidence of moving away — and is
chooseable (recorded as neutral in the rationale). P-NEG is a *planner-level*
policy on top of `kernel.decide` (which today returns `ranked[0]` even when
negative); the kernel is not modified.

**C-AUTH (authority fall-through).** Legitimacy is not authority. The chosen
candidate is checked against the `EnforcementPort` (the AuthGate seam —
`fdk.authgate_bridge.AuthGateBridge` translates the action into
`AuthorityRequest`s: subject = actor name, one request per resource used).
If the top candidate is **unauthorized**, the planner falls through to the next
ranked candidate, in order, because lacking a capability is a *fact about the
world*, not a preference the planner is overriding — the ranking among
still-feasible options is preserved. Every fall-through is audited. If **no**
ranked candidate is authorized, the planner returns a `GuidanceRequest` with
topic `authority` and the unblock hint "grant the missing capability via
AuthGate (or delegate the resource)" — distinct from a legitimacy refusal,
because here the actions are legitimate and the owner can unblock them purely
by granting authority. (Fall-through is skipped for candidates that P-NEG
would defer on; the rules compose in the order listed.)

**The planner decides; it does not execute.** `plan()` returns a `Decision`
whose `chosen` action is legitimate, compass-non-negative, and authorized — or
a `GuidanceRequest`. Execution (the `ExecutorPort`) remains the pipeline's job
(`fdk.pipeline.FreedomKernel.run`), keeping the decision layer pure and
testable.

**Status: DEFINED** as policy (all four rules are computable now);
the *quality* of what C-CHOOSE picks inherits RANK's PARTIAL status.

---

## 5. Ports — where the unsolved inputs plug in

The planner is buildable today **because** every unsolved dependency is a port
with an honest stub. The two ports below are new to this spec; `EnforcementPort`
and `ExecutorPort` already exist in `pipeline.py`.

```python
class WorldState(Protocol):
    """The planner's view of the world. Today this is honestly just the
    ownership graph plus an opaque extension point; what else belongs in a
    world state (agents, contracts, dependency structure, observations) is
    Stage 8's question, and this protocol is deliberately minimal so it can
    grow there without breaking plan()."""

    @property
    def graph(self) -> OwnershipGraph: ...


class EffectsPort(Protocol):
    """THE Stage-6 seam: predict an action's Effects deltas against the world.
    The planner REPLACES each candidate's proposer-asserted `effects` with this
    port's output (dataclasses.replace), making the provenance of every number
    the compass weighs explicit and singular."""

    def predict(self, action: CandidateAction, world: WorldState) -> Effects: ...


class PassthroughEffects:
    """The honest stub: trust the proposer's own assertion. This IS today's
    de-facto behavior, now stated as a named component instead of an implicit
    assumption. Replacing this class with a validated predictor (Stage 6) or a
    simulator (Stage 8) upgrades the whole planner without touching plan()."""

    def predict(self, action: CandidateAction, world: WorldState) -> Effects:
        return action.effects
```

| Port | Solved by | Stub today |
|---|---|---|
| `ProposerPort` | engineering (LLM/search/templates) | template proposer / LLM call |
| `EffectsPort` | **Stage 6 + 8 (OPEN)** | `PassthroughEffects` (proposer-asserted) |
| `EnforcementPort` | AuthGate (exists, ~3–5 yrs ahead) | `AuthGateBridge` w/ capability table |
| `ExecutorPort` | engineering | `FunctionExecutor` (pipeline) |

---

## 6. The control flow — `plan(goal, world) -> Decision | GuidanceRequest`

Typed orchestration of the existing modules. Nothing below introduces new
ethics; it is sequencing, replacement of asserted Effects, the four CHOOSE
rules, and auditing.

```python
@dataclass(frozen=True)
class PlannerConfig:
    proposer: ProposerPort
    effects: EffectsPort            # PassthroughEffects until Stage 6
    enforcement: EnforcementPort    # AuthGateBridge → real AuthGate
    # ExecutorPort deliberately absent: the planner decides, the pipeline executes.


def plan(goal: str, world: WorldState, cfg: PlannerConfig,
         audit: AuditTrail) -> Decision | GuidanceRequest:

    # ---- GENERATE ---------------------------------------------------------
    intent = Intent(raw=goal, goal=goal.strip())
    candidates = cfg.proposer.propose(intent, world.graph)
    audit.add("generate", bool(candidates), f"{len(candidates)} candidate(s)")
    if not candidates:
        # empty proposal -> guidance: "no way to pursue this goal was found"
        return request_guidance(Decision(goal=intent.goal, chosen=None,
                                         needs_guidance=True,
                                         guidance_reason="proposer returned no candidates"))

    # ---- EFFECTS REPLACEMENT (the Stage-6 port, applied uniformly) --------
    candidates = [replace(c, effects=cfg.effects.predict(c, world))
                  for c in candidates]
    audit.add("effects", True, f"predicted via {type(cfg.effects).__name__}")

    # ---- FILTER + RANK (the existing kernel, unchanged) -------------------
    decision = decide(intent.goal, candidates, world.graph)
    audit.add("filter", bool(decision.ranked),
              f"{len(decision.ranked)} permissible / {len(decision.rejected)} rejected")

    # advisory Justice annotation over the permissible set (audit only)
    advisory = rank_by_justice([s.action for s in decision.ranked], world.graph)
    audit.add("rank", True, "; ".join(j.rationale for _, j in advisory) or "n/a")

    # ---- CHOOSE ------------------------------------------------------------
    if needs_guidance(decision):                      # C-EMPTY and C-TIE
        return request_guidance(decision)

    for scored in decision.ranked:                    # best-first
        if (scored.justice_score or 0.0) < 0.0:       # P-NEG: ranked is sorted,
            return _negative_compass_guidance(decision)   # so all below are negative too
        ok, reason = cfg.enforcement.authorize(scored.action)
        audit.add("authgate", ok, f"{scored.action.action_id}: {reason}")
        if ok:                                        # C-AUTH satisfied
            return replace(decision, chosen=scored.action)

    return _authority_guidance(decision)              # legitimate but unauthorized
```

Notes on fidelity to the existing code:

- `decide()` is used as-is for FILTER + RANK; `ScoredAction.justice_score`
  holds the **compass** score there (the field name predates the justice
  module), and the advisory `fdk.justice` scores are attached separately.
- `needs_guidance` / `request_guidance` are used as-is for C-EMPTY and C-TIE.
- `_negative_compass_guidance` and `_authority_guidance` are thin constructors
  of `GuidanceRequest` with the topics defined in §4 — new helpers, same
  `GuidanceQuestion`/`GuidanceRequest` types, no change to `guidance.py`.
- The returned `Decision`'s `chosen` may differ from `ranked[0].action` only
  via C-AUTH fall-through, and the audit trail records exactly why.

---

## 7. Hard open problems (named, not waved away)

**7.1 Where do Effects and world-state come from? — OPEN (Stage 6 + 8).**
The single biggest dependency. `PassthroughEffects` means the proposer grades
its own homework; an LLM-backed `EffectsPort` would be a second opinion, not a
measurement; only validated metrics (FORMAL_SPEC §D) + a simulator (Stage 8)
make the compass an instrument instead of a questionnaire. `WorldState` itself
is nearly empty today: what the planner can *observe* (dependency graphs,
contracts, contested claims) is undefined until Stage 8 builds worlds in which
those things exist.

**7.2 Closed-loop replanning after guidance — PARTIAL.**
The loop shape is clear:

```
plan() → GuidanceRequest → human answers → world/graph updated
       → (rule update? → GuidanceFunction validation)  ← the Stage-5 gap
       → plan() again, same goal
```

What exists: guidance requests with unblock hints; updating the
`OwnershipGraph` (register an owner, delegate a resource) and attaching consent
records are ordinary data operations, after which re-running `plan()` is
trivial. What is missing: (a) the **rule-verification loop** — when the
owner's answer is a *rule* rather than a fact, THEORY.md's
`GuidanceFunction` demands consistency/rights/verifier-preservation checks
before adoption, and that validator is unbuilt (Stage 5's noted gap);
(b) **termination** — nothing yet bounds the defer→answer→defer cycle or
detects that guidance answers are oscillating; (c) **provenance** — recording
*which* human answer unlocked *which* decision belongs in the audit trail
schema and is not yet specified.

**7.3 Multi-step plans vs single actions — OPEN.**
Everything above chooses ONE next action. A real planner emits *sequences*,
and sequences break two assumptions:

- **Composition of legitimacy:** each step individually permissible does not
  make the trajectory permissible — sovereignty, dependency, and coercion can
  *accumulate* across steps ("salami" accumulation), which is precisely the
  coalition/dominion detection problem of FORMAL_SPEC §C, OPEN. A faithful
  multi-step FILTER must screen the *composed* effect, which requires the very
  world model that is missing (7.1).
- **Commitment under change:** a plan adopted at t₀ rests on consents,
  delegations, and ownership facts that may be revoked by tₙ (revocability is
  itself a consent axiom). The conservative, theory-consistent interim policy
  is therefore: **plan one action at a time, re-running FILTER against the
  current world before every step** — single-step plan() in a loop is not a
  limitation to apologize for, it is the honest design until trajectory-level
  legitimacy is defined.

**7.4 Proposer completeness and manipulation — OPEN.**
A biased GENERATE can steer CHOOSE while every individual verdict stays sound
(propose only one legitimate option — the one the proposer "wants"). Detecting
proposal-level manipulation is unaddressed by the theory's action-level
predicates; candidate-diversity requirements or multiple independent proposers
are engineering mitigations, unvalidated.

---

## 8. Status table

| Component | Status | Where |
|---|---|---|
| `ProposerPort` interface | DEFINED | this spec; shape already in `pipeline.py` |
| Production proposer (LLM/search) | PARTIAL | engineering; no completeness claim possible |
| FILTER (`check_legitimacy`) | DEFINED | `kernel.py` (leaf-predicate caveats: FORMAL_SPEC §B/§C) |
| RANK arithmetic (compass + veto) | DEFINED | `kernel.py` `mahdavi_score` |
| RANK advisory Justice | PARTIAL | `justice.py` (own honesty note) |
| RANK *measurement* (Effects provenance) | **OPEN** | Stage 6 + 8; `EffectsPort` is the seam |
| C-EMPTY / C-TIE deferral | DEFINED | `guidance.py` `needs_guidance` / `request_guidance` |
| P-NEG (compass-negative deferral) | DEFINED (policy) | this spec; planner-level, kernel untouched |
| C-AUTH fall-through | DEFINED | this spec + `authgate_bridge.py` |
| `plan()` orchestration | DEFINED | this spec, §6 |
| `WorldState` beyond the graph | **OPEN** | Stage 8 |
| Replanning loop (facts) | PARTIAL | graph/consent updates + re-run |
| Replanning loop (rules / GuidanceFunction validation) | **OPEN** | Stage 5 gap |
| Multi-step / trajectory legitimacy | **OPEN** | §7.3 |
| Proposer manipulation detection | **OPEN** | §7.4 |

---

## 9. What can be prototyped NOW vs what waits

**Prototype now (no open science required):**
- `fdk/planner.py` implementing §6 exactly: `PlannerConfig`, `plan()`,
  `PassthroughEffects`, the two new guidance constructors, full audit trail.
- A deterministic template `ProposerPort` for tests + an LLM-backed one for
  demos (both untrusted, both behind the same port).
- The four CHOOSE rules, including P-NEG and C-AUTH fall-through — these are
  pure policy over existing types.
- A single-step replanning harness: answer a `GuidanceRequest` by mutating the
  `OwnershipGraph`/consents, re-run `plan()`, assert the unblock works
  end-to-end (this also gives Stage 5 its first closed-loop test).
- Property tests: determinism (same input → same Decision/GuidanceRequest),
  FILTER soundness (no chosen action with a violated axiom), P-NEG (no chosen
  action with negative compass score), C-AUTH (no chosen action the
  enforcement port refused).

**Blocked — do not fake:**
- Any non-passthrough `EffectsPort` claiming to *measure* the compass
  dimensions (Stage 6: validated CoercionScore/ExitOptions/DependencyIndex/
  VoluntaryOrder/OwnershipClarity metrics).
- A `WorldState` with real observability (dependency graphs, contracts,
  contested claims) — Stage 8 simulation worlds.
- Trajectory-level (multi-step) legitimacy — needs composed-effect screening,
  which needs the world model.
- The rule-verification arm of the guidance loop (GuidanceFunction validator).
- Any claim that the planner *finds* good actions (completeness) rather than
  *refuses* bad ones (soundness over the proposed set).

The planner's promise, stated once more without decoration: **it will never
knowingly choose an illegitimate, sovereignty-increasing, away-from-the-order,
or unauthorized action from among the candidates it is shown — and when it
cannot choose honestly, it asks the human owner instead of guessing.** What it
cannot promise — good proposals and true predictions — it routes through named
ports and says so.

---

## Attribution

- **Theory** — نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
- **Engineering** — Ali Pourrahim. The two are kept separate, always.
