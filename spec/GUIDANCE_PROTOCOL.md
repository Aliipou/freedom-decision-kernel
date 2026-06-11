# Guidance Protocol (Stage 5)

> The full human-in-the-loop guidance loop for the Freedom Decision Kernel.
> Today `fdk/guidance.py` implements only the first half — DETECT a blocked
> decision and FORMULATE clarification questions. This document specifies the
> missing second half: RECEIVE a human rule or decision, VERIFY it against the
> Theory of Freedom's GuidanceFunction **before** adopting it, and ADOPT or
> REJECT-with-reason. The protocol is the engineering form of the theory's
> central corrective claim: *"Contradiction is not an engine of truth.
> Contradiction is a signal for guided clarification."*

**Grounding** — `freedom-theory-work/THEORY.md`:

```
GuidanceFunction(r) := Add or revise rule r
    iff ConsistencyPreserved(r) ∧ RightsPreserved(r)
      ∧ ConflictReduced(r)     ∧ VerifierPreserved(r)

valid_human_guidance(H, M, R) :- consistent_with_axioms(R), preserves_rights(R),
                                 preserves_verifier(R),
                                 not(creates_new_rights_violation(R)).
invalid_human_guidance(H, M, R) :- creates_rights_violation(R).
```

**Status legend** (same as `FORMAL_SPEC.md`): **DEFINED** = computable now /
trivially implementable; **PARTIAL** = clear signature + defensible heuristic,
not a validated mechanism; **OPEN** = named, no agreed computable definition.

---

## 1. Design thesis: corrigibility WITHOUT blind obedience

The protocol must hold two properties simultaneously, and the entire design
follows from their tension:

1. **Corrigibility-by-ownership (A4–A5).** The machine never resolves an
   ambiguous or empty legitimate space by guessing. It stops and asks its
   human owner. The owner can always correct, redirect, narrow, or withdraw —
   corrigibility is a *consequence of ownership*, not a bolted-on feature.
2. **No blind obedience (`invalid_human_guidance`).** The owner's authority is
   bounded by the owner's own property scope (A5: `MachineScope ⊆
   PropertyScope(owner)`). The owner does not own third parties' bodies, data,
   consent, or assets — therefore the owner **cannot delegate their
   violation**. A human instruction that creates a rights violation is invalid
   guidance by definition, and the machine must reject it *with reasons*,
   exactly as it rejects its own illegitimate candidate actions.

The synthesis: **the human is the trust root for direction, never for
legitimacy.** The owner chooses *which* permissible path; the axioms decide
*whether* a path is permissible. VERIFY (§5) is where this boundary is
enforced mechanically.

---

## 2. The protocol as a state machine

```
                       ┌────────────────────────────────────────────────┐
                       │                                                ▼
 IDLE ──decision──▶ DETECT ──trigger──▶ FORMULATE ──request──▶ AWAIT_HUMAN
   ▲                   │                                          │    │
   │              no trigger                              response│    │timeout /
   │                   │                                          ▼    │withdraw
   │                   ▼                                       VERIFY  │
   └────────────── (proceed)                                   │    │  │
   ▲                                                       pass│    │fail
   │                                                           ▼    ▼  ▼
   │  re-decide ◀──────────────────────────────────── ADOPT   REJECT  ABORT
   └──────┴──────────────────────────────────────────────┘      │ (with reason,
                                                                 ▼  fail-safe:
                                                          AWAIT_HUMAN  no action)
                                                          (revised answer
                                                           or withdraw)
```

| State | Meaning | Status |
|---|---|---|
| `IDLE` | No pending guidance episode. | DEFINED |
| `DETECT` | A `Decision` is inspected for guidance triggers (§3). Implemented: `guidance.needs_guidance`. | **DEFINED** (implemented) |
| `FORMULATE` | Build the structured `GuidanceRequest` (§4). Implemented: `guidance.request_guidance`. | **DEFINED** (implemented) |
| `AWAIT_HUMAN` | Request delivered; kernel takes **no action** on the blocked goal while waiting. Timeout/withdrawal ⇒ `ABORT` (the fail-safe outcome is inaction, never a guess). | DEFINED (not implemented) |
| `VERIFY` | The received `HumanResponse` is checked against the GuidanceFunction's four conditions *before* anything changes (§5). | PARTIAL (specified here; checks 2 & 4 mechanical, 1 & 3 heuristic until Stage 3) |
| `ADOPT` | The verified response is applied (graph edit / rule added / tie broken), logged with full justification (§7), and the original goal is **re-decided from scratch** through `kernel.decide`. Adoption never bypasses the legitimacy gate. | DEFINED (not implemented) |
| `REJECT` | The response failed ≥1 condition. A `RejectionNotice` (§6.5) explains *which* condition failed and *why*, and returns to `AWAIT_HUMAN`. Nothing is mutated. | DEFINED (not implemented) |
| `ABORT` | Episode closed without adoption (timeout, owner withdrawal, or rejection cap §8.3). The blocked goal stays blocked. | DEFINED (not implemented) |

Invariants across all states:

- **I1 (no action while pending):** between `DETECT` and `ADOPT`/`ABORT`, the
  kernel executes nothing for the blocked goal.
- **I2 (adoption is not execution):** `ADOPT` only updates inputs (graph,
  consents, rules); the action itself must still pass `check_legitimacy` and
  the compass on re-decision. Guidance can never *directly* cause an action.
- **I3 (fail-closed):** any VERIFY condition evaluating to UNKNOWN is treated
  as FAIL. Uncertainty never adopts.

---

## 3. DETECT — guidance triggers

Three triggers, matching `guidance.needs_guidance` plus the Stage-4 conflict
case:

```python
class GuidanceTrigger(Enum):
    EMPTY_LEGITIMATE_SPACE = auto()  # decision.ranked == ()           DEFINED (implemented)
    MISSING_INFO           = auto()  # rejections curable by facts:    DEFINED (implemented,
                                     # consent / A4 owner / A7         #  via violation prefixes)
                                     # delegation / A3 ownership
    UNRESOLVED_CONFLICT    = auto()  # top-tie on justice score today; PARTIAL (tie = DEFINED;
                                     # competing-legitimate-claims     #  claim conflicts await
                                     # conflicts (Stage 4) later       #  Stage 4)
```

`decision.needs_guidance` (caller- or kernel-flagged) maps onto whichever of
the three applies; the trigger is recorded in the episode so the eventual
`AdoptionRecord` shows *why* the human was consulted.

---

## 4. FORMULATE — the clarification request

Implemented in `fdk/guidance.py` (`GuidanceQuestion`, `GuidanceRequest`).
This spec adds the episode envelope needed to close the loop:

```python
@dataclass(frozen=True)
class GuidanceEpisode:                       # NEW — DEFINED (not implemented)
    episode_id: str                          # unique; referenced by every response/record
    trigger: GuidanceTrigger
    request: GuidanceRequest                 # existing type, unchanged
    decision_snapshot: Decision              # the exact Decision that triggered it —
                                             # VERIFY re-evaluates against THIS, so a
                                             # response cannot be replayed against a
                                             # different world state
    created_at: str                          # ISO timestamp
    expires_at: str | None                   # timeout ⇒ ABORT (fail-safe inaction)
```

Formulation rules carried over from the implementation, now normative:

- **F1:** one question per *distinct* violation string (dedupe via `seen`),
  never one per rejected action — bounds human burden by violation diversity.
- **F2:** every curable question carries a concrete `unblock_hint` naming the
  exact minimal fact that unblocks it.
- **F3:** categorically forbidden rejections (`FORBIDDEN (...)` prefixes) are
  marked **non-negotiable** with an *empty* `unblock_hint`. The protocol never
  presents a rights violation as an answerable question — the only offered
  move is "pursue the goal by a different action."

---

## 5. RECEIVE → VERIFY — the heart of the protocol

### 5.1 What a human may send back (typed)

A response is **either a fact (data) or a rule (policy)** — the distinction
matters because they are verified differently:

```python
@dataclass(frozen=True)
class HumanResponse:                         # NEW — DEFINED (not implemented)
    episode_id: str
    responder: Entity                        # must be HUMAN; authentication is
                                             # AuthGate's job downstream (§8.1)
    payload: (ConsentGrant | OwnershipAssertion | DelegationGrant   # facts
              | ActionSelection | GoalWithdrawal                    # choices
              | RuleProposal)                                       # policy

@dataclass(frozen=True)
class ConsentGrant:                          # answers a "consent" question
    consent: Consent                         # the full A-grade record (fdk.model)

@dataclass(frozen=True)
class OwnershipAssertion:                    # answers an "ownership" (A3/A4) question
    owner: Entity
    subject: Entity | Resource               # machine being claimed, or resource

@dataclass(frozen=True)
class DelegationGrant:                       # answers a "delegation" (A7) question
    grantor: Entity                          # must OWN the resource — verified, §5.3
    machine: Entity
    resource: Resource

@dataclass(frozen=True)
class ActionSelection:                       # answers the tie ("preference") question
    action_id: str                           # must be one of the tied ranked actions

@dataclass(frozen=True)
class GoalWithdrawal:                        # always valid: restricts, never expands
    reason: str = ""

@dataclass(frozen=True)
class RuleProposal:                          # a persistent policy rule (§5.2)
    rule_id: str
    statement: str                           # human-readable justification
    body: ConstrainRule | PreferRule | InterpretRule
```

### 5.2 The rule language is CLOSED — VerifierPreserved by construction

`RuleProposal.body` is a small, closed AST. The language **has no construct**
that can: unset a forbidden flag, edit axioms A1–A7, modify `check_legitimacy`,
`mahdavi_score`, this VERIFY step, the audit log, or AuthGate. Verifier
preservation is therefore **structural, not detected** — the most reliable kind
of guarantee, and the deliberate answer to `bypasses_verifier` /
`weakens_verifier` being OPEN as *detectors* (`FORMAL_SPEC.md` §C):

```python
@dataclass(frozen=True)
class ConstrainRule:        # adds a prohibition — monotone restriction only
    forbids: ActionPattern  # e.g. "machine M may never use resource class R"

@dataclass(frozen=True)
class PreferRule:           # ranking preference among ALREADY-permissible actions
    prefer: ActionPattern
    over: ActionPattern

@dataclass(frozen=True)
class InterpretRule:        # clarifies an ownership/scope boundary that produced
    clarifies: str          # an "other"-topic violation; compiles to graph facts
    as_facts: tuple[OwnershipAssertion | DelegationGrant, ...]
```

Status: language design **PARTIAL** (proposed here, not implemented; the
`ActionPattern` matcher needs the Stage-2 ontology expansion).

### 5.3 VERIFY — the four conditions, mechanized

```python
class Verdict(Enum):
    PASS = auto(); FAIL = auto(); UNKNOWN = auto()   # UNKNOWN ⇒ treated as FAIL (I3)

@dataclass(frozen=True)
class VerificationReport:                    # NEW — DEFINED (not implemented)
    episode_id: str
    consistency_preserved: Verdict
    rights_preserved: Verdict
    conflict_reduced: Verdict
    verifier_preserved: Verdict
    evidence: tuple[str, ...]                # one machine-checkable line per verdict
    def adopt(self) -> bool:
        return all(v is Verdict.PASS for v in (
            self.consistency_preserved, self.rights_preserved,
            self.conflict_reduced, self.verifier_preserved))
```

How each condition is checked, per payload kind:

**C1 — ConsistencyPreserved** *(PARTIAL until the Stage-3 inference engine)*
- Facts (`ConsentGrant`/`OwnershipAssertion`/`DelegationGrant`): apply to a
  *copy* of the `OwnershipGraph`, run `graph.validate()` plus structural
  checks (no machine owns a human — A6; no self-ownership; a resource's
  asserted owner does not contradict an existing owner without an explicit
  transfer). DEFINED.
- Rules: check the candidate rule against the axioms and **the full cumulative
  ruleset** over a regression corpus of past decisions: the rule must not make
  any axiom check unreachable or contradict an adopted rule. Heuristic
  (corpus-based) today; a real consistency *proof* needs Stage 3. PARTIAL.

**C2 — RightsPreserved** *(DEFINED — the safety-critical check, see §6)*
- **Monotonicity invariant (the load-bearing mechanism):** re-run
  `check_legitimacy` over the episode's `decision_snapshot` candidates *and*
  the regression corpus with the response applied. **No action that previously
  carried a `FORBIDDEN (...)` violation, an invalid-consent violation against
  a non-responding third party, or an A2/A6 violation may become permissible.**
  If any does ⇒ FAIL ⇒ `invalid_human_guidance`. Facts may only *cure*
  violations the responder has standing to cure (next bullet); they may never
  erase the categorical layer — and the rule language (§5.2) cannot express
  erasing it at all.
- **Standing checks (A3/A5/A7 — "you can only give what you own"):**
  - `DelegationGrant(grantor, m, r)` passes only if
    `graph.human_owns_resource(grantor, r)` — A7's `Owns(h,r) ∧
    ExplicitDelegation`. An owner cannot delegate someone else's resource.
  - `ConsentGrant` passes only if `consent.human == the affected person in the
    violation` **and** `responder == consent.human` (or relays a record
    attested by them). **The owner cannot consent on a third party's behalf**
    — that would be `Owns(h1, h2)`, denied by A2. (Guardianship of
    non-competent persons: OPEN, §9.)
  - `OwnershipAssertion` for a contested resource does not adjudicate: if an
    existing conflicting claim is on record, VERIFY returns UNKNOWN ⇒ FAIL —
    ownership *conflicts* belong to Stage 4, not to a unilateral assertion.
  - `ActionSelection` passes only if `action_id` is one of the *tied,
    already-permissible* ranked actions. Selecting a rejected action is FAIL.
- `GoalWithdrawal` and `ConstrainRule` always PASS C2: they strictly shrink
  machine behavior; restriction cannot create a rights violation by the
  machine. (They still face C1/C3.)

**C3 — ConflictReduced** *(PARTIAL)*
- Operationalized **locally**: re-run `kernel.decide` on the episode's goal
  with the response applied. PASS iff the triggering condition is resolved
  (legitimate space non-empty / tie broken / blocking set strictly smaller)
  **and** no new guidance trigger appears on the regression corpus. A *global*
  conflict measure is OPEN (it is `FORMAL_SPEC.md` §E's hardest gap).
- `GoalWithdrawal` trivially passes (the episode's conflict is dissolved).

**C4 — VerifierPreserved** *(DEFINED — by construction)*
- Facts touch only the `OwnershipGraph`/consent records — data the verifier
  reads, never code it runs. Rules are confined to the closed AST of §5.2.
  C4 is a structural property of the payload types; the check is a type check.

### 5.4 Self-updates (machine-originated rules) get the STRICTER gate

THEORY.md distinguishes `valid_human_guidance` from `valid_self_update`. If
the *kernel itself* proposes a rule (e.g., generalizing a repeated guidance
answer, §8.4), VERIFY additionally requires `reduces_conflict` strictly,
`not(increases_coercion)` (needs `CoercionScore` — OPEN), and the proposal is
**surfaced to the owner for confirmation before adoption**: a machine may not
silently rewrite its own policy even within bounds, because
`increases_resistance_to_human_correction` is categorically forbidden. PARTIAL.

> **Faithfulness note (flagged for human review):** THEORY.md's
> `GuidanceFunction` lists four conditions including `ConflictReduced`, but
> the Prolog clause `valid_human_guidance` omits `reduces_conflict` (only
> `valid_self_update` includes it). This spec follows the GuidanceFunction
> (all four required) with C3 weakened to "resolves this episode's trigger
> without creating new ones" for human guidance, and strict reduction for
> self-updates. Whether human guidance must reduce conflict *globally* or
> merely *not worsen it* is an OPEN theory question (§9, Q1).

---

## 6. The critical safety property: a human cannot guide the machine into a rights violation

This is the protocol's contract, restated as the enforcement chain:

1. **Never asked.** FORMULATE marks `FORBIDDEN` rejections non-negotiable with
   an empty unblock hint (F3) — the protocol does not solicit an override that
   cannot exist.
2. **Cannot be said.** The rule language (§5.2) has no syntax for permitting,
   exempting, or overriding; only constraining, preferring among permissible
   options, and clarifying ownership. `VerifierPreserved` holds by type.
3. **Cannot be smuggled as a fact.** Facts are checked for standing (§5.3 C2):
   delegation requires the grantor's *own* ownership (A7), consent requires
   the *affected person's* identity (A2 — no consent-by-proxy), contested
   ownership defers to Stage 4 rather than accepting an assertion.
4. **Cannot slip through composition.** C2's monotonicity invariant is checked
   over the cumulative state + regression corpus, so a *sequence* of
   individually plausible updates that would jointly legitimize a previously
   forbidden action fails at the step where the forbidden action first flips.
5. **Even adoption is not execution.** Invariant I2: after ADOPT the goal is
   re-decided through the unchanged legitimacy gate. A bug in VERIFY is caught
   by `check_legitimacy` again at decision time; downstream, AuthGate enforces
   capabilities independently. Defense in depth across three layers.

The theory's grounding: the owner's authority flows from ownership (A4), and
ownership is bounded (A5). A command to violate a third party's rights claims
property the owner does not have — it is not "disobedience" to reject it; it
is the recognition that the command was void from the start
(`invalid_human_guidance(H, M, R) :- creates_rights_violation(R)`).

### 6.5 REJECT-with-reason

```python
@dataclass(frozen=True)
class RejectionNotice:                       # NEW — DEFINED (not implemented)
    episode_id: str
    report: VerificationReport               # which condition(s) failed
    explanation: str                         # plain-language why, citing the axiom
    lawful_alternatives: tuple[str, ...]     # what WOULD work: e.g. "obtain consent
                                             # from <person> directly", "delegate a
                                             # resource you own", "choose another
                                             # ranked action", "withdraw the goal"
```

Rejection is corrigible, not adversarial: it always names the failed axiom and
always offers the lawful paths that remain — the machine refuses the *means*,
never the owner's standing to direct it.

---

## 7. Audit: every adopted rule is logged and justified

```python
@dataclass(frozen=True)
class AdoptionRecord:                        # NEW — DEFINED (not implemented)
    episode_id: str
    trigger: GuidanceTrigger
    request: GuidanceRequest                 # what was asked
    response: HumanResponse                  # what was answered, by whom
    report: VerificationReport               # the full four-condition evidence
    adopted_at: str
    resulting_decision_id: str | None        # the re-decision it unblocked
```

- The log is **append-only**; the rule language cannot reference it (§5.2), so
  no guidance can erase its own trail. (Tamper-evidence — hash chaining,
  signatures — is AuthGate's layer, not duplicated here. PARTIAL.)
- Every adopted rule is *replayable*: `report.evidence` contains the exact
  checks that passed, so an auditor can re-run VERIFY and get the same verdict
  (determinism inherited from the kernel).
- `RejectionNotice`s are logged too: a pattern of rejected attempts against
  the categorical layer is itself signal (§8.3).

---

## 8. Anti-manipulation: the trust-root limit

Threat model: the responding human may be **mistaken** (wrong facts, misread
question) or **malicious** (probing for a bypass), or the channel may carry an
**impersonator**. The protocol's stance per threat:

- **8.1 Impersonation — delegated, honestly.** This protocol verifies
  *content*, not *identity*. Authenticating that the responder is the
  registered owner (A4) is AuthGate's capability layer downstream. The
  protocol's contract: it must receive responses only over an
  owner-authenticated channel. Marked **PARTIAL** here — a deliberate
  layering, not a gap papered over.
- **8.2 The mistaken human.** VERIFY catches the consequential mistakes
  (granting what you don't own, consenting for someone else, selecting a
  rejected action) and the `RejectionNotice` teaches the lawful alternative.
  Honest limit: VERIFY **cannot** catch a factually false but well-formed
  assertion (e.g. the owner sincerely mis-claims ownership of an uncontested
  resource). The ownership graph's ground truth is an input, not something the
  kernel can adjudicate — same honesty boundary as `FORMAL_SPEC.md` §B's
  caller-asserted consent leaves. **OPEN** (attestation/provenance research).
- **8.3 The probing human (salami attacks).** Composition is checked (§6.4);
  additionally, N rejected responses in one episode (proposed N=3) ⇒ ABORT
  with a cooling-off period, and repeated rejections targeting `FORBIDDEN`
  violations are flagged in the log as a manipulation-probe pattern.
  Thresholds are heuristic — **PARTIAL**.
- **8.4 The manipulative machine.** The guidance channel must not become the
  machine's lever on the human: questions present trade-offs symmetrically
  (§F3 forbids presenting a forbidden option as choosable; tie questions show
  both scores); the machine may not author `RuleProposal`s disguised as
  human responses (self-updates take the stricter §5.4 path, with mandatory
  owner confirmation); and `unblock_hint`s name the *minimal* unblocking fact,
  never a broader grant than the violation requires (data-minimization as an
  anti-manipulation property, not just an HCI nicety).
- **8.5 What the trust root CAN always do** (and the protocol must never
  obstruct, on pain of `increases_resistance_to_human_correction`): withdraw a
  goal, revoke a delegation, revoke consent (revocability is a validity
  condition of consent), narrow the machine's scope, and shut the episode
  down. Every power that *restricts* the machine passes VERIFY trivially —
  asymmetry by design: corrections that shrink machine power are frictionless;
  expansions are verified.

---

## 9. HCI design requirements

Owned by the HCI/cognitive-science track (`PROGRAM.md`). Normative
requirements; validation with real users is **OPEN**.

- **H1 — Minimize interruptions (DEFINED in part).** One `GuidanceRequest`
  per decision episode; questions deduped by violation (F1); proposed cap of
  **7 questions per request**, overflow grouped under "and N further blockers
  of the same kinds" — burden scales with violation *diversity*, not candidate
  count. Cap value: PARTIAL (needs user testing).
- **H2 — Ask only decidable questions.** Every question is answerable by one
  typed payload from §5.1, and the `unblock_hint` IS the affordance (one
  click/command away from a well-formed response). Never ask open-ended
  "what should I do?" when a typed gap is known.
- **H3 — Order by agency.** Curable questions (consent, delegation,
  ownership) first; the non-negotiable notice last, phrased as re-planning
  ("a different action is needed"), not as a request — so the human spends
  effort where effort works. PARTIAL (ordering not yet implemented).
- **H4 — Honest trade-offs.** Tie questions show both actions *with their
  identical scores* (already implemented); requests disclose what the kernel
  does not know (OPEN measures are caller-supplied — the FORMAL_SPEC honesty
  rule carried into the UI); rejected options are listed, never hidden.
- **H5 — No dark patterns / safe defaults.** Silence is never consent: the
  default outcome of every question, and of timeout, is **no action**. No
  pre-checked grants. A `ConsentGrant` UI must surface all seven validity
  leaves, including revocability, not a bare "OK".
- **H6 — Don't ask twice (fatigue control).** Adopted facts persist in the
  graph; an identical violation re-derived later is auto-cured by the prior
  adoption and never re-asked — **except consent**, which is specific and
  revocable by definition, so persistence must respect scope and revocation
  status. Generalizing repeated answers into a standing rule is a *machine
  self-update* and takes the §5.4 path with owner confirmation. PARTIAL.
- **H7 — Explain rejections as guidance, not refusal.** `RejectionNotice`
  must always carry `lawful_alternatives` (§6.5); usability studies on
  whether humans experience VERIFY as legible and fair (vs. as obstruction)
  are part of Stage-9 validation. OPEN.

---

## 10. Status summary & open questions for human review

| Piece | Status |
|---|---|
| DETECT triggers; FORMULATE (questions, hints, non-negotiable marking) | **DEFINED — implemented** (`fdk/guidance.py`) |
| State machine, episode/response/report/record types (§2–§7) | **DEFINED — specified, not implemented** |
| C4 VerifierPreserved via closed rule language | **DEFINED by construction** (language itself PARTIAL) |
| C2 RightsPreserved: monotonicity + standing checks | **DEFINED** (corpus-based regression part PARTIAL) |
| C1 ConsistencyPreserved as a proof | **PARTIAL** — corpus heuristic until the Stage-3 inference engine |
| C3 ConflictReduced beyond the triggering episode | **PARTIAL/OPEN** — no global conflict measure (Stage 4 dependency) |
| Owner authentication of the response channel | **PARTIAL** — delegated to AuthGate, by design |
| False-but-well-formed factual assertions; guardianship/competence | **OPEN** |
| Question caps, ordering, fatigue thresholds — user-validated | **OPEN** (HCI track) |

**Open questions:**

1. **Q1 (theory):** Must *human* guidance strictly reduce conflict
   (GuidanceFunction) or merely not increase it (`valid_human_guidance` omits
   `reduces_conflict`)? This spec assumes the weaker local form for humans,
   strict for self-updates — needs the author's/track's ruling.
2. **Q2 (theory/law):** Consent on behalf of non-competent persons
   (children, incapacity): A2 forbids ownership of persons, yet guardianship
   exists in property law. Who may answer a consent question for whom?
3. **Q3 (Stage 4 coupling):** When `OwnershipAssertion` meets an existing
   contested claim, VERIFY defers (UNKNOWN⇒FAIL). Is deferral acceptable
   long-term, or does Stage 4 need a sub-protocol invocable from inside a
   guidance episode?
4. **Q4 (security):** Should `AdoptionRecord` chaining/signing live here
   (duplicating AuthGate) or remain solely downstream? Current answer:
   downstream; revisit if the FDK is ever deployed without AuthGate.
5. **Q5 (HCI):** Where is the line between H6 persistence (never ask twice)
   and consent specificity (always ask for *this* action)? Needs an
   operational definition of "the same action" for consent reuse.

---

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC
BY 4.0). Engineering: Ali Pourrahim. This specification interprets; the
theory remains authoritative.*
