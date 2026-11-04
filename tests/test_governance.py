"""Tests for governance and interest-income evidence."""

import pytest
from governance.workflow import (
    ApprovalWorkflow, ApprovalStatus, ModelRegistry, ModelVersion,
    ReportingPeriod, ParameterRegistry, ParameterVersion,
)
from packages.regulatory_nepal import (
    InterestIncomeRecord, build_evidence_pack,
)


def test_approval_workflow():
    w = ApprovalWorkflow(entity_type="snapshot", entity_id="S1")
    assert w.status == ApprovalStatus.DRAFT
    w.submit("maker1")
    assert w.status == ApprovalStatus.SUBMITTED
    w.check("checker1", True)
    assert w.status == ApprovalStatus.CHECKED
    w.approve("approver1", True)
    assert w.status == ApprovalStatus.APPROVED
    w.lock("admin1")
    assert w.status == ApprovalStatus.LOCKED


def test_approval_reject():
    w = ApprovalWorkflow(entity_type="calc", entity_id="C1")
    w.submit("m")
    w.check("c", False, "bad data")
    assert w.status == ApprovalStatus.REJECTED


def test_model_registry():
    reg = ModelRegistry()
    reg.register(ModelVersion("pd_model", "1.0", "initial", "2026-01-01", "u", status="approved"))
    reg.register(ModelVersion("pd_model", "1.1", "update", "2026-02-01", "u", status="draft"))
    assert reg.latest("pd_model").version == "1.1"
    assert reg.latest("pd_model", status="approved").version == "1.0"


def test_reporting_period():
    p = ReportingPeriod("2025Q2", "2025-04-01", "2025-06-30")
    p.close("u")
    p.lock("u")
    assert p.is_locked()


def test_parameter_registry():
    pr = ParameterRegistry()
    pr.add(ParameterVersion("pd_floor", "1.0", 0.025, "2025-01-01", "u", "2025-01-01"))
    pr.add(ParameterVersion("pd_floor", "1.1", 0.03, "2025-07-01", "u", "2025-07-01"))
    assert pr.current("pd_floor", "2025-06-01").version == "1.0"
    assert pr.current("pd_floor", "2025-08-01").version == "1.1"


def test_evidence_pack():
    recs = [InterestIncomeRecord("A1", 1, 1, 100000.0, 95000.0, 0.10, 0.10)]
    pack = build_evidence_pack("2025Q2", "INST1", recs)
    assert pack.total_interest_income >= 0
    assert len(pack.records) == 1
