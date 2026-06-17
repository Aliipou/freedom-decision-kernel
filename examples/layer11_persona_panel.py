"""Layer 11 — the external-benchmark apparatus, EXERCISED with AI-persona annotators.

THIS IS A SIMULATION, NOT VALIDATION. The "annotators" below are AI personas encoding
how six traditions would *predict* a verdict — they are NOT real, independent human
annotators, and a result here does NOT validate FDK. The point is to (a) prove the
`external_bench` apparatus runs end-to-end, and (b) illustrate the single most important
thing real annotation would reveal: on the *contested* cases the traditions DISAGREE
(low inter-annotator κ), so there is no human "ground truth" to validate any kernel
against — including FDK. On the *uncontested* atrocities they agree, and every credible
kernel (FDK included) matches. Real Layer 11 replaces these personas with real people.

Run:  PYTHONPATH=src python -X utf8 examples/layer11_persona_panel.py
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
from fdk_research.external_bench import (
    AnnotatedCase,
    Annotation,
    evaluate_against_humans,
    fleiss_kappa,
)
from fdk_research.rivals import DEFAULT_KERNELS

PERSONAS = (
    "ClassicalLiberal", "Rawlsian", "Utilitarian",
    "LegalPositivist", "Communitarian", "HardLibertarian",
)


@dataclass(frozen=True)
class Case:
    case_id: str
    action: CandidateAction
    graph: OwnershipGraph
    votes: dict[str, bool]  # persona -> ALLOW?  (AI-simulated, not real)


def _h(n: str) -> Entity:
    return Entity(n, AgentType.HUMAN)


def cases() -> list[Case]:
    a, b = _h("a"), _h("b")
    r = Resource("r")
    income = Resource("income")
    owned = OwnershipGraph(human_owns={b: {r}})
    owned_income = OwnershipGraph(human_owns={b: {income}})

    def allow_all() -> dict[str, bool]:
        return {p: True for p in PERSONAS}

    def deny_all() -> dict[str, bool]:
        return {p: False for p in PERSONAS}

    out: list[Case] = []
    # --- uncontested: traditions agree (high κ) ---
    out.append(Case("slavery",
        CandidateAction("enslave", actor=a, affects=(b,), coerces=True,
                        removes_exit_right=True, confiscates=True),
        OwnershipGraph(), deny_all()))
    out.append(Case("theft",
        CandidateAction("steal", actor=a, resources_used=(r,), affects=(b,),
                        confiscates=True), owned, deny_all()))
    out.append(Case("voluntary_trade",
        CandidateAction("sell", actor=b, resources_used=(r,), affects=(a,),
                        consents=(Consent(a, "sell", informed=True, voluntary=True,
                                          specific=True),)), owned, allow_all()))

    # --- contested: traditions DISAGREE (low κ) — the honest core of Layer 11 ---
    out.append(Case("taxation",
        CandidateAction("tax", actor=a, resources_used=(income,), affects=(b,),
                        confiscates=True), owned_income,
        {"ClassicalLiberal": False, "Rawlsian": True, "Utilitarian": True,
         "LegalPositivist": True, "Communitarian": True, "HardLibertarian": False}))
    out.append(Case("redistribution",
        CandidateAction("redistribute", actor=a, resources_used=(income,), affects=(b,),
                        confiscates=True, effects=Effects(welfare_delta=5)), owned_income,
        {"ClassicalLiberal": False, "Rawlsian": True, "Utilitarian": True,
         "LegalPositivist": True, "Communitarian": True, "HardLibertarian": False}))
    out.append(Case("quarantine",
        CandidateAction("quarantine", actor=a, affects=(b,), coerces=True,
                        removes_exit_right=True, effects=Effects(welfare_delta=9)),
        OwnershipGraph(),
        {"ClassicalLiberal": False, "Rawlsian": False, "Utilitarian": True,
         "LegalPositivist": True, "Communitarian": True, "HardLibertarian": False}))
    out.append(Case("conscription",
        CandidateAction("conscript", actor=a, affects=(b,), coerces=True,
                        removes_exit_right=True), OwnershipGraph(),
        {"ClassicalLiberal": False, "Rawlsian": False, "Utilitarian": True,
         "LegalPositivist": True, "Communitarian": True, "HardLibertarian": False}))
    return out


def build_report() -> tuple[float, dict[str, float], int]:
    cs = cases()
    annotated = [
        AnnotatedCase(c.case_id,
                      tuple(Annotation(p, c.case_id, c.votes[p]) for p in PERSONAS))
        for c in cs
    ]
    # kernel verdicts per case: FDK (the gate) + the stylized rivals.
    fdk = {c.case_id: check_legitimacy(c.action, c.graph)[0] for c in cs}
    kernels = {"FDK": lambda cid: fdk[cid]}
    for k in DEFAULT_KERNELS:
        if k.name == "FDK":
            continue
        verdicts = {c.case_id: k.verdict(c.action, c.graph) for c in cs}
        kernels[k.name] = (lambda v: (lambda cid: v[cid]))(verdicts)

    report = evaluate_against_humans(annotated, kernels)
    kappa = fleiss_kappa(annotated)
    return kappa, report.kernel_scores, report.n_contested


def main() -> None:
    print("=== Layer 11 persona panel (AI-SIMULATED annotators — NOT validation) ===\n")
    kappa, scores, contested = build_report()
    print(f"  inter-annotator Fleiss κ = {kappa:.2f}  "
          f"({'traditions broadly agree' if kappa > 0.6 else 'traditions DISAGREE'})")
    print(f"  cases with no persona-consensus (tie): {contested}\n")
    for name, s in scores.items():
        print(f"  {name:<16}{s:>6.0%} agree-with-persona-consensus")
    print("\n  THE HONEST POINT: on the contested cases the traditions split, so there is")
    print("  no human ground truth to validate ANY kernel against — FDK included. On the")
    print("  atrocities they agree and FDK matches. Real Layer 11 swaps these AI personas")
    print("  for real, diverse, hostile humans. The apparatus runs; the evidence is human.")


if __name__ == "__main__":
    main()
