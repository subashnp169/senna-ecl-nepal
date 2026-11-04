"""Multi-tenant model, RBAC and audit logging."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Set


class Permission(Enum):
    READ = "read"
    WRITE = "write"
    APPROVE = "approve"
    ADMIN = "admin"
    EXPORT = "export"


ROLE_PERMISSIONS: Dict[str, Set[Permission]] = {
    "viewer": {Permission.READ, Permission.EXPORT},
    "analyst": {Permission.READ, Permission.WRITE, Permission.EXPORT},
    "checker": {Permission.READ, Permission.WRITE, Permission.APPROVE, Permission.EXPORT},
    "approver": {Permission.READ, Permission.APPROVE, Permission.EXPORT},
    "admin": {Permission.READ, Permission.WRITE, Permission.APPROVE, Permission.ADMIN, Permission.EXPORT},
}


@dataclass
class Tenant:
    tenant_id: str
    name: str
    plan: str = "standard"  # standard / enterprise
    primary_color: str = "1F3864"
    language: str = "EN"
    currency: str = "NPR"
    logo_url: str = ""
    fiscal_year_start: str = "07-16"  # MM-DD (Nepal: Shrawan 1)
    calendar: str = "BS"  # BS or AD
    active: bool = True


@dataclass
class User:
    user_id: str
    tenant_id: str
    email: str
    role: str
    full_name: str = ""
    active: bool = True

    def has(self, perm: Permission) -> bool:
        return perm in ROLE_PERMISSIONS.get(self.role, set())


@dataclass
class AuditLogEntry:
    timestamp: str
    tenant_id: str
    user_id: str
    action: str
    resource: str
    detail: str = ""
    ip: str = ""


class AuditLog:
    def __init__(self):
        self.entries: List[AuditLogEntry] = []

    def record(self, tenant_id: str, user_id: str, action: str, resource: str, detail: str = "", ip: str = "") -> None:
        self.entries.append(AuditLogEntry(datetime.now().isoformat(), tenant_id, user_id, action, resource, detail, ip))

    def for_tenant(self, tenant_id: str) -> List[AuditLogEntry]:
        return [e for e in self.entries if e.tenant_id == tenant_id]

    def for_user(self, user_id: str) -> List[AuditLogEntry]:
        return [e for e in self.entries if e.user_id == user_id]


@dataclass
class TenantConfig:
    """Per-tenant ECL configuration (extends reporting TenantConfig)."""
    tenant_id: str
    pd_floor: float = 0.025
    lgd_floor_no_history: float = 0.45
    collateral_haircut: float = 0.25
    scenario_weights: Dict[str, float] = field(default_factory=lambda: {"optimistic": 0.2, "base": 0.5, "pessimistic": 0.3})
    segmentation: List[str] = field(default_factory=lambda: ["retail", "sme", "corporate", "microfinance"])
    cure_period_days: int = 90
    reporting_currency: str = "NPR"


def check_access(user: User, perm: Permission) -> bool:
    if not user.active:
        return False
    return user.has(perm)
