"""Tests for ingestion and reporting."""

import os
import tempfile
import pytest

from connectors.excel_2_2.template_generator import build_template
from connectors.excel_2_2.ingestion import ingest_excel
from reporting.generator import TenantConfig, generate_excel_report, generate_csv_report, generate_json_report


def test_template_and_ingest():
    d = tempfile.mkdtemp()
    path = os.path.join(d, "tmpl.xlsx")
    build_template(path)
    assert os.path.exists(path)
    res = ingest_excel(path, institution_id="TEST", as_of_date="2025-06-30")
    assert res.ok
    assert len(res.loans) == 1
    assert res.loans[0].account_id == "ACC001"


def test_reports():
    d = tempfile.mkdtemp()
    results = [{"loan_name": "A", "stage": 1, "ead": 1000.0, "ecl_applied": 9.0}]
    totals = {"count": 1, "total_ead": 1000.0, "total_ecl": 9.0, "coverage": 0.9,
              "stage1": {"count": 1, "ead": 1000.0, "ecl": 9.0, "coverage": 0.9},
              "stage2": {"count": 0, "ead": 0.0, "ecl": 0.0, "coverage": 0.0},
              "stage3": {"count": 0, "ead": 0.0, "ecl": 0.0, "coverage": 0.0}}
    tenant = TenantConfig(name="TestBank")
    xp = generate_excel_report(results, totals, tenant, os.path.join(d, "r.xlsx"))
    cp = generate_csv_report(results, os.path.join(d, "r.csv"))
    jp = generate_json_report(results, totals, os.path.join(d, "r.json"))
    assert os.path.exists(xp) and os.path.exists(cp) and os.path.exists(jp)
