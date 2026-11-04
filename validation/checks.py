"""Data validation, reconciliation and quality checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""
    severity: str = "error"  # error / warning


@dataclass
class ValidationReport:
    checks: List[CheckResult] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(c.passed or c.severity != "error" for c in self.checks)

    def add(self, c: CheckResult) -> None:
        self.checks.append(c)


def check_required_fields(rows: List[Dict[str, Any]], required: List[str]) -> CheckResult:
    missing = [f for f in required if any(f not in r or r.get(f) is None for r in rows)]
    return CheckResult("required_fields", len(missing) == 0, f"missing: {missing}" if missing else "ok")


def check_non_negative(rows: List[Dict[str, Any]], fields: List[str]) -> CheckResult:
    bad = []
    for r in rows:
        for f in fields:
            v = r.get(f)
            if v is not None and (not isinstance(v, (int, float)) or v < 0):
                bad.append((r.get("account_id"), f, v))
    return CheckResult("non_negative", len(bad) == 0, f"violations: {bad[:5]}" if bad else "ok")


def check_unique(rows: List[Dict[str, Any]], field: str) -> CheckResult:
    vals = [r.get(field) for r in rows]
    dupes = [v for v in set(vals) if vals.count(v) > 1]
    return CheckResult("unique", len(dupes) == 0, f"duplicates: {dupes[:5]}" if dupes else "ok")


def check_control_totals(rows: List[Dict[str, Any]], reported_total: float, field: str = "outstanding", tol: float = 1.0) -> CheckResult:
    actual = sum(r.get(field, 0) or 0 for r in rows)
    diff = abs(actual - reported_total)
    return CheckResult("control_total", diff <= tol, f"actual={actual} reported={reported_total} diff={diff}")


def check_date_consistency(rows: List[Dict[str, Any]]) -> CheckResult:
    bad = []
    for r in rows:
        od = r.get("origination_date")
        md = r.get("maturity_date")
        if od and md and str(od) > str(md):
            bad.append(r.get("account_id"))
    return CheckResult("date_consistency", len(bad) == 0, f"bad: {bad[:5]}" if bad else "ok")


def reconcile_ecl(ecl_total: float, provision_total: float, tol: float = 0.01) -> CheckResult:
    diff = abs(ecl_total - provision_total)
    return CheckResult("ecl_provision_recon", diff <= tol, f"diff={diff}")


def run_standard_checks(rows: List[Dict[str, Any]], reported_total: float) -> ValidationReport:
    rep = ValidationReport()
    rep.add(check_required_fields(rows, ["account_id", "outstanding"]))
    rep.add(check_non_negative(rows, ["outstanding", "undrawn_limit", "dpd"]))
    rep.add(check_unique(rows, "account_id"))
    rep.add(check_control_totals(rows, reported_total))
    rep.add(check_date_consistency(rows))
    return rep
