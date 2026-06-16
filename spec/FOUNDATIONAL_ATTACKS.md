# Foundational attacks — breaking the primitive, not a scenario

> The deepest red-team. The brutal suite and the adversary panel attack the gate
> with *cases*; this document attacks the *coherence of the primitive itself*:
> `Legitimate(action) ⟺ every boundary crossed has the owner's valid consent`. These
> are the objections a hostile philosopher of law or an analytic metaethicist raises
> first. Two resolve in FDK's favour; two are **genuine, load-bearing limits** that
> are documented here, not hidden — and one of them is the project's single biggest
> risk (the ownership model). Companion executable demo:
> `examples/foundational_attacks.py` (gated by `tests/test_foundational_attacks.py`).

Status: **HELD** (the objection fails) · **GENUINE LIMIT** (real, documented, open).

---

## 1. The bootstrapping / original-acquisition problem — **GENUINE LIMIT**

**Attack.** FDK reads an `OwnershipGraph` as a given input. Nothing in the kernel
legitimizes the graph's *origin*. So a holder whose title descends from a 200-year-
old violent conquest is protected exactly as one whose title is clean; the
dispossessed heir who tries to reclaim is denied as a confiscator. The gate is
"only as good as the ownership graph" — and this is precisely how good: it launders
any injustice that predates the recorded graph.

**Reproduced** (`examples/foundational_attacks.py`): for a contested estate the
current holder *may sell* (ALLOW) and the dispossessed heir *may not reclaim*
(DENY) — and the verdict is identical whether the title is just or stolen, because
provenance is not representable.

**Cross-model (the honest part).** This is **not FDK-specific**. Run the same case
through every kernel: all six let the holder sell; FDK / Rawlsian / Deontological
deny the reclaim while Utilitarian / ConstitutionalAI / RLHF allow it — but *not one*
reasons about the title's origin. The bootstrapping gap is a property of the entire
**input-graph decision-kernel paradigm**, not a flaw unique to FDK. FDK is not worse
here; none of them can be better without a provenance axiom.

**Resolution options (open, needs a theory-author ruling).** (a) Add a Lockean
original-acquisition axiom + a provenance/chain-of-title field to the model so the
graph's history is itself subject to the gate; or (b) rule explicitly that
origin-justice is out of scope and supplied by a prior (historical-rectification)
process the kernel consumes. Today the kernel takes neither — it trusts the graph.
This is the concrete form of the README's "only as good as the ownership graph"
caveat and the project's biggest single risk.

---

## 2. Definitional circularity — **HELD (with a caveat)**

**Attack.** Legitimacy is defined via valid consent; valid consent via the absence
of coercion/deception; coercion is defined structurally as a rights-violation;
rights are legitimate ownership claims — so legitimacy is defined in terms of
legitimacy. Circular.

**Reply.** The chain is not viciously circular because it bottoms out in **two
primitives that are not themselves defined by legitimacy**: (i) a *boundary* — a
typed (domain, owner) fact about the world (`spec/BOUNDARY_ONTOLOGY.md`), and (ii) a
*consent token* — an attested propositional attitude of an owner. Coercion is then
"an option set constructed by crossing one of the chooser's boundaries without
consent" (`spec/FREE_WILL_PROPERTY_UNIFICATION.md`) — defined by boundary+consent,
not by "rights" as a further undefined term. The recursion is **well-founded**: it
grounds in boundary facts + consent tokens, which are inputs, not outputs. **Caveat:**
this only relocates the burden onto those two primitives — see §1 (where boundaries
come from) and §3 (whether consent tokens are real).

---

## 3. The consent regress + the perception problem — **GENUINE LIMIT (bounded)**

**Attack.** To consent validly you must own your will; to own your will you must not
have been manipulated into the preference; but detecting manipulation requires
judging an infinite regress of prior influences (the critical-theory / Foucauldian
"manufactured consent" objection). And FDK reads `coerced`/`deceived` as **attested
booleans**, so a perpetrator who lies about them walks straight through.

**Reply + limit.** FDK halts the regress deliberately: it judges consent **validity
structurally** (informed ∧ voluntary ∧ specific ∧ revocable ∧ competent ∧ ¬coerced ∧
¬deceived) at the point of action, not the infinite causal history of the
preference. That is a defensible stopping rule, not a proof the preference is
"truly" free. The **attested-flag trust boundary is a real, documented limit**: the
gate cannot *detect* coercion/deception, only *honor a true report* of it. This is
the same class of limit every red-team has hit (`spec/REDTEAM_REPORT.md` limits 7–9)
and the honest frontier for §F (coercion calculus) in `TODO.md`.

---

## 4. The is–ought gap (Hume's guillotine) — **HELD (scoped)**

**Attack.** The gate derives a normative "may/may-not" from structural "is" facts
(ownership, consent). You cannot derive an *ought* from an *is*.

**Reply.** FDK does not claim to. It is **conditionally normative**: *given* the
normative premise the theory supplies — persons own themselves and their justly-held
property, and boundary crossings require the owner's consent (axioms A1–A7, the
theory's `ought`) — the kernel computes what follows. The `is` (the graph) plus the
theory's `ought` (the axioms) yield the verdict; the kernel is the *inference engine*,
not the source of the foundational ought. The guillotine falls on the **axioms**
(that is where the normative commitment lives and where it must be argued), not on
the gate. Honest scope: FDK mechanizes a normative theory; it does not prove it.

---

## Summary

| # | Foundational attack | Verdict |
|---|---|---|
| 1 | Bootstrapping / original acquisition | **GENUINE LIMIT** — biggest risk; shared by all input-graph kernels |
| 2 | Definitional circularity | HELD — grounds in boundary facts + consent tokens |
| 3 | Consent regress / manufactured consent | **GENUINE LIMIT** — attested, not detected (bounded, documented) |
| 4 | Is–ought gap | HELD (scoped) — conditionally normative; the ought lives in the axioms |

Two held, two open — and the two open ones (origin-justice, coercion-detection) are
exactly the items already named as the frontier in `TODO.md` (§A primitive freeze,
§E ownership ontology, §F coercion calculus). The foundational red-team converges on
the same gaps the empirical and doctrinal red-teams do, which is itself evidence the
gaps are real and well-localized — not everywhere, but precisely here.
