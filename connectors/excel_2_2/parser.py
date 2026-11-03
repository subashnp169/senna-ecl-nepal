from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass
class ParseResult:
    rows: list[dict[str, Any]]
    errors: list[str]
    control_totals: dict[str, float | int]


ALIASES = {
    "customer_code": ["CUSTOMER_CODE"],
    "account_no": ["AC_NO"],
    "principal_outstanding": ["F_OUTSTANDING_PRICIPAL", "F_OUTSTANDING_PRINCIPAL"],
    "interest_outstanding": ["F_OUTSTANDING_INTEREST"],
    "overdue_days": ["OVERDUE_DAYS"],
    "classification_code": ["CLASSIFICATION"],
    "existing_provision": ["PROVISION"],
}


def _find_column(columns: list[str], candidates: list[str]) -> str | None:
    normalized = {str(c).strip().upper(): c for c in columns}
    for candidate in candidates:
        if candidate.upper() in normalized:
            return normalized[candidate.upper()]
    return None


def parse_2_2_workbook(path: str | Path) -> ParseResult:
    df = pd.read_excel(path)
    mapping: dict[str, str] = {}
    errors: list[str] = []
    for target, candidates in ALIASES.items():
        source = _find_column(list(df.columns), candidates)
        if source is None:
            errors.append(f"Missing required column for {target}: {candidates}")
        else:
            mapping[target] = source
    if errors:
        return ParseResult([], errors, {})

    out = pd.DataFrame({target: df[source] for target, source in mapping.items()})
    for field in ["principal_outstanding", "interest_outstanding", "overdue_days", "existing_provision"]:
        out[field] = pd.to_numeric(out[field], errors="coerce")
    if out["account_no"].isna().any():
        errors.append("One or more rows have blank account numbers")
    if out["customer_code"].isna().any():
        errors.append("One or more rows have blank customer codes")
    duplicates = int(out["account_no"].duplicated().sum())
    if duplicates:
        errors.append(f"Duplicate account numbers found: {duplicates}")

    totals = {
        "row_count": int(len(out)),
        "customer_count": int(out["customer_code"].nunique(dropna=True)),
        "account_count": int(out["account_no"].nunique(dropna=True)),
        "principal_outstanding": float(out["principal_outstanding"].fillna(0).sum()),
        "interest_outstanding": float(out["interest_outstanding"].fillna(0).sum()),
        "existing_provision": float(out["existing_provision"].fillna(0).sum()),
    }
    return ParseResult(out.where(pd.notnull(out), None).to_dict("records"), errors, totals)
