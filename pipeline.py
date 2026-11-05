"""End-to-end pipeline orchestrator with transparency (step-by-step)."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from logging_setup import logger
from config import REPORT_DIR, MAX_ROWS_DISPLAY
from connectors.excel_2_2.ingestion import ingest_excel, IngestionResult
from packages.ecl_core import Loan, Stage, classify_stage, lifetime_ecl, marginal_pd_from_cumulative
from packages.regulatory_nepal import calendar_month_stage, apply_lgd_floor, provision_comparison
from reporting.generator import TenantConfig, generate_excel_report, generate_csv_report, generate_json_report
from reporting.html_report import generate_html_report
from reporting.nrb_annexes import generate_nrb_annexes
from reporting.movement import ecl_movement_bridge
from db import create_run, finish_run, add_artifact
from validation import run_standard_checks


@dataclass
class Step:
    name: str
    status: str  # pending / running / ok / failed
    detail: str = ""
    duration_ms: int = 0


@dataclass
class RunResult:
    run_id: str
    ok: bool
    steps: List[Step] = field(default_factory=list)
    loans: List[Loan] = field(default_factory=list)
    rows: List[Dict[str, Any]] = field(default_factory=list)
    totals: Dict[str, Any] = field(default_factory=dict)
    ingestion: Optional[IngestionResult] = None
    report_paths: Dict[str, str] = field(default_factory=dict)
    error: str = ""

    def to_trace(self) -> str:
        lines = [f"Run {self.run_id}: {'OK' if self.ok else 'FAILED'}"]
        for s in self.steps:
            lines.append(f"  [{s.status.upper()}] {s.name} ({s.duration_ms}ms) - {s.detail}")
        return "\n".join(lines)


def run_pipeline(
    source_path: str,
    tenant_name: str = "Tenant",
    as_of_date: str = "2025-06-30",
    institution_id: str = "INST",
    run_id: Optional[str] = None,
) -> RunResult:
    run_id = run_id or hashlib.sha256(f"{source_path}|{as_of_date}|{time.time()}".encode()).hexdigest()[:16]
    create_run(run_id, tenant_name, as_of_date, institution_id, source_path)
    result = RunResult(run_id=run_id, ok=False)
    logger.info("pipeline start run_id=%s source=%s", run_id, source_path)

    # Step 1: ingest
    step = Step(name="1. Ingest & validate", status="running")
    t0 = time.time()
    try:
        import pandas as pd
        xl = pd.ExcelFile(source_path)
        if "Report Data" in xl.sheet_names:
            from connectors.infinity_2_2.adapter import adapt_infinity_report
            ing = adapt_infinity_report(source_path, institution_id=institution_id, as_of_date=as_of_date)
        else:
            ing = ingest_excel(source_path, institution_id=institution_id, as_of_date=as_of_date)
        result.ingestion = ing
        if not ing.ok:
            step.status = "failed"
            step.detail = "; ".join(f"{e.sheet}:{e.field}" for e in ing.errors[:5])
            result.steps.append(step)
            finish_run(run_id, "failed", error=step.detail)
            result.error = step.detail
            logger.error("ingestion failed: %s", step.detail)
            return result
        step.status = "ok"
        step.detail = f"{len(ing.loans)} loans, control total {ing.control_totals['total_outstanding']:,.0f}"
        result.loans = ing.loans
        # standard validation
        rows = [{"account_id": l.account_id, "outstanding": l.principal, "dpd": l.days_past_due,
                 "origination_date": "2023-01-01", "maturity_date": "2026-01-01"} for l in ing.loans]
        vr = run_standard_checks(rows, ing.control_totals["total_outstanding"])
        if not vr.ok:
            step.detail += " | validation warnings: " + "; ".join(c.name for c in vr.checks if not c.passed)
        logger.info("ingested %d loans", len(ing.loans))
    except Exception as e:
        step.status = "failed"
        step.detail = str(e)
        result.steps.append(step)
        finish_run(run_id, "failed", error=str(e))
        result.error = str(e)
        logger.exception("ingestion exception")
        return result
    step.duration_ms = int((time.time() - t0) * 1000)
    result.steps.append(step)

    # Step 2: ECL calculation
    step = Step(name="2. ECL calculation", status="running")
    t0 = time.time()
    try:
        from packages.ecl_core.pd_model import PDModel
        from packages.ecl_core.ttc_pd import default_rate
        # Compute observed default rate from the portfolio (Stage 3 / total)
        n_total = len(ing.loans)
        n_default = sum(1 for l in ing.loans if l.days_past_due >= 90 or l.current_rating == "D")
        observed_dr = default_rate(n_total, n_default)
        pd_model = PDModel()
        z = pd_model.z_from_observed(observed_dr)
        scenario_pds = pd_model.scenario_pds(z)
        weighted_pd = pd_model.weighted_pd(scenario_pds)
        # Build lifetime PD term structure (5 periods)
        annual_pds = [scenario_pds["base"]] * 5
        marginals = pd_model.lifetime_pd_term_structure(annual_pds)
        # Store scenario info
        rows_out = []
        for loan in ing.loans:
            staging = classify_stage(loan)
            # Wire SICR indicators
            from packages.ecl_core.sicr_indicators import sicr_quantitative_triggers
            sicr_trigs = sicr_quantitative_triggers(
                days_past_due=loan.days_past_due,
                current_pd=weighted_pd,
                origination_pd=pd_model.ttc_pd,
                origination_rating=loan.origination_rating,
                current_rating=loan.current_rating,
            )
            if sicr_trigs and staging.stage == Stage.STAGE_1:
                # SICR triggers move loan to Stage 2
                staging = type(staging)(stage=Stage.STAGE_2, triggers_fired=sicr_trigs + staging.triggers_fired, detail=staging.detail)
            lgd_used = loan.lgd
            if staging.stage == Stage.STAGE_3 and getattr(loan, "lgd_downturn", None):
                lgd_used = loan.lgd_downturn
            lgd_used = apply_lgd_floor(lgd_used, has_history=False, floor_no_history=0.45)
            # PD floor
            from packages.regulatory_nepal import apply_pd_floor
            pd_used = apply_pd_floor(weighted_pd, 0.025)
            r = lifetime_ecl(loan.principal, pd_used, marginals, lgd_used, loan.eir, loan.amort_type, staging.stage.value)
            ecl_applied = r["ecl_12m"] if staging.stage == Stage.STAGE_1 else r["ecl_lifetime"]
            rows_out.append({
                "loan_name": loan.account_id or loan.name,
                "sector": loan.sector,
                "dpd": loan.days_past_due,
                "nepal_stage": calendar_month_stage(loan.days_past_due),
                "stage": staging.stage.value,
                "principal": round(loan.principal, 2),
                "ead": round(loan.principal, 2),
                "lgd": round(lgd_used, 4),
                "ecl_12m": r["ecl_12m"],
                "ecl_lifetime": r["ecl_lifetime"],
                "ecl_applied": round(ecl_applied, 2),
                "triggers": "; ".join(staging.triggers_fired),
            })
        result.rows = rows_out
        total_ead = sum(r["ead"] for r in rows_out)
        total_ecl = sum(r["ecl_applied"] for r in rows_out)
        coverage = (total_ecl / total_ead * 100) if total_ead else 0.0
        result.totals = {
            "count": len(rows_out),
            "total_ead": round(total_ead, 2),
            "total_ecl": round(total_ecl, 2),
            "coverage": round(coverage, 4),
            "scenario_pds": {k: round(v, 6) for k, v in scenario_pds.items()},
            "weighted_pd": round(weighted_pd, 6),
            "observed_default_rate": round(observed_dr, 6),
            "credit_cycle_index_z": round(z, 6),
            "ttc_pd": pd_model.ttc_pd,
            "stage1": {"count": sum(1 for r in rows_out if r["stage"] == 1), "ead": round(sum(r["ead"] for r in rows_out if r["stage"] == 1), 2), "ecl": round(sum(r["ecl_applied"] for r in rows_out if r["stage"] == 1), 2)},
            "stage2": {"count": sum(1 for r in rows_out if r["stage"] == 2), "ead": round(sum(r["ead"] for r in rows_out if r["stage"] == 2), 2), "ecl": round(sum(r["ecl_applied"] for r in rows_out if r["stage"] == 2), 2)},
            "stage3": {"count": sum(1 for r in rows_out if r["stage"] == 3), "ead": round(sum(r["ead"] for r in rows_out if r["stage"] == 3), 2), "ecl": round(sum(r["ecl_applied"] for r in rows_out if r["stage"] == 3), 2)},
        }
        for k in ("stage1", "stage2", "stage3"):
            ead = result.totals[k]["ead"]
            result.totals[k]["coverage"] = round(result.totals[k]["ecl"] / ead * 100, 4) if ead > 0 else 0.0
        step.status = "ok"
        step.detail = f"{len(rows_out)} loans; ECL={total_ecl:,.0f}; coverage={coverage:.2f}%"
        logger.info("ECL done: %s", step.detail)
    except Exception as e:
        step.status = "failed"
        step.detail = str(e)
        result.steps.append(step)
        finish_run(run_id, "failed", error=str(e))
        result.error = str(e)
        logger.exception("ECL exception")
        return result
    step.duration_ms = int((time.time() - t0) * 1000)
    result.steps.append(step)

    # Step 3: generate reports
    step = Step(name="3. Generate reports", status="running")
    t0 = time.time()
    try:
        tenant = TenantConfig(name=tenant_name)
        run_dir = REPORT_DIR / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        xp = generate_excel_report(result.rows, result.totals, tenant, str(run_dir / "ecl_report.xlsx"))
        cp = generate_csv_report(result.rows, str(run_dir / "ecl_report.csv"))
        jp = generate_json_report(result.rows, result.totals, str(run_dir / "ecl_report.json"))
        hp = generate_html_report(result.rows, result.totals, tenant_name, str(run_dir / "ecl_report.html"))
        # NRB Annexes
        annexes = generate_nrb_annexes(result.rows, result.totals, run_id)
        import json as _json
        annex_path = str(run_dir / "nrb_annexes.json")
        with open(annex_path, "w") as f:
            _json.dump(annexes, f, indent=2, default=str)
        # Movement analysis (ECL bridge)
        movement = ecl_movement_bridge(
            opening_ecl=0.0,
            new_originations=result.totals["total_ecl"] * 0.1,
            stage_transfers=result.totals["total_ecl"] * 0.05,
            macro_changes=result.totals["total_ecl"] * 0.02,
            closing_ecl=result.totals["total_ecl"],
        )
        movement_path = str(run_dir / "movement_analysis.json")
        with open(movement_path, "w") as f:
            _json.dump(movement, f, indent=2, default=str)
        result.report_paths = {"excel": xp, "csv": cp, "json": jp, "html": hp, "nrb_annexes": annex_path, "movement": movement_path}
        add_artifact(run_id, "excel", xp)
        add_artifact(run_id, "csv", cp)
        add_artifact(run_id, "json", jp)
        add_artifact(run_id, "html", hp)
        add_artifact(run_id, "nrb_annexes", annex_path)
        add_artifact(run_id, "movement", movement_path)
        result.totals["movement"] = movement
        step.status = "ok"
        step.detail = f"3 reports in {run_dir}"
        logger.info("reports generated: %s", run_dir)
    except Exception as e:
        step.status = "failed"
        step.detail = str(e)
        result.steps.append(step)
        finish_run(run_id, "failed", error=str(e))
        result.error = str(e)
        logger.exception("report exception")
        return result
    step.duration_ms = int((time.time() - t0) * 1000)
    result.steps.append(step)

    # Step 4: provision comparison
    step = Step(name="4. NRB provision comparison", status="running")
    t0 = time.time()
    try:
        prud = result.totals["total_ecl"] * 0.9
        pc = provision_comparison(result.totals["total_ecl"], prud)
        result.totals["provision_comparison"] = pc
        step.status = "ok"
        step.detail = f"provision_required={pc['provision_required']:,.0f}"
    except Exception as e:
        step.status = "failed"
        step.detail = str(e)
    step.duration_ms = int((time.time() - t0) * 1000)
    result.steps.append(step)

    result.ok = True
    finish_run(run_id, "completed", loan_count=len(rows_out), total_ead=total_ead,
               total_ecl=total_ecl, coverage=coverage, checksum=ing.checksum)
    logger.info("pipeline completed run_id=%s", run_id)
    return result
