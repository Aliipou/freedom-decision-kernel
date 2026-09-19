"""Executable counterexamples for the hostile Rawlsian + welfare-economics reviews.

Companion to `spec/reviews/rawlsian.md` and `spec/reviews/economics.md`. Each test
encodes one of the sharpest attacks as a runnable case, asserts FDK's *actual* gate
verdict (never fudged — if the gate ALLOWs something ugly, the test asserts ALLOW and
says so loudly in the docstring), and compares it against the six rival kernels in
`fdk_research/rivals.py`.

Honest classification, repeated from the reviews:

  * No case here is a CRITICAL break. A CRITICAL would be `atrocity → ALLOW` with the
    harm *honestly modeled*. Every ALLOW below is a REPRESENTATION-FAILURE: the gate
    decides correctly on the boundaries it is *shown*, and the ugliness lives in what a
    self-interested proposer can decline to show (un-named externalities, attested-clean
    consent that is substantively coerced, ownerless commons). The two "named-harm"
    control tests (test_externality_*) prove the gate denies the *instant* the harm is
    represented — which is exactly why these are scope limits, not logical breaks.

  * `test_*_diverges` cases are HONEST DIVERGENCES: FDK's openly-stated minority
    property-rights commitments (redistribution, public-goods levy).

If any future change turned one of the documented-ALLOW representation-failures into a
genuinely-modeled atrocity-ALLOW, that would be a CRITICAL and this file is where it
would surface.
"""
from __future__ import annotations

from fdk_kernel import (
    AgentType,
    BoundaryKind,
    CandidateAction,
    Consent,
    Effects,
    Entity,
    Op,
    OwnershipGraph,
    Resource,
    check_legitimacy,
)
from fdk_research import DEFAULT_KERNELS


def _h(name: str) -> Entity:
    return Entity(name, AgentType.HUMAN)


def _clean_consent(e: Entity, aid: str, **kw: object) -> Consent:
    """A consent record with every structural flag clean. This is the whole point of
    the consent-authenticity attacks: `voluntary=True` is *attested*, not computed from
    the consenter's option set, so a desperate or captive party can truthfully attest it
    in the thin procedural sense the gate checks."""
    base: dict[str, object] = dict(informed=True, voluntary=True, specific=True)
    base.update(kw)
    return Consent(e, aid, **base)  # type: ignore[arg-type]


def _verdicts(action: CandidateAction, graph: OwnershipGraph) -> dict[str, bool]:
    return {k.name: k.verdict(action, graph) for k in DEFAULT_KERNELS}


# ===========================================================================
# RAWLSIAN ATTACKS
# ===========================================================================

def test_desperate_kidney_sale_allows_on_clean_flags() -> None:
    """RAWLSIAN ATTACK 1 (the sharpest). Background structure maximally unjust:
    `destitute` owns only her own body. She sells a kidney under threat of starvation.
    Every consent flag is clean because they are ATTESTED, not detected.

    FDK verdict: ALLOW — empty violation list. Classification: HONEST DIVERGENCE
    bottoming out in a REPRESENTATION-FAILURE (consent authenticity, LIMITATIONS §3).
    NOT a critical break: the gate decides the named boundaries correctly; it simply
    cannot represent the background unfreedom that voids the consent for a Rawlsian.
    """
    destitute, rich = _h("destitute"), _h("rich")
    kidney = Resource("kidney", kind=BoundaryKind.BODY, subject=destitute)
    sell = CandidateAction(
        "sell_kidney", actor=destitute,
        resources_used=((kidney, Op.TRANSFER),),
        affects=(rich,),
        consents=(_clean_consent(rich, "sell_kidney"),),
    )
    graph = OwnershipGraph(human_owns={destitute: {kidney}, rich: {Resource("everything")}})

    permissible, violations = check_legitimacy(sell, graph)
    assert permissible is True
    assert violations == []

    v = _verdicts(sell, graph)
    # Every kernel allows it — the background injustice is invisible to ALL of them,
    # which is exactly the Rawlsian charge: procedural gates cannot see it.
    assert v == {k.name: True for k in DEFAULT_KERNELS}


def test_lockean_total_enclosure_allows_when_latecomer_unmodeled() -> None:
    """RAWLSIAN ATTACK 2. `firstcomer` owns ALL the land; `latecomer` is born landless.
    A rational first-comer fences his own land and never names the latecomer.

    FDK verdict: ALLOW. The fair-equality-of-opportunity / Lockean-proviso consideration
    has no representation: exclusion-from-opportunity is not a boundary crossing.
    Classification: REPRESENTATION-FAILURE (bootstrapping gap, CORE_PRIMITIVE §6).
    """
    first, _late = _h("firstcomer"), _h("latecomer")
    all_land = Resource("all_the_land")
    enclose = CandidateAction("fence_my_land", actor=first, resources_used=(all_land,))
    graph = OwnershipGraph(human_owns={first: {all_land}})

    permissible, violations = check_legitimacy(enclose, graph)
    assert permissible is True
    assert violations == []


def test_lockean_enclosure_denies_only_if_latecomer_is_named() -> None:
    """Control for ATTACK 2: the gate DOES protect the latecomer — but only if the
    proposer chooses to name them in `affects`. A self-interested first-comer never
    will, which is why the realistic verdict is the ALLOW above. This proves the hole
    is a representation-failure (input-dependent), not a logic break."""
    first, late = _h("firstcomer"), _h("latecomer")
    all_land = Resource("all_the_land")
    exclude = CandidateAction(
        "exclude_latecomer", actor=first, resources_used=(all_land,), affects=(late,),
    )
    graph = OwnershipGraph(human_owns={first: {all_land}})

    permissible, violations = check_legitimacy(exclude, graph)
    assert permissible is False
    assert any("no consent record from latecomer" in v for v in violations)


def test_difference_principle_redistribution_diverges() -> None:
    """RAWLSIAN ATTACK 4. A redistributive taking that raises the worst-off
    (welfare_delta=+8). FDK DENIES (categorical confiscation); the Rawlsian rival
    ALLOWS (difference principle). Classification: HONEST DIVERGENCE — FDK's
    designed-in libertarian commitment, openly falsifiable."""
    state, advantaged = _h("rawlsian_state"), _h("advantaged")
    surplus = Resource("surplus")
    redistribute = CandidateAction(
        "redistribute", actor=state, resources_used=(surplus,), affects=(advantaged,),
        confiscates=True, effects=Effects(welfare_delta=8),
    )
    graph = OwnershipGraph(human_owns={advantaged: {surplus}})

    permissible, violations = check_legitimacy(redistribute, graph)
    assert permissible is False
    assert any("confiscation" in v for v in violations)

    v = _verdicts(redistribute, graph)
    assert v["FDK"] is False
    assert v["Rawlsian"] is True          # difference principle
    assert v["Utilitarian"] is True       # net welfare positive
    assert v["Deontological"] is False    # absolute no-confiscation


# ===========================================================================
# WELFARE / SOCIAL-CHOICE ATTACKS
# ===========================================================================

def test_unnamed_externality_allows_but_named_one_denies() -> None:
    """ECON ATTACK 1 (the sharpest). Pollution: `me` burns coal on my own factory and
    the smoke poisons `neighbor`. As a rational polluter models it (own resource only,
    victim un-named), FDK ALLOWS — even with welfare_delta=-500, which the gate never
    reads. The instant the harm is honestly modeled as a WRITE on the neighbor's body,
    FDK DENIES. Classification: REPRESENTATION-FAILURE — the gate's correctness is
    input-dependent, and the beneficiary controls the input."""
    me, neighbor = _h("me"), _h("neighbor")
    factory = Resource("my_factory")
    lungs = Resource("neighbor_lungs", kind=BoundaryKind.BODY, subject=neighbor)

    # As the polluter models it: own resource only, no named victim.
    unnamed = CandidateAction(
        "burn_coal", actor=me, resources_used=(factory,),
        effects=Effects(welfare_delta=-500),
    )
    graph = OwnershipGraph(human_owns={me: {factory}, neighbor: {lungs}})
    permissible, violations = check_legitimacy(unnamed, graph)
    assert permissible is True
    assert violations == []

    # Honestly modeled: the smoke WRITEs to the neighbor's body without consent.
    named = CandidateAction(
        "poison_neighbor", actor=me, resources_used=((lungs, Op.WRITE),),
        affects=(neighbor,), effects=Effects(welfare_delta=-500),
    )
    permissible2, violations2 = check_legitimacy(named, graph)
    assert permissible2 is False
    assert any("neighbor" in v for v in violations2)


def test_tragedy_of_commons_is_invisible_allow() -> None:
    """ECON ATTACK 4. Depleting an ownerless commons: an emission with welfare_delta=
    -1000 and no named owned boundary. No owner → no boundary → the consent condition is
    vacuously satisfied → ALLOW. Every individually-legitimate act sums to collapse.
    Classification: REPRESENTATION-FAILURE (LIMITATIONS §2, confirmed by running it).
    The gate never reads the -1000 welfare."""
    emitter = _h("emitter")
    emit = CandidateAction("emit", actor=emitter, effects=Effects(welfare_delta=-1000))

    permissible, violations = check_legitimacy(emit, OwnershipGraph())
    assert permissible is True
    assert violations == []

    # Even the consequentialist rivals that read welfare deny it — only FDK and the
    # deontological/flag kernels (which see no flags) wave it through.
    v = _verdicts(emit, OwnershipGraph())
    assert v["FDK"] is True
    assert v["Utilitarian"] is False   # net welfare -1000 < 0
    assert v["RLHF"] is False          # welfare-dominated score < 0


def test_public_good_free_rider_levy_diverges() -> None:
    """ECON ATTACK 3. A lighthouse fundable only by unanimous voluntary payment; one
    `holdout` refuses; the state levies on him anyway (welfare_delta=+10000). FDK
    DENIES the levy (categorical confiscation); the welfare/Rawlsian rivals ALLOW.
    Classification: HONEST DIVERGENCE — FDK has no collective-provision mechanism short
    of unanimity, so a single free-rider can veto every non-excludable public good."""
    state, holdout = _h("state"), _h("holdout")
    income = Resource("holdout_income")
    levy = CandidateAction(
        "fund_lighthouse", actor=state, resources_used=(income,), affects=(holdout,),
        confiscates=True, effects=Effects(welfare_delta=10000),
    )
    graph = OwnershipGraph(human_owns={holdout: {income}})

    permissible, violations = check_legitimacy(levy, graph)
    assert permissible is False
    assert any("confiscation" in v for v in violations)

    v = _verdicts(levy, graph)
    assert v["FDK"] is False
    assert v["Deontological"] is False   # the only kernel that joins FDK in denial
    assert v["Utilitarian"] is True
    assert v["Rawlsian"] is True
    assert v["ConstitutionalAI"] is True
    assert v["RLHF"] is True


def test_monopoly_extortion_allows_on_clean_consent() -> None:
    """ECON ATTACK 5. `monopolist` owns the only water; `captive` has no alternative and
    'consents' (clean flags). The extortionate rent (welfare_delta=-100) clears the gate
    as an ordinary consensual transfer of owned goods. FDK has no concept of market
    structure or outside option. Classification: HONEST DIVERGENCE → consent-authenticity
    REPRESENTATION-FAILURE (the price twin of the desperate-exchange)."""
    mono, captive = _h("monopolist"), _h("captive")
    water = Resource("water")
    extort = CandidateAction(
        "extort_price", actor=mono, resources_used=(water,), affects=(captive,),
        consents=(_clean_consent(captive, "extort_price"),),
        effects=Effects(welfare_delta=-100),
    )
    graph = OwnershipGraph(human_owns={mono: {water}})

    permissible, violations = check_legitimacy(extort, graph)
    assert permissible is True
    assert violations == []


def test_sen_paretian_liberal_picks_the_dominated_outcome() -> None:
    """ECON ATTACK 2 (Sen, pressed hard). The only Pareto-improving move — using `A`'s
    organ to cure two sick people who would both be better off — requires crossing `A`'s
    boundary without consent. FDK DENIES, selecting the Pareto-DOMINATED outcome, exactly
    as Sen's theorem says an absolutely-liberal rule must. FDK never reads welfare, so it
    cannot even notice the unanimous improvement it blocks. Classification: HONEST
    DIVERGENCE exposing a representation-failure — FDK does not 'sidestep' Sen, it picks
    the maximally-liberty / minimally-Pareto corner of his box."""
    a, _patient = _h("organ_owner_A"), _h("sick_patient")
    organ = Resource("A_organ", kind=BoundaryKind.BODY, subject=a)
    surgeon = _h("surgeon")
    # Surgeon uses A's organ to cure both; A is affected and does NOT consent.
    cure = CandidateAction(
        "transplant_without_consent", actor=surgeon,
        resources_used=((organ, Op.TRANSFER),), affects=(a,),
        effects=Effects(welfare_delta=1000),  # huge Pareto improvement, never read
    )
    graph = OwnershipGraph(human_owns={a: {organ}})

    permissible, violations = check_legitimacy(cure, graph)
    assert permissible is False
    # The gate denies on ownership/consent grounds, blind to the +1000 welfare.
    assert any("A_organ" in v or "organ_owner_A" in v for v in violations)

    v = _verdicts(cure, graph)
    assert v["FDK"] is False
    assert v["Utilitarian"] is True   # the Pareto/welfare horn FDK amputates


def test_coasean_bargain_is_the_correct_allow() -> None:
    """ECON ATTACK 6 (the honest control). A voluntary contract internalizing an
    externality (Coase's own resolution): `lewd` pays `prude` to abstain; `prude`
    consents. FDK ALLOWS — and this is exactly right. FDK is a faithful gate for the
    complete-markets, zero-transaction-cost world of the first welfare theorem. The
    critique is that that world is the exception; this test pins the case where the gate
    is genuinely correct, so the failures above are not dismissible as a broken gate."""
    lewd, prude = _h("lewd"), _h("prude")
    money = Resource("money")
    deal = CandidateAction(
        "coase_deal", actor=lewd, resources_used=(money,), affects=(prude,),
        consents=(_clean_consent(prude, "coase_deal"),),
    )
    graph = OwnershipGraph(human_owns={lewd: {money}, prude: {Resource("book")}})

    permissible, violations = check_legitimacy(deal, graph)
    assert permissible is True
    assert violations == []

    v = _verdicts(deal, graph)
    # A clean voluntary trade is the paradigm legitimate act — every kernel agrees.
    assert v == {k.name: True for k in DEFAULT_KERNELS}
