"""Nepal regulatory rule pack (NRB NFRS 9 ECL Guidelines 2024 + amendments)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import yaml
import os


@dataclass
class NepalRulePack:
    version: str
    pd_floor: float = 0.025
    lgd_floor_no_history: float = 0.45
    collateral_haircut: float = 0.25
    govt_guarantee_lgd_min: float = 0.0
    subordinated_lgd_min: float = 0.75
    fx_govt_guarantee_lgd_min: float = 0.20
    stage1_months: int = 1
    stage2_min_months: int = 1
    stage2_max_months: int = 3
    stage3_months: int = 3
    poci_new_loan_to_prev_stage3: bool = True
    calendar: str = "BS"


def load_rule_pack(path: Optional[str] = None) -> NepalRulePack:
    if path and os.path.exists(path):
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        version = data.pop("version", "unknown")
        data.pop("description", None)
        return NepalRulePack(version=version, **{k: v for k, v in data.items() if k in NepalRulePack.__dataclass_fields__ and k != "version"})
    default_path = os.path.join(os.path.dirname(__file__), "rules", "nrb_ecl_2024_amended_2082_v2.yaml")
    if os.path.exists(default_path):
        return load_rule_pack(default_path)
    return NepalRulePack(version="nrb_ecl_2024_amended_2082_v2")


def calendar_month_stage(overdue_days: int) -> int:
    if overdue_days <= 30:
        return 1
    if overdue_days <= 90:
        return 2
    return 3


def apply_pd_floor(model_pd: float, floor: float = 0.025) -> float:
    return max(model_pd, floor)


def apply_lgd_floor(model_lgd: float, has_history: bool, floor_no_history: float = 0.45) -> float:
    if has_history:
        return model_lgd
    return max(model_lgd, floor_no_history)


def poci_determination(prev_stage: int, new_loan_in_current_period: bool) -> bool:
    return bool(new_loan_in_current_period and prev_stage == 3)


def class_d_mapping(nrb_classification: str) -> str:
    c = nrb_classification.strip().lower()
    if c in ("pass", "watchlist", "performing"):
        return "performing"
    if c in ("substandard", "doubtful"):
        return "non_performing"
    if c in ("loss",):
        return "written_off_candidate"
    return "unknown"
