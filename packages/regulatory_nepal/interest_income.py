"""Interest income recognition per NRB Guidance Note 2025."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InterestIncomeRecord:
    account_id: str
    previous_quarter_stage: int
    current_quarter_stage: int
    gross_carrying_amount: float
    amortised_cost: float
    coupon_rate: float
    eir: float
    accrued_interest_receivable: float = 0.0
    interest_suspense: float = 0.0
    cash_interest_collected: float = 0.0
    is_poci: bool = False


def interest_income_method(stage: int) -> str:
    """Interest recognition method by stage."""
    if stage == 3:
        return "cash_basis"
    return "effective_interest_rate"


def quarterly_interest_income(rec: InterestIncomeRecord) -> dict:
    """Compute quarterly interest income using previous-quarter stage (NRB 2025)."""
    method = interest_income_method(rec.previous_quarter_stage)
    if method == "cash_basis":
        income = rec.cash_interest_collected
    else:
        income = rec.gross_carrying_amount * rec.eir / 4.0  # quarterly
    return {
        "account_id": rec.account_id,
        "method": method,
        "interest_income": round(income, 2),
        "accrued_interest_receivable": rec.accrued_interest_receivable,
        "interest_suspense": rec.interest_suspense,
    }
