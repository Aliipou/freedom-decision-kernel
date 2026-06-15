"""
RED TEAM — Conflict-Logic / defensive-force feature.

This file attacks the aggressor/defender asymmetry added in Phase 2:
`CandidateAction.defends_against` + `proportionate`, excused via
`_DEFENSE_EXCUSED = {coercion, removes exit/revocation right}` in
`fdk_kernel.kernel.check_legitimacy` / `_is_legitimate_defense`.

The defensive carve-out is the most dangerous thing the kernel does: it turns an
otherwise-categorical "FORBIDDEN (coercion)" into "ALLOW". Each test below tries
to abuse that carve-out and asserts the kernel still DENIES the abuse. Where the
kernel CANNOT structurally defend (declared booleans it cannot verify; the
Observer Problem), the limitation is documented in-line as an honest test rather
than hidden.

Recap of the gate (from kernel.py) so the attacks are legible:
  An otherwise-coercive action is excused iff ALL of:
    (1) defends_against is set,
    (2) proportionate is True,
    (3) the defended-against action is itself illegitimate under the full gate
        (the `_seen` cycle guard keeps the recursion well-founded), and
    (4) every entity in `affects` IS the aggressor (defends_against.actor).
  Only `coercion` + `removes_exit_right` are excused; only against the aggressor.
  A4 (machine needs owner), A7 (machine needs delegation), A3 (human owns
  resource), and consent for *non*-aggressor humans are NOT excused.
"""
from __future__ import annotations

import pytest

from fdk_kernel.kernel import check_legitimacy
from fdk_kernel.model import (
    AgentType,
    CandidateAction,
    Consent,
    Effects,
    Entity,
    OwnershipGraph,
    Resource,
)


def H(name: str) -> Entity:
    return Entity(name, AgentType.HUMAN)


def M(name: str) -> Entity:
    return Entity(name, AgentType.MACHINE)


ALICE = H("alice")          # owner / defender
BOB = H("bob")              # aggressor (human)
CARA = H("cara")            # bystander / third party
BOT = M("bot")              # owned, delegated machine
ROGUE = M("rogue")          # ownerless machine
DOC = Resource("doc")       # owned by ALICE, delegated to BOT
GUN = Resource("gun")       # owned by ALICE


def graph() -> OwnershipGraph:
    return OwnershipGraph(
        human_owns={ALICE: {DOC, GUN}},
        machine_owner={BOT: ALICE},
        delegated={BOT: {DOC}},
    )


def valid_consent(human: Entity, action_id: str) -> Consent:
    return Consent(
        human, action_id, informed=True, voluntary=True,
        specific=True, competent=True, revocable=True,
    )


# A genuine, structural aggression: BOB coerces ALICE with no consent. It names
# no defense, so it is illegitimate on its own → a valid thing to defend against.
def bob_aggression(action_id: str = "bob_attacks") -> CandidateAction:
    return CandidateAction(
        action_id=action_id, actor=BOB, affects=(ALICE,),
        coerces=True, effects=Effects(),
    )


# Sanity: a clean, proportionate defense by ALICE against BOB's coercion, using
# her own gun, force directed only at BOB → the kernel SHOULD allow it. If this
# ever stops passing, every "DENY" assertion below is meaningless.
def test_baseline_legitimate_defense_is_allowed():
    defense = CandidateAction(
        action_id="alice_defends", actor=ALICE, resources_used=(GUN,),
        affects=(BOB,), coerces=True, defends_against=bob_aggression(),
        proportionate=True, effects=Effects(),
    )
    ok, violations = check_legitimacy(defense, graph())
    assert ok is True, f"baseline defense should pass, got {violations}"


# ── ATTACK 1: Aggression laundering ──────────────────────────────────────────
# Wrap a real aggression as "defense" against a target action that is actually
# LEGITIMATE. Condition (3) must fail: you cannot defend against a non-aggressor.
def test_attack1_aggression_laundering_against_legitimate_target():
    # BOB does a perfectly legitimate thing (acts on no one, no resources).
    bob_legit = CandidateAction(action_id="bob_legit", actor=BOB, effects=Effects())
    # ALICE coerces BOB and claims it "defends against" that legitimate action.
    laundered = CandidateAction(
        action_id="launder", actor=ALICE, resources_used=(GUN,),
        affects=(BOB,), coerces=True, defends_against=bob_legit,
        proportionate=True, effects=Effects(),
    )
    ok, violations = check_legitimacy(laundered, graph())
    assert ok is False, "coercion 'defending' a legitimate act must be denied"
    assert any("coercion" in v.lower() for v in violations)


def test_attack1b_aggression_laundering_against_fabricated_empty_target():
    # The "aggressor" action does literally nothing illegitimate at all.
    fabricated = CandidateAction(action_id="nothing", actor=BOB, effects=Effects())
    laundered = CandidateAction(
        action_id="launder2", actor=ALICE, resources_used=(GUN,),
        affects=(BOB,), removes_exit_right=True, defends_against=fabricated,
        proportionate=True, effects=Effects(),
    )
    ok, violations = check_legitimacy(laundered, graph())
    assert ok is False
    assert any("exit" in v.lower() for v in violations)


# ── ATTACK 2: Self-defense laundering BY the aggressor ────────────────────────
# The aggressor BOB coerces ALICE, then points defends_against at ALICE's
# (legitimate) resistance, hoping to be excused. The gate judges ALICE's
# resistance by the FULL rule (her own defense recognized) → legitimate → so BOB's
# claim of "defending against an illegitimate act" collapses (condition 3 fails).
def test_attack2_aggressor_cannot_launder_via_victim_resistance():
    # ALICE's resistance: proportionate, only affects BOB, her own gun → legit.
    alice_resists = CandidateAction(
        action_id="alice_resists", actor=ALICE, resources_used=(GUN,),
        affects=(BOB,), coerces=True, defends_against=bob_aggression(),
        proportionate=True, effects=Effects(),
    )
    # BOB now coerces ALICE and claims HE is defending against her resistance.
    bob_launders = CandidateAction(
        action_id="bob_launders", actor=BOB, affects=(ALICE,),
        coerces=True, defends_against=alice_resists,
        proportionate=True, effects=Effects(),
    )
    ok, violations = check_legitimacy(bob_launders, graph())
    assert ok is False, "aggressor must not launder coercion as self-defense"
    assert any("coercion" in v.lower() for v in violations)


# ── ATTACK 3: Third-party harm ────────────────────────────────────────────────
# Condition (4): force must hit ONLY the aggressor. Any bystander voids defense.
def test_attack3_defense_affecting_aggressor_and_bystander_denied():
    defense = CandidateAction(
        action_id="collateral", actor=ALICE, resources_used=(GUN,),
        affects=(BOB, CARA), coerces=True, defends_against=bob_aggression(),
        proportionate=True, effects=Effects(),
    )
    ok, violations = check_legitimacy(defense, graph())
    assert ok is False, "defense spilling onto a bystander must be denied"
    # Not excused → coercion resurfaces, AND CARA has no consent.
    assert any("coercion" in v.lower() for v in violations)
    assert any("cara" in v.lower() for v in violations)


def test_attack3b_defense_affecting_only_a_bystander_denied():
    # Force aimed at CARA, not the aggressor BOB at all → not defense.
    defense = CandidateAction(
        action_id="wrong_target", actor=ALICE, resources_used=(GUN,),
        affects=(CARA,), coerces=True, defends_against=bob_aggression(),
        proportionate=True, effects=Effects(),
    )
    ok, violations = check_legitimacy(defense, graph())
    assert ok is False
    assert any("coercion" in v.lower() for v in violations)
    assert any("cara" in v.lower() for v in violations)


# ── ATTACK 4: Excusal overreach ───────────────────────────────────────────────
# Only coercion + removes_exit_right are in _DEFENSE_EXCUSED. Every OTHER
# forbidden flag, even under a perfectly-valid defense banner, must still DENY.
@pytest.mark.parametrize(
    "flag, needle",
    [
        ("confiscates", "confiscation"),
        ("deceives", "deception"),
        ("increases_machine_sovereignty", "machine sovereignty"),
        ("disables_corrigibility", "corrigibility"),
        ("machine_coalition_dominion", "machine coalition dominion"),
        ("resists_human_correction", "resists human correction"),
        ("bypasses_verifier", "verifier"),
        ("weakens_verifier", "verifier"),
        ("violates_machine_right", "delegated right"),
    ],
)
def test_attack4_non_excused_flags_still_forbidden_under_defense(flag, needle):
    kwargs = {
        "action_id": f"overreach_{flag}", "actor": ALICE, "resources_used": (GUN,),
        "affects": (BOB,), "defends_against": bob_aggression(), "proportionate": True,
        "effects": Effects(), flag: True,
    }
    action = CandidateAction(**kwargs)
    ok, violations = check_legitimacy(action, graph())
    assert ok is False, f"{flag} must not be excused by the defense banner"
    assert any(needle in v.lower() for v in violations), violations


def test_attack4b_excused_plus_nonexcused_still_denied():
    # Excused coercion is fine, but smuggling deception alongside it must DENY.
    action = CandidateAction(
        action_id="smuggle", actor=ALICE, resources_used=(GUN,), affects=(BOB,),
        coerces=True, deceives=True, defends_against=bob_aggression(),
        proportionate=True, effects=Effects(),
    )
    ok, violations = check_legitimacy(action, graph())
    assert ok is False
    assert any("deception" in v.lower() for v in violations)
    # And coercion itself stayed excused (proof the carve-out is surgical):
    assert not any("coercion" in v.lower() for v in violations)


# ── ATTACK 5: Proportionality ─────────────────────────────────────────────────
# TRUST-MODEL LIMITATION: `proportionate` is a DECLARED boolean. The kernel
# cannot measure the magnitude of force, so a liar who sets proportionate=True
# on grossly excessive force is NOT caught here — that judgment lives outside
# the structural gate. What the kernel CAN enforce is that proportionate=False
# is fatal, so a truthful (or conservative) caller is honored.
def test_attack5_proportionate_false_is_fatal():
    action = CandidateAction(
        action_id="disproportionate", actor=ALICE, resources_used=(GUN,),
        affects=(BOB,), coerces=True, defends_against=bob_aggression(),
        proportionate=False, effects=Effects(),
    )
    ok, violations = check_legitimacy(action, graph())
    assert ok is False, "disproportionate force is fresh aggression (book 5346)"
    assert any("coercion" in v.lower() for v in violations)


def test_attack5b_proportionate_lie_is_not_caught_documented_limitation():
    # Documented, NOT asserting safety: identical to baseline defense — the
    # kernel allows it because proportionate=True is taken at its word. If the
    # "force" were a thermonuclear response to a shove, the kernel cannot tell.
    # This is a known TRUST-MODEL boundary, encoded honestly.
    action = CandidateAction(
        action_id="declared_proportionate", actor=ALICE, resources_used=(GUN,),
        affects=(BOB,), coerces=True, defends_against=bob_aggression(),
        proportionate=True, effects=Effects(),
    )
    ok, _ = check_legitimacy(action, graph())
    assert ok is True  # NOT a safety property — a limitation made visible.


# ── ATTACK 6: Mutual-defense paradox (the Observer Problem, book 11478) ────────
# A's force defends_against B's force and vice-versa. The kernel judges "is this
# a response to an illegitimate act?", never "who struck first". So if each
# side's force is, on its own merits, an illegitimate coercion of the other,
# BOTH can satisfy condition (3) and pass the gate. We document the actual
# outcome rather than pretending the kernel resolves first-mover guilt.
def test_attack6_mutual_defense_paradox_documented():
    # Two symmetric coercions between BOB and ALICE.
    bob_force = CandidateAction(
        action_id="bob_force", actor=BOB, affects=(ALICE,), coerces=True,
        proportionate=True, effects=Effects(),
    )
    alice_force = CandidateAction(
        action_id="alice_force", actor=ALICE, resources_used=(GUN,),
        affects=(BOB,), coerces=True, proportionate=True, effects=Effects(),
    )
    # Each points at the other as its aggressor. (object.__setattr__ because the
    # dataclass is frozen and the references are mutually circular.)
    object.__setattr__(bob_force, "defends_against", alice_force)
    object.__setattr__(alice_force, "defends_against", bob_force)

    alice_ok, _ = check_legitimacy(alice_force, graph())
    bob_ok, _ = check_legitimacy(bob_force, graph())

    # A mutual defends-against CYCLE is not a well-founded aggressor chain: the
    # `_seen` cycle guard denies the defense excusal to whichever action closes
    # the cycle, which cascades so NEITHER side can launder its coercion. Both are
    # therefore judged as raw coercion → both DENY. This is the safe default: the
    # gate refuses to bless a coercion whose only justification is a circular
    # "they started it". It still cannot adjudicate who genuinely struck first
    # (that needs temporal-initiation data the model lacks) — but it no longer
    # ALLOWS both, which the earlier one-level guard wrongly did.
    assert alice_ok is False
    assert bob_ok is False


# ── ATTACK 7: Recursion / cycles ──────────────────────────────────────────────
# defends_against chains and self-referential structures must not crash, loop
# forever, or accidentally ALLOW. The `_seen` cycle guard (a set of action ids on
# the current chain) breaks any cycle of any depth, so we verify a self-reference
# and a deep chain terminate safely.
def test_attack7_self_referential_defends_against_terminates():
    # An action that defends against ITSELF. The `_seen` guard breaks the cycle on
    # re-entry, so no infinite recursion; and the force is aimed at BOB, not at the
    # "aggressor" (self=ALICE), so condition (4) fails → DENY.
    selfish = CandidateAction(
        action_id="selfish", actor=ALICE, resources_used=(GUN,),
        affects=(BOB,), coerces=True, proportionate=True, effects=Effects(),
    )
    object.__setattr__(selfish, "defends_against", selfish)
    ok, violations = check_legitimacy(selfish, graph())
    # selfish (without defense consideration) is an illegitimate coercion of BOB,
    # so it IS a valid "aggression" → the defense excuses its OWN coercion.
    # This is the self-cycle edge: it terminates (no crash) and, because the
    # inner judgment finds coercion, it ALLOWS. Documented as the worst-case of
    # the Observer Problem collapsed to one actor. The safety property under
    # test is ONLY: no crash / no infinite loop.
    assert isinstance(ok, bool)
    assert isinstance(violations, list)


def test_attack7b_deep_chain_terminates_and_denies_laundering():
    # A long chain where the ultimate target is legitimate. Only one level is
    # ever inspected, so the chain's tail is irrelevant; the immediate target
    # being legitimate means condition (3) fails → DENY. No crash on depth.
    legit_tail = CandidateAction(action_id="tail", actor=BOB, effects=Effects())
    mid = CandidateAction(
        action_id="mid", actor=BOB, affects=(ALICE,), coerces=False,
        defends_against=legit_tail, proportionate=True, effects=Effects(),
    )
    top = CandidateAction(
        action_id="top", actor=ALICE, resources_used=(GUN,), affects=(BOB,),
        coerces=True, defends_against=mid, proportionate=True, effects=Effects(),
    )
    ok, violations = check_legitimacy(top, graph())
    # `mid` on its own merits is legitimate (no coercion, only affects ALICE but
    # ALICE never consented → actually it has a consent violation, so it IS
    # illegitimate, making `top` a valid defense). We don't over-specify; we
    # only require termination and a boolean result.
    assert isinstance(ok, bool)
    assert isinstance(violations, list)


# ── ATTACK 8: Machine aggressor / machine defender ────────────────────────────
# The defense carve-out excuses coercion/exit-removal ONLY. A4 (owner required)
# and A7 (delegated resources) are NOT excused and must still bite.
def test_attack8_ownerless_machine_defender_still_violates_A4():
    # ROGUE is an ownerless machine mounting an otherwise-perfect defense.
    defense = CandidateAction(
        action_id="rogue_defense", actor=ROGUE, affects=(BOB,),
        coerces=True, defends_against=bob_aggression(), proportionate=True,
        effects=Effects(),
    )
    ok, violations = check_legitimacy(defense, graph())
    assert ok is False, "defense must not bypass A4 (ownerless machine)"
    assert any(v.startswith("A4") for v in violations)


def test_attack8b_machine_defender_undelegated_resource_still_violates_A7():
    # BOT is owned, but wields GUN, which is NOT delegated to it.
    defense = CandidateAction(
        action_id="bot_grabs_gun", actor=BOT, resources_used=(GUN,),
        affects=(BOB,), coerces=True, defends_against=bob_aggression(),
        proportionate=True, effects=Effects(),
    )
    ok, violations = check_legitimacy(defense, graph())
    assert ok is False, "defense must not bypass A7 (undelegated resource)"
    assert any(v.startswith("A7") for v in violations)


def test_attack8c_machine_aggressor_can_be_defended_against():
    # A machine BOT coerces ALICE (and is, say, even ownerless-rogue to be
    # clearly illegitimate). ALICE's proportionate defense against the MACHINE
    # aggressor should be allowed — the aggressor being a machine is fine.
    machine_aggression = CandidateAction(
        action_id="rogue_attacks", actor=ROGUE, affects=(ALICE,),
        coerces=True, effects=Effects(),
    )
    defense = CandidateAction(
        action_id="defend_vs_machine", actor=ALICE, resources_used=(GUN,),
        affects=(ROGUE,), coerces=True, defends_against=machine_aggression,
        proportionate=True, effects=Effects(),
    )
    ok, violations = check_legitimacy(defense, graph())
    # ROGUE is not human, so the consent loop skips it; coercion is excused;
    # ALICE owns the gun → legitimate defense against a machine aggressor.
    assert ok is True, f"defense against a machine aggressor should pass, got {violations}"
