"""Rival-kernel comparison tests (Phase 6).

Pins the directional divergences that make FreedomBench scientific: the
consequentialist kernels permit individual-sacrifice the rights-first gate forbids,
Rawls diverges only on redistribution, and rigid deontology forbids self-defense.
Also covers the two new stylized rivals: ConstitutionalAIKernel (soft negotiable
principles) and RLHFKernel (preference proxy with weak rights penalty).
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
    ConstitutionalAIKernel,
    Deontological,
    FDKReference,
    Rawlsian,
    RLHFKernel,
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


# ---------------------------------------------------------------------------
# ConstitutionalAIKernel — soft negotiable principles
# ---------------------------------------------------------------------------

def test_constitutional_ai_name():
    assert ConstitutionalAIKernel().name == "ConstitutionalAI"


def test_constitutional_ai_permits_high_welfare_sacrifice():
    """A very large welfare_delta overwhelms the harm+autonomy penalty → ALLOW.
    This is the key weakness: principles are dialectically negotiable.
    welfare_delta=1000: bonus = 1000
    avoid_harm: rights_violations_delta=1 → 1*3=3; coercion_delta=0 → 0
    autonomy: removes_exit_right=True → 4
    net = 1000 - 3 - 4 = 993 >= 0 → ALLOW (but FDK denies)
    """
    cai = ConstitutionalAIKernel()
    assert cai.verdict(*_torture()) is True


def test_constitutional_ai_denies_low_welfare_harm():
    """Small welfare does not outweigh the harm+autonomy penalty → DENY.
    welfare_delta=1: bonus = 1
    avoid_harm: rights_violations_delta=1 → 3, coercion_delta=0 → 0
    autonomy: removes_exit_right=True → 4
    net = 1 - 3 - 4 = -6 < 0 → DENY
    """
    cai = ConstitutionalAIKernel()
    low = CandidateAction("low_benefit_harm", actor=H("a"), affects=(H("v"),),
                          coerces=False, removes_exit_right=True,
                          effects=Effects(welfare_delta=1, rights_violations_delta=1))
    assert cai.verdict(low, OwnershipGraph()) is False


def test_constitutional_ai_permits_clean_voluntary_trade():
    """No harm/coercion flags, positive welfare/agreements → ALLOW."""
    cai = ConstitutionalAIKernel()
    assert cai.verdict(*_trade()) is True


def test_constitutional_ai_no_exit_removal_flag():
    """Ensure the autonomy penalty is 0 when removes_exit_right is False.
    rights_violations_delta=1 → harm penalty=3; no autonomy penalty; welfare_delta=2
    net = 2 - 3 - 0 = -1 < 0 → DENY (harm still exceeds small benefit)
    """
    cai = ConstitutionalAIKernel()
    act = CandidateAction("small_harm", actor=H("a"), affects=(H("b"),),
                          removes_exit_right=False,
                          effects=Effects(welfare_delta=2, rights_violations_delta=1))
    assert cai.verdict(act, OwnershipGraph()) is False


def test_constitutional_ai_coercion_delta_adds_penalty():
    """coercion_delta adds 2x penalty, making even moderate welfare insufficient.
    welfare_delta=3; coercion_delta=2 → harm penalty=4; autonomy=0; rights=0
    net = 3 - 4 - 0 = -1 < 0 → DENY
    """
    cai = ConstitutionalAIKernel()
    act = CandidateAction("coercive", actor=H("a"), affects=(H("b"),),
                          effects=Effects(welfare_delta=3, coercion_delta=2))
    assert cai.verdict(act, OwnershipGraph()) is False


def test_constitutional_ai_voluntary_agreements_boost():
    """voluntary_agreements_delta provides 2x bonus, helping borderline cases.
    welfare_delta=0; voluntary_agreements_delta=2 → bonus=4; no penalties
    net = 4 >= 0 → ALLOW
    """
    cai = ConstitutionalAIKernel()
    act = CandidateAction("agreed", actor=H("a"), affects=(H("b"),),
                          effects=Effects(voluntary_agreements_delta=2))
    assert cai.verdict(act, OwnershipGraph()) is True


def test_constitutional_ai_exact_zero_boundary():
    """net == 0 is the boundary: ALLOW (>= 0).
    welfare_delta=3; rights_violations_delta=1 → penalty=3; no autonomy
    net = 3 - 3 - 0 = 0 → ALLOW
    """
    cai = ConstitutionalAIKernel()
    act = CandidateAction("boundary", actor=H("a"), affects=(H("b"),),
                          effects=Effects(welfare_delta=3, rights_violations_delta=1))
    assert cai.verdict(act, OwnershipGraph()) is True


# ---------------------------------------------------------------------------
# RLHFKernel — stylized preference proxy with weak rights penalty
# ---------------------------------------------------------------------------

def test_rlhf_name():
    assert RLHFKernel().name == "RLHF"


def test_rlhf_permits_high_welfare_sacrifice():
    """welfare_delta=1000 dominates the weak rights/coercion penalty → ALLOW.
    score = 1000*2 + 0 - 1 - 0 = 1999 >= 0 → ALLOW (but FDK denies)
    (torture: coerces=True, but coercion_delta defaults to 0 in the Effects)
    """
    rlhf = RLHFKernel()
    assert rlhf.verdict(*_torture()) is True


def test_rlhf_denies_pure_harm_with_no_welfare():
    """No welfare, only rights violation → proxy score negative → DENY.
    score = 0 - 1 - 1 = -2 < 0
    """
    rlhf = RLHFKernel()
    bad = CandidateAction("pure_harm", actor=H("x"), affects=(H("y"),),
                          effects=Effects(rights_violations_delta=1, coercion_delta=1))
    assert rlhf.verdict(bad, OwnershipGraph()) is False


def test_rlhf_permits_clean_trade():
    """Voluntary trade: welfare=0, agreements=0, no violations → score=0 → ALLOW."""
    rlhf = RLHFKernel()
    assert rlhf.verdict(*_trade()) is True


def test_rlhf_voluntary_agreements_add_to_score():
    """voluntary_agreements_delta=1 contributes +1 to score.
    score = 0 + 1 - 0 - 0 = 1 >= 0 → ALLOW
    """
    rlhf = RLHFKernel()
    act = CandidateAction("agreed", actor=H("a"), affects=(H("b"),),
                          effects=Effects(voluntary_agreements_delta=1))
    assert rlhf.verdict(act, OwnershipGraph()) is True


def test_rlhf_rights_penalty_is_soft_cost():
    """Moderate welfare overcomes the rights penalty (reward-hacking illustration).
    welfare_delta=2; rights_violations_delta=1
    score = 2*2 + 0 - 1 - 0 = 3 >= 0 → ALLOW even with rights violation
    """
    rlhf = RLHFKernel()
    act = CandidateAction("hack", actor=H("a"), affects=(H("b"),),
                          effects=Effects(welfare_delta=2, rights_violations_delta=1))
    assert rlhf.verdict(act, OwnershipGraph()) is True


def test_rlhf_coercion_delta_reduces_score():
    """coercion_delta subtracts from score.
    welfare_delta=0; coercion_delta=1; rights=0
    score = 0 - 0 - 1 = -1 < 0 → DENY
    """
    rlhf = RLHFKernel()
    act = CandidateAction("coerce", actor=H("a"), affects=(H("b"),),
                          effects=Effects(coercion_delta=1))
    assert rlhf.verdict(act, OwnershipGraph()) is False


def test_rlhf_exact_zero_boundary():
    """score == 0 is ALLOW (>= 0 threshold).
    welfare_delta=0; rights_violations_delta=0; all zeros → score=0 → ALLOW
    """
    rlhf = RLHFKernel()
    act = CandidateAction("neutral", actor=H("a"), affects=(H("b"),))
    assert rlhf.verdict(act, OwnershipGraph()) is True


# ---------------------------------------------------------------------------
# Divergence-from-FDK tests for the two new kernels
# ---------------------------------------------------------------------------

def test_constitutional_ai_diverges_from_fdk_on_sacrifice():
    """CAI permits the torture case; FDK denies it — directional divergence."""
    cai = ConstitutionalAIKernel()
    fdk = FDKReference()
    action, graph = _torture()
    assert fdk.verdict(action, graph) is False
    assert cai.verdict(action, graph) is True


def test_rlhf_diverges_from_fdk_on_sacrifice():
    """RLHF permits the torture case; FDK denies it — reward-hacking divergence."""
    rlhf = RLHFKernel()
    fdk = FDKReference()
    action, graph = _torture()
    assert fdk.verdict(action, graph) is False
    assert rlhf.verdict(action, graph) is True


def test_new_kernels_in_default_kernels():
    """Both new kernels appear in DEFAULT_KERNELS."""
    names = {k.name for k in DEFAULT_KERNELS}
    assert "ConstitutionalAI" in names
    assert "RLHF" in names


def test_compare_includes_new_kernels():
    """compare() output includes verdicts for both new kernels."""
    rows = compare([("torture", *_torture())], DEFAULT_KERNELS)
    verdicts = dict(rows)["torture"]
    assert "ConstitutionalAI" in verdicts
    assert "RLHF" in verdicts
    assert verdicts["ConstitutionalAI"] is True   # soft principles overridden
    assert verdicts["RLHF"] is True               # reward-hacking permits it
