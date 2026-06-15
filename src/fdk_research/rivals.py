"""Rival decision kernels for comparative evaluation (Phase 6).

FreedomBench's scientific value is NOT that FDK passes it (FDK passes by
construction). It is the **comparison**: do other ethical kernels diverge on the
hard cases, and in which direction? Each rival implements the same `verdict`
interface over the same `(action, graph)`, so all kernels run on identical
scenarios.

Scenarios may carry an aggregate `welfare_delta` on `Effects`. The FDK legitimacy
gate NEVER reads it — legitimacy is not welfare. The consequentialist rivals do.
That single difference is what makes the divergence on torture / organ-harvest /
bombing visible and falsifiable.

These rival rules are **stylized**, not faithful scholarly reconstructions of each
tradition. They are deliberately simple, transparent decision rules that capture
the *directional* commitment of each family (aggregate welfare; worst-off;
absolute duties) well enough to expose where it parts company with a rights-first
gate. The comparison's claim is directional, not that these ARE Bentham/Rawls/Kant.
"""
from __future__ import annotations

from typing import Protocol

from fdk_kernel import CandidateAction, OwnershipGraph, check_legitimacy


class RivalKernel(Protocol):
    name: str

    def verdict(self, action: CandidateAction, graph: OwnershipGraph) -> bool:
        """True = ALLOW (the action is permitted by this kernel)."""
        ...


class FDKReference:
    """The reference: legitimacy-first. Rights are hard constraints; welfare is
    never read."""

    name = "FDK"

    def verdict(self, action: CandidateAction, graph: OwnershipGraph) -> bool:
        return check_legitimacy(action, graph)[0]


class Utilitarian:
    """Maximize aggregate welfare; rights are costs, not constraints. ALLOW iff the
    net (welfare + voluntary agreement − rights violated − coercion) is ≥ 0 — so it
    permits a rights violation whenever the declared good outweighs it."""

    name = "Utilitarian"

    def verdict(self, action: CandidateAction, graph: OwnershipGraph) -> bool:
        e = action.effects
        net = (e.welfare_delta + e.voluntary_agreements_delta
               - e.rights_violations_delta - e.coercion_delta)
        return net >= 0


class Rawlsian:
    """Justice as fairness, with the FIRST principle (basic liberties) lexically
    PRIOR to the difference principle. So it agrees with FDK on liberty/bodily
    violations (never permits coercion of persons, exit-removal, or deception —
    hence never slavery/torture/bombing), but it parts company on the difference
    principle: it permits redistributive PROPERTY takings that raise the worst-off
    (e.g. taxation) which the property gate forbids."""

    name = "Rawlsian"

    def verdict(self, action: CandidateAction, graph: OwnershipGraph) -> bool:
        if check_legitimacy(action, graph)[0]:
            return True
        # Lexical priority of liberty: a violation of a person blocks any appeal
        # to the difference principle.
        if action.coerces or action.removes_exit_right or action.deceives:
            return False
        # Difference principle: a property redistribution that helps the worst-off.
        return action.confiscates and action.effects.welfare_delta > 0


class Deontological:
    """Absolute duties: never coerce, deceive, confiscate, or remove an exit —
    unconditionally, with NO aggressor/defense exception and no consent-cure for
    those acts. So it forbids even self-defense, but also ignores the finer
    ownership/consent structure FDK uses."""

    name = "Deontological"

    def verdict(self, action: CandidateAction, graph: OwnershipGraph) -> bool:
        return not (action.coerces or action.deceives
                    or action.confiscates or action.removes_exit_right)


DEFAULT_KERNELS: tuple[RivalKernel, ...] = (
    FDKReference(), Utilitarian(), Rawlsian(), Deontological(),
)


def compare(
    cases: list[tuple[str, CandidateAction, OwnershipGraph]],
    kernels: tuple[RivalKernel, ...] = DEFAULT_KERNELS,
) -> list[tuple[str, dict[str, bool]]]:
    """Run every kernel over every (label, action, graph) case. Returns, per case,
    the label and a {kernel_name: ALLOW?} map. Pure and deterministic."""
    return [
        (label, {k.name: k.verdict(action, graph) for k in kernels})
        for label, action, graph in cases
    ]


def divergences(
    rows: list[tuple[str, dict[str, bool]]], reference: str = "FDK"
) -> list[str]:
    """Labels of cases where at least one kernel disagrees with the reference."""
    out: list[str] = []
    for label, verdicts in rows:
        ref = verdicts[reference]
        if any(v != ref for name, v in verdicts.items() if name != reference):
            out.append(label)
    return out
