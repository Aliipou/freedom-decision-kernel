# Project status — final disposition (2026-06-20)

A deliberate closure, not an abandonment. After an extended adversarial process (red-team,
killer test, orthogonality test, Stage-1 discriminant analysis, residual decomposition), the
returns on the *theory* are flat. This file records where each part of the project stands and
what should — and should not — be reopened.

## FDK as a theory of freedom — **CLOSED** (negative result published)

The claim that FDK is a new theory of freedom / consent / legitimacy did **not** survive its
own attacks. It reduces to, or is silent where, Nozick / Pettit / Sen, and the surviving
"reversibility" idea is — on the evidence — a **reparameterization of the existing lock-in
literature** (≈ switching cost; residual small and indistinguishable from collinearity/noise).
The full negative result is published in [`paper/README.md`](paper/README.md) (12 critical
papers) and the empirics in [`data/RED_TEAM.md`](data/RED_TEAM.md).

**Do not reopen** (diminishing returns, already exhausted): proving "freedom = property,"
hunting a new philosophical construct, re-fighting Pettit/Sen/Nozick, or writing more papers to
rescue the theory. That contest is over, and closing it was the right call.

## FDK research layer — **FINISHED**

`src/fdk_kernel/` + `src/fdk_research/` are complete as an artifact (frozen kernel, four-checker
verification, 100% coverage). No further research expansion is planned. The repository is kept
as an **engineering + honest-research showcase** — see [`ENGINEERING.md`](ENGINEERING.md).

## Lock-in Analytics tool — **BUILT, then FROZEN pending real data**

The deployable tool exists: `lockin-scan` (CLI + CI gate), `fdk_research.lockin` /
`reversibility`, `POSITIONING.md`. It turns a known cost into a visible, gateable number — the
SonarQube model, no new science claimed. **It is frozen here** because the only thing that can
advance it is *real data*, not more code:

- the validation questions (does the score predict migration pain — **Q-A**; does it improve a
  CIO's decision — **Q-B**) need **100+ real migration episodes** with measured outcomes;
- the real moat is a **maintained portability knowledge base**, not the algorithm (the bundled
  one is an LLM seed).

Resume only with real migration data or a design partner. Absent those, leave frozen.

## AuthGate — **the one OPEN thread**

This is the part worth keeping alive. The decisive question is narrow and answerable:

> **Where do OPA / Cedar / Zanzibar / ABAC fail, but legitimacy-before-authorization
> (AuthGate) succeeds?** Find **three real scenarios** where an *authorized-but-illegitimate*
> agent action is caught by the legitimacy layer and waved through by a pure authorization
> stack. If those three exist and are compelling, there is a real product.

(See `freedom-kernel-work` for AuthGate, and the FDK↔AuthGate seam already built there.)

## Energy allocation (the honest recommendation)

~80% on backend / cloud / distributed systems / **AuthGate** — where the demonstrated
competitive advantage is *systems and engineering*, not political philosophy. ~20% on
**Lock-in Analytics**, and only to the point of collecting real data. Work on what a customer
or an employer will pay for today.

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Engineering: Ali Pourrahim. The negative result is a result; the repository stands as evidence
of how it was reached.*
