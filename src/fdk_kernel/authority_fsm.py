"""Authority Flow State Machine (AFSM) — compositional safety across the system.

A state is an effective :class:`Authority` (a set of rights). Transitions are the
operations any subsystem can perform on authority:

* ``GRANT(rights)``    — the ONLY amplifying transition: an explicit, auditable issuance.
* ``DELEGATE(rights)`` — attenuate to the requested rights (meet) — narrows.
* ``CONSTRAIN(rights)``— apply a ceiling (meet) — narrows.
* ``REVOKE``           — drop to bottom (DENY-all).

**Compositional safety theorem** (exhaustively verified over a finite right-universe):
from *any* state, no sequence of NON-GRANT transitions can reach a state with more
authority than the start. There is no hidden path that amplifies authority without an
explicit grant. This lifts the per-component "authority only narrows" to the whole
system — the cross-repo property a set of secure components does not give you for free.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum
from itertools import combinations

from fdk_kernel.authority_lattice import Authority


class Op(Enum):
    GRANT = "grant"
    DELEGATE = "delegate"
    CONSTRAIN = "constrain"
    REVOKE = "revoke"


@dataclass(frozen=True)
class Transition:
    op: Op
    arg: Authority | None = None  # rights for grant/delegate/constrain; None for revoke


def is_amplifying(op: Op) -> bool:
    """Only GRANT can raise authority. Everything else narrows or holds."""
    return op is Op.GRANT


def step(state: Authority, transition: Transition) -> Authority:
    if transition.op is Op.GRANT:
        if transition.arg is None:
            raise ValueError("GRANT requires rights")
        return state.join(transition.arg)        # the only way up — explicit issuance
    if transition.op is Op.DELEGATE:
        if transition.arg is None:
            raise ValueError("DELEGATE requires rights")
        return state.meet(transition.arg)        # narrows
    if transition.op is Op.CONSTRAIN:
        if transition.arg is None:
            raise ValueError("CONSTRAIN requires rights")
        return state.meet(transition.arg)        # narrows
    return Authority(frozenset())                # REVOKE -> bottom


_UNIVERSE = ("read", "write", "exec", "delegate")


def _all_authorities() -> list[Authority]:
    out: list[Authority] = []
    for r in range(len(_UNIVERSE) + 1):
        for combo in combinations(_UNIVERSE, r):
            out.append(Authority(frozenset(combo)))
    return out


def _non_grant_transitions() -> list[Transition]:
    transitions: list[Transition] = [Transition(Op.REVOKE)]
    for a in _all_authorities():
        transitions.append(Transition(Op.DELEGATE, a))
        transitions.append(Transition(Op.CONSTRAIN, a))
    return transitions


def reachable_without_grant(start: Authority) -> set[Authority]:
    """Every state reachable from ``start`` using only non-grant transitions (BFS)."""
    seen: set[Authority] = {start}
    queue: deque[Authority] = deque([start])
    transitions = _non_grant_transitions()
    while queue:
        current = queue.popleft()
        for transition in transitions:
            nxt = step(current, transition)
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def verify_compositional_safety() -> bool:
    """From every start state, no non-grant transition path amplifies authority."""
    return all(
        reached <= start
        for start in _all_authorities()
        for reached in reachable_without_grant(start)
    )
