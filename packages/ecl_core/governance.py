"""Governance: overlays, audit, maker-checker placeholders."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Overlay:
    name: str
    amount: float
    reason: str
    approved_by: str = ""
    status: str = "PENDING"  # PENDING / APPROVED / REJECTED


@dataclass
class AuditEntry:
    timestamp: str
    actor: str
    action: str
    detail: str


def apply_overlays(base_ecl: float, overlays: List[Overlay]) -> float:
    total = base_ecl
    for o in overlays:
        if o.status == "APPROVED":
            total += o.amount
    return total
