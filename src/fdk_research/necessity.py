"""Necessity rule (research layer) — book 38091–38096, 38102–38108.

The Theory of Freedom admits NO emergency exception: "there are no emergency
exceptions … No emergency suspends axioms … Necessity only limits the choice among
permissible options; it does not make the violation of rights permissible"
(book 38091–38096). So an emergency NEVER relaxes the legitimacy gate — that stays
in `fdk_kernel`, untouched.

Necessity operates only as a SELECTION rule over the already-permissible set, exactly
as the book's clause:

    permissible_under_emergency(A, E) :-
        emergency(E), permissible(A), least_harmful_among_permissible(A, E).   (38102–38108)

Two kinds of "emergency" must not be confused:

* An emergency that is itself an ongoing rights-violation — a robbery in progress,
  an invasion, a profiteer manufacturing scarcity to coerce (book 34721) — is
  AGGRESSION. It is handled by the kernel's aggressor/defender asymmetry: acting to
  SAVE property rights against that aggressor is legitimate (see CONFLICT_LOGIC.md).
* A natural emergency with no aggressor (fire, pandemic) gets no exception. If no
  option is permissible, this returns None and the kernel's defer-to-human stands —
  necessity confers no licence to cross a non-aggressor's boundary.
"""
from __future__ import annotations

from fdk_kernel.model import Decision, Effects, ScoredAction


def harm(effects: Effects) -> int:
    """Predicted harm of an action: rights violated + coercion exerted + ownership
    ambiguity introduced. Lower is less harmful. (Deltas are after − before.)"""
    return (
        effects.rights_violations_delta
        + effects.coercion_delta
        + effects.ownership_ambiguity_delta
    )


def least_harmful_among_permissible(decision: Decision) -> ScoredAction | None:
    """Book 38102–38108: among the PERMISSIBLE options, the least harmful.

    Operates only on `decision.ranked` (the legitimate set the kernel already
    passed). Returns None when that set is empty — necessity grants no exception,
    so the kernel's `needs_guidance` defer is the final word. This never makes an
    illegitimate action permissible (38095); it only chooses among legitimate ones.
    """
    if not decision.ranked:
        return None
    return min(decision.ranked, key=lambda s: harm(s.action.effects))
