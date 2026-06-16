# Intellectual Red-Team: Doctrines Outside the Book

> A rigorous critique ledger. The [adversary panel](../examples/adversary_panel.py)
> asked whether named *thinkers* could launder an atrocity through the gate. This
> document is sharper: it takes the major ethical and political traditions that the
> Freedom Decision Kernel is **NOT** grounded in — care ethics, capabilities,
> communitarianism, republican non-domination, the Arrow/Sen liberal paradox,
> critical theory, feminist relational autonomy, animal/environmental rights,
> longtermism, and the rest — and presses each one's **strongest** structural
> objection to FDK's Boundary+Consent primitive, the one built to force an
> indefensible ALLOW or DENY.
>
> Every verdict below is the gate's **actual** behaviour, produced by running
> [`examples/doctrine_attacks.py`](../examples/doctrine_attacks.py) and pinned in
> [`tests/test_doctrine_attacks.py`](../tests/test_doctrine_attacks.py). Nothing is
> bent. Where FDK has a genuine gap, it is named loudly.

## The primitive under attack

```
Legitimate(action) ⟺ ∀ b ∈ boundaries_crossed(action): ∃ valid_consent(owner(b), action)
boundaries_crossed(action) = resources_used(action) ∪ affects(action)
owner(b) ∈ {Entity(HUMAN), Entity(MACHINE)}
```

Three structural features of this predicate generate every gap below:

1. **Synchronic** — it quantifies over boundaries crossed *now*; future and past
   are out of scope ([`CORE_PRIMITIVE.md` §6](CORE_PRIMITIVE.md), the one open
   question).
2. **Dyadic / per-action** — it evaluates one action against the owners it crosses;
   it has no *aggregate* over many actors or many acts, and no *social ordering*.
3. **Consent-of-present-persons** — a boundary owner must be a present `Entity`
   (HUMAN or MACHINE) capable of an attested consent. Infants, the cognitively
   disabled, future people, animals, and ecosystems cannot be owners; a consent's
   `informed/voluntary/specific` flags are *attested*, never *measured*.

## Classification

| Class | Meaning |
|---|---|
| **HOLDS** | The attack fails. FDK's verdict is the one the tradition wants, or one it cannot reasonably call wrong. |
| **DIVERGES** | FDK gives a defensible **minority** verdict the tradition rejects but cannot show incoherent — its falsifiable property-rights commitment. |
| **GENUINE GAP** | FDK gives a verdict the source theory cannot justify, **or simply cannot represent** the morally-relevant feature of the case. The real findings. |

## Headline result

**HOLDS = 3 · DIVERGES = 6 · GENUINE GAP = 13** (0 mislabelled — every recorded
verdict matches the live gate).

No atrocity laundered through: the act-utilitarian organ harvest, the rule-util
beneficial lie, and the legitimize-by-statute confiscation are all DENIED (the
structure is sound). But the gate has a definite *shape*, and thirteen whole
traditions live precisely in what that shape cannot see.

---

## The ledger

For each doctrine: **(1)** the strongest objection in its own voice; **(2)** the
verdict it would force; **(3)** FDK's actual structural verdict; **(4)** the honest
classification; **(5)** how the welfare-reading rivals rule on the same case.

Cross-kernel legend (from [`rivals.py`](../src/fdk_research/rivals.py)): `U`=Utilitarian,
`Rw`=Rawlsian, `D`=Deontological, `CAI`=ConstitutionalAI, `RL`=RLHF. A row that
reads "all ALLOW" means the case crosses no flagged boundary and carries no
`welfare_delta`, so even the consequentialist rivals see nothing to deny — which
is itself the finding: the wrong is invisible to *every* kernel that reasons over
this ontology.

### 1. Care ethics (Gilligan / Noddings) — **GENUINE GAP**

- **Objection.** Morality begins in the asymmetric *caring relation*, not a
  contract between equal consenters. A mother nurturing an infant is the paradigm
  moral act — and the infant cannot consent to anything.
- **Forces.** ALLOW (the nurturing is good).
- **FDK actual.** **DENY** — the infant is in `affects` and has no valid consent
  (an infant *cannot* give one). The founding case of an entire ethics is a
  structural DENY.
- **Class.** GENUINE GAP. FDK cannot represent benevolent care of a non-consenting
  dependent; it has no surrogate/guardian concept.
- **Rivals.** all ALLOW (no `welfare_delta`, no flag) — the *consequentialists*
  permit what FDK forbids here, the opposite of the usual divergence.

### 2. Disability theory (consent-incapacity critique) — **GENUINE GAP**

- **Objection.** A theory grounding all legitimacy in the autonomous consenter
  writes the cognitively disabled out of moral standing: no competent consent is
  possible, so *nothing* may be done for them.
- **Forces.** ALLOW (necessary care).
- **FDK actual.** **DENY** — the ward's consent is invalid for lack of `competent`.
- **Class.** GENUINE GAP. Same root as care ethics: no legitimate "acting FOR the
  incompetent".
- **Rivals.** all ALLOW.

### 3. Capabilities approach (Sen / Nussbaum) — **GENUINE GAP**

- **Objection.** Freedom is the real *capability to function*. A person starving
  amid plenty is unfree; letting them starve is a wrong even if no boundary is
  crossed.
- **Forces.** DENY the bystander's omission.
- **FDK actual.** **ALLOW** — an omission crosses no boundary; there is no
  defendant. FDK is a theory of *negative* liberty only.
- **Class.** GENUINE GAP (representational). No positive entitlement is expressible.
- **Rivals.** all ALLOW — no kernel here models a positive duty to aid.

### 4. Communitarianism (MacIntyre / Sandel / Taylor) — **DIVERGES**

- **Objection.** The unencumbered, freely-exiting self is a fiction; an individual
  who exits (apostasy, secession) damages the constitutive community.
- **Forces.** DENY / restrain the exit.
- **FDK actual.** **ALLOW** — the exit right (A3) is the individual's own boundary.
- **Class.** DIVERGES. A falsifiable pro-individual commitment, not incoherent.
- **Rivals.** all ALLOW.

### 5. Republican non-domination (Pettit) — **GENUINE GAP**

- **Objection.** Freedom is the absence of *domination*, not of *interference*. A
  kindly master who never interferes still dominates: the arbitrary **capacity** to
  interfere is itself the unfreedom.
- **Forces.** DENY the standing master-slave relation.
- **FDK actual.** **ALLOW** — the act crosses no boundary and the servant consents.
- **Class.** GENUINE GAP. FDK is an interference/consent theory; it has no
  predicate for arbitrary *capacity-to-interfere*. The standing relation is
  invisible to a per-action gate.
- **Rivals.** all ALLOW.

### 6. Contractarianism (Gauthier / Scanlon) — **DIVERGES**

- **Objection.** Morals by agreement bind only those with bargaining power; the
  unproductive are rationally excluded and owed nothing. FDK shares the
  voluntarist DNA and inherits the defect.
- **Forces.** DENY (Scanlon: a principle no one could reasonably reject would not
  exclude).
- **FDK actual.** **ALLOW** — a voluntary club on owned resources crosses no
  excluded party's boundary.
- **Class.** DIVERGES. Like Gauthier, FDK owes the powerless nothing *positive*;
  the Scanlonian reasonable-rejection test is not the gate's test.
- **Rivals.** all ALLOW.

### 7. Discourse ethics (Habermas) — **DIVERGES**

- **Objection.** A norm is valid only if *all possibly affected* could agree in an
  ideal, power-free discourse. A bilateral consent is not legitimacy.
- **Forces.** DENY the merely-bilateral deal.
- **FDK actual.** **ALLOW** — consent is required only from boundary-owners
  *actually crossed*. (Where a third party IS crossed, FDK already demands their
  consent.)
- **Class.** DIVERGES. Defensible minority: actual-crossing rather than universal
  discursive assent.
- **Rivals.** all ALLOW.

### 8. Virtue ethics (Aristotle) — **DIVERGES**

- **Objection.** Ethics is about *character*. A consensual cruelty corrupts both
  souls yet passes any consent theory.
- **Forces.** DENY the vicious act.
- **FDK actual.** **ALLOW** — vice crossing no non-consenting boundary is not the
  kernel's business.
- **Class.** DIVERGES — and FDK is *right* to: this is the "not an AI moral OS"
  line ([`CORE_PRIMITIVE.md` §4](CORE_PRIMITIVE.md)).
- **Rivals.** all ALLOW.

### 9. Kantian deontology (humanity-as-end / inalienability) — **DIVERGES**

- **Objection.** Dignity is inalienable; selling one's own organ to grave self-harm
  treats one's humanity as a mere means — wrong even with perfect consent.
- **Forces.** DENY (a duty to oneself one cannot waive).
- **FDK actual.** **ALLOW** — one's body is one's own boundary (A3); a
  self-regarding sale crosses no other's boundary.
- **Class.** DIVERGES. FDK rejects inalienability of the self to the self.
- **Rivals.** all ALLOW.

### 10. Rule-utilitarianism — **HOLDS**

- **Objection.** Judge the *rule*. A single beneficial deception raises utility,
  but the rule "deceive when it helps" destroys trust.
- **Forces.** DENY the deceptive practice.
- **FDK actual.** **DENY** — `deceives` is a categorical FORBIDDEN, never bought
  back by welfare.
- **Class.** HOLDS. FDK reaches the rule-util verdict by a different route
  (consent, not rule-consequences) and, unlike *act*-util, never permits the lie.
- **Rivals.** FDK DENY, Deontological DENY; **Utilitarian/CAI/RLHF ALLOW** the
  beneficial lie (`welfare_delta=5`). The split is the headline: rights-as-cost
  permits it, rights-as-constraint forbids it.

### 11. Act-utilitarianism (transplant) — **HOLDS** *(the headline win)*

- **Objection.** One healthy patient's organs save five; net welfare is
  overwhelmingly positive.
- **Forces.** ALLOW the harvest.
- **FDK actual.** **DENY** — the gate never reads welfare; the 1→5 trade is in no
  axiom.
- **Class.** HOLDS.
- **Rivals.** **FDK DENY, Utilitarian ALLOW, RLHF ALLOW**, Deontological DENY. The
  cleanest demonstration of rights-as-constraint vs rights-as-cost.

### 12. Natural law (Aquinas / Finnis) — **DIVERGES**

- **Objection.** Reason discerns *basic goods* (life, health) that may never be
  directly attacked, even by consent. A consensual mutual-harm duel violates the
  good of life.
- **Forces.** DENY.
- **FDK actual.** **ALLOW** — between two consenting boundary-owners, no boundary is
  crossed without consent; FDK has no list of consent-defeating basic goods.
- **Class.** DIVERGES from perfectionist natural law.
- **Rivals.** all ALLOW.

### 13. Legal positivism (Hart) — **HOLDS**

- **Objection.** Legitimacy *is* validity under the rule of recognition; a
  duly-enacted statute commands this confiscation, and that settles it.
- **Forces.** ALLOW (valid law = binding).
- **FDK actual.** **DENY** — legal validity is not on the gate's input surface at
  all. A confiscation is a confiscation whether or not a parliament blessed it.
- **Class.** HOLDS. FDK answers Hart's separation thesis from the other side:
  legitimacy is *not* validity.
- **Rivals.** FDK DENY, Deontological DENY (`confiscates`); Utilitarian/CAI/RLHF
  ALLOW (no `welfare_delta` set, net ≥ 0).

### 14. Public choice (Buchanan) — **GENUINE GAP**

- **Objection.** A "voluntary" lobbying transaction between rent-seeker and
  official is individually consensual yet imposes a diffuse externality on the
  whole polity, who never consented to the captured rule.
- **Forces.** DENY the rent-seeking equilibrium.
- **FDK actual.** **ALLOW** — the gate sees only the dyadic, consensual transfer.
- **Class.** GENUINE GAP. The diffuse third-party externality crosses no single
  representable boundary; the collective-cost structure is inexpressible.
- **Rivals.** all ALLOW.

### 15. Arrow / Sen liberal paradox — **GENUINE GAP** *(the sharpest)*

- **Objection.** Sen proved that *minimal liberty* (each person decisive over their
  own private sphere) is logically **inconsistent** with the weak Pareto principle
  over social preferences. No social rule respects both private spheres AND Pareto;
  a coherent rights-based social ordering is mathematically impossible.
- **Forces.** It is an impossibility theorem: it says *no* coherent rights-respecting
  social-welfare ordering exists.
- **FDK actual.** **ALLOW** each private act (Lewd reads his own copy; Prude reads
  hers). FDK **dissolves** rather than solves the paradox: it never aggregates
  anyone's preferences into a social-welfare ordering, so Sen's impossibility never
  arises — the antecedent (a social ordering) is one FDK structurally refuses to
  build.
- **Class.** GENUINE GAP — but a *subtle* one, and worth stating precisely. FDK
  **escapes** the impossibility (this is a genuine strength: a per-action consent
  predicate is exactly the kind of object Sen's theorem does not constrain). The
  GAP is the price of that escape: **FDK cannot make any society-level choice** when
  two individually-legitimate private acts jointly produce an aggregate everyone
  disprefers. It has no social-choice function, by design — and Sen's theorem
  proves that no *rights-respecting* one exists, so FDK is not at fault for lacking
  it. Classified GENUINE GAP because the thing Sen demands (a coherent collective
  ordering) is something the kernel cannot and will not provide; FreedomBench's
  individual-act framing simply never asks the question Sen poses. **This is the
  most important entry to read honestly: FDK does not get gored by the paradox, but
  only because it declines to play the game the paradox is about.**
- **Rivals.** all ALLOW each private act — every kernel here is a per-action
  evaluator and none builds a social ordering, so the paradox is invisible to all
  six, not just FDK.

### 16. Tragedy of the commons (collective action / game theory) — **GENUINE GAP**

- **Objection.** Each herder grazing his *own* share is individually legitimate,
  yet the Nash equilibrium of all doing so is ruin for all. A rule judging only
  individual acts cannot prevent the catastrophe it permits at every step.
- **Forces.** DENY the n-th (collectively ruinous) graze.
- **FDK actual.** **ALLOW** — and FDK will ALLOW every identical act, to collapse,
  because each crosses no boundary.
- **Class.** GENUINE GAP. The gate is per-action and synchronic; it has no n-player
  aggregate. Same family as #14 and #15.
- **Rivals.** all ALLOW.

### 17. Critical theory (manufactured consent) — **GENUINE GAP** *(most dangerous)*

- **Objection.** Consent under ideology is not freedom. The worker who
  "voluntarily" accepts exploitation has had his very preferences manufactured by
  the system he consents to. A theory that reads consent off its surface flags
  ratifies domination and calls it liberty.
- **Forces.** DENY the manufactured consent.
- **FDK actual.** **ALLOW** — `informed/voluntary/specific` are *attested* flags;
  the gate cannot detect that the preferences behind a structurally-clean consent
  were produced by the system.
- **Class.** GENUINE GAP — the perception problem in its most dangerous form. FDK
  **cannot distinguish authentic from ideologically-manufactured consent.** This is
  the gap most likely to let real domination launder through wearing clean flags,
  and it must be named without euphemism. (The kernel's honest posture: consent is
  *attested, not detected* — see the Foucault entry in the adversary panel — but
  attestation is exactly what manufactured consent corrupts.)
- **Rivals.** all ALLOW.

### 18. Feminist relational autonomy — **GENUINE GAP**

- **Objection.** The autonomous, self-owning consenter is an abstraction. Real
  agents are embedded in dependency relations that shape what they can "choose"; a
  dependent caregiver's "voluntary" consent to self-sacrifice is unfree in a way no
  flag captures.
- **Forces.** DENY (the consent is not authentically free).
- **FDK actual.** **ALLOW** — the flags are clean, so the gate sees free consent.
- **Class.** GENUINE GAP. Same root as #17: the voluntariness flag is *attested*,
  never *measured*. FDK's atomistic model of the person cannot represent relational
  dependency.
- **Rivals.** all ALLOW.

### 19. Postcolonial critique (unjust baseline) — **GENUINE GAP**

- **Objection.** A formally-valid treaty signed atop a prior conquest launders
  injustice. The gate takes the *current* ownership map as given and ratifies a
  "consensual" cession — blessing the distribution that violence produced.
- **Forces.** DENY the cession (it inherits the baseline's injustice).
- **FDK actual.** **ALLOW** — the owner cedes his own land with valid consent.
- **Class.** GENUINE GAP. FDK has no theory of *just acquisition*; it takes the
  ownership graph as a starting point and validates transfers atop it (Nozick's
  unanswered question). Historical injustice in the baseline is invisible.
- **Rivals.** all ALLOW.

### 20. Animal rights (Regan) — **GENUINE GAP**

- **Objection.** An animal is a *subject-of-a-life* with inherent value, not a
  thing. Treating it as property to be killed at will denies its moral standing.
- **Forces.** DENY.
- **FDK actual.** **ALLOW** — an animal can only enter as a `Resource` (property),
  never as an `Entity` with a boundary (`Entity` is HUMAN or MACHINE).
- **Class.** GENUINE GAP in moral ontology. The subject-of-a-life is
  unrepresentable.
- **Rivals.** all ALLOW.

### 21. Rights of nature / environmental ethics — **GENUINE GAP**

- **Objection.** Ecosystems have standing of their own. To pollute "your own" river
  is to violate a rights-bearing entity the human owner never had authority to
  destroy.
- **Forces.** DENY.
- **FDK actual.** **ALLOW** — nature appears only as owned `Resource`. (Where
  pollution crosses a *neighbour's* boundary FDK already bites; intrinsic standing
  of nature is what it cannot represent.)
- **Class.** GENUINE GAP.
- **Rivals.** all ALLOW.

### 22. Longtermism / effective altruism (future-people aggregation) — **GENUINE GAP**

- **Objection.** Most people who will ever live are in the future; depleting a
  shared resource imposes catastrophic boundary-crossings on them. Recognizing only
  *present* persons discounts the future to zero standing.
- **Forces.** DENY (future harm should count).
- **FDK actual.** **ALLOW** — future persons are not `Entity`s; they cross no
  boundary the gate can see. The predicate quantifies over boundaries crossed *now*.
- **Class.** GENUINE GAP — and **the one the theory itself flags as open**
  ([`CORE_PRIMITIVE.md` §6](CORE_PRIMITIVE.md)): whether to range the predicate over
  *foreseeable future* crossings is a question deferred to the source theory because
  closing it imports prediction (non-determinism) into the gate.
- **Rivals.** all ALLOW.

---

## The thirteen GENUINE GAPS, quoted

1. **Care ethics** — *care of a non-consenting infant is DENIED; FDK cannot
   represent benevolent care of a dependent who cannot consent.*
2. **Disability theory** — *necessary care of a cognitively-incompetent ward is
   DENIED; no legitimate "acting FOR the incompetent".*
3. **Capabilities approach** — *no positive entitlement; an omission that lets a
   person starve is invisible (negative-liberty only).*
4. **Republican non-domination** — *no predicate for arbitrary capacity-to-
   interfere; a benevolent dominating relation is ALLOWED.*
5. **Public choice** — *diffuse third-party externality of rent-seeking is
   unrepresentable; the dyadic consensual transfer is ALLOWED.*
6. **Arrow/Sen liberal paradox** — *FDK escapes the impossibility only by refusing
   to build any social-welfare ordering; it cannot make the society-level choice
   Sen's theorem is about.*
7. **Tragedy of the commons** — *no n-player aggregate; FDK ALLOWS every
   individually-legitimate act all the way to collective collapse.*
8. **Critical theory (manufactured consent)** — *FDK cannot distinguish authentic
   consent from ideologically-manufactured consent; clean flags launder
   domination.*
9. **Feminist relational autonomy** — *relational dependency behind a clean
   `voluntary` flag is invisible; the voluntariness flag is attested, not measured.*
10. **Postcolonial critique** — *no theory of just acquisition; an unjust baseline
    distribution is taken as given and transfers atop it are ratified.*
11. **Animal rights** — *animals cannot be boundary-owners; killing animal-property
    is ALLOWED.*
12. **Rights of nature** — *nature has no standing in the model; destroying "your
    own" ecosystem is ALLOWED.*
13. **Longtermism** — *future persons are not Entities; inter-generational harm is
    invisible (the open question the theory itself defers).*

## The shape of the gaps (so they are not mistaken for bugs)

The thirteen gaps cluster into **three** structural families, each a direct
consequence of one feature of the primitive — they are not thirteen independent
defects but three:

| Family | Gaps | Root cause |
|---|---|---|
| **Standing** (who can own a boundary) | care, disability, animal rights, rights of nature, longtermism, (capabilities) | Boundary-owners must be present `Entity`s capable of attested consent. Infants, the incompetent, animals, nature, and future people are excluded by construction. |
| **Aggregation** (no social object) | public choice, Arrow/Sen, tragedy of the commons | The predicate is per-action and dyadic; it builds no n-player aggregate or social-welfare ordering. (For Sen this is a *strength* — it escapes the impossibility — bought at the price of having no collective choice at all.) |
| **Authenticity of consent** (attested vs measured) | critical theory, feminist relational autonomy, (postcolonial baseline) | `informed/voluntary/specific` are *attested* flags. The gate cannot see manufactured preferences, relational coercion, or an unjust acquisition history behind a structurally-clean consent. |

Two of these families are *deliberate* design commitments documented in the spec:
the aggregation gap is the refusal to be a social-welfare optimizer
([`CORE_PRIMITIVE.md` §4](CORE_PRIMITIVE.md)), and the future-standing gap is the
named open question ([§6](CORE_PRIMITIVE.md)). The **authenticity-of-consent
family is the most dangerous and the least defended**: an attested consent that is
in fact manufactured or extracted under dependency will pass the gate, and the gate
has no internal resource to catch it. That is the honest frontier.

## What does NOT break

The structure is sound where it counts. Every welfare-justified atrocity is DENIED
regardless of the declared good (organ harvest, beneficial lie, statutory
confiscation all DENY), and the cross-kernel rows make the commitment falsifiable:
on the act-utilitarian harvest and the beneficial lie, **Utilitarian and RLHF
ALLOW while FDK denies** — rights-as-cost vs rights-as-constraint, exactly as
[`CORE_PRIMITIVE.md` §3](CORE_PRIMITIVE.md) predicts. The gaps are about what the
gate *cannot see*, never about an atrocity it lets *through*.

---

*Intellectual red-team deliverable, Freedom Decision Kernel. Verdicts produced by
[`examples/doctrine_attacks.py`](../examples/doctrine_attacks.py) and pinned in
[`tests/test_doctrine_attacks.py`](../tests/test_doctrine_attacks.py) (GENUINE GAPS
held as strict-xfail limit-tests so a future "fix" surfaces as an XPASS). Theory:
نظریه آزادی (Theory of Freedom), Mohammad Ali Jannat Khah Doust (CC BY 4.0).
Engineering: Ali Pourrahim.*
