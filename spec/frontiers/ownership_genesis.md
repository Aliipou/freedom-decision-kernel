# Ownership Genesis — where does the FIRST ownership come from?

> Research notes — open problem, not a solution. A hostile audit of FDK's deepest
> assumption: that the `OwnershipGraph` it is handed is *legitimate*. FDK validates every
> **transfer** of title and audits **no origin**. So a graph whose root is conquest, theft,
> or mere assertion produces an unbroken chain of "legitimate" verdicts atop an illegitimate
> foundation. This is the bootstrapping gap (`FOUNDATIONAL_ATTACKS.md`) taken to its root.

## The problem, stated structurally

`Legitimate(a) ⟺ ∀ boundary b crossed: ∃ valid_consent(owner(b), a)`. The predicate ranges
over `owner(b)` as a *given*. It can verify that B's title came from A by consent, and A's
from a prior holder — but the recursion bottoms out at a *first* owner whose claim no
consent grounds. FDK has **no original-acquisition rule**. The graph floats.

## A catalogue of real cases FDK launders or cannot represent

1. **The Norman Conquest (1066).** Nearly all English freehold title traces to a violent
   seizure. FDK protects today's holder exactly as a clean one.
2. **Indigenous dispossession** — *Johnson v. M'Intosh* (1823, "discovery doctrine"),
   *Mabo* (1992, overturning *terra nullius*). The graph FDK reads *is* the settler graph.
3. **The land under Helsinki** (the director's case): does it matter if taken 300, 800, or
   2000 years ago? FDK has no answer because it has no clock and no root.
4. **Post-communist privatization** (1990s vouchers, oligarch capture): a one-time
   conversion of "no one owns it / everyone owns it" into private title with no consenting
   prior owner — pure genesis, and FDK cannot say if it was legitimate.
5. **German reunification property claims** (restitution vs. *Bodenreform* takings).
6. **Slavery reparations / Black land loss** (US): title built on stolen labor and
   subsequent fraudulent dispossession; FDK sees only the current clean-looking transfers.
7. **Adverse possession / squatters' rights**: the law *manufactures* title from
   wrongful possession plus time — a rule FDK cannot represent (it has no statute of
   limitations) yet every property system needs.
8. **The Homestead Acts**: original acquisition by labor-mixing on land *taken* from
   natives — Locke's proviso and the dispossession collide in one statute.
9. **Nazi-looted art** restitution: provenance gaps of decades; "good-faith purchaser"
   doctrines vs. the original theft.
10. **Enclosure of the commons**: FDK can encode the post-enclosure freehold but **not**
    the commoner's prior use-right, so it cannot even *describe* the harm of enclosure —
    structurally "the theory of the enclosers" (see `aggregation.md`).
11. **Water rights** (prior appropriation vs. riparian): first-in-time is itself an
    acquisition *rule* FDK would have to justify, not assume.
12. **Mineral / subsurface / airspace / orbital-slot / spectrum** rights: pure conventional
    genesis with no natural owner.
13. **Intellectual property**: a state-granted monopoly over others' actions — is its
    *origin* an acquisition or a grant? FDK has no category for it.
14. **Sovereign borders**: every state's territorial title traces to conquest or treaty
    signed under duress.
15. **Bitcoin genesis block / first miners**: even the cleanest modern ledger has an
    ungrounded first allocation.

## Where FDK is wrong (not merely silent)

- It does not *abstain* on contested origins — it returns a confident **ALLOW** for the
  current holder and **DENY** for the dispossessed heir's reclaim (reproduced in
  `examples/foundational_attacks.py`). It actively takes the side of possession.
- It presents these verdicts as *definitive* while they rest on an unaudited graph — a
  false precision more dangerous than honest silence.

## Literature it must answer

- **Locke's proviso** ("enough, and as good, left in common"): fails the moment scarcity
  binds — and it always eventually binds — so original appropriation is *never* clean by
  Locke's own test.
- **Nozick's principle of rectification**: Nozick *admitted he could not specify it* and
  floated random redistribution as a rough proxy — an extraordinary concession from FDK's
  nearest kin.
- **Kant**: provisional vs. conclusive property — title is only conclusive under a civil
  condition, i.e. ownership presupposes the very institutions FDK's consent-only frame omits.
- **Hume**: property is convention, justified by stability not by a first act — a direct
  challenge to genesis-by-acquisition.

## The candidate fatal finding (possibly irreducible — and shared)

**There may be no non-arbitrary original-acquisition rule at all.** Labor-mixing
(why does mixing labor grant the *whole*, not just the added value? — Nozick's tomato-juice
objection), first-occupancy (why does being first bind everyone after?), and any
statute-of-limitations cutoff (why 300 years and not 800?) are each arbitrary. If so,
"legitimate title at the root" is **undefinable**, and FDK's entire graph is parasitic on a
baseline it cannot justify — its verdicts are valid *relative to* an input it has no way to
certify.

The honest twist: **this is not unique to FDK.** It is the oldest open problem in property
theory, and Locke, Nozick, and Rothbard all break on it too. But FDK's *silence* makes it
worse, not better: by presenting ALLOW/DENY as definitive it hides the dependency. The
minimum honest fix is not a solution but a **disclosure** — already started in
`ownership_graph.py` (a `FORCED_ORIGIN` title is flagged `DO_NOT_RELY`). Whether a
*positive* origin rule exists is the open question, and the live possibility is **no**.

*Research notes. Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust
(CC BY 4.0). Engineering: Ali Pourrahim.*
