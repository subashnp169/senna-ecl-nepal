"""Disaster recovery / backup helpers."""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime


def backup_file(src: str, backup_dir: str) -> str:
    os.makedirs(backup_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.basename(src)
    dst = os.path.join(backup_dir, f"{base}.{ts}.bak")
    shutil.copy2(src, dst)
    return dst


def write_manifest(path: str, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
