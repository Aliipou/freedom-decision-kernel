"""Tests for the FDK 2.0 pre-flight (advisory-layer composition)."""
from __future__ import annotations

from fdk_kernel import AgentType, Consent, Entity
from fdk_research.consent_authenticity import ConsentContext
from fdk_research.ownership_graph import OriginKind, TitleClaim
from fdk_research.preflight import PreflightReport, preflight
from fdk_research.standing import StandingFacts


def _consent() -> Consent:
    return Consent(Entity("u", AgentType.HUMAN), "act", informed=True, voluntary=True,
                   specific=True)


def test_clean_inputs_are_kernel_ready() -> None:
    report = preflight(
        titles=(TitleClaim("r", "alice", OriginKind.CONSENSUAL_TRANSFER,
                           cryptographically_verifiable=True),),
        standings=(StandingFacts(is_human=True),),
        consents=((_consent(), ConsentContext()),),
    )
    assert report.warnings == ()
    assert report.kernel_ready is True
    assert "clean" in report.summary()


def test_forced_title_blocks() -> None:
    report = preflight(titles=(TitleClaim("land", "x", OriginKind.FORCED_ORIGIN),))
    assert report.kernel_ready is False
    assert any(w.layer == "ownership" and w.blocking for w in report.warnings)
    assert "DO NOT trust" in report.summary()


def test_title_note_is_non_blocking() -> None:
    report = preflight(titles=(TitleClaim("r", "x", OriginKind.ORIGINAL_ACQUISITION),))
    assert report.kernel_ready is True  # RELY_WITH_NOTE is a note, not a blocker
    assert any(w.layer == "ownership" and not w.blocking for w in report.warnings)
    assert "review notes only" in report.summary()


def test_no_standing_blocks() -> None:
    report = preflight(standings=(StandingFacts(is_human=False),))  # an animal
    assert report.kernel_ready is False
    assert any(w.layer == "standing" and w.blocking for w in report.warnings)


def test_standing_full_person_no_warning() -> None:
    report = preflight(standings=(StandingFacts(is_human=True),))
    assert report.warnings == ()


def test_manufactured_consent_is_review_not_block() -> None:
    # monopoly → HIGH severity → a review note, never a hard block (no paternalism).
    report = preflight(consents=((_consent(), ConsentContext(monopoly=True)),))
    assert report.kernel_ready is True
    assert any(w.layer == "consent-authenticity" and not w.blocking
               for w in report.warnings)


def test_clean_consent_no_warning() -> None:
    report = preflight(consents=((_consent(), ConsentContext()),))
    assert report.warnings == ()


def test_report_type() -> None:
    assert isinstance(preflight(), PreflightReport)
