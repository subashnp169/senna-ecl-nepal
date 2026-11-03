"""EAD helpers."""

from __future__ import annotations


def ead_total(outstanding: float, undrawn: float = 0.0, ccf: float = 0.0) -> float:
    """EAD = outstanding + undrawn * credit conversion factor."""
    return outstanding + undrawn * ccf


def ead_with_accrued_interest(outstanding: float, accrued_interest: float = 0.0) -> float:
    return outstanding + accrued_interest
