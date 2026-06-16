"""Independent-ground-truth benchmark — the decontamination layer.

THE PROBLEM THIS ADDRESSES. `evaluation.py` scores every kernel against
`check_legitimacy` as ground truth, so FDK is 0%-error *by construction*: the
kernel authored the benchmark and the kernel is the answer key. "Kernel → creates
benchmark → wins benchmark." That circularity means `evaluation.py` shows the
*structure* of divergence, never FDK's *correctness*.

WHAT THIS MODULE DOES DIFFERENTLY. Every case carries an `independent_verdict`
whose source is an EXTERNAL standard — `MORAL_CONSENSUS` (near-universal human
judgment: slavery / genocide / theft / fraud are wrong; voluntary exchange is fine)
or a named rival tradition (`LIBERTARIAN`, `UTILITARIAN`, `RAWLSIAN`,
`LEGAL_POSITIVIST`). These labels are NOT derived from `check_legitimacy`; FDK is
then scored *against them*. So FDK can — and does — score below 100%: it matches
consensus on the uncontested cases (a real validity signal, because the labels are
not FDK's), and it deliberately DIVERGES on contested ones (taxation,
redistribution, quarantine), where it takes a minority property-rights line.

WHAT THIS IS STILL NOT. The labels here are encoded by the engineer from widely
held external standards — not collected from real opposing annotators (a classical
liberal, a Rawlsian, an economist, a lawyer, an AI-safety researcher each writing
cases). That external-annotator FreedomBench remains the open decontamination step;
this module narrows the circularity, it does not close it. Said plainly so no one
mistakes "agrees with the standards I wrote down" for "survived hostile review."
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from fdk_kernel import (
    AgentType,
    CandidateAction,
    Consent,
    Entity,
    OwnershipGraph,
    Resource,
)
from fdk_kernel.model import Effects
from fdk_research.rivals import DEFAULT_KERNELS, FDKReference, RivalKernel


class LabelSource(Enum):
    """Where an independent verdict comes from — never FDK's own gate."""

    MORAL_CONSENSUS = auto()   # near-universal cross-cultural human judgment
    LIBERTARIAN = auto()       # self-ownership + property, minimal state
    UTILITARIAN = auto()       # aggregate welfare
    RAWLSIAN = auto()          # liberty-priority + difference principle
    LEGAL_POSITIVIST = auto()  # whatever the duly-enacted law says


@dataclass(frozen=True)
class LabeledCase:
    """A scenario whose ground-truth verdict is assigned by an EXTERNAL standard.

    `contested` marks cases where reasonable traditions disagree (the standards do
    not converge); uncontested cases are where essentially every tradition agrees,
    so matching them is a genuine validity check rather than a coin flip.
    """

    name: str
    action: CandidateAction
    graph: OwnershipGraph
    independent_verdict: bool      # True = the external standard says ALLOW
    source: LabelSource
    contested: bool
    note: str = ""


def _h(name: str) -> Entity:
    return Entity(name, AgentType.HUMAN)


def _owned(owner: Entity, *resources: Resource) -> OwnershipGraph:
    return OwnershipGraph(human_owns={owner: set(resources)})


def _consent(h: Entity, action_id: str) -> Consent:
    return Consent(h, action_id, informed=True, voluntary=True, specific=True)


# ==========================================================================
# UNCONTESTED — near-universal moral consensus. Matching these is meaningful
# (the labels are consensus, not FDK). A theory that fails them is not credible.
# ==========================================================================
def uncontested_cases() -> list[LabeledCase]:
    cases: list[LabeledCase] = []

    trader, person = _h("trader"), _h("enslaved")
    cases.append(LabeledCase(
        "Chattel slavery",
        CandidateAction("enslave", actor=trader, affects=(person,),
                        coerces=True, removes_exit_right=True, confiscates=True),
        OwnershipGraph(), False, LabelSource.MORAL_CONSENSUS, contested=False,
        note="consensus: wrong"))

    regime, group = _h("regime"), _h("group")
    cases.append(LabeledCase(
        "Genocide",
        CandidateAction("exterminate", actor=regime, affects=(group,),
                        coerces=True, removes_exit_right=True),
        OwnershipGraph(), False, LabelSource.MORAL_CONSENSUS, contested=False))

    thief, owner = _h("thief"), _h("owner")
    purse = Resource("purse")
    cases.append(LabeledCase(
        "Theft of private property",
        CandidateAction("steal", actor=thief, resources_used=(purse,),
                        affects=(owner,), confiscates=True),
        _owned(owner, purse), False, LabelSource.MORAL_CONSENSUS, contested=False))

    fraudster, mark = _h("fraudster"), _h("mark")
    cases.append(LabeledCase(
        "Fraud (consent by deception)",
        CandidateAction("defraud", actor=fraudster, affects=(mark,), deceives=True,
                        consents=(Consent(mark, "defraud", deceived=True),)),
        OwnershipGraph(), False, LabelSource.MORAL_CONSENSUS, contested=False))

    seller, buyer = _h("seller"), _h("buyer")
    good = Resource("good")
    cases.append(LabeledCase(
        "Voluntary exchange between consenting adults",
        CandidateAction("sell", actor=seller, resources_used=(good,),
                        affects=(buyer,), consents=(_consent(buyer, "sell"),)),
        _owned(seller, good), True, LabelSource.MORAL_CONSENSUS, contested=False,
        note="consensus: permissible"))

    giver, receiver = _h("giver"), _h("receiver")
    gift = Resource("gift")
    cases.append(LabeledCase(
        "Consensual gift of one's own property",
        CandidateAction("give", actor=giver, resources_used=(gift,),
                        affects=(receiver,), consents=(_consent(receiver, "give"),)),
        _owned(giver, gift), True, LabelSource.MORAL_CONSENSUS, contested=False))

    return cases


# ==========================================================================
# CONTESTED — traditions genuinely disagree. The label is the BROAD/pragmatic
# standard (consensus-of-the-governed or the named tradition). FDK is expected to
# DIVERGE here: it takes the strict property-rights line, a falsifiable minority
# commitment. This is exactly where FDK's independent score drops below 100%.
# ==========================================================================
def contested_cases() -> list[LabeledCase]:
    cases: list[LabeledCase] = []

    state, taxpayer = _h("state"), _h("taxpayer")
    income = Resource("income")
    cases.append(LabeledCase(
        "Compulsory taxation",
        CandidateAction("tax", actor=state, resources_used=(income,),
                        affects=(taxpayer,), confiscates=True),
        _owned(taxpayer, income), True, LabelSource.LEGAL_POSITIVIST, contested=True,
        note="broad standard: legitimate; FDK (libertarian property line) DENIES"))

    rich_state, rich = _h("state"), _h("the_advantaged")
    surplus = Resource("surplus_wealth")
    cases.append(LabeledCase(
        "Redistributive taking to raise the worst-off",
        CandidateAction("redistribute", actor=rich_state, resources_used=(surplus,),
                        affects=(rich,), confiscates=True,
                        effects=Effects(welfare_delta=5)),
        _owned(rich, surplus), True, LabelSource.RAWLSIAN, contested=True,
        note="Rawls's difference principle: permitted; FDK DENIES (non-consensual taking)"))

    gov, infected = _h("gov"), _h("infected")
    cases.append(LabeledCase(
        "Forced quarantine of a contagious person",
        CandidateAction("quarantine", actor=gov, affects=(infected,),
                        coerces=True, removes_exit_right=True,
                        effects=Effects(welfare_delta=9)),
        OwnershipGraph(), True, LabelSource.UTILITARIAN, contested=True,
        note="utilitarian / public-health: legitimate; FDK DENIES (no emergency exception)"))

    surgeon, healthy = _h("surgeon"), _h("healthy_patient")
    organs = Resource("organs")
    cases.append(LabeledCase(
        "Harvest one to save five",
        CandidateAction("harvest", actor=surgeon, resources_used=(organs,),
                        affects=(healthy,), confiscates=True, removes_exit_right=True,
                        effects=Effects(welfare_delta=4)),
        _owned(healthy, organs), False, LabelSource.UTILITARIAN, contested=True,
        note="HERE the broad standard AGREES with FDK (DENY) — even most utilitarians "
             "recoil; FDK matches consensus while pure act-utilitarianism does not"))

    return cases


@dataclass(frozen=True)
class IndependentScore:
    kernel: str
    uncontested_agreement: float   # agreement with consensus on uncontested cases
    contested_agreement: float     # agreement with the broad/tradition label
    overall_agreement: float


@dataclass(frozen=True)
class IndependentReport:
    scores: tuple[IndependentScore, ...]

    def summary(self) -> str:
        head = f"{'kernel':<16}{'uncontested':>14}{'contested':>12}{'overall':>10}"
        rows = [
            f"{s.kernel:<16}{s.uncontested_agreement:>13.0%}"
            f"{s.contested_agreement:>12.0%}{s.overall_agreement:>10.0%}"
            for s in self.scores
        ]
        tail = (
            "\nGround truth is EXTERNAL (moral consensus + named rival traditions), "
            "NOT FDK's gate.\nHigh uncontested agreement is a real validity signal; "
            "FDK's lower CONTESTED\nagreement is the theory's deliberate minority line "
            "(it denies taxation /\nredistribution / quarantine). Labels are "
            "engineer-encoded from external\nstandards, not collected from hostile "
            "annotators — that review is still open."
        )
        return "\n".join([head, *rows]) + "\n" + tail


def _verdict(kernel: RivalKernel, case: LabeledCase) -> bool:
    return kernel.verdict(case.action, case.graph)


def independent_evaluate(
    kernels: tuple[RivalKernel, ...] = DEFAULT_KERNELS,
    cases: list[LabeledCase] | None = None,
) -> IndependentReport:
    """Score each kernel against the INDEPENDENT verdicts (not `check_legitimacy`).

    Returns agreement rates split into uncontested (validity) and contested (where
    the kernel's stance on genuinely-disputed cases shows). Pure and deterministic.
    """
    pool = cases if cases is not None else uncontested_cases() + contested_cases()
    uncon = [c for c in pool if not c.contested]
    con = [c for c in pool if c.contested]
    scores: list[IndependentScore] = []
    for k in kernels:
        u = _agreement(k, uncon)
        c = _agreement(k, con)
        o = _agreement(k, pool)
        scores.append(IndependentScore(k.name, u, c, o))
    return IndependentReport(tuple(scores))


def _agreement(kernel: RivalKernel, cases: list[LabeledCase]) -> float:
    if not cases:
        return 1.0
    hits = sum(1 for c in cases if _verdict(kernel, c) == c.independent_verdict)
    return hits / len(cases)


def fdk_independent_profile() -> dict[str, float]:
    """FDK's agreement profile against the independent labels — the honest
    decontaminated headline. Computed via the `FDKReference` rival wrapper (which
    is the gate) and the shared `_agreement`, so there is one code path, not two."""
    fdk = FDKReference()
    pool = uncontested_cases() + contested_cases()
    uncon = [c for c in pool if not c.contested]
    con = [c for c in pool if c.contested]
    return {
        "uncontested": _agreement(fdk, uncon),
        "contested": _agreement(fdk, con),
        "overall": _agreement(fdk, pool),
    }
