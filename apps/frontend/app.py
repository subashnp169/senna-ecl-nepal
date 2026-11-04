"""Clean system frontend: wizard + transparency + history."""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
import pandas as pd

from config import INFINITY_FULL_DATA, MAX_ROWS_DISPLAY
from pipeline import run_pipeline
from db import list_runs

st.set_page_config(page_title="SENNA ECL — System", layout="wide")

page = st.sidebar.radio("Navigate", ["Run ECL", "User Guide"], index=0)

if page == "User Guide":
    st.title("SENNA ECL — User Guide")
    guide_path = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "user-guide", "ecl-guide.md")
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "user-guide", "ecl-guide.pdf")
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            st.download_button("Download User Guide (PDF)", f, "ecl-guide.pdf", mime="application/pdf")
    if os.path.exists(guide_path):
        with open(guide_path, encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.warning("Guide not found.")
    st.stop()

st.title("SENNA ECL — System")
st.caption("Well-organized, transparent, user-friendly ECL system. Preliminary/Research outputs only.")

with st.sidebar:
    st.header("Settings")
    tenant_name = st.text_input("Tenant name", "Infinity Laghubitta Bittiya Sanstha Ltd.")
    as_of_date = st.text_input("As-of date", "2025-06-30")
    institution_id = st.text_input("Institution ID", "ILBSL")
    st.divider()
    st.subheader("Data source")
    mode = st.radio("Source", ["Bundled Infinity sample", "Full Infinity data (local)", "Upload file"], index=0)
    uploaded = None
    if mode == "Upload file":
        uploaded = st.file_uploader("Upload vendor Excel (.xlsx)", type=["xlsx"])

st.divider()

colA, colB = st.columns([1, 3])
run_clicked = colA.button("▶ Run ECL", type="primary")
if colB.button("Show run history"):
    st.session_state["show_history"] = True

source_path = None
if mode == "Bundled Infinity sample":
    source_path = "sample_data/infinity_sample.xlsx"
elif mode == "Full Infinity data (local)":
    source_path = str(INFINITY_FULL_DATA)
    if not INFINITY_FULL_DATA.exists():
        st.warning("Full Infinity data not found at the configured path.")

if run_clicked:
    if mode == "Upload file":
        if uploaded is None:
            st.error("Please upload a file first.")
            st.stop()
        import tempfile
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        tmp.write(uploaded.read()); tmp.close()
        source_path = tmp.name

    if not source_path or not os.path.exists(source_path):
        st.error("Source file not available.")
        st.stop()

    progress = st.progress(0, text="Starting...")
    result = None
    # run pipeline (synchronous); show steps after
    with st.spinner("Running pipeline..."):
        result = run_pipeline(source_path, tenant_name=tenant_name, as_of_date=as_of_date,
                              institution_id=institution_id)

    progress.progress(100, text="Done")

    # Transparency: step trace
    st.subheader("Pipeline trace (transparency)")
    for i, s in enumerate(result.steps):
        icon = "✅" if s.status == "ok" else ("❌" if s.status == "failed" else "⏳")
        st.write(f"{icon} **{s.name}** — {s.detail} ({s.duration_ms} ms)")

    if not result.ok:
        st.error(f"Pipeline failed: {result.error}")
        st.stop()

    totals = result.totals
    rows = result.rows

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Loans", totals["count"])
    c2.metric("Total EAD", f"{totals['total_ead']:,.0f}")
    c3.metric("Total ECL", f"{totals['total_ecl']:,.0f}")
    c4.metric("Coverage", f"{totals['coverage']:.2f}%")

    # Stage summary
    st.subheader("Stage summary")
    st.dataframe(pd.DataFrame([
        {"Stage": "Stage 1", "Count": totals["stage1"]["count"], "EAD": totals["stage1"]["ead"], "ECL": totals["stage1"]["ecl"], "Coverage %": totals["stage1"].get("coverage", 0)},
        {"Stage": "Stage 2", "Count": totals["stage2"]["count"], "EAD": totals["stage2"]["ead"], "ECL": totals["stage2"]["ecl"], "Coverage %": totals["stage2"].get("coverage", 0)},
        {"Stage": "Stage 3", "Count": totals["stage3"]["count"], "EAD": totals["stage3"]["ead"], "ECL": totals["stage3"]["ecl"], "Coverage %": totals["stage3"].get("coverage", 0)},
    ]), use_container_width=True)

    # NRB provision comparison
    pc = totals.get("provision_comparison")
    if pc:
        st.subheader("NRB provision comparison")
        st.write(pc)

    # Account-level table (capped for display)
    st.subheader(f"Account-level ECL (showing first {min(len(rows), MAX_ROWS_DISPLAY)} of {len(rows)})")
    df = pd.DataFrame(rows[:MAX_ROWS_DISPLAY])
    st.dataframe(df, use_container_width=True, height=400)

    # Downloads
    st.subheader("Download reports")
    col1, col2, col3, col4 = st.columns(4)
    for col, kind, label, mime in ((col1, "excel", "Excel (.xlsx)", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                                   (col2, "csv", "CSV (.csv)", "text/csv"),
                                   (col3, "json", "JSON (.json)", "application/json"),
                                   (col4, "html", "HTML (.html)", "text/html")):
        pth = result.report_paths.get(kind)
        if pth and os.path.exists(pth):
            with open(pth, "rb") as f:
                col.download_button(label, f, os.path.basename(pth), mime=mime)
    # Preview HTML inline
    hp = result.report_paths.get("html")
    if hp and os.path.exists(hp):
        st.subheader("HTML report preview")
        with open(hp, encoding="utf-8") as f:
            st.components.v1.html(f.read(), height=600, scrolling=True)

    st.info("All outputs are PRELIMINARY/RESEARCH. Not approved for statutory booking.")
    st.session_state["last_result"] = result.run_id

# Run history
if st.session_state.get("show_history"):
    st.divider()
    st.subheader("Run history")
    runs = list_runs(20)
    if runs:
        st.dataframe(pd.DataFrame(runs), use_container_width=True)
    else:
        st.write("No runs yet.")
