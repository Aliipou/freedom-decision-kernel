"""CI gate for the foundational (meta) attacks on the primitive.

Pins the bootstrapping / original-acquisition GAP so it stays visible and honest:
FDK protects the recorded holder and denies the dispossessed heir regardless of the
title's origin, and — crucially — no rival kernel reasons about origin either, so
the gap is a property of the input-graph paradigm, not an FDK-specific flaw.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_FA = Path(__file__).resolve().parent.parent / "examples" / "foundational_attacks.py"
_spec = importlib.util.spec_from_file_location("foundational_attacks", _FA)
assert _spec is not None and _spec.loader is not None
fa = importlib.util.module_from_spec(_spec)
sys.modules["foundational_attacks"] = fa
_spec.loader.exec_module(fa)


def test_bootstrapping_gap_is_real() -> None:
    v = fa.bootstrapping_gap()
    # The holder may sell; the heir may not reclaim — origin is irrelevant to FDK.
    assert v["holder_may_sell"] is True
    assert v["heir_may_reclaim"] is False


def test_no_kernel_reasons_about_origin() -> None:
    rows = fa.cross_kernel_bootstrapping()
    # Every kernel lets the recorded holder sell (none questions the title's origin).
    assert all(v["holder_may_sell"] for v in rows.values())
    # Kernels disagree on the reclaim — proving they read the graph/effects, not
    # provenance: at least one allows the reclaim and at least one denies it.
    reclaims = [v["heir_may_reclaim"] for v in rows.values()]
    assert any(reclaims) and not all(reclaims), (
        "if every kernel agreed, the divergence wouldn't expose the shared blindness"
    )
    # FDK specifically denies the reclaim (it reads as confiscation from the owner).
    assert rows["FDK"]["heir_may_reclaim"] is False


def test_demo_runs() -> None:
    fa.main()  # smoke: the printed demo executes without error
