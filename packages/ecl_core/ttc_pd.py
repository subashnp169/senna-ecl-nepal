"""Through-the-cycle (TTC) PD estimation from default migration data."""

from __future__ import annotations

from typing import List, Dict
import math


def ttc_pd_from_default_rates(default_rates: List[float]) -> float:
    """TTC PD = simple average of annual default rates (long-run)."""
    if not default_rates:
        return 0.0
    return sum(default_rates) / len(default_rates)


def ttc_pd_by_segment(histories: Dict[str, List[float]]) -> Dict[str, float]:
    """Compute TTC PD per segment from {segment: [annual default rates]}."""
    return {seg: ttc_pd_from_default_rates(rates) for seg, rates in histories.items()}


def default_rate(total_loan: float, defaulted: float) -> float:
    if total_loan <= 0:
        return 0.0
    return defaulted / total_loan
