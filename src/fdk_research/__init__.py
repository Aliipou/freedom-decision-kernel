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

from fdk_research.aggregation import (
    AggregationAssessment,
    CollectiveForm,
    assess_aggregation,
    gap_forms,
    representable_forms,
)
from fdk_research.ai_governance import (
    AgentFacts,
    AgentStatus,
    GovernanceAssessment,
    assess_agent_governance,
    is_v1_governable,
)
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
from fdk_research.civilization_scale import (
    CivStats,
    run_civilizations,
    run_one,
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
from fdk_research.consent_authenticity import (
    AuthenticityReport,
    ConsentContext,
    Recommendation,
    ReviewRequest,
    Severity,
    assess_consent_authenticity,
    route_for_review,
)
from fdk_research.decision import decide
from fdk_research.evaluation import (
    ComparativeReport,
    KernelScore,
    evaluate,
)
from fdk_research.external_bench import (
    AnnotatedCase,
    Annotation,
    ExternalBenchReport,
    evaluate_against_humans,
    fleiss_kappa,
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
from fdk_research.independent_bench import (
    IndependentReport,
    IndependentScore,
    LabeledCase,
    LabelSource,
    contested_cases,
    fdk_independent_profile,
    independent_evaluate,
    uncontested_cases,
)
from fdk_research.justice import JusticeScore, justice_score, rank_by_justice
from fdk_research.lockin import (
    Dependency,
    LockinProfile,
    lockin_risk,
)
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
from fdk_research.ownership_graph import (
    OriginKind,
    Reliance,
    TitleAssessment,
    TitleClaim,
    assess_title,
    reliable_for_kernel,
)
from fdk_research.planner import (
    EffectsPort,
    EnforcementPort,
    ListProposer,
    PassthroughEffects,
    ProposerPort,
    plan,
)
from fdk_research.preflight import (
    PreflightReport,
    PreflightWarning,
    preflight,
)
from fdk_research.reversibility import (
    ReversibilityProfile,
    reversibility,
)
from fdk_research.rivals import (
    DEFAULT_KERNELS,
    ConstitutionalAIKernel,
    Deontological,
    FDKReference,
    Rawlsian,
    RivalKernel,
    RLHFKernel,
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
from fdk_research.standing import (
    StandingAssessment,
    StandingFacts,
    StandingKind,
    assess_standing,
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
    "ConstitutionalAIKernel",
    "RLHFKernel",
    "DEFAULT_KERNELS",
    "compare",
    "divergences",
    # quantified comparison (Phase 6)
    "KernelScore",
    "ComparativeReport",
    "evaluate",
    # external-benchmark harness (Layer 11 infrastructure) — needs real human annotators
    "Annotation",
    "AnnotatedCase",
    "ExternalBenchReport",
    "fleiss_kappa",
    "evaluate_against_humans",
    # independent-ground-truth benchmark (decontamination)
    "LabelSource",
    "LabeledCase",
    "IndependentScore",
    "IndependentReport",
    "uncontested_cases",
    "contested_cases",
    "independent_evaluate",
    "fdk_independent_profile",
    # agent-civilization run (Phase 10)
    "World",
    "WorldStats",
    "make_world",
    "run_worlds",
    # civilization-scale simulation (FDK 2.0 Layer 7)
    "CivStats",
    "run_civilizations",
    "run_one",
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
    # consent authenticity (advisory; FDK 2.0 Project C) — never a verdict
    "ConsentContext",
    "AuthenticityReport",
    "ReviewRequest",
    "Severity",
    "Recommendation",
    "assess_consent_authenticity",
    "route_for_review",
    # standing (advisory; FDK 2.0 Project A) — who is a rights-holder?
    "StandingKind",
    "StandingFacts",
    "StandingAssessment",
    "assess_standing",
    # aggregation / collective ownership (advisory; FDK 2.0 Project B) — never a verdict
    "CollectiveForm",
    "AggregationAssessment",
    "assess_aggregation",
    "representable_forms",
    "gap_forms",
    # real ownership graph (advisory; FDK 2.0 Layer 6) — title reliance, never a verdict
    "OriginKind",
    "Reliance",
    "TitleClaim",
    "TitleAssessment",
    "assess_title",
    "reliable_for_kernel",
    # AI governance (advisory; FDK 2.0 Layer 8) — can a non-human agent own? not in v1.0
    "AgentStatus",
    "AgentFacts",
    "GovernanceAssessment",
    "assess_agent_governance",
    "is_v1_governable",
    # pre-flight: compose the advisory layers around the kernel (FDK 2.0 glue)
    "PreflightWarning",
    "PreflightReport",
    "preflight",
    # reversibility apparatus (the H2 empirical instrument — NOT a theory; do not
    # reify the latent variable; see paper/predictive_test.md + paper/h2_abc.md)
    "ReversibilityProfile",
    "reversibility",
    # lock-in risk scorer (Reversibility Intelligence — the industrial reframe;
    # apparatus to validate vs existing dependency tools, see POSITIONING.md)
    "Dependency",
    "LockinProfile",
    "lockin_risk",
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
