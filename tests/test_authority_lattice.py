"""Exhaustive proof that authorities form a bounded lattice and attenuation only narrows."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fdk_kernel.authority_lattice import Authority, attenuate, compose_constraints, verify_lattice


class TestAuthorityLattice(unittest.TestCase):
    def test_all_lattice_laws_and_narrowing_hold(self):
        for name, ok in verify_lattice().items():
            with self.subTest(prop=name):
                self.assertTrue(ok, f"lattice property failed: {name}")

    def test_attenuation_cannot_grant_an_unheld_right(self):
        parent = Authority.of("read")
        got = attenuate(parent, Authority.of("read", "write", "delegate"))
        self.assertEqual(got, Authority.of("read"))  # only what the parent held

    def test_constraints_only_remove(self):
        base = Authority.of("read", "write", "exec")
        r = compose_constraints(base, Authority.of("read", "write"), Authority.of("read"))
        self.assertEqual(r, Authority.of("read"))

    def test_a_constraint_can_deny_all(self):
        self.assertEqual(
            compose_constraints(Authority.of("read"), Authority.of()), Authority.of()
        )


if __name__ == "__main__":
    unittest.main()
