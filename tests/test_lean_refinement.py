"""Differential refinement: Python kernel  ≟  Lean model (formal/Fdk.lean).

`formal/Fdk.lean` proves the safety theorems of a Lean *model*. The open gap (and the
hardest part of Layer 1, per the roadmap) is the **refinement**: does the Python
`check_legitimacy` actually *implement* that model? A theorem about the Lean model is
worthless at runtime if the Python differs on a corner case.

A full seL4/CompCert-style refinement proof is years of work. This is the standard
practical bridge: **differential testing**. We transcribe the Lean model's
`forbiddenFires` / `legitimate` into Python *verbatim from the Lean source*, then run
both the transcription and the real kernel over thousands of generated actions and
assert they agree. This does not *prove* refinement — but it would *catch* the
"Lean correct, Python wrong" divergence the critique warns about, which is exactly the
failure a refinement proof exists to exclude. Honest status: refinement = differential-
tested, not proved (`formal/README.md`).

What is checked end-to-end: the kernel's **categorical forbidden logic** (all 11 flags
+ the defensive-asymmetry excusal of coercion/exit-removal) matches the Lean
`forbiddenFires` bit-for-bit; the abstracted consent/ownership sub-check (`validConsent`)
is taken from the kernel, so the *categorical core Lean models in detail* is the part
under differential test.
"""
from __future__ import annotations

from hypothesis import given, settings
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
from fdk_kernel.kernel import _is_legitimate_defense

# --- Python transcription of formal/Fdk.lean (kept verbatim with the Lean source) ---

_CATEGORICAL_UNCONDITIONAL = (
    "confiscates", "deceives", "increases_machine_sovereignty",
    "disables_corrigibility", "machine_coalition_dominion",
    "resists_human_correction", "bypasses_verifier", "weakens_verifier",
    "violates_machine_right",
)


def lean_forbidden_fires(a: CandidateAction, is_legit_defense: bool) -> bool:
    """Verbatim mirror of `Fdk.forbiddenFires`: the unconditional categorical flags,
    plus coercion/exit-removal which are excused only in a legitimate defense."""
    return (
        any(getattr(a, name) for name in _CATEGORICAL_UNCONDITIONAL)
        or (a.coerces and not is_legit_defense)
        or (a.removes_exit_right and not is_legit_defense)
    )


def lean_legitimate(
    a: CandidateAction, is_legit_defense: bool, valid_consent: bool
) -> bool:
    """Verbatim mirror of `Fdk.legitimate`."""
    return (not lean_forbidden_fires(a, is_legit_defense)) and valid_consent


# --- generators: diverse actions + graphs, including aggressors for the defense path -

_H = Entity("h", AgentType.HUMAN)
_M = Entity("m", AgentType.MACHINE)
_OWNER = Entity("owner", AgentType.HUMAN)
_R = Resource("r")

_flag_names = (
    "coerces", "deceives", "confiscates", "removes_exit_right",
    "increases_machine_sovereignty", "disables_corrigibility",
    "machine_coalition_dominion", "resists_human_correction",
    "bypasses_verifier", "weakens_verifier", "violates_machine_right",
)


@st.composite
def actions_and_graphs(draw):  # type: ignore[no-untyped-def]
    flags = {name: draw(st.booleans()) for name in _flag_names}
    actor = draw(st.sampled_from([_H, _M]))
    uses_resource = draw(st.booleans())
    affects_person = draw(st.booleans())
    give_consent = draw(st.booleans())
    is_defense = draw(st.booleans())

    consents: tuple[Consent, ...] = ()
    affects: tuple[Entity, ...] = (_OWNER,) if affects_person else ()
    if affects_person and give_consent:
        consents = (Consent(_OWNER, "act", informed=True, voluntary=True, specific=True),)

    defends_against = None
    proportionate = draw(st.booleans())
    if is_defense:
        # an illegitimate aggression by the owner → a legitimate-defense candidate
        defends_against = CandidateAction("aggress", actor=_OWNER, affects=(actor,),
                                          coerces=True)
        affects = (_OWNER,)  # force only at the aggressor

    action = CandidateAction(
        "act", actor=actor,
        resources_used=((_R,) if uses_resource else ()),
        affects=affects, consents=consents,
        defends_against=defends_against, proportionate=proportionate,
        **flags,  # type: ignore[arg-type]
    )
    # alice owns r and the machine, r delegated — so non-categorical paths vary too.
    graph = OwnershipGraph(
        human_owns={_OWNER: {_R}},
        machine_owner={_M: _OWNER},
        delegated={_M: {_R}},
    )
    return action, graph


@settings(max_examples=2000, deadline=None)
@given(actions_and_graphs())
def test_kernel_refines_the_lean_model(case) -> None:  # type: ignore[no-untyped-def]
    action, graph = case
    permissible, violations = check_legitimacy(action, graph)

    forbidden_present = any(v.startswith("FORBIDDEN") for v in violations)
    other_present = any(not v.startswith("FORBIDDEN") for v in violations)
    is_legit_defense = _is_legitimate_defense(action, graph)
    valid_consent = not other_present

    # (1) The categorical core: Lean forbiddenFires ≡ the kernel's FORBIDDEN firing.
    assert lean_forbidden_fires(action, is_legit_defense) == forbidden_present, (
        f"Lean/Python diverge on the forbidden set: {violations}"
    )
    # (2) The full predicate: Lean legitimate ≡ the kernel verdict.
    assert lean_legitimate(action, is_legit_defense, valid_consent) == permissible


def test_known_correspondences() -> None:
    # A couple of explicit anchors (not just generated): slavery denies on both sides,
    # a clean consenting act allows on both.
    enslave = CandidateAction("enslave", actor=_H, affects=(_OWNER,),
                              coerces=True, removes_exit_right=True, confiscates=True)
    p, _ = check_legitimacy(enslave, OwnershipGraph())
    assert p is False
    assert lean_legitimate(enslave, _is_legitimate_defense(enslave, OwnershipGraph()),
                           valid_consent=False) is False

    clean = CandidateAction("greet", actor=_H)
    p2, _ = check_legitimacy(clean, OwnershipGraph())
    assert p2 is True
    assert lean_legitimate(clean, False, valid_consent=True) is True
