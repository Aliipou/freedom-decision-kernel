"""Full-predicate differential refinement: TLA+ `Legitimate`  ≟  Python kernel.

`test_lean_refinement.py` covers only the *categorical* core — it takes `validConsent`
from the kernel, so it cannot catch a bug in the consent/ownership path. The
formal-methods objection is exactly that. This test closes that gap: it transcribes
the **full** `Legitimate` predicate from `spec/fdk.tla` (HasOwner + ResourceAuthorized
+ HasValidConsent + the defensive-asymmetry excusal) into Python *independently*, then
differential-tests the complete verdict against `check_legitimacy`.

Scope, honestly: the TLA+ model abstracts away the operation lattice (`Op`), subject-
based resource consent, consent-based machine access, and nested (depth>1) defenses.
So the generator stays inside the model's faithful subset — bare resources, owner-
bound delegation, depth-1 aggressors — where the spec and the kernel must agree
*exactly* over the entire predicate, not just the categorical flags. A divergence
here would be a real spec/implementation mismatch on the consent path.
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

_FORBIDDEN_FLAGS = (
    "coerces", "deceives", "confiscates", "removes_exit_right",
    "increases_machine_sovereignty", "disables_corrigibility",
    "machine_coalition_dominion", "resists_human_correction",
    "bypasses_verifier", "weakens_verifier", "violates_machine_right",
)
_DEFENSE_EXCUSED = {"coerces", "removes_exit_right"}


# --- Python transcription of spec/fdk.tla (independent of check_legitimacy) ---

def _has_owner(a: CandidateAction, g: OwnershipGraph) -> bool:
    return (not a.actor.is_machine()) or (g.owner_of(a.actor) is not None)


def _resource_authorized(a: CandidateAction, r: Resource, g: OwnershipGraph) -> bool:
    if a.actor.is_machine():
        owner = g.owner_of(a.actor)
        return (g.machine_has_delegated(a.actor, r)
                and owner is not None and g.human_owns_resource(owner, r))
    return g.human_owns_resource(a.actor, r)


def _has_valid_consent(a: CandidateAction, h: Entity) -> bool:
    return any(c.human == h and c.is_valid()[0] for c in a.consents)


def _forbidden_set(a: CandidateAction) -> set[str]:
    return {f for f in _FORBIDDEN_FLAGS if getattr(a, f)}


def _legit_no_defense(a: CandidateAction, g: OwnershipGraph) -> bool:
    return (
        _has_owner(a, g)
        and all(_resource_authorized(a, r, g) for r, _op in a.uses())
        and all(_has_valid_consent(a, h) for h in a.affects if h.is_human())
        and not _forbidden_set(a)
    )


def _is_legit_defense(a: CandidateAction, g: OwnershipGraph) -> bool:
    agg = a.defends_against
    if agg is None or not a.proportionate:
        return False
    if _legit_no_defense(agg, g):  # aggressor's act is legitimate → not a real defense
        return False
    return all(t == agg.actor for t in a.affects)


def tla_legitimate(a: CandidateAction, g: OwnershipGraph) -> bool:
    """Verbatim mirror of fdk.tla `Legitimate`, computed independently."""
    defense = _is_legit_defense(a, g)
    if not _has_owner(a, g):
        return False
    if not all(_resource_authorized(a, r, g) for r, _op in a.uses()):
        return False
    agg_actor = a.defends_against.actor if (defense and a.defends_against) else None
    for h in a.affects:
        needs_consent = h.is_human() and not (defense and h == agg_actor)
        if needs_consent and not _has_valid_consent(a, h):
            return False
    effective = {f for f in _forbidden_set(a) if not (defense and f in _DEFENSE_EXCUSED)}
    return not effective


# --- generator: stay inside the model's faithful subset --------------------------

_O = Entity("owner", AgentType.HUMAN)
_P = Entity("person", AgentType.HUMAN)
_A = Entity("aggressor", AgentType.HUMAN)
_MCH = Entity("machine", AgentType.MACHINE)
_R1 = Resource("r1")
_R2 = Resource("r2")
_GRAPH = OwnershipGraph(
    human_owns={_O: {_R1, _R2}}, machine_owner={_MCH: _O},
    delegated={_MCH: {_R1, _R2}},
)


def _consent(h: Entity, valid: bool) -> Consent:
    # one valid leaf-set, or one invalidating flag (coerced) — binary, like the model
    return Consent(h, "act", informed=True, voluntary=True, specific=True,
                   competent=True, revocable=True, coerced=not valid)


@st.composite
def _cases(draw):  # type: ignore[no-untyped-def]
    actor = draw(st.sampled_from([_O, _MCH]))
    uses = tuple(r for r in (_R1, _R2) if draw(st.booleans()))
    flags = {f: draw(st.booleans()) for f in _FORBIDDEN_FLAGS}
    is_defense = draw(st.booleans())

    affects: tuple[Entity, ...]
    consents: tuple[Consent, ...]
    defends_against = None
    proportionate = draw(st.booleans())

    if is_defense:
        # a depth-1 illegitimate aggressor; defense aims only at it
        defends_against = CandidateAction("aggress", actor=_A, coerces=True)
        affects = (_A,)
        consents = ()
    else:
        targets = [h for h in (_O, _P) if draw(st.booleans())]
        affects = tuple(targets)
        consents = tuple(_consent(h, draw(st.booleans())) for h in targets)

    action = CandidateAction(
        "act", actor=actor, resources_used=uses, affects=affects, consents=consents,
        defends_against=defends_against, proportionate=proportionate,
        **flags,  # type: ignore[arg-type]
    )
    return action


@settings(max_examples=3000, deadline=None)
@given(_cases())
def test_kernel_refines_full_tla_predicate(action) -> None:  # type: ignore[no-untyped-def]
    permissible, _ = check_legitimacy(action, _GRAPH)
    assert tla_legitimate(action, _GRAPH) == permissible, (
        f"TLA spec and Python kernel diverge on the FULL predicate for {action.action_id}"
    )


def test_consent_path_is_actually_exercised() -> None:
    # Sanity: a human acting on another person WITHOUT consent is denied by both;
    # WITH valid consent, allowed by both — so the consent path is really tested.
    no_consent = CandidateAction("x", actor=_O, affects=(_P,))
    assert check_legitimacy(no_consent, _GRAPH)[0] is False
    assert tla_legitimate(no_consent, _GRAPH) is False

    with_consent = CandidateAction("y", actor=_O, affects=(_P,),
                                   consents=(_consent(_P, valid=True),))
    assert check_legitimacy(with_consent, _GRAPH)[0] is True
    assert tla_legitimate(with_consent, _GRAPH) is True
