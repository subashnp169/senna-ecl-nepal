"""Shared types for the international ECL core."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Tuple


class Stage(Enum):
    STAGE_1 = 1  # 12-month ECL
    STAGE_2 = 2  # Lifetime ECL (SICR)
    STAGE_3 = 3  # Lifetime ECL (credit-impaired)


class AmortType(Enum):
    BULLET = "bullet"
    ANNUITY = "annuity"
    AMORTISING = "amortising"


@dataclass(frozen=True)
class ECLInput:
    """Single-period ECL component inputs."""

    pd: Decimal
    lgd: Decimal
    ead: Decimal
    discount_factor: Decimal = Decimal("1")

    def __post_init__(self) -> None:
        for name, rate in (("pd", self.pd), ("lgd", self.lgd), ("discount_factor", self.discount_factor)):
            if rate < 0:
                raise ValueError(f"{name} cannot be negative")
        if self.ead < 0:
            raise ValueError("ead cannot be negative")


@dataclass
class Loan:
    """Loan-level record used by the international core."""

    name: str
    principal: float  # EAD proxy / outstanding balance
    origination_rating: str
    current_rating: str
    lgd: float
    eir: float
    maturity: int  # remaining maturity (years)
    amort_type: str = "bullet"
    region: str = "global"
    days_past_due: int = 0
    qualitative_flags: List[str] = field(default_factory=list)
    lgd_downturn: Optional[float] = None
    origination_pd: Optional[float] = None  # if known
    current_pd_override: Optional[float] = None
    is_poci: bool = False  # purchased/originated credit impaired
    collateral_value: float = 0.0
    undrawn_limit: float = 0.0
    sector: str = "general"
    customer_id: Optional[str] = None
    account_id: Optional[str] = None


@dataclass
class SICRConfig:
    """Configurable SICR thresholds (IFRS 9 B5.5.17-18, EBA GL/2017/06)."""

    notch_downgrade_threshold: int = 2
    pd_relative_threshold: float = 2.0
    pd_absolute_threshold: float = 0.005
    dpd_stage2_threshold: int = 30
    dpd_stage3_threshold: int = 90
    qualitative_stage2_triggers: Tuple[str, ...] = (
        "watchlist", "forbearance", "sector_stress", "covenant_breach",
    )
    qualitative_stage3_triggers: Tuple[str, ...] = (
        "bankruptcy", "distressed_restructuring", "fraud", "unlikely_to_pay",
    )
    allow_low_credit_risk_exemption: bool = False


@dataclass
class StagingResult:
    stage: Stage
    triggers_fired: List[str]
    detail: dict


@dataclass
class Scenario:
    """Macro scenario definition."""

    name: str
    weight: float
    pd_multiplier: float = 1.0
    lgd_multiplier: float = 1.0
    ead_multiplier: float = 1.0
    description: str = ""


@dataclass
class ECLResult:
    loan_name: str
    stage: Stage
    ecl_12m: float
    ecl_lifetime: float
    ecl_applied: float
    pd_used: float
    lgd_used: float
    ead_used: float
    triggers: List[str] = field(default_factory=list)
    scenario_breakdown: dict = field(default_factory=dict)
