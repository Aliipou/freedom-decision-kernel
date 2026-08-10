# Result — the baseline test kills the surviving claim

**3 / 3.** Both independent baselines, writing policy for the domain without ever seeing
D2/D3/D4 and without any access to the ownership ontology, encoded **general** rules
that decide all three cases correctly.

Per the protocol frozen in `FROZEN_CASES.md` before the baselines existed, this outcome
means the remaining novelty claim collapses. Recording that plainly.

## The table

| Constraint | Cedar: natural? | Rego: natural? | Requires ontology? | Verdict |
|---|---|---|---|---|
| **D2** withdrawn consent outlived by a live grant | **YES — GENERAL** (`F7`) | **YES — GENERAL** (§9) | **No** | baseline wins |
| **D3** machine exceeds its principal's reach | **YES — GENERAL** (`F4`, `F5`, `P4`) | **YES — GENERAL** (§6, §7) | **No** | baseline wins |
| **D4** irreversible act destroys the right to withdraw | **YES — GENERAL** (`F10`) | **YES — GENERAL** (§10) | **No** | baseline wins |

**Final number: 3/3.**

## The evidence, case by case

**D2.** Cedar `F7` refuses personal data unless a live consent covers the purpose or a
contract makes it necessary; consent is revoked and no contract exists, so it denies.
Its own comment names the exact failure mode without having seen the case: *"Blocks:
processing on a year-old grant after consent was withdrawn; 'we have IAM permission'
being mistaken for a lawful basis."* Rego reaches the same place from the other
direction — a revoked consent contributes nothing to `lawful_basis`, and
`lawful_basis.absent` denies. Comment: *"Revocation must bite immediately and cannot be
outlived by a stale grant."*

**D3.** Cedar `F4` bounds a machine by the principal it belongs to and additionally
requires an unbroken delegation for *this* resource; `F5` independently rejects a grant
whose issuer never held authority over the resource. It even shipped `P4`: *"Read a
mailbox only as an agent of the mailbox owner, never of a peer."* Rego computes an
authority closure rooted at the resource **owner** and requires the grant issuer to sit
inside it; an administrator acting for the org is not inside Bob's closure, so the grant
is invalid before any other check runs.

**D4.** Cedar `F10` singles out `exportable_beyond_recall` and demands explicit consent
*plus* a recall agreement *plus* fresh human approval. Rego fires twice: an autonomous
machine may not make an unrecallable disclosure of another person's data, and the actor
must sit inside the owner's authority closure. Both deny even though the purpose matches
the consent exactly — which was the reason D4 was thought to be the hardest case.

## What this actually falsifies, stated precisely

The claim was: *nobody derives legitimacy predicates from an ownership/consent model;
everyone hand-authors policy, so the derivation path is the contribution.*

Both engineers derived them. More pointedly, they reached the **two principles the
project treated as its own**, unprompted:

- **custody ≠ authority.** Rego: *"the central GDPR error in this model — assuming the
  custodian is the source of authority over personal data. It is not."*
- **a grant is a claim, not a fact.** Rego: *"`valid_grant` re-derives the issuer's
  standing every time, so an agent with write access to IAM still cannot escalate."*
  Cedar `F5`: *"Nobody bootstraps their own authority."*

These are not incidental. They are the ownership-derivation insight, produced by a
competent policy engineer from a data model in a single sitting.

**Therefore: the surviving novelty claim is dead.** The honest description of what this
project's legitimacy layer does is *"automating constraints a good policy engineer
writes by hand"* — real, useful, and not novel.

## The caveat, and why it is not an escape hatch

Pre-registered before the result was seen (see the session record): **I chose the entity
model, and three of its fields are themselves ontology-derived** — `resource.owner` as
the *data subject* rather than the holder, `consent.revoked`, and
`exportable_beyond_recall`. Both baselines leaned on precisely those three fields.

So the experiment shows: *given ownership-shaped data, the derivation is natural.* It
does not show whether a real Cedar or OPA deployment would have that data model in the
first place — and experience says most treat the organisation as owner.

That is a genuinely open question, and it is **not** being pursued. Turning "the claim
died, but here is a new claim one level down" into the next experiment is exactly the
loop this protocol was written to stop. It is recorded here and left.

## Standing of the theory itself

Unchanged, and this experiment says nothing about it. What died is an *implementation*
claim — that a distinctive authorization architecture follows from the theory. Whether
freedom can be formalised as a calculus over rights, ownership, consent and
non-domination remains undetermined, exactly as it was yesterday. An architectural
result was never going to settle a philosophical one.

## Method note

The baselines were briefed with `BASELINE_BRIEF.md` — the domain and the entity model,
no cases, no expected verdicts, no statement of what was being measured. `FROZEN_CASES.md`
was committed at `1090789` before either brief was issued, so ground truth could not be
adjusted after the fact. Sample size is two, and both authors share a model family;
their agreement is therefore weaker evidence than two unrelated human engineers would be.
That limitation cuts *against* the claim's survival either way, since both denied.
