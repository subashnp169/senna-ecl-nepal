"""Core ECL calculation: single-period, lifetime, scenarios, discounting."""

from __future__ import annotations

from decimal import Decimal
from typing import List, Dict

from .types import ECLInput
from .pd import amortisation_profile, discount_factors, marginal_pd_from_cumulative
from .lgd import lgd_floor_applied


def calculate_ecl_decimal(inp: ECLInput) -> Decimal:  # type: ignore[name-defined]
    """Transparent single-period ECL component (Decimal, quantized)."""
    for name, rate in (("pd", inp.pd), ("lgd", inp.lgd), ("discount_factor", inp.discount_factor)):
        if rate < 0:
            raise ValueError(f"{name} cannot be negative")
    if inp.ead < 0:
        raise ValueError("ead cannot be negative")
    return (inp.pd * inp.lgd * inp.ead * inp.discount_factor).quantize(Decimal("0.01"))


def ecl_single(pd: float, lgd: float, ead: float, discount_factor: float = 1.0) -> float:
    return pd * lgd * ead * discount_factor


def lifetime_ecl(
    principal: float,
    pd_12m: float,
    marginal_pds: List[float],
    lgd: float,
    eir: float,
    amort_type: str = "bullet",
    stage: int = 2,
) -> dict:
    """Compute 12-month and lifetime ECL.

    For Stage 1: 12-month ECL uses 12m PD.
    For Stage 2/3: lifetime ECL sums discounted marginal PD * LGD * EAD over horizon.
    """
    maturity = len(marginal_pds) if marginal_pds else 1
    eads = amortisation_profile(principal, maturity, amort_type)
    dfs = discount_factors(eir, maturity)

    # 12-month ECL (first period)
    m0 = marginal_pds[0] if marginal_pds else pd_12m
    ecl_12m = ecl_single(m0, lgd, eads[0] if eads else principal, dfs[0] if dfs else 1.0)

    # Lifetime ECL
    survival = 1.0
    ecl_life = 0.0
    cum_pd = 0.0
    for t in range(maturity):
        m_pd = marginal_pds[t] if t < len(marginal_pds) else 0.0
        # probability of default in period t = survival * marginal
        pd_period = survival * m_pd
        ead_t = eads[t] if t < len(eads) else principal
        df_t = dfs[t] if t < len(dfs) else 1.0
        ecl_life += pd_period * lgd * ead_t * df_t
        survival *= (1.0 - m_pd)
        cum_pd = 1.0 - survival
    # If no term structure provided, fall back to 12m PD over horizon
    if not marginal_pds:
        ecl_life = ecl_single(pd_12m, lgd, principal, 1.0)
    return {
        "ecl_12m": round(ecl_12m, 2),
        "ecl_lifetime": round(ecl_life, 2),
        "cumulative_pd": round(cum_pd, 6) if marginal_pds else pd_12m,
    }


def scenario_weighted_ecl(
    base_ecl: float,
    scenarios: List[dict],
) -> dict:
    """Probability-weighted ECL across macro scenarios.

    scenarios: list of {name, weight, ecl} or {name, weight, multiplier}.
    """
    total_weight = sum(s.get("weight", 0.0) for s in scenarios)
    if total_weight <= 0:
        raise ValueError("scenario weights must sum to > 0")
    weighted = 0.0
    breakdown = {}
    for s in scenarios:
        w = s.get("weight", 0.0) / total_weight
        ecl = s.get("ecl", base_ecl * s.get("multiplier", 1.0))
        weighted += w * ecl
        breakdown[s["name"]] = {"weight": w, "ecl": ecl}
    return {"weighted_ecl": round(weighted, 2), "breakdown": breakdown}


def portfolio_aggregate(results: List[dict]) -> dict:
    """Aggregate loan-level ECL results into portfolio summary."""
    totals = {
        "count": 0,
        "total_ead": 0.0,
        "total_ecl": 0.0,
        "stage1": {"count": 0, "ead": 0.0, "ecl": 0.0},
        "stage2": {"count": 0, "ead": 0.0, "ecl": 0.0},
        "stage3": {"count": 0, "ead": 0.0, "ecl": 0.0},
    }
    for r in results:
        stage = r["stage"]
        key = f"stage{stage.value if hasattr(stage, 'value') else stage}"
        totals["count"] += 1
        totals["total_ead"] += r.get("ead", r.get("principal", 0.0))
        totals["total_ecl"] += r["ecl_applied"]
        bucket = totals[f"stage{stage.value if hasattr(stage, 'value') else stage}"]
        bucket["count"] += 1
        bucket["ead"] += r.get("ead", r.get("principal", 0.0))
        bucket["ecl"] += r["ecl_applied"]
    for k in ("stage1", "stage2", "stage3"):
        ead = totals[k]["ead"]
        totals[k]["coverage"] = round(totals[k]["ecl"] / ead * 100, 4) if ead > 0 else 0.0
    totals["coverage"] = round(totals["total_ecl"] / totals["total_ead"] * 100, 4) if totals["total_ead"] > 0 else 0.0
    return totals
