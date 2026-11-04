"""SFTP batch connector: manifest validation and ingestion."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class BatchManifest:
    batch_id: str
    institution_id: str
    as_of_date: str
    files: List[str]
    checksum: str = ""


def validate_manifest(manifest: Dict[str, Any]) -> List[str]:
    errors = []
    for f in ("batch_id", "institution_id", "as_of_date", "files"):
        if f not in manifest:
            errors.append(f"missing field: {f}")
    if "files" in manifest and not isinstance(manifest["files"], list):
        errors.append("files must be a list")
    return errors


def load_manifest(path: str) -> BatchManifest:
    with open(path) as f:
        data = json.load(f)
    errs = validate_manifest(data)
    if errs:
        raise ValueError("; ".join(errs))
    return BatchManifest(
        batch_id=data["batch_id"],
        institution_id=data["institution_id"],
        as_of_date=data["as_of_date"],
        files=data["files"],
        checksum=data.get("checksum", ""),
    )
