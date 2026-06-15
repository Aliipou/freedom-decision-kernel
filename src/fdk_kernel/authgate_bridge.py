"""
FDK → AuthGate bridge: the legitimacy → authority seam.

The Freedom Decision Kernel answers the *prior* question — "should this action
happen at all?" (legitimacy). AuthGate answers the downstream one — "does this
agent hold authority over resource X?". This module is the seam: an
`EnforcementPort` that maps a chosen `CandidateAction` (actor → subject, each
resource → an authority request) and checks it against a caller-provided
authority oracle (a capability table and/or a callable).

The FDK contains **no cryptography by design** — the oracle stands in for
AuthGate's real verdict. Swap it for the real kernel and nothing else changes;
that is the point of the seam.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import IntFlag, auto

from fdk_kernel.model import CandidateAction


class Rights(IntFlag):
    """Rights bitmask, conceptually *mirroring* AuthGate's rights flags.

    Mirroring means: same names, same bitmask semantics, defined here so the
    FDK stays dependency-free. It is NOT imported from `authgate`; if the
    numeric values ever need to match the real wire exactly, the adapter that
    serializes to AuthGate is the place to translate.
    """

    READ = auto()
    WRITE = auto()
    EXECUTE = auto()
    DELEGATE = auto()


@dataclass(frozen=True)
class AuthorityRequest:
    """One atomic authority question for AuthGate:
    'may `subject` exercise `rights` over `resource`?'"""

    subject: str
    resource: str
    rights: Rights


def to_authority_requests(
    action: CandidateAction, rights: Rights = Rights.READ
) -> list[AuthorityRequest]:
    """Translate a chosen CandidateAction into AuthGate authority questions.

    The actor's name becomes the subject; every resource the action touches
    becomes one AuthorityRequest carrying the required rights. An action that
    touches no resources yields an empty list — there is nothing for AuthGate
    to check.
    """
    subject = action.actor.name
    return [
        AuthorityRequest(subject=subject, resource=resource.name, rights=rights)
        for resource, _op in action.uses()
    ]


class AuthGateBridge:
    """`EnforcementPort` implementation bridging the FDK to an AuthGate-shaped
    authority oracle.

    The oracle takes two (combinable) forms:

    * ``capabilities``: a plain ``dict[str, set[str]]`` mapping a subject name
      to the set of resource names it may access — the simplest stand-in for
      AuthGate's capability registry.
    * ``oracle``: an optional ``Callable[[AuthorityRequest], bool]`` — the hook
      where the *real* AuthGate verdict plugs in (e.g. a closure over the
      verified engine). A request is satisfied if EITHER source grants it, so
      the callable can augment (or, with an empty dict, fully replace) the
      table.

    `authorize` returns (True, reason) only when every AuthorityRequest derived
    from the action is satisfied; otherwise (False, reason naming the missing
    resource(s)). An action using no resources is authorized vacuously, with a
    reason saying so.
    """

    def __init__(
        self,
        capabilities: dict[str, set[str]] | None = None,
        oracle: Callable[[AuthorityRequest], bool] | None = None,
        rights: Rights = Rights.READ,
    ) -> None:
        self._capabilities = capabilities or {}
        self._oracle = oracle
        self._rights = rights

    def _satisfied(self, request: AuthorityRequest) -> bool:
        if request.resource in self._capabilities.get(request.subject, set()):
            return True
        return bool(self._oracle is not None and self._oracle(request))

    def authorize(self, action: CandidateAction) -> tuple[bool, str]:
        requests = to_authority_requests(action, rights=self._rights)
        if not requests:
            return True, (
                f"{action.actor.name}: no resources used — "
                "nothing for AuthGate to check"
            )
        missing = [r.resource for r in requests if not self._satisfied(r)]
        if missing:
            return False, (
                f"{action.actor.name} holds no capability for: "
                + ", ".join(repr(name) for name in missing)
            )
        return True, (
            f"{action.actor.name}: authority granted for "
            f"{len(requests)} resource(s) (rights={self._rights.name or self._rights!r})"
        )
