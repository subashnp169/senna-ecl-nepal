"""Macroeconomic-variable (MEV) based credit cycle index (Z)."""

from __future__ import annotations

from typing import List, Dict
import math


def credit_cycle_index_z(observed_default_rate: float, ttc_pd: float, rho: float) -> float:
    """Compute the standardized credit-cycle index Z from observed vs TTC default rate.

    Z = (Phi^-1(observed) - Phi^-1(TTC)) / sqrt(1 - rho)

    Convention: Z positive = downturn (observed defaults exceed TTC).
    (Matches Infinity's PD workbook: Z_Retail positive in bad periods.)
    """
    from scipy.stats import norm
    if observed_default_rate <= 0 or observed_default_rate >= 1:
        observed_default_rate = min(max(observed_default_rate, 1e-6), 1 - 1e-6)
    if ttc_pd <= 0 or ttc_pd >= 1:
        ttc_pd = min(max(ttc_pd, 1e-6), 1 - 1e-6)
    if rho <= 0 or rho >= 1:
        raise ValueError("rho must be in (0,1)")
    return (norm.ppf(observed_default_rate) - norm.ppf(ttc_pd)) / math.sqrt(1.0 - rho)


def mev_regression_z(mev_values: Dict[str, float], coefficients: Dict[str, float],
                     intercept: float = 0.0) -> float:
    """Compute Z from a linear MEV regression: Z = intercept + sum(coef_i * mev_i).

    Coefficients and intercept come from the institution's calibrated model
    (e.g. Infinity's Retail Equation sheet).
    """
    z = intercept
    for k, v in mev_values.items():
        z += coefficients.get(k, 0.0) * v
    return z
