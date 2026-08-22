"""Structured constitutional violations — stable axiom + rule IDs for M1 artifacts."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Violation:
    """One constitutional violation under accepted inputs."""

    axiom_id: str
    rule_id: str
    reason: str  # human-readable; same strings as legacy check_legitimacy output
