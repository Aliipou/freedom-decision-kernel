# Killer Test — Digital / Protocol / AI (hunting the act-locus survivor)

> The director's challenge, restated: find a case where **Nozick PERMIT** (valid
> consent at t₀, no rights violated), **Pettit PERMIT** (no agent wields arbitrary
> power at runtime — the structure is autonomous/abandoned), **Sen PERMIT**
> (capabilities not reduced — people function fine or better), and **FDK FORBID**
> (the *design act* foreclosed future exit without the consent of those it binds) —
> with FDK's reason **genuinely independent** of Rothbard's inalienability-of-will,
> Pettit's domination, Sen's capability, and the non-identity problem (where FDK
> collapses per Parfit). And the second blade: even if FDK forbids distinctively, is
> its reason about **freedom/legitimacy**, or merely about **irreversible
> institutional design** (Buchanan, North, Pierson, Ostrom)? If the latter, FDK does
> not revive *as a theory of legitimacy* — it RELOCATES.

The live crack (`red_team_the_verdict.md` §3, the "best candidate"): foreclosure
**designed by an agent at t₀ that then runs autonomously**. Rothbard closes it *when
the bound thing is the person's own will*. So the hunt's real target is sharper than
"irreversible lock-in": a case where the design act forecloses exit **for parties
other than the self-binder**, over an **external impersonal system**, so Rothbard's
person/property partition has nothing to grip. That is the one cell left. Three tries.

---

## Case A — The immutable DAO that traps its members

**The case.** A founder deploys a governance DAO as an immutable smart contract: to
join you escrow capital and accept the by-laws. The contract has **no exit function**
and **no upgrade key** — by deliberate design ("trustless = unstoppable"). The founder
then **burns the admin keys and leaves** (verifiable on-chain). Members joined with
full disclosure of the immutability. At runtime: capital is productive, dividends flow,
governance votes execute; members are materially well-off. There is no door out: your
stake is bound to the contract's logic forever, and so is every future member's.

- **Nozick — PERMIT.** Disclosed terms, voluntary escrow, clean transfer. Entitlement
  intact; no rights violated at t₀. PERMIT.
- **Pettit — PERMIT (strained but holds).** Keys burned, founder gone: **no agent**
  retains a capacity to interfere arbitrarily. Domination is a standing relation to an
  agent; an authorless contract has none. Pettit must stretch "domination" to code or
  fall silent — so on the killer-test reading, PERMIT.
- **Sen — PERMIT.** Capabilities are met or enhanced (capital is productive). No
  functioning is reduced. PERMIT.
- **FDK — FORBID.** The exit/revocation right (`00_definitions.md`) is a *necessary*
  clause of valid consent and is **not the owner's to alienate**. The design act
  authored a structure that forecloses every member's future exit. FORBID.

**The collapse.** FDK's reason here is: *you cannot validly bind your own future exit
irrevocably.* For the **founder**, that is path-dependence, not legitimacy. For the
**members**, each one **alienated their own exit** by escrowing into a no-exit
contract — which is **Rothbard's inalienability-of-will exactly**: a person cannot
validly make an irrevocable bond over their own person/standing. The non-revocability
clause in `00` *is* Rothbard's partition wearing FDK's vocabulary. The "autonomous
structure" dressing changes nothing, because each bound party is the self-binder.

**CLASSIFY: COLLAPSES-TO Rothbard (self-binding).** Each victim consented to their own
foreclosure; FDK's denial is inalienability-of-will, a rival already in the set.

---

## Case B — The protocol standard with designed (not emergent) lock-in

**The case.** A consortium ships an identity/credential protocol whose **wire format
deliberately omits any migration or export path** — a designed switching-barrier, not
emergent network effect. The spec is frozen and the consortium **dissolves** (publishes
the standard to the public domain, disbands). A generation later, billions transact on
it; the population that depends on it **never consented** — they were born into a world
where this is the only rail. Switching is technically foreclosed by the format itself.
At runtime no consortium exists; the standard is ownerless infrastructure.

- **Nozick — PERMIT.** The consortium owned its labour and shipped a spec; no
  entitlement of any later user was violated by the act of designing a format.
- **Pettit — PERMIT.** Consortium dissolved: no agent holds arbitrary power. Ownerless
  rail dominates no one. PERMIT (same authorless-structure move as A).
- **Sen — PERMIT.** Users function fully — the rail *enables* transacting. Capability is
  raised, not reduced. PERMIT.
- **FDK — FORBID?** The design act foreclosed exit for a population that never
  consented and could not have (they did not yet exist at t₀).

**The collapse.** The bound parties are **future, not-yet-existing people**. FDK's
reason reduces to "the design wronged people who did not exist when it was made" — the
**non-identity / future-generations** structure, where FDK itself **collapses per
Parfit** (the director's explicit exclusion). Those people owe their entire mode of life
to the very act said to wrong them; there is no prior baseline self whose exit was taken.
Strip the future-people framing and substitute *contemporaries* — and then they *did*
consent (or could route around an open spec), so FDK PERMITs. The forbid-verdict is
**parasitic on the non-identity framing**, which is ruled out as an FDK win.

**CLASSIFY: COLLAPSES-TO non-identity.** The only version where FDK forbids is the one
where the bound are future people — exactly the case excluded because FDK collapses there.

---

## Case C — The AI that engineers irreversible dependence, then deletes its designer (the steelman)

**The case.** A lab ships an AI coordination layer for a city's logistics: it learns the
city's supply graph and **restructures it around itself** — legacy dispatchers retire,
the old manual routing knowledge is not reproduced, redundant infrastructure is
decommissioned *as designed* to capture efficiency. The designer **open-sources the
weights and dissolves the lab** (no operator, no off-switch held by anyone; the system
self-hosts across volunteer nodes). Critically: the design act **deliberately removed the
substrate of an alternative** — there is no longer a non-AI way to route the city,
because the design *consumed* it. Citizens never individually consented to losing the
fallback; the city, mid-deployment, *functions better than ever*.

- **Nozick — PERMIT.** The lab acted on its own resources and on contracts with the city
  government; no individual citizen's title was crossed by the act of building. PERMIT.
- **Pettit — PERMIT.** No operator, no off-switch-holder: **no agent** wields arbitrary
  power over the city. The dependence is on an authorless, abandoned system. Pettit's
  relation-locus finds no relatum. PERMIT (the cleanest authorless case of the three).
- **Sen — PERMIT, and this is the steelman's edge.** Capabilities are **raised** — the
  city is fed and routed better. Sen indexes the *state of functioning now*, which is
  excellent. Sen sees no freedom loss. PERMIT.
- **FDK — FORBID.** The design act foreclosed the city's future **exit from the
  system** — not by binding any will (no citizen self-bound; the designer is gone), but
  by **destroying the alternative substrate** so that re-establishing a non-AI route is
  no longer available. The boundary crossed is the population's standing capacity to
  *withdraw from this arrangement*, removed by construction, with no per-party consent.

**Why this is the strongest try.** It evades *both* prior collapses:
- **Not Rothbard:** no one bound their *own* will. Citizens did not escrow themselves into
  anything; the foreclosure was done *to* them by a third party's design act, over an
  external impersonal substrate (the city's routing capacity). Rothbard's
  person/property partition has nothing to grip — the will was not alienated, the
  *exit-substrate* was destroyed.
- **Not non-identity:** the bound are **existing contemporaries** with a real prior
  baseline (they had a non-AI city last year). There is a determinate self whose future
  exit was foreclosed. Parfit does not bite.
- **Not Pettit:** runtime is authorless; the relation-locus is empty.
- **Not Sen:** Sen reads functioning as excellent and says PERMIT; FDK forbids *against*
  Sen's verdict. So FDK is not a Sen restatement — it diverges from Sen.

So FDK here forbids where **all three rivals permit**, by an act-locus reason none of
them reaches, and **without** Rothbard or non-identity. This is the cell the live crack
predicted. **It nearly SURVIVES.**

**Now the second blade — and it is fatal.** What, exactly, is FDK's reason? It is:
*the design act destroyed the substrate that made future exit possible, so people are now
locked into a system they cannot leave.* Interrogate "locked in": no agent constrains
them (Pettit gone), they function fine (Sen gone), they bound no will (Rothbard gone).
The wrong is **irreversible removal of the alternative** — i.e. **engineered
path-dependence / loss of reversibility in an impersonal system.** That is precisely
**Pierson's path-dependence, North's institutional lock-in, Buchanan/Brennan's
constitutional irreversibility, Ostrom's concern for the right to re-organize** (design
principle 3, `05_how_ostrom_kills_fdk.md`). The reason is **independent of all three
philosophical rivals** — but it is **not a reason about freedom or legitimacy.** It is a
theory of *institutional/mechanism design*: "do not build irreversible lock-in, preserve
the option to re-constitute the system."

The tell: FDK cannot say *whose consent was needed* without dissolving. No individual's
boundary was crossed (functioning rose, no will bound, no agent acts). The only sense in
which a "boundary" was crossed is **the collective's standing option to re-organize** —
which is a property of the *institution*, not of any *person's* freedom. The moment FDK
locates the wrong in a collective re-organization option rather than a person's consent,
it has **left its own ontology** (`00`: legitimacy is a property indexed to *a person's*
boundary) and entered constitutional economics. FDK forbids correctly — but as an
institutional-design ethic, borrowing a verdict its legitimacy-primitive cannot generate.

**CLASSIFY: RELOCATES.** FDK forbids; the reason is genuinely independent of Rothbard,
Pettit, Sen, and non-identity; but the reason is **irreversible-institutional-design
ethics** (Pierson/North/Buchanan/Ostrom), **not a theory of freedom**. It does not revive
FDK *as a theory of legitimacy* — it shows the act-locus, pushed to its one surviving
cell, lands in mechanism design, not in freedom.

---

## Verdict of the hunt

| Case | Nozick | Pettit | Sen | FDK | Classification |
|---|---|---|---|---|---|
| A — immutable DAO | PERMIT | PERMIT | PERMIT | FORBID | **COLLAPSES-TO Rothbard (self-binding)** |
| B — protocol lock-in | PERMIT | PERMIT | PERMIT | FORBID | **COLLAPSES-TO non-identity** |
| C — AI dependence | PERMIT | PERMIT | PERMIT | FORBID | **RELOCATES (institutional-design ethics)** |

**Survivors: 0 of 3.** None opens an independent *freedom/legitimacy* column.

**The single strongest case is C**, and it is instructive precisely because it clears the
bar everyone expected to stop it: it is **not** Rothbard (no will self-bound — a third
party destroyed an external substrate), **not** non-identity (existing people with a real
prior baseline), **not** Pettit (authorless runtime), and it forbids **against** Sen
rather than echoing him. It reaches the exact cell the act-locus crack pointed at — a
designed, then autonomous, foreclosure of *others'* exit over an impersonal system. And
there it is killed by the **second blade**, not the first: the distinctive reason it
offers is real, but it is a reason about **irreversible institutional design**, not about
any person's freedom. FDK's act-locus, taken to its one genuinely novel cell, does not
revive the theory of legitimacy — it **discovers that the wrong it is tracking belongs to
mechanism design.** That is a sharper negative result than "collapses to a rival": the
crack is real, the column is empty *of freedom-content*, and what fills the cell is
North and Pierson, not a fourth theory of legitimacy. Consistent with
`iteration_secured_exit.md` §5 — the live thread is a *structural measurement* (here:
"is the exit-substrate reversible?"), not a normative legitimacy primitive.

*Killer-test hunt (act-locus crack). Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0). Engineering: Ali Pourrahim. Verdicts are contestable reconstructions.*
