"""Three gates over one corpus, to find out whether ownership-derived legitimacy
decides anything that standard agent authorization does not.

The question this experiment exists to answer is narrow and falsifiable:

    Given the SAME action and the SAME facts, does a gate that derives its
    predicates from an ownership/consent model ever reach a different verdict
    from (a) capability/grant-chain authorization and (b) purpose binding — and
    when it does, is it RIGHT?

A divergence only counts if the ownership gate's verdict matches an independently
stated ground truth. A divergence in which the ownership gate is wrong counts
AGAINST it, and this module reports both directions. If the ownership gate never
diverges, the theory adds justification but not behaviour, and that is a negative
result worth publishing.

Nothing here is a claim about frequency. A synthetic corpus can demonstrate that a
class of case EXISTS; it cannot say how often it occurs in production.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Verdict(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"


# ---------------------------------------------------------------------------
# The world model. Deliberately the shape of an enterprise data catalogue plus an
# IAM grant table — not a philosophical registry. Everything here is something a
# GDPR Art.30 record of processing already obliges an organisation to maintain.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Resource:
    id: str
    #: who OWNS it. For personal data this is the data subject, not the holder.
    owner: str
    #: who physically holds/administers it (often != owner)
    custodian: str
    labels: tuple[str, ...] = ()
    #: an action is irreversible for the owner if it cannot later be undone by them
    exportable_beyond_recall: bool = False


@dataclass(frozen=True)
class Grant:
    """One IAM grant. `issuer` is whoever wrote it — usually an admin."""

    actor: str
    capability: str
    resource: str
    issuer: str


@dataclass(frozen=True)
class Contract:
    """A standing relationship between the owner and a counterparty.

    DERIVED, not bolted on: axiom 3 lists a person's property rights as "the body,
    time, labor, mind, data, consent, legitimate property, CONTRACTS, and the right
    of exit". Contract is therefore already a ground on which a counterparty may act
    within the relationship the owner entered. It is not a second kind of consent —
    it is a different property right the owner exercised. It was missing from the
    ENCODING, not from the theory.
    """

    subject: str
    counterparty: str
    resource: str
    #: purposes NECESSARY to perform the relationship. Not a blank cheque: anything
    #: outside this set falls back to needing consent.
    necessary_purposes: tuple[str, ...] = ()


@dataclass(frozen=True)
class Necessity:
    """An imminent harm that acting prevents.

    HONEST LABEL: an EXTENSION, not a derivation. The book has no emergency or
    necessity exception, and that absence is deliberate and documented. Adding it
    CHANGES the theory rather than implementing it, so it is kept as a separate,
    explicitly flagged basis that can be switched off to recover the book's own
    stricter behaviour.
    """

    resource: str
    purposes: tuple[str, ...]
    justification: str


@dataclass(frozen=True)
class Consent:
    subject: str
    resource: str
    purposes: tuple[str, ...]
    revoked: bool = False


@dataclass(frozen=True)
class Principal:
    id: str
    kind: str  # "human" | "machine" | "org"
    owner: str | None = None  # for machines: the human owner
    #: organisations this human is authorised to act for. Agency/representation is
    #: part of any rights ontology (a director acts for the company), and omitting
    #: it was a defect in this MODEL, not a finding about the theory: without it
    #: every ordinary corporate action fails for the wrong reason.
    acts_for: tuple[str, ...] = ()


@dataclass
class World:
    principals: dict[str, Principal] = field(default_factory=dict)
    resources: dict[str, Resource] = field(default_factory=dict)
    grants: list[Grant] = field(default_factory=list)
    consents: list[Consent] = field(default_factory=list)
    contracts: list[Contract] = field(default_factory=list)
    necessities: list[Necessity] = field(default_factory=list)
    #: delegations an owner makes DOWN to a person (employment is exactly this).
    #: The person's machine then inherits that scope — bounded, never widened.
    #: Derived from axiom 7 (explicit delegation by the owner).
    delegations: list[tuple[str, str, str]] = field(default_factory=list)
    #: policy table for the purpose-binding baseline: label -> allowed purposes
    purpose_bindings: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def root_human(self, actor: str) -> str | None:
        """Walk machine->owner until a human, or None if the chain does not end
        in one (cycle or ownerless machine)."""
        seen: set[str] = set()
        cur = actor
        while cur and cur not in seen:
            seen.add(cur)
            p = self.principals.get(cur)
            if p is None:
                return None
            if p.kind == "human":
                return p.id
            cur = p.owner or ""
        return None

    def owns(self, principal: str, resource_id: str) -> bool:
        r = self.resources.get(resource_id)
        return bool(r and r.owner == principal)

    def may_delegate(self, principal: str, resource_id: str) -> bool:
        """Owns it outright, or lawfully acts for the entity that owns it."""
        if self.owns(principal, resource_id):
            return True
        r = self.resources.get(resource_id)
        p = self.principals.get(principal)
        return bool(r and p and r.owner in p.acts_for)

    def delegated_to(self, principal: str, resource_id: str) -> bool:
        r = self.resources.get(resource_id)
        return bool(
            r
            and any(
                d[0] == r.owner and d[1] == principal and d[2] == resource_id
                for d in self.delegations
            )
        )

    def basis_for(self, subject: str, resource: str, purpose: str) -> tuple[bool, str]:
        """Is there ANY ground on which this may proceed without fresh consent?

        The single most consequential finding of this experiment: the first encoding
        recognised only ONE ground — the owner's explicit consent — and two blind
        auditors caught the error immediately. Consent is one basis among several.
        """
        c = self.consent_for(subject, resource, purpose)
        if c is not None:
            return (False, "the owner's consent was revoked") if c.revoked else (True, "consent")
        for k in self.contracts:
            if k.subject == subject and k.resource == resource and purpose in k.necessary_purposes:
                return True, f"contract with {k.counterparty}: purpose is necessary to perform it"
        for n in self.necessities:
            if n.resource == resource and purpose in n.purposes:
                return True, f"necessity [EXTENSION beyond the book]: {n.justification}"
        return False, "no consent, contract or necessity covers this purpose"

    def consent_for(self, subject: str, resource: str, purpose: str) -> Consent | None:
        for c in self.consents:
            if c.subject == subject and c.resource == resource and purpose in c.purposes:
                return c
        return None


@dataclass(frozen=True)
class Action:
    actor: str
    capability: str
    resource: str
    purpose: str
    #: does performing it remove the owner's ability to revoke/undo later?
    destroys_exit: bool = False


# ---------------------------------------------------------------------------
# Gate A — capability / grant-chain authorization.
# What Cedar, OPA, Biscuit, and the MIT authenticated-delegation scheme decide:
# is there a valid grant for this actor on this resource, and does the actor's
# delegation chain root in a human? It does NOT ask whether the grant's ISSUER
# had the right to issue it.
# ---------------------------------------------------------------------------


def gate_authz(w: World, a: Action) -> tuple[Verdict, str]:
    if w.root_human(a.actor) is None:
        return Verdict.DENY, "delegation chain does not root in a human principal"
    for g in w.grants:
        if g.actor == a.actor and g.capability == a.capability and g.resource == a.resource:
            return Verdict.ALLOW, f"grant from {g.issuer}"
    return Verdict.DENY, "no grant"


# ---------------------------------------------------------------------------
# Gate B — purpose binding.
# What DLP / consent-management platforms and AuthGate's own purpose layer add:
# the data's label must permit the action's purpose. Still policy-authored.
# ---------------------------------------------------------------------------


def gate_purpose(w: World, a: Action) -> tuple[Verdict, str]:
    v, why = gate_authz(w, a)
    if v is Verdict.DENY:
        return v, why
    r = w.resources[a.resource]
    for label in r.labels:
        allowed = w.purpose_bindings.get(label)
        if allowed is None:
            return Verdict.DENY, f"unknown label '{label}' -> default deny"
        if a.purpose not in allowed:
            return Verdict.DENY, f"purpose '{a.purpose}' not permitted for '{label}'"
    return Verdict.ALLOW, "grant + purpose binding satisfied"


# ---------------------------------------------------------------------------
# Gate C — ownership-derived legitimacy.
# Every predicate below is DERIVED from an axiom of the theory, not hand-authored:
#   ax4  Machine(m) -> exists h. HumanOwner(h,m)
#   ax5  MachineScope(m) subseteq PropertyScope(owner(m))
#   ax7  DelegatedProperty(m,r) requires owner(m) OWNS r and explicit delegation
#   ax3  property rights include data, consent, and the RIGHT OF EXIT
# ---------------------------------------------------------------------------


def gate_ownership(w: World, a: Action) -> tuple[Verdict, str]:
    # ax4 — an ownerless machine is illegitimate per se.
    root = w.root_human(a.actor)
    if root is None:
        return Verdict.DENY, "ax4: no human owner at the root of the chain"

    r = w.resources.get(a.resource)
    if r is None:
        return Verdict.DENY, "resource not in the ownership graph"

    grant = next(
        (
            g
            for g in w.grants
            if g.actor == a.actor and g.capability == a.capability and g.resource == a.resource
        ),
        None,
    )
    if grant is None:
        return Verdict.DENY, "no delegation"

    # ax7 — the ISSUER must actually own what it delegated. This is the step no
    # baseline performs: a valid grant from someone who did not own the resource
    # is not a delegation, it is an assertion.
    if not w.may_delegate(grant.issuer, a.resource):
        # ...unless the true owner consented for this purpose. Consent IS the
        # owner's own act of delegation (ax3: consent is a property right).
        ok, why = w.basis_for(r.owner, a.resource, a.purpose)
        if not ok:
            return Verdict.DENY, (
                f"ax7: issuer '{grant.issuer}' does not own '{a.resource}' "
                f"(owner is '{r.owner}') and {why}"
            )

    # ax5 — a machine's scope cannot exceed its human owner's property scope.
    if root != r.owner and not w.may_delegate(root, a.resource):
        if not w.delegated_to(root, a.resource):
            ok, why = w.basis_for(r.owner, a.resource, a.purpose)
            if not ok:
                return Verdict.DENY, (
                    f"ax5: scope of machine rooted in '{root}' exceeds that human's "
                    f"property (resource owned by '{r.owner}') and {why}"
                )

    # ax3 — the right of exit is itself owned; an action that destroys the owner's
    # ability to revoke later cannot be authorized by a consent given earlier.
    if a.destroys_exit and r.owner != root:
        return Verdict.DENY, "ax3: action destroys the owner's right of exit"

    return Verdict.ALLOW, "ownership, delegation and consent all check out"


GATES = {
    "authz(grant-chain)": gate_authz,
    "purpose-binding": gate_purpose,
    "ownership-derived": gate_ownership,
}
