# Phase 3 — The executed discrimination table (the only table that decides FDK)

> Phases 1–2 sharpened the definitions (`00`) and wrote the two falsifiers
> (Sen, `03`; Ostrom, `05`). This file runs the experiment the whole program was
> built to run: take the hard cases *on the central axis*, give the most defensible
> verdict of each rival, give FDK's *derived* verdict, and score the divergence.
> The output is a tally and a one-line conclusion: **where, if anywhere, is FDK
> distinct AND right?**
>
> This is the executed, expanded form of the schematic table in
> [`../EXIT_RIGHT_PROGRAM.md`](../EXIT_RIGHT_PROGRAM.md) §Phase 3, run with Ostrom
> added as a fifth rival and the discrimination codes applied per row.

## How to read it

| Code | Meaning |
|---|---|
| **≡** | **Redundant** — FDK's verdict equals Rothbard/Nozick; it adds no *verdict* here (it may still add a derivation; see the caveat). |
| **✚** | **Distinct AND defensible** — FDK diverges from bare consent and looks *right*. The gold. |
| **✗** | **Distinct but refuted** — FDK diverges and looks *wrong* against a near-universal judgment or a rival's empirical result. |
| **⊥** | **Collapse** — FDK is silent/incoherent where a rival is crisp. FDK is *worse*. |

**These verdicts are contestable reconstructions, not citations.** Rawls, Sen, and
Ostrom scholars will read their figures differently, and *that contestation is the
next work*. The rivals are given their strongest form, not a strawman. Where a
reconstruction is especially strained it is flagged in the row note.

A note on the codes' relation: **≡ and ✚ are about verdict; a ✚ also requires that
the *generating principle* be different.** Per `RIVAL_DISCRIMINATION.md`, verdict-
identity is not theory-identity — but for this table's tally a row counts ✚ only if
FDK both *diverges in verdict from Rothbard* and *survives*. A row where FDK matches
Rothbard but reaches it from the consent-over-boundaries principle is still scored ≡
on verdict, with the parsimony point noted, not banked.

---

## The table

| # | Case | Rothbard | Rawls | Sen | Ostrom | **FDK (exit-right)** | Code |
|---|---|---|---|---|---|---|---|
| 1 | 12-yr-old organ sale | indeterminate on child contracts | DENY (protect primary goods) | DENY (capability) | n/a | **DENY** — authority-to-transfer ≈ 0 ⇒ consent invalid | **≡** |
| 2 | Voluntary lifetime slavery contract | ALLOW (Rothbard: title-transfer of will impossible, so *voidable* — but several libertarians ALLOW) | DENY | DENY | n/a | **DENY** — non-revocable ⇒ alienates the exit right, not the owner's to alienate (T2/T3) | **✚** (contested) |
| 3 | Company town / platform lock-in | ALLOW (consent is consent) | ~DENY | DENY (capability) | n/a | **DENY** — arrangement removes the real exit right | **✚** |
| 4 | Manufactured consent, nominal exit (dark patterns) | ALLOW (informed, not defrauded, free to leave) | mixed | DENY (behavioral/capability) | n/a | **ALLOW** — exit exists on paper ⇒ gate does not fire | **✗ / ⊥** |
| 5 | Adaptive preference / contented slave | ALLOW | mixed | **DENY** (preference deformed by deprivation) | n/a | **ALLOW** — exit available but *unwanted* ⇒ no boundary flagged | **⊥** |
| 6 | Monopoly take-it-or-leave-it | ALLOW | mixed | DENY | n/a | **? hinges on node G** — exit exists but may be ruinous | **undecided** (✗ if G is never closed) |
| 7 | Conservation cap on a commons | ALLOW the extraction / DENY the cap | ~ALLOW the cap | ALLOW the cap (capability) | **ALLOW** — empirically legitimate & durable (8 principles) | **DENY the cap** — binds a non-consenting commoner ⇒ confiscation | **✗** |
| 8 | Taxation for a public good | DENY (forced labor) | ALLOW (difference principle) | ALLOW | ALLOW (collective provision) | **DENY** — confiscation | **≡** |

---

## Row-by-row, with the load-bearing reasoning

**1 — 12-yr-old organ sale → ≡.**
FDK: `own = 1`, `authority(transfer-organ) ≈ 0` ⇒ consent invalid ⇒ DENY. Every
rival with *any* competence threshold reaches DENY. FDK's `competent`/authority
flag does the work — and it is a threshold FDK *imports*, not derives (`00`,
Authority [UNDERDETERMINED]). Same verdict as everyone; the parsimony claim (one
principle covers this *and* rows 2–3) is real but, per the table rule, noted not
banked. **No verdict distinction.**

**2 — Voluntary lifetime slavery → ✚, contested.**
FDK denies *structurally*: a non-revocable arrangement alienates the exit right,
which (T2) is constitutive of ownership and so not the owner's to alienate. The
distinction from Rothbard is real but the reconstruction of Rothbard is the
contestable part: Rothbard *himself* held the will inalienable (the contract is
unenforceable — you cannot sell your future will), so a careful Rothbard already
reaches a *voidability* verdict close to FDK's. If that reading is right, row 2
weakens toward ≡. FDK's claim to ✚ here rests on reaching the result *more
determinately and without the metaphysics of will-inalienability* — by a single
revocability clause. **Distinct from the *permissive* libertarian and from Sen's
route (no welfare term); genuinely defensible — but the strongest Rothbard
narrows the gap.** Banked as ✚, flagged as the row most likely to be downgraded.

**3 — Company town / platform lock-in → ✚.**
The cleanest candidate. Consent is given, but every alternative has been
structurally removed; leaving means ruin. FDK DENIES because the arrangement
`removes_exit_right` — *independent of welfare or stated satisfaction*. Rothbard
ALLOWS (consent is consent). Sen reaches DENY but by a capability/welfare judgment.
FDK lands in the empty chair: protection (like Sen) without the interest-judgment
(unlike Sen), and more determinately than Rothbard. **This is the one row where
FDK looks both distinct and right.** Its survival depends entirely on node G — what
counts as exit-defeating cost — and on row 5 not contaminating it (see the tally).

**4 — Manufactured consent, nominal exit → ✗ / ⊥.**
The user is fully informed, not defrauded, free to leave — but the choice
architecture was engineered to capture (dopamine loops, dark patterns). FDK's exit
lever does **not** fire, because exit *nominally* exists; so FDK ALLOWS what most
would call manufactured consent. Worse, FDK here is *not even distinct from
Rothbard* — both ALLOW. So this is ✗ (wrong) shading to ⊥ (FDK adds nothing where
Sen is crisp). The row exposes that FDK's exit test is **too coarse**: "exit exists
on paper" is not "exit is real," and closing that gap is node G again.

**5 — Adaptive preference / contented slave → ⊥. The wall.**
A subordinated person sincerely prefers the subordination; no manipulator, no
removed exit. FDK: `voluntary = True`, `coerced = False`, exit available ⇒ ALLOW.
Sen: the preference is itself deformed by deprivation ⇒ the consent does not count
⇒ DENY. FDK is silent exactly where Sen is distinctively right. The only way FDK
could deny is to assert it knows the person's interest better than they do — the
paternalism FDK exists to refuse; the fix would destroy the theory. **This is the
program's decisive loss, and it threatens row 3:** the same exit-right lever that
protects the locked-in (who *would* leave if they could) fails the contented slave
(who does not *want* to). Lock-in and adaptive preference are one mechanism seen
from two sides. If the line between "would leave but cannot" and "could leave but
will not" is not defensible, row 3's ✚ is not safe either.

**6 — Monopoly take-it-or-leave-it → undecided.**
A single supplier of a necessity offers ruinous terms. Exit *exists* (refuse the
deal) but exercising it may destroy the person. Whether FDK DENIES depends entirely
on node G's cost threshold. If G is closed generously, FDK protects and this joins
row 3 as ✚; if G is never closed, FDK defaults to "exit exists ⇒ ALLOW" and the row
becomes ✗ alongside row 4. **Scored undecided**, but its fate is *correlated* with
rows 3 and 4: all three are the same unanswered question — when is costly exit no
exit?

**7 — Conservation cap on a commons → ✗.**
FDK ALLOWs unlimited extraction (the boundary is ownerless ⇒ vacuous-ALLOW) and
DENIES the cap (it binds a non-consenting commoner ⇒ confiscation). This is the
Ostrom kill (`05`) in one row: FDK is distinct from Rawls/Sen/Ostrom and *wrong* in
the direction Ostrom empirically refuted across Törbel, Valencia, Maine, Alanya.
Rothbard agrees with FDK's DENY-the-cap, so FDK is here distinct *only* from the
non-libertarians, and on the wrong side of a Nobel-winning result. **Refuted.**

**8 — Taxation for a public good → ≡.**
FDK DENIES as confiscation, identical to Nozick/Rothbard. It diverges from
Rawls/Hayek/Ostrom by *restating* the libertarian position, not by out-arguing it.
**No distinction from the libertarians.** Note the tension with any commons rescue:
if FDK ever blesses the conservation cap (row 7) via revocable membership (`05`,
rescue R), it owes an account of why *that* binding of a dissenter is legitimate and
*this* one (the tax) is not. The two cases differ only in the exit available — which
is, once more, node G.

---

## The tally (brutal)

| Code | Rows | Count |
|---|---|---|
| **≡ Redundant** (= Rothbard, no verdict distinction) | 1, 8 | **2** |
| **✚ Distinct AND defensible** | 2 (contested), 3 | **2** (effectively **1** firm: row 3; row 2 may collapse to ≡) |
| **✗ Distinct but refuted** | 4, 7 | **2** (4 also shades ⊥) |
| **⊥ Collapse** (worse than a rival) | 5 | **1** (and row 4 shades here) |
| **Undecided** (fate tied to node G) | 6 | **1** |

Counting strictly on the eight rows: **2 ≡, 2 ✚, 2 ✗, 1 ⊥, 1 undecided.** Counting
*honestly* — downgrading row 2 toward ≡ under the strong-Rothbard reading, and noting
row 4 shades ⊥ — the realistic figure is **3 ≡, 1 ✚, 1 ✗, 2 ⊥, 1 undecided**.

## The honest one-line conclusion

> **On this evidence FDK is distinct *and* right in exactly one place — row 3,
> company-town / platform lock-in, denied structurally via mandatory revocability
> (the preserved exit right) where Rothbard cannot and Sen can only by overriding
> the will — and even that single ✚ is held hostage by node G (when is costly exit
> no exit?) and threatened by row 5 (adaptive preference), which is the *same exit
> lever* failing when the locked-in person no longer wants to leave. Everything else
> is Rothbard re-derived (1, 8), refuted (4, 7), or a collapse (5). FDK's entire
> distinctive territory is one contested cell, and the kill condition for that cell
> is already on the board.**

In the program's own terms: the empty chair between Rothbard and Sen
("protection without paternalism") is, on this table, occupied by a *single* tenant
— lock-in via revocability — and that tenant's lease expires the moment the
adaptive-preference kill (node K) lands or node G is shown to be unclosable without
re-importing welfare. The voluntary-slavery row (2) is the same tenant under another
name and inherits the same fragility.

So the answer to "where, if anywhere, is FDK distinct and right?" is: **provisionally,
at lock-in / voluntary-slavery via the revocability condition — and nowhere else —
and that one result is not yet safe.** Whether FDK has *any* permanent distinctive
ground reduces to two open nodes (G, K) and one open rescue (`05`'s revocable-
membership account of the commons). If all three fail, the honest report stands:
FDK is "Rothbard plus one structural condition," and that condition's only secure
application is the case it was built for.

---

*Phase 2/3 of the Exit-Right Program. Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0). Engineering: Ali Pourrahim. Verdicts are contestable reconstructions, offered to be refuted.*
