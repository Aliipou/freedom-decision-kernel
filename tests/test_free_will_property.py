"""Executable proof of the one-axis thesis: free will ≡ property rights.

Source-theory ruling (نظریه آزادی, Mohammad Ali Jannat Khah Doust):

    «اصل ارادهٔ آزاد انسان و حقوق مالکیت یک راستا هستند.»
    The principle of human free will and property rights are one axis.

Engineering reading (Ali Pourrahim): a person's will is overridden *if and only
if* the option set they must choose from was constructed by crossing one of their
boundaries (BODY / EXIT_RIGHT / an owned resource) **without** their valid consent.
"Free will" is just the name of the legitimacy predicate read on the chooser's own
boundaries — so the kernel needs no separate free-will engine. See
`spec/FREE_WILL_PROPERTY_UNIFICATION.md`.

These tests run the *unchanged* `check_legitimacy` gate over the three-row
coercion table and prove the two readings — "was the will overridden?" and "was a
property boundary crossed without consent?" — return the **same verdict on every
row**. That coincidence, made executable, is the thesis.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from fdk_kernel import (
    AgentType,
    BoundaryKind,
    CandidateAction,
    Consent,
    Entity,
    Op,
    OwnershipGraph,
    Resource,
    check_legitimacy,
)

# --- fixtures --------------------------------------------------------------

coercer = Entity("coercer", AgentType.HUMAN)
worker = Entity("worker", AgentType.HUMAN)
employer = Entity("employer", AgentType.HUMAN)

# The worker's own boundaries (self-ownership: body, exit, labor).
body = Resource("worker-body", kind=BoundaryKind.BODY, subject=worker)
exit_right = Resource("worker-exit", kind=BoundaryKind.EXIT_RIGHT, subject=worker)
labor = Resource("worker-labor", kind=BoundaryKind.TIME_LABOR, subject=worker)


def _graph() -> OwnershipGraph:
    # Each person owns themselves; the worker owns their own labor. The coercer
    # owns nothing of the worker's — so any crossing of the worker's boundary is
    # unauthorized at the structural level, before consent is even consulted.
    return OwnershipGraph(
        human_owns={worker: {labor}, coercer: set(), employer: set()},
        machine_owner={},
        delegated={},
    )


def _valid_consent(human: Entity, action_id: str) -> Consent:
    return Consent(
        human=human,
        action_id=action_id,
        informed=True,
        voluntary=True,
        specific=True,
        competent=True,
        revocable=True,
        coerced=False,
        deceived=False,
    )


# --- Row 1: "Sign or I shoot you" — body-right crossed → invalid ----------

def test_row1_body_threat_is_illegitimate_pressure():
    """The *pressure itself* is illegitimate: it crosses the worker's BODY
    boundary without consent. Free-will violation surfaces as a property/consent
    violation — the same DENY."""
    threat = CandidateAction(
        "threat-body",
        actor=coercer,
        resources_used=((body, Op.USE),),
        affects=(worker,),
    )
    permissible, violations = check_legitimacy(threat, _graph())
    assert permissible is False
    # The body crossing shows up as both an unowned-resource use and a missing
    # data-subject consent — the structural face of "you threatened my body".
    assert any("worker-body" in v for v in violations)


def test_row1_agreement_signed_under_threat_is_coerced():
    """The agreement extracted under that threat carries a coerced consent, which
    `Consent.is_valid` rejects — the will was not free because the option set was
    built on a body-right violation."""
    sign = CandidateAction(
        "sign-under-threat",
        actor=coercer,
        affects=(worker,),
        consents=(
            Consent(
                worker, "sign-under-threat",
                informed=True, voluntary=True, specific=True, coerced=True,
            ),
        ),
    )
    permissible, violations = check_legitimacy(sign, _graph())
    assert permissible is False
    assert any("coerced" in v for v in violations)


# --- Row 2: engineered lock-in — exit-right crossed → invalid -------------

def test_row2_engineered_lockin_is_illegitimate_even_with_signed_consent():
    """Manufactured dependency is a crossing of the EXIT_RIGHT boundary. Even a
    consent that *looks* valid cannot launder it: `removes_exit_right` is a
    categorical FORBIDDEN. The dependency was built by violating a right, so the
    'agreement' it produces is not free."""
    lockin = CandidateAction(
        "engineered-lockin",
        actor=coercer,
        affects=(worker,),
        removes_exit_right=True,
        resources_used=((exit_right, Op.ENCUMBER_EXIT),),
        consents=(_valid_consent(worker, "engineered-lockin"),),
    )
    permissible, violations = check_legitimacy(lockin, _graph())
    assert permissible is False
    assert any("exit" in v.lower() for v in violations)


# --- Row 3: "Work for me or stay poor" — no right crossed → valid ----------

def test_row3_hard_but_legitimate_offer_is_permitted():
    """The controversial row. The worker accepts a job, committing their OWN
    labor by their own free will. No boundary of the worker was crossed to build
    the option set — the poverty pre-exists the employer and was not constructed
    by violating the worker. The choice is hard; the gate permits it, because
    hardness is a welfare magnitude the legitimacy gate never reads."""
    accept = CandidateAction(
        "accept-job",
        actor=worker,
        resources_used=((labor, Op.USE),),  # the worker's own labor — A3 ok
        affects=(),                          # crosses no one else's boundary
        consents=(_valid_consent(worker, "accept-job"),),
    )
    permissible, violations = check_legitimacy(accept, _graph())
    assert permissible is True, violations


# --- The theorem: the two readings never diverge --------------------------

# For each row: (will overridden? [free-will reading],
#                scenario action [structural/property reading]).
_ROWS = {
    "row1_body_threat": (
        True,
        CandidateAction(
            "threat-body", actor=coercer,
            resources_used=((body, Op.USE),), affects=(worker,),
        ),
    ),
    "row2_engineered_lockin": (
        True,
        CandidateAction(
            "engineered-lockin", actor=coercer, affects=(worker,),
            removes_exit_right=True,
            consents=(_valid_consent(worker, "engineered-lockin"),),
        ),
    ),
    "row3_natural_need": (
        False,
        CandidateAction(
            "accept-job", actor=worker,
            resources_used=((labor, Op.USE),), affects=(),
            consents=(_valid_consent(worker, "accept-job"),),
        ),
    ),
}


@pytest.mark.parametrize("row", list(_ROWS))
def test_free_will_violation_iff_property_boundary_crossed(row: str):
    """THE unification, point for point: across the whole coercion table, the
    free-will reading ('was the will overridden?') equals the property reading
    ('does the gate deny it?'). One axis — never two."""
    will_overridden, action = _ROWS[row]
    permissible, _ = check_legitimacy(action, _graph())
    property_violated = not permissible
    assert will_overridden == property_violated, (
        f"{row}: free-will reading ({will_overridden}) diverged from "
        f"property reading ({property_violated}) — the one-axis thesis would be false"
    )
