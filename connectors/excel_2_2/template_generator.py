"""Generate the vendor/tenant Excel data template for ECL ingestion."""

from __future__ import annotations

import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


def build_template(out_path: str) -> str:
    wb = Workbook()

    header_fill = PatternFill("solid", fgColor="1F3864")
    header_font = Font(color="FFFFFF", bold=True)
    note_font = Font(italic=True, size=9, color="555555")

    def style_header(ws, row=1):
        for cell in ws[row]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.row_dimensions[row].height = 30

    def set_widths(ws, widths):
        for i, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w

    # --- README ---
    ws = wb.active
    ws.title = "README"
    readme = [
        ("SENNA ECL — Vendor/Tenant Data Template", None),
        ("", None),
        ("Purpose: Provide portfolio data in the canonical format required by SENNA ECL.", None),
        ("Fill each sheet. Do not rename sheets or header rows. Dates: YYYY-MM-DD. Amounts: numbers (no commas).", None),
        ("", None),
        ("Sheet", "Description"),
        ("Loan_Master", "One row per loan account (required)."),
        ("Collateral", "One row per collateral item (optional but recommended)."),
        ("Customer", "One row per customer (optional)."),
        ("Repayment_Schedule", "Contractual repayment schedule (optional, improves EAD)."),
        ("Transactions", "Loan transactions including reversals/write-offs/recoveries (optional)."),
        ("Macro", "Macro indicators and scenario weights by period (required for forward-looking)."),
        ("Historical", "Historical stage/default/recovery for PD-LGD calibration (optional)."),
        ("", None),
        ("Control total: sum(Loan_Master.outstanding) must equal your reported portfolio total.", None),
    ]
    for r in readme:
        ws.append(list(r))
    ws["A1"].font = Font(bold=True, size=14, color="1F3864")
    for row in ws.iter_rows(min_row=6, max_row=12):
        for c in row:
            c.font = Font(bold=True)
    set_widths(ws, [28, 90])

    # --- Loan_Master ---
    ws = wb.create_sheet("Loan_Master")
    cols = ["account_id", "customer_id", "product", "sector", "branch", "currency",
            "origination_date", "maturity_date", "outstanding", "undrawn_limit",
            "interest_rate", "eir", "dpd", "classification", "nrb_classification",
            "status", "origination_rating", "current_rating", "watchlist", "forbearance"]
    ws.append(cols)
    style_header(ws)
    sample = ["ACC001", "CUST001", "Term Loan", "Agriculture", "KTM", "NPR",
              "2024-01-15", "2027-01-15", 1500000, 200000, 0.12, 0.125, 0, "Pass", "Pass", "Active", "BBB", "BBB", False, False]
    ws.append(sample)
    set_widths(ws, [12, 12, 12, 14, 8, 8, 14, 14, 14, 12, 12, 8, 6, 14, 16, 10, 12, 12, 10, 12])

    # --- Collateral ---
    ws = wb.create_sheet("Collateral")
    cols = ["account_id", "collateral_type", "valuation_date", "fair_value", "forced_sale_value", "haircut"]
    ws.append(cols)
    style_header(ws)
    ws.append(["ACC001", "Land", "2025-06-30", 2000000, 1600000, 0.25])
    set_widths(ws, [12, 14, 14, 14, 16, 8])

    # --- Customer ---
    ws = wb.create_sheet("Customer")
    cols = ["customer_id", "segment", "risk_grade", "watchlist_flag", "forbearance_flag", "npl_history"]
    ws.append(cols)
    style_header(ws)
    ws.append(["CUST001", "Retail", "BBB", False, False, False])
    set_widths(ws, [12, 12, 12, 12, 14, 12])

    # --- Repayment_Schedule ---
    ws = wb.create_sheet("Repayment_Schedule")
    cols = ["account_id", "period", "due_date", "principal_due", "interest_due"]
    ws.append(cols)
    style_header(ws)
    ws.append(["ACC001", 1, "2025-07-15", 50000, 15000])
    set_widths(ws, [12, 8, 14, 14, 14])

    # --- Transactions ---
    ws = wb.create_sheet("Transactions")
    cols = ["account_id", "txn_date", "amount", "type"]
    ws.append(cols)
    style_header(ws)
    ws.append(["ACC001", "2025-06-30", 100000, "repayment"])
    set_widths(ws, [12, 14, 14, 14])

    # --- Macro ---
    ws = wb.create_sheet("Macro")
    cols = ["period", "gdp_growth", "inflation", "interest_rate", "unemployment",
            "weight_optimistic", "weight_base", "weight_pessimistic"]
    ws.append(cols)
    style_header(ws)
    ws.append(["2025-Q2", 0.04, 0.06, 0.07, 0.03, 0.2, 0.5, 0.3])
    set_widths(ws, [12, 12, 12, 14, 14, 14, 12, 16])

    # --- Historical ---
    ws = wb.create_sheet("Historical")
    cols = ["account_id", "period", "stage", "default_flag", "recovery_amount"]
    ws.append(cols)
    style_header(ws)
    ws.append(["ACC001", "2025-Q1", 1, False, 0])
    set_widths(ws, [12, 12, 8, 12, 16])

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    wb.save(out_path)
    return out_path


if __name__ == "__main__":
    p = build_template(os.path.join(os.path.dirname(__file__), "..", "templates", "SENNA_ECL_Vendor_Data_Template.xlsx"))
    print("written", p)
