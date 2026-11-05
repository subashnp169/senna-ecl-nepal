"""NRB Annex report templates (Annex 1-4)."""

from __future__ import annotations

from typing import Any, Dict, List
from datetime import datetime


def annex1_stage_summary(results: List[Dict[str, Any]], totals: Dict[str, Any]) -> Dict[str, Any]:
    """NRB Annex 1: Stage-wise ECL summary."""
    return {
        "title": "NRB Annex 1 - Stage-wise Expected Credit Loss Summary",
        "generated_at": datetime.now().isoformat(),
        "rows": [
            {"stage": "Stage 1", "count": totals["stage1"]["count"], "ead": totals["stage1"]["ead"], "ecl": totals["stage1"]["ecl"]},
            {"stage": "Stage 2", "count": totals["stage2"]["count"], "ead": totals["stage2"]["ead"], "ecl": totals["stage2"]["ecl"]},
            {"stage": "Stage 3", "count": totals["stage3"]["count"], "ead": totals["stage3"]["ead"], "ecl": totals["stage3"]["ecl"]},
            {"stage": "Total", "count": totals["count"], "ead": totals["total_ead"], "ecl": totals["total_ecl"]},
        ],
    }


def annex2_stage_migration(current: Dict[str, Any], previous: Dict[str, Any] = None) -> Dict[str, Any]:
    """NRB Annex 2: Stage migration matrix."""
    return {
        "title": "NRB Annex 2 - Stage Migration Matrix",
        "generated_at": datetime.now().isoformat(),
        "current": current,
        "previous": previous,
    }


def annex3_account_detail(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """NRB Annex 3: Account-level ECL detail."""
    return {
        "title": "NRB Annex 3 - Account-level ECL Detail",
        "generated_at": datetime.now().isoformat(),
        "count": len(results),
        "rows": results,
    }


def annex4_provision_comparison(ecl: float, prudential: float, provision: float) -> Dict[str, Any]:
    """NRB Annex 4: ECL vs prudential provision comparison."""
    return {
        "title": "NRB Annex 4 - ECL vs Prudential Provision Comparison",
        "generated_at": datetime.now().isoformat(),
        "ecl": ecl,
        "prudential": prudential,
        "provision_required": provision,
        "higher_of_variance": provision - min(ecl, prudential),
    }


def generate_nrb_annexes(results, totals, run_id) -> Dict[str, Any]:
    pc = totals.get("provision_comparison", {})
    return {
        "annex1": annex1_stage_summary(results, totals),
        "annex2": annex2_stage_migration(totals),
        "annex3": annex3_account_detail(results),
        "annex4": annex4_provision_comparison(
            totals["total_ecl"],
            pc.get("prudential", totals["total_ecl"] * 0.9),
            pc.get("provision_required", totals["total_ecl"]),
        ),
    }
