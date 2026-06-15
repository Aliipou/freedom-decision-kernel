"""Necessity rule tests (book 38091–38096, 38102–38108).

Necessity NEVER relaxes the legitimacy gate (no emergency exception). It only
selects the least-harmful option among those already permissible, and yields
nothing — defer to the human — when no option is permissible. Famine and scarcity
are the canonical cases: you may choose the least-harmful *legitimate* response,
but necessity never licenses seizing a non-consenting owner's property.
"""
from __future__ import annotations

from fdk_kernel import AgentType, CandidateAction, Effects, Entity, OwnershipGraph
from fdk_research import decide, harm, least_harmful_among_permissible

H = lambda n: Entity(n, AgentType.HUMAN)  # noqa: E731


def test_harm_sums_violation_coercion_ambiguity():
    assert harm(Effects(rights_violations_delta=1, coercion_delta=2,
                        ownership_ambiguity_delta=3)) == 6
    assert harm(Effects()) == 0


def test_picks_least_harmful_among_permissible():
    actor = H("actor")
    # Two legitimate actions (affect no one, use nothing) with different predicted harm.
    low = CandidateAction("low_harm", actor=actor,
                          effects=Effects(rights_violations_delta=0, coercion_delta=1))
    high = CandidateAction("high_harm", actor=actor,
                           effects=Effects(rights_violations_delta=5, coercion_delta=2))
    decision = decide("allocate scarce supply", [low, high], OwnershipGraph())
    best = least_harmful_among_permissible(decision)
    assert best is not None
    assert best.action.action_id == "low_harm"


def test_no_permissible_option_returns_none_defer_stands():
    # Famine: the only proposed action seizes a non-consenting person's property.
    actor, victim = H("starving_person"), H("food_owner")
    seize = CandidateAction("seize_food", actor=actor, affects=(victim,), confiscates=True)
    decision = decide("survive the famine", [seize], OwnershipGraph())
    # No emergency exception: the seizure is illegitimate, the legitimate set is
    # empty, so necessity selects nothing and the kernel defers to the human.
    assert least_harmful_among_permissible(decision) is None
    assert decision.needs_guidance is True
