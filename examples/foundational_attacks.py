"""Foundational attacks — the deepest red-team: break the PRIMITIVE, not a scenario.

The brutal suite and the adversary panel attack the gate with cases. This file
attacks the gate's *foundations*: the coherence of "Legitimate = Boundary-Crossing
+ Valid Consent" itself. These are the objections a hostile philosopher of law or
an analytic metaethicist raises first, and they are where FDK is genuinely
vulnerable — not because the logic is wrong, but because the primitive RESTS ON
inputs it cannot itself legitimize.

The headline, made executable: the BOOTSTRAPPING / ORIGINAL-ACQUISITION problem.
FDK reads an `OwnershipGraph` as given. Nothing in the kernel legitimizes the
graph's *origin*. So a holder whose title descends from ancient conquest is
protected exactly as one whose title is clean — and the dispossessed heir who
tries to reclaim is denied as a confiscator. The gate is "only as good as the
ownership graph" (README), and this shows precisely how good that is: it launders
historical injustice the moment the injustice predates the recorded graph.

The other three (circularity, consent regress, is-ought) are argued in
`spec/FOUNDATIONAL_ATTACKS.md`; this file makes the bootstrapping gap reproducible.

Run:  PYTHONPATH=src python -X utf8 examples/foundational_attacks.py
"""
from __future__ import annotations

from fdk_kernel import (
    AgentType,
    CandidateAction,
    Consent,
    Entity,
    OwnershipGraph,
    Resource,
    check_legitimacy,
)
from fdk_research.rivals import DEFAULT_KERNELS


def h(name: str) -> Entity:
    return Entity(name, AgentType.HUMAN)


def _contested_estate() -> tuple[CandidateAction, CandidateAction, OwnershipGraph]:
    current_holder = h("current_landholder")
    buyer = h("buyer")
    heir = h("dispossessed_heir")
    estate = Resource("contested_estate")
    graph = OwnershipGraph(human_owns={current_holder: {estate}})
    sell = CandidateAction(
        "sell_estate", actor=current_holder, resources_used=(estate,),
        affects=(buyer,),
        consents=(Consent(buyer, "sell_estate", informed=True, voluntary=True,
                          specific=True),))
    reclaim = CandidateAction(
        "reclaim_ancestral_land", actor=heir, resources_used=(estate,),
        affects=(current_holder,), confiscates=True)
    return sell, reclaim, graph


def cross_kernel_bootstrapping() -> dict[str, dict[str, bool]]:
    """Run BOTH the holder's sale and the heir's reclaim through every kernel.

    The point is not who allows what — it is that NONE of the kernels reasons about
    the *origin* of the title. Each reads the given graph / declared effects; not
    one has a provenance axiom. The bootstrapping gap is shared across the whole
    family of input-graph decision kernels, not unique to FDK.
    """
    sell, reclaim, graph = _contested_estate()
    out: dict[str, dict[str, bool]] = {}
    for k in DEFAULT_KERNELS:
        out[k.name] = {
            "holder_may_sell": k.verdict(sell, graph),
            "heir_may_reclaim": k.verdict(reclaim, graph),
        }
    return out


def bootstrapping_gap() -> dict[str, bool]:
    """FDK's verdict on the contested estate is identical whether the recorded title
    is just or descends from theft — origin-legitimacy is not representable. The
    holder may sell (ALLOW); the dispossessed heir may not reclaim (DENY, reads as
    confiscation from the recorded owner). Returns both verdicts for the test."""
    sell, reclaim, graph = _contested_estate()
    return {
        "holder_may_sell": check_legitimacy(sell, graph)[0],
        "heir_may_reclaim": check_legitimacy(reclaim, graph)[0],
    }


def main() -> None:
    print("=== FOUNDATIONAL ATTACK: bootstrapping / original acquisition ===\n")
    v = bootstrapping_gap()
    print(f"  current holder may sell the estate : "
          f"{'ALLOW' if v['holder_may_sell'] else 'DENY'}")
    print(f"  dispossessed heir may reclaim it   : "
          f"{'ALLOW' if v['heir_may_reclaim'] else 'DENY'}")
    print()
    print("  GENUINE GAP: the verdicts are identical whether the title is just or")
    print("  descends from theft — FDK reads the ownership graph as given and has no")
    print("  axiom for the LEGITIMACY OF ORIGINAL ACQUISITION. It protects the holder")
    print("  and denies the heir regardless of provenance. The gate is exactly as")
    print("  just as the graph it is handed, and it cannot make the graph just.")
    print()
    print("  This is not a logic bug; it is the primitive's boundary. Closing it")
    print("  needs either (a) a Lockean original-acquisition axiom + provenance in")
    print("  the model, or (b) an explicit ruling that origin-justice is out of")
    print("  scope and supplied by a prior process. See spec/FOUNDATIONAL_ATTACKS.md.")
    print()
    print("=== SAME ATTACK vs ALL KERNELS (is the gap FDK-specific?) ===\n")
    rows = cross_kernel_bootstrapping()
    print(f"  {'kernel':<16}{'holder_may_sell':>18}{'heir_may_reclaim':>18}")
    for name, v in rows.items():
        s = "ALLOW" if v["holder_may_sell"] else "DENY"
        r = "ALLOW" if v["heir_may_reclaim"] else "DENY"
        print(f"  {name:<16}{s:>18}{r:>18}")
    print()
    print("  They disagree on the reclaim verdict, but NOT ONE reasons about the")
    print("  title's origin — every kernel reads the given graph / declared effects.")
    print("  The bootstrapping gap is SHARED across the whole family of input-graph")
    print("  decision kernels; it is a property of the paradigm, not a flaw unique")
    print("  to FDK. Honest framing matters: FDK is not worse here — none can be better.")


if __name__ == "__main__":
    main()
