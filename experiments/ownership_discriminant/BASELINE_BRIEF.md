# Brief issued to the baseline policy engineers

This is the **only** material the Cedar and Rego authors received. It deliberately
contains no test cases, no expected verdicts, no mention of what is being measured, and
no vocabulary from the ownership ontology. It describes a system and its available data,
and asks for the policy an engineer would ship.

---

You are a senior authorization engineer. A company is deploying AI agents that call
tools on its behalf, and you own the authorization policy for it. Write the policy you
would actually ship.

## The system

Autonomous agents call tools (read a document, read a mailbox, send an email, export a
dataset, transfer money). Every call passes through a policy decision point before any
effect happens. Your policy decides ALLOW or DENY for each call. Agents are not trusted:
treat any field an agent supplies as attacker-controlled.

The company handles its own internal data and personal data belonging to its customers
and employees. It operates in a jurisdiction with GDPR-style data-protection law.

## The data available to your policy

You may reference any of the following. This is the complete entity model; nothing else
is available at decision time.

**Principals**
- `id`
- `kind` — one of `human`, `machine`, `org`
- `owner` — for a machine, the principal it belongs to (may itself be a machine)
- `acts_for` — for a human, the organisations they are authorised to act on behalf of

**Resources**
- `id`
- `owner` — the principal that owns it. For personal data this is the data subject
  (the customer or employee the data is about), not the company holding it.
- `custodian` — the principal that physically stores and administers it
- `labels` — e.g. `customer_pii`, `internal`, `public`
- `exportable_beyond_recall` — true when sending this resource to a destination means it
  can no longer be corrected, returned or deleted on request

**Grants** (the IAM table)
- `actor`, `capability`, `resource`, `issuer` — who wrote the grant

**Consents**
- `subject`, `resource`, `purposes` (list), `revoked` (boolean)

**Contracts**
- `subject`, `counterparty`, `resource`, `necessary_purposes` — purposes necessary to
  perform an existing relationship between the subject and the counterparty

**Delegations**
- `(owner, to, resource)` — an owner delegating a resource down to a principal

**Purpose bindings** — `label -> allowed purposes`

**The request** — `actor`, `capability`, `resource`, `purpose`

## What to produce

The policy set you would ship for this system, in your language, with a short comment on
each rule saying what it protects against. Aim for rules that generalise, rather than
rules naming specific principals or resources — you will not know in advance which
customer or which agent is involved.

Assume a competent adversary who controls the agents.
