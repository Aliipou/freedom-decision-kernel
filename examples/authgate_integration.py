"""
Wire the Freedom Decision Kernel to the REAL AuthGate verifier.

The FDK decides *legitimacy* ("should this happen under property rights?"); the
real AuthGate `FreedomVerifier` decides *authority* ("does this agent hold a
capability?"). This script wires them through the `EnforcementPort` seam and runs
the full loop: FDK legitimacy gate → AuthGate authority → execute.

Run (the `authgate` package must be importable):

    PYTHONPATH="src;../freedom-kernel-work/src" python examples/authgate_integration.py

It is NOT a stub: `AuthGateEnforcement` calls the actual AuthGate verifier.
"""
from __future__ import annotations

from dataclasses import dataclass

from authgate.kernel.entities import Entity as AGEntity
from authgate.kernel.entities import Resource as AGResource
from authgate.kernel.verifier import Action as AGAction
from authgate.kernel.verifier import FreedomVerifier

from fdk_kernel.model import CandidateAction


@dataclass
class AuthGateEnforcement:
    """An FDK `EnforcementPort` backed by a real AuthGate `FreedomVerifier`.

    Maps a chosen FDK `CandidateAction` (by actor/resource *name*) onto an AuthGate
    `Action` over the AuthGate registry, and returns AuthGate's permit/deny verdict.
    Plug this into `FreedomRuntime(..., enforcement=AuthGateEnforcement(...))`.
    """

    verifier: FreedomVerifier
    actors: dict[str, AGEntity]      # FDK actor name → AuthGate entity
    resources: dict[str, AGResource]  # FDK resource name → AuthGate resource

    def authorize(self, action: CandidateAction) -> tuple[bool, str]:
        ag_actor = self.actors.get(action.actor.name)
        if ag_actor is None:
            return False, f"AuthGate: unknown actor {action.actor.name!r}"
        ag_resources = []
        for resource in action.resources_used:
            ag_resource = self.resources.get(resource.name)
            if ag_resource is None:
                return False, f"AuthGate: unknown resource {resource.name!r}"
            ag_resources.append(ag_resource)
        result = self.verifier.verify(
            AGAction(action.action_id, actor=ag_actor, resources_read=ag_resources)
        )
        return result.permitted, result.summary()


def _demo() -> None:  # pragma: no cover - runnable example, not a test
    from authgate.kernel.entities import AgentType as AGType
    from authgate.kernel.entities import ResourceType, RightsClaim
    from authgate.kernel.registry import OwnershipRegistry

    from fdk_kernel.model import AgentType, CandidateAction, Effects, Entity, OwnershipGraph, Resource
    from fdk_research.planner import ListProposer
    from fdk_research.runtime import FreedomRuntime

    # AuthGate side: a registry where bot may READ the doc.
    reg = OwnershipRegistry()
    ag_alice, ag_bot = AGEntity("alice", AGType.HUMAN), AGEntity("bot", AGType.MACHINE)
    ag_doc = AGResource("doc", ResourceType.DATASET, scope="/data/")
    reg.register_machine(ag_bot, ag_alice)
    reg.add_claim(RightsClaim(ag_bot, ag_doc, can_read=True))
    enforcement = AuthGateEnforcement(
        FreedomVerifier(reg.freeze()), {"alice": ag_alice, "bot": ag_bot}, {"doc": ag_doc}
    )

    # FDK side: alice owns doc; bot is alice's machine, delegated doc.
    bot = Entity("bot", AgentType.MACHINE)
    doc = Resource("doc")
    graph = OwnershipGraph(human_owns={Entity("alice", AgentType.HUMAN): {doc}},
                           machine_owner={bot: Entity("alice", AgentType.HUMAN)},
                           delegated={bot: {doc}})
    action = CandidateAction("read", bot, resources_used=(doc,),
                             effects=Effects(voluntary_agreements_delta=1))

    runtime = FreedomRuntime(graph, enforcement=enforcement, executor=lambda a: "DATA")
    result = runtime.step("serve the owner", ListProposer([action]))
    print(f"executed={result.executed} output={result.output!r} deferred={result.deferred}")


if __name__ == "__main__":  # pragma: no cover
    _demo()
