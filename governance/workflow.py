"""Governance: maker-checker-approver workflow, model registry, periods, audit."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional


class Role(Enum):
    MAKER = "maker"
    CHECKER = "checker"
    APPROVER = "approver"
    ADMIN = "admin"
    VIEWER = "viewer"


class ApprovalStatus(Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    CHECKED = "checked"
    APPROVED = "approved"
    REJECTED = "rejected"
    LOCKED = "locked"


@dataclass
class AuditEntry:
    timestamp: str
    actor: str
    role: str
    action: str
    detail: str


@dataclass
class ApprovalWorkflow:
    entity_type: str  # e.g. "snapshot", "calculation", "overlay", "parameter"
    entity_id: str
    status: ApprovalStatus = ApprovalStatus.DRAFT
    maker: Optional[str] = None
    checker: Optional[str] = None
    approver: Optional[str] = None
    audit: List[AuditEntry] = field(default_factory=list)
    rejection_reason: str = ""

    def submit(self, actor: str) -> None:
        if self.status != ApprovalStatus.DRAFT:
            raise ValueError("only DRAFT can be submitted")
        self.status = ApprovalStatus.SUBMITTED
        self.maker = actor
        self.audit.append(AuditEntry(datetime.now().isoformat(), actor, "maker", "submit", f"{self.entity_type}:{self.entity_id}"))

    def check(self, actor: str, ok: bool, reason: str = "") -> None:
        if self.status != ApprovalStatus.SUBMITTED:
            raise ValueError("only SUBMITTED can be checked")
        if ok:
            self.status = ApprovalStatus.CHECKED
            self.checker = actor
            self.audit.append(AuditEntry(datetime.now().isoformat(), actor, "checker", "check_ok", reason or "ok"))
        else:
            self.status = ApprovalStatus.REJECTED
            self.rejection_reason = reason
            self.audit.append(AuditEntry(datetime.now().isoformat(), actor, "checker", "check_rejected", reason))

    def approve(self, actor: str, ok: bool, reason: str = "") -> None:
        if self.status != ApprovalStatus.CHECKED:
            raise ValueError("only CHECKED can be approved")
        if ok:
            self.status = ApprovalStatus.APPROVED
            self.approver = actor
            self.audit.append(AuditEntry(datetime.now().isoformat(), actor, "approver", "approve", reason or "ok"))
        else:
            self.status = ApprovalStatus.REJECTED
            self.rejection_reason = reason
            self.audit.append(AuditEntry(datetime.now().isoformat(), actor, "approver", "approve_rejected", reason))

    def lock(self, actor: str) -> None:
        if self.status != ApprovalStatus.APPROVED:
            raise ValueError("only APPROVED can be locked")
        self.status = ApprovalStatus.LOCKED
        self.audit.append(AuditEntry(datetime.now().isoformat(), actor, "admin", "lock", "period locked"))


@dataclass
class ModelVersion:
    model_id: str
    version: str
    description: str
    created_at: str
    created_by: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: str = "draft"  # draft / validated / approved / retired


@dataclass
class ModelRegistry:
    models: Dict[str, List[ModelVersion]] = field(default_factory=dict)

    def register(self, mv: ModelVersion) -> None:
        self.models.setdefault(mv.model_id, []).append(mv)

    def latest(self, model_id: str, status: Optional[str] = None) -> Optional[ModelVersion]:
        versions = self.models.get(model_id, [])
        if status:
            versions = [v for v in versions if v.status == status]
        return versions[-1] if versions else None

    def all_versions(self, model_id: str) -> List[ModelVersion]:
        return list(self.models.get(model_id, []))


@dataclass
class ReportingPeriod:
    period_id: str
    start_date: str
    end_date: str
    status: str = "open"  # open / closed / locked
    locked_by: Optional[str] = None
    locked_at: Optional[str] = None

    def close(self, actor: str) -> None:
        if self.status != "open":
            raise ValueError("period not open")
        self.status = "closed"

    def lock(self, actor: str) -> None:
        if self.status not in ("open", "closed"):
            raise ValueError("period cannot be locked")
        self.status = "locked"
        self.locked_by = actor
        self.locked_at = datetime.now().isoformat()

    def is_locked(self) -> bool:
        return self.status == "locked"


@dataclass
class ParameterVersion:
    param_id: str
    version: str
    value: Any
    effective_from: str
    created_by: str
    created_at: str
    reason: str = ""


class ParameterRegistry:
    def __init__(self):
        self.params: Dict[str, List[ParameterVersion]] = {}

    def add(self, pv: ParameterVersion) -> None:
        self.params.setdefault(pv.param_id, []).append(pv)

    def current(self, param_id: str, as_of: str) -> Optional[ParameterVersion]:
        candidates = [p for p in self.params.get(param_id, []) if p.effective_from <= as_of]
        return candidates[-1] if candidates else None
