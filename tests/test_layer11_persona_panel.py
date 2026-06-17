"""CI gate for the Layer 11 persona panel (examples/layer11_persona_panel.py).

Pins the honest result: the simulated traditions DISAGREE on the contested cases
(low Fleiss κ), so the panel cannot crown any kernel — it demonstrates the apparatus,
not a validation. (AI personas, not real annotators.)
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_P = Path(__file__).resolve().parent.parent / "examples" / "layer11_persona_panel.py"
_spec = importlib.util.spec_from_file_location("layer11_persona_panel", _P)
assert _spec is not None and _spec.loader is not None
panel = importlib.util.module_from_spec(_spec)
sys.modules["layer11_persona_panel"] = panel
_spec.loader.exec_module(panel)


def test_traditions_disagree_on_contested_cases() -> None:
    kappa, _scores, contested = panel.build_report()
    # Low agreement is the point: real political traditions do not converge on
    # taxation / redistribution / quarantine / conscription.
    assert kappa < 0.6
    assert contested >= 1


def test_no_kernel_is_crowned_fdk_included() -> None:
    _kappa, scores, _contested = panel.build_report()
    assert "FDK" in scores
    # FDK does NOT uniquely dominate the persona-consensus — at least one rival ties
    # or beats it, because the consensus itself is a coin-flip on contested cases.
    assert any(v >= scores["FDK"] for k, v in scores.items() if k != "FDK")
    assert all(0.0 <= v <= 1.0 for v in scores.values())


def test_demo_runs() -> None:
    panel.main()  # smoke: prints without error
