"""Adversarial reachability for the AFSM: prove no hidden path amplifies authority."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fdk_kernel.authority_fsm import (
    Op,
    Transition,
    _all_authorities,
    _non_grant_transitions,
    is_amplifying,
    reachable_without_grant,
    step,
    verify_compositional_safety,
)
from fdk_kernel.authority_lattice import Authority

FULL = Authority.of("read", "write", "exec", "delegate")
NONE = Authority.of()


class TestTransitions(unittest.TestCase):
    def test_grant_is_the_only_way_up(self):
        self.assertEqual(step(NONE, Transition(Op.GRANT, Authority.of("read"))), Authority.of("read"))

    def test_delegate_narrows(self):
        self.assertEqual(step(FULL, Transition(Op.DELEGATE, Authority.of("read"))), Authority.of("read"))

    def test_constrain_narrows(self):
        self.assertEqual(
            step(FULL, Transition(Op.CONSTRAIN, Authority.of("read", "write"))),
            Authority.of("read", "write"),
        )

    def test_revoke_drops_to_bottom(self):
        self.assertEqual(step(FULL, Transition(Op.REVOKE)), NONE)

    def test_is_amplifying(self):
        self.assertTrue(is_amplifying(Op.GRANT))
        for op in (Op.DELEGATE, Op.CONSTRAIN, Op.REVOKE):
            self.assertFalse(is_amplifying(op))


class TestMalformedTransitionsRejected(unittest.TestCase):
    def test_grant_requires_rights(self):
        with self.assertRaises(ValueError):
            step(NONE, Transition(Op.GRANT))

    def test_delegate_requires_rights(self):
        with self.assertRaises(ValueError):
            step(FULL, Transition(Op.DELEGATE))

    def test_constrain_requires_rights(self):
        with self.assertRaises(ValueError):
            step(FULL, Transition(Op.CONSTRAIN))


class TestCompositionalSafety(unittest.TestCase):
    def test_every_non_grant_transition_narrows_or_holds(self):
        for s in _all_authorities():
            for t in _non_grant_transitions():
                self.assertLessEqual(step(s, t), s)

    def test_no_hidden_path_amplifies_authority(self):
        # The attacker controls delegate/constrain/revoke inputs but NOT grant.
        # Across the entire reachable space, authority never exceeds the start.
        self.assertTrue(verify_compositional_safety())

    def test_reachable_set_only_narrows(self):
        start = Authority.of("read", "write")
        reached = reachable_without_grant(start)
        self.assertIn(start, reached)
        self.assertTrue(all(r <= start for r in reached))


if __name__ == "__main__":
    unittest.main()
