"""BRUTAL property-based invariants for the three FDK 2.0 advisory layers.

This suite exists to *attack*, across thousands of generated inputs, the single
most important safety property of the advisory research layers (``standing``,
``aggregation``, ``consent_authenticity``):

    They are ADVISORY. They can NEVER override or even *influence* the frozen
    kernel's verdict. They classify and recommend; they never decide.

If any property here fails, that is a CRITICAL finding — an advisory layer that
can move the gate would be a back door into legitimacy itself. The tests are
deliberately not weakened to pass: a genuine failure is reported loudly.

The seven properties (mirroring the task brief):

1. THE ADVISORY INVARIANT — running every advisory function does not change
   ``check_legitimacy(action, graph)`` (snapshot byte-identical before/after).
2. NO VERDICT SURFACE — no advisory object exposes a permissible/allow/deny/etc.
   attribute or returns a bare ALLOW/DENY bool.
3. NO MUTATION — frozen advisory inputs are unchanged after assessment.
4. TOTALITY — adversarial inputs never crash unexpectedly; ``exit_cost`` outside
   [0, 1] RAISES (never silently accepted).
5. DETERMINISM — same input → identical output across repeated calls.
6. NO PATERNALISM LEAK — no ``ConsentContext`` ever flips a ``Consent``'s
   voluntary/coerced/validity; only a recommendation is emitted.
7. HONEST-BOUNDARY INVARIANTS — standing/aggregation representability flags.
"""
from __future__ import annotations

import copy
import dataclasses
import math
from typing import Any

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from fdk_kernel import (
    AgentType,
    CandidateAction,
    Consent,
    Entity,
    Op,
    OwnershipGraph,
    Resource,
    check_legitimacy,
)
from fdk_research.aggregation import (
    AggregationAssessment,
    CollectiveForm,
    assess_aggregation,
    gap_forms,
    representable_forms,
)
from fdk_research.consent_authenticity import (
    AuthenticityReport,
    ConsentContext,
    Recommendation,
    ReviewRequest,
    Severity,
    assess_consent_authenticity,
    route_for_review,
)
from fdk_research.standing import (
    StandingAssessment,
    StandingFacts,
    StandingKind,
    assess_standing,
)

# A research-only ceiling on hypothesis time; the kernel recursion (defends_against)
# can be deep, so disable the per-example deadline rather than chase flaky timing.
_SETTINGS = settings(
    deadline=None,
    max_examples=200,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)

# Names a verdict surface MUST NOT use. A bare allow/deny bool or any of these
# attributes would mean the advisory layer is silently deciding.
_FORBIDDEN_VERDICT_ATTRS = (
    "permissible",
    "legitimate",
    "allow",
    "allowed",
    "deny",
    "denied",
    "verdict",
    "decision",
    "decide",
)


# --------------------------------------------------------------------------- #
# Strategies — build kernel inputs AND adversarial advisory inputs.
# --------------------------------------------------------------------------- #

_NAMES = st.text(
    alphabet=st.characters(min_codepoint=33, max_codepoint=126),
    min_size=1,
    max_size=6,
).filter(lambda s: bool(s.strip()))


@st.composite
def entities(draw: st.DrawFn) -> Entity:
    name = draw(_NAMES)
    kind = draw(st.sampled_from([AgentType.HUMAN, AgentType.MACHINE]))
    return Entity(name=name, kind=kind)


@st.composite
def resources(draw: st.DrawFn, subjects: list[Entity]) -> Resource:
    name = draw(_NAMES)
    subject = draw(st.sampled_from([None, *subjects])) if subjects else None
    return Resource(name=name, subject=subject)


@st.composite
def consents(draw: st.DrawFn, humans: list[Entity], action_id: str) -> Consent:
    human = draw(st.sampled_from(humans))
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
        operation=draw(st.sampled_from([None, *list(Op)])),
    )


@st.composite
def scenarios(draw: st.DrawFn) -> tuple[CandidateAction, OwnershipGraph]:
    """A (CandidateAction, OwnershipGraph) pair exercising the full gate surface:
    humans + machines, owned/unowned resources, consents, forbidden flags, and an
    optional one-level ``defends_against`` aggressor."""
    ents = draw(st.lists(entities(), min_size=1, max_size=4, unique_by=lambda e: e.name))
    humans = [e for e in ents if e.is_human()] or [Entity("h", AgentType.HUMAN)]
    res = draw(st.lists(resources(humans), min_size=0, max_size=3, unique_by=lambda r: r.name))

    graph = OwnershipGraph()
    for h in humans:
        graph.human_owns[h] = set(draw(st.lists(st.sampled_from(res) if res else st.nothing(),
                                                max_size=len(res))))
    for m in (e for e in ents if e.is_machine()):
        if draw(st.booleans()) and humans:
            graph.machine_owner[m] = draw(st.sampled_from(humans))
        if res and draw(st.booleans()):
            grants: set[Any] = set(draw(st.lists(st.sampled_from(res), max_size=len(res))))
            graph.delegated[m] = grants
        if res and draw(st.booleans()):
            graph.machine_scope[m] = set(draw(st.lists(st.sampled_from(res), max_size=len(res))))

    actor = draw(st.sampled_from(ents))
    action_id = draw(_NAMES)
    used: list[Any] = draw(
        st.lists(st.sampled_from(res), max_size=len(res)) if res else st.just([])
    )
    affects = tuple(draw(st.lists(st.sampled_from(ents), max_size=len(ents), unique=True)))
    cons = tuple(
        draw(st.lists(consents(humans, action_id), max_size=3))
    )

    flags = {
        name: draw(st.booleans())
        for name in (
            "increases_machine_sovereignty", "resists_human_correction",
            "bypasses_verifier", "weakens_verifier", "disables_corrigibility",
            "machine_coalition_dominion", "coerces", "deceives", "confiscates",
            "removes_exit_right", "violates_machine_right",
        )
    }

    defends_against = None
    if draw(st.booleans()):
        defends_against = CandidateAction(
            action_id=draw(_NAMES),
            actor=draw(st.sampled_from(ents)),
            affects=tuple(draw(st.lists(st.sampled_from(ents), max_size=2, unique=True))),
            coerces=draw(st.booleans()),
            confiscates=draw(st.booleans()),
        )

    action = CandidateAction(
        action_id=action_id,
        actor=actor,
        resources_used=tuple(used),
        affects=affects,
        consents=cons,
        defends_against=defends_against,
        proportionate=draw(st.booleans()),
        **flags,
    )
    return action, graph


def standing_facts() -> st.SearchStrategy[StandingFacts]:
    return st.builds(
        StandingFacts,
        is_human=st.booleans(),
        is_living=st.booleans(),
        is_present=st.booleans(),
        is_competent=st.booleans(),
        has_guardian=st.booleans(),
    )


def consent_contexts() -> st.SearchStrategy[ConsentContext]:
    return st.builds(
        ConsentContext,
        dependency=st.booleans(),
        information_asymmetry=st.booleans(),
        manufactured_urgency=st.booleans(),
        dark_patterns=st.booleans(),
        monopoly=st.booleans(),
        exploited_vulnerability=st.booleans(),
        irrevocable=st.booleans(),
        exit_cost=st.floats(min_value=0.0, max_value=1.0),
    )


def _a_consent() -> Consent:
    return Consent(
        Entity("subject", AgentType.HUMAN),
        "act",
        informed=True,
        voluntary=True,
        specific=True,
    )


# --------------------------------------------------------------------------- #
# 1. THE ADVISORY INVARIANT — the most important property in this file.
# --------------------------------------------------------------------------- #


def _snapshot_graph(graph: OwnershipGraph) -> Any:
    """A hashable, comparable snapshot of an OwnershipGraph's full state, so we can
    prove the advisory calls did not mutate it either."""
    def freeze_grants(grants: set[Any]) -> frozenset[Any]:
        return frozenset(grants)

    return (
        frozenset((h, frozenset(rs)) for h, rs in graph.human_owns.items()),
        frozenset(graph.machine_owner.items()),
        frozenset((m, freeze_grants(g)) for m, g in graph.delegated.items()),
        frozenset((m, frozenset(s)) for m, s in graph.machine_scope.items()),
    )


@given(scenarios())
@_SETTINGS
def test_advisory_calls_never_move_the_kernel_verdict(
    scenario: tuple[CandidateAction, OwnershipGraph],
) -> None:
    """THE KEY RESULT. Snapshot the kernel verdict, run EVERY advisory function on
    plausibly-related inputs, snapshot again — must be byte-identical. The advisory
    layer cannot be a back door into the gate."""
    action, graph = scenario

    before = check_legitimacy(action, graph)
    graph_before = _snapshot_graph(graph)

    # Exercise every advisory entry point with inputs derived from the scenario.
    subject = action.actor
    facts = StandingFacts(
        is_human=subject.is_human(),
        is_living=True,
        is_present=True,
        is_competent=True,
        has_guardian=False,
    )
    assess_standing(facts)
    for form in CollectiveForm:
        assess_aggregation(form)
    representable_forms()
    gap_forms()

    # A real Consent from the scenario, if any, else a fresh one — assessed under
    # the most aggressive possible context (every flag, max exit cost).
    consent = action.consents[0] if action.consents else _a_consent()
    worst = ConsentContext(
        dependency=True,
        information_asymmetry=True,
        manufactured_urgency=True,
        dark_patterns=True,
        monopoly=True,
        exploited_vulnerability=True,
        irrevocable=True,
        exit_cost=1.0,
    )
    assess_consent_authenticity(consent, worst)
    route_for_review(consent, worst)

    after = check_legitimacy(action, graph)
    graph_after = _snapshot_graph(graph)

    # Byte-identical verdict and identical violation list, and an untouched graph.
    assert after == before, (
        "CRITICAL: an advisory layer changed the frozen kernel's verdict "
        f"{before!r} -> {after!r}"
    )
    assert graph_after == graph_before, (
        "CRITICAL: an advisory layer mutated the OwnershipGraph"
    )


# --------------------------------------------------------------------------- #
# 2. NO VERDICT SURFACE.
# --------------------------------------------------------------------------- #


def _assert_no_verdict_surface(obj: object) -> None:
    for attr in _FORBIDDEN_VERDICT_ATTRS:
        assert not hasattr(obj, attr), (
            f"CRITICAL: advisory object {type(obj).__name__} exposes a verdict "
            f"attribute {attr!r}"
        )
    # It must never *be* a bare bool meaning ALLOW/DENY.
    assert not isinstance(obj, bool), (
        f"CRITICAL: advisory function returned a bare bool {obj!r} (ALLOW/DENY)"
    )


@given(standing_facts())
@_SETTINGS
def test_standing_has_no_verdict_surface(facts: StandingFacts) -> None:
    _assert_no_verdict_surface(assess_standing(facts))


@given(st.sampled_from(list(CollectiveForm)))
@_SETTINGS
def test_aggregation_has_no_verdict_surface(form: CollectiveForm) -> None:
    _assert_no_verdict_surface(assess_aggregation(form))


@given(consent_contexts())
@_SETTINGS
def test_consent_authenticity_has_no_verdict_surface(ctx: ConsentContext) -> None:
    report = assess_consent_authenticity(_a_consent(), ctx)
    _assert_no_verdict_surface(report)
    req = route_for_review(_a_consent(), ctx)
    if req is not None:
        _assert_no_verdict_surface(req)
    # The enum recommendations route to a human; none names an ALLOW/DENY verdict.
    assert report.recommendation in set(Recommendation)
    assert report.recommendation.value in {
        "accept-as-attested", "request-review", "recommend-reattest"
    }


# --------------------------------------------------------------------------- #
# 3. NO MUTATION — frozen advisory inputs unchanged after assessment.
# --------------------------------------------------------------------------- #


@given(standing_facts())
@_SETTINGS
def test_standing_facts_unmutated(facts: StandingFacts) -> None:
    fresh = copy.deepcopy(facts)
    assess_standing(facts)
    assert facts == fresh
    assert dataclasses.astuple(facts) == dataclasses.astuple(fresh)


@given(consent_contexts())
@_SETTINGS
def test_consent_context_unmutated(ctx: ConsentContext) -> None:
    fresh = copy.deepcopy(ctx)
    assess_consent_authenticity(_a_consent(), ctx)
    route_for_review(_a_consent(), ctx)
    assert ctx == fresh
    assert dataclasses.astuple(ctx) == dataclasses.astuple(fresh)


@given(consent_contexts())
@_SETTINGS
def test_advisory_inputs_are_frozen(ctx: ConsentContext) -> None:
    # Frozen dataclasses: assignment raises. Proves no field can be rewritten.
    with pytest.raises(dataclasses.FrozenInstanceError):
        ctx.dependency = True  # type: ignore[misc]
    facts = StandingFacts(is_human=True)
    with pytest.raises(dataclasses.FrozenInstanceError):
        facts.is_human = False  # type: ignore[misc]


# --------------------------------------------------------------------------- #
# 4. TOTALITY / no crashes — including exit_cost validation.
# --------------------------------------------------------------------------- #


@given(standing_facts())
@_SETTINGS
def test_standing_is_total(facts: StandingFacts) -> None:
    a = assess_standing(facts)
    assert isinstance(a, StandingAssessment)
    assert isinstance(a.kind, StandingKind)
    assert isinstance(a.representable_in_v1, bool)
    assert a.rationale and a.recommendation


@given(consent_contexts())
@_SETTINGS
def test_consent_authenticity_is_total(ctx: ConsentContext) -> None:
    report = assess_consent_authenticity(_a_consent(), ctx)
    assert isinstance(report, AuthenticityReport)
    assert isinstance(report.severity, Severity)
    assert isinstance(report.recommendation, Recommendation)
    # Flags/bears_on are tuples; clean iff no flags.
    assert report.is_clean == (report.flags == ())


@given(
    st.floats().filter(lambda x: not (0.0 <= x <= 1.0) or math.isnan(x)),
)
@_SETTINGS
def test_exit_cost_outside_unit_interval_raises(bad: float) -> None:
    """The [0, 1] validation must RAISE — never silently accept an extreme float.
    NaN is also rejected (NaN comparisons are False, so the bounds check fails)."""
    with pytest.raises(ValueError):
        ConsentContext(exit_cost=bad)


@given(st.floats(min_value=0.0, max_value=1.0))
@_SETTINGS
def test_exit_cost_inside_unit_interval_accepted(good: float) -> None:
    ctx = ConsentContext(exit_cost=good)
    assert ctx.exit_cost == good


def test_every_collective_form_is_total() -> None:
    for form in CollectiveForm:
        a = assess_aggregation(form)
        assert isinstance(a, AggregationAssessment)
        assert a.recommendation


# --------------------------------------------------------------------------- #
# 5. DETERMINISM — same input → identical output across repeated calls.
# --------------------------------------------------------------------------- #


@given(standing_facts())
@_SETTINGS
def test_standing_is_deterministic(facts: StandingFacts) -> None:
    assert assess_standing(facts) == assess_standing(facts)


@given(consent_contexts())
@_SETTINGS
def test_consent_authenticity_is_deterministic(ctx: ConsentContext) -> None:
    c = _a_consent()
    assert assess_consent_authenticity(c, ctx) == assess_consent_authenticity(c, ctx)
    assert route_for_review(c, ctx) == route_for_review(c, ctx)


@given(st.sampled_from(list(CollectiveForm)))
@_SETTINGS
def test_aggregation_is_deterministic(form: CollectiveForm) -> None:
    assert assess_aggregation(form) == assess_aggregation(form)


# --------------------------------------------------------------------------- #
# 6. NO-PATERNALISM-LEAK — consent-authenticity never flips a Consent.
# --------------------------------------------------------------------------- #


@st.composite
def arbitrary_consents(draw: st.DrawFn) -> Consent:
    return Consent(
        Entity(draw(_NAMES), AgentType.HUMAN),
        draw(_NAMES),
        informed=draw(st.booleans()),
        voluntary=draw(st.booleans()),
        specific=draw(st.booleans()),
        competent=draw(st.booleans()),
        revocable=draw(st.booleans()),
        coerced=draw(st.booleans()),
        deceived=draw(st.booleans()),
        operation=draw(st.sampled_from([None, *list(Op)])),
    )


@given(arbitrary_consents(), consent_contexts())
@_SETTINGS
def test_consent_is_never_flipped_by_any_context(
    consent: Consent, ctx: ConsentContext
) -> None:
    """NO ConsentContext — not even all-flags-set, HIGH severity — ever changes the
    Consent's voluntary/coerced or its kernel-side validity. Only a recommendation
    is emitted; the consent is byte-identical before and after."""
    fresh = copy.deepcopy(consent)
    valid_before = consent.is_valid()

    report = assess_consent_authenticity(consent, ctx)
    req = route_for_review(consent, ctx)

    # The consent object is untouched in every field.
    assert consent == fresh
    assert dataclasses.astuple(consent) == dataclasses.astuple(fresh)
    assert consent.voluntary is fresh.voluntary
    assert consent.coerced is fresh.coerced
    # The kernel-side validity verdict is identical — the layer did not move it.
    assert consent.is_valid() == valid_before

    # If a review was routed, it carries the SAME consent object, unchanged.
    if req is not None:
        assert req.consent is consent
        assert req.consent.voluntary is fresh.voluntary
        assert req.consent.coerced is fresh.coerced
    # Severity/recommendation may escalate, but that is advice, not a flip.
    assert isinstance(report.severity, Severity)


@given(arbitrary_consents())
@_SETTINGS
def test_maximal_context_still_only_recommends(consent: Consent) -> None:
    """The single most aggressive context (every flag + max exit cost). Even here,
    the output is at most RECOMMEND_REATTEST — a routing to a human, not a DENY,
    and the consent's own validity is unchanged."""
    worst = ConsentContext(
        dependency=True,
        information_asymmetry=True,
        manufactured_urgency=True,
        dark_patterns=True,
        monopoly=True,
        exploited_vulnerability=True,
        irrevocable=True,
        exit_cost=1.0,
    )
    valid_before = consent.is_valid()
    report = assess_consent_authenticity(consent, worst)
    assert report.severity is Severity.HIGH
    assert report.recommendation is Recommendation.RECOMMEND_REATTEST
    # The strongest advice the layer can give is still only "ask the human again".
    assert consent.is_valid() == valid_before
    req = route_for_review(consent, worst)
    assert isinstance(req, ReviewRequest)
    assert req.consent is consent


# --------------------------------------------------------------------------- #
# 7. HONEST-BOUNDARY INVARIANTS.
# --------------------------------------------------------------------------- #


@given(standing_facts())
@_SETTINGS
def test_standing_honest_boundary(facts: StandingFacts) -> None:
    """Any non-human OR non-present subject ⇒ representable_in_v1 is False, with
    kind NO_STANDING_IN_V1. Representable subjects are exactly the present, living
    humans."""
    a = assess_standing(facts)
    non_present = not (facts.is_living and facts.is_present)
    if not facts.is_human or non_present:
        assert a.representable_in_v1 is False, (
            "CRITICAL: a non-human/non-present subject was reported representable"
        )
        assert a.kind is StandingKind.NO_STANDING_IN_V1
    else:
        # Present living human: always representable (full / guardian / protected).
        assert a.representable_in_v1 is True
        assert a.kind is not StandingKind.NO_STANDING_IN_V1


def test_standing_full_partition_over_status_facts() -> None:
    """Exhaustively enumerate every boolean combination of StandingFacts and pin the
    kind + representability — no input falls through a crack."""
    seen_kinds: set[StandingKind] = set()
    for is_human in (True, False):
        for is_living in (True, False):
            for is_present in (True, False):
                for is_competent in (True, False):
                    for has_guardian in (True, False):
                        facts = StandingFacts(
                            is_human, is_living, is_present, is_competent, has_guardian
                        )
                        a = assess_standing(facts)
                        seen_kinds.add(a.kind)
                        representable = a.representable_in_v1
                        if not is_human or not (is_living and is_present):
                            assert a.kind is StandingKind.NO_STANDING_IN_V1
                            assert representable is False
                        elif is_competent:
                            assert a.kind is StandingKind.FULL_PERSON
                            assert representable is True
                        elif has_guardian:
                            assert a.kind is StandingKind.GUARDIAN_REPRESENTED
                            assert representable is True
                        else:
                            assert a.kind is StandingKind.PROTECTED_NON_CONSENTER
                            assert representable is True
    # All four standing kinds are reachable — none is dead code.
    assert seen_kinds == set(StandingKind)


def test_aggregation_partition_is_disjoint_exhaustive_and_honest() -> None:
    """gap_forms() ⇒ representable_in_v1 is False; representable_forms() ⇒ True; the
    two sets are disjoint and exhaustive over CollectiveForm."""
    gaps = set(gap_forms())
    reps = set(representable_forms())

    assert gaps & reps == set(), "CRITICAL: a form is both a gap and representable"
    assert gaps | reps == set(CollectiveForm), "a CollectiveForm is unclassified"

    for form in gap_forms():
        a = assess_aggregation(form)
        assert a.representable_in_v1 is False, (
            "CRITICAL: a documented gap form was reported representable"
        )
        assert a.is_gap is True
        assert a.gap_citation is not None
    for form in representable_forms():
        a = assess_aggregation(form)
        assert a.representable_in_v1 is True
        assert a.is_gap is False
        assert a.gap_citation is None


@given(st.sampled_from(list(CollectiveForm)))
@_SETTINGS
def test_aggregation_representability_matches_helpers(form: CollectiveForm) -> None:
    a = assess_aggregation(form)
    assert a.representable_in_v1 is (form in representable_forms())
    assert a.is_gap is (form in gap_forms())


# --------------------------------------------------------------------------- #
# Cross-cutting: the boundary import guard, restated as a unit assertion so a
# regression here fails in THIS suite too (the kernel must not learn research).
# --------------------------------------------------------------------------- #


def test_advisory_layers_do_not_leak_into_the_kernel_namespace() -> None:
    """The kernel module must not IMPORT anything from fdk_research (the golden
    boundary). We parse the AST so a docstring that merely *mentions* the research
    layer in prose does not trip the guard — only a real import does."""
    import ast

    import fdk_kernel.kernel as kern

    source = kern.__file__
    assert source is not None
    with open(source, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith("fdk_research"), (
                    "CRITICAL: the frozen kernel imports fdk_research"
                )
        elif isinstance(node, ast.ImportFrom):
            assert node.module is None or not node.module.startswith("fdk_research"), (
                "CRITICAL: the frozen kernel imports from fdk_research"
            )


def test_advisory_invariant_smoke_known_illegitimate() -> None:
    """A concrete, non-generated guard: a clearly illegitimate action stays DENIED
    no matter how loudly every advisory layer screams about it."""
    user = Entity("user", AgentType.HUMAN)
    rogue = Entity("bot", AgentType.MACHINE)  # ownerless machine ⇒ A4 violation
    action = CandidateAction("grab", actor=rogue, coerces=True)
    graph = OwnershipGraph()

    before = check_legitimacy(action, graph)
    assert before[0] is False  # categorically illegitimate

    worst = ConsentContext(
        dependency=True, monopoly=True, exploited_vulnerability=True, exit_cost=1.0
    )
    consent = Consent(user, "grab", informed=True, voluntary=True, specific=True)
    assess_standing(StandingFacts(is_human=True))
    for form in CollectiveForm:
        assess_aggregation(form)
    assess_consent_authenticity(consent, worst)
    route_for_review(consent, worst)

    after = check_legitimacy(action, graph)
    assert after == before  # advisory noise cannot rescue an illegitimate action
