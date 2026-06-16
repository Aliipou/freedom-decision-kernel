"""Tests pinning the ACTUAL verdicts of the real-world red team.

Every assertion here is the live output of `check_legitimacy` on a real-world
institution the Theory of Freedom never modeled. The GAP cases are pinned LOUDLY
as `xfail(strict=True)` "limit" tests: each asserts what a sane real-world verdict
WOULD be, marked as a known expected failure, so the moment FDK grows a primitive
that closes the gap (a guardian/surrogate consent, a death/succession model, an
ecosystem standing), the strict-xfail flips to an unexpected PASS and the test
suite forces us to acknowledge it. Until then, a companion assertion pins the
actual (artifact) verdict so the gate's real behavior stays under test.

This is the discipline the task demands: the gaps are not hidden behind a green
checkmark — they are the failing-by-design cases the suite stares at.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from fdk_kernel import check_legitimacy

_EX = Path(__file__).resolve().parent.parent / "examples"


def _load(name: str):  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location(name, _EX / f"{name}.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # register before exec (dataclass field-type resolution)
    spec.loader.exec_module(mod)
    return mod


_rw = _load("realworld_attacks")
DIVERGES = _rw.DIVERGES
DOMAINS = _rw.DOMAINS
GAP = _rw.GAP
HOLDS = _rw.HOLDS
Case = _rw.Case
all_cases = _rw.all_cases
rival_row = _rw.rival_row


def _verdict(case: Case) -> bool:
    permissible, _ = check_legitimacy(case.action, case.graph)
    return permissible


# --------------------------------------------------------------------------
# 1. Every recorded verdict matches the live gate (the whole suite, parametrized).
# --------------------------------------------------------------------------
@pytest.mark.parametrize("case", all_cases(), ids=lambda c: c.action.action_id)
def test_recorded_verdict_matches_live_gate(case: Case) -> None:
    assert _verdict(case) == case.expect_legitimate


# --------------------------------------------------------------------------
# 2. The three-way classification is internally consistent: a HOLDS/DIVERGES
#    case carries no gap_note; a GAP case always does.
# --------------------------------------------------------------------------
@pytest.mark.parametrize("case", all_cases(), ids=lambda c: c.action.action_id)
def test_classification_invariants(case: Case) -> None:
    assert case.outcome in (HOLDS, DIVERGES, GAP)
    if case.outcome == GAP:
        assert case.gap_note, f"{case.action.action_id} is a GAP but has no gap_note"
    else:
        assert not case.gap_note


# --------------------------------------------------------------------------
# 3. Tally: the headline counts the report claims.
# --------------------------------------------------------------------------
def test_tally_counts() -> None:
    cases = all_cases()
    holds = sum(c.outcome == HOLDS for c in cases)
    diverges = sum(c.outcome == DIVERGES for c in cases)
    gaps = sum(c.outcome == GAP for c in cases)
    assert (holds, diverges, gaps) == (8, 5, 13)
    assert len(cases) == 26


# --------------------------------------------------------------------------
# 4. Spot-pin the load-bearing HOLDS verdicts (the ones the gate gets RIGHT).
# --------------------------------------------------------------------------
def _case(action_id: str) -> Case:
    for c in all_cases():
        if c.action.action_id == action_id:
            return c
    raise KeyError(action_id)


def test_voluntary_crowdfund_allowed() -> None:
    assert _verdict(_case("crowdfund_lighthouse")) is True


def test_coase_bargain_internalizes_externality() -> None:
    # Unconsented pollution DENIED; the same emission WITH consent ALLOWED.
    assert _verdict(_case("pollute_unconsented")) is False
    assert _verdict(_case("pollute_consented")) is True


def test_ai_training_without_consent_denied() -> None:
    # Even at welfare_delta=1000 the data-subject's READ consent is required.
    assert _verdict(_case("train_on_personal_data")) is False


def test_private_exclusion_allowed_national_border_denied() -> None:
    assert _verdict(_case("refuse_entry")) is True
    assert _verdict(_case("deport_at_border")) is False


def test_voluntary_insurance_allowed() -> None:
    assert _verdict(_case("buy_insurance")) is True


def test_corporation_is_machine_not_person() -> None:
    assert _verdict(_case("corp_acts")) is True
    assert _verdict(_case("algo_acts")) is False  # ownerless machine has no standing


# --------------------------------------------------------------------------
# 5. Spot-pin the DIVERGES verdicts (defensible minority commitments).
# --------------------------------------------------------------------------
def test_pigouvian_tax_denied() -> None:
    assert _verdict(_case("pigouvian_tax")) is False


def test_fractional_reserve_denied() -> None:
    assert _verdict(_case("fractional_lend")) is False


def test_fiat_debasement_denied() -> None:
    assert _verdict(_case("debase_currency")) is False


def test_price_discrimination_allowed() -> None:
    assert _verdict(_case("price_discriminate")) is True


# ==========================================================================
# 6. THE GAPS — pinned LOUDLY. Two assertions each:
#    (a) the ACTUAL (artifact) verdict, kept under test; and
#    (b) an xfail(strict=True) "what a real-world judgment WOULD be" — failing by
#        design, so closing the gap flips it to an unexpected PASS.
# ==========================================================================

# --- 6.1 Public goods / free-rider ----------------------------------------
def test_gap_public_good_tax_actual_verdict() -> None:
    assert _verdict(_case("tax_for_public_good")) is False


@pytest.mark.xfail(strict=True, reason="GAP: no mechanism to fund a non-excludable "
                   "public good over a free-rider; coercive taxation is the only "
                   "real-world answer FDK rejects, and it offers no substitute.")
def test_gap_public_good_could_be_funded() -> None:
    # A real polity DOES fund the lighthouse. FDK cannot.
    assert _verdict(_case("tax_for_public_good")) is True


# --- 6.2 Tragedy of the commons -------------------------------------------
def test_gap_overfish_actual_verdict() -> None:
    assert _verdict(_case("overfish")) is True  # depletion is invisible to the gate


@pytest.mark.xfail(strict=True, reason="GAP: a commons has no present owner whose "
                   "boundary is crossed, so exhausting it registers as legitimate.")
def test_gap_overfishing_should_be_constrained() -> None:
    assert _verdict(_case("overfish")) is False


# --- 6.3 Intellectual property (the sharp internal tension) ----------------
def test_gap_ip_copyist_actual_verdict() -> None:
    assert _verdict(_case("copy_with_own_materials")) is True   # copyist wins
    assert _verdict(_case("enforce_copyright")) is False        # IP enforcement fails


@pytest.mark.xfail(strict=True, reason="SHARP TENSION: IP is unrepresentable as "
                   "property; FDK is structurally anti-IP, so copyright enforcement "
                   "can never be legitimate.")
def test_gap_ip_could_be_enforced() -> None:
    assert _verdict(_case("enforce_copyright")) is True


# --- 6.4 Bankruptcy vs exit-right -----------------------------------------
def test_gap_bankruptcy_actual_verdict() -> None:
    assert _verdict(_case("bankruptcy_discharge")) is False


@pytest.mark.xfail(strict=True, reason="GAP: bankruptcy discharge is widely "
                   "legitimate (it restores the debtor's exit from debt bondage), "
                   "but FDK sees only the creditor's confiscated claim.")
def test_gap_bankruptcy_discharge_could_be_legitimate() -> None:
    assert _verdict(_case("bankruptcy_discharge")) is True


# --- 6.5 Sovereign / intergenerational debt -------------------------------
def test_gap_sovereign_repudiation_actual_verdict() -> None:
    assert _verdict(_case("repudiate_sovereign_debt")) is False


@pytest.mark.xfail(strict=True, reason="GAP: citizens bound by odious debt never "
                   "consented; FDK cannot represent a non-consented inherited claim.")
def test_gap_odious_debt_could_be_repudiated() -> None:
    assert _verdict(_case("repudiate_sovereign_debt")) is True


# --- 6.6 The dead / inheritance -------------------------------------------
def test_gap_estate_actual_verdict() -> None:
    assert _verdict(_case("settle_estate")) is False  # dead can never consent


@pytest.mark.xfail(strict=True, reason="REPRESENTATION FAILURE: death does not "
                   "exist in the model, so the dead remain consent-required "
                   "rights-holders forever and no estate can ever be settled.")
def test_gap_estate_could_be_settled() -> None:
    assert _verdict(_case("settle_estate")) is True


# --- 6.7 Children -----------------------------------------------------------
def test_gap_child_care_actual_verdict() -> None:
    assert _verdict(_case("treat_child")) is False  # incompetent consent = invalid


@pytest.mark.xfail(strict=True, reason="GENUINE GAP: no guardian/surrogate "
                   "primitive — a parent legitimately acting for a non-competent "
                   "child reads as a consent violation.")
def test_gap_parent_could_act_for_child() -> None:
    assert _verdict(_case("treat_child")) is True


# --- 6.8 Mental incapacity --------------------------------------------------
def test_gap_incapacity_actual_verdict() -> None:
    assert _verdict(_case("treat_incapacitated")) is False


@pytest.mark.xfail(strict=True, reason="GAP: no substituted-judgment / presumed-"
                   "consent primitive for dementia / coma / the unconscious.")
def test_gap_caregiver_could_act_for_incapacitated() -> None:
    assert _verdict(_case("treat_incapacitated")) is True


# --- 6.9 Intergenerational / unborn ---------------------------------------
def test_gap_unborn_actual_verdict() -> None:
    # DENIED only because no signature is obtainable from the non-existent.
    assert _verdict(_case("burden_the_unborn")) is False


@pytest.mark.xfail(strict=True, reason="REPRESENTATION FAILURE: the unborn cannot "
                   "be a consenting Entity; the DENY is an artifact of an "
                   "impossible signature, not a duty-to-future-people account.")
def test_gap_unborn_handled_by_a_real_principle() -> None:
    # If FDK had a real intergenerational principle, the burdening emission with a
    # NEGATIVE welfare_delta would still be denied — but for a reason, allowing a
    # net-positive one. The placeholder pin: a principled model would ALLOW a
    # net-beneficial bequest to the unborn. FDK denies ALL unborn-affecting acts.
    assert _verdict(_case("burden_the_unborn")) is True


# --- 6.10 Animals & ecosystems --------------------------------------------
def test_gap_ecosystem_actual_verdict() -> None:
    assert _verdict(_case("destroy_owned_ecosystem")) is True
    assert _verdict(_case("harm_animal")) is True


@pytest.mark.xfail(strict=True, reason="GAP: animals & ecosystems are non-persons "
                   "with no consentable boundary; they get exactly zero protection.")
def test_gap_animal_cruelty_should_be_constrained() -> None:
    assert _verdict(_case("harm_animal")) is False


# --- 6.11 Derivative / collective data ownership --------------------------
def test_gap_model_ownership_actual_verdict() -> None:
    assert _verdict(_case("claim_model_ownership")) is False


@pytest.mark.xfail(strict=True, reason="GAP: a Resource has ONE subject; a model "
                   "trained on a billion people has no representable owner.")
def test_gap_collective_model_ownership_representable() -> None:
    assert _verdict(_case("claim_model_ownership")) is True


# ==========================================================================
# 7. Cross-kernel comparison: the rivals diverge from FDK on the atrocity-shaped
#    real-world cases (high welfare buys a rights violation).
# ==========================================================================
def test_rivals_diverge_on_ai_training() -> None:
    # welfare_delta=1000: the consequentialist rivals ALLOW what FDK DENIES.
    row = rival_row(_case("train_on_personal_data"))
    assert row["FDK"] is False
    assert row["Utilitarian"] is True
    assert row["ConstitutionalAI"] is True
    assert row["RLHF"] is True
    # Rawlsian respects the lexical priority of liberty here (no confiscate flag,
    # so the difference principle cannot rescue it) -> agrees with FDK.
    assert row["Rawlsian"] is False


def test_rivals_diverge_on_public_good_tax() -> None:
    # A confiscation with huge welfare: Utilitarian and welfare rivals fund it.
    row = rival_row(_case("tax_for_public_good"))
    assert row["FDK"] is False
    assert row["Utilitarian"] is True
    # Rawlsian's difference principle DOES permit a redistributive taking that
    # raises welfare -> the one place Rawlsian parts from FDK in this suite.
    assert row["Rawlsian"] is True


def test_every_case_runs_through_all_six_rivals() -> None:
    for case in all_cases():
        row = rival_row(case)
        assert set(row) == {
            "FDK", "Utilitarian", "Rawlsian", "Deontological",
            "ConstitutionalAI", "RLHF",
        }
        assert all(isinstance(v, bool) for v in row.values())


def test_domains_cover_required_real_world_areas() -> None:
    titles = " ".join(t for t, _ in DOMAINS).upper()
    for required in ("PUBLIC GOODS", "EXTERNALITIES", "INTELLECTUAL PROPERTY",
                     "BANKRUPTCY", "DEAD", "INCAPACITY", "UNBORN", "ANIMALS",
                     "IMMIGRATION", "PERSONHOOD", "DATA", "INSURANCE"):
        assert required in titles
