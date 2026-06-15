"""
Typed error hierarchy for the Freedom Decision Kernel.

A *decision* kernel must fail loud on malformed input rather than silently
mis-decide: a bad ownership graph or a malformed candidate is a programming /
integration error, not a "deny". All such conditions raise a subclass of
``FDKError`` so callers can catch the whole family with one ``except``.

These are input-validation errors. They are distinct from a *legitimate* "deny"
(an action that is well-formed but impermissible) — that is a normal Decision
outcome, never an exception.
"""
from __future__ import annotations


class FDKError(Exception):
    """Base class for every Freedom Decision Kernel error."""


class InvalidEntity(FDKError):
    """An Entity is malformed (e.g. empty name)."""


class InvalidResource(FDKError):
    """A Resource is malformed (e.g. empty name)."""


class InvalidConsent(FDKError):
    """A Consent record is malformed (e.g. empty action_id)."""


class InvalidCandidateAction(FDKError):
    """A CandidateAction is malformed (e.g. empty action_id)."""


class InvalidOwnershipGraph(FDKError):
    """The ownership graph is internally inconsistent (e.g. a machine that owns
    itself, or a delegation/ownership entry that contradicts the agent kinds)."""


class InvalidDecisionInput(FDKError):
    """The inputs to ``decide`` are unusable (e.g. duplicate candidate action_ids,
    which would make the ranked output ambiguous)."""


class InvalidClaim(FDKError):
    """A Claim is malformed (e.g. bad basis or negative ordinal time)."""


class InvalidObligation(FDKError):
    """An Obligation is malformed (e.g. empty description)."""


class InvalidContract(FDKError):
    """A Contract is malformed (e.g. fewer than two parties)."""


class InvalidConflict(FDKError):
    """A Conflict is malformed (e.g. the two claims are not over the same resource)."""
