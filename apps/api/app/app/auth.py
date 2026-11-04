"""Lightweight auth (HMAC token) for the API scaffold."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Optional

SECRET = "change-me-in-production"


def create_token(user_id: str, tenant_id: str, role: str, ttl_seconds: int = 3600) -> str:
    payload = {"sub": user_id, "tenant": tenant_id, "role": role, "exp": int(time.time()) + ttl_seconds}
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    sig = hmac.new(SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{sig}"


def verify_token(token: str) -> Optional[dict]:
    try:
        body, sig = token.split(".")
        expected = hmac.new(SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        # pad
        pad = "=" * (-len(body) % 4)
        payload = json.loads(base64.urlsafe_b64decode(body + pad))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None
