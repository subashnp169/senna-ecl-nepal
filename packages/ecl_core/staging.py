"""Staging engine: IFRS 9 stage classification with SICR waterfall."""

from __future__ import annotations

from typing import List, Optional

from .types import Loan, Stage, StagingResult, SICRConfig


RATING_SCALE = [
    "AAA", "AA+", "AA", "AA-",
    "A+", "A", "A-",
    "BBB+", "BBB", "BBB-",
    "BB+", "BB", "BB-",
    "B+", "B", "B-",
    "CCC", "CCC+", "CCC-", "CC", "C", "D",
]

# normalise to a canonical notch index
_CANONICAL = [
    "AAA", "AA+", "AA", "AA-",
    "A+", "A", "A-",
    "BBB+", "BBB", "BBB-",
    "BB+", "BB", "BB-",
    "B+", "B", "B-",
    "CCC", "D",
]


def _notch(rating: str) -> int:
    r = rating.strip().upper()
    if r in ("CCC/C", "CCC+", "CCC-"):
        r = "CCC"
    if r not in _CANONICAL:
        # best-effort prefix match
        for c in _CANONICAL:
            if r.startswith(c.rstrip("+-")):
                r = c
                break
    if r not in _CANONICAL:
        raise ValueError(f"Unknown rating: {rating}")
    return _CANONICAL.index(r)


def notch_distance(rating_from: str, rating_to: str) -> int:
    """Signed notch distance. Positive = downgrade."""
    return _notch(rating_to) - _notch(rating_from)


def is_investment_grade(rating: str) -> bool:
    return _notch(rating) <= _CANONICAL.index("BBB-")


# S&P-style 1Y PD table (global) - illustrative, must be replaced with institution data
SP_1Y_PD = {
    "AAA": 0.0001, "AA+": 0.0002, "AA": 0.0003, "AA-": 0.0005,
    "A+": 0.0008, "A": 0.0012, "A-": 0.0018,
    "BBB+": 0.0025, "BBB": 0.0040, "BBB-": 0.0065,
    "BB+": 0.0100, "BB": 0.0150, "BB-": 0.0220,
    "B+": 0.0350, "B": 0.0550, "B-": 0.0850,
    "CCC": 0.2612, "D": 1.0,
}

SP_1Y_PD_EUROPE = {
    "AAA": 0.00005, "AA+": 0.0001, "AA": 0.0002, "AA-": 0.0004,
    "A+": 0.0006, "A": 0.0010, "A-": 0.0015,
    "BBB+": 0.0020, "BBB": 0.0036, "BBB-": 0.0055,
    "BB+": 0.0090, "BB": 0.0140, "BB-": 0.0200,
    "B+": 0.0320, "B": 0.0500, "B-": 0.0800,
    "CCC": 0.2626, "D": 1.0,
}


def _get_1y_pd(rating: str, region: str) -> float:
    table = SP_1Y_PD_EUROPE if region == "europe" else SP_1Y_PD
    r = rating.strip().upper()
    if r in ("CCC/C", "CCC+", "CCC-"):
        r = "CCC"
    if r == "D":
        return 1.0
    if r in table:
        return table[r]
    # prefix fallback
    for c in table:
        if r.startswith(c.rstrip("+-")):
            return table[c]
    return 0.004  # conservative default


def _rating_category(rating: str) -> str:
    categories = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC"]
    r = rating.strip().upper()
    if r in categories:
        return r
    if r == "D":
        return "CCC"
    for cat in categories:
        if r.startswith(cat.rstrip("+-")):
            return cat
    return "B"


def classify_stage(loan: Loan, config: SICRConfig = SICRConfig()) -> StagingResult:
    """IFRS 9 stage classification waterfall (Stage 3 -> Stage 2 -> Stage 1)."""
    triggers: List[str] = []
    detail = {
        "origination_rating": loan.origination_rating,
        "current_rating": loan.current_rating,
        "days_past_due": loan.days_past_due,
        "qualitative_flags": loan.qualitative_flags,
    }

    # ---- Stage 3 (credit-impaired) ----
    if loan.days_past_due >= config.dpd_stage3_threshold:
        triggers.append(f"DPD >= {config.dpd_stage3_threshold} (default backstop)")
    if loan.current_rating.strip().upper() == "D":
        triggers.append("Rating = D (default)")
    for flag in loan.qualitative_flags:
        if flag in config.qualitative_stage3_triggers:
            triggers.append(f"Qualitative flag: {flag}")
    if loan.is_poci:
        triggers.append("POCI (purchased/originated credit impaired)")

    if triggers:
        detail["stage3_triggers"] = triggers
        return StagingResult(stage=Stage.STAGE_3, triggers_fired=triggers, detail=detail)

    # ---- Stage 2 (SICR) ----
    notches = notch_distance(loan.origination_rating, loan.current_rating)
    detail["notch_change"] = notches
    if notches >= config.notch_downgrade_threshold:
        triggers.append(
            f"Downgrade {notches} notches ({loan.origination_rating} -> {loan.current_rating}) "
            f">= {config.notch_downgrade_threshold}"
        )

    pd_orig = loan.origination_pd if loan.origination_pd is not None else _get_1y_pd(loan.origination_rating, loan.region)
    pd_curr = loan.current_pd_override if loan.current_pd_override is not None else _get_1y_pd(loan.current_rating, loan.region)
    detail["pd_origination"] = pd_orig
    detail["pd_current"] = pd_curr
    if pd_orig > 0:
        pd_ratio = pd_curr / pd_orig
        pd_abs = pd_curr - pd_orig
        detail["pd_ratio"] = round(pd_ratio, 4)
        detail["pd_abs_change"] = round(pd_abs, 6)
        if pd_ratio >= config.pd_relative_threshold and pd_abs >= config.pd_absolute_threshold:
            triggers.append(
                f"PD ratio {pd_ratio:.2f}x >= {config.pd_relative_threshold:.1f}x "
                f"AND abs change {pd_abs:.4%} >= {config.pd_absolute_threshold:.4%}"
            )

    if loan.days_past_due >= config.dpd_stage2_threshold:
        triggers.append(
            f"DPD = {loan.days_past_due} >= {config.dpd_stage2_threshold} (IFRS 9 A5.5.11 rebuttable presumption)"
        )
    for flag in loan.qualitative_flags:
        if flag in config.qualitative_stage2_triggers:
            triggers.append(f"Qualitative flag: {flag}")

    if triggers and config.allow_low_credit_risk_exemption and is_investment_grade(loan.current_rating):
        detail["low_credit_risk_exemption"] = True
        return StagingResult(
            stage=Stage.STAGE_1,
            triggers_fired=[f"SICR triggers overridden by low-credit-risk exemption (IG): {triggers}"],
            detail=detail,
        )

    if triggers:
        detail["stage2_triggers"] = triggers
        return StagingResult(stage=Stage.STAGE_2, triggers_fired=triggers, detail=detail)

    # ---- Stage 1 ----
    return StagingResult(
        stage=Stage.STAGE_1,
        triggers_fired=["No SICR triggers fired - loan remains performing"],
        detail=detail,
    )
