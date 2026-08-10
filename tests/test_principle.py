"""The Authority Principle, made concrete (see PRINCIPLE.md).

Information and compute enter the system only as constraint inputs (ceilings), so no
amount of either can amplify authority. Authority comes only from an explicit grant.
"""

import sys
import unittest
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fdk_kernel.authority_algebra import Decision, compose


class TestAuthorityPrinciple(unittest.TestCase):
    def test_information_and_compute_cannot_amplify_authority(self):
        # Model "more information" and "more compute" as additional constraint ceilings.
        # Across every base grant and every (information, compute) pair, authority never
        # rises above what was explicitly granted. No-Amplification axiom.
        for grant in Decision:
            for information, compute in product(Decision, Decision):
                self.assertLessEqual(compose(grant, information, compute), grant)

    def test_a_quantum_attacker_with_unlimited_compute_gains_nothing(self):
        # An attacker modelled as ALLOW-wishing constraints cannot raise a denied base.
        for wished in Decision:
            self.assertEqual(compose(Decision.DENY, wished, wished, wished), Decision.DENY)

    def test_default_is_deny(self):
        self.assertEqual(min(Decision), Decision.DENY)


if __name__ == "__main__":
    unittest.main()
