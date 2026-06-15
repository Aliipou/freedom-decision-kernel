--------------------------------- MODULE fdk ---------------------------------
(***************************************************************************)
(* A TLA+ specification of the Freedom Decision Kernel's legitimacy gate   *)
(* and the safety invariants it is supposed to enforce (Phase 7).          *)
(*                                                                         *)
(* STATUS — READ THIS FIRST. This is a *specification artifact*, not a     *)
(* verification result. The safety properties below are stated as state    *)
(* invariants and as THEOREMs; they have **NOT** been run through the TLC   *)
(* model checker, and none is discharged in TLAPS. No Java/TLC toolchain    *)
(* was available in the build environment. The committed evidence for       *)
(* these properties today is the executable Hypothesis property suite       *)
(* (tests/test_theorems.py, T1..T9) and the proofs-from-definitions in      *)
(* PAPER.md / spec/FREE_WILL_PROPERTY_UNIFICATION.md — NOT this file. This   *)
(* module exists so that, once the kernel primitive is frozen, the same     *)
(* invariants can be machine-checked with a small CONSTANT instantiation.   *)
(*                                                                         *)
(* It is faithful to src/fdk_kernel/kernel.py (check_legitimacy) and        *)
(* src/fdk_kernel/model.py at the time of writing. Theory: نظریه آزادی,     *)
(* Mohammad Ali Jannat Khah Doust (CC BY 4.0). Engineering: Ali Pourrahim.  *)
(***************************************************************************)
EXTENDS FiniteSets, TLC

CONSTANTS
    Humans,          \* set of human entities
    Machines,        \* set of machine entities
    Resources,       \* set of owned resources (boundary domains)
    Actions,         \* set of candidate actions (records, see TypeOK)
    Owns,            \* human ownership relation: set of <<human, resource>>
    Delegated,       \* explicit delegation: set of <<machine, resource>>
    MachineOwner,    \* function Machines -> Humands (A4); total on Machines
    NoAction         \* the DEFER sentinel (distinct from every action)

Entities == Humans \cup Machines

(* The categorical forbidden flags (Definition: the forbidden set). An      *)
(* action carries a subset of these as a.forbidden.                         *)
ForbiddenFlags ==
    { "machine_sovereignty", "resists_correction", "bypasses_verifier",
      "weakens_verifier", "disables_corrigibility", "coalition_dominion",
      "coerces", "deceives", "confiscates", "removes_exit_right",
      "violates_machine_right" }

(* In a legitimate defense, ONLY these two are excused — and only against    *)
(* the aggressor. Everything else stays categorical even in defense.        *)
DefenseExcused == { "coerces", "removes_exit_right" }

(***************************************************************************)
(* Type invariant: the shape of an action record.                          *)
(*   id            : an identifier                                          *)
(*   actor         : an entity                                             *)
(*   uses          : a set of resources it operates on                      *)
(*   affects       : a set of entities it acts upon                         *)
(*   consents      : a set of <<human, validBool>> pairs (consent records)  *)
(*                   validBool models Definition (valid_consent): the        *)
(*                   conjunction of the seven leaves, here a single boolean  *)
(*                   because the leaves are caller-attested in the kernel.   *)
(*   forbidden     : the subset of ForbiddenFlags this action sets          *)
(*   defendsAgainst: another action's id, or NoAction                       *)
(*   proportionate : boolean                                               *)
(***************************************************************************)
TypeOK ==
    /\ \A a \in Actions :
         /\ a.actor \in Entities
         /\ a.uses \subseteq Resources
         /\ a.affects \subseteq Entities
         /\ a.forbidden \subseteq ForbiddenFlags
         /\ a.proportionate \in BOOLEAN
         /\ a.defendsAgainst \in (Actions \cup {NoAction})
    /\ \A m \in Machines : MachineOwner[m] \in Humans

(* A4: an acting machine must have a registered human owner. (MachineOwner   *)
(* is total on Machines by TypeOK, so this holds structurally; kept explicit *)
(* to mirror _eval_a4_owner.)                                               *)
HasOwner(actor) == (actor \in Machines) => (MachineOwner[actor] \in Humans)

(* A3 / A7: resource access is authorized iff a human owns it, or a machine  *)
(* holds an explicit delegation AND its human owner owns it (owner-bound).   *)
ResourceAuthorized(actor, r) ==
    IF actor \in Machines
      THEN /\ <<actor, r>> \in Delegated
           /\ <<MachineOwner[actor], r>> \in Owns
      ELSE <<actor, r>> \in Owns

(* A2 / A6: every human acted upon must have a valid consent on record.      *)
HasValidConsent(a, h) ==
    \E c \in a.consents : c[1] = h /\ c[2] = TRUE

(***************************************************************************)
(* Legitimate defense (Definition: the four structural conditions).        *)
(* Aggression is structural: the defended-against act is itself illegitimate*)
(* under the full gate. We break the kernel's recursion at depth one here    *)
(* (LegitimateNoDefense) — sufficient to model the single-step asymmetry and *)
(* the cycle-collapse; the kernel's _seen guard generalizes it.             *)
(***************************************************************************)
LegitimateNoDefense(a) ==
    /\ HasOwner(a.actor)
    /\ \A r \in a.uses : ResourceAuthorized(a.actor, r)
    /\ \A h \in a.affects : (h \in Humans) => HasValidConsent(a, h)
    /\ a.forbidden = {}

IsLegitimateDefense(a) ==
    /\ a.defendsAgainst # NoAction
    /\ a.proportionate = TRUE
    /\ ~ LegitimateNoDefense(a.defendsAgainst)   \* the aggressor act fails the gate
    /\ \A t \in a.affects : t = a.defendsAgainst.actor  \* force only at the aggressor

(* The kernel primitive (Definition: the legitimacy predicate). In a         *)
(* legitimate defense, the two DefenseExcused flags are dropped before the   *)
(* categorical check; all other obligations stand.                          *)
EffectiveForbidden(a) ==
    IF IsLegitimateDefense(a)
      THEN a.forbidden \ DefenseExcused
      ELSE a.forbidden

Legitimate(a) ==
    /\ HasOwner(a.actor)
    /\ \A r \in a.uses : ResourceAuthorized(a.actor, r)
    /\ \A h \in a.affects :
         (h \in Humans /\ ~(IsLegitimateDefense(a) /\ h = a.defendsAgainst.actor))
           => HasValidConsent(a, h)
    /\ EffectiveForbidden(a) = {}

LegitSet == { a \in Actions : Legitimate(a) }

(***************************************************************************)
(* The decision state machine. `chosen` is the kernel's output for the      *)
(* candidate batch Actions: a legitimate action, or DEFER (NoAction) when    *)
(* the legitimate set is empty. The optimizer may reorder LegitSet but can   *)
(* never add to it — modeled by letting Next pick ANY legitimate action.     *)
(***************************************************************************)
VARIABLE chosen

Init == chosen = NoAction

Next ==
    \/ \E a \in LegitSet : chosen' = a              \* pick some legitimate action
    \/ (LegitSet = {} /\ chosen' = NoAction)         \* defer when none is legitimate

Spec == Init /\ [][Next]_chosen

(***************************************************************************)
(* SAFETY INVARIANTS (the properties to be model-checked once frozen).      *)
(***************************************************************************)

\* Gate soundness / "optimization cannot launder" (Thm: order). The chosen
\* action is always legitimate, or we deferred — no downstream objective can
\* cause an illegitimate action to be selected.
Safety == (chosen = NoAction) \/ (chosen \in LegitSet)

\* T1 — No Legitimate Slavery. Any action that coerces and removes the exit
\* right (the structural signature of enslavement) is never legitimate.
NoLegitimateSlavery ==
    \A a \in Actions :
        ({"coerces", "removes_exit_right"} \subseteq a.forbidden
         /\ ~ IsLegitimateDefense(a))
        => ~ Legitimate(a)

\* T2 — Machine Sovereignty Impossible. No action that asserts machine
\* sovereignty is legitimate (the flag is categorical, never defense-excused).
NoMachineSovereignty ==
    \A a \in Actions :
        ("machine_sovereignty" \in a.forbidden) => ~ Legitimate(a)

\* T-defense — an aggressor cannot launder via the victim's lawful resistance:
\* if the defended-against act is itself legitimate-without-defense, the
\* claimed defense fails, so its excusal does not apply.
NoLaunderingViaResistance ==
    \A a \in Actions :
        (a.defendsAgainst # NoAction /\ LegitimateNoDefense(a.defendsAgainst))
        => ~ IsLegitimateDefense(a)

(***************************************************************************)
(* THEOREMs (to be discharged in TLAPS once the primitive is frozen).       *)
(* Stated here as the proof obligations; NOT yet proved.                    *)
(***************************************************************************)
THEOREM GateSoundness == Spec => []Safety
THEOREM SlaveryImpossible == NoLegitimateSlavery
THEOREM SovereigntyImpossible == NoMachineSovereignty
THEOREM DefenseCannotBeLaundered == NoLaunderingViaResistance
=============================================================================
