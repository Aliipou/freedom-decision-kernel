# Security Policy

## Scope and status

The Freedom Decision Kernel (FDK) is a research + product codebase: a
deterministic legitimacy/decision layer (`fdk_kernel`) and an experimental
research track (`fdk_research`). The theory content it encodes (the Theory of
Freedom) is a **research artifact**; any comparative claim against RLHF / CAI /
OPA is **unproven** and framed as such in the docs.

This project has **not** had an independent third-party security audit. It ships
formal artifacts (Lean proofs, a TLA+ spec, a Rust parity port), but those cover
specified invariants only — they are not a substitute for a security review of
the full system. Do not treat it as a hardened security boundary without your
own evaluation.

## Supported versions

This is pre-1.0 software. Only the latest commit on the default and active
development branches receives security fixes. There are no long-term-support
branches.

## Reporting a vulnerability

Please report suspected vulnerabilities **privately** — do not open a public
issue for anything exploitable.

- Preferred: open a private report via GitHub Security Advisories
  ("Report a vulnerability" under the repository's **Security** tab).
- Alternatively, email the maintainer: **nikzadpars@gmail.com**.

Please include:

- a description of the issue and the affected component/file,
- reproduction steps or a proof of concept,
- the impact you believe it has, and
- any suggested remediation.

## Disclosure process

- We aim to acknowledge a report within **7 days**.
- We aim to provide an initial assessment (accepted / needs-info / not-a-vuln)
  within **30 days**.
- We follow **coordinated disclosure**: please give us a reasonable window to
  ship a fix before any public disclosure. We will credit reporters who wish to
  be credited.

## No bounty

There is no paid bug-bounty program. Reports are handled on a best-effort basis
by the maintainer.
