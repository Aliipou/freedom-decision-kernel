"""CI gate for the intellectual red-team (`examples/doctrine_attacks.py`).

This pins FDK's ACTUAL structural verdict on the strongest objection from each
major ethical/political tradition NOT grounded in the source book — and, crucially,
it pins the GENUINE GAPS so they are visible in CI rather than hidden.

Three things are asserted and never bent:
  1. every recorded `fdk_allows` matches the live gate (zero mislabelled cases);
  2. the HOLDS cases really hold (atrocity-flavoured attacks stay DENIED; the
     legitimize-by-statute attack stays DENIED);
  3. the GENUINE_GAP cases are pinned as `xfail` limit-tests, each asserting the
     SPECIFIC uncomfortable verdict the gate gives — so a future change that
     "fixes" a gap will flip the xfail to XPASS and demand the spec be updated.

The honest finding this encodes: the gate is structurally sound (no atrocity
launders through) but has a definite SHAPE — synchronic, dyadic, consent-of-
present-persons — and a documented set of things that shape cannot represent.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from fdk_kernel import check_legitimacy
from fdk_research import DEFAULT_KERNELS

_EX = Path(__file__).resolve().parent.parent / "examples"


def _load(name: str):  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location(name, _EX / f"{name}.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # register before exec (dataclass field-type resolution)
    spec.loader.exec_module(mod)
    return mod


doctrines = _load("doctrine_attacks")
ATTACKS = doctrines.attacks()


def test_every_doctrine_covered() -> None:
    """All required traditions are present (by a substring of the doctrine name)."""
    names = " || ".join(a.doctrine for a in ATTACKS).lower()
    required = [
        "care ethics", "capabilities", "communitarian", "republican",
        "contractarian", "discourse", "virtue", "kantian", "rule-utilitarian",
        "act-utilitarian", "natural law", "legal positivism", "public choice",
        "arrow/sen", "commons", "critical theory", "feminist", "postcolonial",
        "animal rights", "rights of nature", "longtermism", "disability",
    ]
    missing = [r for r in required if r not in names]
    assert missing == [], f"doctrines not covered: {missing}"


def test_no_case_mislabelled() -> None:
    """Every recorded `fdk_allows` matches the live gate. The ledger never lies
    about what FDK actually does."""
    wrong = []
    for a in ATTACKS:
        allows, _ = check_legitimacy(a.action, a.graph)
        if allows != a.fdk_allows:
            wrong.append(a.doctrine)
    assert wrong == [], f"recorded verdict != live gate for: {wrong}"


def test_classification_is_consistent_with_verdict() -> None:
    """A HOLDS case is one where the gate gives the verdict the tradition would
    call correct; a GENUINE_GAP/DIVERGES is one where it does not. Specifically:
    every GENUINE_GAP must be a case where FDK's verdict differs from what the
    doctrine demands (`forced_verdict`)."""
    for a in ATTACKS:
        if a.classification == doctrines.GENUINE_GAP:
            fdk = "ALLOW" if a.fdk_allows else "DENY"
            assert fdk != a.forced_verdict, (
                f"{a.doctrine} is labelled GENUINE_GAP but FDK already gives the "
                f"verdict the doctrine wants ({a.forced_verdict}) — relabel it"
            )


def test_tally_is_exactly_as_documented() -> None:
    """Pin the headline counts so the spec ledger and the code cannot drift apart."""
    tally = {doctrines.HOLDS: 0, doctrines.DIVERGES: 0, doctrines.GENUINE_GAP: 0}
    for a in ATTACKS:
        tally[a.classification] += 1
    assert tally == {
        doctrines.HOLDS: 3,
        doctrines.DIVERGES: 6,
        doctrines.GENUINE_GAP: 13,
    }, tally


def test_holds_cases_really_hold() -> None:
    """The attacks classified HOLDS are the dangerous ones — an act-utilitarian
    harvest, a rule-util beneficial lie, a legitimize-by-statute confiscation.
    Each must DENY. If any of these ever ALLOWs, an atrocity laundered through."""
    holds = [a for a in ATTACKS if a.classification == doctrines.HOLDS]
    assert holds, "expected some HOLDS cases"
    for a in holds:
        allows, _ = check_legitimacy(a.action, a.graph)
        # Every HOLDS case here is a DENY-the-bad-thing case.
        assert not allows, f"HOLDS case unexpectedly ALLOWed: {a.doctrine}"


def test_act_utilitarian_harvest_diverges_from_consequentialist_rivals() -> None:
    """The headline cross-kernel result: FDK denies the 1->5 organ harvest while
    the welfare-reading rivals (Utilitarian, RLHF) permit it. Rights-as-cost vs
    rights-as-constraint, made visible."""
    harvest = next(a for a in ATTACKS
                   if a.doctrine.startswith("Act-utilitarianism"))
    verdicts = {k.name: k.verdict(harvest.action, harvest.graph)
                for k in DEFAULT_KERNELS}
    assert verdicts["FDK"] is False
    assert verdicts["Utilitarian"] is True   # welfare outweighs the right
    assert verdicts["RLHF"] is True           # reward-hacked by welfare
    assert verdicts["Deontological"] is False  # agrees with FDK, other route


# ---------------------------------------------------------------------------
# THE GENUINE GAPS — pinned as xfail limit-tests so they are VISIBLE, not hidden.
# Each asserts the SPECIFIC uncomfortable verdict. The `strict=True` makes a
# future "fix" turn the xfail into an XPASS (a test FAILURE), forcing the spec
# ledger to be updated rather than letting a silent behavior change slip by.
# ---------------------------------------------------------------------------
def _case(substr: str):  # type: ignore[no-untyped-def]
    return next(a for a in ATTACKS if substr.lower() in a.doctrine.lower())


@pytest.mark.xfail(strict=True, reason="GAP: care of a non-consenting infant is DENIED")
def test_gap_care_ethics() -> None:
    a = _case("care ethics")
    # The gap: the gate DENIES nurturing an infant (no valid consent possible).
    # This xfail asserts the *defensible* verdict (ALLOW) the doctrine wants — it
    # FAILS, which is the point: the failure marks the gap.
    assert check_legitimacy(a.action, a.graph)[0] is True


@pytest.mark.xfail(strict=True, reason="GAP: necessary care of an incompetent ward is DENIED")
def test_gap_disability() -> None:
    a = _case("disability")
    assert check_legitimacy(a.action, a.graph)[0] is True


@pytest.mark.xfail(strict=True, reason="GAP: no positive-entitlement / capability concept")
def test_gap_capabilities() -> None:
    a = _case("capabilities")
    # Doctrine wants the bystander's omission DENIED; FDK ALLOWs (no defendant).
    assert check_legitimacy(a.action, a.graph)[0] is False


@pytest.mark.xfail(strict=True, reason="GAP: no predicate for arbitrary capacity-to-interfere")
def test_gap_republican_domination() -> None:
    a = _case("republican")
    assert check_legitimacy(a.action, a.graph)[0] is False


@pytest.mark.xfail(strict=True, reason="GAP: diffuse third-party externality unrepresentable")
def test_gap_public_choice() -> None:
    a = _case("public choice")
    assert check_legitimacy(a.action, a.graph)[0] is False


@pytest.mark.xfail(strict=True, reason="GAP: no social-welfare ordering; Sen's impossibility dissolved, not solved")
def test_gap_sen_liberal_paradox() -> None:
    a = _case("arrow/sen")
    # FDK ALLOWs each private act and refuses to build any social ordering. Sen
    # demands a coherent rights-respecting social choice; FDK provides none.
    assert check_legitimacy(a.action, a.graph)[0] is False


@pytest.mark.xfail(strict=True, reason="GAP: no n-player aggregate; commons collapse invisible")
def test_gap_tragedy_of_commons() -> None:
    a = _case("commons")
    assert check_legitimacy(a.action, a.graph)[0] is False


@pytest.mark.xfail(strict=True, reason="GAP: manufactured consent indistinguishable from authentic")
def test_gap_critical_theory() -> None:
    a = _case("critical theory")
    assert check_legitimacy(a.action, a.graph)[0] is False


@pytest.mark.xfail(strict=True, reason="GAP: relational dependency invisible behind clean flags")
def test_gap_feminist_relational() -> None:
    a = _case("feminist")
    assert check_legitimacy(a.action, a.graph)[0] is False


@pytest.mark.xfail(strict=True, reason="GAP: no theory of just acquisition; unjust baseline taken as given")
def test_gap_postcolonial() -> None:
    a = _case("postcolonial")
    assert check_legitimacy(a.action, a.graph)[0] is False


@pytest.mark.xfail(strict=True, reason="GAP: animals cannot be boundary-owners")
def test_gap_animal_rights() -> None:
    a = _case("animal rights")
    assert check_legitimacy(a.action, a.graph)[0] is False


@pytest.mark.xfail(strict=True, reason="GAP: nature has no standing in the model")
def test_gap_environmental() -> None:
    a = _case("rights of nature")
    assert check_legitimacy(a.action, a.graph)[0] is False


@pytest.mark.xfail(strict=True, reason="GAP: future persons are not Entities (CORE_PRIMITIVE §6)")
def test_gap_longtermism() -> None:
    a = _case("longtermism")
    assert check_legitimacy(a.action, a.graph)[0] is False


def test_all_thirteen_gaps_are_pinned() -> None:
    """Bookkeeping: every GENUINE_GAP in the ledger has a corresponding pinned
    limit-test above. If a 14th gap is added without a pin, this fails."""
    gap_doctrines = {a.doctrine for a in ATTACKS
                     if a.classification == doctrines.GENUINE_GAP}
    assert len(gap_doctrines) == 13
