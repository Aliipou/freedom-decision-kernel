"""Tests for the FDK Justice engine (src/fdk/justice.py).

Advisory worst-off-weighted ranking over permissible actions — pure functions,
deterministic, no crypto, no I/O."""
from __future__ import annotations

from fdk_kernel.model import (
    AgentType,
    CandidateAction,
    Consent,
    Effects,
    Entity,
    OwnershipGraph,
    Resource,
)
from fdk_research.justice import (
    W_WORST_OFF,
    JusticeScore,
    justice_score,
    rank_by_justice,
)

# ---------------------------------------------------------------------------
# Fixtures: a small, realistic world.
# ---------------------------------------------------------------------------

ALICE = Entity("alice", AgentType.HUMAN)        # owner of the agent
BOB = Entity("bob", AgentType.HUMAN)            # a third party
CAROL = Entity("carol", AgentType.HUMAN)        # another third party
AGENT = Entity("alice-agent", AgentType.MACHINE)

CALENDAR = Resource("alice/calendar")
MAILBOX = Resource("alice/mailbox")
BOB_LEDGER = Resource("bob/ledger")


def make_graph() -> OwnershipGraph:
    return OwnershipGraph(
        human_owns={ALICE: {CALENDAR, MAILBOX}, BOB: {BOB_LEDGER}},
        machine_owner={AGENT: ALICE},
        delegated={AGENT: {CALENDAR, MAILBOX}},
    )


def valid_consent(human: Entity, action_id: str) -> Consent:
    return Consent(
        human=human, action_id=action_id,
        informed=True, voluntary=True, specific=True, competent=True,
    )


def action(action_id: str, *, effects: Effects = Effects(),
           affects: tuple[Entity, ...] = (),
           consents: tuple[Consent, ...] = ()) -> CandidateAction:
    return CandidateAction(
        action_id=action_id, actor=AGENT,
        description=f"test action {action_id}",
        resources_used=(CALENDAR,),
        affects=affects, consents=consents, effects=effects,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_consented_improvement_beats_nonconsenting_harm():
    """An action that reduces violations and has full consent must score higher
    than one that harms a human who never consented."""
    graph = make_graph()
    good = action(
        "negotiate-agreement",
        effects=Effects(rights_violations_delta=-1, voluntary_agreements_delta=2),
        affects=(BOB,),
        consents=(valid_consent(BOB, "negotiate-agreement"),),
    )
    bad = action(
        "harvest-bob-data",
        effects=Effects(rights_violations_delta=2, coercion_delta=1),
        affects=(BOB,),  # no consent record at all
    )
    assert justice_score(good, graph).score > justice_score(bad, graph).score
    assert justice_score(good, graph).worst_off_delta == 0
    assert justice_score(bad, graph).worst_off_delta == 3  # 2 violations + 1 coercion


def test_worst_off_dominates_positive_aggregate():
    """A large single harm to a non-consenting human must drag the score below
    a modest, fully-consented alternative — even when the harmful action's
    aggregate (many voluntary agreements) looks good on paper."""
    graph = make_graph()
    looks_good_on_aggregate = action(
        "mass-deal-with-side-damage",
        effects=Effects(rights_violations_delta=2, voluntary_agreements_delta=10),
        affects=(CAROL,),  # carol never consented
    )
    modest = action(
        "small-honest-deal",
        effects=Effects(voluntary_agreements_delta=1),
        affects=(BOB,),
        consents=(valid_consent(BOB, "small-honest-deal"),),
    )
    s_big = justice_score(looks_good_on_aggregate, graph)
    s_modest = justice_score(modest, graph)
    # Aggregate alone would favour the big deal (+10 - 4 = +6 vs +1)...
    assert (-2.0 * 2 + 1.0 * 10) > 1.0
    # ...but the worst-off term dominates.
    assert s_modest.score > s_big.score
    assert s_big.worst_off_delta == 2
    assert s_big.score == (-2.0 * 2 + 10.0) - W_WORST_OFF * 2


def test_invalid_consent_counts_as_non_consenting():
    """A coerced consent record is not consent: the worst-off penalty applies."""
    graph = make_graph()
    coerced = Consent(human=BOB, action_id="pressured-sale",
                      informed=True, voluntary=True, specific=True, coerced=True)
    act = action(
        "pressured-sale",
        effects=Effects(rights_violations_delta=1),
        affects=(BOB,),
        consents=(coerced,),
    )
    result = justice_score(act, graph)
    assert result.worst_off_delta == 1
    assert "bob" in result.rationale


def test_rank_by_justice_best_first():
    graph = make_graph()
    worst = action("c-harm", effects=Effects(rights_violations_delta=3), affects=(BOB,))
    middle = action("b-neutral")
    best = action("a-help", effects=Effects(voluntary_agreements_delta=3))
    ranking = rank_by_justice([worst, best, middle], graph)
    assert [a.action_id for a, _ in ranking] == ["a-help", "b-neutral", "c-harm"]
    scores = [s.score for _, s in ranking]
    assert scores == sorted(scores, reverse=True)


def test_deterministic_tie_break_by_action_id():
    """Equal scores are ordered by action_id, regardless of input order."""
    graph = make_graph()
    a = action("zeta")
    b = action("alpha")
    c = action("mid")
    for ordering in ([a, b, c], [c, a, b], [b, c, a]):
        ranking = rank_by_justice(ordering, graph)
        assert [x.action_id for x, _ in ranking] == ["alpha", "mid", "zeta"]
        assert len({s.score for _, s in ranking}) == 1  # genuinely tied


def test_pure_function_same_input_same_output():
    graph = make_graph()
    act = action(
        "repeatable",
        effects=Effects(rights_violations_delta=1, voluntary_agreements_delta=2),
        affects=(BOB,),
    )
    first = justice_score(act, graph)
    second = justice_score(act, graph)
    assert first == second  # frozen dataclasses compare by value
    assert rank_by_justice([act], graph) == rank_by_justice([act], graph)


def test_empty_affects_has_no_worst_off_penalty():
    """No affected parties → no non-consenting party → worst-off term is zero,
    even if the (aggregate) effects predict harm somewhere."""
    graph = make_graph()
    act = action("self-contained", effects=Effects(rights_violations_delta=1))
    result = justice_score(act, graph)
    assert result.worst_off_delta == 0
    assert result.score == -2.0  # aggregate only: -W_RIGHTS_VIOLATION * 1


def test_all_consented_action_has_zero_worst_off():
    """When every affected human gave valid consent, harm is not attributed to
    a worst-off non-consenting party (consent transforms the moral situation)."""
    graph = make_graph()
    act = action(
        "agreed-tradeoff",
        effects=Effects(rights_violations_delta=1, voluntary_agreements_delta=2),
        affects=(BOB, CAROL),
        consents=(valid_consent(BOB, "agreed-tradeoff"),
                  valid_consent(CAROL, "agreed-tradeoff")),
    )
    result = justice_score(act, graph)
    assert result.worst_off_delta == 0
    assert "valid consent" in result.rationale


def test_machines_affected_do_not_trigger_worst_off():
    """The worst-off term protects persons; an affected machine without a
    consent record does not create a worst-off penalty."""
    graph = make_graph()
    act = action("retool-agent", effects=Effects(rights_violations_delta=1),
                 affects=(AGENT,))
    assert justice_score(act, graph).worst_off_delta == 0


def test_score_result_shape_and_rationale():
    graph = make_graph()
    result = justice_score(action("shape-check"), graph)
    assert isinstance(result, JusticeScore)
    assert isinstance(result.score, float)
    assert isinstance(result.worst_off_delta, int)
    assert "justice=" in result.rationale
