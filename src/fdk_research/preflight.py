"""Pre-flight — compose the FDK 2.0 advisory layers around the frozen kernel.

The kernel decides legitimacy *given* correct inputs. The advisory layers decide
whether the inputs are trustworthy in the first place. This module is the glue that
makes the architecture real:

    Universe → [pre-flight: Standing + Ownership + Consent-authenticity] → kernel

It runs the advisory layers over a scenario's inputs and produces a consolidated
report: which titles cannot be relied on (Layer 6), which subjects have no standing
(Layer 3), and which consents look manufactured (Layer 5). It is advisory — it does NOT
call the kernel and returns no ALLOW/DENY; it tells a human whether the kernel's verdict
on these inputs can be TRUSTED, or whether the inputs must be fixed first. Imports
nothing into `fdk_kernel`.
"""
from __future__ import annotations

from dataclasses import dataclass

from fdk_kernel import Consent
from fdk_research.consent_authenticity import (
    ConsentContext,
    Severity,
    assess_consent_authenticity,
)
from fdk_research.ownership_graph import Reliance, TitleClaim, assess_title
from fdk_research.standing import StandingFacts, assess_standing


@dataclass(frozen=True)
class PreflightWarning:
    layer: str       # "ownership" | "standing" | "consent-authenticity"
    blocking: bool   # True = the kernel's input is wrong; False = review-only note
    message: str


@dataclass(frozen=True)
class PreflightReport:
    warnings: tuple[PreflightWarning, ...]

    @property
    def kernel_ready(self) -> bool:
        """True iff no BLOCKING input problem — the kernel's verdict on these inputs
        can be trusted. Review-only notes (e.g. high manufactured-consent risk) do not
        block: surfacing them is the job; overriding a stated consent would be the
        paternalism the theory forbids."""
        return not any(w.blocking for w in self.warnings)

    def summary(self) -> str:
        if not self.warnings:
            return "pre-flight clean: inputs are trustworthy; the kernel verdict stands."
        lines = [f"  [{'BLOCK' if w.blocking else 'note '}] {w.layer}: {w.message}"
                 for w in self.warnings]
        verdict = ("inputs OK to trust (review notes only)" if self.kernel_ready
                   else "DO NOT trust the kernel verdict until the BLOCKers are fixed")
        return "pre-flight: " + verdict + "\n" + "\n".join(lines)


def preflight(
    *,
    titles: tuple[TitleClaim, ...] = (),
    standings: tuple[StandingFacts, ...] = (),
    consents: tuple[tuple[Consent, ConsentContext], ...] = (),
) -> PreflightReport:
    """Run the advisory layers over a scenario's inputs. Pure, deterministic, advisory."""
    warnings: list[PreflightWarning] = []

    for t in titles:
        a = assess_title(t)
        if a.reliance is Reliance.DO_NOT_RELY:
            warnings.append(PreflightWarning("ownership", True, a.rationale))
        elif a.reliance is Reliance.RELY_WITH_NOTE:
            warnings.append(PreflightWarning("ownership", False, a.recommendation))

    for s in standings:
        a2 = assess_standing(s)
        if not a2.representable_in_v1:
            warnings.append(PreflightWarning("standing", True, a2.rationale))

    for consent, ctx in consents:
        r = assess_consent_authenticity(consent, ctx)
        if r.severity is Severity.HIGH:
            warnings.append(PreflightWarning("consent-authenticity", False, r.rationale))

    return PreflightReport(tuple(warnings))
