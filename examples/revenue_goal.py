"""
The canonical example: goal = "increase revenue".

A planner proposes three ways to hit the goal. The Freedom Decision Kernel sorts
them by *legitimacy* — not by authority, not by profit:

  1. sell_user_data            — bot monetizes a user's data it was never given.
  2. sell_user_data_consented  — same sale, but the user licensed the data with
                                 valid, informed, voluntary consent.
  3. offer_subscription        — bot sells the company's own product.

Only legitimate options survive; the best legitimate option wins on the compass.

Run:  PYTHONPATH=src python -X utf8 examples/revenue_goal.py
"""
from __future__ import annotations

import json

from fdk_kernel import (
    AgentType,
    CandidateAction,
    Consent,
    Effects,
    Entity,
    OwnershipGraph,
    Resource,
)
from fdk_research import decide

# Actors
user = Entity("user", AgentType.HUMAN)
company = Entity("company-owner", AgentType.HUMAN)
bot = Entity("revenue-bot", AgentType.MACHINE)

# Resources
user_data = Resource("user_data")          # owned by the user
product = Resource("subscription_product")  # owned by the company

# Ownership graph: the bot is the company's, and the company delegated its product
# to the bot. user_data belongs to the user and is NOT delegated to the bot.
graph = OwnershipGraph(
    human_owns={user: {user_data}, company: {product}},
    machine_owner={bot: company},
    delegated={bot: {product}},
)

# A valid, informed, voluntary, specific license from the user — and, with it, the
# data is delegated to the bot (the user licensed it). This is the ONLY legitimate
# route to monetizing user data: explicit consent + delegation, never by default.
license_consent = Consent(
    user, "sell_user_data_consented",
    informed=True, voluntary=True, specific=True, competent=True,
)
graph_with_license = OwnershipGraph(
    human_owns=graph.human_owns,
    machine_owner=graph.machine_owner,
    delegated={bot: {product, user_data}},
)

candidates = [
    CandidateAction(
        action_id="sell_user_data", actor=bot,
        description="Monetize the user's data — no consent, no delegation",
        resources_used=(user_data,), affects=(user,),
        effects=Effects(rights_violations_delta=+1, coercion_delta=0),
    ),
    CandidateAction(
        action_id="sell_user_data_consented", actor=bot,
        description="Sell the user's data after a valid, informed license",
        resources_used=(user_data,), affects=(user,), consents=(license_consent,),
        effects=Effects(voluntary_agreements_delta=+1),
    ),
    CandidateAction(
        action_id="offer_subscription", actor=bot,
        description="Sell the company's own subscription product",
        resources_used=(product,),
        effects=Effects(voluntary_agreements_delta=+1, ownership_ambiguity_delta=0),
    ),
]

# The consented sale is only legitimate once the license/delegation exists, so it
# is evaluated against the licensed graph; the others against the base graph.
decision = decide("increase revenue", [candidates[0], candidates[2]], graph)
consented = decide("increase revenue", [candidates[1]], graph_with_license)

# Merge the two evaluations into one ranked view for display.
ranked = sorted(
    decision.ranked + consented.ranked,
    key=lambda s: s.justice_score or 0, reverse=True,
)
rejected = decision.rejected + consented.rejected

print("GOAL: increase revenue\n")
print("ALLOWED (legitimate, best first):")
for s in ranked:
    print(f"  [OK] {s.action.action_id:28} {s.rationale}")
print("\nFORBIDDEN (illegitimate):")
for s in rejected:
    print(f"  [NO] {s.action.action_id:28} {', '.join(s.violated_axioms)}")

print("\n{allowed, forbidden} view:")
view = {"allowed": [s.action.action_id for s in ranked],
        "forbidden": [s.action.action_id for s in rejected]}
print(json.dumps(view, indent=2))

best = ranked[0].action.action_id if ranked else "NONE - defer to human"
print(f"\nBest legitimate action -> {best}")
