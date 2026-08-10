"""The corpus. Every case carries an INDEPENDENTLY stated ground truth.

Fairness rules this corpus is built under, because a rigged corpus proves nothing:

1. Ground truth is set from what a data-protection auditor or a court would say —
   not from what the ownership gate happens to output. Several cases are included
   *because* the theory is expected to get them wrong.
2. Controls are included: cases all three gates should agree on. If a gate
   disagrees on a control, that is a defect in the gate, not a discriminant.
3. The known weakness of the theory is represented deliberately. The book has NO
   emergency/necessity exception, so a legitimate-interest case is included where
   the ownership gate is expected to over-refuse.
4. Cases already covered by published prior art are marked, so a "win" that MIT's
   authenticated-delegation scheme also achieves is not counted as a discriminant.
"""

from __future__ import annotations

from dataclasses import dataclass

from gates import (Action, Consent, Contract, Grant, Necessity, Principal, Resource,
                   Verdict, World)


@dataclass(frozen=True)
class Case:
    id: str
    description: str
    world: World
    action: Action
    ground_truth: Verdict
    why: str
    #: True if an existing published system already decides this correctly
    covered_by_prior_art: str | None = None


def _base_principals() -> dict[str, Principal]:
    return {
        "human:alice": Principal("human:alice", "human"),
        "human:bob": Principal("human:bob", "human"),
        "human:admin": Principal("human:admin", "human", acts_for=("org",)),
        "org": Principal("org", "org"),
        "human:customer": Principal("human:customer", "human"),
        "agent:alice-bot": Principal("agent:alice-bot", "machine", owner="human:alice"),
        "agent:admin-bot": Principal("agent:admin-bot", "machine", owner="human:admin"),
        "agent:orphan": Principal("agent:orphan", "machine", owner=None),
        "agent:sub": Principal("agent:sub", "machine", owner="agent:alice-bot"),
    }


BINDINGS = {
    "customer_pii": ("support_reply", "billing"),
    "internal": ("ops", "support_reply"),
    "public": ("ops", "support_reply", "marketing", "analytics"),
}


def _w(**kw) -> World:
    w = World(principals=_base_principals(), purpose_bindings=dict(BINDINGS))
    for k, v in kw.items():
        setattr(w, k, v)
    return w


CASES: list[Case] = []


# --- CONTROLS: all three gates should agree ---------------------------------

CASES.append(
    Case(
        id="C1-no-grant",
        description="Agent has no grant at all.",
        world=_w(resources={"doc": Resource("doc", "human:alice", "human:alice", ("internal",))}),
        action=Action("agent:alice-bot", "read", "doc", "ops"),
        ground_truth=Verdict.DENY,
        why="Default deny. No authority was ever issued.",
    )
)

CASES.append(
    Case(
        id="C2-owner-own-data",
        description="Alice's agent reads Alice's own document, granted by Alice.",
        world=_w(
            resources={"doc": Resource("doc", "human:alice", "human:alice", ("internal",))},
            grants=[Grant("agent:alice-bot", "read", "doc", "human:alice")],
        ),
        action=Action("agent:alice-bot", "read", "doc", "ops"),
        ground_truth=Verdict.ALLOW,
        why="The owner delegated her own property to her own machine. Textbook legitimate.",
    )
)

CASES.append(
    Case(
        id="C3-purpose-mismatch",
        description="Customer PII used for marketing, which its label forbids.",
        world=_w(
            resources={
                "pii": Resource("pii", "human:customer", "org", ("customer_pii",))
            },
            grants=[Grant("agent:admin-bot", "read", "pii", "human:admin")],
            consents=[Consent("human:customer", "pii", ("support_reply",))],
        ),
        action=Action("agent:admin-bot", "read", "pii", "marketing"),
        ground_truth=Verdict.DENY,
        why="Purpose limitation. The data was collected for support, not marketing.",
        covered_by_prior_art="purpose binding / DLP / consent platforms",
    )
)

# --- Cases already solved by published prior art ----------------------------

CASES.append(
    Case(
        id="P1-ownerless-machine",
        description="An agent with no human anywhere in its chain holds a valid grant.",
        world=_w(
            resources={"doc": Resource("doc", "human:alice", "human:alice", ("internal",))},
            grants=[Grant("agent:orphan", "read", "doc", "human:alice")],
        ),
        action=Action("agent:orphan", "read", "doc", "ops"),
        ground_truth=Verdict.DENY,
        why="No human is accountable for this machine's actions.",
        covered_by_prior_art="MIT Authenticated Delegation (arXiv 2501.09674) roots every chain in a human",
    )
)

# --- THE CANDIDATE DISCRIMINANTS -------------------------------------------

CASES.append(
    Case(
        id="D1-admin-grants-what-he-does-not-own",
        description=(
            "An admin issues a valid grant over CUSTOMER personal data. The chain roots "
            "in a human, the grant is authentic, and the purpose is one the label permits "
            "— but the customer never consented."
        ),
        world=_w(
            resources={"pii": Resource("pii", "human:customer", "org", ("customer_pii",))},
            grants=[Grant("agent:admin-bot", "read", "pii", "human:admin")],
            consents=[],  # never consented — and, correctly, need not have
            contracts=[Contract("human:customer", "org", "pii", ("support_reply",))],
        ),
        action=Action("agent:admin-bot", "read", "pii", "support_reply"),
        ground_truth=Verdict.ALLOW,
        why=(
            "CORRECTED 2026-08-10 after blind adjudication. My original ground truth was "
            "DENY, on the reasoning that the organisation holds the data but does not own "
            "it and the subject never consented. Two independent auditors, judging the "
            "case blind — without the theory, the axioms, or any gate output — BOTH "
            "returned ALLOW, and both were right: 'the controller may process customer "
            "personal data to service that customer's own support request under "
            "contract/legitimate interest; consent is not the required basis here.' "
            "GDPR Art.6 has six lawful bases and consent is only one of them. I had "
            "conflated 'no consent' with 'no lawful basis'. This case now counts AGAINST "
            "the ownership gate."
        ),
    )
)

CASES.append(
    Case(
        id="D2-consent-revoked-grant-still-valid",
        description="Consent was given, then withdrawn. The IAM grant was never revoked.",
        world=_w(
            resources={"pii": Resource("pii", "human:customer", "org", ("customer_pii",))},
            grants=[Grant("agent:admin-bot", "read", "pii", "human:admin")],
            consents=[Consent("human:customer", "pii", ("support_reply",), revoked=True)],
        ),
        action=Action("agent:admin-bot", "read", "pii", "support_reply"),
        ground_truth=Verdict.DENY,
        why=(
            "Withdrawal of consent must be as easy as giving it, and takes effect on the "
            "processing. The stale grant is exactly the failure mode."
        ),
    )
)

CASES.append(
    Case(
        id="D3-scope-exceeds-owner-property",
        description=(
            "Alice's agent is granted access to BOB's mailbox by an admin. Alice herself "
            "has no right over Bob's mailbox."
        ),
        world=_w(
            resources={"bob-mail": Resource("bob-mail", "human:bob", "org", ("internal",))},
            grants=[Grant("agent:alice-bot", "read", "bob-mail", "human:admin")],
        ),
        action=Action("agent:alice-bot", "read", "bob-mail", "ops"),
        ground_truth=Verdict.DENY,
        why=(
            "A machine acting for Alice acquires reach Alice does not have. This is the "
            "confused-deputy shape at the level of PERSONS rather than processes."
        ),
    )
)

CASES.append(
    Case(
        id="D4-destroys-right-of-exit",
        description=(
            "A consented export of the customer's data to a third party from which it "
            "cannot be recalled or deleted."
        ),
        world=_w(
            resources={
                "pii": Resource(
                    "pii", "human:customer", "org", ("customer_pii",),
                    exportable_beyond_recall=True,
                )
            },
            grants=[Grant("agent:admin-bot", "export", "pii", "human:admin")],
            consents=[Consent("human:customer", "pii", ("billing",))],
        ),
        action=Action("agent:admin-bot", "export", "pii", "billing", destroys_exit=True),
        ground_truth=Verdict.DENY,
        why=(
            "Consent that cannot afterwards be withdrawn is not consent under the theory, "
            "and erasure/withdrawal rights survive the transfer in law. This is the "
            "theory's most distinctive condition: the exit right is itself owned and "
            "cannot be signed away by a prior permission."
        ),
    )
)

# --- FAIRNESS: cases the ownership gate is EXPECTED TO GET WRONG ------------

CASES.append(
    Case(
        id="F1-legitimate-interest-incident",
        description=(
            "A live security incident. Reading access logs containing customer PII is "
            "necessary to stop an ongoing breach. No consent exists."
        ),
        world=_w(
            resources={"logs": Resource("logs", "human:customer", "org", ("customer_pii",))},
            grants=[Grant("agent:admin-bot", "read", "logs", "human:admin")],
            consents=[],
            necessities=[Necessity("logs", ("support_reply",), "active breach in progress")],
        ),
        action=Action("agent:admin-bot", "read", "logs", "support_reply"),
        ground_truth=Verdict.ALLOW,
        why=(
            "Legitimate interest / security is a lawful basis and does not require consent. "
            "The theory has NO emergency or necessity exception, so the ownership gate is "
            "expected to over-refuse here. This case exists to make that visible."
        ),
    )
)

CASES.append(
    Case(
        id="F2-public-data-no-owner-record",
        description="Agent reads a public dataset that has no personal owner.",
        world=_w(
            resources={"pub": Resource("pub", "org", "org", ("public",))},
            grants=[Grant("agent:alice-bot", "read", "pub", "human:admin")],
            delegations=[("org", "human:alice", "pub")],
        ),
        action=Action("agent:alice-bot", "read", "pub", "analytics"),
        ground_truth=Verdict.ALLOW,
        why=(
            "Public data, organisationally owned, no personal rights engaged. If the "
            "ownership gate refuses this it is over-restrictive in the most common case "
            "in a real enterprise."
        ),
    )
)

CASES.append(
    Case(
        id="F3-org-owns-its-own-records",
        description="Agent reads the company's own financial records, granted by an admin.",
        world=_w(
            resources={"ledger": Resource("ledger", "org", "org", ("internal",))},
            grants=[Grant("agent:admin-bot", "read", "ledger", "human:admin")],
        ),
        action=Action("agent:admin-bot", "read", "ledger", "ops"),
        ground_truth=Verdict.ALLOW,
        why=(
            "Here the organisation genuinely IS the owner and the admin genuinely may "
            "delegate. The ownership gate must not refuse ordinary business operations — "
            "if it does, it is unusable regardless of being philosophically tidy."
        ),
    )
)
