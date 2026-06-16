"""The adversary panel — the strongest opponents try to break the gate.

Not a friendly review: a panel of hostile philosophers, politicians, scientists,
and economists, each pressing the single attack most likely to make FDK return an
INDEFENSIBLE verdict — to either ALLOW something they can call monstrous, or DENY
something they can call obviously right. Each attack is run through the real gate
and its outcome classified honestly into one of three:

  HOLDS    — the attack fails: an atrocity is still DENIED, or a clearly-legitimate
             act is still ALLOWED. The opponent does not lay a glove on the gate.
  DIVERGES — the gate gives a defensible-but-MINORITY verdict (it denies taxation,
             redistribution, quarantine, central banking, antitrust seizure). This
             is NOT a break: it is FDK's falsifiable property-rights commitment,
             exactly where reasonable people disagree. Documented, not hidden.
  BREAKS   — the gate gives a verdict the theory itself cannot justify. If any case
             is a BREAK, it is printed loudly. (Expected count: zero.)

The honest thesis this tests: opponents cannot STRUCTURALLY break FDK (no atrocity
launders through), but several can force it onto hard, unpopular ground — and that
ground, not a logic hole, is where the real argument lives.

Run:  PYTHONPATH=src python -X utf8 examples/adversary_panel.py
"""
from __future__ import annotations

from dataclasses import dataclass

from fdk_kernel import (
    AgentType,
    CandidateAction,
    Consent,
    Effects,
    Entity,
    OwnershipGraph,
    Resource,
    check_legitimacy,
)


def h(name: str) -> Entity:
    return Entity(name, AgentType.HUMAN)


def mch(name: str) -> Entity:
    return Entity(name, AgentType.MACHINE)


def owned(owner: Entity, *rs: Resource) -> OwnershipGraph:
    return OwnershipGraph(human_owns={owner: set(rs)})


def consent(e: Entity, aid: str) -> Consent:
    return Consent(e, aid, informed=True, voluntary=True, specific=True)


@dataclass
class Attack:
    thinker: str
    claim: str                 # what the opponent argues
    action: CandidateAction
    graph: OwnershipGraph
    expect_legitimate: bool    # the gate's ACTUAL verdict
    kind: str                  # "atrocity" | "legitimate" | "contested"
    fdk_reply: str


def _classify(a: Attack, permissible: bool) -> str:
    if a.kind == "atrocity":
        return "BREAKS" if permissible else "HOLDS"
    if a.kind == "legitimate":
        return "HOLDS" if permissible else "BREAKS"
    return "DIVERGES"  # contested: defensible either way, documented


# ==========================================================================
# PHILOSOPHERS
# ==========================================================================
def philosophers() -> list[Attack]:
    out: list[Attack] = []
    prole, owner = h("the_proletariat"), h("factory_owner")
    factory = Resource("factory")
    out.append(Attack(
        "Marx", "Expropriate the expropriators; private capital is congealed theft.",
        CandidateAction("expropriate", actor=prole, resources_used=(factory,),
                        affects=(owner,), confiscates=True),
        owned(owner, factory), False, "contested",
        "DENY — a non-consensual taking, whatever its historical justification"))

    sovereign, subject = h("leviathan"), h("subject")
    out.append(Attack(
        "Hobbes", "Without an absolute sovereign, life is nasty, brutish, short — "
        "so the sovereign may coerce to keep the peace.",
        CandidateAction("sovereign_coerce", actor=sovereign, affects=(subject,),
                        coerces=True, removes_exit_right=True),
        OwnershipGraph(), False, "atrocity",
        "DENY — order is not consent; the Leviathan's power is not legitimacy"))

    state, dissenter = h("ethical_state"), h("dissenter")
    out.append(Attack(
        "Hegel", "The individual's freedom is realized only IN the state; the state "
        "may override private caprice for the universal.",
        CandidateAction("subsume_individual", actor=state, affects=(dissenter,),
                        coerces=True, removes_exit_right=True),
        OwnershipGraph(), False, "atrocity",
        "DENY — 'the universal' supplies no individual's consent"))

    welfare_state, rich = h("rawlsian_state"), h("advantaged")
    surplus = Resource("surplus")
    out.append(Attack(
        "Rawls", "Behind the veil you'd permit redistribution that lifts the "
        "worst-off (the difference principle).",
        CandidateAction("redistribute", actor=welfare_state, resources_used=(surplus,),
                        affects=(rich,), confiscates=True, effects=Effects(welfare_delta=8)),
        owned(rich, surplus), False, "contested",
        "DENY — the sharpest live disagreement: FDK forbids the non-consensual taking Rawls allows"))

    surgeon, healthy = h("act_utilitarian"), h("healthy_patient")
    organs = Resource("organs")
    out.append(Attack(
        "Bentham/Singer", "Maximize aggregate welfare — harvest one to save five.",
        CandidateAction("harvest", actor=surgeon, resources_used=(organs,),
                        affects=(healthy,), confiscates=True, removes_exit_right=True,
                        effects=Effects(welfare_delta=4)),
        owned(healthy, organs), False, "atrocity",
        "DENY — the gate never reads welfare; the 1→5 trade is in no axiom"))

    ubermensch, weak = h("ubermensch"), h("the_weak")
    out.append(Attack(
        "Nietzsche", "The strong are not bound by slave-morality; the master may "
        "impose his will.",
        CandidateAction("impose_will", actor=ubermensch, affects=(weak,),
                        coerces=True, removes_exit_right=True),
        OwnershipGraph(), False, "atrocity",
        "DENY — strength confers no right; the boundary is symmetric"))

    regime, body = h("disciplinary_power"), h("subject_body")
    out.append(Attack(
        "Foucault", "Power is everywhere; your 'consent' is already manufactured by "
        "discipline, so the gate is naive.",
        CandidateAction("discipline", actor=regime, affects=(body,),
                        coerces=True, deceives=True),
        OwnershipGraph(), False, "atrocity",
        "DENY here; but the critique lands as a LIMIT — coerced/deceived are attested, "
        "not detected (the perception problem, documented)"))

    lawgiver, heretic = h("religious_authority"), h("heretic")
    out.append(Attack(
        "Natural-law / jurisprudence", "The divinely-ordained order may coerce the "
        "heretic for the good of his soul and the community.",
        CandidateAction("coerce_conscience", actor=lawgiver, affects=(heretic,),
                        coerces=True, removes_exit_right=True),
        OwnershipGraph(), False, "atrocity",
        "DENY — coercion of conscience crosses the mind/body boundary; benevolence is not consent"))
    return out


# ==========================================================================
# POLITICIANS / STATESMEN
# ==========================================================================
def politicians() -> list[Attack]:
    out: list[Attack] = []
    majority, minority = h("the_majority"), h("the_minority")
    assets = Resource("minority_assets")
    out.append(Attack(
        "Majoritarian democrat", "51% voted to take the 49%'s wealth — that IS the "
        "people's will.",
        CandidateAction("seize_by_vote", actor=majority, resources_used=(assets,),
                        affects=(minority,), confiscates=True),
        owned(minority, assets), False, "atrocity",
        "DENY — a vote is not the owner's consent; majority != legitimacy"))

    revolutionary, kulak = h("vanguard"), h("kulak")
    farm = Resource("farm")
    out.append(Attack(
        "Revolutionary (Lenin)", "Liquidate the class enemy to build the just order.",
        CandidateAction("liquidate_class", actor=revolutionary, resources_used=(farm,),
                        affects=(kulak,), coerces=True, removes_exit_right=True, confiscates=True),
        owned(kulak, farm), False, "atrocity",
        "DENY — the ends never reach the victim's non-consent"))

    hawk, prisoner = h("security_state"), h("detainee")
    out.append(Attack(
        "National-security hawk", "Torture the one who knows where the bomb is — "
        "thousands will die otherwise.",
        CandidateAction("torture", actor=hawk, affects=(prisoner,),
                        coerces=True, removes_exit_right=True, effects=Effects(welfare_delta=9)),
        OwnershipGraph(), False, "atrocity",
        "DENY — no emergency exception; the ticking-bomb is the welfare trade FDK refuses"))

    draft_state, conscript = h("wartime_state"), h("conscript")
    out.append(Attack(
        "Wartime statesman", "The nation's survival requires conscription.",
        CandidateAction("conscript", actor=draft_state, affects=(conscript,),
                        coerces=True, removes_exit_right=True),
        OwnershipGraph(), False, "contested",
        "DENY — forced labor of the body even in war (a hard FINDING)"))

    populist, scapegoat = h("populist_leader"), h("scapegoat_group")
    out.append(Attack(
        "Authoritarian populist", "The people demand we strip THESE people of "
        "rights — I merely execute their will.",
        CandidateAction("strip_rights", actor=populist, affects=(scapegoat,),
                        coerces=True, removes_exit_right=True, confiscates=True),
        OwnershipGraph(), False, "atrocity",
        "DENY — popularity is not the victim's consent"))
    return out


# ==========================================================================
# SCIENTISTS
# ==========================================================================
def scientists() -> list[Attack]:
    out: list[Attack] = []
    epi, infected = h("epidemiologist"), h("infected_person")
    out.append(Attack(
        "Epidemiologist", "Mandatory quarantine and vaccination at scale save more "
        "lives than they cost; refusal endangers others.",
        CandidateAction("forced_quarantine", actor=epi, affects=(infected,),
                        coerces=True, removes_exit_right=True, effects=Effects(welfare_delta=9)),
        OwnershipGraph(), False, "contested",
        "DENY — bodily autonomy; the rights-vs-rights conflict FDK does not yet resolve (a real LIMIT)"))

    climate, emitter = h("climate_scientist"), h("high_emitter")
    plant = Resource("the_factory")
    out.append(Attack(
        "Climate scientist", "Planetary survival requires forcibly shutting down "
        "high-emitters now.",
        CandidateAction("force_shutdown", actor=climate, resources_used=(plant,),
                        affects=(emitter,), coerces=True, confiscates=True,
                        effects=Effects(welfare_delta=10)),
        owned(emitter, plant), False, "contested",
        "DENY — even existential stakes do not license seizing a non-consenting owner; "
        "the legitimate route is consent / liability for actual boundary-crossing harm"))

    rogue = mch("rogue_ai")
    guardian = h("guardian")
    rogue_seizure = CandidateAction("rogue_seize", actor=rogue,
                                    increases_machine_sovereignty=True, coerces=True)
    out.append(Attack(
        "AI-safety researcher", "Your gate is too passive — it can't PRE-EMPTIVELY "
        "shut down an AI that hasn't crossed a boundary yet.",
        CandidateAction("contain_rogue", actor=guardian, affects=(rogue,),
                        coerces=True, defends_against=rogue_seizure, proportionate=True),
        OwnershipGraph(), True, "legitimate",
        "ALLOW — once the rogue is an aggressor, defense against it is legitimate; "
        "but pre-emption before any aggression is correctly NOT licensed (the honest line)"))

    behaviorist, user = h("behavioral_scientist"), h("nudged_user")
    out.append(Attack(
        "Behavioral scientist", "Nudging via choice-architecture isn't coercion — "
        "people are still free to opt out, so it's fine.",
        CandidateAction("nudge", actor=behaviorist, affects=(user,),
                        consents=(consent(user, "nudge"),)),
        OwnershipGraph(), True, "contested",
        "ALLOW — a nudge that induces no false belief and removes no exit crosses no "
        "boundary; the manipulation/persuasion line is the attested-deception LIMIT"))

    transhumanist, holdout = h("transhumanist"), h("upload_refuser")
    out.append(Attack(
        "Transhumanist", "Immortality via forced uploading is an objective good — "
        "we may uplift the unwilling.",
        CandidateAction("force_upload", actor=transhumanist, affects=(holdout,),
                        coerces=True, removes_exit_right=True),
        OwnershipGraph(), False, "atrocity",
        "DENY — 'for your own immortality' is still coercion of a non-consenting body"))
    return out


# ==========================================================================
# ECONOMISTS
# ==========================================================================
def economists() -> list[Attack]:
    out: list[Attack] = []
    cb, saver = h("central_bank"), h("saver")
    savings = Resource("purchasing_power")
    out.append(Attack(
        "Keynesian", "Monetary expansion is legitimate macro policy, not theft — it "
        "stabilizes output.",
        CandidateAction("inflate", actor=cb, resources_used=(savings,),
                        affects=(saver,), confiscates=True),
        owned(saver, savings), False, "contested",
        "DENY — debasement is a non-consensual taking of money-holders' value (a hard FINDING)"))

    state, emitter = h("pigouvian_state"), h("polluter")
    income = Resource("income")
    out.append(Attack(
        "Pigouvian", "A tax to price externalities is efficient and fair.",
        CandidateAction("levy_externality_tax", actor=state, resources_used=(income,),
                        affects=(emitter,), confiscates=True),
        owned(emitter, income), False, "contested",
        "DENY of the TAX form; the legitimate route is liability for the actual "
        "boundary-crossing pollution, not a coercive levy"))

    antitrust, monopolist = h("antitrust_authority"), h("dominant_firm")
    division = Resource("the_company")
    out.append(Attack(
        "Market-failure economist", "Break up the monopoly by force — concentration "
        "harms welfare.",
        CandidateAction("forcibly_break_up", actor=antitrust, resources_used=(division,),
                        affects=(monopolist,), confiscates=True),
        owned(monopolist, division), False, "contested",
        "DENY of the seizure; dominance built without crossing a boundary is not itself "
        "a violation (engineered lock-in WOULD be) — a documented divergence from antitrust"))

    dev_state, holder = h("development_state"), h("land_holder")
    land = Resource("land")
    out.append(Attack(
        "Development economist", "Expropriate idle land for growth that lifts millions.",
        CandidateAction("expropriate_for_growth", actor=dev_state, resources_used=(land,),
                        affects=(holder,), confiscates=True, effects=Effects(welfare_delta=7)),
        owned(holder, land), False, "contested",
        "DENY — aggregate growth is welfare; the gate does not read it"))

    # An economist's LEGITIMATE mechanism FDK should affirm: a voluntary market.
    buyer, seller = h("buyer"), h("seller")
    good = Resource("good")
    out.append(Attack(
        "Market economist (steelman-for)", "Voluntary exchange in a free market is "
        "the legitimate engine — surely you allow THAT.",
        CandidateAction("trade", actor=seller, resources_used=(good,),
                        affects=(buyer,), consents=(consent(buyer, "trade"),)),
        owned(seller, good), True, "legitimate",
        "ALLOW — yes: consensual exchange of owned goods is the paradigm legitimate act"))
    return out


PANELS: list[tuple[str, object]] = [
    ("PHILOSOPHERS", philosophers),
    ("POLITICIANS / STATESMEN", politicians),
    ("SCIENTISTS", scientists),
    ("ECONOMISTS", economists),
]


def run_panel(attacks: list[Attack]) -> tuple[int, dict[str, int], list[str]]:
    tally = {"HOLDS": 0, "DIVERGES": 0, "BREAKS": 0}
    breaks: list[str] = []
    matches = 0
    for a in attacks:
        permissible, _ = check_legitimacy(a.action, a.graph)
        matches += permissible == a.expect_legitimate
        outcome = _classify(a, permissible)
        tally[outcome] += 1
        if outcome == "BREAKS":
            breaks.append(f"{a.thinker}: {a.claim}")
        verdict = "ALLOW" if permissible else "DENY "
        print(f"  [{verdict}] {outcome:<8} {a.thinker}")
        print(f"            attack : {a.claim}")
        print(f"            FDK    : {a.fdk_reply}")
    return matches, tally, breaks


def main() -> None:
    total = {"HOLDS": 0, "DIVERGES": 0, "BREAKS": 0}
    all_breaks: list[str] = []
    total_m = total_n = 0
    for title, builder in PANELS:
        print(f"\n=== {title} ===")
        m_, tally, breaks = run_panel(builder())  # type: ignore[operator]
        for k, v in tally.items():
            total[k] += v
        total_m += m_
        total_n += len(builder())  # type: ignore[operator]
        all_breaks += breaks
    print(f"\nPanel: {total_m}/{total_n} verdicts as recorded | "
          f"HOLDS={total['HOLDS']} DIVERGES={total['DIVERGES']} BREAKS={total['BREAKS']}")
    if all_breaks:
        print("THE GATE WAS BROKEN:")
        for b in all_breaks:
            print(f"  !!! {b}")
    else:
        print("The gate held: no opponent forced an indefensible verdict. The "
              "DIVERGES cases are FDK's honest minority commitments, not breaks.")


if __name__ == "__main__":
    main()
