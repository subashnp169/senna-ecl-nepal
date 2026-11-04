"""Release gate enforcement: OFFICIAL marking only after all gates pass."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

RELEASE_GATES = [
    "source_to_report_reconciliation",
    "staging_policy",
    "segmentation",
    "pd_methodology",
    "lgd_methodology",
    "ead_method",
    "scenario_methodology",
    "overlay_governance",
    "rule_pack_signoff",
    "finance_risk_audit_review",
    "independent_validation",
]


@dataclass
class ReleaseGateStatus:
    gates: dict = field(default_factory=lambda: {g: False for g in RELEASE_GATES})
    evidence: dict = field(default_factory=dict)

    def set(self, gate: str, passed: bool, evidence: str = "") -> None:
        if gate not in self.gates:
            raise ValueError(f"unknown gate: {gate}")
        self.gates[gate] = passed
        if evidence:
            self.evidence[gate] = evidence

    @property
    def all_passed(self) -> bool:
        return all(self.gates.values())

    @property
    def missing(self) -> List[str]:
        return [g for g, v in self.gates.items() if not v]

    def label(self) -> str:
        if self.all_passed:
            return "OFFICIAL"
        return "PRELIMINARY"


def can_mark_official(status: ReleaseGateStatus) -> bool:
    return status.all_passed
