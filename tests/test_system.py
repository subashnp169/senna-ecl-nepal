"""Tests for Infinity adapter and pipeline."""

import os
import pytest

from connectors.infinity_2_2.adapter import adapt_infinity_report
from pipeline import run_pipeline

SAMPLE = "sample_data/infinity_sample.xlsx"
FULL = r"D:\data\NRB_2_2_REPORT_REVAMPED_000080__20261008_095117.xlsx"


def test_adapter_sample():
    # sample is vendor format, not raw; adapter should fail gracefully
    res = adapt_infinity_report(SAMPLE, "ILBSL", "2025-06-30")
    # sample has no Report Data sheet -> error
    assert not res.ok or len(res.loans) == 0


def test_pipeline_sample():
    r = run_pipeline(SAMPLE, tenant_name="ILBSL", as_of_date="2025-06-30", institution_id="ILBSL")
    assert r.ok
    assert len(r.loans) == 120
    assert "excel" in r.report_paths


@pytest.mark.skipif(not os.path.exists(FULL), reason="full data not present")
def test_pipeline_full():
    r = run_pipeline(FULL, tenant_name="ILBSL", as_of_date="2025-06-30", institution_id="ILBSL")
    assert r.ok
    assert len(r.loans) > 30000
