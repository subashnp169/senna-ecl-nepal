"""Security helpers: input sanitization, secret handling."""

from __future__ import annotations

import re
import hashlib
import secrets


def sanitize_identifier(value: str) -> str:
    """Allow only alphanumeric + underscore for SQL identifiers."""
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value or ""):
        raise ValueError(f"unsafe identifier: {value}")
    return value


def mask_secret(value: str, show: int = 4) -> str:
    if not value:
        return ""
    if len(value) <= show:
        return "*" * len(value)
    return value[:show] + "*" * (len(value) - show)


def generate_token(n: int = 32) -> str:
    return secrets.token_urlsafe(n)


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()
