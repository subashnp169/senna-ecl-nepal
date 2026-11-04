"""Clean, simple white frontend to check ECL on uploaded data."""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
import pandas as pd
import tempfile

from connectors.excel_2_2.ingestion import ingest_excel
from packages.ecl_core import Loan, Stage, classify_stage, lifetime_ecl, marginal_pd_from_cumulative
from packages.regulatory_nepal import calendar_month_stage, apply_lgd_floor, provision_comparison
from reporting.generator import TenantConfig, generate_excel_report, generate_csv_report, generate_json_report

st.set_page_config(page_title="SENNA ECL — Check", layout="wide")
st.title("SENNA ECL — Check")
st.caption("Upload a vendor Excel file → run ECL → view & download reports. Preliminary/Research outputs only.")

with st.sidebar:
    st.header("Settings")
    tenant_name = st.text_input("Tenant name", "Infinity Laghubitta")
    as_of_date = st.text_input("As-of date (YYYY-MM-DD)", "2025-06-30")
    institution_id = st.text_input("Institution ID", "ILBSL")
    st.divider()
    st.write("Sample file: `sample_data/infinity_sample.xlsx`")

uploaded = st.file_uploader("Upload vendor Excel (.xlsx)", type=["xlsx"])
use_sample = st.checkbox("Use bundled Infinity sample instead", value=False)

if use_sample:
    path = "sample_data/infinity_sample.xlsx"
    uploaded = None

if st.button("Run ECL", type="primary"):
    if uploaded is not None:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        tmp.write(uploaded.read()); tmp.close()
        path = tmp.name

    if not os.path.exists(path):
        st.error("No file available.")
        st.stop()

    with st.spinner("Ingesting..."):
        res = ingest_excel(path, institution_id=institution_id, as_of_date=as_of_date)

    if not res.ok:
        st.error("Ingestion failed:")
        for e in res.errors:
            st.write(f"- {e.sheet} row {e.row}: {e.field} — {e.message}")
        st.stop()

    st.success(f"Ingested {len(res.loans)} loans. Control total: {res.control_totals['total_outstanding']:,.0f}")

    cum_pd = [0.01, 0.025, 0.04, 0.06, 0.08]
    marginals = marginal_pd_from_cumulative(cum_pd)

    rows = []
    for loan in res.loans:
        staging = classify_stage(loan)
        lgd_used = loan.lgd
        if staging.stage.value == 3 and loan.lgd_downturn:
            lgd_used = loan.lgd_downturn
        lgd_used = apply_lgd_floor(lgd_used, has_history=False, floor_no_history=0.45)
        r = lifetime_ecl(loan.principal, 0.02, marginals, lgd_used, loan.eir, loan.amort_type, staging.stage.value)
        ecl_applied = r["ecl_12m"] if staging.stage == Stage.STAGE_1 else r["ecl_lifetime"]
        rows.append({
            "Account": loan.account_id or loan.name,
            "Sector": loan.sector,
            "Branch": loan.branch if hasattr(loan, "branch") else "",
            "DPD": loan.days_past_due,
            "Nepal stage": calendar_month_stage(loan.days_past_due),
            "Stage": staging.stage.value,
            "EAD": round(loan.principal, 2),
            "LGD": round(lgd_used, 4),
            "12m ECL": r["ecl_12m"],
            "Lifetime ECL": r["ecl_lifetime"],
            "ECL Applied": round(ecl_applied, 2),
            "Triggers": "; ".join(staging.triggers_fired),
        })

    df = pd.DataFrame(rows)
    totals = {
        "count": len(df),
        "total_ead": float(df["EAD"].sum()),
        "total_ecl": float(df["ECL Applied"].sum()),
        "coverage": float(df["ECL Applied"].sum() / df["EAD"].sum() * 100) if df["EAD"].sum() else 0.0,
        "stage1": {"count": int((df["Stage"] == 1).sum()), "ead": float(df[df["Stage"] == 1]["EAD"].sum()), "ecl": float(df[df["Stage"] == 1]["ECL Applied"].sum()), "coverage": 0.0},
        "stage2": {"count": int((df["Stage"] == 2).sum()), "ead": float(df[df["Stage"] == 2]["EAD"].sum()), "ecl": float(df[df["Stage"] == 2]["ECL Applied"].sum()), "coverage": 0.0},
        "stage3": {"count": int((df["Stage"] == 3).sum()), "ead": float(df[df["Stage"] == 3]["EAD"].sum()), "ecl": float(df[df["Stage"] == 3]["ECL Applied"].sum()), "coverage": 0.0},
    }
    for k in ("stage1", "stage2", "stage3"):
        ead = totals[k]["ead"]
        totals[k]["coverage"] = round(totals[k]["ecl"] / ead * 100, 4) if ead > 0 else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Loans", totals["count"])
    c2.metric("Total EAD", f"{totals['total_ead']:,.0f}")
    c3.metric("Total ECL", f"{totals['total_ecl']:,.0f}")
    c4.metric("Coverage", f"{totals['coverage']:.2f}%")

    st.subheader("Stage summary")
    st.dataframe(pd.DataFrame([
        {"Stage": "Stage 1", "Count": totals["stage1"]["count"], "EAD": totals["stage1"]["ead"], "ECL": totals["stage1"]["ecl"], "Coverage %": totals["stage1"]["coverage"]},
        {"Stage": "Stage 2", "Count": totals["stage2"]["count"], "EAD": totals["stage2"]["ead"], "ECL": totals["stage2"]["ecl"], "Coverage %": totals["stage2"]["coverage"]},
        {"Stage": "Stage 3", "Count": totals["stage3"]["count"], "EAD": totals["stage3"]["ead"], "ECL": totals["stage3"]["ecl"], "Coverage %": totals["stage3"]["coverage"]},
    ]), use_container_width=True)

    st.subheader("Account-level ECL")
    st.dataframe(df, use_container_width=True, height=400)

    # provision comparison demo
    prud = totals["total_ecl"] * 0.9
    pc = provision_comparison(totals["total_ecl"], prud)
    st.subheader("NRB provision comparison")
    st.write(pc)

    # downloads
    tenant = TenantConfig(name=tenant_name)
    d = tempfile.mkdtemp()
    xp = generate_excel_report(rows, totals, tenant, os.path.join(d, "ecl_report.xlsx"))
    cp = generate_csv_report(rows, os.path.join(d, "ecl_report.csv"))
    jp = generate_json_report(rows, totals, os.path.join(d, "ecl_report.json"))

    st.subheader("Download reports")
    col1, col2, col3 = st.columns(3)
    with open(xp, "rb") as f:
        col1.download_button("Excel (.xlsx)", f, "ecl_report.xlsx")
    with open(cp, "rb") as f:
        col2.download_button("CSV (.csv)", f, "ecl_report.csv")
    with open(jp, "rb") as f:
        col3.download_button("JSON (.json)", f, "ecl_report.json")

    st.info("All outputs are PRELIMINARY/RESEARCH. Not approved for statutory booking.")
