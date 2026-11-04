"""Quarterly interest-income evidence pack (NRB 2025)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict
from packages.regulatory_nepal import quarterly_interest_income, InterestIncomeRecord


@dataclass
class EvidencePack:
    period: str
    institution_id: str
    records: List[Dict]
    total_interest_income: float
    total_accrued: float
    total_suspense: float


def build_evidence_pack(period: str, institution_id: str, records: List[InterestIncomeRecord]) -> EvidencePack:
    out = []
    total_income = 0.0
    total_accrued = 0.0
    total_suspense = 0.0
    for r in records:
        res = quarterly_interest_income(r)
        out.append(res)
        total_income += res["interest_income"]
        total_accrued += r.accrued_interest_receivable
        total_suspense += r.interest_suspense
    return EvidencePack(
        period=period,
        institution_id=institution_id,
        records=out,
        total_interest_income=round(total_income, 2),
        total_accrued=round(total_accrued, 2),
        total_suspense=round(total_suspense, 2),
    )
