"""Streamlit ECL dashboard for SENNA ECL Nepal."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
import pandas as pd
import numpy as np

from packages.ecl_core import (
    Loan, Stage, classify_stage, lifetime_ecl, marginal_pd_from_cumulative,
    scenario_weighted_ecl, portfolio_aggregate, vasicek_pit_pd,
)
from packages.ecl_core.types import SICRConfig
from packages.regulatory_nepal import (
    NepalRulePack, load_rule_pack, calendar_month_stage, apply_pd_floor,
    apply_lgd_floor, provision_comparison,
)

st.set_page_config(page_title="SENNA ECL Nepal", layout="wide")
st.title("SENNA ECL Nepal — Expected Credit Loss Engine")
st.caption("NFRS 9 / IFRS 9 | NRB NFRS 9 ECL Guidelines 2024 (amended 2082/83) | Research/Preliminary outputs only")

st.sidebar.header("Configuration")
rule_pack = load_rule_pack()
st.sidebar.write(f"Rule pack: {rule_pack.version}")
st.sidebar.write(f"PD floor: {rule_pack.pd_floor:.2%}")
st.sidebar.write(f"LGD floor (no history): {rule_pack.lgd_floor_no_history:.0%}")
st.sidebar.write(f"Collateral haircut: {rule_pack.collateral_haircut:.0%}")

# Sample portfolio
sample = [
    {"name": "AlphaIndustries", "principal": 2_000_000, "orig": "BBB", "curr": "BBB", "lgd": 0.45, "eir": 0.035, "mat": 5, "dpd": 0, "flags": []},
    {"name": "BetaLogistics", "principal": 3_000_000, "orig": "A", "curr": "A-", "lgd": 0.45, "eir": 0.030, "mat": 7, "dpd": 0, "flags": []},
    {"name": "GammaRetail", "principal": 5_000_000, "orig": "BBB", "curr": "BB-", "lgd": 0.45, "eir": 0.045, "mat": 5, "dpd": 0, "flags": []},
    {"name": "DeltaConstruction", "principal": 1_500_000, "orig": "BB", "curr": "BB", "lgd": 0.45, "eir": 0.050, "mat": 4, "dpd": 35, "flags": []},
    {"name": "EpsilonEnergy", "principal": 4_000_000, "orig": "BBB+", "curr": "BBB-", "lgd": 0.45, "eir": 0.040, "mat": 6, "dpd": 0, "flags": ["watchlist"]},
    {"name": "ZetaServices", "principal": 800_000, "orig": "BB", "curr": "CCC", "lgd": 0.45, "lgd_dt": 0.65, "eir": 0.060, "mat": 3, "dpd": 95, "flags": []},
    {"name": "EtaHoldings", "principal": 2_500_000, "orig": "BB+", "curr": "B-", "lgd": 0.45, "lgd_dt": 0.65, "eir": 0.055, "mat": 5, "dpd": 0, "flags": ["distressed_restructuring"]},
]

cum_pd = [0.01, 0.025, 0.04, 0.06, 0.08]
marginals = marginal_pd_from_cumulative(cum_pd)

rows = []
for s in sample:
    loan = Loan(
        name=s["name"], principal=s["principal"], origination_rating=s["orig"],
        current_rating=s["curr"], lgd=s["lgd"], eir=s["eir"], maturity=s["mat"],
        days_past_due=s["dpd"], qualitative_flags=s["flags"], region="global",
        lgd_downturn=s.get("lgd_dt"),
    )
    staging = classify_stage(loan)
    lgd_used = loan.lgd
    if staging.stage == Stage.STAGE_3 and loan.lgd_downturn:
        lgd_used = loan.lgd_downturn
    lgd_used = apply_lgd_floor(lgd_used, has_history=False, floor_no_history=rule_pack.lgd_floor_no_history)
    res = lifetime_ecl(loan.principal, 0.02, marginals, lgd_used, loan.eir, loan.amort_type, staging.stage.value)
    ecl_applied = res["ecl_12m"] if staging.stage == Stage.STAGE_1 else res["ecl_lifetime"]
    nepal_stage = calendar_month_stage(loan.days_past_due)
    rows.append({
        "Loan": loan.name, "Orig": loan.origination_rating, "Curr": loan.current_rating,
        "DPD": loan.days_past_due, "Nepal month-stage": nepal_stage,
        "Stage": staging.stage.value, "EAD": loan.principal, "LGD": round(lgd_used, 4),
        "12m ECL": res["ecl_12m"], "Lifetime ECL": res["ecl_lifetime"],
        "ECL Applied": round(ecl_applied, 2), "Triggers": "; ".join(staging.triggers_fired),
    })

df = pd.DataFrame(rows)
st.subheader("Portfolio ECL results")
st.dataframe(df, use_container_width=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total EAD", f"{df['EAD'].sum():,.0f}")
col2.metric("Total ECL", f"{df['ECL Applied'].sum():,.0f}")
col3.metric("Coverage %", f"{df['ECL Applied'].sum()/df['EAD'].sum()*100:.2f}%")
col4.metric("Stage 3 count", int((df['Stage'] == 3).sum()))

st.subheader("Scenario weighting demo")
scen = st.slider("Base ECL multiplier (base case)", 0.5, 1.5, 1.0, 0.05)
scenarios = [
    {"name": "Optimistic", "weight": 0.2, "multiplier": 0.7},
    {"name": "Base", "weight": 0.5, "multiplier": scen},
    {"name": "Pessimistic", "weight": 0.3, "multiplier": 1.4},
]
base_ecl = float(df["ECL Applied"].sum())
sw = scenario_weighted_ecl(base_ecl, scenarios)
st.write(sw)

st.subheader("Vasicek PIT-PD demo")
colA, colB = st.columns(2)
rho = colA.slider("Asset correlation (rho)", 0.01, 0.5, 0.12, 0.01)
z = colB.slider("Systematic factor z", -3.0, 3.0, 0.0, 0.1)
ttc = 0.02
pit = vasicek_pit_pd(ttc, rho, z)
st.write(f"TTC PD {ttc:.2%} -> PIT PD {pit:.2%} (rho={rho}, z={z})")

st.subheader("NRB provision comparison demo")
prud = st.number_input("Prudential provision", value=100000.0)
pc = provision_comparison(base_ecl, prud)
st.write(pc)

st.info("All outputs are PRELIMINARY/RESEARCH. Not approved for statutory booking.")
