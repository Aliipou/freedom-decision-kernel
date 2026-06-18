# Phase 1 — Definitions sharp enough that two readers cannot diverge

> The test for this file: hand any definition below to two honest readers, give
> them a contested case, and they must reach the **same** verdict. Where they
> can't, the definition is flagged **[UNDERDETERMINED]** — those flags are the
> real work, not failures to hide. Definitions are stated as *necessary +
> sufficient* conditions, each with the counterexample that would break it.

## The core terms

### Person
**Def.** An entity that owns itself: the unique locus of a will that can hold
rights and give or withhold consent.
- *Necessary:* a standing capacity (even if dormant — sleep, anaesthesia) to form
  a will about boundary crossings on itself.
- *Sufficient:* nothing weaker; mere interests (an animal's pain) do **not** confer
  personhood on this definition — that is a deliberate, contestable narrowing.
- **[UNDERDETERMINED]** the *threshold* of "capacity to form a will": fetus, the
  permanently comatose, advanced dementia, a future AI. This is the Standing
  frontier; the exit-right program does **not** resolve it and must not pretend to.

### Ownership
**Def.** A **binary** relation: `owns(person, thing)` holds or it does not. Title
is not graded (the settled ruling — "40% ownership" is the abuse lever).
- *Necessary:* a legitimate origin (self-ownership, voluntary transfer, or original
  acquisition) — and origin legitimacy is itself **[UNDERDETERMINED]** (the
  Ownership-Genesis hole, off this axis).
- *Sufficient:* an unbroken consent-grounded chain from a legitimate origin.
- **Counterexample that would break it:** any case where we want to say someone
  "partly owns" a thing in a way that is *not* re-describable as full ownership +
  graded **authority**. If such a case exists, binary ownership is wrong.

### Authority
**Def.** The **graded** capacity to *exercise* a right one owns — to act on, alienate,
or contract over the owned thing. `Authority ∈ [0,1]`, and is act-relative.
- *Key separation:* **Ownership ≠ Authority.** A child fully *owns* its body
  (ownership = 1) but has near-zero *authority* to transfer organs (authority ≈ 0).
- *Sufficient for an act A:* `Authority(person, A) ≥ Threshold(A)`, where the
  threshold rises with stakes/irreversibility.
- **[UNDERDETERMINED]** who measures Authority, and on what scale — the paternalism
  risk lives here (see `03_how_sen_kills_fdk.md`).

### Consent
**Def.** An **attestation by a rights-holder authorising a specific boundary
crossing**, valid only if it is informed, specific, competent, voluntary, *and
revocable*.
- *Necessary (the load-bearing clause):* **revocability** — a consent that cannot
  be withdrawn alienates the exit right, which is not the owner's to alienate.
- *Sufficient:* all clauses hold *and* authority is sufficient for the act.
- **Counterexample probe:** sincere consent to a non-revocable arrangement (the
  voluntary slave). FDK says invalid (no revocability); the test is whether that is
  defensible without paternalism. See `03_how_sen_kills_fdk.md`.

### Exit / revocation right
**Def.** The standing, *exercisable* ability to withdraw from an arrangement and
end future obligation, **at a cost that does not itself destroy the person**.
- *Necessary:* the withdrawal is available in fact, not only on paper.
- **[UNDERDETERMINED — the program's central technical gap, node G]** the
  **cost threshold**: how costly may exit be before "available" is a fiction
  (ruin, statelessness, starvation)? Any answer risks re-importing welfare. Until
  this is pinned, every downstream theorem about lock-in is *schematic*.

### Legitimacy
**Def.** A property of an *action*: legitimate iff every boundary it crosses has the
valid consent of that boundary's owner. Three-valued in practice: ALLOW / DENY /
DEFER.
- *Separation:* **Legitimacy ≠ Legality.** A legal act (chattel slavery under 1850
  law) can be illegitimate; an illegal act (escaping it) can be legitimate.
- *Separation:* **Legitimacy ≠ Welfare.** An action that raises aggregate welfare
  by crossing a non-consenting boundary is illegitimate. (This is FDK's whole
  anti-utilitarian spine.)

### Freedom
**Def.** The state of having one's boundaries crossed *only* by one's own valid
consent. **Not** the satisfaction of preferences; **not** happiness; **not** the
range of options (a content slave with no options can be unfree though satisfied;
a poor person with few options is not thereby unfree if no one crosses their
boundary without consent).
- *Separations:* `Freedom ≠ Welfare`, `Freedom ≠ Happiness`, `Freedom ≠ Capability`.
- **[UNDERDETERMINED]** whether *option-poverty produced by others' prior
  legitimate acts* (structural monopoly) counts as a boundary crossing. This is
  exactly where Sen attacks (`03_how_sen_kills_fdk.md`).

### Responsibility
**Def.** The **graded** liability for the consequences of one's acts, tracking
authority: one is responsible for an act to the degree one had the authority
(competence) to do otherwise.
- *Separation:* responsibility grades with authority, not with ownership — a child
  owns its acts but bears reduced responsibility for them.

## The concept-separation table (collapse any one → the theory explodes)

| Must stay distinct | Collapsing them causes |
|---|---|
| Ownership ≠ Authority | "the incompetent don't own themselves" → strip the vulnerable |
| Consent ≠ Preference | "they're satisfied, so it's fine" → the contented slave passes |
| Authenticity ≠ Sincerity | "she sincerely agreed" → manufactured consent passes |
| Legitimacy ≠ Legality | the theory becomes positivism (whatever the law says) |
| Freedom ≠ Welfare | utilitarian override returns; FDK loses its identity |
| Exit-right ≠ Exit-taken | "she stayed, so she consented" → lock-in passes |

## The hard cases this file must survive (stress test of the definitions)

For each, the definitions above must yield a *determinate* reading or be honestly
flagged. (Verdicts here are the kernel's; their defensibility is Phases 2–3.)

| Case | Reading under these definitions | Determinate? |
|---|---|---|
| 12-year-old organ sale | own=1, authority≈0 ⇒ consent invalid ⇒ DENY | yes |
| Comatose patient | own=1, authority=0, no current will ⇒ others act only as defeasible guardians | partial — guardian scope [UNDERDETERMINED] |
| Advanced dementia | own=1, authority lapsing ⇒ prior-self directives + guardian | partial |
| Animal | not a person (no self-ownership) ⇒ outside the gate ⇒ owner may harm | yes, and **morally contested** (Phase 2/Singer) |
| Future AI | personhood threshold [UNDERDETERMINED] | **no — open** |
| Fetus | personhood threshold [UNDERDETERMINED] | **no — open** |
| Voluntary lifetime slave | consent non-revocable ⇒ invalid ⇒ DENY | yes — but the *kill case* (Phase 3) |
| Addiction | consent's voluntariness/authenticity degraded ⇒ ? | partial — hinges on node G |
| Brainwashing / cult | authenticity (not sincerity) absent ⇒ DENY *if* engineered foreclosure shown | partial — evidentiary |

**The honest output of Phase 1:** the definitions are determinate on the *capacity*
cases (child, dementia) and the *structural-foreclosure* cases (lifetime slavery,
lock-in), and **genuinely open** on personhood-threshold cases (fetus, AI, animals)
and on the **exit-cost threshold (node G)**. The program's distinctive claims all
sit on the determinate cases; its survival sits on node G and the adaptive-preference
kill (node K). Everything that follows is built only on the determinate ground.

*Phase 1 of the Exit-Right Program. See [`../EXIT_RIGHT_PROGRAM.md`](../EXIT_RIGHT_PROGRAM.md).*
