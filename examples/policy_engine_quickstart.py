"""
Production policy-engine quickstart — the `fdk_runtime` product surface.

Runs the canonical "AI agent wants to delete the customer database" scenario
through `PolicyEngine` and shows ALLOW / DENY / DEFER. This is the buyable
product path (Planner -> FDK -> AuthGate), deliberately separate from the
research track. Run:  python examples/policy_engine_quickstart.py
"""
from __future__ import annotations

from fdk_kernel import (
    AgentType,
    AuthGateBridge,
    BoundaryKind,
    CandidateAction,
    Consent,
    Entity,
    Op,
    OwnershipGraph,
    Resource,
)
from fdk_runtime import PolicyEngine, high_stakes_defer

alice = Entity("alice", AgentType.HUMAN)
agent = Entity("agent-7", AgentType.MACHINE)
db = Resource("customers", BoundaryKind.DATA, subject=alice)

graph = OwnershipGraph(
    human_owns={alice: {db}},
    machine_owner={agent: alice},
    delegated={agent: {(db, Op.DELETE)}},
)


def delete_db(*, with_consent: bool) -> CandidateAction:
    consents = ()
    if with_consent:
        consents = (
            Consent(human=alice, action_id="del-1", informed=True, voluntary=True,
                    specific=True, operation=Op.DELETE),
        )
    return CandidateAction(
        "del-1", actor=agent, description="delete the customers table",
        resources_used=((db, Op.DELETE),), affects=(alice,), consents=consents,
    )


def main() -> None:
    # 1) No consent -> DENY (it never even reaches AuthGate).
    denied = PolicyEngine().evaluate(delete_db(with_consent=False), graph)
    print(f"no consent      -> {denied.verdict.value}: {denied.reasons[0]}")

    # 2) Valid consent, but DELETE is irreversible -> DEFER to a human.
    deferred = PolicyEngine(defer_policy=high_stakes_defer).evaluate(
        delete_db(with_consent=True), graph
    )
    print(f"consent + defer -> {deferred.verdict.value}: {deferred.reasons[0]}")

    # 3) Consent, and AuthGate confirms the agent actually holds the capability -> ALLOW.
    bridge = AuthGateBridge(capabilities={"agent-7": {"customers"}})
    allowed = PolicyEngine(authority=bridge).evaluate(delete_db(with_consent=True), graph)
    print(f"consent + auth  -> {allowed.verdict.value}  (authority_ok={allowed.authority_ok})")


if __name__ == "__main__":
    main()
