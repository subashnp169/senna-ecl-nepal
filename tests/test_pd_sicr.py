"""Tests for new PD/SICR modules aligned with SAR Advisors / Infinity PD model."""

import pytest
from packages.ecl_core import (
    vasicek_pit_pd, ttc_pd_from_default_rates, default_rate,
    credit_cycle_index_z, sicr_quantitative_triggers, probation_period_exit_stage3,
    stage_transfer_rules,
)


def test_vasicek_standard():
    # z=0 -> conditional at mean
    v0 = vasicek_pit_pd(0.10, 0.12, 0.0)
    assert 0.0 < v0 < 1.0
    # monotonic: higher z (downturn) -> higher PIT
    assert vasicek_pit_pd(0.10, 0.12, 2.0) > v0
    assert vasicek_pit_pd(0.10, 0.12, -2.0) < v0


def test_ttc_pd():
    rates = [0.05, 0.10, 0.15]
    assert ttc_pd_from_default_rates(rates) == pytest.approx(0.10)
    assert default_rate(1000, 50) == 0.05


def test_credit_cycle_index():
    # observed > ttc -> positive z (downturn)
    z = credit_cycle_index_z(0.15, 0.10, 0.12)
    assert z > 0
    z2 = credit_cycle_index_z(0.05, 0.10, 0.12)
    assert z2 < 0


def test_sicr_indicators():
    trigs = sicr_quantitative_triggers(
        days_past_due=45,
        current_pd=0.06,
        origination_pd=0.02,
        origination_rating="BBB",
        current_rating="BB",
    )
    assert any("DPD" in t for t in trigs)
    assert any("Absolute lifetime PD" in t for t in trigs)
    assert any("Relative lifetime PD" in t for t in trigs)
    assert any("downgrade" in t.lower() for t in trigs)


def test_sicr_no_triggers():
    trigs = sicr_quantitative_triggers(
        days_past_due=10,
        current_pd=0.01,
        origination_pd=0.009,
        origination_rating="BBB",
        current_rating="BBB",
    )
    assert trigs == []


def test_probation():
    assert probation_period_exit_stage3(False) == 180
    assert probation_period_exit_stage3(True) == 730
    rules = stage_transfer_rules()
    assert "stage3_exit_probation_days" in rules


def test_mev_regression():
    from packages.ecl_core.mev import mev_regression_z
    z = mev_regression_z({"gdp": 0.04, "inflation": 0.06}, {"gdp": -0.5, "inflation": 0.3}, intercept=0.0)
    assert isinstance(z, float)
