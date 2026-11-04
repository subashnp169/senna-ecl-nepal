"""Tests for HTML report."""

import os, tempfile
import pytest
from reporting.html_report import generate_html_report


def test_html_report():
    d = tempfile.mkdtemp()
    results = [{"loan_name": "A", "stage": 1, "dpd": 0, "ead": 1000.0, "lgd": 0.45, "ecl_applied": 9.0, "triggers": "none"}]
    totals = {"count": 1, "total_ead": 1000.0, "total_ecl": 9.0, "coverage": 0.9,
              "stage1": {"count": 1, "ead": 1000.0, "ecl": 9.0, "coverage": 0.9},
              "stage2": {"count": 0, "ead": 0.0, "ecl": 0.0, "coverage": 0.0},
              "stage3": {"count": 0, "ead": 0.0, "ecl": 0.0, "coverage": 0.0}}
    p = generate_html_report(results, totals, "TestBank", os.path.join(d, "r.html"))
    assert os.path.exists(p)
    content = open(p, encoding="utf-8").read()
    assert "TestBank" in content
    assert "<table>" in content
    assert "PRELIMINARY" in content
