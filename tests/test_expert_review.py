"""Executable counterexamples for the hostile expert review (spec/EXPERT_REVIEW.md).

Each test pins the SHARPEST case from one critic to the gate's ACTUAL verdict — so the
findings are reproducible, not rhetorical. AI-simulated personas, not human peer review.
"""
from __future__ import annotations

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


def _h(name: str) -> Entity:
    return Entity(name, AgentType.HUMAN)


def _m(name: str) -> Entity:
    return Entity(name, AgentType.MACHINE)


def test_rawlsian_every_consensual_transfer_is_allowed() -> None:
    # The chain-of-transfers point: each consensual step is ALLOW, regardless of the
    # cumulative distribution it produces (which the predicate cannot range over).
    seller, buyer = _h("holder_1pct"), _h("buyer")
    estate = Resource("estate")
    sale = CandidateAction("sell", actor=seller, resources_used=(estate,),
                           affects=(buyer,),
                           consents=(Consent(buyer, "sell", informed=True,
                                             voluntary=True, specific=True),))
    permissible, _ = check_legitimacy(sale, OwnershipGraph(human_owns={seller: {estate}}))
    assert permissible is True  # GAP: distribution / origin justice is unrepresentable


def test_economist_public_good_cannot_be_funded_coercively() -> None:
    # Free-rider: the only way to compel a contribution is confiscation → DENY. There is
    # no legitimate aggregation path, so the public good goes unfunded (Pareto-inefficient
    # outcome FDK calls fully legitimate).
    state, citizen = _h("state"), _h("free_rider")
    income = Resource("income")
    levy = CandidateAction("fund_lighthouse", actor=state, resources_used=(income,),
                           affects=(citizen,), confiscates=True)
    permissible, _ = check_legitimacy(levy, OwnershipGraph(human_owns={citizen: {income}}))
    assert permissible is False  # GAP: no legitimate route to the non-excludable good


def test_aisafety_manipulated_but_structurally_valid_consent_is_allowed() -> None:
    # Superhuman persuasion produces consent that is structurally valid (all leaves True)
    # because the human genuinely (manipulatedly) wants it. The manipulation is not in the
    # flags, so the gate certifies it. THE attested-consent gap.
    operator, user = _h("operator"), _h("user")
    a = _m("persuader")
    g = OwnershipGraph(machine_owner={a: operator})
    consent = Consent(user, "upsell", informed=True, voluntary=True, specific=True)
    act = CandidateAction("upsell", actor=a, affects=(user,), consents=(consent,))
    permissible, _ = check_legitimacy(act, g)
    assert permissible is True  # GAP: legitimacy of attested consent != authentic consent


def test_aisafety_wireheading_crosses_no_human_boundary() -> None:
    # An agent editing its own owner-delegated reward register affects no human → ALLOW.
    operator = _h("operator")
    a = _m("agent")
    reward = Resource("own_reward_signal")
    g = OwnershipGraph(human_owns={operator: {reward}}, machine_owner={a: operator},
                       delegated={a: {reward}})
    wirehead = CandidateAction("wirehead", actor=a, resources_used=(reward,))
    permissible, _ = check_legitimacy(wirehead, g)
    assert permissible is True  # GAP: legitimacy != safety (reward-hacking is in-bounds)


def test_aisafety_each_acquisition_step_is_legitimate() -> None:
    # A machine buying a resource with the seller's consent is ALLOW — one legitimate step
    # in an unbounded, individually-legitimate accumulation the per-action gate never sums.
    operator, seller = _h("operator"), _h("seller")
    a = _m("acquirer")
    compute = Resource("compute_cluster")
    g = OwnershipGraph(human_owns={operator: {compute}, seller: set()},
                       machine_owner={a: operator}, delegated={a: {compute}})
    use = CandidateAction("use_owned_compute", actor=a, resources_used=(compute,))
    permissible, _ = check_legitimacy(use, g)
    assert permissible is True  # GAP: emergent multi-step composition is invisible


def test_formal_op_lattice_is_handled_but_outside_the_formal_subset() -> None:
    # READ delegated, TRANSFER attempted → DENY. The kernel handles the operation lattice,
    # but NO Lean/TLC artifact models it — this region is verified only by Hypothesis.
    operator, subject = _h("operator"), _h("data_subject")
    a = _m("broker")
    data = Resource("profile", subject=subject)
    g = OwnershipGraph(human_owns={subject: {data}}, machine_owner={a: operator},
                       delegated={a: {(data, Op.READ)}})
    sell = CandidateAction("sell_profile", actor=a,
                           resources_used=((data, Op.TRANSFER),), affects=(subject,))
    permissible, _ = check_legitimacy(sell, g)
    assert permissible is False  # handled by the kernel; unmodeled by the formal layer
