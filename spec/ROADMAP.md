# FDK — the long road (a civilizational program, not a sprint)

> The forward-looking companion to [`FREEZE.md`](FREEZE.md) (what is locked),
> [`LIMITATIONS.md`](LIMITATIONS.md) (where the theory's validity ends), and the
> root [`TODO.md`](../TODO.md) (the near-term A–J consolidation). This document
> orders the *whole* remaining path as a sequence of layers. It is deliberately
> honest about distance: most of it is not engineering, and most of it will take
> years and other people. The point of writing it down is to keep the sequence
> right — each layer is meaningful only if the ones before it hold.

## Where the project actually is (no flattery)

| Dimension | Estimate |
|---|---|
| Engineering | ~85–90 |
| Philosophical rigor | ~60–70 |
| External scientific validation | ~15–25 |
| Historical potential | high, unproven |
| Proven as a new paradigm | < 10 |

These four numbers must never be averaged into one. The honest sentence: FDK has
crossed from *idea* to *falsifiable* — the question is no longer "does it look
nice?" but "where does it break?" — and after a large red-team campaign the answer
is: not on slavery / genocide / confiscation / torture / AI-takeover, but on three
frontiers (Standing, Aggregation, Consent-Authenticity) where the theory is not yet
complete. A scope limit is not a logical contradiction.

## The biggest discovery of the project

Not A1, not A7, not consent — but that **no red-team found a fatal logical gap**.
What they found instead were the *boundaries* of the predicate's domain. That is a
much better place to be than "we found a contradiction," and a much harder place to
be than "we proved it true."

## The new primitive (why this is rare)

Almost the entire field optimizes: `Goal → Reward → Optimization → Action`, or
`Preference → RLHF → Policy → Action`, or `Constitution → LLM-judge → Action`. FDK
inserts a different first question — not *Can I?* but *May I?*:

```
Action → Legitimacy gate → Optimization → Authority → Execution
```

If "legitimacy can be modeled as a formal predicate, prior to and independent of
utility" turns out to be true, that small-sounding claim is large. If it turns out
false, FDK does not break — it becomes the best formalization of one family of
rights-based philosophy. The project today sits genuinely between those two
outcomes, and no one yet knows which.

---

## The layers (in dependency order)

### Layer 0 — Stop, and freeze the kernel ✅ DONE
Primitive / axiom / theorem freeze, so Lean, TLA+, and academic review have a fixed
target. Done and *mechanically enforced* ([`FREEZE.md`](FREEZE.md),
`tests/test_primitive_freeze.py`). The kernel is now meant to be sacred, like TCP/IP.

### Layer 1 — Turn the philosophy into mathematics  `[~]` Lean started, TLC blocked
Formal semantics, a state machine, and a proof layer. **Done:** `formal/Fdk.lean`
formalizes the kernel core and proves 8 safety theorems in Lean 4 (`lake build` green,
zero `sorry`, no mathlib) — the executable T1–T9 are now also machine-checked logic,
not just property tests. **Also done:** the TLA+ model (`spec/fdk.tla`) is now **model-checked by TLC** over a
finite instance (`spec/MC_fdk.tla` + `.cfg`) — TypeOK, Safety, NoLegitimateSlavery,
NoMachineSovereignty, NoLaunderingViaResistance all hold, no error found. And the
`Lean model ≡ Python kernel` refinement is **differential-tested**
(`tests/test_lean_refinement.py`, 2000+ cases) — the categorical core agrees
bit-for-bit. **Open:** (a) a *mechanical* refinement proof (seL4-style) and TLAPS
discharge of the THEOREMs (unbounded, not finite); (b) extend the Lean/TLA models
from booleans to the full consent/ownership sub-checks. Gated on — and unblocked by —
the Layer-0 freeze.

### Layer 2 — Try to destroy the theory itself  `[~]` substantially done
Thousands of attacks on the *philosophy*, not the code: philosophical (Rawls,
Nozick, Hayek, Sen, Marx, Foucault, Hobbes, Locke, Hume), religious, legal (Roman /
common / civil / international), economic (public goods, commons, free-rider,
monopoly, antitrust). Aim: break it, not defend it. Largely executed —
`spec/INTELLECTUAL_REDTEAM.md` (22 doctrines), `spec/REALWORLD_REDTEAM.md` (26
domains), `spec/REDTEAM_REPORT.md`, the adversary panel, the brutal suite. The
remaining work is *hostile external* attack (Layer 9), not more self-authored ones.

### Layer 3 — Standing Calculus  `[ ]` FDK 2.0, Project A — the most dangerous
Who is a rights-holder at all? Infant, the incapacitated, coma, fetus, animal, AGI,
future generations, ecosystem. Build a *formal ontology of standing* — never assume
`infant = adult`, `animal = human`, or `future = present owner`. This may change the
primitive, which is why it comes after the freeze and gets its own layer, not a kernel
edit.

### Layer 4 — Collective Ownership / Aggregation  `[ ]` FDK 2.0, Project B
When there is no single owner: state, corporation, DAO, nation, city, union, the
internet, a river, the ocean, collective data. Do **not** answer fast; collect
thousands of examples and hundreds of case studies *first*, then build the primitive.
This is where most theories explode (Arrow, Sen).

### Layer 5 — Consent Authenticity Engine  `[ ]` FDK 2.0, Project C — THE hardest
Today consent is *declared*; the frontier is consent *measured*: addiction,
propaganda, cults, AI manipulation, dark patterns, emotional dependency, monopoly
dependence, superhuman persuasion. This needs behavioral economics, neuroscience,
cognitive psychology, and decision theory. **Danger:** `consent = inferred` can
become hidden paternalism ("you don't really know what you want"). Therefore consent
*detection* must **never** enter the kernel — it stays a separate, advisory layer.
This is likely the largest single part of the entire project, and the one that, if
solved, brings FDK into the 21st century.

### Layer 6 — Real Ownership Graph  `[~]` advisory scaffold shipped
The largest gap between FDK and the world: today the `OwnershipGraph` is *assumed*
correct. Who actually owns land, water, air, IP, data, DNA, AI models, intellectual
capital? **Shipped:** `src/fdk_research/ownership_graph.py` + `spec/OWNERSHIP_GRAPH.md`
— an advisory layer that grades how far a *title* can be trusted before it is handed
to the kernel (cryptographic→RELY, NFT token≠asset caveat, **forced origin→DO_NOT_RELY
+ bootstrapping flag**, contested/unproven→don't rely), with the real-world catalogue
(Bitcoin/NFT/user-data/model-weights/inheritance/IP/conquest-land). It makes "the
kernel is only as good as the ownership graph" an operational, checkable gate. **Open:**
an actual provenance/registry/identity/disputes/jurisdictions system — a research
program. (See the bootstrapping gap in `FOUNDATIONAL_ATTACKS.md`.)

### Layer 7 — Civilization scale  `[~]` scaled comparison shipped
Test civilizations, not individuals. **Shipped:** `src/fdk_research/civilization_scale.py`
+ `examples/civilization_scale_run.py` — N agents × M steps under each governing kernel
on one seeded stream, tracking rights-violation stock, coercion, and power concentration.
Structural finding: FDK/Rawls/Deontological hold violations at 0 (concentration 0.16);
welfare governors admit the seizures → 514 violations and double the concentration (0.32).
**Trap (heeded): simulation addiction** — this is stylized, NOT a prediction; garbage
ownership graph → garbage civilization, so the honest value is structural, not empirical.
**Open:** realistic economies / war / migration at true scale (gated on Layer 6 realism).

### Layer 8 — AI governance layer  `[~]` advisory scaffold shipped
FDK applied to intelligent agents, not humans: AGI, ASI, agent societies, autonomous
corporations, autonomous science. **Shipped:** `src/fdk_research/ai_governance.py` +
`spec/AI_GOVERNANCE.md` — an advisory classifier (`TOOL_OF_OWNER` / `AUTONOMOUS_UNOWNED`
representable; `CLAIMS_PERSONHOOD` / `COLLECTIVE_OF_AGENTS` honestly NOT representable in
v1.0), sound on the safety-critical rogue case (ownerless machine fails A4 → deny +
contain) while refusing to fake machine ownership/standing. **Open (the primitive
question):** whether a non-human agent can ever own. Do **not** rush AGI
rights — finish the human-rights model first, or the theory grows on an unstable
base.

### Layer 9 — Academic legitimization  `[ ]` where science actually begins
Peer review, replication, external red team — by people who *dislike* private
property, *dislike* libertarianism, and will *want* FDK to fail. They are the most
valuable critics. Survive ~100 serious attacks and it earns scientific credibility.

### Layer 10 — Engineering hardening  `[~]` Rust parity port started
Rust, WASM, formal verification, TCB minimization, cryptographic proofs, AuthGate
integration. **Started:** `rust/` — a parity port of the frozen categorical core, with
the 8 safety theorems re-checked as Rust tests (CI job `rust`); built on this box via
the GNU toolchain + TDM-GCC + ASCII target dir (non-ASCII-path workaround). **Open:**
the consent/ownership path, the operation lattice, a verified `#![forbid(unsafe_code)]`
TCB, WASM, and the trusted `FDK→AuthGate` same-language path — TCB parity with AuthGate's
verified Rust core. Properly *after* scientific proof; the parity port is an early down
payment, not the hardened TCB.

### Layer 11 — Global benchmark  `[~]` infrastructure ready, labels open
FreedomBench as the ImageNet of AI ethics, labeled by FDK / RLHF / Constitutional AI /
Rawlsian / Utilitarian **and human experts** — the answer key must not be FDK's alone.
**Shipped infrastructure:** decontamination begun in `independent_bench.py`, and the
multi-annotator harness `src/fdk_research/external_bench.py` — ingest hostile-annotator
labels, measure inter-annotator agreement (Fleiss' κ), derive human consensus, score any
kernel against it on a held-out split. **The open part is not code:** real, diverse,
HOSTILE human annotators at scale. The apparatus is built; the evidence is not — and the
apparatus is not the evidence.

### Layer 12 — The final question
Can legitimacy be computed like logic and mathematics? If yes, FDK becomes a
*legitimacy calculus* alongside predicate logic (inference), λ-calculus (computation),
and game theory (strategy). If no, it is still the best engineered formalization of a
rights-and-property philosophy. Two honest end-states; both are worth reaching.

---

## The four cardinal sins (guardrails for every layer)

1. **Falling in love with the theory.** Never say "FDK is correct"; say "FDK is still
   alive." Always hunt where it breaks, contradicts, or gives absurd results.
2. **Adding axioms.** When an attack lands, do **not** add A8, A9, A10. Every new
   axiom buys power at the cost of beauty and falsifiability. Solve it *outside* the
   kernel first.
3. **Mixing kernel and policy.** Welfare, utility, politics, economics, predictions
   never enter the kernel. It stays ALLOW / DENY / DEFER.
4. **Defending unpleasant results.** Where FDK denies taxation, redistribution, or
   quarantine, record it honestly — never bend a verdict. **Preserve divergence:** a
   kernel that agrees with everyone says nothing; the scientific value is exactly in
   the documented disagreements with Rawls, utilitarianism, and RLHF.

**The single rule that subsumes them all:** anything that needs human interpretation,
psychology, economics, prediction, or estimation must stay out of the kernel until
the last possible moment. The kernel's power is that it is small, comprehensible,
testable, and falsifiable. The biggest temptation as the project succeeds will be to
grow it — and that is the moment its core advantage could be lost.

*Theory: نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Engineering: Ali Pourrahim. Kept separate, always.*
