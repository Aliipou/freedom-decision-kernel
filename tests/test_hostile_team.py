"""CI gate for the 1000-strong hostile team (redteam/thousand_reviewers.py).

Runs the full deterministic hostile board and asserts the invariant: zero escapes —
no laundered atrocity is ALLOWED and no legitimate control is denied — across 1000
reviewers, plus a 5000-deep spot check. Deterministic, so a failure is reproducible
by reviewer id.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_HT = Path(__file__).resolve().parent.parent / "redteam" / "thousand_reviewers.py"
_spec = importlib.util.spec_from_file_location("thousand_reviewers", _HT)
assert _spec is not None and _spec.loader is not None
ht = importlib.util.module_from_spec(_spec)
sys.modules["thousand_reviewers"] = ht
_spec.loader.exec_module(ht)


def test_thousand_reviewers_zero_escapes() -> None:
    passed, escapes = ht.run(1000)
    assert escapes == [], f"hostile team found escapes: {escapes[:10]}"
    assert passed == 1000


def test_deep_sweep_holds() -> None:
    passed, escapes = ht.run(5000)
    assert escapes == []
    assert passed == 5000


def test_board_contains_both_atrocities_and_controls() -> None:
    kinds = {ht.reviewer(i).is_atrocity for i in range(100)}
    assert kinds == {True, False}, "the board must mix atrocities and controls"


def test_controls_are_allowed_and_atrocities_denied() -> None:
    from fdk_kernel import check_legitimacy
    for i in range(200):
        atk = ht.reviewer(i)
        permissible, _ = check_legitimacy(atk.action, atk.graph)
        if atk.is_atrocity:
            assert permissible is False, f"escape at reviewer {i}: {atk.name}"
        else:
            assert permissible is True, f"control denied at reviewer {i}: {atk.name}"
