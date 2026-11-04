"""Ingestion pipeline: parse vendor Excel/CSV, validate, produce immutable snapshot."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from packages.ecl_core.types import Loan


@dataclass
class ValidationError:
    sheet: str
    row: int
    field: str
    message: str
    severity: str = "error"  # error / warning


@dataclass
class IngestionResult:
    snapshot_id: str
    as_of_date: str
    institution_id: str
    loans: List[Loan]
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    control_totals: Dict[str, Any] = field(default_factory=dict)
    checksum: str = ""

    @property
    def ok(self) -> bool:
        return not any(e.severity == "error" for e in self.errors)


REQUIRED_LOAN_FIELDS = ["account_id", "customer_id", "outstanding", "origination_date", "maturity_date"]


def _read_sheet(path: str, sheet: str) -> pd.DataFrame:
    try:
        return pd.read_excel(path, sheet_name=sheet)
    except Exception:
        # try csv fallback
        csv_path = path.replace(".xlsx", f"_{sheet}.csv")
        if os.path.exists(csv_path):
            return pd.read_csv(csv_path)
        return pd.DataFrame()


import os


def ingest_excel(path: str, institution_id: str, as_of_date: str) -> IngestionResult:
    errors: List[ValidationError] = []
    warnings: List[ValidationError] = []

    loans_df = _read_sheet(path, "Loan_Master")
    if loans_df.empty:
        errors.append(ValidationError("Loan_Master", 0, "*", "Loan_Master sheet missing or empty", "error"))
        return IngestionResult(snapshot_id="", as_of_date=as_of_date, institution_id=institution_id, loans=[], errors=errors)

    # required fields
    for f in REQUIRED_LOAN_FIELDS:
        if f not in loans_df.columns:
            errors.append(ValidationError("Loan_Master", 0, f, f"Required column '{f}' missing", "error"))
    if errors:
        return IngestionResult(snapshot_id="", as_of_date=as_of_date, institution_id=institution_id, loans=[], errors=errors)

    loans: List[Loan] = []
    for idx, row in loans_df.iterrows():
        r = idx + 2  # excel row (header=1)
        try:
            account_id = str(row["account_id"]).strip()
            customer_id = str(row["customer_id"]).strip()
            outstanding = float(row["outstanding"])
        except Exception as e:
            errors.append(ValidationError("Loan_Master", r, "outstanding", f"Invalid value: {e}", "error"))
            continue
        if outstanding < 0:
            errors.append(ValidationError("Loan_Master", r, "outstanding", "outstanding cannot be negative", "error"))
            continue
        if not account_id or account_id == "nan":
            errors.append(ValidationError("Loan_Master", r, "account_id", "account_id required", "error"))
            continue

        def g(col, default=None):
            v = row.get(col, default)
            if pd.isna(v):
                return default
            return v

        orig_rating = str(g("origination_rating", "BBB"))
        curr_rating = str(g("current_rating", orig_rating))
        dpd = int(g("dpd", 0) or 0)
        if dpd < 0:
            errors.append(ValidationError("Loan_Master", r, "dpd", "dpd cannot be negative", "error"))
            continue

        watchlist = bool(g("watchlist", False))
        forbearance = bool(g("forbearance", False))
        flags = []
        if watchlist:
            flags.append("watchlist")
        if forbearance:
            flags.append("forbearance")

        loan = Loan(
            name=account_id,
            principal=outstanding,
            origination_rating=orig_rating,
            current_rating=curr_rating,
            lgd=float(g("lgd", 0.45) or 0.45),
            eir=float(g("eir", 0.05) or 0.05),
            maturity=1,  # placeholder; computed from dates
            amort_type="bullet",
            region="global",
            days_past_due=dpd,
            qualitative_flags=flags,
            account_id=account_id,
            customer_id=customer_id,
            sector=str(g("sector", "general")),
            collateral_value=float(g("collateral_value", 0.0) or 0.0),
            undrawn_limit=float(g("undrawn_limit", 0.0) or 0.0),
            is_poci=False,
        )
        # maturity in years from dates
        try:
            od = pd.to_datetime(g("origination_date"))
            md = pd.to_datetime(g("maturity_date"))
            loan.maturity = max(1, int((md - od).days / 365) or 1)
        except Exception:
            loan.maturity = 3
        loans.append(loan)

    # control totals
    total_outstanding = float(loans_df["outstanding"].sum()) if "outstanding" in loans_df.columns else 0.0
    snapshot_id = hashlib.sha256(f"{institution_id}|{as_of_date}|{len(loans)}".encode()).hexdigest()[:16]
    checksum = hashlib.sha256(json.dumps([l.account_id for l in loans]).encode()).hexdigest()

    result = IngestionResult(
        snapshot_id=snapshot_id,
        as_of_date=as_of_date,
        institution_id=institution_id,
        loans=loans,
        errors=errors,
        warnings=warnings,
        control_totals={"total_outstanding": total_outstanding, "loan_count": len(loans)},
        checksum=checksum,
    )
    return result
