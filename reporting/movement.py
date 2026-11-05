"""Movement analysis: ECL bridge (period-over-period)."""

from __future__ import annotations

from typing import Dict, List


def ecl_movement_bridge(
    opening_ecl: float,
    new_originations: float = 0.0,
    stage_transfers: float = 0.0,
    model_changes: float = 0.0,
    macro_changes: float = 0.0,
    write_offs: float = 0.0,
    recoveries: float = 0.0,
    closing_ecl: float = 0.0,
) -> Dict[str, float]:
    """ECL movement bridge: opening -> closing with drivers."""
    bridge = {
        "opening_ecl": opening_ecl,
        "new_originations": new_originations,
        "stage_transfers": stage_transfers,
        "model_changes": model_changes,
        "macro_changes": macro_changes,
        "write_offs": -write_offs,
        "recoveries": -recoveries,
        "closing_ecl": closing_ecl,
    }
    computed = opening_ecl + new_originations + stage_transfers + model_changes + macro_changes - write_offs - recoveries
    bridge["residual"] = round(closing_ecl - computed, 2)
    return bridge
