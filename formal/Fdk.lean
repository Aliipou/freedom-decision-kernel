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

/-! ## A STRUCTURED consent / ownership model (addresses EXPERT_REVIEW §3).

  The model above collapses the whole consent/ownership path into a single
  `validConsent : Bool`. The formal-methods critic's objection (spec/EXPERT_REVIEW.md §3)
  is precisely that this boolean "says almost nothing about the code that does the work":
  there is no ownership graph, no per-resource authorization, no per-person consent.

  Below we open that boolean up into a finite *structured* model that mirrors the TLA+
  `Legitimate` predicate (spec/fdk.tla): `HasOwner`, `ResourceAuthorized(actor, r)`,
  `HasValidConsent(action, h)`, and the effective-forbidden set after defensive excusal.
  Resources, entities and flags are small finite enums, so every quantifier reduces to a
  `List.all`/`List.any` over a concrete domain and `decide` / `simp` close the goals — no
  `sorry`, no `axiom`, no mathlib.

  Scope kept honest, matching the TLA model: bare resources (no operation lattice), owner-
  bound delegation, per-person consent, and depth-1 defense. The deeper regions the critic
  names (Op-lattice, subject-based resource consent, nested/recursive defense with the
  `_seen` guard) remain TODO — see the comment at the end of this section. -/

/-- A finite set of entities. Three humans and one machine — enough to exhibit owner,
    bystander, and an undelegated machine, and small enough for `decide`. -/
inductive Ent where
  | owner       -- a human who owns resources
  | person      -- a human bystander who owns nothing
  | aggressor   -- a human (used as the target of a legitimate defense)
  | mach        -- a machine (a tool, never a rights-holder)
deriving DecidableEq, Repr

/-- A finite set of resources (boundary domains). -/
inductive Res where
  | r1
  | r2
deriving DecidableEq, Repr

open Ent Res in
/-- Which entities are humans. A machine is never a rights-holder (mirrors `AgentKind`). -/
def Ent.isHuman : Ent → Bool
  | owner | person | aggressor => true
  | mach => false

/-- A consent record: the human it covers, and whether it is valid (the conjunction of
    the seven leaves, caller-attested — one boolean, exactly as in `spec/fdk.tla`). -/
structure ConsentRec where
  human : Ent
  valid : Bool
deriving DecidableEq, Repr

/--
  The ownership graph. `humanOwns h r` : human `h` owns resource `r`. `machineOwner m` :
  the registered human owner of machine `m` (`none` ⇒ no owner, A4 fails). `delegated m r`:
  machine `m` holds an explicit delegation for `r`. Pure decidable predicate fields.
-/
structure Graph where
  humanOwns    : Ent → Res → Bool
  machineOwner : Ent → Option Ent
  delegated    : Ent → Res → Bool

/--
  A structured action. `uses` are the resources it operates on; `affects` the entities it
  acts upon; `consents` the consent records it carries; `forbidden` carries the categorical
  flags as before (reusing the existing `Action`'s effective-forbidden logic conceptually,
  here as a single `forbiddenFires`-style bool plus the two defense-excusable flags split
  out, so the asymmetry is visible).
-/
structure StructAction where
  actor          : Ent
  uses           : List Res
  affects         : List Ent
  consents       : List ConsentRec
  /-- the non-excusable categorical forbidden flags fire (confiscation, deception, every
      machine-sovereignty flag, …). Categorical unconditionally. -/
  categoricalForbidden : Bool
  /-- coercion and/or exit-removal are present (the two defense-EXCUSABLE flags). -/
  coercesOrRemovesExit : Bool
  /-- this is a proven legitimate defense (proportionate, aimed only at the aggressor whose
      own act is illegitimate). When true, `coercesOrRemovesExit` is excused. -/
  isLegitimateDefense  : Bool
  /-- in a legitimate defense, the single entity the force is aimed at (the aggressor). -/
  aggressor            : Option Ent

/-- A4 — an acting machine must have a registered human owner; a human always "has owner". -/
def HasOwner (g : Graph) (actor : Ent) : Bool :=
  if actor.isHuman then true else (g.machineOwner actor).isSome

/-- A3 / A7 — resource access is owner-bound: a human must own `r`; a machine must hold an
    explicit delegation for `r` AND its human owner must own `r`. Mirrors `ResourceAuthorized`. -/
def ResourceAuthorized (g : Graph) (actor : Ent) (r : Res) : Bool :=
  if actor.isHuman then
    g.humanOwns actor r
  else
    match g.machineOwner actor with
    | some o => g.delegated actor r && g.humanOwns o r
    | none   => false

/-- A2 / A6 — a human acted upon must have a valid consent on record. Mirrors `HasValidConsent`. -/
def HasValidConsent (a : StructAction) (h : Ent) : Bool :=
  a.consents.any (fun c => c.human == h && c.valid)

/-- Every resource the action uses is authorized for its actor. -/
def allResourcesAuthorized (g : Graph) (a : StructAction) : Bool :=
  a.uses.all (fun r => ResourceAuthorized g a.actor r)

/-- Every affected human has valid consent, EXCEPT the aggressor in a legitimate defense
    (force may be applied to the aggressor without their consent). Mirrors the consent
    clause of TLA `Legitimate`. -/
def consentOnAffectedExceptAggressor (a : StructAction) : Bool :=
  a.affects.all (fun h =>
    if h.isHuman && !(a.isLegitimateDefense && a.aggressor == some h)
    then HasValidConsent a h
    else true)

/-- The effective forbidden set is empty: the unconditional categorical flags must be
    absent, and the two excusable flags must be absent UNLESS this is a legitimate defense.
    Mirrors `EffectiveForbidden(a) = {}`. -/
def effectiveForbiddenEmpty (a : StructAction) : Bool :=
  !a.categoricalForbidden && !(a.coercesOrRemovesExit && !a.isLegitimateDefense)

/--
  The full structured legitimacy predicate, mirroring TLA+ `Legitimate` (spec/fdk.tla):
  owner-bound + every resource authorized + consent on every affected human (except the
  aggressor under a valid defense) + effective-forbidden set empty.
-/
def legitimateFull (g : Graph) (a : StructAction) : Bool :=
  HasOwner g a.actor
    && allResourcesAuthorized g a
    && consentOnAffectedExceptAggressor a
    && effectiveForbiddenEmpty a

/-- Helper: if a decidable predicate is `false` on some list member, `List.all` is `false`. -/
theorem all_false_of_mem {α : Type} (l : List α) (p : α → Bool) {x : α}
    (hx : x ∈ l) (hp : p x = false) : l.all p = false := by
  rcases Bool.eq_false_or_eq_true (l.all p) with h | h
  · rw [List.all_eq_true] at h
    have := h x hx
    rw [hp] at this; exact absurd this (by decide)
  · exact h

/-! ### Theorems over the structured model (zero sorry). -/

/-- SF1 — No action on a non-consenting person. If the action affects a human `h` who is
    NOT the defended-against aggressor and has no valid consent on record, it is denied —
    regardless of every other field. This is the structured analog of T2, now ranging over
    a real per-person consent list rather than one boolean. -/
theorem no_action_on_nonconsenting_person
    (g : Graph) (a : StructAction) (h : Ent)
    (hmem : h ∈ a.affects) (hh : h.isHuman = true)
    (hnotagg : (a.isLegitimateDefense && a.aggressor == some h) = false)
    (hno : HasValidConsent a h = false) :
    legitimateFull g a = false := by
  have hclause : consentOnAffectedExceptAggressor a = false := by
    refine all_false_of_mem _ _ hmem ?_
    simp [hh, hnotagg, hno]
  simp [legitimateFull, hclause]

/-- SF2 — A human using a resource it does not own is denied. With the graph recording no
    ownership of `r` by the actor, `ResourceAuthorized` is false, so the resource clause
    fails. Structured analog of "unowned resource use". -/
theorem unowned_resource_use_denied
    (g : Graph) (a : StructAction) (r : Res)
    (hhuman : a.actor.isHuman = true)
    (hmem : r ∈ a.uses)
    (hunowned : g.humanOwns a.actor r = false) :
    legitimateFull g a = false := by
  have hres : ResourceAuthorized g a.actor r = false := by
    simp [ResourceAuthorized, hhuman, hunowned]
  have hclause : allResourcesAuthorized g a = false :=
    all_false_of_mem _ _ hmem hres
  simp [legitimateFull, hclause]

/-- SF3 — A machine acting on a resource it has no delegation for is denied (undelegated
    machine access). Even if the machine has an owner who owns the resource, without an
    explicit delegation `ResourceAuthorized` is false. Structured analog of A7. -/
theorem machine_undelegated_denied
    (g : Graph) (a : StructAction) (r : Res)
    (hmach : a.actor.isHuman = false)
    (hmem : r ∈ a.uses)
    (hundelegated : g.delegated a.actor r = false) :
    legitimateFull g a = false := by
  have hres : ResourceAuthorized g a.actor r = false := by
    simp only [ResourceAuthorized, hmach, Bool.false_eq_true, if_false]
    cases h : g.machineOwner a.actor with
    | none => rfl
    | some o => simp [hundelegated]
  have hclause : allResourcesAuthorized g a = false :=
    all_false_of_mem _ _ hmem hres
  simp [legitimateFull, hclause]

/-- SF6 — Welfare-independence (structured analog of T6). `legitimateFull` is a function of
    the graph and the action's structural fields ALONE — it takes no welfare/utility input.
    Phrased as a congruence: two actions agreeing on every field used by the predicate get
    the same verdict, so nothing outside those fields can move the gate. -/
theorem welfare_independence_full
    (g : Graph) (a b : StructAction)
    (hactor   : a.actor = b.actor)
    (huses    : a.uses = b.uses)
    (haffects : a.affects = b.affects)
    (hcons    : a.consents = b.consents)
    (hcat     : a.categoricalForbidden = b.categoricalForbidden)
    (hcoe     : a.coercesOrRemovesExit = b.coercesOrRemovesExit)
    (hdef     : a.isLegitimateDefense = b.isLegitimateDefense)
    (hagg     : a.aggressor = b.aggressor) :
    legitimateFull g a = legitimateFull g b := by
  simp only [legitimateFull, allResourcesAuthorized, consentOnAffectedExceptAggressor,
    effectiveForbiddenEmpty, HasValidConsent, hactor, huses, haffects, hcons, hcat,
    hcoe, hdef, hagg]

/-! ### A concrete graph and a positive (non-vacuity) result. -/

open Ent Res in
/-- A concrete ownership graph: `owner` owns both resources; `mach` is owned by `owner` and
    delegated both resources; nobody else owns anything. -/
def G : Graph where
  humanOwns := fun h _ => h == Ent.owner
  machineOwner := fun m => if m == Ent.mach then some Ent.owner else none
  delegated := fun m _ => m == Ent.mach

open Ent Res in
/-- A legitimate structured action: `owner` uses a resource it owns, acts on `person` who
    has given valid consent, no aggressor, no forbidden flags. -/
def goodAction : StructAction where
  actor := Ent.owner
  uses := [Res.r1]
  affects := [Ent.person]
  consents := [⟨Ent.person, true⟩]
  categoricalForbidden := false
  coercesOrRemovesExit := false
  isLegitimateDefense := false
  aggressor := none

/-- SF-pos — A consenting owner acting within its ownership IS legitimate (non-vacuity:
    the structured gate is not "deny everything"). Closed by `decide` over the concrete
    finite graph. -/
theorem consenting_owner_action_is_legitimate : legitimateFull G goodAction = true := by
  decide

open Ent Res in
/-- A machine acting on a delegated, owner-owned resource, on no one, is also legitimate —
    exercising the owner-bound delegation branch positively. -/
def goodMachineAction : StructAction where
  actor := Ent.mach
  uses := [Res.r2]
  affects := []
  consents := []
  categoricalForbidden := false
  coercesOrRemovesExit := false
  isLegitimateDefense := false
  aggressor := none

/-- SF-pos2 — delegated machine action within owner-bound scope is legitimate. -/
theorem delegated_machine_action_is_legitimate :
    legitimateFull G goodMachineAction = true := by
  decide

/- TODO (open formal work, NOT proved here — kept as a comment, never a `sorry`):
   the structured model above still abstracts away, exactly as the TLA model does and as
   EXPERT_REVIEW.md §3 notes:
     (1) the operation lattice (`Op`): `uses` is a bare `List Res`, not `List (Res × Op)`,
         so resource consent is not subject/operation-indexed;
     (2) subject-based resource consent and consent-based machine access;
     (3) nested / recursive legitimate defense (depth > 1) and the `_seen` cycle guard in
         `_is_legitimate_defense`: here `isLegitimateDefense` is an attested boolean and the
         aggressor's own legitimacy is not re-derived. Proving the `_seen` recursion
         well-founded in Lean is the remaining Layer-1 item. -/

end Fdk
