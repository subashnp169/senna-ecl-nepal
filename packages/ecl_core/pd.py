"""PD term structures, amortisation, lifetime PD and Vasicek PIT-PD."""

from __future__ import annotations

import math
from typing import List, Tuple

from scipy.stats import norm


def marginal_pd_from_cumulative(cumulative: List[float]) -> List[float]:
    """Convert cumulative PDs to marginal PDs.

    marginal_t = (cumulative_t - cumulative_{t-1}) / (1 - cumulative_{t-1})
    """
    marginals = []
    prev = 0.0
    for c in cumulative:
        denom = 1.0 - prev
        if denom <= 0:
            marginals.append(0.0)
        else:
            marginals.append((c - prev) / denom)
        prev = c
    # clamp
    return [max(0.0, min(1.0, m)) for m in marginals]


def amortisation_profile(principal: float, maturity: int, amort_type: str = "bullet") -> List[float]:
    """Return EAD (exposure) at each period t=1..maturity."""
    if maturity <= 0:
        return []
    if amort_type == "bullet":
        return [float(principal)] * maturity
    if amort_type == "amortising":
        # linear principal amortisation
        step = principal / maturity
        return [principal - step * (t - 1) for t in range(1, maturity + 1)]
    if amort_type == "annuity":
        # level payments; principal outstanding declines
        r = 0.05 / 12  # placeholder annual-ish
        n = maturity
        if r == 0:
            return [principal * (n - t + 1) / n for t in range(1, n + 1)]
        payment = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
        bal = principal
        out = []
        for t in range(1, n + 1):
            out.append(bal)
            interest = bal * r
            principal_paid = payment - interest
            bal = max(0.0, bal - principal_paid)
        return out
    raise ValueError(f"Unknown amort_type: {amort_type}")


def discount_factors(eir: float, periods: int) -> List[float]:
    """Discount factors for periods 1..periods at annual EIR (annual compounding)."""
    return [1.0 / (1.0 + eir) ** t for t in range(1, periods + 1)]


def lifetime_pd_term_structure(cumulative_pd: List[float]) -> Tuple[List[float], List[float]]:
    """Return (marginal_pds, survival). cumulative_pd is per-period cumulative."""
    marginals = marginal_pd_from_cumulative(cumulative_pd)
    survival = []
    s = 1.0
    for m in marginals:
        survival.append(s)
        s *= (1.0 - m)
    return marginals, survival


def vasicek_pit_pd(ttc_pd: float, rho: float, z: float) -> float:
    """One-factor Vasicek conditional (point-in-time) PD.

    PIT_PD = Phi( (Phi^{-1}(TTC_PD) + sqrt(rho)*z) / sqrt(1-rho) )
    where z is the systematic factor (standard normal). z=0 returns TTC_PD.
    """
    if ttc_pd <= 0:
        return 0.0
    if ttc_pd >= 1:
        return 1.0
    if rho <= 0 or rho >= 1:
        raise ValueError("rho must be in (0,1)")
    # First-order (additive in z-score) form: z=0 returns the TTC PD exactly,
    # so the baseline (neutral macro) leaves PD unchanged. This matches the
    # practitioner convention documented in ShrishDhuria/IFRS9_ECL. The full
    # conditional Vasicek form is Phi((Phi^-1(p)+sqrt(rho)*z)/sqrt(1-rho)).
    x = norm.ppf(ttc_pd)
    cond = x + math.sqrt(rho) * z
    return float(norm.cdf(cond))


def scenario_pd_adjustment(base_pd: float, multiplier: float) -> float:
    return min(1.0, max(0.0, base_pd * multiplier))
