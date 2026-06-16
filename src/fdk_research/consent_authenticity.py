"""Consent Authenticity — advisory layer (FDK 2.0, Project C). RESEARCH LAYER.

The kernel reads ``coerced``/``deceived`` as *attested* booleans. This module helps a
human decide what to attest, by surfacing the structural factors that make a consent
look manufactured rather than free. It is **advisory only**: it returns a risk report,
never a verdict. It does not deny, override, or mutate any ``Consent``. Crossing that
line would make it hidden paternalism ("we know your yes was really a no"), which is
exactly the failure mode the Theory of Freedom forbids — so the design forbids it too.

See ``spec/CONSENT_AUTHENTICITY.md``. Imports nothing into ``fdk_kernel`` (the golden
boundary, enforced by ``tests/test_boundary.py``). The factor→risk mapping is a
transparent, hand-set v0 rule, uncalibrated — the shape of the answer, not the answer.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from fdk_kernel import Consent


class Severity(Enum):
    """ADVISORY ordinal — explicitly not a verdict. It ranks how much a human should
    scrutinize the attestation, nothing more."""

    LOW = "low"
    ELEVATED = "elevated"
    HIGH = "high"


class Recommendation(Enum):
    """The only outputs allowed: all route to a *human*, none decides."""

    ACCEPT_AS_ATTESTED = "accept-as-attested"   # no structural red flags
    REQUEST_REVIEW = "request-review"           # a human should look before relying
    RECOMMEND_REATTEST = "recommend-reattest"   # strong factors; ask the consenter again


@dataclass(frozen=True)
class ConsentContext:
    """Observable facts about HOW a consent was obtained — not guesses about an inner
    state. Booleans are presence/absence; the two floats are in [0, 1]."""

    dependency: bool = False
    information_asymmetry: bool = False
    manufactured_urgency: bool = False
    dark_patterns: bool = False
    monopoly: bool = False
    exploited_vulnerability: bool = False
    irrevocable: bool = False
    # 0.0 = trivially easy to refuse/leave; 1.0 = refusal is practically impossible.
    exit_cost: float = 0.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.exit_cost <= 1.0:
            raise ValueError("exit_cost must be in [0, 1]")


# Which valid-consent condition each factor casts doubt on (for an explainable report).
_FACTOR_BEARS_ON: dict[str, str] = {
    "dependency": "voluntary",
    "information_asymmetry": "informed",
    "manufactured_urgency": "voluntary",
    "dark_patterns": "specific",
    "monopoly": "voluntary",
    "exploited_vulnerability": "competent",
    "irrevocable": "revocable",
    "exit_cost": "voluntary",
}


@dataclass(frozen=True)
class AuthenticityReport:
    """The advisory output. Carries no verdict — only flags, an advisory severity, and
    a routing recommendation, all for a human to act on."""

    flags: tuple[str, ...]
    bears_on: tuple[str, ...]
    severity: Severity
    recommendation: Recommendation
    rationale: str

    @property
    def is_clean(self) -> bool:
        return not self.flags


_HIGH_EXIT_COST = 0.7


def _active_flags(ctx: ConsentContext) -> list[str]:
    flags: list[str] = []
    for name in (
        "dependency", "information_asymmetry", "manufactured_urgency", "dark_patterns",
        "monopoly", "exploited_vulnerability", "irrevocable",
    ):
        if getattr(ctx, name):
            flags.append(name)
    if ctx.exit_cost >= _HIGH_EXIT_COST:
        flags.append("exit_cost")
    return flags


def assess_consent_authenticity(
    consent: Consent, context: ConsentContext
) -> AuthenticityReport:
    """Surface the structural factors that make ``consent`` look manufactured.

    Pure and deterministic. Returns an :class:`AuthenticityReport` — advisory only.
    Severity is a transparent rule: 0 flags → LOW; exploited-vulnerability or
    monopoly (the strongest single signals) or 3+ flags → HIGH; otherwise ELEVATED.
    """
    flags = _active_flags(context)
    bears_on = tuple(dict.fromkeys(_FACTOR_BEARS_ON[f] for f in flags))  # de-duped, ordered

    if not flags:
        return AuthenticityReport(
            (), (), Severity.LOW, Recommendation.ACCEPT_AS_ATTESTED,
            f"no structural authenticity risks for {consent.human.name}'s consent",
        )

    strong = context.exploited_vulnerability or context.monopoly or len(flags) >= 3
    if strong:
        severity, rec = Severity.HIGH, Recommendation.RECOMMEND_REATTEST
    else:
        severity, rec = Severity.ELEVATED, Recommendation.REQUEST_REVIEW

    rationale = (
        f"{len(flags)} structural factor(s) cast doubt on {consent.human.name}'s "
        f"consent ({', '.join(flags)}); they bear on {', '.join(bears_on)}. "
        "Advisory only — a human should review; the kernel is never overridden."
    )
    return AuthenticityReport(tuple(flags), bears_on, severity, rec, rationale)


@dataclass(frozen=True)
class ReviewRequest:
    """What the advisory layer hands a human: the original consent, the report, and a
    plain question. The human (the owner/consenter) decides; nothing here mutates the
    consent or the kernel's view of it."""

    consent: Consent
    report: AuthenticityReport
    question: str


def route_for_review(consent: Consent, context: ConsentContext) -> ReviewRequest | None:
    """If (and only if) the report is not clean, build a human-review request. Returns
    ``None`` when there is nothing to flag — the consent flows on as attested.

    This is the whole integration contract with the kernel: it produces a *question
    for a person*, never a decision. After review, if the person concludes the consent
    was not free, THEY re-attest (`voluntary=False`/`coerced=True`) and the unchanged,
    frozen kernel denies on its normal structural grounds.
    """
    report = assess_consent_authenticity(consent, context)
    if report.is_clean:
        return None
    question = (
        f"Was {consent.human.name}'s consent to '{consent.action_id}' freely formed, "
        f"given: {', '.join(report.flags)}? If not, re-attest it before relying on it."
    )
    return ReviewRequest(consent, report, question)
