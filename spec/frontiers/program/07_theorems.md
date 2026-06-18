# Phase 4 — The theorem ledger for the consent / exit axis

> Phases 1–3 fixed the terms and ran the rivals. This file stops writing prose and
> states the axis as axioms and theorems, each with an explicit derivation that
> cites the axioms it uses. Every verdict the program issues must trace back to a
> line here. Where a derivation does **not** close, it is flagged — a theorem
> ledger that hides its open lemmas is dishonest.
>
> Scope note. The kernel's own safety properties (slavery, sovereignty, defensive
> asymmetry) are ledgered separately in [`../../THEOREMS.md`](../../THEOREMS.md)
> and numbered T1–T9 there. **That numbering is unrelated to this file.** Here T1–T7
> are the *philosophical* theorems of the exit-right axis, in the sense of
> [`../EXIT_RIGHT_PROGRAM.md`](../EXIT_RIGHT_PROGRAM.md) Phase 4 — claims meant to
> be proved or broken, not executable tests.

---

## 0. Primitives and notation

Carried verbatim in meaning from [`00_definitions.md`](00_definitions.md); only the
symbols are introduced here.

```text
Person(p)              p is a self-owning locus of will (00_definitions §Person).
Boundary(b)            a surface around an owned thing that may not be crossed
                       without consent.
owns(p, b)             BINARY (settled ruling): p is the owner of boundary b.
                       Either holds or does not; never graded.
crosses(a, b)          action a crosses boundary b.
owner(b)               the unique p with owns(p, b)  (well-defined by binarity).
Act(a)                 a is an action (a transfer, an arrangement, a crossing).

Consent(c, p, a)       c is an attestation by p authorising action a.
informed(c) specific(c) competent(c) voluntary(c) revocable(c)
                       the five clauses of consent (00_definitions §Consent).
valid(c)               c meets every clause AND authority is sufficient (see A-A).
revocable(c)           the exit right under c is standing and EXERCISABLE in fact
                       — withdrawal available, not merely on paper.

Authority(p, a) ∈ [0,1]   GRADUAL: p's capacity to exercise the right for act a.
Threshold(a) ∈ [0,1]      the authority an act a requires; rises with stakes /
                          irreversibility (00_definitions §Authority).

Legitimate(a)          a's verdict ∈ {ALLOW, DENY, DEFER}. NOT a score, NEVER a
                       function of welfare (00_definitions §Legitimacy).
ExitCost(a) ∈ [0,∞]    the cost to the owner of exercising revocation under a.
Gbar                   the exit-cost threshold above which "revocable" is a fiction.
                       UNKNOWN — open node G (§Open nodes).
```

Convention: `⊢` is "derivable in this ledger"; `[X,Y]` after a line names the
axioms/theorems used. ALLOW/DENY/DEFER are the only verdicts; nothing here ever
produces a magnitude.

---

## 1. Axioms

Each axiom is stated, then given the single observation that would **falsify** it
(§Falsifiers collects these).

**A-C — Consent axiom.**
```text
∀a ∀b.  crosses(a, b) ∧ Legitimate(a)=ALLOW  →
        ∃c.  Consent(c, owner(b), a) ∧ valid(c)
```
A boundary crossing is legitimate only with the valid consent of that boundary's
owner. (This is the kernel core restated; cf. AXIOM_REGISTRY A2/A3 and C1.)

**A-R — Revocability axiom.**
```text
∀c.  valid(c) → revocable(c)
```
A consent is valid only if it is revocable. The exit right is **constitutive of
ownership** and is **not** among the things the owner may alienate: to alienate it
is to cease to be the owner the consent presupposed, which is incoherent. (Per
00_definitions §Consent, "revocability is the load-bearing clause"; AXIOM_REGISTRY
C1 lists `revocable(H,A)`.)

**A-A — Authority axiom.**
```text
∀c ∀a.  valid(c) → Authority(owner(b), a) ≥ Threshold(a)
```
A consent is valid only if the consenter's authority for the act meets the act's
threshold. Ownership is binary but *authority is gradual*; a full owner may still
lack the authority to perform a high-threshold act (the child owns its body fully,
authority to alienate organs ≈ 0). This is the clause that lets the ledger DENY
without denying ownership.

**A-X — Exit-reality axiom (the bridge to node G).**
```text
∀c.  revocable(c) → ExitCost( the act c authorises ) ≤ Gbar
```
"Revocable" means the withdrawal is available *in fact*, which fails once exit is
so costly that no owner could take it (ruin, statelessness, starvation). A-X makes
revocability cost-sensitive. It is stated as an axiom but its **content is empty
until `Gbar` is fixed** — see node G. Every theorem that routes through A-X is
therefore *schematic*.

A-C, A-R, A-A are the load-bearing trio. A-X is the honest hinge that exposes where
the program is not yet closed.

---

## 2. Theorems

### T1 — Every legitimate transfer requires valid consent.
```text
Transfer(a) ∧ Legitimate(a)=ALLOW  ⊢  ∃c. valid(c) ∧ Consent(c, owner(b), a)
```
**Derivation.** A transfer is a boundary crossing of the transferred thing's
owner. Apply A-C directly: ALLOW requires `∃c. valid(c)`. ∎ **[A-C]**

### T2 — Consent without revocation is invalid.
```text
¬revocable(c)  ⊢  ¬valid(c)
```
**Derivation.** A-R is `valid(c) → revocable(c)`. Contrapositive:
`¬revocable(c) → ¬valid(c)`. ∎ **[A-R]**

### T3 (corollary) — No valid contract can foreclose its own exit; hence voluntary lifetime slavery is illegitimate even if sincere.
```text
Contract(a) ∧ ( a forecloses revocation of a )  ⊢  Legitimate(a)=DENY
```
**Derivation.** Suppose `a` is a contract whose terms make the consent `c`
grounding it non-revocable (lifetime, no-exit). By the definition of foreclosure,
`¬revocable(c)`. By T2, `¬valid(c)`. By T1 (contrapositive of A-C), a transfer
without valid consent cannot be ALLOW; the verdict is DENY. Sincerity of `c` is
nowhere used in the derivation, so it cannot rescue `a`: the wrong is structural,
not motivational. ∎ **[T1, T2]**

**Schematic flag.** "Forecloses revocation" is read through A-X: a contract
forecloses exit either by *terms* (explicit no-withdrawal) or by *cost*
(`ExitCost(a) > Gbar`). The terms-branch is closed; the cost-branch depends on
`Gbar`. T3 is a theorem on the terms-branch and **schematic** on the cost-branch.

### T4 (corollary) — An arrangement that structurally removes all real exit is illegitimate regardless of stated satisfaction (lock-in).
```text
Arrangement(a) ∧ ExitCost(a) > Gbar  ⊢  Legitimate(a)=DENY
```
**Derivation.** If `ExitCost(a) > Gbar` then by A-X `¬revocable(c)` for the consent
`c` sustaining `a` (revocability would require `ExitCost ≤ Gbar`). By T2,
`¬valid(c)`; by A-C, DENY. The owner's *stated satisfaction* is a fact about
preference, not about `c`'s revocability, and preference is held distinct from
consent (00_definitions, the separation table: `Consent ≠ Preference`,
`Exit-right ≠ Exit-taken`). So satisfaction cannot raise the verdict to ALLOW. ∎
**[A-X, T2]**

**Schematic flag.** T4 is **entirely** on the cost-branch: it *is* the lock-in
theorem and it consumes `Gbar` in its premise. Until node G fixes `Gbar`, T4 has
no truth-conditions — it says "lock-in is illegitimate" without yet saying which
arrangements are lock-in. This is the program's central unclosed dependency.

### T5 (corollary) — Sub-threshold authority blocks legitimacy without denying ownership.
```text
owns(p, b) ∧ Authority(p, a) < Threshold(a)  ⊢  Legitimate(a)=DENY
```
**Derivation.** By A-A, `valid(c) → Authority(p,a) ≥ Threshold(a)`. Contrapositive:
`Authority(p,a) < Threshold(a) → ¬valid(c)`. By A-C, no valid consent ⇒ DENY. Note
`owns(p,b)` is untouched: the verdict denies the *act*, not the *title*. ∎ **[A-A,
A-C]** This is the child-organ-sale verdict (own = 1, authority ≈ 0 ⇒ DENY) and the
formal guarantee that "the incompetent don't own themselves" never follows from a
DENY here.

### T6 (corollary) — Child-transfer and guardian defeasibility.
```text
Person(child) ∧ Authority(child, a) < Threshold(a)  ⊢  Legitimate(a)=DENY
AND  a guardian g may act for child only as a DEFEASIBLE proxy:
     Legitimate(g acts) = ALLOW  →  ( within Authority the child lacks )
                                   ∧ ( revocable by the child on competence )
```
**Derivation, part 1.** Direct instance of T5 with `p = child`: a high-threshold
transfer binding a child is DENY. **[T5]**
**Derivation, part 2.** A guardian holds no *ownership* of the child (A1/A2 of the
kernel: no person owns another). The guardian can only exercise borrowed authority.
That borrowed exercise must itself satisfy A-R: it is valid only while revocable —
here, revocable by the child upon reaching competence, and revocable meanwhile by
the standing possibility of challenge. A guardianship that purports to be *final*
(irrevocable by the maturing child) re-instantiates T3's foreclosure and is DENY. ∎
**[A-A, A-R, T3]**

**Schematic flag.** "Reaching competence" imports the Authority threshold, whose
scale and measurer are flagged [UNDERDETERMINED] in 00_definitions §Authority; T6
part 2 is determinate in *form* (defeasibility required) but not in *calibration*.

### T7 (corollary) — Manufactured consent with a nominal exit.
```text
Consent(c, p, a) ∧ sincere(c) ∧ ( exit exists on paper )
∧ ( the conditions of c's formation were arranged by an interested party
    to drive ExitCost(a) > Gbar )                       ⊢  Legitimate(a)=DENY
```
**Derivation.** Sincerity and paper-exit are both present, so neither the voluntary
clause's *felt* aspect nor the literal existence of an exit clause is the issue.
The interested-party arrangement raises `ExitCost(a) > Gbar`; by A-X the consent is
non-revocable in fact; by T2 invalid; by A-C, DENY. The locus of the wrong is the
*formation* (upstream), not the attestation, which is exactly why sincerity does
not save it. ∎ **[A-X, T2]**

**Schematic flag.** T7 inherits T4's dependence on `Gbar` (cost-branch) AND it
brushes node K: if the interested party did *not* exist, and the high exit cost is
not arranged but merely obtained, the case is no longer "manufactured" but
"adaptive" — and the derivation above no longer fires, because there is no
formation-wrong and (per K) the preference itself may have moved. T7 marks the edge
of what A-R reaches.

---

## 3. The inference chain (provenance of every verdict)

```text
AXIOM            THEOREM           COROLLARY              DECISION
─────            ───────           ─────────              ────────
A-C ───────────► T1 ─────────────────────────────────► ALLOW iff valid consent
A-R ───────────► T2 ──┐
                      ├──────────► T3 (slavery) ───────► DENY  (terms-branch: closed)
A-X ──────────────────┴► T4 (lock-in) ─────────────────► DENY  (cost-branch: ⟂ G)
A-A ───────────► T5 ──┬► T6 (child / guardian) ────────► DENY + DEFER (defeasible)
A-R, A-X ─────────────┴► T7 (manufactured consent) ────► DENY  (cost-branch: ⟂ G, ⟂ K)
```

Reading: a verdict is admissible only if a path traces it leftward to an axiom.
Verdicts whose path touches A-X carry the `⟂ G` (perpendicular-to-G, i.e. blocked
on node G) marker; T7 additionally carries `⟂ K`. These markers are not decoration
— they are the honest statement that the verdict is *conditional on an unproved
lemma*.

---

## 4. Open nodes (the unproved lemmas the force of T3/T4 depends on)

The ledger is candid that its most distinctive verdicts rest on two lemmas it has
not proved. They are not footnotes; per [`../EXIT_RIGHT_PROGRAM.md`](../EXIT_RIGHT_PROGRAM.md)
they are where ~90% of the program's value sits.

### Node G — the exit-cost threshold `Gbar`.
```text
LEMMA-G (UNPROVED):  there exists a principled Gbar such that
                     ExitCost(a) > Gbar  ⟺  exit under a is no exit,
                     and Gbar is definable WITHOUT reading welfare.
```
A-X, and through it T4 and the cost-branches of T3 and T7, are **schematic** until
LEMMA-G is discharged. The danger is precise: every natural way to set `Gbar`
("ruin", "starvation", "statelessness") is a *welfare* magnitude, and importing it
would violate the `Legitimacy ≠ Welfare` separation that defines FDK
(00_definitions §Legitimacy). So LEMMA-G must either (a) find a non-welfare
criterion for "exit-defeating cost" — e.g. cost that itself destroys the *agency*
presupposed by ownership, a structural not a hedonic fact — or (b) concede that the
cost-branch theorems cannot be stated without welfare, which would collapse the
program toward Rothbard (no cost edge) or Sen (welfare edge). **Until G closes, T4
is not a theorem and T3/T7 are theorems only on their terms-branch.**

### Node K — adaptive preference (the threat to A-R's universality).
```text
LEMMA-K (UNPROVED):  a purely STRUCTURAL test (A-R + A-X, no interest-judgment)
                     can correctly DENY a sincere, settled consent to a
                     non-revocable arrangement that the owner does not WANT to exit.
```
A-R is stated universally (`valid(c) → revocable(c)`), and T3/T4 lean on that
universality. The adaptive-preference case (the contented slave: sincere consent,
real exit available, exit *unwanted* because the preference adapted to
subordination) is the one case where the structural reading and considered judgment
may part. Two horns:
- If A-R correctly DENYs the adaptive case on purely structural grounds, LEMMA-K
  holds and A-R is genuinely universal.
- If denying it requires asking whether the *preference* is authentic — an
  interest-judgment about the person's good — then A-R is NOT self-sufficient
  there, FDK must borrow Sen's move, and "protection without paternalism" fails on
  this case. Per Phase 3's table, this is FDK's one predicted **loss**.

LEMMA-K is **not merely unproved; it may be false.** If it is false, A-R's
universality must be *restricted* to "manufactured but not yet internalised"
consent, and T3/T4 lose force exactly on the adaptive sub-case while surviving
everywhere else. The ledger states this rather than papering over it.

**Dependency summary.**
```text
T1               independent of G, K            (closed)
T2               independent of G, K            (closed)
T3 terms-branch  closed ;  cost-branch ⟂ G
T4               ⟂ G  (entirely schematic until LEMMA-G)
T5, T6 part 1    closed ; calibration ⟂ Authority-scale [UNDERDETERMINED]
T6 part 2        closed in form ; calibration ⟂ Authority-scale
T7               ⟂ G  and edge-⟂ K
A-R universality ⟂ K  (may require restriction)
```

---

## 5. What would falsify each axiom

A ledger owes the conditions under which it is wrong.

- **A-C falsified by:** a boundary crossing that considered judgment calls
  legitimate yet that has *no* valid consent of the owner and is *not*
  re-describable as a defensive response to a prior illegitimate crossing. (Pure
  beneficial trespass that everyone endorses and no consent covers.) One robust
  such case ends the consent core.
- **A-R falsified by:** a *non-revocable* arrangement that considered judgment
  robustly calls legitimate, with no manufactured formation and no hidden exit —
  i.e. a case where alienating the exit right is genuinely fine. The adaptive-
  preference case (node K) is the live candidate; if it forces ALLOW, A-R is at
  least non-universal, at most false.
- **A-A falsified by:** a case where sufficient authority is present yet considered
  judgment still DENYs (authority does no work), OR where DENY tracks something
  other than the authority/threshold gap — which would show A-A is not the right
  graded variable.
- **A-X falsified by:** the discovery that "exit is real" cannot be made
  cost-sensitive without welfare (this is node G stated as a falsifier), OR a case
  where high exit cost is present but the arrangement is clearly legitimate
  (showing cost is the wrong handle on revocability). Either outcome breaks the
  bridge A-X was meant to be.

The first axiom to fall takes its dependent theorems with it, per §3's chain. That
is the intended brittleness: the ledger is built to be broken at a *named* joint,
not to be admired.

---

*Phase 4 of the Exit-Right Program. Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0). Engineering: Ali Pourrahim. Open nodes G and K are unproved; T3/T4 are schematic until G is closed.*
