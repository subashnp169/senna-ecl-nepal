"""SICR indicators per NRB 2024 / SAR Advisors methodology."""

from __future__ import annotations

from typing import List, Tuple


def sicr_quantitative_triggers(
    days_past_due: int,
    current_pd: float,
    origination_pd: float,
    origination_rating: str,
    current_rating: str,
    notch_downgrade_threshold: int = 2,
) -> List[str]:
    """Return list of quantitative SICR triggers fired (NRB 2024 / SAR)."""
    triggers = []
    # 30 DPD backstop
    if days_past_due >= 30:
        triggers.append(f"DPD >= 30 (backstop) [actual {days_past_due}]")
    # Absolute lifetime PD >= 5%
    if current_pd >= 0.05:
        triggers.append(f"Absolute lifetime PD >= 5% [actual {current_pd:.2%}]")
    # Relative lifetime PD increase >= 100%
    if origination_pd > 0 and (current_pd / origination_pd) >= 2.0:
        triggers.append(f"Relative lifetime PD increase >= 100% [ratio {(current_pd/origination_pd):.2f}x]")
    # Risk rating downgrade by N notches or to non-investment grade
    try:
        from .staging import notch_distance
        notches = notch_distance(origination_rating, current_rating)
        if notches >= notch_downgrade_threshold:
            triggers.append(f"Rating downgrade {notches} notches >= {notch_downgrade_threshold}")
        # to non-investment grade
        from .staging import is_investment_grade
        if is_investment_grade(origination_rating) and not is_investment_grade(current_rating):
            triggers.append("Downgraded to non-investment grade")
    except Exception:
        pass
    return triggers


def probation_period_exit_stage3(restructured: bool = False) -> int:
    """Minimum probation days before exiting Stage 3."""
    return 730 if restructured else 180


def stage_transfer_rules() -> dict:
    return {
        "stage2_to_stage1": "evidence of significant reduction in credit risk (Board-approved criteria)",
        "stage3_exit_probation_days": 180,
        "stage3_restructured_exit_probation_days": 730,
        "restructured_to_stage1": "no move to 12-month ECL without sufficient evidence of improved credit risk",
    }
