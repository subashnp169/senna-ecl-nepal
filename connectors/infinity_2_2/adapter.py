"""Adapter: convert raw Infinity NRB 2.2 report to canonical IngestionResult."""

from __future__ import annotations

import hashlib
import pandas as pd
from typing import List, Optional
from connectors.excel_2_2.ingestion import IngestionResult, ValidationError
from packages.ecl_core.types import Loan


CLS_MAP = {1.0: ("Pass", "BBB"), 1.1: ("Watchlist", "BB"), 3.0: ("Substandard", "B"),
           4.0: ("Doubtful", "CCC"), 5.0: ("Loss", "D")}


def _cls(v):
    try:
        return float(v)
    except Exception:
        return 1.0


def adapt_infinity_report(path: str, institution_id: str, as_of_date: str) -> IngestionResult:
    errors: List[ValidationError] = []
    warnings: List[ValidationError] = []

    try:
        df = pd.read_excel(path, sheet_name="Report Data")
    except Exception as e:
        # maybe already canonical
        try:
            df = pd.read_excel(path, sheet_name="Loan_Master")
        except Exception:
            errors.append(ValidationError("Report", 0, "*", f"Cannot read sheet: {e}", "error"))
            return IngestionResult(snapshot_id="", as_of_date=as_of_date, institution_id=institution_id, loans=[], errors=errors)

    if "F_OUTSTANDING_PRICIPAL" not in df.columns:
        errors.append(ValidationError("Report Data", 0, "F_OUTSTANDING_PRICIPAL", "Not an Infinity 2.2 report", "error"))
        return IngestionResult(snapshot_id="", as_of_date=as_of_date, institution_id=institution_id, loans=[], errors=errors)

    loans: List[Loan] = []
    seen = set()
    for idx, row in df.iterrows():
        r = idx + 2
        try:
            outstanding = float(row.get("F_OUTSTANDING_PRICIPAL", 0) or 0)
        except Exception:
            errors.append(ValidationError("Report Data", r, "F_OUTSTANDING_PRICIPAL", "invalid outstanding", "error"))
            continue
        if outstanding <= 0:
            continue
        ac_no = str(row.get("AC_NO", "")).strip()
        if not ac_no or ac_no == "nan":
            ac_no = f"ACC{idx+1:05d}"
        if ac_no in seen:
            errors.append(ValidationError("Report Data", r, "AC_NO", f"duplicate account {ac_no}", "warning"))
            warnings.append(ValidationError("Report Data", r, "AC_NO", f"duplicate account {ac_no}", "warning"))
        seen.add(ac_no)

        cls = _cls(row.get("CLASSIFICATION", 1.0))
        nrb_cls, rating = CLS_MAP.get(cls, ("Pass", "BBB"))
        dpd = int(row.get("OVERDUE_DAYS", 0) or 0)
        if dpd < 0:
            dpd = 0
        try:
            rate = float(row.get("INT_RATE", 12) or 12) / 100.0
        except Exception:
            rate = 0.12
        try:
            limit = float(row.get("F_APPROVED_LIMIT", 0) or 0)
        except Exception:
            limit = 0.0
        undrawn = max(0.0, limit - outstanding) if limit > 0 else 0.0
        try:
            cust_code = str(row.get("CUSTOMER_CODE", "")).strip()
        except Exception:
            cust_code = ""
        if not cust_code or cust_code == "nan":
            cust_code = ac_no
        watchlist = (cls == 1.1)
        flags = ["watchlist"] if watchlist else []

        loan = Loan(
            name=ac_no,
            principal=outstanding,
            origination_rating=rating,
            current_rating=rating,
            lgd=0.45,
            eir=rate if rate > 0 else 0.12,
            maturity=3,
            amort_type="bullet",
            region="global",
            days_past_due=dpd,
            qualitative_flags=flags,
            account_id=ac_no,
            customer_id=cust_code,
            sector=str(row.get("CAT_NAME", "General")),
            collateral_value=0.0,
            undrawn_limit=undrawn,
            is_poci=False,
        )
        loans.append(loan)

    total_outstanding = float(df["F_OUTSTANDING_PRICIPAL"].fillna(0).sum())
    snapshot_id = hashlib.sha256(f"{institution_id}|{as_of_date}|{len(loans)}".encode()).hexdigest()[:16]
    checksum = hashlib.sha256(",".join(l.account_id for l in loans).encode()).hexdigest()

    return IngestionResult(
        snapshot_id=snapshot_id,
        as_of_date=as_of_date,
        institution_id=institution_id,
        loans=loans,
        errors=errors,
        warnings=warnings,
        control_totals={"total_outstanding": total_outstanding, "loan_count": len(loans)},
        checksum=checksum,
    )
