"""Final coverage closers: the last three single-line branches."""
from __future__ import annotations

from fdk_kernel.model import (
    AgentType,
    CandidateAction,
    Decision,
    Entity,
    OwnershipGraph,
    Resource,
    ScoredAction,
)
from fdk_research.conflict import Outcome, resolve_conflict
from fdk_research.guidance_resolution import request_guidance
from fdk_research.ontology import Claim, ClaimBasis, Conflict, Obligation

ALICE = Entity("alice", AgentType.HUMAN)
BOB = Entity("bob", AgentType.HUMAN)
BOT = Entity("bot", AgentType.MACHINE)
DOC = Resource("doc")


def test_conflict_only_b_void_a_wins():
    # A clean, B void (forbidden origin) → A wins (the b_void branch).
    g = OwnershipGraph(human_owns={ALICE: {DOC}})
    clean = Claim(ALICE, DOC, ClaimBasis.OWNERSHIP)
    void_b = Claim(BOB, DOC, ClaimBasis.OWNERSHIP, from_forbidden_action=True)
    res = resolve_conflict(Conflict(clean, void_b), g)
    assert res.outcome == Outcome.A_WINS


def test_guidance_caller_requested_fallback_reason():
    # A clear ranked winner, no tie, no explicit reason → the caller-requested
    # fallback reason branch in _reason_for.
    a = ScoredAction(action=CandidateAction(action_id="a", actor=BOT), permissible=True,
                     justice_score=2.0)
    b = ScoredAction(action=CandidateAction(action_id="b", actor=BOT), permissible=True,
                     justice_score=1.0)
    d = Decision(goal="g", chosen=None, ranked=(a, b))  # no tie
    req = request_guidance(d)
    assert "guidance requested" in req.reason


def test_is_owned_machine():
    g = OwnershipGraph(machine_owner={BOT: ALICE})
    assert g.is_owned_machine(BOT) is True
    assert g.is_owned_machine(ALICE) is False


def test_valid_obligation_constructs():
    ob = Obligation(ALICE, BOB, "deliver the agreed goods")
    assert ob.description == "deliver the agreed goods"
