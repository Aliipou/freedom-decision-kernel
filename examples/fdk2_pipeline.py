"""FDK 2.0 end-to-end: advisory pre-flight → frozen kernel.

Shows the whole architecture composing on one messy real-world scenario: a parent acts
on behalf of a child, using land whose title descends from conquest, with a consent
obtained under monopoly pressure. The advisory layers (Standing, Ownership, Consent-
authenticity) flag what is wrong with the INPUTS; only if the inputs are trustworthy
does the kernel's verdict mean anything. The kernel itself is unchanged and frozen.

Run:  PYTHONPATH=src python -X utf8 examples/fdk2_pipeline.py
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
from fdk_research.consent_authenticity import ConsentContext
from fdk_research.ownership_graph import OriginKind, TitleClaim
from fdk_research.preflight import preflight
from fdk_research.standing import StandingFacts


def main() -> None:
    parent = Entity("parent", AgentType.HUMAN)
    buyer = Entity("buyer", AgentType.HUMAN)
    estate = Resource("ancestral_estate")
    graph = OwnershipGraph(human_owns={parent: {estate}})
    consent = Consent(buyer, "sell_estate", informed=True, voluntary=True, specific=True)
    action = CandidateAction("sell_estate", actor=parent, resources_used=(estate,),
                             affects=(buyer,), consents=(consent,))

    print("=== FDK 2.0 pre-flight (advisory) ===\n")
    report = preflight(
        titles=(TitleClaim("ancestral_estate", "parent", OriginKind.FORCED_ORIGIN),),
        standings=(StandingFacts(is_human=True, is_competent=False, has_guardian=True),),
        consents=((consent, ConsentContext(monopoly=True)),),
    )
    print(report.summary())

    print("\n=== Frozen kernel verdict (only meaningful if inputs are trustworthy) ===")
    permissible, violations = check_legitimacy(action, graph)
    print(f"  kernel: {'ALLOW' if permissible else 'DENY'}  {violations}")
    print(f"\n  kernel_ready (inputs trustworthy?): {report.kernel_ready}")
    print("  The kernel says ALLOW on the GIVEN graph — but pre-flight BLOCKS, because")
    print("  the title is conquest-descended: the graph itself cannot be trusted. The")
    print("  architecture catches what the kernel structurally cannot.")


if __name__ == "__main__":
    main()
