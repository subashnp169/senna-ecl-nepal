"""NRB annex / regulatory reporting helpers."""

from __future__ import annotations

from typing import List, Dict


def provision_comparison(ecl: float, prudential: float) -> Dict[str, float]:
    """NRB requires provision = max(ECL, prudential provision)."""
    final = max(ecl, prudential)
    return {
        "ecl": round(ecl, 2),
        "prudential": round(prudential, 2),
        "provision_required": round(final, 2),
        "higher_of_variance": round(final - min(ecl, prudential), 2),
    }


def stage_summary_rows(results: List[dict]) -> List[dict]:
    rows = []
    for r in results:
        rows.append({
            "account": r.get("loan_name") or r.get("account_id"),
            "stage": r.get("stage"),
            "ead": r.get("ead", r.get("principal", 0.0)),
            "ecl": r.get("ecl_applied", 0.0),
        })
    return rows
