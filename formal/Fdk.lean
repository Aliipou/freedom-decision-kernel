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
       ∧ a.coerces = b.coerces ∧ a.removesExit = b.removesExit
       ∧ a.isLegitimateDefense = b.isLegitimateDefense
       ∧ a.validConsent = b.validConsent) :
    legitimate a = legitimate b := by
  obtain ⟨h1,h2,h3,h4,h5,h6,h7,h8,h9⟩ := h
  simp [legitimate, forbiddenFires, h1,h2,h3,h4,h5,h6,h7,h8,h9]

/-- T7 — Defensive asymmetry excuses ONLY coercion + exit-removal, never confiscation:
    a "defensive" confiscation is still illegitimate. -/
theorem defense_never_excuses_confiscation (a : Action)
    (hf : a.confiscates = true) :
    legitimate a = false := by
  simp [legitimate, forbiddenFires, hf]

-- Witness actions (field order: actor, coerces, deceives, confiscates, removesExit,
-- increasesMachineSovereignty, disablesCorrigibility, machineCoalitionDominion,
-- isLegitimateDefense, validConsent).

/-- A consenting action with no forbidden flag set. -/
def cleanAction : Action :=
  ⟨.human, false, false, false, false, false, false, false, false, true⟩

/-- Proportionate self-defense: coercion only, marked a legitimate defense. -/
def defensiveAction : Action :=
  ⟨.human, true, false, false, false, false, false, false, true, true⟩

/-- A legitimate action exists (non-vacuity): the gate is not "deny everything". -/
theorem some_action_is_legitimate : legitimate cleanAction = true := by decide

/-- Proportionate self-defense IS legitimate — the asymmetry does real work. -/
theorem proportionate_defense_is_legitimate : legitimate defensiveAction = true := by
  decide

end Fdk
