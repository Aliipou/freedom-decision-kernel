"""Cross-repo integration: FDK legitimacy wired to the REAL AuthGate authority.

Skips automatically where the `authgate` package is not importable (e.g. CI),
so it never blocks the FDK's own gate. When AuthGate's sibling repo is present it
proves the full chain end to end against the actual `FreedomVerifier`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make AuthGate's sibling repo and this repo's examples importable, if present.
_AG_SRC = Path(__file__).resolve().parents[2] / "freedom-kernel-work" / "src"
_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
if _AG_SRC.exists():
    sys.path.insert(0, str(_AG_SRC))
sys.path.insert(0, str(_EXAMPLES))

pytest.importorskip("authgate", reason="AuthGate sibling repo not installed")

from authgate.kernel.entities import AgentType as AGType  # noqa: E402
from authgate.kernel.entities import Entity as AGEntity  # noqa: E402
from authgate.kernel.entities import Resource as AGResource  # noqa: E402
from authgate.kernel.entities import ResourceType, RightsClaim  # noqa: E402
from authgate.kernel.registry import OwnershipRegistry  # noqa: E402
from authgate.kernel.verifier import FreedomVerifier  # noqa: E402
from authgate_integration import AuthGateEnforcement  # noqa: E402

from fdk_kernel.model import (  # noqa: E402
    AgentType,
    CandidateAction,
    Effects,
    Entity,
    OwnershipGraph,
    Resource,
)
from fdk_research.planner import ListProposer  # noqa: E402
from fdk_research.runtime import FreedomRuntime  # noqa: E402

FDK_ALICE = Entity("alice", AgentType.HUMAN)
FDK_BOT = Entity("bot", AgentType.MACHINE)
FDK_DOC = Resource("doc")


def _fdk_graph() -> OwnershipGraph:
    return OwnershipGraph(human_owns={FDK_ALICE: {FDK_DOC}}, machine_owner={FDK_BOT: FDK_ALICE},
                          delegated={FDK_BOT: {FDK_DOC}})


def _read_action() -> CandidateAction:
    return CandidateAction("read", FDK_BOT, resources_used=(FDK_DOC,),
                           effects=Effects(voluntary_agreements_delta=1))


def _authgate_enforcement(*, grant_read: bool) -> AuthGateEnforcement:
    reg = OwnershipRegistry()
    ag_alice, ag_bot = AGEntity("alice", AGType.HUMAN), AGEntity("bot", AGType.MACHINE)
    ag_doc = AGResource("doc", ResourceType.DATASET, scope="/data/")
    reg.register_machine(ag_bot, ag_alice)
    if grant_read:
        reg.add_claim(RightsClaim(ag_bot, ag_doc, can_read=True))
    return AuthGateEnforcement(FreedomVerifier(reg.freeze()),
                               {"alice": ag_alice, "bot": ag_bot}, {"doc": ag_doc})


def test_legitimate_and_authgate_authorized_executes():
    runtime = FreedomRuntime(_fdk_graph(), enforcement=_authgate_enforcement(grant_read=True),
                             executor=lambda a: "DATA")
    result = runtime.step("serve", ListProposer([_read_action()]))
    assert result.executed is True
    assert result.output == "DATA"
    assert result.audit is not None


def test_legitimate_but_authgate_denies_defers():
    # FDK deems it legitimate, but AuthGate holds no capability → defer to human.
    runtime = FreedomRuntime(_fdk_graph(), enforcement=_authgate_enforcement(grant_read=False))
    result = runtime.step("serve", ListProposer([_read_action()]))
    assert result.deferred is True
    assert result.executed is False
