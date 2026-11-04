"""Build a sanitized sample dataset from Infinity's real NRB 2.2 report."""

from __future__ import annotations

import os
import random
import pandas as pd
from openpyxl import load_workbook

SRC = r"D:\data\NRB_2_2_REPORT_REVAMPED_000080__20261008_095117.xlsx"
OUT_DIR = r"D:\senna-ecl-nepal\sample_data"
N = 120
random.seed(42)


def cls_to_rating(c):
    m = {1.0: "BBB", 1.1: "BB", 3.0: "B", 4.0: "CCC", 5.0: "D"}
    return m.get(float(c) if c is not None else 1.0, "BB")


def cls_to_nrb(c):
    m = {1.0: "Pass", 1.1: "Watchlist", 3.0: "Substandard", 4.0: "Doubtful", 5.0: "Loss"}
    return m.get(float(c) if c is not None else 1.0, "Pass")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    df = pd.read_excel(SRC)
    # stratified sample across classifications
    parts = []
    for c, g in df.groupby("CLASSIFICATION"):
        k = min(len(g), max(5, int(N * len(g) / len(df))))
        parts.append(g.sample(n=k, random_state=42))
    sample = pd.concat(parts).sample(n=N, random_state=42).reset_index(drop=True)

    rows = []
    for i, r in sample.iterrows():
        outstanding = float(r["F_OUTSTANDING_PRICIPAL"] or 0)
        if outstanding <= 0:
            continue
        limit = float(r.get("F_APPROVED_LIMIT", 0) or 0)
        undrawn = max(0.0, limit - outstanding) if limit > 0 else 0.0
        dpd = int(r.get("OVERDUE_DAYS", 0) or 0)
        rate = float(r.get("INT_RATE", 12) or 12) / 100.0
        cls = r.get("CLASSIFICATION", 1.0)
        rows.append({
            "account_id": f"ACC{i+1:04d}",
            "customer_id": f"CUST{i+1:04d}",
            "product": str(r.get("F_TYPE_OF_CREDIT", "General Loan")),
            "sector": str(r.get("CAT_NAME", "General")),
            "branch": str(r.get("BR_NAME", "Branch")),
            "currency": "NPR",
            "origination_date": "2023-01-15",
            "maturity_date": "2026-01-15",
            "outstanding": round(outstanding, 2),
            "undrawn_limit": round(undrawn, 2),
            "interest_rate": round(rate, 4),
            "eir": round(rate, 4),
            "dpd": dpd,
            "classification": cls_to_nrb(cls),
            "nrb_classification": cls_to_nrb(cls),
            "status": "Active",
            "origination_rating": cls_to_rating(cls),
            "current_rating": cls_to_rating(cls),
            "watchlist": bool(cls == 1.1),
            "forbearance": False,
            "collateral_value": round(outstanding * random.uniform(0.8, 1.3), 2),
            "collateral_type": random.choice(["Land", "Building", "Gold", "None"]),
        })

    loan_df = pd.DataFrame(rows)

    # collateral sheet
    coll_rows = []
    for r in rows:
        if r["collateral_type"] != "None":
            coll_rows.append({
                "account_id": r["account_id"],
                "collateral_type": r["collateral_type"],
                "valuation_date": "2025-06-30",
                "fair_value": r["collateral_value"],
                "forced_sale_value": round(r["collateral_value"] * 0.8, 2),
                "haircut": 0.25,
            })
    coll_df = pd.DataFrame(coll_rows)

    cust_rows = [{"customer_id": r["customer_id"], "segment": "Microfinance", "risk_grade": r["origination_rating"],
                  "watchlist_flag": r["watchlist"], "forbearance_flag": False, "npl_history": r["classification"] in ("Substandard", "Doubtful", "Loss")}
                 for r in rows]
    cust_df = pd.DataFrame(cust_rows)

    macro_df = pd.DataFrame([
        {"period": "2025-Q2", "gdp_growth": 0.04, "inflation": 0.06, "interest_rate": 0.07, "unemployment": 0.03,
         "weight_optimistic": 0.2, "weight_base": 0.5, "weight_pessimistic": 0.3},
    ])

    # write using template
    from connectors.excel_2_2.template_generator import build_template
    tmpl = os.path.join(OUT_DIR, "infinity_sample_template.xlsx")
    build_template(tmpl)
    wb = load_workbook(tmpl)
    # replace Loan_Master data
    ws = wb["Loan_Master"]
    if ws.max_row > 1:
        ws.delete_rows(2, ws.max_row - 1)
    for r in rows:
        ws.append([r[c] for c in ["account_id", "customer_id", "product", "sector", "branch", "currency",
                                  "origination_date", "maturity_date", "outstanding", "undrawn_limit",
                                  "interest_rate", "eir", "dpd", "classification", "nrb_classification",
                                  "status", "origination_rating", "current_rating", "watchlist", "forbearance"]])
    # Collateral
    ws = wb["Collateral"]
    if ws.max_row > 1:
        ws.delete_rows(2, ws.max_row - 1)
    for r in coll_rows:
        ws.append([r["account_id"], r["collateral_type"], r["valuation_date"], r["fair_value"], r["forced_sale_value"], r["haircut"]])
    # Customer
    ws = wb["Customer"]
    if ws.max_row > 1:
        ws.delete_rows(2, ws.max_row - 1)
    for r in cust_rows:
        ws.append([r["customer_id"], r["segment"], r["risk_grade"], r["watchlist_flag"], r["forbearance_flag"], r["npl_history"]])
    # Macro
    ws = wb["Macro"]
    if ws.max_row > 1:
        ws.delete_rows(2, ws.max_row - 1)
    for r in macro_df.to_dict("records"):
        ws.append([r["period"], r["gdp_growth"], r["inflation"], r["interest_rate"], r["unemployment"],
                   r["weight_optimistic"], r["weight_base"], r["weight_pessimistic"]])

    out = os.path.join(OUT_DIR, "infinity_sample.xlsx")
    wb.save(out)
    # also csv
    loan_df.to_csv(os.path.join(OUT_DIR, "infinity_sample_loans.csv"), index=False)
    print("written", out, "rows:", len(rows))


if __name__ == "__main__":
    main()
