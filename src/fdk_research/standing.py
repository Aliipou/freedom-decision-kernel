"""Standing — advisory layer (FDK 2.0, Project A). RESEARCH LAYER.

The frozen kernel is a legitimacy predicate for a *competent, living, consenting
adult person*. Standing asks the prior question it cannot: who is a rights-holder at
all? Infant, the incapacitated, a coma patient, a fetus, an animal, an ecosystem, a
future generation, an AGI. This module classifies a subject's standing and recommends
how — if at all — to express it in the unchanged kernel. It is **advisory only**: it
returns no verdict, mutates nothing, and (per the roadmap) never assumes
``infant = adult``, ``animal = human``, or ``future = present owner``.

Crucially, it is honest about its own limits: several classes of being have **no
standing object in v1.0 at all**, and this module says so loudly rather than faking a
representation (which would mean smuggling a new axiom into a frozen kernel). Closing
those cases is future work that may change the primitive — which is exactly why it
lives out here, not in ``fdk_kernel``. See ``spec/STANDING.md``. Imports nothing into
the kernel (``tests/test_boundary.py``).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class StandingKind(Enum):
    """How a subject can hold rights, ordered from fully-representable to not."""

    FULL_PERSON = "full-person"                          # competent adult: consents for self
    GUARDIAN_REPRESENTED = "guardian-represented"        # child/incapacitated WITH a surrogate
    PROTECTED_NON_CONSENTER = "protected-non-consenter"  # cannot consent, no surrogate
    NO_STANDING_IN_V1 = "no-standing-in-v1"              # animal/ecosystem/future/AGI


@dataclass(frozen=True)
class StandingFacts:
    """An advisory description of a subject — supplied by a human/proposer, not read
    from the kernel (the kernel's ``Entity`` has no age, species, or vitality). These
    are observable status facts, not judgments of worth."""

    is_human: bool
    is_living: bool = True
    is_present: bool = True       # False for future (or past) persons
    is_competent: bool = True     # False for infant / incapacitated / coma
    has_guardian: bool = False    # a surrogate who can attest on the subject's behalf


@dataclass(frozen=True)
class StandingAssessment:
    """Advisory output. ``representable_in_v1`` is the honest flag: can the frozen
    kernel express this subject as a rights-holder at all? It is never a verdict."""

    kind: StandingKind
    representable_in_v1: bool
    rationale: str
    recommendation: str


def assess_standing(facts: StandingFacts) -> StandingAssessment:
    """Classify standing and recommend how to represent it in the frozen kernel.

    Pure and deterministic. Advisory only — returns no ALLOW/DENY and mutates nothing.
    """
    # Non-human subjects (animals, ecosystems, AGI as a rights-holder) have no
    # standing object in v1.0: the kernel's persons are HUMAN, and a MACHINE is a tool,
    # never a rights-bearer. This is the honest gap, not a solved case.
    if not facts.is_human:
        return StandingAssessment(
            StandingKind.NO_STANDING_IN_V1, False,
            "non-human subject: the frozen model has no rights-holder for animals, "
            "ecosystems, or machine persons.",
            "Do NOT shoehorn into the kernel. Treat as out-of-frame and flag for the "
            "Standing research program; representing it may change the primitive.",
        )

    # Non-present persons (future generations; the dead) cannot be an `Entity` in
    # `affects` without an impossible signature — they are unrepresentable in v1.0.
    if not (facts.is_living and facts.is_present):
        return StandingAssessment(
            StandingKind.NO_STANDING_IN_V1, False,
            "non-present person (future generation or the dead): no Entity can stand "
            "for them, so duties toward them are not expressible in v1.0.",
            "Out-of-frame. Intergenerational standing is open research; do not fake it "
            "with a placeholder Entity.",
        )

    # Present, living, competent adult: the kernel's native case.
    if facts.is_competent:
        return StandingAssessment(
            StandingKind.FULL_PERSON, True,
            "competent living present person: holds standing directly.",
            "Represent normally — the subject attests their own Consent.",
        )

    # Present but not competent (infant, incapacitated) WITH a surrogate: representable
    # by having the guardian attest, as a recommendation a human acts on.
    if facts.has_guardian:
        return StandingAssessment(
            StandingKind.GUARDIAN_REPRESENTED, True,
            "non-competent person with a surrogate: standing is exercised through a "
            "guardian.",
            "Construct the kernel Consent with the GUARDIAN as the attesting human, "
            "acting on the subject's behalf — and record the representation. The kernel "
            "is unchanged; the guardianship is asserted by a human, not inferred here.",
        )

    # Non-competent with no surrogate: the kernel protects them by DENYING for lack of
    # valid consent — protective, but only by omission, not by a first-class doctrine.
    return StandingAssessment(
        StandingKind.PROTECTED_NON_CONSENTER, True,
        "non-competent person with no surrogate: cannot validly consent, so the kernel "
        "denies any action on them for want of consent.",
        "DEFER to a human: appoint a guardian before acting. The protection here is a "
        "side-effect of default-deny, not a best-interests mechanism — that is open work.",
    )
