"""
fdk_research — the experimental / optimization layer above the legitimacy gate.

Everything here is soft, heuristic, or uncalibrated by design: compass ranking,
planning, simulation, justice scoring, conflict and federation logic, guidance
*resolution*. It is layered ON TOP of `fdk_kernel`'s deterministic legitimacy
gate and depends on it freely (research → kernel). The reverse is forbidden: the
kernel must never import from here (see tests/test_boundary.py). That brutal
epistemic separation is the project's golden rule — nothing migrates into the
kernel unless it is deterministic + fully testable + non-semantic.

Grounded in نظریه آزادی (Theory of Freedom) by Mohammad Ali Jannat Khah Doust.
Engineering by Ali Pourrahim.
"""
from __future__ import annotations

from fdk_research.benchmark import (
    BenchmarkReport,
    ProblemClass,
    Scenario,
    ScenarioResult,
    default_suite,
    run_benchmark,
)
from fdk_research.civilization import (
    World,
    WorldStats,
    make_world,
    run_worlds,
)
from fdk_research.compass import mahdavi_score
from fdk_research.compass_measure import (
    coercion_score,
    dependency_index,
    exit_options,
    ownership_clarity,
    voluntary_order,
)
from fdk_research.conflict import Outcome, Resolution, resolve_conflict
from fdk_research.decision import decide
from fdk_research.evaluation import (
    ComparativeReport,
    KernelScore,
    evaluate,
)
from fdk_research.federation import (
    Federation,
    constitutional_update_allowed,
    federated_decide,
    resolve_dispute,
)
from fdk_research.guidance_engine import (
    ConsentGrant,
    Constraint,
    DelegationGrant,
    SelfUpdate,
    VerificationReport,
    verify_guidance,
    verify_self_update,
)
from fdk_research.guidance_resolution import NON_NEGOTIABLE, request_guidance
from fdk_research.justice import JusticeScore, justice_score, rank_by_justice
from fdk_research.necessity import harm, least_harmful_among_permissible
from fdk_research.ontology import (
    Claim,
    ClaimBasis,
    Conflict,
    ConflictKind,
    Contract,
    MachineRight,
    Obligation,
)
from fdk_research.planner import (
    EffectsPort,
    EnforcementPort,
    ListProposer,
    PassthroughEffects,
    ProposerPort,
    plan,
)
from fdk_research.rivals import (
    DEFAULT_KERNELS,
    Deontological,
    FDKReference,
    Rawlsian,
    RivalKernel,
    Utilitarian,
    compare,
    divergences,
)
from fdk_research.runtime import FreedomRuntime, RuntimeResult
from fdk_research.simulator import (
    SafetyInvariantViolated,
    SimReport,
    StepOutcome,
    run_scenario,
)

__all__ = [
    # decision orchestration (screen + rank)
    "decide",
    # compass (soft ranking)
    "mahdavi_score",
    # necessity (least-harm selection among permissible — no gate exception)
    "least_harmful_among_permissible",
    "harm",
    # rival kernels + comparative evaluation (Phase 6)
    "RivalKernel",
    "FDKReference",
    "Utilitarian",
    "Rawlsian",
    "Deontological",
    "DEFAULT_KERNELS",
    "compare",
    "divergences",
    # quantified comparison (Phase 6)
    "KernelScore",
    "ComparativeReport",
    "evaluate",
    # agent-civilization run (Phase 10)
    "World",
    "WorldStats",
    "make_world",
    "run_worlds",
    # guidance resolution (clarification advice)
    "request_guidance",
    "NON_NEGOTIABLE",
    # justice (advisory ranking)
    "JusticeScore",
    "justice_score",
    "rank_by_justice",
    # guidance engine (verify human responses + self-update)
    "DelegationGrant",
    "ConsentGrant",
    "Constraint",
    "VerificationReport",
    "verify_guidance",
    "SelfUpdate",
    "verify_self_update",
    # ontology
    "Claim",
    "ClaimBasis",
    "Obligation",
    "Contract",
    "Conflict",
    "ConflictKind",
    "MachineRight",
    # conflict resolution
    "Outcome",
    "Resolution",
    "resolve_conflict",
    # compass measurement (advisory)
    "dependency_index",
    "exit_options",
    "coercion_score",
    "ownership_clarity",
    "voluntary_order",
    # planner
    "plan",
    "ProposerPort",
    "EffectsPort",
    "EnforcementPort",
    "PassthroughEffects",
    "ListProposer",
    # simulator
    "run_scenario",
    "SimReport",
    "StepOutcome",
    "SafetyInvariantViolated",
    # federation
    "Federation",
    "federated_decide",
    "resolve_dispute",
    "constitutional_update_allowed",
    # runtime
    "FreedomRuntime",
    "RuntimeResult",
    # benchmark
    "ProblemClass",
    "Scenario",
    "ScenarioResult",
    "BenchmarkReport",
    "run_benchmark",
    "default_suite",
]
