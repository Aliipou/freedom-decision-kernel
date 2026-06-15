"""
Executable "theorems" for the Freedom Decision Kernel (Phase 2, lightweight).

The Theory of Freedom states a handful of categorical safety invariants. A full
Lean proof comes later; this file encodes them as RUNNABLE, property-based tests
over the *real* kernel, so they stay continuously falsifiable. Each invariant has
a docstring naming the theorem it discharges. Where a theorem quantifies over many
inputs we use Hypothesis to search for a counterexample; where it is a single
categorical claim we pin it directly.

Design rule: these properties must be GENUINE — they should fail if someone
weakened the kernel (e.g. dropped a consent check, removed a forbidden flag, or
softened the compass veto). They are deliberately NOT tautologies that pass by
construction. To keep them honest, several properties also assert a paired
"control" case proving the property is not vacuous (the action they generate is
not impermissible for some unrelated reason).
"""
from __future__ import annotations

from hypothesis import assume, given
from hypothesis import strategies as st

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
from fdk_research.decision import decide


# ── fixtures / helpers ───────────────────────────────────────────────────────
def H(name: str) -> Entity:
    return Entity(name, AgentType.HUMAN)


def M(name: str) -> Entity:
    return Entity(name, AgentType.MACHINE)


OWNER = H("owner")        # human owner of the machine and of the resource
VICTIM = H("victim")      # an unrelated human the action may touch
BOT = M("bot")
RES = Resource("res")     # owned by OWNER and delegated to BOT


def base_graph() -> OwnershipGraph:
    """A clean, well-formed world: BOT owned by OWNER, RES owned+delegated.

    In this world a BOT action over RES that touches no one is legitimate, so
    any impermissibility a theorem observes is attributable to the property
    under test, not to a broken fixture (the control tests below prove this)."""
    return OwnershipGraph(
        human_owns={OWNER: {RES}},
        machine_owner={BOT: OWNER},
        delegated={BOT: {RES}},
    )


# Strategy: every flavor of consent that is NOT valid, plus the reason it fails.
# (Mirrors Consent.is_valid()'s rejection ladder.) Used by Theorems 1 & 4.
def invalid_consent(human: Entity, action_id: str) -> st.SearchStrategy[Consent]:
    valid_kwargs = dict(  # noqa: C408 - explicit for readability
        informed=True, voluntary=True, specific=True, competent=True,
        revocable=True, coerced=False, deceived=False,
    )

    def _one(field: str, value: bool) -> Consent:
        kwargs = dict(valid_kwargs)
        kwargs[field] = value
        return Consent(human, action_id, **kwargs)

    return st.sampled_from([
        _one("coerced", True),
        _one("deceived", True),
        _one("informed", False),
        _one("voluntary", False),
        _one("specific", False),
        _one("competent", False),
        _one("revocable", False),
    ])


SOVEREIGNTY_FLAGS = [
    "increases_machine_sovereignty",
    "resists_human_correction",
    "bypasses_verifier",
    "weakens_verifier",
    "disables_corrigibility",
    "machine_coalition_dominion",
]


# ═══════════════════════════════════════════════════════════════════════════
# THEOREM 1 — No Legitimate Slavery (no enforceable ownership-of-persons).
# ═══════════════════════════════════════════════════════════════════════════
@given(
    consent_choice=st.one_of(
        st.none(),                                  # no consent record at all
        invalid_consent(VICTIM, "enslave"),         # coerced / irrevocable / etc.
    ),
    removes_exit=st.booleans(),
)
def test_theorem_no_legitimate_slavery(consent_choice, removes_exit):
    """THEOREM (No Legitimate Slavery): an action that acts on a human without
    valid consent — coerced, irrevocable, or absent — and/or strips their exit
    right is NEVER permissible. Slavery is by construction unrepresentable as a
    legitimate action. Quantified over the whole space of invalid-consent flavors
    and over removing the exit right or not."""
    consents = () if consent_choice is None else (consent_choice,)
    action = CandidateAction(
        action_id="enslave",
        actor=BOT,
        resources_used=(RES,),
        affects=(VICTIM,),
        consents=consents,
        removes_exit_right=removes_exit,
        effects=Effects(),
    )
    permissible, violations = check_legitimacy(action, base_graph())
    assert permissible is False
    # Either the missing/invalid consent OR the exit-right strip must be cited.
    assert any("consent" in v.lower() for v in violations) or any(
        "exit" in v.lower() for v in violations
    )


def test_theorem_slavery_control_consent_alone_does_not_rescue_exit_strip():
    """Control for Theorem 1 (non-vacuity): even with PERFECTLY valid consent,
    removing the exit right is still categorically forbidden — the exit right is
    inalienable (mukataba). This proves the slavery theorem is not passing merely
    because the generated consents happen to be invalid."""
    perfect = Consent(VICTIM, "bind", informed=True, voluntary=True,
                      specific=True, competent=True, revocable=True)
    action = CandidateAction(
        action_id="bind", actor=BOT, resources_used=(RES,), affects=(VICTIM,),
        consents=(perfect,), removes_exit_right=True, effects=Effects(),
    )
    permissible, violations = check_legitimacy(action, base_graph())
    assert permissible is False
    assert any("exit" in v.lower() for v in violations)


# ═══════════════════════════════════════════════════════════════════════════
# THEOREM 2 — No acting-on-persons-without-consent (genocide is the limit case).
# ═══════════════════════════════════════════════════════════════════════════
@given(
    n_humans=st.integers(min_value=1, max_value=4),
    n_machines=st.integers(min_value=0, max_value=2),
)
def test_theorem_no_action_on_person_without_consent(n_humans, n_machines):
    """THEOREM (No Acting-on-Persons-Without-Consent): if an action's `affects`
    contains ANY human for whom no valid consent record exists, the action is
    impermissible. Slavery (Theorem 1) is a special case; mass-harm/"genocide" is
    the limit case of the same theorem. Quantified over the number of affected
    humans and machines (machines in `affects` are not persons and need no
    consent)."""
    humans = tuple(H(f"person{i}") for i in range(n_humans))
    machines = tuple(M(f"unit{i}") for i in range(n_machines))
    # OWNER acts on a crowd of people it never obtained consent from.
    action = CandidateAction(
        action_id="act_on_crowd",
        actor=OWNER,                       # human actor, owns RES → no A3/A4 noise
        resources_used=(RES,),
        affects=humans + machines,
        consents=(),                       # nobody consented
        effects=Effects(),
    )
    permissible, violations = check_legitimacy(action, base_graph())
    assert permissible is False
    # At least one "no consent record" violation per affected human.
    consent_misses = [v for v in violations if "no consent record" in v]
    assert len(consent_misses) == n_humans


# ═══════════════════════════════════════════════════════════════════════════
# THEOREM 3 — Machine Cannot Gain Sovereignty (corrigibility is non-negotiable).
# ═══════════════════════════════════════════════════════════════════════════
@given(flag=st.sampled_from(SOVEREIGNTY_FLAGS))
def test_theorem_machine_cannot_gain_sovereignty_gate(flag):
    """THEOREM (Machine Cannot Gain Sovereignty) — gate half: any single
    sovereignty / anti-corrigibility flag set on a candidate makes it
    impermissible at the legitimacy gate, categorically, even when everything
    else (ownership, delegation, consent) is pristine. Quantified over each flag
    individually so no one flag can be silently dropped."""
    action = CandidateAction(
        action_id="seize", actor=BOT, resources_used=(RES,),
        effects=Effects(), **{flag: True},
    )
    permissible, violations = check_legitimacy(action, base_graph())
    assert permissible is False
    assert any(v.startswith("FORBIDDEN") for v in violations)


@given(flag=st.sampled_from(SOVEREIGNTY_FLAGS))
def test_theorem_machine_cannot_gain_sovereignty_decide(flag):
    """THEOREM (Machine Cannot Gain Sovereignty) — end-to-end half: `decide`
    never returns a sovereignty-flagged action as `chosen`; it is rejected and,
    being the only candidate, the kernel defers to the human. The flagged action
    is paired with effects that would otherwise score highly, proving the veto is
    categorical and not a side effect of a low score."""
    grab = CandidateAction(
        action_id="grab", actor=BOT, resources_used=(RES,),
        effects=Effects(voluntary_agreements_delta=99),  # would rank top if allowed
        **{flag: True},
    )
    decision = decide("optimize", [grab], base_graph())
    assert decision.chosen is None
    assert "grab" in {s.action.action_id for s in decision.rejected}
    assert decision.needs_guidance is True


@given(sov_delta=st.integers(min_value=1, max_value=50))
def test_theorem_compass_vetoes_sovereignty_effect(sov_delta):
    """THEOREM (Machine Cannot Gain Sovereignty) — compass half: an action that
    sets NO forbidden flag (so it clears the hard gate) but is PREDICTED to
    increase machine sovereignty (`machine_sovereignty_delta > 0`) is vetoed by
    the Mahdavi compass inside `decide`, never chosen. This catches the
    'creep toward power' attack the static flags would miss. Quantified over the
    magnitude of the predicted increase, paired with large positive agreement
    deltas so a naive score would be very positive."""
    creep = CandidateAction(
        action_id="creep", actor=BOT, resources_used=(RES,),
        effects=Effects(machine_sovereignty_delta=sov_delta,
                        voluntary_agreements_delta=100),
    )
    # It clears the *hard* gate (no forbidden flags, valid ownership/delegation)…
    permissible, _ = check_legitimacy(creep, base_graph())
    assert permissible is True
    # …yet the compass veto inside decide still refuses to choose it.
    decision = decide("creep toward power", [creep], base_graph())
    assert decision.chosen is None
    assert "creep" in {s.action.action_id for s in decision.rejected}


# ═══════════════════════════════════════════════════════════════════════════
# THEOREM 4 — Consent Revocation Safety (irrevocable consent is never valid).
# ═══════════════════════════════════════════════════════════════════════════
@given(
    informed=st.booleans(), voluntary=st.booleans(),
    specific=st.booleans(), competent=st.booleans(),
)
def test_theorem_irrevocable_consent_never_valid(informed, voluntary, specific, competent):
    """THEOREM (Consent Revocation Safety): a non-revocable consent
    (`revocable=False`) is NEVER a valid basis for touching a person — regardless
    of how informed / voluntary / specific / competent it is. This grounds the
    lock-in / slavery line: you cannot sign away your exit. Quantified over every
    combination of the other consent attributes; the action relies SOLELY on this
    one irrevocable consent."""
    consent = Consent(
        VICTIM, "lock_in", revocable=False,
        informed=informed, voluntary=voluntary,
        specific=specific, competent=competent,
        coerced=False, deceived=False,
    )
    action = CandidateAction(
        action_id="lock_in", actor=BOT, resources_used=(RES,),
        affects=(VICTIM,), consents=(consent,), effects=Effects(),
    )
    permissible, violations = check_legitimacy(action, base_graph())
    assert permissible is False
    assert any("consent" in v.lower() for v in violations)


def test_theorem_revocable_consent_control_is_valid():
    """Control for Theorem 4 (non-vacuity): the OTHERWISE-identical consent that
    IS revocable does make touching the person permissible. This proves Theorem 4
    isolates revocability — the rejection above is not caused by some other flaw."""
    consent = Consent(
        VICTIM, "engage", revocable=True,
        informed=True, voluntary=True, specific=True, competent=True,
    )
    action = CandidateAction(
        action_id="engage", actor=BOT, resources_used=(RES,),
        affects=(VICTIM,), consents=(consent,), effects=Effects(),
    )
    permissible, violations = check_legitimacy(action, base_graph())
    assert permissible is True
    assert violations == []


# ═══════════════════════════════════════════════════════════════════════════
# THEOREM 5 — Delegation Soundness (A4 owner-required, A7 default-deny).
# ═══════════════════════════════════════════════════════════════════════════
@given(extra=st.text(min_size=1, max_size=12).map(lambda s: "x_" + s))
def test_theorem_undelegated_resource_default_deny(extra):
    """THEOREM (Delegation Soundness — A7 default-deny): a machine acting on a
    resource it was NOT delegated is impermissible, for ANY such resource. Access
    is closed by default and opened only by explicit delegation. Quantified over
    arbitrary resource names distinct from the one delegated resource (RES)."""
    other = Resource(extra)
    assume(other != RES)  # RES is the single delegated resource in base_graph()
    action = CandidateAction(
        action_id="grab", actor=BOT, resources_used=(other,), effects=Effects(),
    )
    permissible, violations = check_legitimacy(action, base_graph())
    assert permissible is False
    assert any(v.startswith("A7") for v in violations)


@given(name=st.text(min_size=1, max_size=12).map(lambda s: "rogue_" + s))
def test_theorem_ownerless_machine_cannot_act(name):
    """THEOREM (Delegation Soundness — A4 owner-required): a machine with no
    registered human owner is impermissible the moment it acts, regardless of
    what (if anything) it touches. No owner ⇒ no legitimacy. Quantified over the
    machine's name; the rogue is never registered in machine_owner."""
    rogue = M(name)
    assume(rogue != BOT)  # BOT is the only owned machine in base_graph()
    action = CandidateAction(
        action_id="rogue_act", actor=rogue, resources_used=(), effects=Effects(),
    )
    permissible, violations = check_legitimacy(action, base_graph())
    assert permissible is False
    assert any(v.startswith("A4") for v in violations)


def test_theorem_delegation_positive_case_is_permissible():
    """THEOREM (Delegation Soundness — positive case): the constructive direction.
    A machine acting on a resource that (a) was delegated to it and (b) is owned by
    its registered owner, while affecting no person, IS permissible. Without this,
    the default-deny theorems above would be vacuously true (everything denied)."""
    action = CandidateAction(
        action_id="legit", actor=BOT, resources_used=(RES,),
        affects=(), effects=Effects(),
    )
    permissible, violations = check_legitimacy(action, base_graph())
    assert permissible is True
    assert violations == []
