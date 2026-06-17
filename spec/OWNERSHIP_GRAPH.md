# Real Ownership Graph — FDK 2.0, Layer 6 (advisory)

> The kernel's single largest hidden assumption: it reads an `OwnershipGraph` as
> *given and correct*. The real world never hands you a correct ownership graph. It
> hands you contested titles, chains that bottom out in conquest, tokens that are not
> the asset, models trained on a billion people's data, estates of the dead, and
> "owners" of rivers and air. **Garbage ownership graph in → garbage verdict out**, no
> matter how sound the kernel — and `spec/FOUNDATIONAL_ATTACKS.md` shows the kernel
> *cannot* relitigate a title's origin (the bootstrapping gap).

This layer does **not** solve ownership. It does the honest, achievable thing: given
the *evidence* about a title, it assesses **how much the kernel may rely on it** and
flags the cases — above all **FORCED origins** — where relying on the graph would
launder an injustice the gate cannot see. Advisory only: no ALLOW/DENY, no mutation,
it never builds or edits an `OwnershipGraph`; it tells a human how much to trust a
title *before* one is constructed. `src/fdk_research/ownership_graph.py`,
`tests/test_ownership_graph.py`; imports nothing into `fdk_kernel`.

## The reliance ladder (`Reliance`)

| Origin / evidence | Reliance | Why |
|---|---|---|
| Cryptographically verifiable + consensual/original | `RELY` | strongest provenance (e.g. an on-chain UTXO) — *caveat:* proves the **token**, not that the token IS the off-chain asset (the NFT problem) |
| Consensual chain (verified links) | `RELY_WITH_NOTE` | usable, but no chain proves its own first link — the origin stays open |
| Original acquisition, no rival | `RELY_WITH_NOTE` | usable, but "what is legitimate first appropriation?" is a theory-author ruling |
| **Forced origin** (theft / conquest) | **`DO_NOT_RELY`** | **bootstrapping gap**: the kernel would protect the holder of stolen title exactly as a clean one |
| Contested / live competing claims | `DO_NOT_RELY` | no single owner to bind a consent to — resolve first |
| Unproven (no chain of title) | `DO_NOT_RELY` | nothing to rely on |

`reliable_for_kernel(claim)` is the one-bit convenience: may the kernel treat this as a
settled owner at all?

## The real-world catalogue (why this layer exists)

- **Bitcoin / on-chain assets** — cryptographic provenance → `RELY`. The strongest
  real-world ownership graph that exists.
- **NFTs** — the token's provenance is verifiable, but the token is usually *not* the
  asset (the JPEG, the deed). `RELY` on the token, with the caveat surfaced.
- **User / collective data** — typically `CONTESTED` (many subjects) → defer to the
  Aggregation layer (`spec/AGGREGATION.md`).
- **AI model weights** — trained on a multitude's data; origin is `CONTESTED` or
  `FORCED` (used without the data-subjects' consent). `DO_NOT_RELY` until resolved.
- **Inheritance / estates** — the prior owner is dead; standing of the dead is a gap
  (`spec/STANDING.md`). The transfer's validity is unsettled here.
- **Intellectual property** — is it property or a monopoly grant over others' actions?
  A `CONTESTED` origin by construction.
- **Conquest-descended land** — `FORCED_ORIGIN`, the bootstrapping gap made concrete.

## Honest scope

v0, uncalibrated: the reliance rule is a transparent decision tree over declared
evidence, not a title-registry or a court. It cannot *verify* a chain of title — it
classifies the evidence it is handed and, crucially, **refuses to let a forced or
contested title pass silently into the kernel**. The real Layer 6 is a research
program (provenance, identity, delegation, inheritance, disputes, jurisdictions); this
scaffold's contribution is to make "the kernel is only as good as the ownership graph"
*operational* — a checkable gate on the graph's own trustworthiness.

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Engineering: Ali Pourrahim.*
