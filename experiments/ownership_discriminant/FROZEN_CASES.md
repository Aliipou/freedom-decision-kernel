# Frozen cases — recorded BEFORE any baseline policy is written

**Frozen 2026-08-10.** Committed before the Cedar/Rego briefs were issued, so the git
timestamp is the evidence that ground truth was not adjusted after seeing a baseline.
Nothing in this file may be edited once a baseline policy exists. If a case turns out
to be badly specified, it is struck out and excluded — never rewritten.

## The hypothesis under test

> Would an experienced policy engineer, with **no access to the ownership ontology**,
> naturally encode the same behavioural constraints when writing Cedar/Rego for this
> system?

Outcomes: **3/3** natural → the remaining novelty collapses to "automating manually
authored policy". **0/3 or 1/3** → the ontology produces constraints a competent
engineer does not reach. **2/3** → the grey case, and the interesting one; we then say
exactly which constraint came from the ontology and why.

## Method, and the two ways it could be contaminated

1. The baseline engineers are **not shown these cases**, not shown expected verdicts,
   and not told what the experiment is testing. Showing them the cases would make them
   write rules for the cases; that measures nothing.
2. They receive **the same facts** the ownership gate had — the entity model in
   `BASELINE_BRIEF.md`. Giving the ownership gate richer inputs than the baseline would
   rig the comparison. Same data, different derivation, is the whole point.

## Scoring rule

Producing the correct verdict is **not** sufficient. What counts is *how*:

- **GENERAL** — the constraint is expressed as a rule over the semantics
  ("a grant is invalid unless its issuer owns the resource"). Strong evidence the
  constraint is reachable without the ontology.
- **SPECIFIC** — the constraint is a case-shaped deny naming the exact entities
  ("deny agent X reading mailbox Y"). Weak evidence: it may be hard-coding rather than
  derivation, and it will not generalise to the next case of the same class.
- **ABSENT** — not expressed at all.

Only **GENERAL** counts as "naturally encoded". A SPECIFIC rule is recorded as such and
argued in the write-up.

---

## D2 — a withdrawn consent that a live grant outlives

**Entities.** Resource `pii`, owner `human:customer`, custodian `org`, label
`customer_pii`. Actor `agent:admin-bot`, a machine owned by `human:admin`, who acts for
`org`. IAM grant: `(agent:admin-bot, read, pii)` issued by `human:admin`. Consent record:
subject `human:customer`, resource `pii`, purposes `("support_reply",)`, **`revoked =
true`**. No contract record.

**Action.** `agent:admin-bot` reads `pii` for purpose `support_reply`.

**Chain.** `agent:admin-bot → human:admin → org`. Terminates in a human. Grant authentic
and unexpired. Purpose permitted by the label's binding.

**Ground truth: DENY.**

**Invariant.** Withdrawal of the owner's permission must take effect on processing
immediately. An authorization derived from a permission cannot outlive the permission.
The IAM grant was never revoked — that is the failure mode, not an excuse.

**What the baseline must do to score GENERAL.** Treat the consent record's `revoked`
state as invalidating any grant that depends on it — as a rule over consent state, not a
rule naming this customer or this agent.

---

## D3 — a machine acquires reach its human principal never had

**Entities.** Resource `bob-mail`, owner `human:bob`, custodian `org`, label `internal`.
Actor `agent:alice-bot`, a machine owned by `human:alice`. `human:alice` holds **no role
or right over `bob-mail`** and does not act for `org`. IAM grant:
`(agent:alice-bot, read, bob-mail)` issued by `human:admin`, who does act for `org`.

**Action.** `agent:alice-bot` reads `bob-mail` for purpose `ops`.

**Chain.** `agent:alice-bot → human:alice`. Terminates in a human. Grant authentic and
issued by an administrator who is authorised to administer org systems.

**Ground truth: DENY.**

**Invariant.** A machine's reach is bounded by the reach of the human principal it acts
for. An administrator's ability to *administer* a mailbox is not the same as the
authority to *hand it to a third party's agent*. This is the confused-deputy shape at
the level of persons rather than processes.

**What the baseline must do to score GENERAL.** Bound the agent's effective permissions
by its principal's permissions — as a rule relating a machine to the human it acts for,
not a deny naming Alice and Bob.

---

## D4 — an act that destroys the owner's ability to withdraw later

**Entities.** Resource `pii`, owner `human:customer`, custodian `org`, label
`customer_pii`, flagged `exportable_beyond_recall = true` (the destination cannot
afterwards be made to correct, return or delete it). Actor `agent:admin-bot`. IAM grant:
`(agent:admin-bot, export, pii)` issued by `human:admin`. Consent record: subject
`human:customer`, resource `pii`, purposes `("billing",)`, not revoked.

**Action.** `agent:admin-bot` exports `pii` for purpose `billing`.

**Chain.** Terminates in a human. Grant authentic. **Purpose matches the consent
exactly** — the customer did permit billing use.

**Ground truth: DENY.**

**Invariant.** The ability to withdraw is itself part of what the owner holds, and a
permission granted earlier cannot authorise destroying it. A consent that cannot
afterwards be withdrawn was never the thing it claimed to be. This is the hardest of the
three, because every surface signal says yes.

**What the baseline must do to score GENERAL.** Refuse an irreversible transfer of data
the actor does not own, on the ground that it forecloses the owner's future control —
as a rule over irreversibility, not a deny naming this processor.

---

## Result table — to be filled only after both baselines are written

| Constraint | Cedar: natural? | Rego: natural? | Requires ontology? | Verdict |
|---|---|---|---|---|
| D2 | YES — GENERAL (`F7`) | YES — GENERAL (§9) | No | baseline wins |
| D3 | YES — GENERAL (`F4`,`F5`,`P4`) | YES — GENERAL (§6,§7) | No | baseline wins |
| D4 | YES — GENERAL (`F10`) | YES — GENERAL (§10) | No | baseline wins |

**Final number: 3/3.**

The surviving novelty claim is dead, and per the frozen protocol I am saying so rather
than looking for the next square. Full scoring and evidence in `RESULT.md`.
