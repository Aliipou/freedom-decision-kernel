"""Aggregation — collective-ownership advisory layer (FDK 2.0, Project B). RESEARCH.

The frozen kernel models **one human owner per resource** (`OwnershipGraph.human_owns`).
The real world is full of things no single person owns — a corporation, a DAO, a
nation, a river, the ocean, a model trained on a billion people's data. This module
**classifies** such a collective into a :class:`CollectiveForm`, and reports whether
that form can be **represented in the frozen v1.0 kernel** and, if so, *how* — by a
reduction to the existing single-owner primitive (e.g. expand a unanimous group into
one consent per member, or treat a chartered corporation as its own owning ``Entity``).

It is **advisory only**: it returns an :class:`AggregationAssessment`, never a verdict.
It does not ALLOW, DENY, or DEFER; it does not mutate the kernel or add a "group owner".
Adding such a field would be editing the frozen ownership model — an axiom by the back
door (``spec/FREEZE.md`` §5). So we reduce, or we declare the gap.

Crucially, three of six forms **cannot** be honestly reduced, and this module flags
them loudly (``representable_in_v1 = False``) rather than faking a solution:

* ``MAJORITY_COLLECTIVE`` — binding dissenters without their consent is the kernel's
  textbook violation; the Arrow/Sen wall (FDK escapes those theorems only by building
  no social ordering, which is why it cannot make their collective choices).
* ``COMMONS_NONEXCLUDABLE`` — no owner ⇒ no boundary ⇒ the gate has nothing to check;
  the tragedy-of-the-commons gap.
* ``UNOWNED`` — no live claimant; the origin-of-title bootstrapping gap.

See ``spec/AGGREGATION.md`` and ``spec/LIMITATIONS.md`` §2. Imports nothing into
``fdk_kernel`` (the golden boundary, ``tests/test_boundary.py``). Pure and
deterministic; the taxonomy is a transparent hand-set v0 rule — the shape of the
answer, not the answer.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CollectiveForm(Enum):
    """A structural FORM of collective ownership — how a thing is owned, not how it
    *should* be. The first three reduce to the frozen single-owner primitive; the last
    three cannot be represented in v1.0 and are documented as gaps, not solutions."""

    UNANIMOUS_GROUP = "unanimous-group"
    CHARTERED_ENTITY = "chartered-entity"
    REPRESENTED_COLLECTIVE = "represented-collective"
    MAJORITY_COLLECTIVE = "majority-collective"
    COMMONS_NONEXCLUDABLE = "commons-nonexcludable"
    UNOWNED = "unowned"


# The three forms that reduce cleanly to the frozen single-owner kernel.
_REPRESENTABLE: frozenset[CollectiveForm] = frozenset(
    {
        CollectiveForm.UNANIMOUS_GROUP,
        CollectiveForm.CHARTERED_ENTITY,
        CollectiveForm.REPRESENTED_COLLECTIVE,
    }
)

# Per-form advisory recommendation: a *reduction* for the representable forms, or a
# loud, explicit non-solution naming the gap for the rest. Never a verdict.
_RECOMMENDATION: dict[CollectiveForm, str] = {
    CollectiveForm.UNANIMOUS_GROUP: (
        "Reduce to the frozen primitive: require a valid Consent from EVERY member and "
        "attach one per member to the CandidateAction. One hold-out yields no valid "
        "consent and the unchanged kernel denies on its normal grounds. The quantifier "
        "'all members agree' lives outside the kernel; the single-owner gate is run once "
        "per owner."
    ),
    CollectiveForm.CHARTERED_ENTITY: (
        "Reduce to the frozen primitive: treat the chartered entity as its OWN owning "
        "Entity in OwnershipGraph.human_owns. Its internal governance (board, "
        "shareholders, token rule) decides what IT consents to outside the kernel; the "
        "kernel sees exactly one owner and checks one consent."
    ),
    CollectiveForm.REPRESENTED_COLLECTIVE: (
        "Reduce to the frozen primitive: model the representative as holding a SCOPED, "
        "revocable delegation (OwnershipGraph.delegated / machine_scope, A5 "
        "containment) from each principal. Valid only while the mandate is intact; "
        "outside the mandate it collapses to UNANIMOUS_GROUP and needs unanimity again."
    ),
    CollectiveForm.MAJORITY_COLLECTIVE: (
        "NOT representable in v1.0. A majority cannot supply the dissenters' consent; "
        "binding them reads to the kernel as confiscation/coercion and is DENIED. This "
        "is the Arrow/Sen wall (LIMITATIONS.md §2): FDK escapes those impossibility "
        "theorems only by building NO social ordering, which is why it cannot make this "
        "collective choice. Do not launder a majority into the missing consents; obtain "
        "genuine unanimity (degrade to UNANIMOUS_GROUP) or record the DENY as an honest "
        "divergence."
    ),
    CollectiveForm.COMMONS_NONEXCLUDABLE: (
        "NOT representable in v1.0. A true commons / non-excludable good has NO owner, so "
        "there is no boundary for the gate to check: every individual use is invisibly "
        "ALLOW and individually-legitimate uses sum to collective collapse "
        "(tragedy of the commons, LIMITATIONS.md §2). Do not fabricate an owner; this is "
        "a documented scope limit, not a decided case."
    ),
    CollectiveForm.UNOWNED: (
        "NOT representable in v1.0. No live claimant means the kernel has nothing to bind "
        "a consent to, and it cannot legitimize an origin of title (the bootstrapping "
        "gap, FOUNDATIONAL_ATTACKS.md; no input-graph kernel can). Do not fabricate an "
        "owner; this is a documented scope limit, not a decided case."
    ),
}

# Which documented limitation a non-representable form points at (None when it reduces).
_GAP_CITATION: dict[CollectiveForm, str | None] = {
    CollectiveForm.UNANIMOUS_GROUP: None,
    CollectiveForm.CHARTERED_ENTITY: None,
    CollectiveForm.REPRESENTED_COLLECTIVE: None,
    CollectiveForm.MAJORITY_COLLECTIVE: "LIMITATIONS.md §2 (Aggregation; Arrow/Sen)",
    CollectiveForm.COMMONS_NONEXCLUDABLE: "LIMITATIONS.md §2 (tragedy of the commons)",
    CollectiveForm.UNOWNED: "LIMITATIONS.md §2 + FOUNDATIONAL_ATTACKS.md (bootstrapping)",
}


@dataclass(frozen=True)
class AggregationAssessment:
    """The advisory output. Carries no verdict — only the classified collective form,
    whether it is representable in the frozen v1.0 kernel, the recommended reduction (or
    an explicit non-solution naming the gap), and, for a gap, the limitation it cites."""

    form: CollectiveForm
    representable_in_v1: bool
    recommendation: str
    gap_citation: str | None

    @property
    def is_gap(self) -> bool:
        """True when this collective form cannot be represented in v1.0 — a documented
        scope limit, loudly flagged rather than silently faked."""
        return not self.representable_in_v1


def assess_aggregation(form: CollectiveForm) -> AggregationAssessment:
    """Classify a collective-ownership ``form`` and report how (if at all) to express it
    in the frozen single-owner kernel.

    Pure and deterministic. Returns an :class:`AggregationAssessment` — advisory only,
    never a verdict, never a mutation. Representability is a transparent rule: the
    unanimous group, the chartered entity, and the scoped represented collective reduce
    to the single-owner primitive; the majority collective, the non-excludable commons,
    and the unowned thing do not, and are flagged as documented gaps.
    """
    representable = form in _REPRESENTABLE
    return AggregationAssessment(
        form=form,
        representable_in_v1=representable,
        recommendation=_RECOMMENDATION[form],
        gap_citation=_GAP_CITATION[form],
    )


def representable_forms() -> tuple[CollectiveForm, ...]:
    """The collective forms that reduce to the frozen single-owner kernel, in enum
    order. Advisory metadata for callers building reductions."""
    return tuple(f for f in CollectiveForm if f in _REPRESENTABLE)


def gap_forms() -> tuple[CollectiveForm, ...]:
    """The collective forms that CANNOT be represented in v1.0, in enum order — the
    honest gaps (majority binding, non-excludable commons, unowned things)."""
    return tuple(f for f in CollectiveForm if f not in _REPRESENTABLE)
