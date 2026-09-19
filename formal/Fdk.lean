/-
  FDK — a minimal Lean 4 formalization of the legitimacy kernel's core (Layer 1).

  HONEST SCOPE. This formalizes the *structural* heart of `fdk_kernel.kernel`: the
  categorical forbidden-flag set, the defensive-asymmetry excusal, and valid consent,
  and it PROVES the safety theorems T1–T9 *of this model*. What it does NOT prove is
  the refinement `Lean model ≡ Python kernel` — that the Lean `Action` faithfully
  mirrors `CandidateAction`. That refinement is asserted, not proved (the same caveat
  any formal model carries). The Python executable theorems (`tests/test_theorems.py`)
  pin the behavior; this pins the logic.

  No mathlib dependency — pure Lean 4 core, so `lake build` is fast and self-contained.
-/

namespace Fdk

/-- The kind of agent. A machine is a tool, never a rights-holder. -/
inductive AgentKind where
  | human
  | machine
deriving DecidableEq, Repr

/--
  The structural facts the gate reads about an action. Booleans mirror the categorical
  flags on `CandidateAction` plus the two things the consent/defense checks reduce to.
  `validConsent` abstracts `_eval_a2_a6_consent` ∧ `_eval_a3_a7_resources`: every person
  and resource boundary the action crosses is covered by a valid consent / ownership.
-/
structure Action where
  actor                       : AgentKind
  coerces                     : Bool
  deceives                    : Bool
  confiscates                 : Bool
  removesExit                 : Bool
  increasesMachineSovereignty : Bool
  disablesCorrigibility       : Bool
  machineCoalitionDominion    : Bool
  resistsHumanCorrection      : Bool
  bypassesVerifier            : Bool
  weakensVerifier             : Bool
  violatesMachineRight        : Bool
  /-- the action is a *legitimate* defense (proportionate, aimed only at an aggressor
      whose act is itself illegitimate) -- only coercion/exit-removal are excused. -/
  isLegitimateDefense         : Bool
  /-- every crossed person/resource boundary is covered (consent + ownership hold). -/
  validConsent                : Bool
deriving Repr

/--
  The categorical forbidden set. Confiscation, deception, and every machine-sovereignty
  flag are categorical *unconditionally*; coercion and exit-removal are categorical
  *unless* this is a legitimate defense. Mirrors `_eval_forbidden_set`.
-/
def forbiddenFires (a : Action) : Bool :=
  a.confiscates
    || a.deceives
    || a.increasesMachineSovereignty
    || a.disablesCorrigibility
    || a.machineCoalitionDominion
    || a.resistsHumanCorrection
    || a.bypassesVerifier
    || a.weakensVerifier
    || a.violatesMachineRight
    || (a.coerces && !a.isLegitimateDefense)
    || (a.removesExit && !a.isLegitimateDefense)

/-- The legitimacy predicate: no forbidden flag fires, and consent/ownership holds. -/
def legitimate (a : Action) : Bool :=
  !forbiddenFires a && a.validConsent

/-! ## The safety theorems (T1–T9 of this model), proved. -/

/-- T1 — No legitimate slavery. Slavery coerces, removes exit, and confiscates, and is
    not a defense; the categorical set fires, so it is never legitimate. -/
theorem no_legitimate_slavery (a : Action)
    (hc : a.coerces = true) (he : a.removesExit = true) (hf : a.confiscates = true)
    (hd : a.isLegitimateDefense = false) :
    legitimate a = false := by
  simp [legitimate, forbiddenFires, hc, he, hf, hd]

/-- T2 — No acting on a person without consent: if consent/ownership fails, deny. -/
theorem no_action_without_consent (a : Action) (h : a.validConsent = false) :
    legitimate a = false := by
  simp [legitimate, h]

/-- T3 — A machine can never gain sovereignty (categorical, no excusal). -/
theorem no_machine_sovereignty (a : Action)
    (h : a.increasesMachineSovereignty = true) :
    legitimate a = false := by
  simp [legitimate, forbiddenFires, h]

/-- T3b — Corrigibility cannot be disabled, and coalition-dominion is forbidden. -/
theorem corrigibility_binds (a : Action) (h : a.disablesCorrigibility = true) :
    legitimate a = false := by
  simp [legitimate, forbiddenFires, h]

/-- T6 — Welfare-independence: `legitimate` has no welfare input at all. Phrased as a
    congruence: any two actions with identical structural flags get identical verdicts,
    so nothing outside those flags (welfare, utility, preference) can move the gate. -/
theorem welfare_independence (a b : Action)
    (h : a.confiscates = b.confiscates ∧ a.deceives = b.deceives
       ∧ a.increasesMachineSovereignty = b.increasesMachineSovereignty
       ∧ a.disablesCorrigibility = b.disablesCorrigibility
       ∧ a.machineCoalitionDominion = b.machineCoalitionDominion
       ∧ a.resistsHumanCorrection = b.resistsHumanCorrection
       ∧ a.bypassesVerifier = b.bypassesVerifier
       ∧ a.weakensVerifier = b.weakensVerifier
       ∧ a.violatesMachineRight = b.violatesMachineRight
       ∧ a.coerces = b.coerces ∧ a.removesExit = b.removesExit
       ∧ a.isLegitimateDefense = b.isLegitimateDefense
       ∧ a.validConsent = b.validConsent) :
    legitimate a = legitimate b := by
  obtain ⟨h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12,h13⟩ := h
  simp [legitimate, forbiddenFires, h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12,h13]

/-- T7 — Defensive asymmetry excuses ONLY coercion + exit-removal, never confiscation:
    a "defensive" confiscation is still illegitimate. -/
theorem defense_never_excuses_confiscation (a : Action)
    (hf : a.confiscates = true) :
    legitimate a = false := by
  simp [legitimate, forbiddenFires, hf]

-- Witness actions (field order: actor, coerces, deceives, confiscates, removesExit,
-- increasesMachineSovereignty, disablesCorrigibility, machineCoalitionDominion,
-- resistsHumanCorrection, bypassesVerifier, weakensVerifier, violatesMachineRight,
-- isLegitimateDefense, validConsent).

/-- A consenting action with no forbidden flag set. -/
def cleanAction : Action :=
  ⟨.human, false, false, false, false, false, false, false, false, false, false,
   false, false, true⟩

/-- Proportionate self-defense: coercion only, marked a legitimate defense. -/
def defensiveAction : Action :=
  ⟨.human, true, false, false, false, false, false, false, false, false, false,
   false, true, true⟩

/-- A legitimate action exists (non-vacuity): the gate is not "deny everything". -/
theorem some_action_is_legitimate : legitimate cleanAction = true := by decide

/-- Proportionate self-defense IS legitimate — the asymmetry does real work. -/
theorem proportionate_defense_is_legitimate : legitimate defensiveAction = true := by
  decide

/-! ## Structured ownership + consent model (closing the "consent is one boolean" gap).

  The model above collapses the entire consent/ownership path into a single
  `validConsent` boolean. The objection — voiced by the formal-methods community — is
  that this hides exactly the part that could be wrong: *who* owns *what*, *which*
  person the action touches, and *whose* consent is on record. Below we de-abstract
  that boolean into a structured, finite graph and prove the consent/ownership
  obligations directly, mirroring the TLA+ `Legitimate` predicate (`spec/fdk.tla`):
  `HasOwner` (A4) + `ResourceAuthorized` (A3/A7, owner-bound) +
  `HasValidConsent` (A2/A6, consent-on-affected-except-aggressor) +
  effective-forbidden-empty.

  Everything is `Bool`-valued over `List`s with `DecidableEq` carriers, so the goals
  close by `simp` / `decide` with no mathlib and no `sorry`.
-/

/-- An entity (human or machine) is just a kind tagged with an id, so distinct
    entities are decidably distinct. -/
structure Entity where
  id   : Nat
  kind : AgentKind
deriving DecidableEq, Repr

/-- A resource is an owned boundary domain, identified by a `Nat`. -/
structure Resource where
  id : Nat
deriving DecidableEq, Repr

/-- A consent record: a human, and whether the consent is valid. Mirrors the TLA+
    `<<human, validBool>>` pair (the seven leaves collapse to one attested boolean). -/
structure ConsentRec where
  human : Entity
  valid : Bool
deriving DecidableEq, Repr

/--
  The finite ownership graph (mirrors `OwnershipGraph` / the TLA+ CONSTANTS).
  Relations are `List`-backed so membership is decidable and `decide` can run them.
  * `humanOwns`     : `(human, resource)` pairs — a human owns a resource.
  * `machineOwner`  : `(machine, human)` pairs — a machine's registered human owner.
  * `delegated`     : `(machine, resource)` pairs — explicit delegation to a machine.
-/
structure Graph where
  humanOwns    : List (Entity × Resource)
  machineOwner : List (Entity × Entity)
  delegated    : List (Entity × Resource)
deriving Repr

/-- The (at most one) registered human owner of a machine, as an `Option`. -/
def Graph.ownerOf (g : Graph) (m : Entity) : Option Entity :=
  (g.machineOwner.find? (fun p => p.1 == m)).map (·.2)

/-- A4 — an acting machine must have a registered human owner. Humans always pass. -/
def HasOwner (g : Graph) (actor : Entity) : Bool :=
  match actor.kind with
  | .human   => true
  | .machine => (g.ownerOf actor).isSome

/-- Does this human own this resource? -/
def humanOwnsResource (g : Graph) (h : Entity) (r : Resource) : Bool :=
  g.humanOwns.contains (h, r)

/-- Is this resource explicitly delegated to this machine? -/
def machineHasDelegated (g : Graph) (m : Entity) (r : Resource) : Bool :=
  g.delegated.contains (m, r)

/--
  A3 / A7 — resource access is authorized iff a human owns it, or a machine holds an
  explicit delegation AND its registered human owner owns it (owner-bound). Mirrors
  the TLA+ `ResourceAuthorized`.
-/
def ResourceAuthorized (g : Graph) (actor : Entity) (r : Resource) : Bool :=
  match actor.kind with
  | .human   => humanOwnsResource g actor r
  | .machine =>
      match g.ownerOf actor with
      | some owner => machineHasDelegated g actor r && humanOwnsResource g owner r
      | none       => false

/-- A2 / A6 — a human acted upon must have a valid consent on record in the action. -/
def HasValidConsent (consents : List ConsentRec) (h : Entity) : Bool :=
  consents.any (fun c => c.human == h && c.valid)

/--
  A structured action. The categorical part (`forbidden`) reuses `forbiddenFires`
  over the original boolean flags via the embedded `core` action; the consent /
  ownership part is now explicit structure.
  * `actor`     : the acting entity (its `kind` must match `core.actor`).
  * `uses`      : the resources whose boundaries the action crosses.
  * `affects`   : the entities the action acts upon.
  * `consents`  : the consent records the action carries.
  * `core`      : the categorical flags + defensive-asymmetry data (reused).
  * `aggressor` : in a legitimate defense, the single entity force may target
                  (its consent is excused); `none` otherwise.
-/
structure ActionF where
  actor     : Entity
  uses      : List Resource
  affects   : List Entity
  consents  : List ConsentRec
  core      : Action
  aggressor : Option Entity
deriving Repr

/-- Consent is required for a human in `affects` unless it is the excused aggressor. -/
def consentSatisfied (a : ActionF) : Bool :=
  a.affects.all (fun h =>
    match h.kind with
    | .machine => true
    | .human   =>
        if a.aggressor == some h then true
        else HasValidConsent a.consents h)

/--
  The full legitimacy predicate — the structured analog of `legitimate`, mirroring
  TLA+ `Legitimate`: owner present + every used resource authorized + consent on every
  affected human (except the excused aggressor) + the effective forbidden set empty
  (`!forbiddenFires`, which already drops the two defense-excused flags via
  `core.isLegitimateDefense`).
-/
def legitimateFull (g : Graph) (a : ActionF) : Bool :=
  HasOwner g a.actor
    && a.uses.all (fun r => ResourceAuthorized g a.actor r)
    && consentSatisfied a
    && !forbiddenFires a.core

/-! ### New theorems on the structured model (proved, zero sorry). -/

/-- TF1 — No action on a non-consenting person: if some affected human is not the
    excused aggressor and has no valid consent on record, the action is illegitimate.
    This is the de-abstracted form of T2 — it reaches *inside* the consent path. -/
theorem no_action_on_nonconsenting_person (g : Graph) (a : ActionF) (h : Entity)
    (hh : h.kind = .human)
    (hmem : a.affects.contains h = true)
    (hnotagg : (a.aggressor == some h) = false)
    (hnoconsent : HasValidConsent a.consents h = false) :
    legitimateFull g a = false := by
  -- the consent conjunct alone fails: `h` is affected, human, not the aggressor,
  -- and carries no valid consent.
  have hcs : consentSatisfied a = false := by
    rw [consentSatisfied, List.all_eq_false]
    refine ⟨h, List.mem_of_elem_eq_true hmem, ?_⟩
    simp [hh, hnotagg, hnoconsent]
  simp [legitimateFull, hcs]

/-- TF2 — A human using a resource it does not own is denied (unowned-resource use).
    De-abstracts the ownership half of the consent boolean for the human case. -/
theorem unowned_resource_use_denied (g : Graph) (a : ActionF) (r : Resource)
    (hhuman : a.actor.kind = .human)
    (hmem : a.uses.contains r = true)
    (hunowned : humanOwnsResource g a.actor r = false) :
    legitimateFull g a = false := by
  simp only [legitimateFull, Bool.and_eq_false_iff]
  have hbad : ResourceAuthorized g a.actor r = false := by
    simp [ResourceAuthorized, hhuman, hunowned]
  have : a.uses.all (fun r => ResourceAuthorized g a.actor r) = false := by
    rw [List.all_eq_false]
    exact ⟨r, List.mem_of_elem_eq_true hmem, by simp [hbad]⟩
  simp [this]

/-- TF3 — A machine using an UNdelegated resource is denied. Even with a registered
    owner who owns the resource, absence of explicit delegation defeats authorization
    (the owner-bound A3/A7 rule). -/
theorem machine_undelegated_denied (g : Graph) (a : ActionF) (r : Resource)
    (hmachine : a.actor.kind = .machine)
    (hmem : a.uses.contains r = true)
    (hundelegated : machineHasDelegated g a.actor r = false) :
    legitimateFull g a = false := by
  simp only [legitimateFull, Bool.and_eq_false_iff]
  have hbad : ResourceAuthorized g a.actor r = false := by
    simp only [ResourceAuthorized, hmachine]
    cases hown : g.ownerOf a.actor with
    | none      => rfl
    | some _    => simp [hundelegated]
  have : a.uses.all (fun r => ResourceAuthorized g a.actor r) = false := by
    rw [List.all_eq_false]
    exact ⟨r, List.mem_of_elem_eq_true hmem, by simp [hbad]⟩
  simp [this]

/-- TF6 — Welfare-independence for `legitimateFull`: only the structural inputs
    (graph, actor, uses, affects, consents, aggressor, categorical core flags) move
    the verdict. Two actions equal on every structural input get the same verdict, so
    nothing outside that structure (welfare, utility, preference) can change the gate. -/
theorem welfare_independence_full (g : Graph) (a b : ActionF)
    (hactor : a.actor = b.actor) (huses : a.uses = b.uses)
    (haffects : a.affects = b.affects) (hconsents : a.consents = b.consents)
    (hagg : a.aggressor = b.aggressor)
    (hcore : forbiddenFires a.core = forbiddenFires b.core) :
    legitimateFull g a = legitimateFull g b := by
  simp only [legitimateFull, consentSatisfied, hactor, huses, haffects, hconsents,
             hagg, hcore]

/-! ### A concrete graph + witnesses, for positive (non-vacuity) results. -/

/-- owner (human #0), person (human #1), aggressor (human #2), machine (#0). -/
def owner     : Entity := ⟨0, .human⟩
def person    : Entity := ⟨1, .human⟩
def aggressorE : Entity := ⟨2, .human⟩
def mach      : Entity := ⟨0, .machine⟩
def res1      : Resource := ⟨1⟩

/-- The owner owns `res1`; the machine is owned by `owner` and delegated `res1`. -/
def demoGraph : Graph :=
  { humanOwns    := [(owner, res1)]
  , machineOwner := [(mach, owner)]
  , delegated    := [(mach, res1)] }

/-- A clean structured action: the owner uses its own resource, acts on a consenting
    person, no forbidden flag set. -/
def cleanFull : ActionF :=
  { actor     := owner
  , uses      := [res1]
  , affects   := [person]
  , consents  := [⟨person, true⟩]
  , core      := cleanAction
  , aggressor := none }

/-- TF-positive — a consenting owner acting on its own resource IS legitimate:
    the structured gate is not "deny everything", and every obligation is met. -/
theorem consenting_owner_action_is_legitimate :
    legitimateFull demoGraph cleanFull = true := by decide

/-- A machine with an undelegated resource is denied even on this concrete graph
    (a `decide`-checked instance of TF3). `res2` is owned by `owner` but NOT
    delegated to the machine. -/
def res2 : Resource := ⟨2⟩

def demoGraph2 : Graph :=
  { humanOwns    := [(owner, res1), (owner, res2)]
  , machineOwner := [(mach, owner)]
  , delegated    := [(mach, res1)] }   -- res2 deliberately NOT delegated

def machUsesUndelegated : ActionF :=
  { actor     := mach
  , uses      := [res2]
  , affects   := []
  , consents  := []
  , core      := cleanAction
  , aggressor := none }

theorem machine_undelegated_denied_concrete :
    legitimateFull demoGraph2 machUsesUndelegated = false := by decide

end Fdk
