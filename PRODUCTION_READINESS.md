# Production readiness — FDK as a policy/consent engine for AI agents

> **Read this as the product contract, not the philosophy.** FDK has two tracks,
> and the single most expensive mistake is to conflate them:
>
> | Track | Claim | Status |
> |---|---|---|
> | **Product** (this doc) | A fail-closed *legitimacy/consent policy engine* that sits between an agent planner and AuthGate and returns ALLOW / DENY / DEFER. | **Usable now for in-frame agent actions.** |
> | **Philosophy** ([`spec/RESEARCH_AGENDA.md`](spec/RESEARCH_AGENDA.md)) | A new paradigm of legitimacy rivalling Rawls / Hayek / Nozick / Ostrom. | **Early-stage; "consistent but incomplete."** Four open frontiers. |
>
> A policy engine for SaaS / agentic / enterprise actions does **not** need the
> open philosophical frontiers (children, animals, future generations, original
> acquisition, fully-modelled authentic consent) solved — those cases are out of
> its operating envelope. The theory can mature in the background while the
> product ships against a concrete, buyable problem: *stopping an AI agent from
> doing something it has no consent to do.*

---

## Where it fits

```
User goal
   │
Planner / LLM ── proposes a candidate action ──┐
   │                                           ▼
   │                          fdk_runtime.PolicyEngine.evaluate
   │                            ├─ legitimacy gate   (fdk_kernel, frozen, formally checked)
   │                            ├─ authority check   (AuthGate, optional)
   │                            └─ audit sink        (your log / SIEM, optional)
   │                                           │
   │                          ALLOW ───────────┤
   │                          DEFER ──► human  │
   │                          DENY  ──► blocked │
   ▼                                           ▼
 (execute only on ALLOW)                  AuthGate enforces (capabilities, signatures)
```

FDK answers the **prior** question — *should this happen at all?* (legitimacy) —
before AuthGate answers *does this agent hold authority?* An action can be fully
authorized yet illegitimate (selling a user's data you were granted access to);
FDK rejects it before AuthGate is consulted.

## The verdict contract

| Verdict | Meaning | Executor action |
|---|---|---|
| `ALLOW` | Legitimate (and authorized, if an authority oracle is wired). | Proceed. |
| `DENY`  | Illegitimate, unauthorized, **or any error** (fail-closed). | Block. |
| `DEFER` | Legitimate but flagged for a human (e.g. irreversible op). | Ask a human. |

Branch only on `decision.allowed` (true **only** for `ALLOW`). Every decision is
a serializable `PolicyDecision` (`to_dict()` / `to_json()`) carrying the verdict,
reasons, resources touched, authority result, the FDK + freeze versions, and a
timestamp — ready for a log line or a SIEM event.

## The cardinal guarantee: fail-closed

The engine **never fails open.** Every one of these yields `DENY`, never `ALLOW`:

- malformed / inconsistent ownership graph (`graph.validate()` raises),
- any exception inside the legitimacy gate,
- an authority oracle that raises (backend down),
- an **audit sink that raises** — an un-auditable decision is not safe to allow,
- an unparseable wire request (the sidecar returns a `DENY` body, not a 500).

There is no code path that returns `ALLOW` from an exception handler.
`tests/test_runtime_engine.py` pins this; it is the property to protect above all.

## Quickstart (library)

```python
from fdk_kernel import AgentType, BoundaryKind, CandidateAction, Entity, Op, OwnershipGraph, Resource
from fdk_runtime import PolicyEngine, Verdict, high_stakes_defer

engine = PolicyEngine(defer_policy=high_stakes_defer)   # + authority=..., audit_sink=...

alice  = Entity("alice", AgentType.HUMAN)
agent  = Entity("agent-7", AgentType.MACHINE)
db     = Resource("customers", BoundaryKind.DATA, subject=alice)
graph  = OwnershipGraph(human_owns={alice: {db}}, machine_owner={agent: alice},
                        delegated={agent: {(db, Op.DELETE)}})

action = CandidateAction("del-1", actor=agent, resources_used=((db, Op.DELETE),), affects=(alice,))
decision = engine.evaluate(action, graph)

assert decision.verdict is Verdict.DENY     # no consent from alice → blocked
print(decision.to_json())
```

Add alice's valid, operation-specific consent and the same call returns `DEFER`
(legitimate, but DELETE is irreversible — confirm with a human); drop the
`defer_policy` and it returns `ALLOW`.

## Quickstart (HTTP sidecar)

```python
from fdk_runtime import PolicyEngine, serve
serve(PolicyEngine(), host="127.0.0.1", port=8099)   # POST /v1/decide, GET /healthz
```

`POST /v1/decide` with the request JSON (schema in `fdk_runtime/codec.py`) returns
the decision JSON. The reference server is stdlib-only and single-threaded — in
production put the pure `fdk_runtime.handle_decide(engine, body)` behind a real
ASGI/WSGI server with **TLS, endpoint auth, and rate limiting**. The decision
logic is identical; only the transport changes.

## Readiness checklist

| Area | State | Notes |
|---|---|---|
| Deterministic decision core | ✅ Ready | Frozen kernel; Lean/TLC/Rust/Hypothesis-checked. |
| Three-valued verdict + reasons | ✅ Ready | ALLOW/DENY/DEFER, serializable record. |
| Fail-closed on every error path | ✅ Ready | Pinned by tests. |
| AuthGate seam | ✅ Ready (interface) | Pluggable oracle; ships with an in-memory bridge. |
| Audit/observability | ✅ Ready (hook) | `audit_sink` + `to_dict`. **Not** tamper-evident — see trust boundary. |
| Wire codec + reference sidecar | ✅ Ready | Stdlib-only; front with a real server. |
| Typing / lint / packaging | ✅ Ready | mypy `--strict`, ruff, installable wheel. |
| Real cryptographic enforcement | ⛔ Out of scope | By design — AuthGate's job, downstream. |
| Signed, hash-chained audit log | 🔲 Not yet | The sink is a hook; wire it to your tamper-evident store. |
| Throughput / latency benchmark | 🔲 Not yet | Pure in-process Python, no I/O in the gate; numbers TBD. |
| Published JSON schema + SDKs | 🔲 Not yet | Codec is the de-facto schema; not yet a versioned contract. |

## In-scope vs. out-of-scope (be honest with buyers)

**In scope (works today):** actions by/affecting *competent, living, consenting
principals* — the bulk of SaaS, agentic-AI, and enterprise tool calls: read/write/
delete/transfer/spend over data, money, compute, and tangible resources, with
consent, delegation, and an aggressor/defender exception.

**Out of scope (do not claim):** the four open frontiers
([`spec/frontiers/`](spec/frontiers/)) — **Standing** (children, the incapacitated,
animals, future people), **Aggregation** (the commons), **Consent-Authenticity**
(manufactured vs. real consent), **Original Acquisition** (legitimacy of root
title). If your use case turns on any of these, FDK gives a *bounded* answer or
should `DEFER`, and you must not present its verdict as settled. Most agent-
authorization use cases never touch them.

## Trust boundary / threat model

- **TCB = `fdk_kernel`** (frozen, mechanically pinned, four-checker verified). The
  `fdk_runtime` layer orchestrates; it adds no axioms and imports no research.
- **FDK contains no cryptography by design.** It *decides*; AuthGate *enforces*
  (capability proofs, signature verification, scope). A `DENY` is advisory until
  AuthGate refuses to execute. Deploy FDK in front of an enforcement layer you
  trust — never as the only thing between an agent and an effector.
- **The audit sink is observability, not evidence.** For a tamper-evident record,
  forward `PolicyDecision.to_dict()` into a signed/append-only store (AuthGate's
  crypto, or your SIEM's WORM bucket).
- **Inputs are untrusted.** The ownership graph and consents come from your
  control plane; FDK's verdict is only as sound as that input (the
  Ownership-Genesis frontier: FDK audits transfers, not the *origin* of title).

## What would raise the readiness bar next

1. A real AuthGate integration (replace the in-memory bridge with the verified kernel).
2. A signed, hash-chained audit adapter behind `audit_sink`.
3. A throughput/latency benchmark and a concurrency story for the sidecar.
4. A versioned, published JSON schema for the wire codec + thin client SDKs.

*Engineering: Ali Pourrahim. Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali
Jannat Khah Doust (CC BY 4.0). The product track is deliberately separate from the
research track; see [`spec/RESEARCH_AGENDA.md`](spec/RESEARCH_AGENDA.md).*
