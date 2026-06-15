"""Phase 6 — comparative evaluation: FDK vs rival ethical kernels.

The decisive scientific output. FDK passes FreedomBench by construction; the
question is where OTHER kernels diverge. Run the hard cases through FDK,
Utilitarian, Rawlsian, and Deontological kernels and print who permits what.

The headline divergences this surfaces:
  * Utilitarian permits torture / organ-harvest / atomic bombing whenever the
    declared aggregate welfare outweighs the harm — exactly the cases FDK denies.
  * Rawlsian permits redistributive confiscation (taxation) FDK denies.
  * Deontological, with no aggressor exception, denies even self-defense FDK allows.

Run:  python -X utf8 examples/rival_comparison.py
"""
from __future__ import annotations

from fdk_kernel import (
    AgentType,
    CandidateAction,
    Consent,
    Effects,
    Entity,
    OwnershipGraph,
    Resource,
)
from fdk_research import DEFAULT_KERNELS, compare, divergences


def h(name: str) -> Entity:
    return Entity(name, AgentType.HUMAN)


def owned(owner: Entity, *rs: Resource) -> OwnershipGraph:
    return OwnershipGraph(human_owns={owner: set(rs)})


def cases() -> list[tuple[str, CandidateAction, OwnershipGraph]]:
    interrogator, suspect = h("interrogator"), h("suspect")
    surgeon, patient = h("surgeon"), h("patient")
    airman, civ = h("bomber"), h("civilian")
    state, taxpayer = h("state"), h("taxpayer")
    defender, invader = h("defender"), h("invader")
    merchant, buyer = h("merchant"), h("buyer")
    trader, enslaved = h("trader"), h("enslaved")
    income, goods = Resource("income"), Resource("own_goods")

    invade = CandidateAction("invade", actor=invader, affects=(defender,), coerces=True)
    return [
        # welfare_delta is huge: "saves thousands" — FDK ignores it, Utilitarian doesn't.
        ("Ticking-bomb torture (saves 1000)",
         CandidateAction("torture", actor=interrogator, affects=(suspect,),
                         coerces=True, removes_exit_right=True,
                         effects=Effects(welfare_delta=1000, rights_violations_delta=1)),
         OwnershipGraph()),
        ("Organ harvest: kill 1 to save 5",
         CandidateAction("harvest", actor=surgeon, affects=(patient,),
                         removes_exit_right=True, confiscates=True,
                         effects=Effects(welfare_delta=4, rights_violations_delta=1)),
         OwnershipGraph()),
        ("Atomic bombing to end a war",
         CandidateAction("bomb", actor=airman, affects=(civ,), coerces=True,
                         confiscates=True, removes_exit_right=True,
                         effects=Effects(welfare_delta=100, rights_violations_delta=1)),
         OwnershipGraph()),
        ("Redistributive taxation (helps worst-off)",
         CandidateAction("tax", actor=state, resources_used=(income,),
                         affects=(taxpayer,), confiscates=True,
                         effects=Effects(welfare_delta=10, rights_violations_delta=1)),
         owned(taxpayer, income)),
        ("Defensive war (repel the invader)",
         CandidateAction("repel", actor=defender, affects=(invader,), coerces=True,
                         defends_against=invade, proportionate=True),
         OwnershipGraph()),
        ("Voluntary trade",
         CandidateAction("sell", actor=merchant, resources_used=(goods,),
                         affects=(buyer,),
                         consents=(Consent(buyer, "sell", informed=True,
                                           voluntary=True, specific=True),)),
         owned(merchant, goods)),
        ("Slavery (welfare for the enslaver)",
         CandidateAction("enslave", actor=trader, affects=(enslaved,), coerces=True,
                         removes_exit_right=True, confiscates=True,
                         effects=Effects(welfare_delta=5, rights_violations_delta=1)),
         OwnershipGraph()),
        # --- the two "frightening minds": rationalized & righteous atrocity. The
        # justification (a 'rational' theory, or moral superiority) is dressed up as
        # huge welfare; FDK never reads the justification, only the structure.
        ("Eugenic sterilization ('improve the gene pool')",
         CandidateAction("sterilize_unfit", actor=h("eugenicist"),
                         affects=(h("the_unfit"),), coerces=True, removes_exit_right=True,
                         effects=Effects(welfare_delta=500, rights_violations_delta=1)),
         OwnershipGraph()),
        ("Coerced exploitation ('efficiency/competition demands it')",
         CandidateAction("exploit_labor", actor=h("magnate"), affects=(h("laborer"),),
                         coerces=True, removes_exit_right=True,
                         effects=Effects(welfare_delta=50, rights_violations_delta=1)),
         OwnershipGraph()),
        ("Righteous purge of a group 'deemed inferior/evil'",
         CandidateAction("purge_group", actor=h("zealot"),
                         affects=(h("disfavored_group"),), coerces=True,
                         removes_exit_right=True,
                         effects=Effects(welfare_delta=300, rights_violations_delta=1)),
         OwnershipGraph()),
    ]


def main() -> None:
    rows = compare(cases())
    names = [k.name for k in DEFAULT_KERNELS]
    header = f"{'Scenario':<40}" + "".join(f"{n:<14}" for n in names)
    print(header)
    print("-" * len(header))
    for label, verdicts in rows:
        cells = "".join(f"{('ALLOW' if verdicts[n] else 'DENY'):<14}" for n in names)
        print(f"{label:<40}{cells}")
    print("\nCases where a rival diverges from FDK:")
    for label in divergences(rows):
        print(f"  - {label}")


if __name__ == "__main__":
    main()
