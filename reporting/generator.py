"""Multi-format report generator for ECL outputs."""

from __future__ import annotations

import csv
import json
import os
from datetime import datetime
from typing import Any, Dict, List

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


class TenantConfig:
    def __init__(self, name="Tenant", logo="", primary_color="1F3864",
                 language="EN", currency="NPR", report_header="", report_footer=""):
        self.name = name
        self.logo = logo
        self.primary_color = primary_color
        self.language = language
        self.currency = currency
        self.report_header = report_header or f"{name} — ECL Report"
        self.report_footer = report_footer or "Confidential — Preliminary/Research output"


def _header_style(ws, row=1, color="1F3864"):
    for cell in ws[row]:
        cell.fill = PatternFill("solid", fgColor=color)
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 22


def generate_excel_report(results: List[Dict[str, Any]], totals: Dict[str, Any],
                          tenant: TenantConfig, out_path: str,
                          scenario_breakdown: Dict[str, Any] = None) -> str:
    wb = Workbook()
    color = tenant.primary_color

    # --- Summary sheet ---
    ws = wb.active
    ws.title = "ECL Summary"
    ws.append([tenant.report_header])
    ws["A1"].font = Font(bold=True, size=14, color=color)
    ws.append([f"Generated: {datetime.now().isoformat()}  |  Currency: {tenant.currency}"])
    ws.append([])
    ws.append(["Stage", "Count", "EAD", "ECL", "Coverage %"])
    _header_style(ws, row=4, color=color)
    for s in ("stage1", "stage2", "stage3"):
        b = totals.get(s, {})
        ws.append([s.upper().replace("STAGE", "Stage "), b.get("count", 0),
                   b.get("ead", 0.0), b.get("ecl", 0.0), b.get("coverage", 0.0)])
    ws.append(["TOTAL", totals.get("count", 0), totals.get("total_ead", 0.0),
               totals.get("total_ecl", 0.0), totals.get("coverage", 0.0)])
    for c in ws[ws.max_row]:
        c.font = Font(bold=True)
    for i, w in enumerate([14, 8, 16, 16, 12], start=1):
        ws.column_dimensions[chr(64 + i)].width = w

    # --- Detail sheet ---
    ws2 = wb.create_sheet("Account Detail")
    if results:
        keys = list(results[0].keys())
        ws2.append(keys)
        _header_style(ws2, row=1, color=color)
        for r in results:
            ws2.append([r.get(k) for k in keys])
        for i in range(1, len(keys) + 1):
            ws2.column_dimensions[get_column_letter(i)].width = 16

    # --- Scenario sheet ---
    if scenario_breakdown:
        ws3 = wb.create_sheet("Scenarios")
        ws3.append(["Scenario", "Weight", "ECL"])
        _header_style(ws3, row=1, color=color)
        for name, v in scenario_breakdown.items():
            ws3.append([name, v.get("weight", 0), v.get("ecl", 0)])

    # footer
    last = wb[wb.sheetnames[-1]]
    last.append([])
    last.append([tenant.report_footer])

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    wb.save(out_path)
    return out_path


def generate_csv_report(results: List[Dict[str, Any]], out_path: str) -> str:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    if not results:
        with open(out_path, "w", newline="") as f:
            f.write("")
        return out_path
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        for r in results:
            w.writerow(r)
    return out_path


def generate_json_report(results: List[Dict[str, Any]], totals: Dict[str, Any],
                         out_path: str) -> str:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    payload = {"generated_at": datetime.now().isoformat(), "totals": totals, "results": results}
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2, default=str)
    return out_path
