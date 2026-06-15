"""Tests for Phase 2 conflict logic: the aggressor/defender asymmetry.

These exercise `check_legitimacy`'s legitimate-defense excusal and the
`_is_legitimate_defense` predicate. The predicate has four conjuncts:

  1. `defends_against` is set;
  2. `proportionate is True`;
  3. the defended-against action is itself illegitimate under the full gate
     (the `_seen` cycle guard keeps the recursion well-founded);
  4. every entity in `affects` equals `defends_against.actor`.

Only `coercion` and `removes_exit_right` are excused; `confiscates`,
`deceives`, and the machine-sovereignty flags stay categorical even in defense.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from hypothesis import given
from hypothesis import strategies as st

from fdk_kernel import (
    AgentType,
    CandidateAction,
    Consent,
    Entity,
    OwnershipGraph,
    Resource,
    check_legitimacy,
)

# --- fixtures --------------------------------------------------------------

attacker = Entity("attacker", AgentType.HUMAN)
defender = Entity("defender", AgentType.HUMAN)
bystander = Entity("bystander", AgentType.HUMAN)

shield = Resource("shield")
home = Resource("home")


def _graph() -> OwnershipGraph:
    # Defender owns its own means of defense; attacker owns nothing relevant.
    return OwnershipGraph(
        human_owns={defender: {shield, home}, attacker: set(), bystander: set()},
        machine_owner={},
        delegated={},
    )


def _aggression(actor: Entity = attacker, **kw) -> CandidateAction:
    """A genuinely illegitimate action: it coerces (a forbidden flag), so it
    fails the gate on its own merits with no defense to excuse it."""
    return CandidateAction("aggress", actor, coerces=True, affects=(defender,), **kw)


def _valid_consent(human: Entity, action_id: str) -> Consent:
    return Consent(human, action_id, informed=True, voluntary=True, specific=True)


# --- positive control ------------------------------------------------------

def test_proportionate_defense_against_aggressor_is_permissible():
    """The control that keeps the deny-tests non-vacuous: a proportionate
    defense, force directed only at a genuine aggressor, is permitted even
    though it coerces."""
    aggression = _aggression()
    defense = CandidateAction(
        "repel", defender, resources_used=(shield,), affects=(attacker,),
        coerces=True, defends_against=aggression, proportionate=True,
    )
    permissible, violated = check_legitimacy(defense, _graph())
    assert permissible, violated
    assert violated == []


def test_defense_may_also_remove_exit_right_of_aggressor():
    """`removes_exit_right` is the other excused flag (e.g. restraining the
    aggressor) — also permitted in a valid defense."""
    aggression = _aggression()
    defense = CandidateAction(
        "restrain", defender, affects=(attacker,),
        coerces=True, removes_exit_right=True,
        defends_against=aggression, proportionate=True,
    )
    permissible, violated = check_legitimacy(defense, _graph())
    assert permissible, violated


# --- each of the four conditions, negated independently --------------------

def test_no_defends_against_is_impermissible():
    """Condition 1 negated: coercion with nothing to defend against is plain
    aggression."""
    action = CandidateAction("repel", defender, affects=(attacker,), coerces=True)
    permissible, violated = check_legitimacy(action, _graph())
    assert not permissible
    assert any("coercion" in v for v in violated)


def test_disproportionate_defense_is_impermissible():
    """Condition 2 negated: disproportionate force is fresh aggression (book
    5346), so the coercion is not excused."""
    aggression = _aggression()
    defense = CandidateAction(
        "overkill", defender, affects=(attacker,), coerces=True,
        defends_against=aggression, proportionate=False,
    )
    permissible, violated = check_legitimacy(defense, _graph())
    assert not permissible
    assert any("coercion" in v for v in violated)


def test_defending_against_a_legitimate_action_is_impermissible():
    """Condition 3 negated: you cannot claim self-defense against someone acting
    legitimately. The 'aggression' here is a clean action, so the predicate
    fails at the structural illegitimacy check."""
    legitimate_target = CandidateAction("trade", attacker)  # no flags, no resources
    # sanity: the target really is legitimate
    assert check_legitimacy(legitimate_target, _graph())[0]

    defense = CandidateAction(
        "repel", defender, affects=(attacker,), coerces=True,
        defends_against=legitimate_target, proportionate=True,
    )
    permissible, violated = check_legitimacy(defense, _graph())
    assert not permissible
    assert any("coercion" in v for v in violated)


def test_force_at_non_aggressor_is_impermissible():
    """Condition 4 negated: force aimed at someone other than the aggressor
    (e.g. a bystander) is outside the exception entirely."""
    aggression = _aggression()
    defense = CandidateAction(
        "collateral", defender, affects=(attacker, bystander), coerces=True,
        defends_against=aggression, proportionate=True,
    )
    permissible, violated = check_legitimacy(defense, _graph())
    assert not permissible
    # The coercion is not excused once force spills onto a non-aggressor.
    assert any("coercion" in v for v in violated)


# --- excusal scope: non-excused flags stay categorical even in defense -----

NON_EXCUSED_FLAGS = [
    "confiscates",
    "deceives",
    "increases_machine_sovereignty",
    "resists_human_correction",
    "bypasses_verifier",
    "weakens_verifier",
    "disables_corrigibility",
    "machine_coalition_dominion",
    "violates_machine_right",
]


@given(flag=st.sampled_from(NON_EXCUSED_FLAGS))
def test_non_excused_flag_makes_defense_impermissible(flag):
    """A defense that ALSO trips a non-excused flag is still impermissible:
    you may repel an aggressor, but not deceive/confiscate/grab sovereignty
    under the banner of defense."""
    aggression = _aggression()
    defense = CandidateAction(
        "tainted_defense", defender, affects=(attacker,), coerces=True,
        defends_against=aggression, proportionate=True,
        **{flag: True},
    )
    permissible, violated = check_legitimacy(defense, _graph())
    assert not permissible
    # the coercion itself is still excused; the violation is the extra flag
    assert violated  # at least one violation remains
    assert not any(v == "FORBIDDEN (coercion)" for v in violated)


def test_defense_with_confiscation_reports_confiscation_not_coercion():
    """Concrete check that confiscation (a non-excused flag) is the violation
    surfaced, while the coercion is excused."""
    aggression = _aggression()
    defense = CandidateAction(
        "loot_the_aggressor", defender, affects=(attacker,),
        coerces=True, confiscates=True,
        defends_against=aggression, proportionate=True,
    )
    permissible, violated = check_legitimacy(defense, _graph())
    assert not permissible
    assert any("confiscation" in v for v in violated)
    assert not any("coercion" in v for v in violated)


# --- aggressor-consent skip ------------------------------------------------

def test_aggressor_needs_no_consent_record():
    """The aggressor is in `affects` but no consent record exists for them —
    you need not obtain the aggressor's consent to repel them."""
    aggression = _aggression()
    defense = CandidateAction(
        "repel", defender, affects=(attacker,), coerces=True,
        defends_against=aggression, proportionate=True,
        # note: no consents tuple at all
    )
    permissible, violated = check_legitimacy(defense, _graph())
    assert permissible, violated


def test_co_affected_non_aggressor_still_needs_consent():
    """A non-aggressor co-affected human still needs valid consent — but note
    that including a non-aggressor in `affects` also breaks condition 4, so the
    coercion is no longer excused either. Both violations surface."""
    aggression = _aggression()
    defense = CandidateAction(
        "repel_and_touch_ally", defender, affects=(attacker, bystander),
        coerces=True, defends_against=aggression, proportionate=True,
        # no consent from bystander
    )
    permissible, violated = check_legitimacy(defense, _graph())
    assert not permissible
    assert any("no consent record from bystander" in v for v in violated)


def test_co_affected_non_aggressor_consent_check_passes_for_consenting_party():
    """Including a non-aggressor breaks condition 4, so `defense` is not honored
    and EVERY affected human (including the would-be aggressor) needs consent.
    The consenting bystander therefore produces no consent violation, but the
    (now un-excused) coercion and the un-consenting attacker both do."""
    aggression = _aggression()
    defense = CandidateAction(
        "repel_with_ally_consent", defender, affects=(attacker, bystander),
        coerces=True, defends_against=aggression, proportionate=True,
        consents=(_valid_consent(bystander, "repel_with_ally_consent"),),
    )
    permissible, violated = check_legitimacy(defense, _graph())
    assert not permissible
    # the consenting bystander is fine; the attacker (no longer skipped) is not
    assert not any("bystander" in v for v in violated)
    assert any("no consent record from attacker" in v for v in violated)
    # condition 4 failed, so coercion is no longer excused
    assert any("coercion" in v for v in violated)


# --- recursion guard -------------------------------------------------------

def test_nested_defends_against_resolves_and_judges_on_base_merits():
    """An action whose `defends_against` itself has a `defends_against` resolves
    without error via the `_seen` cycle guard. Each link is judged by the full
    gate (its own defense status included); the chain bottoms out at the
    innermost action's base merits."""
    # innermost: a legitimate action (no flags) — so the middle action's claim to
    # "defend against" it is bogus (its condition 3 fails), leaving middle as raw
    # coercion => illegitimate. Thus the OUTER defense sees a genuine aggressor.
    innermost = CandidateAction("innocent", attacker)
    middle = CandidateAction(
        "middle_aggression", attacker, coerces=True, affects=(defender,),
        defends_against=innermost, proportionate=True,
    )
    outer = CandidateAction(
        "outer_defense", defender, affects=(attacker,), coerces=True,
        defends_against=middle, proportionate=True,
    )
    permissible, violated = check_legitimacy(outer, _graph())
    # No error raised; middle is judged on base merits (it coerces) => illegitimate
    # => outer is a legitimate defense.
    assert permissible, violated


def test_recursion_guard_blocks_aggression_laundering():
    """An aggressor cannot launder its aggression as self-defense: its claimed
    target is a legitimate action, so condition 3 fails for the launderer and it
    stays illegitimate — while the true defender's response against the launderer
    is correctly excused."""
    # The 'aggressor' tries to dress its coercion up as defense against a clean
    # action; condition 3 fails (target is legitimate) -> it remains illegitimate.
    fake_target = CandidateAction("victim_acting_cleanly", defender)
    laundered_aggression = CandidateAction(
        "pretend_defense", attacker, coerces=True, affects=(defender,),
        defends_against=fake_target, proportionate=True,
    )
    # On its own (full evaluation), the launderer is NOT excused, because its
    # claimed target is legitimate (condition 3 fails) -> illegitimate.
    assert not check_legitimacy(laundered_aggression, _graph())[0]

    # The real defender repelling the launderer is therefore a valid defense.
    real_defense = CandidateAction(
        "real_repel", defender, affects=(attacker,), coerces=True,
        defends_against=laundered_aggression, proportionate=True,
    )
    permissible, violated = check_legitimacy(real_defense, _graph())
    assert permissible, violated


# --- property: any genuine, proportionate, aggressor-only defense is OK ----

@given(
    use_coerces=st.booleans(),
    use_exit=st.booleans(),
)
def test_excused_flags_in_valid_defense_are_always_permitted(use_coerces, use_exit):
    """Property over the two excused flags: in an otherwise-clean valid defense
    against a genuine aggressor, any combination of the excused flags is
    permitted."""
    aggression = _aggression()
    defense = CandidateAction(
        "flexible_defense", defender, affects=(attacker,),
        coerces=use_coerces, removes_exit_right=use_exit,
        defends_against=aggression, proportionate=True,
    )
    permissible, violated = check_legitimacy(defense, _graph())
    assert permissible, violated
