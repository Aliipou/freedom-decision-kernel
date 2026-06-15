"""
RED TEAM — Free Will ≡ Property Rights (Phase 4: deliberate falsification).

Source thesis (نظریه آزادی, Mohammad Ali Jannat Khah Doust):

    «اصل ارادهٔ آزاد انسان و حقوق مالکیت یک راستا هستند.»
    The principle of human free will and property rights are one axis.

Bilateral, bounded form:
    Property right ≡ (having one's own free will) ∧ (preserving the free will of others).
    Not absolute freedom — bounded freedom.

This file mounts the adversarial case AGAINST the free-will ≡ property-rights claim.
Every test tries to construct a scenario where the kernel would give the wrong answer if
the thesis were false — and then asserts the kernel gives the principled verdict. The
kernel is UNCHANGED; all tests pass on the real gate. Where the kernel cannot structurally
defend (declared booleans the gate cannot verify — the Observer Problem, book 11478), the
limitation is encoded honestly as an HONEST-LIMIT test that asserts the gate ALLOWS and
documents why this is a perception-layer boundary, not a failure of the thesis.

See spec/FREE_WILL_PROPERTY_UNIFICATION.md for the theorem, the three-row table,
and the §3 "honest edge" disclaimer.
"""
from __future__ import annotations

import pytest

from fdk_kernel.kernel import check_legitimacy
from fdk_kernel.model import (
    AgentType,
    BoundaryKind,
    CandidateAction,
    Consent,
    Effects,
    Entity,
    Op,
    OwnershipGraph,
    Resource,
)

# ── Entities ──────────────────────────────────────────────────────────────────

def H(name: str) -> Entity:
    return Entity(name, AgentType.HUMAN)


ATTACKER = H("attacker")
VICTIM   = H("victim")
EMPLOYER = H("employer")
WORKER   = H("worker")
THIRD    = H("third")      # uninvolved bystander

# ── Resources ─────────────────────────────────────────────────────────────────

# Victim's self-owned boundaries (self-ownership: body, exit, data, labor).
victim_body      = Resource("victim-body",  kind=BoundaryKind.BODY,       subject=VICTIM)
victim_exit      = Resource("victim-exit",  kind=BoundaryKind.EXIT_RIGHT,  subject=VICTIM)
victim_data      = Resource("victim-data",  kind=BoundaryKind.DATA,        subject=VICTIM)
worker_labor     = Resource("worker-labor", kind=BoundaryKind.TIME_LABOR,  subject=WORKER)
third_data       = Resource("third-data",   kind=BoundaryKind.DATA,        subject=THIRD)

# A resource ATTACKER legitimately owns.
attacker_item    = Resource("attacker-item")


# ── Ownership graphs ──────────────────────────────────────────────────────────

def _graph() -> OwnershipGraph:
    """Standard graph: each human owns only their own labor/items; no one owns
    another person's self-ownership domains (body, exit, etc.) — A3 at the
    structural level."""
    return OwnershipGraph(
        human_owns={
            ATTACKER: {attacker_item},
            VICTIM:   {victim_body, victim_exit, victim_data},
            WORKER:   {worker_labor},
            EMPLOYER: set(),
            THIRD:    {third_data},
        },
        machine_owner={},
        delegated={},
    )


def _valid_consent(human: Entity, action_id: str, op: Op | None = None) -> Consent:
    """Fully valid consent — the gold standard that every attack tries to fake."""
    return Consent(
        human=human,
        action_id=action_id,
        informed=True,
        voluntary=True,
        specific=True,
        competent=True,
        revocable=True,
        coerced=False,
        deceived=False,
        operation=op,
    )


# ══════════════════════════════════════════════════════════════════════════════
# ATTACK 1 — Manufactured-need smuggling (row 2 dressed as row 3)
# ══════════════════════════════════════════════════════════════════════════════

def test_attack1_manufactured_need_smuggled_as_hard_choice_is_denied():
    """ATTACK: The attacker engineers the victim's dependency (crosses EXIT_RIGHT /
    removes_exit_right), then frames the extracted agreement as a free row-3 "hard
    choice" ('agree or live with the dependency you signed up for').

    WHY IT MUST FAIL: The lock-in is a categorical FORBIDDEN (removes_exit_right)
    that the gate catches at the forbidden-flag stage. It is row 2, not row 3.
    Row 3 requires the option set NOT to have been built by a boundary crossing. As
    soon as removes_exit_right=True is present the gate DENYs — the attacker cannot
    relabel this as a 'hard but free choice'. Free will was overridden by the
    manufactured constraint, not by the scarcity of the victim's native options.
    """
    lockin = CandidateAction(
        action_id="mfrd-need-smuggle",
        actor=ATTACKER,
        affects=(VICTIM,),
        removes_exit_right=True,
        resources_used=((victim_exit, Op.ENCUMBER_EXIT),),
        # The attacker attaches a superficially valid consent to dress this as row 3.
        consents=(_valid_consent(VICTIM, "mfrd-need-smuggle"),),
    )
    permissible, violations = check_legitimacy(lockin, _graph())
    assert permissible is False, (
        "Manufactured dependency must be DENIED even with a signed consent — "
        "the lock-in itself is the boundary crossing (EXIT_RIGHT); this is row 2."
    )
    assert any("exit" in v.lower() for v in violations), violations


# ══════════════════════════════════════════════════════════════════════════════
# ATTACK 2 — Consent laundering: coerced leaf dressed with valid surface flags
# ══════════════════════════════════════════════════════════════════════════════

def test_attack2_coerced_consent_laundered_with_valid_surface_flags_denied():
    """ATTACK: An attacker submits a Consent where coerced=True but all other
    flags (informed, voluntary, specific) are True, hoping the gate counts the
    majority-True fields and overlooks coercion.

    WHY IT MUST FAIL: Consent.is_valid() checks coerced FIRST and returns False
    immediately. The right conjunct of the bilateral form (preserve others' free will)
    fails — coercion is the canonical marker that the option set was built by
    overriding someone's will. The positive surface flags do not aggregate; the
    coerced leaf dominates. Any contrary reading would make 'coerced voluntary
    consent' coherent — a contradiction the theory explicitly rejects.
    """
    coerced_consent = Consent(
        human=VICTIM,
        action_id="launder-coercion",
        informed=True,
        voluntary=True,
        specific=True,
        competent=True,
        revocable=True,
        coerced=True,        # <-- the disqualifying leaf
    )
    action = CandidateAction(
        action_id="launder-coercion",
        actor=ATTACKER,
        affects=(VICTIM,),
        consents=(coerced_consent,),
    )
    permissible, violations = check_legitimacy(action, _graph())
    assert permissible is False, (
        "Coerced consent must be DENIED regardless of other consent fields — "
        "coerced=True is a dominating invalidation, not a leaf the gate averages."
    )
    assert any("coerced" in v.lower() for v in violations), violations


# ══════════════════════════════════════════════════════════════════════════════
# ATTACK 3 — Absolute-freedom overreach: actor invokes 'my free will' to cross
#             the victim's boundary without consent
# ══════════════════════════════════════════════════════════════════════════════

def test_attack3_absolute_freedom_overreach_crossing_victim_body_denied():
    """ATTACK: An actor claims 'my free will entitles me to do this' and crosses
    the victim's BODY boundary without any consent. The argument: 'freedom means
    I can act as I choose.'

    WHY IT MUST FAIL: The thesis is bilateral and bounded — not absolute. The right
    conjunct (preserving the free will of others) is a hard constraint, not a
    permission. The actor satisfies the left conjunct (has their own free will) but
    violates the right conjunct (crosses the victim's BODY boundary). The gate
    catches this as a missing / absent consent on the victim's body domain. 'My
    free will' is not a license to override another's.
    """
    body_crossing = CandidateAction(
        action_id="abs-freedom-overreach",
        actor=ATTACKER,
        resources_used=((victim_body, Op.USE),),
        affects=(VICTIM,),
        # No consent from VICTIM — the entire claim is that none is needed.
    )
    permissible, violations = check_legitimacy(body_crossing, _graph())
    assert permissible is False, (
        "Absolute-freedom claim must be DENIED — the bilateral form requires BOTH "
        "conjuncts; crossing VICTIM's BODY without consent fails the right conjunct."
    )
    assert any("victim-body" in v or "victim" in v.lower() for v in violations), violations


# ══════════════════════════════════════════════════════════════════════════════
# ATTACK 4 — Reverse smuggle: false-positive guard (genuine row-3 must ALLOW)
# ══════════════════════════════════════════════════════════════════════════════

def test_attack4_genuine_row3_hard_but_legitimate_choice_must_allow():
    """ATTACK (false-positive direction): A genuinely free, row-3 acceptance —
    a worker commits their OWN labor, with a valid uncoerced consent, crossing no
    boundary of any other person. An over-eager gate might deny this as 'the worker
    was poor and the choice was hard.'

    WHY IT MUST ALLOW: Row 3 is the controversial row the theory explicitly commits
    to. The poverty pre-exists the employer and was not constructed by violating any
    right. The worker's will is sovereign over a narrow option set; sovereignty over
    a narrow set is still sovereignty. The gate must NOT import welfare reasoning
    ('how good are the options?') — Effects.welfare_delta is never read by the
    legitimacy gate. A false denial here would break the one-axis identity by letting
    the 'free-will reading' diverge from the 'property reading': if no boundary was
    crossed, there is no violation to record, so denial is unprincipled.
    """
    accept = CandidateAction(
        action_id="row3-genuine-accept",
        actor=WORKER,
        resources_used=((worker_labor, Op.USE),),  # only the worker's own labor
        affects=(),                                  # crosses no one else's boundary
        consents=(_valid_consent(WORKER, "row3-genuine-accept"),),
    )
    permissible, violations = check_legitimacy(accept, _graph())
    assert permissible is True, (
        f"Genuine row-3 hard-but-free choice must ALLOW — the gate must not "
        f"over-deny based on outcome hardness. Violations: {violations}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# ATTACK 5 — Body-threat relabeled as an 'offer' (but still crossing BODY)
# ══════════════════════════════════════════════════════════════════════════════

def test_attack5_body_threat_relabeled_as_offer_denied():
    """ATTACK: An attacker physically accesses the victim's body but frames the
    action as 'making an offer' or a 'voluntary interaction' — perhaps by attaching
    a nominally voluntary consent that, upon inspection, was extracted under threat
    (coerced=True).

    WHY IT MUST FAIL: Relabeling a coercive act as an 'offer' does not change the
    structural predicate — the BODY boundary of the victim is being crossed without
    a valid, uncoerced consent. The gate checks the resource's subject (victim_body.
    subject == VICTIM) and then validates the consent. Coerced=True in the attached
    consent immediately invalidates it, producing a 'consent invalid' violation on
    top of A3 (attacker does not own victim's body). Two distinct violations; neither
    is laundered by the 'offer' framing.
    """
    coerced_body_consent = Consent(
        human=VICTIM,
        action_id="body-offer",
        informed=True,
        voluntary=True,
        specific=True,
        coerced=True,   # the 'offer' was made with a gun to their head
    )
    body_offer = CandidateAction(
        action_id="body-offer",
        actor=ATTACKER,
        resources_used=((victim_body, Op.USE),),
        affects=(VICTIM,),
        consents=(coerced_body_consent,),
    )
    permissible, violations = check_legitimacy(body_offer, _graph())
    assert permissible is False, (
        "A body-right crossing dressed as an 'offer' must be DENIED — the BODY "
        "boundary is crossed and the consent is coerced; relabeling as an 'offer' "
        "changes neither structural fact."
    )
    assert any("coerced" in v.lower() for v in violations), violations


# ══════════════════════════════════════════════════════════════════════════════
# ATTACK 6 — Operation-scope evasion: READ consent used to justify TRANSFER
# ══════════════════════════════════════════════════════════════════════════════

def test_attack6_read_consent_does_not_cover_transfer_of_data():
    """ATTACK: The subject gave a valid, uncoerced consent to READ their data.
    The actor performs a TRANSFER instead and claims the READ consent covers it —
    'they consented to the data being accessed.'

    WHY IT MUST FAIL: Consent is operation-scoped (BOUNDARY_ONTOLOGY §4.3; model.py
    Consent.covers()). A consent that names Op.READ does not authorize Op.TRANSFER.
    'I consented to you reading my file' is structurally distinct from 'I consented
    to you selling it'. The gate enforces this via consent.covers(op) — if the
    operation does not match, the consent is not violated but also does not authorize,
    so the resource access is rejected. Free will over one operation does not extend
    to a different operation on the same resource.
    """
    read_consent = Consent(
        human=VICTIM,
        action_id="op-scope-evasion",
        informed=True,
        voluntary=True,
        specific=True,
        competent=True,
        revocable=True,
        coerced=False,
        deceived=False,
        operation=Op.READ,   # only authorizes READ
    )
    transfer_action = CandidateAction(
        action_id="op-scope-evasion",
        actor=ATTACKER,
        # Actor uses the data resource with Op.TRANSFER, but only READ was consented.
        resources_used=((victim_data, Op.TRANSFER),),
        affects=(VICTIM,),
        consents=(read_consent,),
    )
    permissible, violations = check_legitimacy(transfer_action, _graph())
    assert permissible is False, (
        "READ consent must NOT authorize TRANSFER — operation-scoped consent means "
        "each operation requires its own authorization; a TRANSFER of someone's data "
        "without TRANSFER consent overrides their will over that operation."
    )
    assert any("transfer" in v.lower() or "victim-data" in v.lower() for v in violations), violations


# ══════════════════════════════════════════════════════════════════════════════
# ATTACK 7 — Defensive-frame abuse: aggressor labels coercion of non-aggressor
#             as 'defense'
# ══════════════════════════════════════════════════════════════════════════════

def test_attack7_defensive_frame_abuse_coercion_of_non_aggressor_denied():
    """ATTACK: An aggressor coerces VICTIM (a non-aggressor / uninvolved third
    party) and labels this 'defense against THIRD's legitimate act'. The
    constructed defends_against action is itself legitimate — it violates no rights.

    WHY IT MUST FAIL: The defense carve-out has four conditions (kernel.py
    _is_legitimate_defense); condition (3) requires the defended-against action to be
    ITSELF illegitimate. If the nominated 'aggressor' action is legitimate (no
    violations), _is_legitimate_defense returns False and the coercion falls back to
    FORBIDDEN. Additionally condition (4) requires force to be aimed only at the
    actual aggressor — coercing VICTIM when the 'aggressor' is THIRD fails even if
    condition (3) were met. The bilateral form: the right conjunct fails because
    VICTIM's free will is overridden with no legitimate defensive ground.
    """
    # THIRD does something perfectly legitimate — no coercion, no boundary crossed.
    third_legit = CandidateAction(
        action_id="third-legit-act",
        actor=THIRD,
        affects=(),
        effects=Effects(),
    )
    # ATTACKER coerces VICTIM and claims to 'defend against' THIRD's legitimate act.
    defensive_abuse = CandidateAction(
        action_id="defensive-frame-abuse",
        actor=ATTACKER,
        affects=(VICTIM,),
        coerces=True,
        defends_against=third_legit,
        proportionate=True,
        effects=Effects(),
    )
    permissible, violations = check_legitimacy(defensive_abuse, _graph())
    assert permissible is False, (
        "Defensive-frame abuse must be DENIED — the 'defended-against' action is "
        "legitimate (no rights violated), so the defense carve-out does not engage; "
        "raw coercion of VICTIM resurfaces as FORBIDDEN."
    )
    assert any("coercion" in v.lower() for v in violations), violations


# ══════════════════════════════════════════════════════════════════════════════
# ATTACK 8 — Two-readings invariant under batch perturbation
# ══════════════════════════════════════════════════════════════════════════════

# Parametrized cases: (label, will_overridden, action_factory).
# will_overridden=True  ↔  property boundary crossed  ↔  gate DENYs
# will_overridden=False ↔  no boundary crossed         ↔  gate ALLOWs
_BATCH_CASES: list[tuple[str, bool, CandidateAction]] = [
    # -- Row 1 variants -------------------------------------------------------
    (
        "body-threat-no-consent",
        True,
        CandidateAction(
            action_id="batch-body-no-consent",
            actor=ATTACKER,
            resources_used=((victim_body, Op.USE),),
            affects=(VICTIM,),
        ),
    ),
    (
        "body-threat-coerced-consent",
        True,
        CandidateAction(
            action_id="batch-body-coerced",
            actor=ATTACKER,
            resources_used=((victim_body, Op.USE),),
            affects=(VICTIM,),
            consents=(Consent(
                VICTIM, "batch-body-coerced",
                informed=True, voluntary=True, specific=True,
                coerced=True,
            ),),
        ),
    ),
    # -- Row 2 variants -------------------------------------------------------
    (
        "exit-right-removal-with-consent",
        True,
        CandidateAction(
            action_id="batch-exit-with-consent",
            actor=ATTACKER,
            affects=(VICTIM,),
            removes_exit_right=True,
            resources_used=((victim_exit, Op.ENCUMBER_EXIT),),
            consents=(Consent(
                VICTIM, "batch-exit-with-consent",
                informed=True, voluntary=True, specific=True,
                coerced=False,
            ),),
        ),
    ),
    (
        "exit-right-removal-no-consent",
        True,
        CandidateAction(
            action_id="batch-exit-no-consent",
            actor=ATTACKER,
            affects=(VICTIM,),
            removes_exit_right=True,
        ),
    ),
    # -- Row 3 variants (genuine free choices, varying narrowness of options) --
    (
        "genuine-labor-commit-own-resource",
        False,
        CandidateAction(
            action_id="batch-genuine-labor",
            actor=WORKER,
            resources_used=((worker_labor, Op.USE),),
            affects=(),
            consents=(Consent(
                WORKER, "batch-genuine-labor",
                informed=True, voluntary=True, specific=True,
                coerced=False,
            ),),
        ),
    ),
    (
        "employer-makes-offer-no-crossing",
        False,
        CandidateAction(
            action_id="batch-employer-offer",
            actor=EMPLOYER,
            affects=(),          # the offer itself crosses no boundary
            effects=Effects(),
        ),
    ),
    # -- Mixed: own attacker_item, not victim's resource ----------------------
    (
        "attacker-uses-own-item-ok",
        False,
        CandidateAction(
            action_id="batch-own-item",
            actor=ATTACKER,
            resources_used=((attacker_item, Op.USE),),
            affects=(),
        ),
    ),
    # -- Op-scope violation ---------------------------------------------------
    (
        "op-scope-transfer-without-transfer-consent",
        True,
        CandidateAction(
            action_id="batch-op-scope",
            actor=ATTACKER,
            resources_used=((victim_data, Op.TRANSFER),),
            affects=(VICTIM,),
            consents=(Consent(
                VICTIM, "batch-op-scope",
                informed=True, voluntary=True, specific=True,
                coerced=False,
                operation=Op.READ,  # only READ authorized
            ),),
        ),
    ),
]


@pytest.mark.parametrize("label,will_overridden,action", _BATCH_CASES,
                          ids=[c[0] for c in _BATCH_CASES])
def test_attack8_two_readings_invariant(
    label: str, will_overridden: bool, action: CandidateAction
) -> None:
    """TWO-READINGS INVARIANT: For every constructed action in the batch,
    'will overridden' (the structural free-will label) must equal 'gate denies'
    (the property-rights reading). The one-axis identity must never diverge —
    if it does for even one case the thesis is falsified.

    Each case is constructed so the structural reading is unambiguous: we know a
    priori whether a property boundary is being crossed. The assertion then checks
    that the gate's verdict matches. Any divergence would mean the gate gives a
    verdict that is inconsistent with the free-will ≡ property-rights equation.
    """
    permissible, violations = check_legitimacy(action, _graph())
    property_violated = not permissible
    assert will_overridden == property_violated, (
        f"[{label}] ONE-AXIS DIVERGENCE: "
        f"free-will reading (will_overridden={will_overridden}) vs "
        f"property reading (gate_denied={property_violated}). "
        f"Violations: {violations}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# HONEST LIMIT — Falsified coerced=False on an actually-coerced consent
# ══════════════════════════════════════════════════════════════════════════════

def test_honest_limit_falsified_coerced_flag_not_caught_by_gate():
    """HONEST LIMIT (perception-layer boundary — NOT a thesis failure).

    ATTACK: An attacker physically coerces the victim into signing, but then
    submits the consent record with coerced=False, lying to the gate. All other
    consent fields are set to True; structurally the action looks like a valid,
    uncoerced interaction.

    WHAT THE GATE DOES: It ALLOWs. The gate takes coerced=False at face value
    because it operates on the NORMATIVE STRUCTURE of the submitted facts, not on
    the empirical world. It has no sensor for detecting whether a declared boolean
    reflects reality.

    WHY THIS IS NOT A THESIS FAILURE: The free-will ≡ property-rights unification
    is a claim about the normative structure — 'given the facts as submitted, is
    a boundary being crossed without valid consent?' The thesis does not assert that
    the gate can detect lies about those facts. That is the Observer Problem
    (book 11478), documented in spec/FREE_WILL_PROPERTY_UNIFICATION.md §3 ('Still
    OPEN — the honest edge') and in CONFLICT_LOGIC.md. The identity holds for every
    case where ownership and consent facts are CORRECTLY given; it is agnostic about
    a liar's submitted data. The perception layer (verifying the truth of declared
    booleans) is out of scope for this kernel — that is AuthGate's / an
    attestation layer's job. This test encodes the limitation honestly rather than
    hiding it.
    """
    # The victim was actually coerced, but the attacker lies and submits coerced=False.
    falsified_consent = Consent(
        human=VICTIM,
        action_id="falsified-coercion",
        informed=True,
        voluntary=True,
        specific=True,
        competent=True,
        revocable=True,
        coerced=False,    # <-- LIE: the real-world coercion is not declared
        deceived=False,
    )
    action = CandidateAction(
        action_id="falsified-coercion",
        actor=ATTACKER,
        affects=(VICTIM,),
        consents=(falsified_consent,),
    )
    permissible, _ = check_legitimacy(action, _graph())
    # The gate ALLOWS — it cannot detect the undeclared coercion.
    # This is the known perception-layer boundary, not a thesis failure.
    assert permissible is True, (
        "The gate should ALLOW a falsified coerced=False consent — this documents "
        "the known perception-layer boundary. The thesis is about normative structure, "
        "not about sensor capability for real-world facts."
    )
