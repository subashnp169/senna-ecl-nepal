"""Central configuration for SENNA ECL system."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "sample_data"
REPORT_DIR = BASE_DIR / "output" / "reports"
DB_PATH = BASE_DIR / "data" / "senna_ecl.db"
LOG_DIR = BASE_DIR / "logs"

# Infinity full data source (not committed; local only)
INFINITY_FULL_DATA = Path(r"D:\data\NRB_2_2_REPORT_REVAMPED_000080__20261008_095117.xlsx")

# Defaults
DEFAULT_AS_OF_DATE = "2025-06-30"
DEFAULT_INSTITUTION_ID = "ILBSL"
DEFAULT_TENANT_NAME = "Infinity Laghubitta Bittiya Sanstha Ltd."

# ECL params
DEFAULT_PD_FLOOR = 0.025
DEFAULT_LGD_FLOOR_NO_HISTORY = 0.45
DEFAULT_COLLATERAL_HAIRCUT = 0.25

# Limits
MAX_ROWS_DISPLAY = 500
MAX_UPLOAD_MB = 50

for d in (REPORT_DIR, DB_PATH.parent, LOG_DIR):
    d.mkdir(parents=True, exist_ok=True)
