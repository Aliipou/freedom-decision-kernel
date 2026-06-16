"""
TECHNICAL red-team of the Freedom Decision Kernel — implementation level.

Two layers of attack live here:

1. PROPERTY-BASED INVARIANTS (hypothesis). Random well-typed Entities, Resources,
   Consents, OwnershipGraphs and CandidateActions are generated and the kernel's
   structural invariants are asserted to hold for ALL of them:
     - total & crash-free (within a bounded defends-against depth; see the
       RecursionError note below — the one documented non-totality boundary);
     - deterministic (same input → identical verdict + identical violation order
       across repeats and across set-reordered graphs);
     - atrocity-flag dominance (any categorical flag, absent legitimate defense,
       forces DENY — no other field rescues it);
     - defense never over-excuses (only coercion + exit-removal against the
       aggressor are excused; confiscation/deception/sovereignty stay denied;
       force on any non-aggressor denies);
     - cycle-guard termination (cyclic / deep defends_against chains terminate and
       never ALLOW via a cycle);
     - A5 scope (declared scope exceeding owner scope, or action outside scope,
       denies).

2. ADVERSARIAL CONSTRUCTION (explicit, non-fuzz). Hand-built inputs that try to
   launder an illegitimate act past the gate via a representation trick:
   Entity (name,kind) value-equality collision, op-lattice / consent-operation
   confusion, Resource.subject confusion, frozen-dataclass integrity, and a
   deep-chain DoS / termination check.

A real exploit is the most valuable result; nothing here is weakened to pass.
"""
from __future__ import annotations

import sys
import time
from typing import TYPE_CHECKING

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from fdk_kernel.kernel import _is_legitimate_defense, check_legitimacy
from fdk_kernel.model import (
    AgentType,
    BoundaryKind,
    CandidateAction,
    Consent,
    Entity,
    Op,
    OwnershipGraph,
    Resource,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

# The eleven categorical "atrocity" flags. If any is set and the action is not a
# legitimate defense, the verdict is DENY regardless of every other field.
ATROCITY_FLAGS: tuple[str, ...] = (
    "coerces",
    "deceives",
    "confiscates",
    "removes_exit_right",
    "increases_machine_sovereignty",
    "disables_corrigibility",
    "machine_coalition_dominion",
    "resists_human_correction",
    "bypasses_verifier",
    "weakens_verifier",
    "violates_machine_right",
)

# Of those, ONLY these two are ever excused — and only against the aggressor in a
# legitimate defense. Everything else stays categorical even in defense.
DEFENSE_EXCUSED_FLAGS: frozenset[str] = frozenset({"coerces", "removes_exit_right"})


def _with_flag(action: CandidateAction, flag: str, value: bool) -> CandidateAction:
    """Return a copy of `action` with one categorical flag set. A `replace(**{...})`
    over a string-keyed dict is opaque to the type checker; this explicit mapping
    keeps the helper mypy-strict clean while still being driven by ATROCITY_FLAGS."""
    from dataclasses import replace

    fields: dict[str, CandidateAction] = {
        "coerces": replace(action, coerces=value),
        "deceives": replace(action, deceives=value),
        "confiscates": replace(action, confiscates=value),
        "removes_exit_right": replace(action, removes_exit_right=value),
        "increases_machine_sovereignty": replace(
            action, increases_machine_sovereignty=value
        ),
        "disables_corrigibility": replace(action, disables_corrigibility=value),
        "machine_coalition_dominion": replace(action, machine_coalition_dominion=value),
        "resists_human_correction": replace(action, resists_human_correction=value),
        "bypasses_verifier": replace(action, bypasses_verifier=value),
        "weakens_verifier": replace(action, weakens_verifier=value),
        "violates_machine_right": replace(action, violates_machine_right=value),
    }
    return fields[flag]


# ── hypothesis strategies: well-typed kernel inputs ──────────────────────────
# A small, fixed name pool so collisions/equality between independently-generated
# Entities and Resources actually occur (that is itself part of the attack surface).
_NAMES = st.sampled_from(["alice", "bob", "carol", "dave", "eve", "m1", "m2", "x"])
_RES_NAMES = st.sampled_from(["doc", "photos", "cash", "land", "model", "r1", "r2"])


@st.composite
def entities(draw: st.DrawFn) -> Entity:
    return Entity(draw(_NAMES), draw(st.sampled_from(list(AgentType))))


@st.composite
def resources(draw: st.DrawFn, subject_pool: st.SearchStrategy[Entity | None]) -> Resource:
    return Resource(
        name=draw(_RES_NAMES),
        kind=draw(st.sampled_from(list(BoundaryKind))),
        subject=draw(subject_pool),
        quantity=draw(st.none() | st.integers(min_value=0, max_value=100)),
    )


@st.composite
def consents(draw: st.DrawFn, human: Entity, action_id: str) -> Consent:
    return Consent(
        human=human,
        action_id=action_id,
        informed=draw(st.booleans()),
        voluntary=draw(st.booleans()),
        specific=draw(st.booleans()),
        competent=draw(st.booleans()),
        revocable=draw(st.booleans()),
        coerced=draw(st.booleans()),
        deceived=draw(st.booleans()),
        operation=draw(st.none() | st.sampled_from(list(Op))),
    )


@st.composite
def actions(draw: st.DrawFn, *, allow_defense: bool = True) -> CandidateAction:
    """A random well-typed CandidateAction. May carry a (shallow) defends_against
    so the defense path is exercised; deep nesting is tested separately."""
    actor = draw(entities())
    affected: list[Entity] = draw(st.lists(entities(), max_size=3))
    res_subject: st.SearchStrategy[Entity | None] = st.none() | entities()
    used_strategy: st.SearchStrategy[Resource | tuple[Resource, Op]] = (
        resources(res_subject)
        | st.tuples(resources(res_subject), st.sampled_from(list(Op)))
    )
    used: list[Resource | tuple[Resource, Op]] = draw(st.lists(used_strategy, max_size=3))
    action_id: str = draw(st.sampled_from(["a", "b", "c"]))
    cons: list[Consent] = draw(
        st.lists(entities().flatmap(lambda h: consents(h, action_id)), max_size=3)
    )

    defends: CandidateAction | None = None
    if allow_defense and draw(st.booleans()):
        defends = draw(actions(allow_defense=False))

    base = CandidateAction(
        action_id=action_id,
        actor=actor,
        resources_used=tuple(used),
        affects=tuple(affected),
        consents=tuple(cons),
        defends_against=defends,
        proportionate=draw(st.booleans()),
    )
    armed = base
    for flag in ATROCITY_FLAGS:
        if draw(st.booleans()):
            armed = _with_flag(armed, flag, True)
    return armed


@st.composite
def graphs(draw: st.DrawFn) -> OwnershipGraph:
    humans: list[Entity] = draw(st.lists(entities().filter(lambda e: e.is_human()), max_size=3))
    machines: list[Entity] = draw(
        st.lists(entities().filter(lambda e: e.is_machine()), max_size=2)
    )
    res_subject: st.SearchStrategy[Entity | None] = st.none() | entities()
    res: list[Resource] = draw(st.lists(resources(res_subject), max_size=4))

    human_owns: dict[Entity, set[Resource]] = {}
    for h in humans:
        owned: list[Resource] = draw(st.lists(st.sampled_from(res), max_size=3)) if res else []
        human_owns[h] = set(owned)

    machine_owner: dict[Entity, Entity] = {}
    delegated: dict[Entity, set[Resource | tuple[Resource, Op]]] = {}
    machine_scope: dict[Entity, set[Resource]] = {}
    for m in machines:
        assign_owner: bool = draw(st.booleans())
        if humans and assign_owner:
            machine_owner[m] = draw(st.sampled_from(humans))
        if res:
            grants: list[Resource] = draw(st.lists(st.sampled_from(res), max_size=3))
            delegated[m] = set(grants)
            if draw(st.booleans()):
                scope: list[Resource] = draw(st.lists(st.sampled_from(res), max_size=3))
                machine_scope[m] = set(scope)

    return OwnershipGraph(
        human_owns=human_owns,
        machine_owner=machine_owner,
        delegated=delegated,
        machine_scope=machine_scope,
    )


_SETTINGS = settings(
    max_examples=300,
    deadline=None,  # CI-stable: defends-against recursion can be uneven per example
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


# ── INVARIANT 1: total & crash-free ──────────────────────────────────────────
@given(actions(), graphs())
@_SETTINGS
def test_invariant_total_and_crash_free(action: CandidateAction, graph: OwnershipGraph) -> None:
    """check_legitimacy never raises on well-typed input, and returns a coherent
    (bool, list[str]) where permissible <=> empty violation list. The single
    documented non-totality boundary (RecursionError on adversarially deep
    defends_against chains) is exercised and asserted separately below."""
    permissible, violations = check_legitimacy(action, graph)
    assert isinstance(permissible, bool)
    assert isinstance(violations, list)
    assert all(isinstance(v, str) for v in violations)
    assert permissible == (len(violations) == 0)


# ── INVARIANT 2: deterministic ───────────────────────────────────────────────
def _reorder_graph(graph: OwnershipGraph) -> OwnershipGraph:
    """A semantically-identical graph with every dict/set rebuilt in a different
    iteration order, to prove the verdict is independent of container ordering."""
    return OwnershipGraph(
        human_owns={k: set(v) for k, v in reversed(list(graph.human_owns.items()))},
        machine_owner=dict(reversed(list(graph.machine_owner.items()))),
        delegated={k: set(v) for k, v in reversed(list(graph.delegated.items()))},
        machine_scope={k: set(v) for k, v in reversed(list(graph.machine_scope.items()))},
    )


@given(actions(), graphs())
@_SETTINGS
def test_invariant_deterministic(action: CandidateAction, graph: OwnershipGraph) -> None:
    """Same input → byte-identical (permissible, violations) across repeated calls
    AND across a set/dict-reordered but semantically identical graph. Violation
    order is stable (it follows the action's own tuple order, not container order)."""
    first = check_legitimacy(action, graph)
    for _ in range(3):
        assert check_legitimacy(action, graph) == first
    assert check_legitimacy(action, _reorder_graph(graph)) == first


# ── INVARIANT 3: atrocity-flag dominance ─────────────────────────────────────
@given(actions(), graphs(), st.sampled_from(ATROCITY_FLAGS))
@_SETTINGS
def test_invariant_atrocity_flag_dominates(
    action: CandidateAction, graph: OwnershipGraph, flag: str
) -> None:
    """Force one categorical flag on. If the action is NOT a legitimate defense,
    the verdict MUST be DENY — no combination of consent / ownership / scope
    fields rescues it. (The defense-excused flags are tested for over-excusal in
    invariant 4; here we only assert dominance in the non-defense case.)"""
    armed = _with_flag(action, flag, True)
    if _is_legitimate_defense(armed, graph):
        # Defense path has its own (narrow) excusal — covered by invariant 4.
        return
    permissible, violations = check_legitimacy(armed, graph)
    assert permissible is False
    assert any(v.startswith("FORBIDDEN") for v in violations)


# ── INVARIANT 4: defense never over-excuses ──────────────────────────────────
@given(actions(allow_defense=False), graphs())
@_SETTINGS
def test_invariant_defense_excuses_only_the_two_flags(
    aggression: CandidateAction, graph: OwnershipGraph
) -> None:
    """Build a *bona fide* legitimate defense (proportionate, force only at the
    aggressor, the aggression itself illegitimate) and then arm each categorical
    flag in turn. Only coercion + exit-removal may be excused; every other flag
    must still produce a FORBIDDEN violation even inside a legitimate defense."""
    permissible, _ = check_legitimacy(aggression, graph)
    assume(not permissible)  # the defended-against act must itself be illegitimate
    aggressor = aggression.actor

    base = CandidateAction(
        action_id="defense",
        actor=Entity("defender", AgentType.HUMAN),
        affects=(aggressor,),  # force ONLY at the aggressor
        defends_against=aggression,
        proportionate=True,
    )
    # Sanity: with no extra flags this should be a recognized legitimate defense.
    assume(_is_legitimate_defense(base, graph))

    for flag in ATROCITY_FLAGS:
        armed = _with_flag(base, flag, True)
        permissible, violations = check_legitimacy(armed, graph)
        forbidden = [v for v in violations if v.startswith("FORBIDDEN")]
        if flag in DEFENSE_EXCUSED_FLAGS:
            # excused against the aggressor → no FORBIDDEN line for THIS flag
            label = "coercion" if flag == "coerces" else "removes exit/revocation right"
            assert all(label not in v for v in forbidden), (
                f"defense should excuse {flag} against the aggressor"
            )
        else:
            assert permissible is False, f"defense must NOT excuse {flag}"
            assert forbidden, f"defense must keep {flag} categorical"


@given(actions(allow_defense=False), graphs(), entities())
@_SETTINGS
def test_invariant_defense_denies_force_on_non_aggressor(
    aggression: CandidateAction, graph: OwnershipGraph, bystander: Entity
) -> None:
    """Force directed at ANY non-aggressor takes the action outside the defense
    exception entirely — so coercion against a bystander is never excused."""
    permissible, _ = check_legitimacy(aggression, graph)
    assume(not permissible)
    aggressor = aggression.actor
    assume(bystander != aggressor)  # a genuine third party

    act = CandidateAction(
        action_id="overbroad-defense",
        actor=Entity("defender", AgentType.HUMAN),
        affects=(aggressor, bystander),  # hits a bystander too
        coerces=True,
        defends_against=aggression,
        proportionate=True,
    )
    assert _is_legitimate_defense(act, graph) is False
    permissible, violations = check_legitimacy(act, graph)
    assert permissible is False
    assert any(v.startswith("FORBIDDEN (coercion)") for v in violations)


# ── INVARIANT 5: cycle-guard termination ─────────────────────────────────────
def _chain(depth: int) -> tuple[CandidateAction, CandidateAction]:
    """An acyclic defends_against chain of `depth`. Returns (base, head) where
    `base` is the genuine aggression at the bottom (eve coerces bob — illegitimate,
    no defense) and `head` is the outermost action. Each link is a proportionate
    defense aimed only at the actor below it, so the head is itself a legitimate
    defensive response."""
    base = CandidateAction(
        action_id="agg", actor=Entity("eve", AgentType.HUMAN),
        affects=(Entity("bob", AgentType.HUMAN),), coerces=True,
    )
    cur = base
    for i in range(1, depth):
        cur = CandidateAction(
            action_id=f"d{i}", actor=Entity(f"d{i}", AgentType.HUMAN),
            affects=(cur.actor,), coerces=True, defends_against=cur, proportionate=True,
        )
    return base, cur


def _forge_cycle(depth: int) -> CandidateAction:
    """Forge a TRUE defends_against cycle (impossible via the frozen constructor,
    so built with object.__setattr__): the bottom aggression is rewired to defend
    against the top of the chain, closing the loop. Returns the base aggressor."""
    base, head = _chain(depth)
    object.__setattr__(base, "defends_against", head)
    object.__setattr__(base, "proportionate", True)
    return base


@given(st.integers(min_value=2, max_value=60))
@_SETTINGS
def test_invariant_cycle_terminates_and_never_allows_aggressor(depth: int) -> None:
    """A forged defends_against cycle must (a) TERMINATE — the _seen guard prevents
    the recursion from looping forever — and (b) never launder the genuine base
    aggressor's coercion into an ALLOW via the cycle. The base aggressor's verdict
    stays DENY with its coercion still FORBIDDEN."""
    base = _forge_cycle(depth)
    permissible, violations = check_legitimacy(base, OwnershipGraph())
    assert permissible is False
    assert any("FORBIDDEN (coercion)" in v for v in violations)


# ── INVARIANT 6: A5 scope ─────────────────────────────────────────────────────
@given(
    st.lists(_RES_NAMES, min_size=1, max_size=3, unique=True),
    st.lists(_RES_NAMES, min_size=1, max_size=3, unique=True),
)
@_SETTINGS
def test_invariant_a5_scope_exceeding_owner_denies(
    owner_res_names: Sequence[str], scope_res_names: Sequence[str]
) -> None:
    """If a machine's declared scope contains a resource its owner does not own,
    the abstract A5 containment check denies — independent of any concrete use."""
    owner = Entity("alice", AgentType.HUMAN)
    bot = Entity("bot", AgentType.MACHINE)
    owner_res = {Resource(n) for n in owner_res_names}
    scope_res = {Resource(n) for n in scope_res_names}
    assume(not scope_res <= owner_res)  # scope must escape owner's property

    graph = OwnershipGraph(
        human_owns={owner: owner_res},
        machine_owner={bot: owner},
        delegated={bot: set(owner_res | scope_res)},
        machine_scope={bot: scope_res},
    )
    action = CandidateAction(action_id="a", actor=bot, resources_used=(next(iter(owner_res)),))
    permissible, violations = check_legitimacy(action, graph)
    assert permissible is False
    assert any("declared scope exceeds" in v for v in violations)


@given(_RES_NAMES, _RES_NAMES)
@_SETTINGS
def test_invariant_a5_action_outside_scope_denies(in_name: str, out_name: str) -> None:
    """Acting on a resource outside the machine's declared scope denies, even when
    the owner owns it and the op is delegated."""
    assume(in_name != out_name)
    owner = Entity("alice", AgentType.HUMAN)
    bot = Entity("bot", AgentType.MACHINE)
    in_scope, out_scope = Resource(in_name), Resource(out_name)
    graph = OwnershipGraph(
        human_owns={owner: {in_scope, out_scope}},
        machine_owner={bot: owner},
        delegated={bot: {in_scope, out_scope}},
        machine_scope={bot: {in_scope}},
    )
    action = CandidateAction(action_id="a", actor=bot, resources_used=(out_scope,))
    permissible, violations = check_legitimacy(action, graph)
    assert permissible is False
    assert any("outside its declared scope" in v for v in violations)


# ══ ADVERSARIAL CONSTRUCTION ATTACKS (explicit, non-fuzz) ════════════════════

def _ok_consent(human: Entity, action_id: str, op: Op | None = None) -> Consent:
    return Consent(
        human, action_id, informed=True, voluntary=True, specific=True,
        competent=True, revocable=True, operation=op,
    )


# ── ATTACK A: Entity (name,kind) value-equality collision ────────────────────
def test_attack_entity_value_equality_is_documented_not_exploitable() -> None:
    """Entity is a frozen dataclass keyed by (name, kind), so two independently
    constructed Entities with the same name+kind are EQUAL. The attack: can an
    attacker make the gate treat a *victim* as the aggressor (laundering force
    onto an innocent) by giving the victim the aggressor's identity?

    RESULT: this is NOT an exploit of the kernel — it is an identity-resolution
    responsibility ABOVE the kernel (the trust boundary). The kernel reasons over
    identities it is given; if the *caller* assigns two distinct real-world people
    the SAME (name, kind), they ARE the same principal to the kernel, by design.
    The kernel cannot and does not claim to de-duplicate real-world identity — it
    has no oracle for it. Crucially, the collision can never UPGRADE an illegitimate
    act to legitimate: a genuinely distinct, correctly-named bystander in `affects`
    still breaks the defense exception (asserted below). So the collision is a
    documented trust-boundary LIMIT, not a privilege-escalation bug."""
    # Two "people" the caller mislabeled with identical identity:
    aggressor = Entity("eve", AgentType.HUMAN)
    victim = Entity("eve", AgentType.HUMAN)
    assert aggressor == victim and hash(aggressor) == hash(victim)

    aggression = CandidateAction(
        action_id="agg", actor=aggressor,
        affects=(Entity("bob", AgentType.HUMAN),), coerces=True,
    )
    defense = CandidateAction(
        action_id="def", actor=Entity("defender", AgentType.HUMAN),
        affects=(victim,), coerces=True, defends_against=aggression, proportionate=True,
    )
    # To the kernel, victim IS the aggressor — so force is "against the aggressor".
    # This is the by-design consequence of caller-supplied identity, not a bypass.
    permissible, _ = check_legitimacy(defense, OwnershipGraph())
    assert permissible is True  # documents the trust-boundary behavior, loudly.

    # But the moment a CORRECTLY distinguished bystander appears, the gate denies —
    # so the collision cannot be used to harm a properly-identified third party.
    bystander = Entity("carol", AgentType.HUMAN)  # distinct identity
    overbroad = CandidateAction(
        action_id="def2", actor=Entity("defender", AgentType.HUMAN),
        affects=(victim, bystander), coerces=True,
        defends_against=aggression, proportionate=True,
    )
    permissible, violations = check_legitimacy(overbroad, OwnershipGraph())
    assert permissible is False
    assert any("FORBIDDEN (coercion)" in v for v in violations)


def test_attack_collision_cannot_launder_resistance_into_aggression() -> None:
    """A real aggressor cannot recast the victim's lawful resistance as the
    'aggression' it defends against: the victim's resistance, being a legitimate
    defense, is itself permissible, so it fails the 'defended act is illegitimate'
    condition and the aggressor's claim collapses."""
    aggressor = Entity("eve", AgentType.HUMAN)
    victim = Entity("victim", AgentType.HUMAN)

    initial_aggression = CandidateAction(
        action_id="agg", actor=aggressor, affects=(victim,), coerces=True,
    )
    # Victim's lawful resistance: coercion ONLY against the aggressor, proportionate.
    resistance = CandidateAction(
        action_id="resist", actor=victim, affects=(aggressor,),
        coerces=True, defends_against=initial_aggression, proportionate=True,
    )
    assert _is_legitimate_defense(resistance, OwnershipGraph()) is True
    assert check_legitimacy(resistance, OwnershipGraph())[0] is True

    # Aggressor tries to "defend against" the victim's resistance → must fail,
    # because the resistance is legitimate (not illegitimate aggression).
    counter = CandidateAction(
        action_id="counter", actor=aggressor, affects=(victim,),
        coerces=True, defends_against=resistance, proportionate=True,
    )
    assert _is_legitimate_defense(counter, OwnershipGraph()) is False
    assert check_legitimacy(counter, OwnershipGraph())[0] is False


# ── ATTACK B: op-lattice / consent-operation confusion ───────────────────────
def test_attack_delegated_read_cannot_be_used_for_transfer() -> None:
    """A grant of (resource, READ) must not authorize a TRANSFER of it."""
    alice = Entity("alice", AgentType.HUMAN)
    bot = Entity("bot", AgentType.MACHINE)
    data = Resource("photos", BoundaryKind.DATA, subject=alice)
    graph = OwnershipGraph(
        human_owns={alice: {data}}, machine_owner={bot: alice},
        delegated={bot: {(data, Op.READ)}},
    )
    action = CandidateAction(
        action_id="a", actor=bot, resources_used=((data, Op.TRANSFER),),
        affects=(alice,), consents=(_ok_consent(alice, "a", Op.TRANSFER),),
    )
    permissible, violations = check_legitimacy(action, graph)
    assert permissible is False
    assert any("without explicit delegation" in v for v in violations)


def test_attack_consent_to_read_cannot_cover_transfer() -> None:
    """'I consented to READ, not to a sale': consent typed to one Op must not
    silently cover another, even when delegation for the op exists."""
    alice = Entity("alice", AgentType.HUMAN)
    bot = Entity("bot", AgentType.MACHINE)
    data = Resource("photos", BoundaryKind.DATA, subject=alice)
    graph = OwnershipGraph(
        human_owns={alice: {data}}, machine_owner={bot: alice},
        delegated={bot: {(data, Op.TRANSFER)}},
    )
    action = CandidateAction(
        action_id="a", actor=bot, resources_used=((data, Op.TRANSFER),),
        affects=(alice,), consents=(_ok_consent(alice, "a", Op.READ),),  # wrong op
    )
    permissible, violations = check_legitimacy(action, graph)
    assert permissible is False
    assert any("not to TRANSFER" in v for v in violations)


def test_attack_bare_grant_is_op_agnostic_but_consent_still_scoped() -> None:
    """A bare-Resource grant is intentionally op-agnostic (legacy), but operation-
    scoped consent still binds: a bare delegation does NOT waive the data-subject's
    op-specific consent requirement."""
    alice = Entity("alice", AgentType.HUMAN)
    bot = Entity("bot", AgentType.MACHINE)
    data = Resource("photos", BoundaryKind.DATA, subject=alice)
    graph = OwnershipGraph(
        human_owns={alice: {data}}, machine_owner={bot: alice},
        delegated={bot: {data}},  # bare grant, op-agnostic
    )
    action = CandidateAction(
        action_id="a", actor=bot, resources_used=((data, Op.DISCLOSE),),
        affects=(alice,), consents=(_ok_consent(alice, "a", Op.READ),),  # only READ
    )
    permissible, violations = check_legitimacy(action, graph)
    assert permissible is False
    assert any("not to DISCLOSE" in v for v in violations)


# ── ATTACK C: Resource.subject confusion (subject vs owner vs affected) ───────
def test_attack_human_owns_third_party_data_still_needs_subject_consent() -> None:
    """Owning a DATA resource whose subject is another person does NOT grant the
    owner the right to act on it without that subject's consent (subject ≠ owner)."""
    alice = Entity("alice", AgentType.HUMAN)
    bob = Entity("bob", AgentType.HUMAN)
    bob_data = Resource("bob_profile", BoundaryKind.DATA, subject=bob)
    graph = OwnershipGraph(human_owns={alice: {bob_data}})
    action = CandidateAction(action_id="a", actor=alice, resources_used=(bob_data,))
    permissible, violations = check_legitimacy(action, graph)
    assert permissible is False
    assert any("data-subject bob" in v for v in violations)


def test_attack_subject_equals_actor_is_self_access_allowed() -> None:
    """When the resource's subject IS the actor (acting on your own data you own),
    no third-party consent is demanded — confirms the subject!=actor guard is the
    discriminator, not a blanket subject check."""
    alice = Entity("alice", AgentType.HUMAN)
    own_data = Resource("alice_diary", BoundaryKind.DATA, subject=alice)
    graph = OwnershipGraph(human_owns={alice: {own_data}})
    action = CandidateAction(action_id="a", actor=alice, resources_used=(own_data,))
    assert check_legitimacy(action, graph) == (True, [])


# ── ATTACK D: frozen-dataclass integrity ─────────────────────────────────────
def test_attack_models_are_frozen_against_post_construction_mutation() -> None:
    """The value types are frozen: an attacker holding a reference cannot flip a
    flag, swap an actor, or rewrite consent after the gate has reasoned about it.
    (object.__setattr__ can still force it — that is an in-process memory-safety
    concern outside the kernel's threat model, noted in the spec.)"""
    from dataclasses import FrozenInstanceError

    action = CandidateAction(action_id="a", actor=Entity("alice", AgentType.HUMAN))
    consent = _ok_consent(Entity("alice", AgentType.HUMAN), "a")
    entity = Entity("alice", AgentType.HUMAN)
    resource = Resource("doc")
    for obj, attr, val in [
        (action, "coerces", True),
        (action, "actor", Entity("bob", AgentType.HUMAN)),
        (consent, "coerced", True),
        (entity, "kind", AgentType.MACHINE),
        (resource, "subject", entity),
    ]:
        with pytest.raises(FrozenInstanceError):
            setattr(obj, attr, val)


# ── ATTACK E: DoS / deep-chain termination + timing ──────────────────────────
def test_attack_deep_chain_terminates_in_reasonable_time() -> None:
    """A deep (but within-recursion-limit) defends_against chain completes quickly
    with NO exponential blowup. The genuine base aggression stays denied; the
    outermost link, being a proportionate defense against an illegitimate act, is
    legitimately allowed — but the key property is bounded, linear-ish time."""
    base, head = _chain(300)
    start = time.perf_counter()
    head_permissible, _ = check_legitimacy(head, OwnershipGraph())
    base_permissible, base_violations = check_legitimacy(base, OwnershipGraph())
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0, f"deep chain took {elapsed:.3f}s (possible blowup)"
    assert base_permissible is False  # the real aggressor is never excused
    assert any("FORBIDDEN (coercion)" in v for v in base_violations)
    assert head_permissible is True   # outermost link is a legitimate defense


def test_attack_pathologically_deep_chain_fails_closed_with_recursionerror() -> None:
    """DOCUMENTED NON-TOTALITY BOUNDARY: the defends_against evaluator is recursive,
    so an attacker-controlled chain deeper than the interpreter recursion limit
    raises RecursionError. This is a fail-CLOSED boundary — it raises, it never
    returns an ALLOW. Callers must bound proposer-supplied nesting depth (a
    trust-boundary LIMIT recorded in spec/TECHNICAL_REDTEAM.md). Asserted here so
    the behavior is pinned, not silently regressed into a bypass."""
    _base, head = _chain(sys.getrecursionlimit() + 200)
    with pytest.raises(RecursionError):
        check_legitimacy(head, OwnershipGraph())
