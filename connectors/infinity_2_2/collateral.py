"""Adapter: read Infinity collateral register (FID Collateral Loan.xlsx)."""

from __future__ import annotations

from typing import Dict, List
import pandas as pd


def read_collateral(path: str) -> List[Dict]:
    """Read 'all security' sheet and return list of {account_id, collateral_type, fmv, dv}.

    The FID file's 'all security' sheet has: member_id, cbs_mem_id, helper, full_name,
    securities_id, fmv, dv. We map cbs_mem_id -> account linkage externally.
    """
    try:
        df = pd.read_excel(path, sheet_name="all security")
    except Exception:
        try:
            df = pd.read_excel(path, sheet_name="all_security")
        except Exception:
            return []
    out = []
    for _, row in df.iterrows():
        out.append({
            "member_id": row.get("member_id"),
            "cbs_mem_id": row.get("cbs_mem_id"),
            "full_name": row.get("full_name"),
            "securities_id": row.get("securities_id"),
            "fmv": row.get("fmv"),
            "dv": row.get("dv"),
        })
    return out


def collateral_coverage(collateral_list: List[Dict], loan_accounts: List[str]) -> dict:
    """Compute how many loan accounts have collateral data."""
    coll_ids = set(str(c.get("cbs_mem_id")) for c in collateral_list if c.get("cbs_mem_id"))
    loan_set = set(loan_accounts)
    matched = loan_set & coll_ids
    return {
        "total_loans": len(loan_set),
        "loans_with_collateral": len(matched),
        "coverage_pct": round(len(matched) / len(loan_set) * 100, 2) if loan_set else 0.0,
        "total_collateral_records": len(collateral_list),
    }
