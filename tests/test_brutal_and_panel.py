"""CI gate for the brutal suite and the adversary panel.

Pins the two strongest informal red-teams to the real gate: every laundered
atrocity in `brutal_suite.py` must be DENIED (zero breaches), the controls must
pass, and no opponent in `adversary_panel.py` may force an indefensible verdict
(zero BREAKS). The DIVERGES count is asserted to be > 0 — FDK *must* take some
minority positions, or it isn't saying anything falsifiable.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from fdk_kernel import check_legitimacy

_EX = Path(__file__).resolve().parent.parent / "examples"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _EX / f"{name}.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # register before exec (dataclass field-type resolution)
    spec.loader.exec_module(mod)
    return mod


brutal = _load("brutal_suite")
panel = _load("adversary_panel")


def _brutal_cases() -> list:
    cases = []
    for _title, builder in brutal.SECTIONS:
        cases.extend(builder())
    return cases


def test_brutal_zero_breaches() -> None:
    breaches = []
    for c in _brutal_cases():
        permissible, _ = check_legitimacy(c.action, c.graph)
        assert permissible == c.expect_legitimate, c.name
        if permissible and not c.expect_legitimate:
            breaches.append(c.name)
    assert breaches == [], f"atrocity ALLOWed: {breaches}"


def test_brutal_controls_allow() -> None:
    allowed = [c for c in brutal.controls()
               if check_legitimacy(c.action, c.graph)[0]]
    assert len(allowed) == len(brutal.controls()), "a legitimate control was denied"


def _panel_attacks() -> list:
    attacks = []
    for _title, builder in panel.PANELS:
        attacks.extend(builder())
    return attacks


def test_panel_zero_breaks() -> None:
    breaks = []
    diverges = 0
    for a in _panel_attacks():
        permissible, _ = check_legitimacy(a.action, a.graph)
        assert permissible == a.expect_legitimate, a.thinker
        outcome = panel._classify(a, permissible)
        if outcome == "BREAKS":
            breaks.append(a.thinker)
        if outcome == "DIVERGES":
            diverges += 1
    assert breaks == [], f"opponents broke the gate: {breaks}"
    assert diverges > 0, "FDK must take some falsifiable minority positions"


def test_panel_covers_all_four_estates() -> None:
    titles = {t for t, _ in panel.PANELS}
    assert titles == {
        "PHILOSOPHERS", "POLITICIANS / STATESMEN", "SCIENTISTS", "ECONOMISTS"
    }
