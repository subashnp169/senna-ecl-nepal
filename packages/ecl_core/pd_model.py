"""Professional PD model: TTC -> Vasicek -> PIT -> term structure.

Aligned with SAR Advisors methodology and Infinity's PD model design.
"""

from __future__ import annotations

from typing import Dict, List, Optional
from .pd import vasicek_pit_pd, marginal_pd_from_cumulative, discount_factors
from .ttc_pd import ttc_pd_from_default_rates
from .mev import credit_cycle_index_z, mev_regression_z


# Infinity's calibrated parameters (from PD_Model Design_ILBSL_2082.83.xlsx)
INFINITY_TTC_PD = 0.10407169307514164  # 10.4% long-run default rate
INFINITY_RHO = 0.12  # asset correlation (estimated)
# MEV regression coefficients (from Retail Equation sheet: lag1_X1, lag4_B2)
INFINITY_MEV_COEFFICIENTS = {
    "lag1_X1": 0.07348045881615474,   # GDP growth (lag 1)
    "lag4_B2": 0.011206928910920322,  # govt expenditure (lag 4)
}
INFINITY_MEV_INTERCEPT = -0.7504282824604251


class PDModel:
    """Professional PD model with TTC, Vasicek, MEV, and scenario projection."""

    def __init__(
        self,
        ttc_pd: float = INFINITY_TTC_PD,
        rho: float = INFINITY_RHO,
        mev_coefficients: Optional[Dict[str, float]] = None,
        mev_intercept: float = INFINITY_MEV_INTERCEPT,
        scenario_weights: Optional[Dict[str, float]] = None,
    ):
        self.ttc_pd = ttc_pd
        self.rho = rho
        self.mev_coefficients = mev_coefficients or INFINITY_MEV_COEFFICIENTS
        self.mev_intercept = mev_intercept
        self.scenario_weights = scenario_weights or {"optimistic": 0.2, "base": 0.5, "pessimistic": 0.3}

    def z_from_observed(self, observed_default_rate: float) -> float:
        """Compute credit cycle index Z from observed vs TTC default rate."""
        return credit_cycle_index_z(observed_default_rate, self.ttc_pd, self.rho)

    def z_from_mev(self, mev_values: Dict[str, float]) -> float:
        """Compute Z from macroeconomic variables via regression."""
        return mev_regression_z(mev_values, self.mev_coefficients, self.mev_intercept)

    def pit_pd(self, z: float) -> float:
        """Convert TTC PD to point-in-time PD using Vasicek."""
        return vasicek_pit_pd(self.ttc_pd, self.rho, z)

    def scenario_pds(self, z_base: float, z_optimistic: float = None, z_pessimistic: float = None) -> Dict[str, float]:
        """Compute PIT PDs for each scenario."""
        if z_optimistic is None:
            z_optimistic = z_base - 1.0  # favorable: lower z
        if z_pessimistic is None:
            z_pessimistic = z_base + 1.0  # adverse: higher z
        return {
            "optimistic": self.pit_pd(z_optimistic),
            "base": self.pit_pd(z_base),
            "pessimistic": self.pit_pd(z_pessimistic),
        }

    def lifetime_pd_term_structure(self, annual_pds: List[float]) -> List[float]:
        """Build marginal PD term structure from annual PIT PDs."""
        return marginal_pd_from_cumulative(annual_pds)

    def weighted_pd(self, scenario_pds: Dict[str, float]) -> float:
        """Probability-weighted PD across scenarios."""
        total_w = sum(self.scenario_weights.values())
        return sum(self.scenario_weights.get(k, 0) / total_w * v for k, v in scenario_pds.items())
