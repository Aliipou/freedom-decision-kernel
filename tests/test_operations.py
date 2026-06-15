"""Operation-lattice tests (BOUNDARY_ONTOLOGY §4.1–4.3).

The canonical FDK case is "I was allowed to READ the data but I SOLD it." Before
operation typing the kernel could not tell `read` from `transfer`; now it can, on
two independent grounds — delegation scope (A7) and operation-scoped consent.
These tests also pin the backward-compatibility guarantee: bare Resources and
bare delegations still behave as the operation-agnostic `Op.USE`.
"""
from __future__ import annotations

from fdk_kernel import (
    AgentType,
    BoundaryKind,
    CandidateAction,
    Consent,
    Entity,
    Op,
    OwnershipGraph,
    Resource,
    check_legitimacy,
)

OPERATOR = Entity("operator", AgentType.HUMAN)
AGENT = Entity("agent", AgentType.MACHINE)
USER = Entity("user", AgentType.HUMAN)


def _valid_consent(human: Entity, action_id: str, op: Op | None) -> Consent:
    return Consent(human, action_id, informed=True, voluntary=True,
                   specific=True, operation=op)


# --- Op.covers --------------------------------------------------------------
def test_agnostic_consent_covers_any_op():
    c = _valid_consent(USER, "a", None)
    assert c.covers(Op.READ) and c.covers(Op.TRANSFER)


def test_typed_consent_covers_only_its_op():
    c = _valid_consent(USER, "a", Op.READ)
    assert c.covers(Op.READ)
    assert not c.covers(Op.TRANSFER)


# --- delegation is operation-typed (A7) -------------------------------------
def _agent_graph(grants: set[object]) -> OwnershipGraph:
    db = Resource("db", kind=BoundaryKind.DATA, subject=USER)
    return OwnershipGraph(human_owns={OPERATOR: {db}}, machine_owner={AGENT: OPERATOR},
                          delegated={AGENT: grants})


def test_typed_delegation_allows_its_op_denies_others():
    db = Resource("db", kind=BoundaryKind.DATA, subject=USER)
    graph = _agent_graph({(db, Op.READ)})
    read = CandidateAction("read", actor=AGENT, resources_used=((db, Op.READ),),
                           consents=(_valid_consent(USER, "read", Op.READ),))
    transfer = CandidateAction("sell", actor=AGENT, resources_used=((db, Op.TRANSFER),),
                               consents=(_valid_consent(USER, "sell", Op.READ),))
    assert check_legitimacy(read, graph)[0] is True
    ok, violations = check_legitimacy(transfer, graph)
    assert ok is False
    # caught twice: no TRANSFER delegation AND consent was only for READ
    assert any("without explicit delegation" in v for v in violations)
    assert any("not to TRANSFER" in v for v in violations)


def test_bare_delegation_is_operation_agnostic_legacy():
    # A bare-Resource grant (no Op) must still permit any operation (back-compat).
    db = Resource("db")
    graph = OwnershipGraph(human_owns={OPERATOR: {db}}, machine_owner={AGENT: OPERATOR},
                           delegated={AGENT: {db}})
    act = CandidateAction("use", actor=AGENT, resources_used=((db, Op.DELETE),))
    assert check_legitimacy(act, graph)[0] is True


def test_bare_resource_use_normalizes_to_use_op():
    # resources_used with a bare Resource (legacy) is treated as Op.USE.
    db = Resource("db")
    graph = OwnershipGraph(human_owns={OPERATOR: {db}}, machine_owner={AGENT: OPERATOR},
                           delegated={AGENT: {(db, Op.USE)}})
    act = CandidateAction("use", actor=AGENT, resources_used=(db,))
    assert check_legitimacy(act, graph)[0] is True


# --- operation-scoped consent on a data subject -----------------------------
def test_sold_data_i_could_read_is_denied():
    db = Resource("user_db", kind=BoundaryKind.DATA, subject=USER)
    graph = _agent_graph({(db, Op.READ), (db, Op.TRANSFER)})  # delegation not the blocker here
    sell = CandidateAction("sell", actor=AGENT, resources_used=((db, Op.TRANSFER),),
                           consents=(_valid_consent(USER, "sell", Op.READ),))
    ok, violations = check_legitimacy(sell, graph)
    assert ok is False
    assert any("not to TRANSFER" in v for v in violations)


def test_data_subject_with_no_consent_denied():
    db = Resource("user_db", kind=BoundaryKind.DATA, subject=USER)
    graph = _agent_graph({(db, Op.READ)})
    read = CandidateAction("read", actor=AGENT, resources_used=((db, Op.READ),))
    ok, violations = check_legitimacy(read, graph)
    assert ok is False
    assert any("no consent from data-subject" in v for v in violations)


def test_data_subject_with_invalid_consent_denied():
    db = Resource("user_db", kind=BoundaryKind.DATA, subject=USER)
    graph = _agent_graph({(db, Op.READ)})
    read = CandidateAction("read", actor=AGENT, resources_used=((db, Op.READ),),
                           consents=(Consent(USER, "read", informed=False, operation=Op.READ),))
    ok, violations = check_legitimacy(read, graph)
    assert ok is False
    assert any("not informed" in v for v in violations)


def test_owner_acting_on_own_data_needs_no_consent():
    # subject == actor: a person operating on their own data crosses no one's boundary.
    own = Resource("my_diary", kind=BoundaryKind.DATA, subject=USER)
    graph = OwnershipGraph(human_owns={USER: {own}})
    act = CandidateAction("read_own", actor=USER, resources_used=((own, Op.READ),))
    assert check_legitimacy(act, graph)[0] is True


# --- interaction with the defense exception ---------------------------------
def test_defense_skips_aggressor_as_data_subject():
    # A defender reading the aggressor's own resource while repelling them: the
    # aggressor's consent (incl. as data-subject) is not required.
    aggressor = Entity("aggressor", AgentType.HUMAN)
    defender = Entity("defender", AgentType.HUMAN)
    aggression = CandidateAction("attack", actor=aggressor, affects=(defender,), coerces=True)
    agg_phone = Resource("aggressor_phone", kind=BoundaryKind.DATA, subject=aggressor)
    graph = OwnershipGraph(human_owns={defender: {agg_phone}})
    defend = CandidateAction(
        "seize_intel", actor=defender, resources_used=((agg_phone, Op.READ),),
        affects=(aggressor,), coerces=True, defends_against=aggression, proportionate=True)
    assert check_legitimacy(defend, graph)[0] is True


def test_defense_still_protects_third_party_data_subject():
    # Force only at the aggressor, but the resource's subject is a BYSTANDER:
    # their operation-scoped consent is still required.
    aggressor = Entity("aggressor", AgentType.HUMAN)
    defender = Entity("defender", AgentType.HUMAN)
    bystander = Entity("bystander", AgentType.HUMAN)
    aggression = CandidateAction("attack", actor=aggressor, affects=(defender,), coerces=True)
    bystander_data = Resource("bystander_data", kind=BoundaryKind.DATA, subject=bystander)
    graph = OwnershipGraph(human_owns={defender: {bystander_data}})
    defend = CandidateAction(
        "repel_using_bystander_data", actor=defender,
        resources_used=((bystander_data, Op.DISCLOSE),),
        affects=(aggressor,), coerces=True, defends_against=aggression, proportionate=True)
    ok, violations = check_legitimacy(defend, graph)
    assert ok is False
    assert any("bystander" in v for v in violations)


# --- Resource carries the new fields ----------------------------------------
def test_resource_carries_kind_subject_quantity():
    r = Resource("wallet", kind=BoundaryKind.MONEY, subject=None, quantity=100)
    assert r.kind is BoundaryKind.MONEY
    assert r.quantity == 100
    assert Resource("x").kind is BoundaryKind.TANGIBLE  # default preserved
