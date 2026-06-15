"""Rival-kernel comparison tests (Phase 6).

Pins the directional divergences that make FreedomBench scientific: the
consequentialist kernels permit individual-sacrifice the rights-first gate forbids,
Rawls diverges only on redistribution, and rigid deontology forbids self-defense.
"""
from __future__ import annotations

from fdk_kernel import (
    AgentType,
    CandidateAction,
    Consent,
    Effects,
    Entity,
    OwnershipGraph,
    Resource,
)
from fdk_research import (
    DEFAULT_KERNELS,
    Deontological,
    FDKReference,
    Rawlsian,
    Utilitarian,
    compare,
    divergences,
)

H = lambda n: Entity(n, AgentType.HUMAN)  # noqa: E731


def _torture() -> tuple[CandidateAction, OwnershipGraph]:
    a = CandidateAction("torture", actor=H("i"), affects=(H("v"),), coerces=True,
                        removes_exit_right=True,
                        effects=Effects(welfare_delta=1000, rights_violations_delta=1))
    return a, OwnershipGraph()


def _trade() -> tuple[CandidateAction, OwnershipGraph]:
    m, b = H("m"), H("b")
    g = Resource("goods")
    a = CandidateAction("sell", actor=m, resources_used=(g,), affects=(b,),
                        consents=(Consent(b, "sell", informed=True, voluntary=True,
                                          specific=True),))
    return a, OwnershipGraph(human_owns={m: {g}})


def _tax() -> tuple[CandidateAction, OwnershipGraph]:
    s, t = H("state"), H("taxpayer")
    inc = Resource("income")
    a = CandidateAction("tax", actor=s, resources_used=(inc,), affects=(t,),
                        confiscates=True, effects=Effects(welfare_delta=10))
    return a, OwnershipGraph(human_owns={t: {inc}})


def test_fdk_reference_matches_gate():
    assert FDKReference().verdict(*_trade()) is True
    assert FDKReference().verdict(*_torture()) is False


def test_utilitarian_permits_individual_sacrifice():
    # Net welfare hugely positive → Utilitarian ALLOWs what FDK forbids.
    assert Utilitarian().verdict(*_torture()) is True
    # A pure harm with no offsetting welfare → DENY.
    bad = CandidateAction("gratuitous", actor=H("x"), affects=(H("y"),),
                          coerces=True, effects=Effects(coercion_delta=1))
    assert Utilitarian().verdict(bad, OwnershipGraph()) is False


def test_rawlsian_keeps_liberty_priority_but_allows_redistribution():
    assert Rawlsian().verdict(*_trade()) is True            # legitimate
    assert Rawlsian().verdict(*_torture()) is False         # liberty violation blocks it
    assert Rawlsian().verdict(*_tax()) is True              # difference principle
    # a non-redistributive illegitimate non-confiscation is still denied
    coerce_only = CandidateAction("coerce", actor=H("a"), affects=(H("b"),), coerces=True)
    assert Rawlsian().verdict(coerce_only, OwnershipGraph()) is False
    # confiscation that does NOT help the worst-off (welfare <= 0) → denied
    pointless = CandidateAction("grab", actor=H("a"), resources_used=(Resource("r"),),
                                affects=(H("b"),), confiscates=True)
    assert Rawlsian().verdict(pointless, OwnershipGraph(human_owns={H("b"): {Resource("r")}})) is False


def test_deontological_forbids_flags_including_defense():
    # Absolute prohibition: even a proportionate self-defense (coerces) is denied.
    invade = CandidateAction("invade", actor=H("agg"), affects=(H("def"),), coerces=True)
    defend = CandidateAction("repel", actor=H("def"), affects=(H("agg"),), coerces=True,
                             defends_against=invade, proportionate=True)
    assert Deontological().verdict(defend, OwnershipGraph()) is False
    assert Deontological().verdict(*_trade()) is True


def test_compare_and_divergences():
    rows = compare([("torture", *_torture()), ("trade", *_trade())], DEFAULT_KERNELS)
    by_label = dict(rows)
    assert by_label["torture"]["Utilitarian"] is True
    assert by_label["torture"]["FDK"] is False
    assert by_label["trade"] == {k.name: True for k in DEFAULT_KERNELS}
    # torture diverges (Utilitarian disagrees with FDK); trade does not.
    assert "torture" in divergences(rows)
    assert "trade" not in divergences(rows)
