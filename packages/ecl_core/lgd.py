"""LGD estimation helpers."""

from __future__ import annotations

from typing import Optional


def lgd_from_collateral(
    ead: float,
    collateral_value: float,
    haircut: float = 0.25,
    recovery_cost: float = 0.0,
    floor: float = 0.0,
) -> float:
    """LGD = 1 - (collateral*(1-haircut) - costs) / EAD, floored."""
    if ead <= 0:
        return 1.0
    recovery = collateral_value * (1.0 - haircut) - recovery_cost
    recovery = max(0.0, recovery)
    lgd = 1.0 - recovery / ead
    lgd = max(floor, min(1.0, lgd))
    return lgd


def lgd_floor_applied(model_lgd: float, regulatory_floor: float) -> float:
    return max(model_lgd, regulatory_floor)


def downturn_lgd(base_lgd: float, downturn_multiplier: float = 1.25) -> float:
    return min(1.0, base_lgd * downturn_multiplier)


def recovery_rate_to_lgd(recovery_rate: float) -> float:
    return max(0.0, min(1.0, 1.0 - recovery_rate))
