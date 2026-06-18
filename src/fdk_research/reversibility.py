"""
Reversibility index (the apparatus, not a theory) — fdk_research, advisory.

This module exists for ONE purpose: to turn FDK's structural reading of an action
into a *number* so that the only open hypothesis about the whole project can be
TESTED rather than argued. After eleven critical papers (`paper/`), the position
is:

  - H1 "FDK is a new theory of freedom/legitimacy" — collapsed.
  - H2 "FDK is a consent-indexed, computable index of structural reversibility /
    lock-in risk" — alive, but until it *predicts* something the existing
    lock-in literature does not, it is re-description, not theory.

The decisive test is incremental predictive validity (ΔR²) of this index over the
established constructs — **quasi-option value** (Arrow–Fisher–Henry 1974),
**Hirschman** exit (1970), **switching costs**, **path-dependence**. This file is
that test's *apparatus*: a per-action score over the consent/ownership model.

CRITICAL HONESTY (do NOT reify "reversibility"). We do not assume the latent
variable FDK tracks *is* reversibility. The profile is deliberately DECOMPOSED
into separately-measurable components so the empirical work can identify *which*
construct (or composite) actually carries any predictive power — op-irreversibility,
consent-revocability, exit-foreclosure, holder-alignment, recovery cost. "FDK ≈
reversibility" is the current best hypothesis about this index's own meaning, to be
tested, not assumed. The aggregate is a *modeling choice* (the weakest-link / min),
flagged as such — mean vs min vs geometric is itself a tuning question for the data.

Advisory and uncalibrated, like the rest of `fdk_research`; the hard legitimacy
gate never reads it.
"""
from __future__ import annotations

from dataclasses import dataclass

from fdk_kernel import CandidateAction, Op

# How reversible is each operation, intrinsically, in [0, 1] (1 = no lasting state
# change; 0 = cannot be undone). Uncalibrated structural priors, not measurements.
_OP_REVERSIBILITY: dict[Op, float] = {
    Op.READ: 1.0,
    Op.USE: 1.0,
    Op.WRITE: 0.5,       # overwrites, but the prior state is lost unless versioned
    Op.DISCLOSE: 0.0,    # information cannot be un-disclosed
    Op.DELETE: 0.2,      # recoverable only from an external backup
    Op.TRANSFER: 0.2,    # requires the counterparty's consent to reverse
    Op.SPEND: 0.1,       # consumed
    Op.ENCUMBER_EXIT: 0.0,  # the operation whose whole point is to foreclose exit
}


@dataclass(frozen=True)
class ReversibilityProfile:
    """A per-action structural profile, each component in [0, 1] (1 = fully
    reversible / exit preserved). Exposed component-wise on purpose: the empirical
    program regresses these *separately* to find which construct, if any, predicts
    real lock-in beyond existing indices — see module docstring."""

    op_reversibility: float       # weakest-link reversibility of the operations used
    consent_revocability: float   # share of relied-on consents that remain revocable
    exit_preservation: float      # 1.0 unless the action forecloses an exit right
    holder_alignment: float       # share of affected persons who hold the undo power
    recovery: float               # 1 - normalized recovery cost (caller-supplied)
    index: float                  # aggregate (weakest link) — a MODELING CHOICE

    def to_dict(self) -> dict[str, float]:
        return {
            "op_reversibility": self.op_reversibility,
            "consent_revocability": self.consent_revocability,
            "exit_preservation": self.exit_preservation,
            "holder_alignment": self.holder_alignment,
            "recovery": self.recovery,
            "index": self.index,
        }


def _op_reversibility(action: CandidateAction) -> float:
    """Weakest-link op reversibility across the boundaries the action crosses. No
    resources touched ⇒ nothing irreversible ⇒ 1.0."""
    ops = [_OP_REVERSIBILITY.get(op, 0.5) for _resource, op in action.uses()]
    return min(ops) if ops else 1.0


def _consent_revocability(action: CandidateAction) -> float:
    """Share of the action's consents that remain revocable. No consents ⇒ nothing
    to lock in ⇒ 1.0."""
    consents = action.consents
    if not consents:
        return 1.0
    return sum(1.0 for c in consents if c.revocable) / len(consents)


def _exit_preservation(action: CandidateAction) -> float:
    """0.0 if the action removes an exit/revocation right (flag or ENCUMBER_EXIT op),
    else 1.0."""
    if action.removes_exit_right:
        return 0.0
    if any(op is Op.ENCUMBER_EXIT for _resource, op in action.uses()):
        return 0.0
    return 1.0


def _holder_alignment(action: CandidateAction) -> float:
    """Share of affected persons who themselves hold the power to undo the crossing,
    proxied by whether they are a consenting party (a consent they gave, they can
    revoke). No affected persons ⇒ 1.0."""
    affected = [e for e in action.affects if e.is_human()]
    if not affected:
        return 1.0
    consenters = {c.human for c in action.consents}
    return sum(1.0 for e in affected if e in consenters) / len(affected)


def reversibility(action: CandidateAction, *, recovery: float = 1.0) -> ReversibilityProfile:
    """Compute the per-action reversibility profile.

    `recovery` is the one component the model cannot derive (the real-world cost to
    reverse, 1 = costless, 0 = ruinous); the caller supplies it from domain data, and
    it defaults to 1.0 (no recovery cost assumed). The aggregate `index` is the
    weakest link — `min` over the components — because a single irreversible boundary
    crossing makes the whole action irreversible; this aggregation is a documented
    modeling choice, not a result.
    """
    if not 0.0 <= recovery <= 1.0:
        raise ValueError(f"recovery must be in [0, 1], got {recovery}")
    op_rev = _op_reversibility(action)
    consent_rev = _consent_revocability(action)
    exit_pres = _exit_preservation(action)
    holder = _holder_alignment(action)
    index = min(op_rev, consent_rev, exit_pres, holder, recovery)
    return ReversibilityProfile(
        op_reversibility=op_rev,
        consent_revocability=consent_rev,
        exit_preservation=exit_pres,
        holder_alignment=holder,
        recovery=recovery,
        index=index,
    )
