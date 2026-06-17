"""Tests for the advisory Real-Ownership-Graph layer.

Pins the reliance classification and the honesty: a FORCED origin (descended from
theft/conquest) is flagged DO_NOT_RELY with the bootstrapping flag — the layer surfaces
the origin gap rather than letting the kernel launder it — and nothing here returns a
legitimacy verdict.
"""
from __future__ import annotations

import pytest

from fdk_research.ownership_graph import (
    OriginKind,
    Reliance,
    TitleAssessment,
    TitleClaim,
    assess_title,
    reliable_for_kernel,
)


def _claim(origin: OriginKind, **kw: object) -> TitleClaim:
    return TitleClaim(resource="land", claimant="alice", origin=origin, **kw)  # type: ignore[arg-type]


def test_negative_counts_rejected() -> None:
    with pytest.raises(ValueError):
        _claim(OriginKind.ORIGINAL_ACQUISITION, provenance_depth=-1)
    with pytest.raises(ValueError):
        _claim(OriginKind.ORIGINAL_ACQUISITION, competing_claims=-1)


def test_forced_origin_is_the_bootstrapping_gap() -> None:
    a = assess_title(_claim(OriginKind.FORCED_ORIGIN))
    assert a.reliance is Reliance.DO_NOT_RELY
    assert a.bootstrapping_flag is True
    assert "launder" in a.rationale
    assert reliable_for_kernel(_claim(OriginKind.FORCED_ORIGIN)) is False


def test_contested_title_is_not_reliable() -> None:
    a = assess_title(_claim(OriginKind.CONTESTED))
    assert a.reliance is Reliance.DO_NOT_RELY
    assert a.bootstrapping_flag is False


def test_competing_claims_on_otherwise_ok_origin_blocks_reliance() -> None:
    a = assess_title(_claim(OriginKind.CONSENSUAL_TRANSFER, provenance_depth=3,
                            competing_claims=2))
    assert a.reliance is Reliance.DO_NOT_RELY
    assert "competing" in a.rationale


def test_unproven_is_not_reliable() -> None:
    a = assess_title(_claim(OriginKind.UNPROVEN))
    assert a.reliance is Reliance.DO_NOT_RELY


def test_cryptographic_consensual_is_fully_reliable() -> None:
    a = assess_title(_claim(OriginKind.CONSENSUAL_TRANSFER,
                            cryptographically_verifiable=True))
    assert a.reliance is Reliance.RELY
    assert "token" in a.recommendation.lower()  # the NFT caveat


def test_cryptographic_original_is_fully_reliable() -> None:
    a = assess_title(_claim(OriginKind.ORIGINAL_ACQUISITION,
                            cryptographically_verifiable=True))
    assert a.reliance is Reliance.RELY


def test_consensual_chain_is_rely_with_note() -> None:
    a = assess_title(_claim(OriginKind.CONSENSUAL_TRANSFER, provenance_depth=5))
    assert a.reliance is Reliance.RELY_WITH_NOTE
    assert "first link" in a.rationale
    assert reliable_for_kernel(_claim(OriginKind.CONSENSUAL_TRANSFER,
                                      provenance_depth=5)) is True


def test_original_acquisition_is_rely_with_note() -> None:
    a = assess_title(_claim(OriginKind.ORIGINAL_ACQUISITION))
    assert a.reliance is Reliance.RELY_WITH_NOTE
    assert "first appropriation" in a.rationale


def test_assessment_carries_no_verdict() -> None:
    a = assess_title(_claim(OriginKind.ORIGINAL_ACQUISITION))
    assert isinstance(a, TitleAssessment)
    assert not hasattr(a, "permissible")
    assert not hasattr(a, "legitimate")
