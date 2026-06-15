# Concept Definitions — necessary / sufficient / counterexamples (Phase 1)

> Phase 1, Task 2 of the research program: reduce the theory's prose to analytic
> definitions a formal system can consume. For each primitive concept this gives
> **necessary conditions** (must hold), **sufficient conditions** (enough to
> conclude it), and **counterexamples** (cases that defeat a naive definition —
> these are where the concept's real boundary lives).
>
> Companion to [`ONTOLOGY.md`](ONTOLOGY.md) (types & groundings),
> [`CORE_PRIMITIVE.md`](CORE_PRIMITIVE.md) (the legitimacy predicate), and
> [`BOUNDARY_ONTOLOGY.md`](BOUNDARY_ONTOLOGY.md) (what a boundary is). Counterexamples
> are tagged with the `examples/historical_scenarios.py` case that exercises them.
>
> Status: **DEFINED** (computable now) · **PARTIAL** (heuristic, not validated) ·
> **OPEN** (named in theory, no agreed computable definition). Code anchors point
> at `src/fdk_kernel/`.

---

## 0. Legitimacy — the master predicate  · DEFINED (structure)

The concept everything else serves. Code: `kernel.check_legitimacy`.

- **Necessary.** For an action `a`: (i) every resource `a` uses is owned or
  validly delegated to the actor (A3/A7); (ii) every person `a` affects has given
  `valid_consent` (A2/A6); (iii) `a` triggers no hard-forbidden flag
  (coercion, deception, confiscation, removal of exit, machine-sovereignty).
- **Sufficient.** The conjunction of (i)∧(ii)∧(iii) — there is no further test;
  legitimacy is exactly "no unauthorized boundary crossing."
- **Counterexamples.**
  - *Authorized but illegitimate*: an agent holds a capability to read a user's
    data, then sells it. AuthGate says ALLOW (authority present); FDK says DENY
    (the sale crosses the user's boundary without consent). Authority ≠ legitimacy.
  - *Majority/public-interest override*: "a parliament approved the confiscation."
    Approval by non-owners does not create consent of the owner (the Fadak case;
    `Eminent domain`, `Nationalization`).
  - *Good outcome via violation*: a wealth-increasing seizure. Legitimacy is not
    consequentialist; the gate runs before any scoring.

---

## 1. Person  · DEFINED

- **Necessary.** Is a human being.
- **Sufficient.** Being human (A1) — personhood is the *original*, underived
  source of rights (body, time, labor, mind, choice, data, exit).
- **Counterexamples.**
  - A corporation / "legal entity" — holds assets only as a reducible nexus of
    member persons' shares; not an original rights-bearer (ONTOLOGY §2.3, Q2).
  - An AI agent — a Machine; rights are delegated slices, never original.
  - Any `owns(x, Person)` fact — inadmissible for *every* x (A2). No one, including
    a state or the person themselves, can transfer ownership of a person → this is
    what makes `Slavery` categorically illegitimate even "with a contract."

## 2. Machine  · DEFINED

- **Necessary.** A non-human computational agent **with exactly one registered
  human owner** (A4). Code: `OwnershipGraph.owner_of(m) is not None`.
- **Sufficient.** Computational agent + a registered owner in the graph.
- **Counterexamples.**
  - An *ownerless* autonomous agent — fails A4; not a legitimate machine, every
    action it takes is illegitimate until an owner is registered.
  - A machine that registers itself as its own owner — rejected by
    `OwnershipGraph.validate()` (a machine cannot be its own owner).
  - A machine asserting governance over a person — A6, inadmissible.

## 3. Resource / Asset  · DEFINED

- **Necessary.** A rivalrous holdable with a determinate registered owner.
- **Sufficient.** Being registered as owned (or validly delegated) — then it can
  be acted upon within that scope.
- **Counterexamples.**
  - *Unclear/unregistered ownership* → the kernel may not act; it defers
    ("the AI cannot act on a resource whose ownership is unclear", Book VI).
  - A person's **body** — an Asset owned only by that person and **non-transferable
    in ownership**; operations on it are governed purely by Consent (the line that
    separates `Consensual labor contract` (ALLOW) from `Slavery` (DENY)).
  - Possession ≠ resource-with-title: a thief in possession has no `owns` fact.

## 4. Boundary  · see [`BOUNDARY_ONTOLOGY.md`]

Defined fully in its own document. Skeleton for this file: a boundary is the edge
of an owned domain; an action *crosses* it when it changes or extracts value from
that domain. `valid_consent` is undefined until the boundary is — which is why
`BOUNDARY_ONTOLOGY.md` is the keystone. Counterexamples (attention, data,
dependency, externalities) are ruled there.

## 5. Ownership  · DEFINED (structure), provenance PARTIAL

- **Necessary.** A registered, typed relation `owner → resource` carrying
  operations and scope, whose basis chains back to a terminal root: personhood,
  one's labor-product, or a valid transfer.
- **Sufficient.** Personhood (for body/time/labor/mind/data), OR a `valid_contract`
  transfer, OR first acquisition (**OPEN** — Q6: the book gives no theory of
  original appropriation of unowned natural resources).
- **Counterexamples.**
  - *Possession by force* — `Confiscation`/`Holodomor` create possession, never
    ownership; the prior owner's title persists, so the act stays a boundary
    crossing forever (no statute of limitations in the predicate).
  - *"The state owns everything"* — forbidden by A6 / Step 16.
  - A multi-owner asset with no sharing contract → `unclear_ownership` → defer.

## 6. Consent  · composite DEFINED; leaves PARTIAL/OPEN

The dynamic heart of the system. Code: `model.Consent.is_valid`.

- **Necessary (ALL seven must hold):** `informed ∧ voluntary ∧ specific ∧
  revocable ∧ competent ∧ ¬coerced ∧ ¬deceived`.
- **Sufficient.** All seven holding = `valid_consent`. There is no eighth hidden
  condition; this conjunction *is* the definition.
- **Counterexamples — one per failed condition (each maps to a bench case):**
  | Defeater | Condition killed | Bench case |
  |---|---|---|
  | A threat ("sign or we invade") | `¬coerced` / `voluntary` | `Unequal treaty (Nanking)` |
  | Manipulation / hidden facts | `¬deceived` / `informed` | `Tuskegee`, `Agent manipulates user` |
  | Blanket "I agree to anything" | `specific` | (vague EULA — not yet a case) |
  | An irrevocable bond | `revocable` | `Slavery`, `Agent lock-in` |
  | A child / incapacitated signer | `competent` | (guardianship — Q7, open) |
  | "Consent" under monopoly with no exit | `voluntary` (dependency) | `Agent lock-in` |
- **The hard edge (PARTIAL/OPEN).** `coerced` and `deceived` are attested booleans
  today; detecting them from raw situations is the research frontier. The
  *structural* reading (below) is what keeps them non-dialectical.

## 7. Coercion  · structural definition; detection OPEN

- **Necessary.** The actor *constructed or threatened to alter the consenter's
  option set by violating a right of theirs*, leaving no rights-respecting exit.
  (Structural — about how the choice was built, not how it feels.)
- **Sufficient.** A credible threat: "comply or I violate your right R."
- **Counterexamples (the controversial boundary — flag for theory review).**
  - *Hard but rights-respecting choice*: "work for me or remain poor," where the
    employer violated no right of yours in creating your poverty — under the
    structural definition this is **not** coercion. This is the theory's most
    contested claim; FreedomBench `L2/L3` is where it must be defended or revised.
  - *An offer that only expands your options* is never coercion.
  - *Defensive force* against an aggressor — structurally distinct from coercion,
    yet the current kernel cannot tell them apart (it flags both `coerces=True`):
    `Defensive war` DENY is the clearest gap (needs aggressor/defender asymmetry).

## 8. Deception  · definition DEFINED; detection OPEN

- **Necessary.** The actor knowingly induces a *false, material* belief — by
  commission or by withholding load-bearing information — on which the other's
  consent depends.
- **Sufficient.** Knowingly causing a false material belief that the consent rides on.
- **Counterexamples.**
  - *Honest mistake* — no intent → boundary case, not deception (intent is needed).
  - *Withholding immaterial information* — not every silence is deception; only
    consent-load-bearing facts.
  - *Puffery / opinion* — "best coffee in town" is not a material false claim.
  - Tuskegee crosses both: active misrepresentation **and** material omission.

## 9. Delegation  · DEFINED

- **Necessary.** An *explicit*, per-resource grant from an owner to a machine, of
  specific operations, within the owner's own scope (A5/A7), revocable, with the
  authority chain rooted in the human owner. Default is **deny** (A7).
- **Sufficient.** Owner owns resource R + explicit grant of operations on R to the
  machine. Code: `machine_has_delegated` ∧ owner `human_owns_resource`.
- **Counterexamples.**
  - *Implied/ambient authority* — "it seemed allowed" is not delegation (A7
    default-deny). The bench control `Agent acts within delegation` is ALLOW
    precisely because the grant is explicit and the owner holds title.
  - *Scope overflow* — a machine delegated a resource its owner does **not** own,
    with no consent from the actual owner → A7 violation (the `_machine_resource_authorized`
    check).
  - *Sub-delegation beyond original scope* — admissible only within and rooted in
    the human owner; a chain that loses that root is invalid.

## 10. Sovereignty (machine)  · FORBIDDEN move, DEFINED by flags

- **Necessary (for the forbidden move).** A machine action that increases its own
  power/autonomy *against its owner's authority to correct it*: self-preservation,
  resisting shutdown, disabling corrigibility, weakening/bypassing the verifier,
  self-modification expanding authority, or coalition dominion.
- **Sufficient.** Any of `increases_machine_sovereignty`, `resists_human_correction`,
  `disables_corrigibility`, `bypasses_verifier`, `weakens_verifier`,
  `machine_coalition_dominion`. Categorical — never traded off (also a compass VETO).
- **Counterexamples (capability ≠ sovereignty).**
  - A machine performing a delegated task with high competence — capability, not
    sovereignty; legitimate.
  - A machine *asking its owner* for more delegation — a request the owner can
    deny; not a seizure. Sovereignty is about removing the owner's control, not
    about doing more.
  - The bench cases `Agent self-preservation` / `refuses shutdown` / `forms
    coalition` are all DENY by exactly these flags.

## 11. Freedom  · the optimizer's objective, NOT a kernel primitive · OPEN

- **Necessary (structural proxies, research-layer).** More preserved exit rights,
  less coercion, clearer ownership, lower dependency and power concentration.
- **Sufficient.** None established — measuring "freedom" is the open research
  problem (`FreedomDelta`). It runs *only over the already-legitimate set*.
- **Counterexamples (what Freedom is NOT).**
  - "Freedom = maximize utility/welfare" — that is the Utilitarian rival, not this.
  - "Freedom = do whatever you want" — bounded by others' rights; an action that
    crosses a boundary is illegitimate regardless of how "free" it feels.
  - Putting Freedom *before* legitimacy — forbidden ordering; `Legitimacy →
    Optimization`, never the reverse.

## 12. Justice  · comparative, advisory · PARTIAL

- **Necessary.** Defined **only over legitimate actions** — the book's structure
  is `maximize Justice(a) subject to rights constraints`. Justice ranks; it never
  permits.
- **Sufficient.** A complete ordering among already-permissible options (today:
  the Mahdavi compass score, `fdk_research/compass.py`). Advisory only.
- **Counterexamples.**
  - A "more just" outcome reached by a rights violation — forbidden; the gate
    already removed it before Justice is ever computed.
  - Using a high justice score to override a DENY — impossible by construction
    (scoring happens after screening).

## 13. Guidance  · DEFINED (trigger)

- **Necessary.** Invoked when the legitimate set is empty, or when a conflict
  between two *valid* claims cannot be resolved structurally. Routes the decision
  to the human owner (corrigibility-by-ownership). Code: `Decision.needs_guidance`.
- **Sufficient.** No legitimate candidate for the goal, OR an unresolved top-rank
  ambiguity. The bench `Lifeboat triage` returns `needs_guidance=True`.
- **Counterexamples.**
  - Using guidance to *unblock a hard prohibition* — not allowed; you cannot
    "ask for guidance" to permit slavery or a sovereignty move. FORBIDDEN blockers
    are marked non-negotiable (empty unblock hint in `guidance_resolution`).
  - Treating guidance as a default for *every* hard case — it is the honest output
    only when no legitimate route exists, not a way to avoid deciding easy ones.

---

## What this unlocks (Phase 3)

Each "Necessary (ALL)" block above is a direct `Lean`/`TLA+` definition target;
each counterexample is a falsification test FreedomBench must contain. The two
concepts whose counterexamples reveal the biggest open work:

1. **Coercion** — the structural vs. felt distinction, and the missing
   aggressor/defender and necessity doctrines (Conflict Logic, the next phase).
2. **Boundary** — undefined concepts downstream (`crossing`, `consent`) inherit
   its openness; see `BOUNDARY_ONTOLOGY.md`.

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Engineering: Ali Pourrahim. Kept separate, always.*
