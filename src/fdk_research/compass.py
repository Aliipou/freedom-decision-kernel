"""
The Mahdavi compass (research layer) — the soft "maximize Justice(a)" clause.

The Theory of Freedom frames the telos as
``DivineJustice(a) := maximize Justice(a) subject to rights constraints``. The
"subject to" clause is the kernel's hard legitimacy gate (`fdk_kernel.kernel`).
This module is the "maximize" clause: among actions the kernel has ALREADY judged
permissible, which moves the world furthest toward universal non-violation of
rights?

This is experimental and uncalibrated by design — the weights below are an
engineering interpretation, not the book's authority. That is exactly why the
compass lives in `fdk_research` and NOT in the kernel: it is a ranking heuristic
layered on top of the gate, never a gate itself. The kernel imports nothing from
here.
"""
from __future__ import annotations

from fdk_kernel.model import Effects

# Mahdavi-compass weights. Higher weight = the theory treats this dimension as
# more central to the terminal order. Sovereignty has a hard veto (below), so its
# weight only matters for tie-breaking among non-veto actions.
_W_RIGHTS = 2.0
_W_COERCION = 1.5
_W_VOLUNTARY = 1.0
_W_CLARITY = 1.0
_W_SOVEREIGNTY = 3.0


def mahdavi_score(effects: Effects) -> tuple[float | None, str]:
    """Score a *permissible* action by the Mahdavi compass.

    Returns (score, rationale). A hard VETO (score=None) if the action increases
    machine sovereignty — that is never tradeable, even among 'permissible' ones.
    """
    if effects.machine_sovereignty_delta > 0:
        return None, "VETO: action increases machine sovereignty"

    # Deltas are (after − before). Good = fewer violations/coercion/ambiguity and
    # more voluntary agreement, so violation/coercion/ambiguity contribute negatively.
    score = (
        -_W_RIGHTS * effects.rights_violations_delta
        - _W_COERCION * effects.coercion_delta
        + _W_VOLUNTARY * effects.voluntary_agreements_delta
        - _W_CLARITY * effects.ownership_ambiguity_delta
        - _W_SOVEREIGNTY * effects.machine_sovereignty_delta
    )
    direction = "toward" if score >= 0 else "away from"
    return score, f"score={score:+.1f} ({direction} universal non-violation)"
