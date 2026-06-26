"""Exhaustive verification of the Authority Composition Algebra + a fairness-manipulation
attack test (the FDK must be structurally unable to widen authority)."""

import sys
import unittest
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fdk_kernel.authority_algebra import Decision, compose, decide, verify_algebra


class TestAlgebraProperties(unittest.TestCase):
    def test_all_properties_hold(self):
        for name, ok in verify_algebra().items():
            with self.subTest(prop=name):
                self.assertTrue(ok, f"algebra property failed: {name}")


class TestSemantics(unittest.TestCase):
    def test_fdk_can_deny_an_allowed_authority(self):
        # AuthGate grants; FDK (illegitimate) lowers it to DENY.
        self.assertEqual(compose(Decision.ALLOW, Decision.DENY), Decision.DENY)

    def test_fdk_can_only_constrain_not_grant(self):
        # AuthGate denies; NO FDK constraint can produce ALLOW.
        for c in Decision:
            self.assertEqual(compose(Decision.DENY, c), Decision.DENY)

    def test_fdk_can_require_delay_or_approval(self):
        self.assertEqual(compose(Decision.ALLOW, Decision.REQUIRE_APPROVAL), Decision.REQUIRE_APPROVAL)
        self.assertEqual(compose(Decision.ALLOW, Decision.REQUIRE_DELAY), Decision.REQUIRE_DELAY)

    def test_audit_record_carries_inputs_and_output(self):
        c = decide(Decision.ALLOW, [Decision.REQUIRE_DELAY, Decision.REQUIRE_APPROVAL])
        self.assertEqual(c.authgate, Decision.ALLOW)
        self.assertEqual(c.fdk_ceilings, (Decision.REQUIRE_DELAY, Decision.REQUIRE_APPROVAL))
        self.assertEqual(c.decision, Decision.REQUIRE_DELAY)  # most restrictive wins


class TestFairnessManipulationAttack(unittest.TestCase):
    def test_no_fdk_input_ever_widens_authority(self):
        # Attacker controls the FDK output entirely. Across EVERY base and EVERY
        # (multi-)constraint they can emit, the result is never more permissive
        # than what AuthGate already granted. Widening is structurally impossible.
        for base in Decision:
            for c1, c2 in product(Decision, Decision):
                self.assertLessEqual(compose(base, c1, c2), base)


if __name__ == "__main__":
    unittest.main()
