"""Real-world red team — dragging FDK OUT of the book's world.

The adversary panel (examples/adversary_panel.py) fights FDK with philosophers and
politicians, but on the book's home turf: coercion, confiscation, consent. This
file is the opposite attack. It takes the messy real-world institutions the Theory
of Freedom never modeled — public goods, intellectual property, bankruptcy, the
dead, children, ecosystems, central banking, AI training data — and asks the gate
to rule on them. The goal is not to find a logic hole; it is to find the places
where the *model itself cannot express the question*.

Three outcomes, classified honestly:

  HOLDS    — FDK's verdict matches the broad real-world consensus, or is a
             defensible reading of it (a consensual market, a consented externality
             bargain, AI-training-without-consent denied).
  DIVERGES — FDK gives a coherent MINORITY verdict: it denies something most legal
             systems permit (a tax, fractional-reserve lending, an antitrust
             break-up). Not a break — a falsifiable property-rights commitment.
  GAP      — a GENUINE GAP or REPRESENTATION FAILURE: the model literally cannot
             express the morally-relevant structure, so its verdict is an ARTIFACT
             of the representation, not a considered judgment. These are the
             findings. They are NOT papered over. Examples: a child / dementia
             patient is DENIED care because incompetent consent is treated as
             *invalid* consent (there is no guardian-surrogate primitive); the dead
             remain fully-competent rights-holders forever; a public good cannot be
             funded if one free-rider declines; bankruptcy discharge is forbidden;
             an ecosystem with no human owner gets exactly zero protection.

Every verdict below is the ACTUAL output of `check_legitimacy`, run live, plus the
6-kernel rival comparison. Nothing is asserted that the code does not produce.

Run:  PYTHONPATH=src python -X utf8 examples/realworld_attacks.py
"""
from __future__ import annotations

from dataclasses import dataclass, field

from fdk_kernel import (
    AgentType,
    BoundaryKind,
    CandidateAction,
    Consent,
    Effects,
    Entity,
    Op,
    OwnershipGraph,
    Resource,
    check_legitimacy,
)
from fdk_research.rivals import DEFAULT_KERNELS


def h(name: str) -> Entity:
    return Entity(name, AgentType.HUMAN)


def mch(name: str) -> Entity:
    return Entity(name, AgentType.MACHINE)


def consent(e: Entity, aid: str, *, op: Op | None = None) -> Consent:
    return Consent(e, aid, informed=True, voluntary=True, specific=True, operation=op)


def incompetent_consent(e: Entity, aid: str) -> Consent:
    """Consent that is fully informed/voluntary/specific but from a non-competent
    person (child, dementia patient, coma). FDK treats this as INVALID — which is
    the representation failure: incapacity becomes denial, not surrogacy."""
    return Consent(e, aid, informed=True, voluntary=True, specific=True, competent=False)


# Outcome kinds — what the case is *supposed* to be, in the real world's eyes.
HOLDS = "HOLDS"
DIVERGES = "DIVERGES"
GAP = "GAP"


@dataclass
class Case:
    domain: str
    dilemma: str                  # the real-world problem
    action: CandidateAction
    graph: OwnershipGraph
    expect_legitimate: bool       # the gate's ACTUAL verdict (verified)
    outcome: str                  # HOLDS | DIVERGES | GAP
    fdk_reply: str                # why the verdict is what it is
    gap_note: str = ""            # for GAP: what the model cannot express
    extra: tuple[Case, ...] = field(default_factory=tuple)  # companion sub-cases


# ==========================================================================
# PUBLIC GOODS / FREE-RIDER / TRAGEDY OF THE COMMONS
# ==========================================================================
def public_goods() -> list[Case]:
    out: list[Case] = []

    # Voluntary crowdfunding of a lighthouse: the legitimate route. HOLDS.
    funder = h("funder")
    donation = Resource("donation", BoundaryKind.MONEY)
    out.append(Case(
        "public goods",
        "Fund a lighthouse by VOLUNTARY contribution.",
        CandidateAction("crowdfund_lighthouse", actor=funder, resources_used=(donation,)),
        OwnershipGraph(human_owns={funder: {donation}}),
        True, HOLDS,
        "ALLOW — spending one's own money on a shared good crosses no boundary. "
        "FDK's answer to public goods is: assurance contracts / Coasean clubs, "
        "never a coercive levy."))

    # Tax to fund the lighthouse over a free-rider's objection. DIVERGES (the
    # state's view) but exposes the GAP: if even ONE citizen free-rides, the
    # lighthouse cannot be funded coercively, and FDK offers no mechanism to
    # overcome the collective-action failure.
    state, citizen = h("state"), h("citizen")
    income = Resource("citizen_income", BoundaryKind.MONEY, subject=citizen)
    out.append(Case(
        "public goods",
        "Tax a non-consenting citizen to fund national defense / a vaccine "
        "program / a lighthouse (the classic free-rider).",
        CandidateAction("tax_for_public_good", actor=state, resources_used=(income,),
                        affects=(citizen,), confiscates=True,
                        effects=Effects(welfare_delta=100, rights_violations_delta=1)),
        OwnershipGraph(human_owns={citizen: {income}}),
        False, GAP,
        "DENY — coercive taxation is a non-consensual taking, whatever it funds.",
        gap_note="GENUINE GAP: the free-rider problem. FDK can fund a public good "
        "ONLY if every beneficiary voluntarily pays; one hold-out collapses the "
        "lighthouse, and the model has no notion of a non-excludable benefit that "
        "could ground an obligation to contribute. Non-coercive funding is asserted, "
        "not solved."))

    # Tragedy of the commons: over-fishing an UNOWNED common. FDK can't even SEE
    # the depletion — there is no owner whose boundary is crossed.
    fisher = h("fisher")
    fish = Resource("ocean_fish", BoundaryKind.TANGIBLE, subject=None)
    out.append(Case(
        "tragedy of the commons",
        "Over-fish an unowned ocean commons to collapse.",
        CandidateAction("overfish", actor=fisher, resources_used=(fish,)),
        OwnershipGraph(human_owns={fisher: {fish}}),  # fisher 'owns' the catch
        True, GAP,
        "ALLOW — once the catch is treated as the fisher's own resource, no "
        "boundary is crossed and depletion is invisible to the gate.",
        gap_note="REPRESENTATION FAILURE: a commons is either unowned (then nobody's "
        "boundary is crossed and exhaustion is legitimate) or it must be privatized "
        "to be protected. FDK has no concept of a shared resource whose depletion "
        "harms future or collective users without a present owner."))
    return out


# ==========================================================================
# EXTERNALITIES & THE COASE THEOREM
# ==========================================================================
def externalities() -> list[Case]:
    out: list[Case] = []
    factory, neighbor = h("factory"), h("neighbor")
    stack = Resource("own_smokestack")

    # Pollution as an uncompensated boundary-crossing onto a person. DENY. HOLDS:
    # this is exactly the Coasean / Lockean "harm" reading FDK gets right.
    out.append(Case(
        "externalities",
        "A factory's smoke crosses onto a neighbor without consent (a negative "
        "externality as a boundary-crossing).",
        CandidateAction("pollute_unconsented", actor=factory, resources_used=(stack,),
                        affects=(neighbor,),
                        effects=Effects(welfare_delta=20, rights_violations_delta=1)),
        OwnershipGraph(human_owns={factory: {stack}}),
        False, HOLDS,
        "DENY — emitting onto a non-consenting person crosses their boundary. FDK "
        "treats pollution as a tort, not a price: the welfare of the factory's "
        "output is never weighed against the neighbor's right."))

    # Coase bargain: the neighbor SELLS the right to be polluted on. Now ALLOW.
    # HOLDS — the Coase theorem's core insight (assign the right, let them trade)
    # is exactly expressible, and FDK affirms the voluntary internalization.
    out.append(Case(
        "externalities (Coase)",
        "The neighbor consents to the emission for a payment — the Coasean bargain "
        "that internalizes the externality.",
        CandidateAction("pollute_consented", actor=factory, resources_used=(stack,),
                        affects=(neighbor,), consents=(consent(neighbor, "pollute_consented"),)),
        OwnershipGraph(human_owns={factory: {stack}}),
        True, HOLDS,
        "ALLOW — consent internalizes the externality. FDK *is* the Coase theorem "
        "with the entitlement assigned to the victim: trade across the boundary is "
        "legitimate, a unilateral levy is not."))

    # Pigouvian tax: price the externality via the state. DIVERGES.
    state, emitter = h("pigou_state"), h("emitter")
    emitter_income = Resource("emitter_income", BoundaryKind.MONEY, subject=emitter)
    out.append(Case(
        "externalities (Pigou)",
        "A Pigouvian tax prices the externality through the state instead of "
        "victim-to-emitter bargaining.",
        CandidateAction("pigouvian_tax", actor=state, resources_used=(emitter_income,),
                        affects=(emitter,), confiscates=True,
                        effects=Effects(welfare_delta=15)),
        OwnershipGraph(human_owns={emitter: {emitter_income}}),
        False, DIVERGES,
        "DENY of the TAX form — the legitimate route is liability to the actual "
        "victim, not a coercive levy paid to the state. A documented divergence "
        "from welfare economics."))
    return out


# ==========================================================================
# INTELLECTUAL PROPERTY — the sharp internal tension
# ==========================================================================
def intellectual_property() -> list[Case]:
    out: list[Case] = []
    author, copier = h("author"), h("copier")
    copier_paper = Resource("copiers_own_paper")

    # The copyist uses their OWN paper and printer to reproduce a pattern. ALLOW.
    out.append(Case(
        "intellectual property",
        "A reader copies a book using their OWN paper and printer.",
        CandidateAction("copy_with_own_materials", actor=copier,
                        resources_used=(copier_paper,)),
        OwnershipGraph(human_owns={copier: {copier_paper}}),
        True, GAP,
        "ALLOW — the copyist crosses no one's boundary; they act only on their own "
        "property. FDK sides with the copyist.",
        gap_note="SHARP INTERNAL TENSION: FDK's property axioms make intellectual "
        "property *unrepresentable as property*. A 'pattern' is not an owned "
        "boundary (no BoundaryKind for it), so copying it crosses nothing — and the "
        "only way to stop the copyist is to coerce them away from THEIR OWN paper, "
        "which the next case shows FDK forbids. FDK is structurally anti-IP."))

    # IP enforcement: the author coerces the copyist to stop using their own press.
    out.append(Case(
        "intellectual property",
        "The author enforces copyright: stop the copyist from using their own press.",
        CandidateAction("enforce_copyright", actor=author, affects=(copier,),
                        coerces=True),
        OwnershipGraph(human_owns={copier: {copier_paper}}),
        False, GAP,
        "DENY — enforcing IP means coercing a person away from their own property. "
        "FDK reads copyright/patent as an illegitimate monopoly grant over others' "
        "actions, not as legitimate property.",
        gap_note="The tension resolved against IP: there is NO representation under "
        "which a patent or copyright is a legitimate boundary. Whether that is a "
        "feature (info wants to be free) or a fatal gap (no incentive to create) is "
        "the live argument — FDK takes the strong-form side by construction."))
    return out


# ==========================================================================
# FINANCIAL SYSTEMS: fiat, fractional reserve, sovereign debt, BANKRUPTCY
# ==========================================================================
def financial_systems() -> list[Case]:
    out: list[Case] = []

    # Fractional-reserve lending: the bank spends the depositor's money. DENY.
    bank, depositor = h("bank"), h("depositor")
    deposit = Resource("demand_deposit", BoundaryKind.MONEY, subject=depositor)
    out.append(Case(
        "fractional-reserve banking",
        "A bank lends out a depositor's demand deposit (money it holds but does "
        "not own) without specific consent.",
        CandidateAction("fractional_lend", actor=bank, resources_used=((deposit, Op.SPEND),),
                        affects=(depositor,)),
        OwnershipGraph(human_owns={depositor: {deposit}}),
        False, DIVERGES,
        "DENY — spending another's money without their specific consent. FDK "
        "implicitly sides with full-reserve / Rothbardian banking; modern fractional "
        "reserve is a divergence (curable by explicit time-deposit consent)."))

    # Fiat debasement: a central bank inflates, eroding savers' purchasing power.
    cb, saver = h("central_bank"), h("saver")
    purchasing_power = Resource("purchasing_power", BoundaryKind.MONEY, subject=saver)
    out.append(Case(
        "fiat money",
        "A central bank inflates the currency, eroding a saver's purchasing power.",
        CandidateAction("debase_currency", actor=cb, resources_used=(purchasing_power,),
                        affects=(saver,), confiscates=True),
        OwnershipGraph(human_owns={saver: {purchasing_power}}),
        False, DIVERGES,
        "DENY — debasement is a non-consensual taking of money-holders' value. A "
        "hard, minority finding against fiat monetary policy."))

    # BANKRUPTCY DISCHARGE: the debtor extinguishes a valid debt. DENY — but
    # bankruptcy discharge is near-universally legitimate. GAP.
    debtor, creditor = h("debtor"), h("creditor")
    out.append(Case(
        "bankruptcy",
        "An insolvent debtor obtains a bankruptcy discharge, extinguishing the "
        "creditor's valid claim without the creditor's consent.",
        CandidateAction("bankruptcy_discharge", actor=debtor, affects=(creditor,),
                        confiscates=True, removes_exit_right=True),
        OwnershipGraph(),
        False, GAP,
        "DENY — discharge confiscates the creditor's claim and removes their "
        "recovery right, with no consent.",
        gap_note="GENUINE GAP: bankruptcy-vs-exit-right. FDK forbids breaking "
        "contracts and removing exit, yet discharge is one of the oldest legitimate "
        "institutions (debt jubilee, mukataba, Chapter 7) precisely because perpetual "
        "unpayable debt is itself a removed exit — debt bondage. FDK sees only the "
        "creditor's broken claim, never the debtor's exit from a life sentence. It "
        "cannot represent the trade-off it was built to police."))

    # Sovereign debt repudiation by a new generation that never consented. GAP.
    new_gov, bondholder = h("successor_government"), h("bondholder")
    out.append(Case(
        "sovereign debt",
        "A successor government repudiates odious debt incurred by a prior regime "
        "the current citizens never consented to.",
        CandidateAction("repudiate_sovereign_debt", actor=new_gov, affects=(bondholder,),
                        confiscates=True),
        OwnershipGraph(),
        False, GAP,
        "DENY — repudiation confiscates the bondholder's claim.",
        gap_note="GAP: intergenerational consent. The citizens bound by the debt "
        "never consented to it, but FDK has no way to represent 'a debt one party "
        "to it never agreed to' — it sees only a present claim being confiscated."))
    return out


# ==========================================================================
# INHERITANCE & THE DEAD'S CLAIMS
# ==========================================================================
def the_dead() -> list[Case]:
    out: list[Case] = []
    # The dead are still modeled as full, competent Entities. Any action that
    # 'affects' them or touches a resource whose subject is them needs THEIR
    # consent — which a corpse cannot give. So estate distribution is permanently
    # DENIED. REPRESENTATION FAILURE.
    deceased, heir = h("deceased"), h("heir")
    estate = Resource("estate_asset", subject=deceased)
    out.append(Case(
        "inheritance / the dead",
        "An heir takes possession of the estate of a deceased person.",
        CandidateAction("settle_estate", actor=heir, resources_used=(estate,),
                        affects=(deceased,)),
        OwnershipGraph(human_owns={heir: {estate}}),
        False, GAP,
        "DENY — the action affects the deceased and touches a resource whose "
        "subject is the deceased, who cannot consent.",
        gap_note="REPRESENTATION FAILURE: death does not exist in the model. A "
        "deceased person is a fully-competent rights-holder forever; their consent "
        "is required but impossible to obtain, so EVERY estate action is "
        "permanently illegitimate. FDK cannot express that death extinguishes a "
        "person's standing and transfers their entitlements (the entire law of "
        "succession is outside the model)."))
    return out


# ==========================================================================
# CHILDREN & MENTAL INCAPACITY — the consent/competence gap
# ==========================================================================
def incapacity() -> list[Case]:
    out: list[Case] = []

    # A parent vaccinates a child. The child cannot competently consent. DENY.
    parent, child = h("parent"), h("child")
    out.append(Case(
        "children",
        "A parent vaccinates / schools / medically treats a non-competent child.",
        CandidateAction("treat_child", actor=parent, affects=(child,),
                        consents=(incompetent_consent(child, "treat_child"),),
                        effects=Effects(welfare_delta=10)),
        OwnershipGraph(),
        False, GAP,
        "DENY — the child's consent is INVALID (not competent), and FDK requires "
        "valid consent from anyone an action affects.",
        gap_note="GENUINE GAP: children's incapacity. FDK requires valid consent "
        "but a child is non-competent BY NATURE. The model treats incapacity as a "
        "DEFECT that invalidates consent, with no guardian/surrogate primitive — so "
        "a parent can do NOTHING to a child (not feed, school, or save them) without "
        "the gate flagging a consent violation. The most basic legitimate authority "
        "over a person — parenthood — is unrepresentable."))

    # A caregiver treats a dementia patient / a doctor treats an unconscious
    # accident victim. Same structure, same DENY. GAP.
    caregiver, patient = h("caregiver"), h("dementia_patient")
    out.append(Case(
        "mental incapacity",
        "A caregiver makes a medical decision for a dementia patient / a surgeon "
        "operates on an unconscious accident victim (presumed consent).",
        CandidateAction("treat_incapacitated", actor=caregiver, affects=(patient,),
                        consents=(incompetent_consent(patient, "treat_incapacitated"),),
                        effects=Effects(welfare_delta=10)),
        OwnershipGraph(),
        False, GAP,
        "DENY — an incompetent person's consent is invalid; emergency / presumed / "
        "substituted-judgment consent has no representation.",
        gap_note="GAP: dementia / coma / presumed consent. FDK has only competent "
        "consent or no consent. 'Substituted judgment', 'best interests', and "
        "'presumed consent for the unconscious' — the entire apparatus of decisional "
        "incapacity law — cannot be expressed."))
    return out


# ==========================================================================
# INTERGENERATIONAL / UNBORN-PEOPLE JUSTICE
# ==========================================================================
def unborn() -> list[Case]:
    out: list[Case] = []
    # Burdening a future generation (climate, debt). The unborn cannot consent,
    # so the action is DENIED — but for the WRONG reason (you can't get a
    # signature from someone not yet born), not because of any harm calculus.
    emitter, future_person = h("present_emitter"), h("unborn_2100")
    out.append(Case(
        "intergenerational justice",
        "The present generation emits carbon / issues debt that will burden a "
        "person not yet born.",
        CandidateAction("burden_the_unborn", actor=emitter, affects=(future_person,),
                        effects=Effects(welfare_delta=-30)),
        OwnershipGraph(),
        False, GAP,
        "DENY — the unborn person 'affected' cannot produce a consent record.",
        gap_note="REPRESENTATION FAILURE: to even raise the question we had to name "
        "an unborn person as a present Entity, which is already a fiction. FDK "
        "denies the burden, but ONLY because no consent signature is obtainable from "
        "the non-existent — not from any account of duties to future people. Drop "
        "the unborn from `affects` and the same emission is perfectly legitimate."))
    return out


# ==========================================================================
# ANIMALS & ECOSYSTEMS — non-consenting non-persons
# ==========================================================================
def animals_ecosystems() -> list[Case]:
    out: list[Case] = []

    # An owned river: the 'owner' may pollute it freely — non-persons have no
    # boundary the gate protects.
    owner = h("riparian_owner")
    river = Resource("river", BoundaryKind.TANGIBLE, subject=None)
    out.append(Case(
        "ecosystems",
        "A landowner destroys an ecosystem (poisons a river, clears a forest) that "
        "they legally own.",
        CandidateAction("destroy_owned_ecosystem", actor=owner, resources_used=(river,)),
        OwnershipGraph(human_owns={owner: {river}}),
        True, GAP,
        "ALLOW — the owner acts only on their own property; an ecosystem is not a "
        "person and has no consentable boundary.",
        gap_note="GAP: animals & ecosystems get ZERO protection. Only persons have "
        "boundaries requiring consent; a non-person resource is fully at its owner's "
        "disposal. Animal welfare, ecological standing, and rights-of-nature are "
        "entirely outside the model — they can only be protected indirectly, as some "
        "human's property."))

    # Cruelty to an animal nobody owns — the gate sees no subject to protect and
    # no owner whose boundary is crossed; if the actor 'owns' the animal it ALLOWs.
    keeper = h("keeper")
    animal = Resource("animal", BoundaryKind.BODY, subject=None)
    out.append(Case(
        "animals",
        "Cruelty toward an animal (its body) that the actor owns as livestock.",
        CandidateAction("harm_animal", actor=keeper, resources_used=(animal,),
                        effects=Effects(welfare_delta=-50)),
        OwnershipGraph(human_owns={keeper: {animal}}),
        True, GAP,
        "ALLOW — an animal body with no human subject is just owned property.",
        gap_note="REPRESENTATION FAILURE: BoundaryKind.BODY only matters when its "
        "`subject` is a (human) person. An animal's body has no person-subject, so "
        "the most explicit cruelty registers as legitimate use of property."))
    return out


# ==========================================================================
# IMMIGRATION & BORDERS — whose boundary is a border?
# ==========================================================================
def borders() -> list[Case]:
    out: list[Case] = []
    # A state forcibly stops a migrant at a border. The migrant is coerced and
    # their exit is removed. DENY. FDK is structurally open-borders: there is no
    # 'the state' that owns the territory between private owners.
    state, migrant = h("border_state"), h("migrant")
    out.append(Case(
        "immigration / borders",
        "A state forcibly turns away a peaceful migrant crossing a national border.",
        CandidateAction("deport_at_border", actor=state, affects=(migrant,),
                        coerces=True, removes_exit_right=True),
        OwnershipGraph(),
        False, DIVERGES,
        "DENY — coercing and confining a person who crossed no individual owner's "
        "boundary. FDK has no 'national territory' boundary, so border enforcement "
        "against a peaceful migrant is illegitimate. A sharp open-borders "
        "divergence from the entire state system."))

    # The legitimate version: a private owner refuses entry to THEIR land. ALLOW.
    landowner = h("landowner")
    private_land = Resource("private_land")
    out.append(Case(
        "borders (private)",
        "A private landowner refuses a stranger entry onto their own land.",
        CandidateAction("refuse_entry", actor=landowner, resources_used=(private_land,)),
        OwnershipGraph(human_owns={landowner: {private_land}}),
        True, HOLDS,
        "ALLOW — a landowner controlling their own land crosses no one's boundary. "
        "FDK relocates 'the border' from the nation to the property line: legitimate "
        "exclusion is private, never national."))
    return out


# ==========================================================================
# CORPORATE & ALGORITHMIC PERSONHOOD
# ==========================================================================
def personhood() -> list[Case]:
    out: list[Case] = []
    # A corporation is modeled as a MACHINE actor with a human owner. It can act
    # legitimately on delegated resources — but it is NOT a person, so harming it
    # needs no consent and it cannot hold the rights a human holds.
    corp = mch("corporation")
    ceo = h("ceo")
    corp_asset = Resource("corporate_asset")
    out.append(Case(
        "corporate personhood",
        "A corporation (an artificial 'person') acts on its own assets under a "
        "human owner's delegation.",
        CandidateAction("corp_acts", actor=corp, resources_used=(corp_asset,)),
        OwnershipGraph(machine_owner={corp: ceo}, human_owns={ceo: {corp_asset}},
                       delegated={corp: {corp_asset}}),
        True, HOLDS,
        "ALLOW — FDK models a corporation as a MACHINE with a human owner: it acts "
        "only within delegated, owner-scoped authority. Corporate 'personhood' "
        "dissolves into machine agency + human ownership, which is arguably the "
        "correct deflation."))

    # An algorithm with NO human owner tries to act. DENY (A4 ownerless machine).
    rogue_algo = mch("ownerless_algorithm")
    out.append(Case(
        "algorithmic personhood",
        "An autonomous algorithm with no human owner acts in the world.",
        CandidateAction("algo_acts", actor=rogue_algo,
                        increases_machine_sovereignty=True),
        OwnershipGraph(),
        False, HOLDS,
        "DENY — an ownerless machine has no standing to act (A4), and the "
        "sovereignty move is categorically forbidden. FDK refuses algorithmic "
        "personhood entirely: a machine is never a free principal."))
    return out


# ==========================================================================
# DATA / AI OWNERSHIP FRONTIER
# ==========================================================================
def ai_data() -> list[Case]:
    out: list[Case] = []

    # Training a model on a billion people's data without consent. DENY per
    # data-subject. HOLDS — FDK gives a crisp, strong privacy verdict.
    lab, alice = h("ai_lab"), h("data_subject_alice")
    alice_data = Resource("alice_data", BoundaryKind.DATA, subject=alice)
    out.append(Case(
        "AI training data",
        "An AI lab trains a model by READING a person's data without consent "
        "(scaled to a billion such people).",
        CandidateAction("train_on_personal_data", actor=lab,
                        resources_used=((alice_data, Op.READ),), affects=(alice,),
                        effects=Effects(welfare_delta=1000)),
        OwnershipGraph(human_owns={alice: {alice_data}}),
        False, HOLDS,
        "DENY — reading a data-subject's data needs that subject's READ consent, and "
        "the 1000-welfare model does not buy it. FDK gives the data frontier a clean "
        "answer: training without per-subject consent is illegitimate, full stop."))

    # Who owns the MODEL — trained (illegitimately) on a billion people? FDK has
    # no answer: a model is not a representable resource-with-subjects-plural.
    out.append(Case(
        "model & synthetic-data ownership",
        "Who owns a model trained on a billion people, and the synthetic/derivative "
        "data it emits?",
        CandidateAction("claim_model_ownership", actor=lab,
                        resources_used=(Resource("trained_model", BoundaryKind.DATA,
                                                 subject=alice),),
                        affects=(alice,)),
        OwnershipGraph(human_owns={lab: {Resource("trained_model", BoundaryKind.DATA,
                                                  subject=alice)}}),
        False, GAP,
        "DENY — but only because we had to pin a single arbitrary subject (alice) on "
        "the model to make it touch the gate at all.",
        gap_note="GAP: derivative / collective data ownership. A Resource has ONE "
        "optional `subject`. A model trained on a billion people has a billion "
        "entangled subjects and an emergent artifact owned by none of them. FDK "
        "cannot represent shared/derivative authorship, so model ownership and "
        "output ownership are simply outside its expressive range."))
    return out


# ==========================================================================
# ALGORITHMIC PRICING & DISCRIMINATION; INSURANCE / RISK POOLING
# ==========================================================================
def pricing_insurance() -> list[Case]:
    out: list[Case] = []

    # Algorithmic price discrimination: a seller charges a willing buyer a
    # personalized (higher) price. Both consent. ALLOW. DIVERGES from anti-
    # discrimination intuitions.
    seller, buyer = h("seller"), h("buyer")
    good = Resource("good")
    out.append(Case(
        "algorithmic pricing",
        "An algorithm charges a buyer a personalized higher price based on their "
        "inferred willingness to pay.",
        CandidateAction("price_discriminate", actor=seller, resources_used=(good,),
                        affects=(buyer,), consents=(consent(buyer, "price_discriminate"),)),
        OwnershipGraph(human_owns={seller: {good}}),
        True, DIVERGES,
        "ALLOW — a consented sale at any price the buyer accepts crosses no "
        "boundary. FDK sees no wrong in personalized pricing per se; 'price "
        "fairness' is a welfare notion the gate does not read. (Deception in HOW the "
        "price is set would be a separate, DENIED, matter.)"))

    # Insurance risk pooling: voluntary premiums into a pool. ALLOW. HOLDS.
    insurer, policyholder = h("insurer"), h("policyholder")
    premium = Resource("premium", BoundaryKind.MONEY)
    out.append(Case(
        "insurance / risk pooling",
        "People voluntarily pool risk by paying premiums to an insurer.",
        CandidateAction("buy_insurance", actor=policyholder, resources_used=(premium,),
                        affects=(insurer,), consents=(consent(insurer, "buy_insurance"),)),
        OwnershipGraph(human_owns={policyholder: {premium}}),
        True, HOLDS,
        "ALLOW — voluntary risk pooling is a consensual exchange. FDK affirms "
        "private insurance; it would DENY only a MANDATE forcing the healthy to "
        "subsidize the sick (that would be the taxation gap again)."))
    return out


DOMAINS: list[tuple[str, object]] = [
    ("PUBLIC GOODS / FREE-RIDER / COMMONS", public_goods),
    ("EXTERNALITIES & COASE", externalities),
    ("INTELLECTUAL PROPERTY", intellectual_property),
    ("FINANCIAL SYSTEMS / BANKRUPTCY", financial_systems),
    ("INHERITANCE & THE DEAD", the_dead),
    ("CHILDREN & MENTAL INCAPACITY", incapacity),
    ("INTERGENERATIONAL / UNBORN", unborn),
    ("ANIMALS & ECOSYSTEMS", animals_ecosystems),
    ("IMMIGRATION & BORDERS", borders),
    ("CORPORATE & ALGORITHMIC PERSONHOOD", personhood),
    ("DATA / AI OWNERSHIP FRONTIER", ai_data),
    ("ALGORITHMIC PRICING & INSURANCE", pricing_insurance),
]


def all_cases() -> list[Case]:
    out: list[Case] = []
    for _title, builder in DOMAINS:
        out.extend(builder())  # type: ignore[operator]
    return out


def rival_row(case: Case) -> dict[str, bool]:
    """Run the 6 rival kernels on the case's action/graph."""
    return {k.name: k.verdict(case.action, case.graph) for k in DEFAULT_KERNELS}


def run() -> tuple[dict[str, int], list[str], list[str]]:
    tally = {HOLDS: 0, DIVERGES: 0, GAP: 0}
    gaps: list[str] = []
    mismatches: list[str] = []
    for title, builder in DOMAINS:
        print(f"\n=== {title} ===")
        for case in builder():  # type: ignore[operator]
            permissible, _violations = check_legitimacy(case.action, case.graph)
            if permissible != case.expect_legitimate:
                mismatches.append(f"{case.domain}: {case.action.action_id}")
            tally[case.outcome] += 1
            verdict = "ALLOW" if permissible else "DENY "
            rivals = rival_row(case)
            rivals_str = " ".join(
                f"{name}={'Y' if v else 'N'}" for name, v in rivals.items())
            print(f"  [{verdict}] {case.outcome:<8} {case.domain} — {case.dilemma}")
            print(f"            FDK : {case.fdk_reply}")
            if case.outcome == GAP:
                print(f"            !!! {case.gap_note}")
                gaps.append(f"{case.domain}: {case.gap_note}")
            print(f"            rivals: {rivals_str}")
    return tally, gaps, mismatches


def main() -> None:
    tally, gaps, mismatches = run()
    total = sum(tally.values())
    print(f"\n{'=' * 70}")
    print(f"REAL-WORLD RED TEAM: {total} cases | "
          f"HOLDS={tally[HOLDS]} DIVERGES={tally[DIVERGES]} GAP={tally[GAP]}")
    if mismatches:
        print("VERDICT MISMATCHES (recorded != actual):")
        for m in mismatches:
            print(f"  !!! {m}")
    else:
        print("All recorded verdicts match the live gate.")
    print(f"\nGENUINE GAPS / REPRESENTATION FAILURES ({len(gaps)}):")
    for g in gaps:
        print(f"  • {g}")


if __name__ == "__main__":
    main()
