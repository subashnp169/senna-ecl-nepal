"""SICR configuration is in types; this module holds SICR detection helpers."""

from __future__ import annotations

from typing import List


def sicr_triggers_summary(triggers: List[str]) -> str:
    return "; ".join(triggers) if triggers else "none"
