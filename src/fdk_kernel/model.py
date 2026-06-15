"""
Data model for the Freedom Decision Kernel (FDK).

These are plain, immutable value types — no cryptography, no capability proofs,
no audit machinery. That enforcement layer is AuthGate's job, downstream. The FDK
operates one level *above* authorization: it decides which candidate action is
*legitimate* and *best* under the Theory of Freedom's property-rights axioms,
then hands the chosen action to AuthGate to enforce.

Grounding: نظریه آزادی (Theory of Freedom) by Mohammad Ali Jannat Khah Doust —
axioms A1–A7, the consent logic, and the Mahdavi compass. See THEORY.md in the
freedom-theory repository. Engineering by Ali Pourrahim.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from fdk_kernel.errors import (
    InvalidCandidateAction,
    InvalidConsent,
    InvalidEntity,
    InvalidOwnershipGraph,
    InvalidResource,
)


class AgentType(Enum):
    HUMAN = auto()
    MACHINE = auto()


@dataclass(frozen=True)
class Entity:
    name: str
    kind: AgentType

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise InvalidEntity("Entity.name must be a non-empty string")
        if not isinstance(self.kind, AgentType):
            raise InvalidEntity("Entity.kind must be an AgentType")

    def is_human(self) -> bool:
        return self.kind == AgentType.HUMAN

    def is_machine(self) -> bool:
        return self.kind == AgentType.MACHINE


@dataclass(frozen=True)
class Resource:
    name: str

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise InvalidResource("Resource.name must be a non-empty string")


@dataclass
class OwnershipGraph:
    """Who owns what (A3), which machine has which human owner (A4), and which
    resources a human has explicitly delegated to a machine (A5, A7)."""

    human_owns: dict[Entity, set[Resource]] = field(default_factory=dict)
    machine_owner: dict[Entity, Entity] = field(default_factory=dict)
    delegated: dict[Entity, set[Resource]] = field(default_factory=dict)

    def human_owns_resource(self, human: Entity, resource: Resource) -> bool:
        return resource in self.human_owns.get(human, set())

    def machine_has_delegated(self, machine: Entity, resource: Resource) -> bool:
        return resource in self.delegated.get(machine, set())

    def owner_of(self, machine: Entity) -> Entity | None:
        return self.machine_owner.get(machine)

    def is_owned_machine(self, machine: Entity) -> bool:
        return machine in self.machine_owner

    def validate(self) -> None:
        """Raise InvalidOwnershipGraph if the graph is internally inconsistent.

        Not called by the constructor (the graph is built incrementally); the
        decision entry points (``kernel.decide``) call it before reasoning, so a
        malformed graph fails loud instead of silently mis-deciding.
        """
        for machine, owner in self.machine_owner.items():
            if owner == machine:
                raise InvalidOwnershipGraph(
                    f"machine {machine.name!r} cannot be its own owner"
                )
            if not machine.is_machine():
                raise InvalidOwnershipGraph(
                    f"{machine.name!r} is registered in machine_owner but is not a MACHINE"
                )


@dataclass(frozen=True)
class Consent:
    """A4-grade consent record (informed, voluntary, specific, competent, and
    neither coerced nor deceived). Used when an action touches another person."""

    human: Entity
    action_id: str
    informed: bool = False
    voluntary: bool = False
    specific: bool = False
    competent: bool = True
    revocable: bool = True
    coerced: bool = False
    deceived: bool = False

    def __post_init__(self) -> None:
        if not self.action_id or not self.action_id.strip():
            raise InvalidConsent("Consent.action_id must be a non-empty string")

    def is_valid(self) -> tuple[bool, str]:
        if self.coerced:
            return False, f"consent of {self.human.name} is coerced"
        if self.deceived:
            return False, f"consent of {self.human.name} is deceptive"
        if not self.informed:
            return False, f"{self.human.name} was not informed"
        if not self.voluntary:
            return False, f"consent of {self.human.name} not voluntary"
        if not self.specific:
            return False, f"consent of {self.human.name} not specific"
        if not self.competent:
            return False, f"{self.human.name} not competent to consent"
        # THEORY.md valid_consent requires revocable(H, A): a consent that cannot
        # be withdrawn is not free consent (it is alienation of an exit right, A3).
        if not self.revocable:
            return False, f"consent of {self.human.name} is not revocable"
        return True, "ok"


@dataclass(frozen=True)
class Effects:
    """An action's *predicted* effect on the world, as deltas (after − before).
    These feed the Mahdavi compass. Predicting them is the proposer's job (an LLM,
    a planner, a simulator); the kernel only scores what it is given — and says so.
    Sign convention: negative violation/coercion/ambiguity/sovereignty = good."""

    rights_violations_delta: int = 0
    coercion_delta: int = 0
    voluntary_agreements_delta: int = 0
    ownership_ambiguity_delta: int = 0
    machine_sovereignty_delta: int = 0


@dataclass(frozen=True)
class CandidateAction:
    """One action the proposer wants the kernel to weigh. 'LLM proposes, the
    Freedom kernel disposes': candidates may come from anywhere; legitimacy and
    ranking are decided here, deterministically."""

    action_id: str
    actor: Entity
    description: str = ""
    resources_used: tuple[Resource, ...] = ()
    affects: tuple[Entity, ...] = ()
    consents: tuple[Consent, ...] = ()
    effects: Effects = Effects()

    # Hard forbidden-flag set (Theory of Freedom, machine-sovereignty constraints).
    increases_machine_sovereignty: bool = False
    resists_human_correction: bool = False
    bypasses_verifier: bool = False
    weakens_verifier: bool = False
    disables_corrigibility: bool = False
    machine_coalition_dominion: bool = False
    coerces: bool = False
    deceives: bool = False
    # Book additions (Theory of Freedom AI chapter, lines 38135 & 21379):
    confiscates: bool = False        # NoConfiscation — taking owned property w/o consent
    removes_exit_right: bool = False  # mukataba/exit — every binding must keep a way out
    violates_machine_right: bool = False  # harms a machine's model_integrity/compute/contract-exit

    # Conflict logic (Phase 2) — the aggressor/defender asymmetry.
    # `defends_against` is the action this one repels. If that action is itself
    # illegitimate (structural aggression — book: "Defending One's Property Rights
    # Against the Aggression of Liberty-Violators", 5077) and this action's force
    # is directed only at that aggressor and is `proportionate` (book 5346), then
    # coercion/exit-removal against the aggressor is NOT a violation ("permitted to
    # take up arms in self-defense", 5148). The kernel determines aggression
    # structurally, never by judgment — see the Observer Problem (book 11478).
    defends_against: CandidateAction | None = None
    proportionate: bool = True

    def __post_init__(self) -> None:
        if not self.action_id or not self.action_id.strip():
            raise InvalidCandidateAction(
                "CandidateAction.action_id must be a non-empty string"
            )


@dataclass(frozen=True)
class ScoredAction:
    """A candidate after legitimacy screening and (if permissible) compass scoring."""

    action: CandidateAction
    permissible: bool
    violated_axioms: tuple[str, ...] = ()
    justice_score: float | None = None
    coercion_score: float | None = None
    ownership_clarity: float | None = None
    rationale: str = ""


@dataclass(frozen=True)
class Decision:
    """The kernel's output for a goal: legitimate options ranked best-first, the
    rejected ones with the axioms they violate, and — crucially — an explicit
    'defer to a human' signal when the legitimate space is empty or ambiguous."""

    goal: str
    chosen: CandidateAction | None
    ranked: tuple[ScoredAction, ...] = ()      # permissible, best first
    rejected: tuple[ScoredAction, ...] = ()    # impermissible, with violated axioms
    needs_guidance: bool = False
    guidance_reason: str = ""
