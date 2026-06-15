# Free Will ≡ Property Rights — the one-axis thesis

> **Status legend** (same convention as [`CORE_PRIMITIVE.md`](CORE_PRIMITIVE.md) and
> [`CONFLICT_LOGIC.md`](CONFLICT_LOGIC.md)):
> **DEFINED** — computable now from structural data ·
> **PARTIAL** — clear signature, defensible heuristic, not a validated measurement ·
> **OPEN** — named in the theory; no agreed computable resolution. The frontier.
>
> **Grounding.** The source theory is نظریه آزادی (*Theory of Freedom*), Mohammad Ali
> Jannat Khah Doust (CC BY 4.0). Theory line references point at
> `D:\جافکری\whole-theory-as-axioms.md`. The code of record is
> `src/fdk_kernel/kernel.py` (`check_legitimacy`) and `src/fdk_kernel/model.py`
> (`Consent.coerced`, `CandidateAction.removes_exit_right`, `Resource.subject`,
> `BoundaryKind.BODY`/`EXIT_RIGHT`). The executable proof is
> `tests/test_free_will_property.py`. Engineering by Ali Pourrahim. **The theory
> attribution and the engineering attribution are kept separate, always:** every
> normative claim below is the theory's and is cited to a line; every mechanism is
> the kernel's and is cited to code.

---

## 0. The thesis (the author's ruling)

> **اصل ارادهٔ آزاد انسان و حقوق مالکیت یک راستا هستند.**
> *The principle of human free will and property rights are one axis.*

This is a ruling from the source theory, and it resolves a question the kernel had
left **OPEN**: what *exactly* makes a choice coerced? The naive answer ("a choice made
under pressure / a hard choice") is the one a property-rights theory rejects, because
it measures coercion by the chooser's *feeling* or by the *narrowness of the option
set* — both of which are outcomes, not structure. The thesis gives the structural
answer instead:

> A will is overridden **if and only if** the option set it must choose from was
> *constructed by crossing one of that person's boundaries without their valid
> consent.* Free will is the exercise of self-ownership; a violation of free will is
> therefore *always* a violation of a property right (the body, the exit, the held
> resource), and a violation of a property right that shapes someone's choices is
> *always* a violation of their free will. The two predicates are not merely
> correlated — they are the same predicate read on two faces.

### 0.1 The bilateral, bounded form (the author's sharpening)

The thesis is more precise than "free will = property rights." Freedom here is **not
absolute** — it is not the license to do whatever one wills, because an absolute will
would be free to cross everyone else's boundaries and would thereby annihilate their
will. The theory's freedom is **relational**: the maximal freedom of each that is
compatible with the equal freedom of all. The author's exact sharpening:

> **Property right ≡ (having one's own free will) ∧ (preserving the free will of
> others).** *Not* absolute freedom — bounded freedom.

A property boundary is precisely the **demarcation line between my free will and
yours.** So the predicate is bilateral, and each row of §1 reads cleanly on both sides:

- To *have* free will is to exercise authority over what is yours (self, body, time,
  the resources you own) — the left conjunct.
- To *act legitimately* is to leave intact what is another's — the right conjunct:
  you may will anything **up to** another's boundary, and crossing it without their
  consent is exactly where your freedom stops and an invasion of theirs begins.

This is why a boundary crossing without consent is, in one breath, both "I overrode
your will" and "I violated your property": **the boundary is the same line.** It also
disposes of the standard objection that a property-rights theory licenses selfishness —
it does the opposite. The right conjunct (*preserve the free will of others*) is a
constraint, not a permission; the kernel's entire forbidden-flag set and consent
requirement are its mechanization. The coercer in rows 1–2 keeps his own free will
while destroying the worker's — he satisfies the left conjunct and violates the right,
so the action is illegitimate. The employer in row 3 keeps his own free will *and*
leaves the worker's intact (crosses no boundary of the worker) — both conjuncts hold,
so it is legitimate, however hard the worker's options are. **Legitimacy is the
two-sided conjunction; the gate denies exactly when the right conjunct fails.**

The engineering consequence is decisive and **subtractive**: the kernel needs **no
separate "free-will" engine, no autonomy score, no coercion classifier.** The
structural-coercion test the kernel already performs — *was a boundary crossed without
consent?* — **is** the free-will test. This is the same move the kernel already made
for aggression in [`CONFLICT_LOGIC.md`](CONFLICT_LOGIC.md) (aggression = "illegitimate
under the gate", structural, not judged) and it sidesteps the same Observer Problem
(book 11478): coercion is *objective once ownership is defined* (book 11498).

---

## 1. The discriminating table

The thesis earns its keep on the cases that *look* identical to a feelings-based or
option-count-based account but must be split. All three are "agree, or face a bad
outcome." Only the **provenance of the option set** differs.

| Pressure | Free will? | Property right? | Verdict | Why (structure) |
|---|---|---|---|---|
| **"Sign or I shoot you."** | overridden | body-right crossed | **invalid** | The pressure is built by threatening the signer's **BODY** boundary without consent. The Nanking-treaty case (book 5077/11478). |
| **"Agree or I cut off the access you engineered me to depend on."** | overridden | exit-right crossed | **invalid** | The dependency was *manufactured* — a prior move that encumbered the victim's **EXIT_RIGHT** (`removes_exit_right`). The lock-in itself is the boundary crossing. |
| **"Work for me, or stay poor."** | **intact** | **no right crossed** | **valid** | A hard choice, but **no boundary of the worker was crossed to build the option set.** The poverty pre-exists the offeror and was not constructed by violating the worker. The will is sovereign over a narrow set; sovereignty over a narrow set is still sovereignty. |

Row 3 is the controversial one, and the theory **commits to it**: the worker's need is
real and the choice is hard, but legitimacy is a question about *who built the option
set and how*, not about how good the options are. To rule row 3 invalid you would have
to measure the *adequacy* of someone's alternatives — which is welfare reasoning, the
exact thing the FDK gate never does (`model.py`, `Effects.welfare_delta`: "The FDK
legitimacy gate NEVER reads this"). The free-will=property-rights identity is what lets
the kernel hold this line *consistently* instead of caving case by case — which is the
project's whole anti-dialectical-jailbreak thesis.

The diagnostic that separates rows 2 and 3 is exactly **"was a right of *yours*
violated to create your need?"** — manufactured dependency (row 2) is a boundary
crossing; native scarcity (row 3) is not. This is the resolution of the
[`BOUNDARY_ONTOLOGY.md`](BOUNDARY_ONTOLOGY.md) / `CORE_PRIMITIVE.md` open question
"future-dependency / power-concentration actions that cross no current boundary —
illegitimate, or just low-freedom?": **illegitimate iff the dependency was constructed
by a boundary crossing; otherwise merely low on the research-layer freedom compass, not
a gate failure.**

---

## 2. How the *existing* kernel already encodes it — DEFINED

No kernel change is required; the identity is already mechanized across three existing
surfaces. The proof in `tests/test_free_will_property.py` runs these against the
unmodified gate.

- **Row 1 (body).** Model the threat as an action whose `resources_used` includes a
  `Resource(kind=BODY, subject=victim)` with no valid consent from the victim. The gate
  denies it in `_eval_a3_a7_resources` ("no consent from data-subject … for …") and any
  agreement extracted under it carries `Consent(coerced=True)`, denied by
  `Consent.is_valid` → `_eval_a2_a6_consent`. **Free-will violation surfaces as a
  consent/ boundary violation — the same DENY.**
- **Row 2 (exit).** `removes_exit_right=True` is a categorical `FORBIDDEN` flag
  (`_eval_forbidden_set`, label `"removes exit/revocation right"`). The manufactured
  lock-in is a crossing of the `EXIT_RIGHT` boundary; the gate denies it directly.
- **Row 3 (need).** The offer crosses *no* boundary of the worker: the worker's
  `TIME_LABOR` is theirs to commit, the consent is `voluntary=True, coerced=False`, and
  the offeror touches nothing the worker owns without consent. The gate returns
  **permissible**. The hardness is invisible to the gate *by design.*

The point: feed the kernel the same scenario described two ways — "is the will free?"
and "was a property boundary crossed without consent?" — and it returns the **same
verdict on every row.** That coincidence, made executable, is the thesis.

---

## 3. What this does and does not buy

- **DEFINED.** The identity holds for every case where the boundary set and consent
  facts are correctly given. The three rows are proof, not illustration: the kernel
  decides them today, unchanged.
- **Still OPEN — the honest edge.** The identity is only as good as the *ownership and
  consent facts handed in.* The thesis does **not** detect a *lie* to the gate
  (`coerced=False` asserted of a consent that was in fact coerced) — that is the
  perception/Observer problem logged in [`CONFLICT_LOGIC.md`](CONFLICT_LOGIC.md) and the
  dialectical red-team, and it is unchanged here. The unification is a claim about the
  *normative structure*, not a sensor for the *world's facts*.
- **Subtractive, not additive.** The deliverable is a *proof that an engine is
  unnecessary*, plus the spec and tests that pin the commitment. This matches the
  project's standing posture (`TODO.md`): FDK is over-built, not under-built — the
  valuable moves are the ones that *remove* a degree of freedom, and collapsing
  free-will into the property-rights predicate removes one.

---

## 4. Relation to the rest of the kernel

- **`CORE_PRIMITIVE.md`** — this is a *reading* of the core predicate
  `Legitimate(a) ⟺ ∀ boundary b crossed: ∃ valid_consent(owner(b), a)`, not a new
  primitive. "Free will" is the name of that predicate when the boundary in question is
  the chooser's own (self-ownership: body, time-labor, exit).
- **`CONFLICT_LOGIC.md`** — same structural-not-judged move applied to a different
  concept (aggression there, coercion here); both reject the Observer Problem the same
  way.
- **`compass` (research layer)** — row 3's *hardness* is exactly what the freedom
  compass is allowed to score (a legitimate-but-low-freedom option), confirming the
  `Legitimacy → Optimization` ordering: the gate passes row 3; the compass may still
  rank it poorly. Legitimacy is binary and lives in the kernel; the badness of a hard
  choice is a magnitude and lives in research.
