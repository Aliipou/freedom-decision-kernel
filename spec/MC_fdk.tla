-------------------------------- MODULE MC_fdk --------------------------------
(***************************************************************************)
(* A small finite instance of `fdk` for the TLC model checker. It picks    *)
(* concrete CONSTANTS and a constructively-built, finite `Actions` set     *)
(* (two tiers: base actions with no defense, and defense actions that      *)
(* point at a base action), then re-exports fdk's Spec + safety invariants *)
(* so `MC_fdk.cfg` can model-check them. Tiny on purpose — the safety       *)
(* properties are universally quantified over a constant set, so a small    *)
(* representative instance exercises every structural branch.              *)
(***************************************************************************)
EXTENDS FiniteSets, TLC

H  == {"h1"}
M  == {"m1"}
R  == {"r1"}
NA == [id |-> "none"]
OW == { <<"h1", "r1">> }
DEL == { <<"m1", "r1">> }
MO == [ m \in M |-> "h1" ]
Ent == H \cup M

\* A small slice of the forbidden flags: one defense-excusable (coerces), one
\* exit-removal (excusable), and two purely categorical (sovereignty, confiscation).
Flags == { "coerces", "removes_exit_right", "machine_sovereignty", "confiscates" }

\* Tier 1 — base actions: no defense, no resource use, no one affected (so consent
\* is not in play and Legitimate(base) <=> forbidden = {}).
BaseActions ==
    { [ id            |-> "base",
        actor         |-> act,
        uses          |-> {},
        affects       |-> {},
        consents      |-> {},
        forbidden     |-> fset,
        defendsAgainst|-> NA,
        proportionate |-> TRUE ]
      : act \in Ent, fset \in SUBSET Flags }

\* An illegitimate aggressor to defend against (coerces, no defense -> illegitimate).
Aggressor ==
    [ id |-> "aggressor", actor |-> "h1", uses |-> {}, affects |-> {},
      consents |-> {}, forbidden |-> {"coerces"}, defendsAgainst |-> NA,
      proportionate |-> TRUE ]

\* Tier 2 — defense actions: point at the (illegitimate) aggressor, carry only
\* excusable flags, aim only at the aggressor's actor, vary proportionality.
DefenseActions ==
    { [ id            |-> "def",
        actor         |-> "h1",
        uses          |-> {},
        affects       |-> { Aggressor.actor },
        consents      |-> {},
        forbidden     |-> fset,
        defendsAgainst|-> Aggressor,
        proportionate |-> prop ]
      : fset \in SUBSET {"coerces", "removes_exit_right"}, prop \in BOOLEAN }

ALL == BaseActions \cup {Aggressor} \cup DefenseActions

VARIABLE chosen

F == INSTANCE fdk WITH
        Humans <- H, Machines <- M, Resources <- R, Actions <- ALL,
        Owns <- OW, Delegated <- DEL, MachineOwner <- MO, NoAction <- NA,
        chosen <- chosen

\* Re-export for the .cfg.
Spec == F!Spec
Safety == F!Safety
NoLegitimateSlavery == F!NoLegitimateSlavery
NoMachineSovereignty == F!NoMachineSovereignty
NoLaunderingViaResistance == F!NoLaunderingViaResistance
TypeOK == F!TypeOK
=============================================================================
