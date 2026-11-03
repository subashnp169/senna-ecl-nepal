"""Tests for the international ECL core."""

import pytest
from packages.ecl_core import (
    Loan, Stage, classify_stage, ecl_single, lifetime_ecl,
    marginal_pd_from_cumulative, vasicek_pit_pd, scenario_weighted_ecl,
    lgd_from_collateral, ead_total,
)
from packages.ecl_core.types import SICRConfig
from packages.regulatory_nepal import (
    calendar_month_stage, apply_pd_floor, apply_lgd_floor, poci_determination,
    provision_comparison,
)


def test_ecl_single():
    assert ecl_single(0.02, 0.45, 1000.0) == pytest.approx(9.0)


def test_marginal_pd():
    cum = [0.01, 0.03, 0.06]
    m = marginal_pd_from_cumulative(cum)
    assert len(m) == 3
    assert m[0] == pytest.approx(0.01)
    # monotonic-ish
    assert all(0 <= x <= 1 for x in m)


def test_classify_stage1():
    loan = Loan(name="a", principal=100, origination_rating="BBB", current_rating="BBB", lgd=0.45, eir=0.05, maturity=3)
    r = classify_stage(loan)
    assert r.stage == Stage.STAGE_1


def test_classify_stage3_dpd():
    loan = Loan(name="b", principal=100, origination_rating="BB", current_rating="BB", lgd=0.45, eir=0.05, maturity=3, days_past_due=95)
    r = classify_stage(loan)
    assert r.stage == Stage.STAGE_3


def test_classify_stage2_watchlist():
    loan = Loan(name="c", principal=100, origination_rating="BBB", current_rating="BBB", lgd=0.45, eir=0.05, maturity=3, qualitative_flags=["watchlist"])
    r = classify_stage(loan)
    assert r.stage == Stage.STAGE_2


def test_vasicek_zero():
    assert vasicek_pit_pd(0.02, 0.12, 0.0) == pytest.approx(0.02, rel=1e-6)


def test_vasicek_bounds():
    p = vasicek_pit_pd(0.02, 0.12, 2.0)
    assert 0.0 <= p <= 1.0
    assert p > 0.02


def test_scenario_weighted():
    sw = scenario_weighted_ecl(100.0, [{"name": "a", "weight": 0.5, "multiplier": 1.0}, {"name": "b", "weight": 0.5, "multiplier": 2.0}])
    assert sw["weighted_ecl"] == pytest.approx(150.0)


def test_lgd_collateral():
    lgd = lgd_from_collateral(1000.0, 800.0, haircut=0.25)
    assert 0 <= lgd <= 1


def test_ead():
    assert ead_total(1000, 500, 0.5) == 1250.0


def test_calendar_month_stage():
    assert calendar_month_stage(15) == 1
    assert calendar_month_stage(45) == 2
    assert calendar_month_stage(120) == 3


def test_pd_floor():
    assert apply_pd_floor(0.01, 0.025) == 0.025
    assert apply_pd_floor(0.05, 0.025) == 0.05


def test_lgd_floor():
    assert apply_lgd_floor(0.3, False, 0.45) == 0.45
    assert apply_lgd_floor(0.3, True, 0.45) == 0.3


def test_poci():
    assert poci_determination(3, True) is True
    assert poci_determination(2, True) is False
    assert poci_determination(3, False) is False


def test_provision_comparison():
    pc = provision_comparison(100.0, 150.0)
    assert pc["provision_required"] == 150.0


def test_lifetime_ecl_stage1():
    marg = marginal_pd_from_cumulative([0.01, 0.02, 0.03])
    r = lifetime_ecl(1000.0, 0.01, marg, 0.45, 0.05, "bullet", 1)
    assert r["ecl_12m"] >= 0
    assert r["ecl_lifetime"] >= 0
