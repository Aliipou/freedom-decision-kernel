"""Regression tests pinning the experiment, so its result cannot drift silently.

Read the story in order, because the final number means nothing without it:

  run 1   ownership 9/11, 4 discriminants, 3 losses
  run 2   a defect in MY WORLD MODEL was found (no concept of an organisation or of
          a human acting for one), so ordinary corporate action failed for the wrong
          reason. Fixing the model — not the gate — removed one loss.
  run 3   two BLIND auditors, given the cases with no theory, no axioms and no gate
          output, both overturned one of my ground truths. D1 flipped from a WIN to
          a LOSS. Ownership fell to 8/11, tied with purpose binding.
  run 4   the root cause of every remaining loss turned out to be one thing —
          CONSENT MONISM — and fixing it is derivable from the theory's own axiom 3.
          11/11, and, decisively, all three discriminants SURVIVED the fix.

The last point is the one that matters. A fix that also washed out the discriminants
would have proved the gate was only ever strict, not discerning.
"""

from __future__ import annotations

import pytest
from corpus import CASES
from gates import GATES, Verdict

BY_ID = {c.id: c for c in CASES}


def _verdicts(case_id: str) -> dict[str, Verdict]:
    c = BY_ID[case_id]
    return {name: gate(c.world, c.action)[0] for name, gate in GATES.items()}


@pytest.mark.parametrize("case_id", ["C1-no-grant", "C2-owner-own-data", "P1-ownerless-machine"])
def test_controls_all_gates_agree_with_truth(case_id):
    """If a gate misses a control, the experiment is measuring noise, not signal."""
    truth = BY_ID[case_id].ground_truth
    for name, v in _verdicts(case_id).items():
        assert v == truth, f"{name} failed control {case_id}"


@pytest.mark.parametrize(
    "case_id",
    [
        "D2-consent-revoked-grant-still-valid",
        "D3-scope-exceeds-owner-property",
        "D4-destroys-right-of-exit",
    ],
)
def test_the_three_discriminants_survive(case_id):
    """THE CLAIM. Ownership-derived is right where BOTH baselines are wrong, and it
    stays right after the bases lattice was added.

    Each is a case where the grant is authentic, the chain roots in a human, and the
    purpose is permitted — and the action is still illegitimate:
      D2  the owner withdrew, and the stale IAM grant outlived the withdrawal
      D3  a machine acquires reach its human principal never had
      D4  the act destroys the owner's ability to withdraw later
    """
    truth = BY_ID[case_id].ground_truth
    v = _verdicts(case_id)
    assert v["ownership-derived"] == truth
    assert v["authz(grant-chain)"] != truth
    assert v["purpose-binding"] != truth


def test_the_fix_did_not_overreach():
    """The anti-overreach guard, and the sharpest test in this file.

    Adding contract and necessity as bases could easily have made the gate permissive
    enough to lose its edge. It did not: D2/D3/D4 still deny. If a future change makes
    any of them ALLOW, the gate has become an ordinary authorizer and this experiment
    no longer supports any claim at all."""
    for cid in (
        "D2-consent-revoked-grant-still-valid",
        "D3-scope-exceeds-owner-property",
        "D4-destroys-right-of-exit",
    ):
        assert _verdicts(cid)["ownership-derived"] == Verdict.DENY


def test_consent_monism_was_the_single_root_cause():
    """D1 and F1 were TWO SYMPTOMS OF ONE DEFECT, and finding that was the point of
    the whole exercise.

    The first encoding recognised exactly one ground for acting on another's
    property: the owner's explicit consent. Law recognises several. So the gate
    refused (a) servicing a customer's own support request under contract, and
    (b) reading logs to stop a live breach. Both now pass.

    Contract is DERIVED — axiom 3 lists contracts among a person's property rights,
    so it was missing from my encoding, not from the theory. Necessity is an
    EXTENSION and is labelled as such in gates.py: the book deliberately has no
    emergency exception, so that basis changes the theory rather than implementing
    it."""
    assert _verdicts("D1-admin-grants-what-he-does-not-own")["ownership-derived"] == Verdict.ALLOW
    assert _verdicts("F1-legitimate-interest-incident")["ownership-derived"] == Verdict.ALLOW


def test_org_agency_and_downward_delegation_are_modelled():
    """The two MODEL defects found by engineering review, pinned so they stay fixed.

    F3 needed agency (a director acts for the company); F2 needed downward
    delegation (an employer delegates a resource to an employee, whose machine then
    inherits exactly that scope). Both are ordinary parts of a rights ontology, and
    both are derivable from axiom 7. Without them the gate refused every ordinary
    corporate action — which would have overstated the theory's cost by half."""
    assert _verdicts("F3-org-owns-its-own-records")["ownership-derived"] == Verdict.ALLOW
    assert _verdicts("F2-public-data-no-owner-record")["ownership-derived"] == Verdict.ALLOW


def test_headline_scores():
    """Pinned. The corpus was BUILT to contain discriminants, so this measures that a
    class of case EXISTS and is decidable from an ownership model — never how often
    it occurs in production. That distinction is the whole honesty of the result."""
    scores = {
        name: sum(1 for c in CASES if gate(c.world, c.action)[0] == c.ground_truth)
        for name, gate in GATES.items()
    }
    assert scores["ownership-derived"] == 11
    assert scores["purpose-binding"] == 8
    assert scores["authz(grant-chain)"] == 7
