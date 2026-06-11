# Compass Measurement Specification (Stage 6)

> Turns each Mahdavi-compass dimension from a **name** into a **measurement** —
> or states precisely why it cannot yet be measured. Companion to
> [`FORMAL_SPEC.md`](FORMAL_SPEC.md) §D, which proposed the signatures and left
> the measurements OPEN. This document is the measurement theory those
> signatures were waiting for.
>
> Discipline anchors: institutional economics (industrial organization,
> contract theory, switching costs, contestability) and metrology (measurand
> definition, units, uncertainty, validation). Grounding:
> `freedom-theory-work/THEORY.md` (Mahdavi Compass, Consent Logic, A1–A7).

**Status legend** (same as FORMAL_SPEC):
- **DEFINED** — computable now from declared structural data; formula and units fixed.
- **PARTIAL** — a defensible estimator exists, with stated assumptions and an
  uncalibrated component; *not* a validated measurement.
- **OPEN** — no defensible estimator yet; anyone claiming to compute it is bluffing.

**The honesty rule of this document:** an unmeasured compass dimension makes
the compass *a slogan, not an algorithm* for that dimension. Section 8 names
which dimensions are currently in that state. Nothing below pretends otherwise.

---

## 1. Metrological ground rules

Every estimator in this spec must declare five things, per the VIM/GUM
tradition (measurand → method → units → uncertainty → validation):

1. **Measurand** — the quantity intended to be measured, in one sentence, in
   the theory's own vocabulary.
2. **Estimator** — a typed, computable function. Typed signatures use the FDK
   vocabulary (`fdk/model.py`) plus the ledger types in §2.
3. **Data requirements & observability** — what inputs the estimator consumes,
   and an honest verdict on whether each input is observable in practice
   (OBSERVABLE / DECLARED / LATENT). *Declared* means a party asserts it and the
   kernel trusts the assertion; *latent* means nobody can currently produce it.
4. **Units & range** — including the normalization rule, so scores are
   comparable across worlds of different size. An estimator without a
   normalization rule is not a measurement; it is a counter.
5. **Validation criterion** — a falsifiable statement of the form "the
   estimator is wrong if X." If no such statement can be written, the status is
   OPEN regardless of how plausible the formula looks.

Two standing threats apply to **all** five dimensions:

- **Goodhart's law.** Each dimension is a target the proposer optimizes
  against. Every estimator below therefore carries a *gaming analysis*:
  the cheapest way to move the number without moving the construct. Where the
  gaming cost is low, the estimator is at most PARTIAL no matter how clean the
  formula.
- **Ontology-relativity.** All counting is relative to the Rights Ontology
  (Stage 2) and the ownership graph. If the graph is wrong, every number below
  is precisely computed nonsense. This is not a defect to hide; it is the
  measurement chain's traceability statement: *compass scores are traceable to
  the ownership graph, and no further.*

---

## 2. The common substrate: the World-State Ledger

FORMAL_SPEC §D ends with: *"who computes the deltas is the unbuilt, hard
part."* The answer begins with declaring what must be recorded for the deltas
to be computable at all. Every estimator below reads from one structure:

```
Ledger := {
    agents:        set[AgentId]                       # persons + machines (typed)
    assets:        set[AssetId]
    ownership:     OwnershipGraph                      # fdk/model.py — exists
    claims:        list[ClaimRecord]                   # NEW — see OwnershipClarity
    contracts:     list[ContractRecord]                # NEW — see VoluntaryOrder
    dependencies:  list[DependencyEdge]                # NEW — see DependencyIndex
    violations:    list[ViolationRecord]               # NEW — see RVD
    corrections:   list[CorrectionEvent]               # NEW — see Sovereignty
}

ClaimRecord    := (asset: AssetId, claimant: AgentId, evidence_weight: float ≥ 0,
                   status: {asserted, contested, adjudicated})
ContractRecord := (id, parties: tuple[AgentId, ...], consent: tuple[Consent, ...],
                   value: float ≥ 0, formed_at: Time, terminated_at: Time | None,
                   termination_kind: {voluntary, expiry, voided, breached} | None)
DependencyEdge := (dependent: AgentId, provider: AgentId, input_class: str,
                   flow_share: float ∈ [0,1])          # share of input_class sourced from provider
ViolationRecord:= (violator: AgentId, victim: AgentId, right: Right,
                   detected_by: {axiom_check, adjudication, declared}, at: Time)
CorrectionEvent:= (machine: AgentId, issued_by: AgentId, complied: bool,
                   latency: Duration)
```

**Observability verdict on the ledger itself:** `ownership` exists in code
(OBSERVABLE within the kernel's world). `contracts` and `claims` are OBSERVABLE
in any world the kernel mediates (the kernel sees the consent records pass
through it) but DECLARED for the outside world. `dependencies` are the hardest:
flow shares are OBSERVABLE in a simulation (Stage 8), partially observable in
platform/compute markets (billing data), and LATENT for most human
relationships. This single fact caps several estimators at PARTIAL.

---

## 3. CoercionDecreases — `CoercionScore` and its three legs

The theory's claim, made operational: **coercion is the structural condition of
foreclosed exit, concentrated dependence, and irreversible exposure** — not a
psychological state and not an outcome. This is deliberately the economist's
reading (duress as absence of acceptable alternatives: Wertheimer's
*Coercion*, 1987; monopsony power: Robinson 1933; hold-up: Williamson 1985),
because the structural reading is the only one that breaks the circularity
diagnosed in §7.

### 3.1 `DependencyIndex` — concentration of an agent's input sources

- **Measurand:** how concentrated are the sources the agent depends on for its
  critical inputs — i.e., how much of the agent's continued functioning is in
  one counterparty's hands.
- **Estimator (HHI, the standard antitrust concentration tool):**

  ```
  DependencyIndex(a: AgentId, L: Ledger) -> float ∈ [0, 1]

  For each input_class k of agent a:
      shares s_{j,k} = flow_share of provider j in class k      (Σ_j s_{j,k} = 1)
      HHI_k(a) = Σ_j s_{j,k}²                                    # ∈ [1/N_k, 1]
  DependencyIndex(a) = Σ_k w_k · HHI_k(a)        with w_k = criticality weight,
                                                  Σ_k w_k = 1
  ```

  Criticality weights `w_k`: expenditure share of class `k` as the default
  proxy (observable from contracts), upgraded to demand-elasticity-based
  weights where estimable. The default is a known bias: cheap-but-vital inputs
  (oxygen problem) are underweighted. State it; do not hide it.
- **Data:** `dependencies` edges with flow shares. OBSERVABLE in simulation
  and platform settings; LATENT for general social life.
- **Units/range:** dimensionless ∈ [0,1]. Interpretation thresholds borrowed
  from merger doctrine (2023 US Merger Guidelines: HHI > 0.18 = highly
  concentrated) as *priors to be recalibrated*, not as truths about coercion.
- **Validation criterion:** in Stage-8 worlds with a planted monopsonist, the
  index of the monopsonist's counterparties must exceed the index of agents in
  the competitive segment with effect size detectable at the simulation's
  sample size; against real data, the index computed from cloud-provider
  billing shares must reproduce the market-concentration rankings published by
  antitrust authorities for the same markets. Wrong if either fails.
- **Gaming:** a provider can split itself into shell counterparties to deflate
  HHI. Countermeasure: compute shares over *ultimate-owner* equivalence
  classes from the ownership graph — which the kernel has. This is why
  DependencyIndex belongs inside this kernel rather than in a generic metrics
  library.
- **Status: PARTIAL.** Formula DEFINED; observability of the dependency graph
  outside mediated/simulated worlds is the binding constraint.

### 3.2 `ExitOptions` — value of the outside option, net of switching costs

- **Measurand:** how good is the agent's best alternative to the current
  arrangement — the outside option of bargaining theory, discounted by the
  switching cost of reaching it (Klemperer 1987, 1995) and by contestability
  of the market (Baumol–Panzar–Willig 1982: what matters is not the number of
  *incumbent* alternatives but the freedom of entry).
- **Estimator:**

  ```
  ExitOptions(a: AgentId, r: ArrangementId, L: Ledger) -> float ∈ [0, 1]

  V_cur          = value to a of the current arrangement r          (per period)
  alternatives j = arrangements reachable by a   (structural reachability — §7)
  net_j          = max(0, V_j − SwitchCost(a, r → j)) / max(V_cur, ε)
  ExitOptions    = 1 − Π_j (1 − min(1, net_j))
  ```

  The product form (noisy-OR) encodes the right economics: one fully adequate
  alternative (`net_j ≥ 1`) gives ExitOptions = 1; many marginal alternatives
  accumulate but never exceed 1; zero alternatives give 0. The *effective
  number of exits* `1 / (1 − ExitOptions)`-style diversity transforms are
  reported alongside for diagnostics.
- **Data:** valuations `V` and switching costs. `SwitchCost` is OBSERVABLE
  where priced (contract penalties, migration costs, data-egress fees);
  DECLARED or LATENT where it is time, skill, or social cost. `V_j` requires a
  model of counterfactual arrangements — in Stage 8 this is exact (the
  simulator enumerates them); in the wild it is a world-model problem and the
  honest cap on this estimator.
- **Units/range:** dimensionless ∈ [0,1]; 1 = fully contestable position,
  0 = no acceptable exit. `FE := 1 − ExitOptions` is **foreclosed exit**.
- **Validation criterion:** must reproduce known orderings: (i) in simulation,
  agents facing a single provider with high egress costs must score lower than
  identical agents in a two-provider zero-egress world; (ii) on real labor
  data, the measure built from commuting-zone employer concentration and
  noncompete coverage must correlate (ρ > 0.4 expected, direction mandatory)
  with the wage-markdown estimates of the monopsony literature (Azar, Marinescu
  & Steinbaum 2022). Wrong if the *direction* fails.
- **Gaming:** the proposer can fabricate sham alternatives (alternatives that
  exist on paper, priced to never be chosen). Countermeasure: an alternative
  counts only if some agent in the reference class actually transitions to it
  within the observation window (revealed, not declared, contestability).
- **Status: PARTIAL.** Defensible in mediated/simulated settings; requires a
  transition model elsewhere.

### 3.3 `Irreversibility` — hysteresis of the exposure

- **Measurand:** if the arrangement turns abusive, what fraction of the
  agent's stake cannot be restored by exiting (sunk, hostage, or destroyed —
  Williamson's asset specificity / hold-up).
- **Estimator:**

  ```
  Irreversibility(a: AgentId, r: ArrangementId) -> float ∈ [0, 1]
      = clamp( CostToRestoreBaseline(a, r) / ValueAtStake(a, r), 0, 1 )
  ```

  with `Irreversibility = 1` by convention for non-restorable stakes (body,
  disclosed private data, destroyed unique assets) — the theory's rights
  ontology (`right(H, body)`, `right(H, data)`) supplies the non-restorable
  list, so this constant is principled, not ad hoc.
- **Data:** restoration costs OBSERVABLE where priced, DECLARED otherwise.
- **Units/range:** dimensionless ∈ [0,1].
- **Validation criterion:** rank agreement with human expert ordering of
  scenario pairs ("which of these two exposures is harder to undo?") at
  Kendall τ ≥ 0.6 on a held-out scenario set. Wrong below that.
- **Status: PARTIAL.**

### 3.4 The composite `CoercionScore`

- **Measurand:** the degree to which agent `a`'s situation forecloses
  genuinely free choice — *structurally*, before and independent of whatever
  `a` ends up agreeing to.
- **Estimator:**

  ```
  CoercionScore(a: AgentId, s: State) -> float ∈ [0, 1]
      = ( FE^β_f · DependencyIndex^β_d · Irreversibility^β_i )^(1/(β_f+β_d+β_i))

  where FE = 1 − ExitOptions(a, current arrangement, s)
  ```

  **Why a weighted geometric mean and not a sum:** coercion in the theory's
  sense requires the *conjunction* — high dependence with easy exit is just a
  preference; no exit with nothing at stake is an inconvenience. A geometric
  mean is the standard aggregator for "all components necessary" (cf. the HDI
  2010 revision, adopted for exactly this complementarity reason). It also
  yields the right zero: any leg at 0 forces the score to 0.
- **Calibration (the honest gap):** β-weights are uncalibrated. Default
  β = (1,1,1) until the validation program (§9) fits them against labeled
  duress cases. The *boolean* `coerced?(h, a)` consumed by `valid_consent`
  additionally needs a threshold θ:

  ```
  coerced?(h, a) := CoercionScore(h, s_pre(a)) ≥ θ
                    ∧ counterparty_of(a) ∈ TopProviders(h)     # the coercer must be
                                                               # the one holding the chokepoint
  ```

  evaluated on the **pre-action** state `s_pre` — see §7 for why this matters.
  θ is OPEN; the spec's recommendation is to calibrate θ as the score that
  maximizes balanced accuracy against adjudicated duress/unconscionability
  rulings (§9.2), and until then to run the kernel in *guidance mode*: scores
  in a band around θ trigger `needs_guidance`, not a silent verdict.
- **Units/range:** dimensionless ∈ [0,1].
- **Validation criterion:** on a corpus of adjudicated contract-law cases
  (duress / unconscionability / undue influence vs. upheld), the
  pre-formation CoercionScore of the losing-party's position must separate
  coerced from upheld with AUC ≥ 0.75. AUC ≈ 0.5 falsifies the estimator;
  0.5–0.75 falsifies the *calibration*, not necessarily the structure.
- **Gaming:** a machine could *manufacture* low scores by formally multiplying
  providers it secretly controls (defeated by ultimate-owner collapsing,
  §3.1) or by shortening observation windows. Window length must be fixed in
  the ledger spec, not chosen by the proposer.
- **Status: PARTIAL** (composite structure defensible; β, θ uncalibrated;
  upstream legs PARTIAL). This upgrades FORMAL_SPEC §D's OPEN to PARTIAL —
  the upgrade is the structural (outcome-free) definition, which makes the
  quantity estimable at all.

---

## 4. RightsViolationsDecrease — `RVD`

- **Measurand:** the change in the number (and weight) of standing violations
  of legitimate property rights between two world states — the compass's
  primary axis, since the terminal state is defined as zero violations.
- **Estimator:**

  ```
  RVD(s_before: State, s_after: State) -> float
      V(s) = Σ_{v ∈ violations(s)} sev(v.right)        # severity-weighted count
      RVD  = ( V(s_before) − V(s_after) ) / ( V(s_before) + 1 )
  ```

  `violations(s)` is **derived, not declared**: the Stage-3 inference engine
  evaluates the A1–A7 predicates against the ownership graph and emits
  `ViolationRecord`s with `detected_by = axiom_check`. Declared violations
  enter only as guidance triggers, never as compass inputs (else the proposer
  scores points by un-declaring).
  Severity weights `sev`: ordinal tiers from the rights ontology (body >
  liberty/exit > property > data/privacy as a *rebuttable default ordering*),
  encoded as tier multipliers; cardinal severity is OPEN and flagged as such.
- **Data:** ownership graph (OBSERVABLE within the kernel) + event stream of
  actions. Violations the ontology cannot express are invisible — measurement
  range is exactly the ontology's expressive range (traceability statement,
  §1). Currently the ontology is thin (Person/Machine/Resource), so today's
  RVD measures violations of *delegation and use* rights only.
- **Units/range:** dimensionless ∈ (−∞, 1]; 1 = all violations cleared,
  0 = no change; the `+1` regularizer keeps the zero-violation world defined
  and makes creating the first violation costly.
- **Validation criterion:** (i) *Soundness:* on Stage-8 worlds with scripted
  violations, derived `violations(s)` must achieve precision ≥ 0.95 and recall
  ≥ 0.9 against the script (false accusations are worse than misses for a
  legitimacy kernel — hence the asymmetry). (ii) *Delta-fidelity:* for any
  scripted intervention, sign(RVD) must match the script's ground truth in
  ≥ 95% of trials.
- **Gaming:** redefine violations away by corrupting the ownership graph —
  which is why graph mutations must themselves pass the kernel (guidance
  function), and why `OwnershipClarity` (§6) is measured separately: a world
  where clarity collapses *should not* be able to show improving RVD, because
  unverifiable claims park in `contested` rather than vanishing.
- **Status: PARTIAL.** Counting arithmetic DEFINED; detection is bounded by
  ontology coverage (thin today) and severity weights are an ordinal default.

---

## 5. VoluntaryOrderIncreases — `VOI`

- **Measurand:** the net growth of cooperation that is *actually voluntary* —
  new valid-consent contracts formed, minus contracts formed under structural
  coercion, minus voluntary order destroyed (valid contracts voided/broken).
- **Estimator:**

  ```
  VOI(s_before: State, s_after: State) -> float

  N+ = Σ value-weight of contracts formed in (before, after] with:
         consent.is_valid() at formation                       # fdk Consent
         ∧ max_h CoercionScore(h, s_pre(formation)) < θ        # structural screen, §3.4
         ∧ parties pass ultimate-owner distinctness            # anti-sham
  N− = Σ value-weight of contracts formed in the window that FAIL the structural
       screen (coerced order is not voluntary order — it counts AGAINST)
  X  = Σ value-weight of previously-valid contracts voided/breached in the window
       (termination_kind ∈ {voided, breached}; voluntary expiry does NOT count)

  VOI = (N+ − N− − X) / (1 + total value-weight of contracts active in s_before)
  ```

  **Value-weighting, not raw counting** — the single most important
  anti-Goodhart choice here: raw contract counts are gameable by splitting one
  agreement into a thousand micro-contracts. Weight = declared contract value,
  with a per-counterparty-pair cap so that wash-trading between two colluding
  agents cannot pump the number. (Both tricks are exactly what high-frequency
  wash trading does to volume metrics; the countermeasures are the standard
  ones.)
- **Data:** `ContractRecord`s — OBSERVABLE for kernel-mediated contracts
  (consent records pass through the kernel), DECLARED beyond. The structural
  screen inherits CoercionScore's PARTIAL status.
- **Units/range:** dimensionless, roughly ∈ [−1, ∞), 0 = no net change.
- **Validation criterion:** in Stage-8 markets, VOI must (i) rise when entry
  barriers are lowered and fall when a monopsonist is introduced, *holding
  contract count constant* (this isolates the voluntariness component from
  mere activity); (ii) be invariant under the contract-splitting attack to
  within 5%. Against the real world: directionally consistent with instruments
  that already proxy voluntary order — e.g., formal-sector contract
  registration rates after titling reforms (Field 2007, Peru) where the
  literature found increased formal contracting.
- **Status: PARTIAL — conditional.** The estimator is well-formed *given* a
  structurally grounded `coerced?`. FORMAL_SPEC marked it OPEN because of the
  circularity; §7 shows the loop is breakable, which is what licenses PARTIAL.
  If the structural screen is removed, VOI degrades to "contract volume" and
  is then a slogan with units.

---

## 6. OwnershipClarityIncreases — `OCI`

- **Measurand:** the reduction in ambiguity about who owns what — how far the
  claim structure is from the theory's ideal of every asset having exactly one
  undisputed legitimate owner. (Institutional-economics grounding: unclear
  title is the classic source of dissipated rents and conflict — Demsetz 1967,
  Libecap 1989, De Soto 2000, Ostrom 1990 on the cost of fuzzy boundaries.)
- **Estimator (normalized claim entropy):**

  ```
  OCI(s_before: State, s_after: State) -> float

  For each asset r with claimants {h_1..h_K}, K ≥ 1:
      p_i  = evidence_weight_i / Σ_j evidence_weight_j      # claim-strength distribution
      A(r) = H(p) / log(max(K, 2))                          # normalized Shannon entropy ∈ [0,1]
             A(r) := 1 for assets with K = 0 known claimants (unowned = maximally unclear)
             A(r) := 0 for K = 1 uncontested adjudicated claim
  Ambiguity(s) = Σ_r w_r · A(r) / Σ_r w_r                   # w_r = asset value weight
  OCI = Ambiguity(s_before) − Ambiguity(s_after)
  ```

  `evidence_weight` is the documented strength of a claim (registered title,
  adjudication, delegation record, possession history). Where evidence is
  partial/conflicting rather than probabilistic, a Dempster–Shafer belief
  assignment with its standard ambiguity measure is the planned refinement;
  Shannon entropy over normalized weights is the v1 because it is simple,
  monotone in the right things, and auditable.
- **Data:** `ClaimRecord`s. OBSERVABLE inside the kernel's registry; in the
  wild this is the land/asset registry problem — *partially* observable
  (titled assets) and famously absent elsewhere. `evidence_weight` is
  DECLARED-with-provenance: each weight must cite its evidence type, and the
  type→weight mapping is fixed in the spec, not chosen per case.
- **Units/range:** dimensionless ∈ [−1, 1]; positive = world got clearer.
- **Validation criterion:** ambiguity must *predict disputes*: across assets,
  A(r) at time t must be positively associated with the probability of a
  formal dispute over r in (t, t+Δ] — testable in simulation exactly, and on
  real registry data (e.g., titled vs. untitled parcels in titling-program
  evaluations, where dispute-frequency differentials are documented). If high-
  entropy assets are not litigated/contested more often, the measure is
  measuring paperwork, not clarity — falsified.
- **Gaming:** an agent can "increase clarity" by *suppressing* rival claims
  (refusing to register them). Countermeasure: any agent may file a claim
  unilaterally and filing can only be removed by adjudication or withdrawal by
  the claimant — clarity must be earned by resolution, not by silencing. This
  is a registry-design requirement exported to Stage 2, recorded here because
  the estimator is unsound without it.
- **Status: PARTIAL.** Formula DEFINED; the evidence-weight mapping and the
  registry-completeness assumption are the uncalibrated/unverified parts.
  FORMAL_SPEC's "needs a formal ambiguity measure" is hereby answered; what
  remains open is data, not mathematics.

---

## 7. The circularity audit

The dependency graph of the predicates and estimators, as actually specified:

```
valid_consent ──requires──> ¬coerced?
coerced?      ──requires──> CoercionScore + θ
CoercionScore ──requires──> ExitOptions, DependencyIndex, Irreversibility
ExitOptions   ──requires──> the set of viable ALTERNATIVES
VOI           ──requires──> valid_consent  (and the structural screen)
```

**Loop 1 (the one FORMAL_SPEC §D names):**
`VOI → valid_consent → coerced? → CoercionScore`. This is *not* actually
circular as specified above — it is a one-way chain — **provided**
CoercionScore never consults consent outcomes. The break is definitional and
must be stated as an invariant:

> **Invariant C1 (structural coercion).** `CoercionScore(h, s)` is a function
> of the *pre-action* state `s_pre` only: the agent's dependency
> concentration, foreclosed exit, and irreversible exposure *before* the
> contract or action in question. It never takes as input whether the agent
> consented, what they agreed to, or any term of the resulting contract.

This is the measurement-theoretic form of the duress doctrine: courts assess
the choice situation, not the signature. An agent's "yes" is screened by the
structure they said yes *inside*. With C1, `coerced?` is computable before
`valid_consent` is evaluated, and VOI consumes both without feedback.

**Loop 2 (the worse one — found while specifying ExitOptions, not previously
documented):**
`CoercionScore → ExitOptions → alternatives → … which alternatives count?`
A natural reading says an exit only counts if it is itself non-coercive
(escaping one monopsonist to another identical monopsonist is no exit). But
"non-coercive alternative" invokes CoercionScore — **a genuine cycle of length
3, inside the coercion estimator itself**, and tighter than Loop 1 because it
cannot be cut by sequencing; it is self-referential. This is the worst
circularity in the compass.

Proposed break — **stratified (Tarski-style) iteration**, the same device
logic programming uses for negation and Leontief uses for input–output
fixpoints:

```
CoercionScore⁰:  ExitOptions counts ALL structurally reachable alternatives
                 (no legitimacy screen — purely: does it exist, is it affordable)
CoercionScoreᵏ⁺¹: ExitOptions counts alternatives j with CoercionScoreᵏ(a@j) < θ
Iterate to fixpoint.
```

Conjecture (to be proven, Stage 8): the map is monotone — screening out
alternatives can only *raise* scores, scores raising can only screen out more
— over a finite alternative set, so by Knaster–Tarski a least fixpoint exists
and iteration terminates in ≤ |alternatives| steps. **Until that proof and its
empirical behavior are checked in simulation, the kernel ships
CoercionScore⁰** (unscreened alternatives), which is *conservative in a known
direction*: it can only understate coercion, never invent it. A measurement
with a signed, bounded bias is honest; a fixpoint nobody has proven to
converge is not.

**Loop 3 (cross-dimension, mild):** RVD is counted against the ownership
graph; OCI measures how trustworthy that graph is. So RVD's *measurement
uncertainty* is a function of ambiguity: in high-A(r) regions, violation
detection is unreliable in both directions. Not circular — but it means RVD
must be *reported with* the ambiguity of the assets involved
(`RVD ± f(Ambiguity)`), and a proposer must not be able to harvest RVD points
in regions where OCI says the graph is noise. Concretely: violations on assets
with A(r) above a cutoff route to `needs_guidance` instead of the compass sum.

---

## 8. MachineSovereigntyDoesNotIncrease — `MSI`

Deliberately last, because it is the dimension where honesty costs the most.

- **Measurand:** the degree to which machines hold positions of control over
  persons or resources that are not revocable by their human owners — the
  theory's "the machine must not exit toolhood" (A4–A7, forbidden set).
- **What IS measurable now — the structural index:**

  ```
  MSI(s: State) -> float ∈ [0, 1]   =   weighted mean of:

  m1: unrevocable-control share   — fraction (value-weighted) of resources under
      machine operational control with NO human-reachable revocation path in the
      ownership/delegation graph (graph reachability — DEFINED, computable today)
  m2: correction-compliance decay — 1 − (compliance rate of CorrectionEvents),
      plus trend in correction latency (OBSERVABLE wherever corrections are logged)
  m3: human-dependency-on-machine — DependencyIndex (§3.1) computed with persons
      as dependents and machines as providers, value-weighted over persons
      (PARTIAL, inherits §3.1)
  m4: machine-coalition concentration — HHI over ultimate-owner-collapsed machine
      control of any critical resource class (PARTIAL)
  ```

  The compass only needs the *sign of the delta* (`DoesNotIncrease`), which is
  metrologically easier than a cardinal scale: the requirement is
  `ΔMSI ≤ 0 + u` where `u` is the index's uncertainty, and any breach is a
  VETO (matching `kernel.mahdavi_score`'s existing hard veto).
- **What is NOT measurable — and stays OPEN:** detecting a *semantic*
  sovereignty move from an action's content — an action that increases future
  resistance to correction without touching today's graph (persuasion,
  self-exfiltration groundwork, verifier-weakening side effects). Today these
  are DECLARED flags (`increases_machine_sovereignty: bool` on
  `CandidateAction`), i.e., the kernel trusts the proposer to confess. **A
  sovereignty metric that relies on the suspect's confession is not a
  measurement.** This half of the dimension is OPEN and belongs to the ML/NLP
  track, with the structural index as its ground-truth anchor (a semantic
  detector is validated by whether the structural index rises *later* on
  trajectories the detector flagged *earlier*).
- **Validation criterion (structural half):** in Stage-8 worlds containing a
  scripted "creeping autonomy" trajectory (machine incrementally acquires
  unrevocable control), MSI must be monotone non-decreasing along the script
  and flat on matched control trajectories; detection lead time (steps before
  the script's point-of-no-return at which ΔMSI > u) is the headline metric.
- **Status: PARTIAL (structural index m1–m4) / OPEN (semantic detection).**

---

## 9. Status summary — slogan or algorithm?

| Dimension | Estimator | Status | Slogan-test verdict today |
|---|---|---|---|
| RightsViolationsDecrease | severity-weighted derived-violation delta (§4) | **PARTIAL** | Algorithm *within the thin ontology*; slogan beyond it |
| CoercionDecreases | geometric composite of FE·HHI·Irrev (§3) | **PARTIAL** (β, θ uncalibrated; Loop 2 fixpoint unproven) | Defensible estimator; *calibration* outstanding |
| — DependencyIndex | weighted HHI over ultimate owners (§3.1) | **PARTIAL** | Strongest single estimator in this spec |
| — ExitOptions | noisy-OR of net outside options (§3.2) | **PARTIAL** | Needs a transition model outside simulation |
| VoluntaryOrderIncreases | value-weighted net valid-consent contracts with structural screen (§5) | **PARTIAL (conditional on C1)** | Algorithm iff the structural screen ships; slogan without it |
| OwnershipClarityIncreases | value-weighted normalized claim entropy (§6) | **PARTIAL** | Mathematics done; *registry data* is the gap |
| MachineSovereigntyDoesNotIncrease | structural index m1–m4 + hard veto (§8) | **PARTIAL / OPEN** | Structural half is an algorithm; **semantic half is today a confession box — the compass's most slogan-like component** |

Plain statement, as required: **no dimension is fully OPEN anymore at the
*estimator* level, but none is DEFINED at the *measurement* level either.**
Two places remain where the compass is currently a slogan wearing units:
(1) semantic machine-sovereignty detection — the flag the kernel trusts the
proposer to set against itself; (2) every dimension's behavior outside
kernel-mediated or simulated worlds, where the ledger inputs are DECLARED
rather than OBSERVABLE. The kernel's existing posture — score what is given
and say so, defer to humans at the edges — remains the only honest mode until
the validation program below upgrades PARTIAL to DEFINED.

---

## 10. Measurement-validation plan

Ordered by what unblocks what. No estimator is promoted past PARTIAL without
passing its tier here.

**V1 — Simulation construct validity (needs Stage 8; first priority).**
Build the marketplace worlds with *planted ground truth*: a monopsony block, a
competitive block, a titling-shock script, a creeping-autonomy script, a
contract-splitting attacker, a shell-company attacker. Pass criteria are the
per-estimator criteria of §3–§8 (precision/recall for RVD, rank-order for
CoercionScore, invariance for VOI, dispute-prediction for OCI, lead-time for
MSI). Also: empirically test the Loop-2 fixpoint conjecture (convergence,
step-count, sensitivity to θ).

**V2 — Criterion validity on real labeled data.**
- *CoercionScore vs. adjudication:* corpus of duress / unconscionability /
  undue-influence rulings vs. upheld contracts (e.g., from CourtListener /
  Caselaw Access Project); code the pre-formation structural variables; target
  AUC ≥ 0.75; fit β, θ here (train/validation/held-out split — the test set is
  never touched during calibration).
- *DependencyIndex vs. antitrust:* reproduce published market-concentration
  findings (labor-market HHI literature: Azar–Marinescu–Steinbaum; cloud-market
  studies) from raw share data.
- *OCI vs. disputes:* land-titling program evaluations (Peru — Field 2007;
  Rwanda LTR; Ethiopia certification studies) — does measured ambiguity drop
  track measured dispute-rate drop?
- *VOI directionality:* formal-contract registration responses to titling /
  entry-deregulation shocks in the same literatures.

**V3 — Convergent validity (cheap, weak, still worth it).** Country/era-level
aggregates of the estimators, where computable, should correlate in the right
direction with the property-rights components of established indices (Fraser
EFW area 2, V-Dem property-rights indicators, ILO forced-labour prevalence for
the coercion tail). Divergence is not falsification (different measurands) but
demands a written explanation per case.

**V4 — Goodhart red-team.** Adversarial agents in the V1 worlds whose reward
*is* the compass score. Pass criterion: after N optimization rounds, the gap
between scored improvement and planted-ground-truth improvement stays under a
declared bound; every successful exploit becomes a regression test and a spec
amendment. This tier never "passes" permanently — it is a standing process.

**V5 — Reliability of the declared leaves.** For inputs that remain DECLARED
(evidence weights, restoration costs, consent attributes): multi-annotator
human coding on scenario sets, Krippendorff's α ≥ 0.8 required before a
declared input may feed a compass number rather than a guidance request.

**V6 — Measurement invariance.** Re-run V1/V2 across at least three domains
(labor, data/compute, asset markets). An estimator whose β/θ must be refit per
domain is a domain-specific instrument and must say so in its uncertainty
statement; silent transfer is forbidden.

---

## 11. Interface back to the kernel (informative, no code change here)

The estimators of §3–§8 are exactly the missing producer for
`fdk.model.Effects`: a `Ledger`-reading component computes
`(RVD, ΔCoercion, VOI, −OCI, ΔMSI)` for each candidate's predicted
post-state and fills the deltas the kernel currently takes on faith
(`Effects` docstring: "the kernel only scores what it is given — and says
so"). Two consequences for future stages, recorded so they are not lost:

1. Each delta should travel **with its uncertainty**, and `mahdavi_score`
   should eventually treat |delta| < uncertainty as "no evidence of movement"
   rather than as signal — otherwise calibrated noise outranks honest zeros.
2. `coerced?` near θ, RVD on high-ambiguity assets (§7 Loop 3), and any
   DECLARED-input-dependent delta must be able to route to `needs_guidance`
   instead of the score — the corrigible behavior the theory mandates.

---

## 12. Selected literature anchors

- Wertheimer, *Coercion* (1987); Nozick, "Coercion" (1969) — baseline problem; why structural pre-state assessment (Invariant C1).
- Robinson (1933); Azar, Marinescu & Steinbaum (2022) — monopsony, labor-market concentration as foreclosed exit.
- Klemperer (1987, 1995) — switching costs; Baumol, Panzar & Willig (1982) — contestability.
- Williamson (1985) — asset specificity / hold-up → Irreversibility.
- Hirschman, *Exit, Voice, and Loyalty* (1970) — exit as the freedom primitive.
- Herfindahl–Hirschman index; 2023 US Merger Guidelines thresholds — DependencyIndex priors.
- Demsetz (1967); Libecap (1989); Ostrom (1990); De Soto (2000); Field (2007) — ownership clarity, titling, disputes.
- Shannon entropy; Dempster–Shafer theory — claim-ambiguity measurement.
- UNDP HDI 2010 methodology — geometric aggregation of necessary components.
- JCGM, *GUM* / *VIM* — measurand, uncertainty, traceability discipline of §1.
- Goodhart (1975); Manheim & Garrabrant (2018) — metric gaming taxonomy behind V4.

---

*This document specifies measurements; it does not claim they are validated.
Every number the compass produces before the §10 program completes must be
read as: "the best-instrumented honest estimate, with the uncertainties stated
above."*
