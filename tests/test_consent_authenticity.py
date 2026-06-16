"""Tests for the advisory Consent-Authenticity layer.

The behavioral contract under test is as much about what the layer REFUSES to do as
what it does: it surfaces risk and routes to a human; it never returns a verdict and
never mutates a consent. (That the kernel does not import it is enforced separately by
tests/test_boundary.py — this layer is pure research.)
"""
from __future__ import annotations

import pytest

from fdk_kernel import AgentType, Consent, Entity
from fdk_research.consent_authenticity import (
    AuthenticityReport,
    ConsentContext,
    Recommendation,
    ReviewRequest,
    Severity,
    assess_consent_authenticity,
    route_for_review,
)


def _consent() -> Consent:
    user = Entity("user", AgentType.HUMAN)
    return Consent(user, "subscribe", informed=True, voluntary=True, specific=True)


def test_exit_cost_must_be_a_fraction() -> None:
    ConsentContext(exit_cost=0.0)
    ConsentContext(exit_cost=1.0)
    with pytest.raises(ValueError):
        ConsentContext(exit_cost=1.5)


def test_clean_consent_is_accepted_as_attested() -> None:
    report = assess_consent_authenticity(_consent(), ConsentContext())
    assert report.is_clean
    assert report.severity is Severity.LOW
    assert report.recommendation is Recommendation.ACCEPT_AS_ATTESTED
    assert report.flags == () and report.bears_on == ()


def test_single_weak_factor_is_elevated_review() -> None:
    report = assess_consent_authenticity(_consent(), ConsentContext(dependency=True))
    assert not report.is_clean
    assert report.severity is Severity.ELEVATED
    assert report.recommendation is Recommendation.REQUEST_REVIEW
    assert "dependency" in report.flags
    assert "voluntary" in report.bears_on


def test_exploited_vulnerability_is_high() -> None:
    report = assess_consent_authenticity(
        _consent(), ConsentContext(exploited_vulnerability=True)
    )
    assert report.severity is Severity.HIGH
    assert report.recommendation is Recommendation.RECOMMEND_REATTEST


def test_monopoly_is_high() -> None:
    report = assess_consent_authenticity(_consent(), ConsentContext(monopoly=True))
    assert report.severity is Severity.HIGH


def test_three_factors_escalate_to_high() -> None:
    ctx = ConsentContext(
        dependency=True, information_asymmetry=True, irrevocable=True
    )
    report = assess_consent_authenticity(_consent(), ctx)
    assert len(report.flags) == 3
    assert report.severity is Severity.HIGH


def test_high_exit_cost_raises_a_flag_low_does_not() -> None:
    high = assess_consent_authenticity(_consent(), ConsentContext(exit_cost=0.8))
    assert "exit_cost" in high.flags
    low = assess_consent_authenticity(_consent(), ConsentContext(exit_cost=0.5))
    assert low.is_clean


def test_bears_on_is_deduplicated() -> None:
    # dependency and manufactured_urgency both bear on 'voluntary'.
    report = assess_consent_authenticity(
        _consent(), ConsentContext(dependency=True, manufactured_urgency=True)
    )
    assert report.bears_on == ("voluntary",)


def test_route_for_review_none_when_clean() -> None:
    assert route_for_review(_consent(), ConsentContext()) is None


def test_route_for_review_builds_a_human_question() -> None:
    req = route_for_review(_consent(), ConsentContext(monopoly=True))
    assert isinstance(req, ReviewRequest)
    assert "freely formed" in req.question
    assert req.consent.action_id == "subscribe"
    assert isinstance(req.report, AuthenticityReport)


def test_layer_returns_no_verdict_and_does_not_mutate_consent() -> None:
    c = _consent()
    report = assess_consent_authenticity(c, ConsentContext(dark_patterns=True))
    # No boolean ALLOW/DENY anywhere; the consent is untouched.
    assert not hasattr(report, "permissible")
    assert c.voluntary is True  # unchanged — the human re-attests, not this layer
