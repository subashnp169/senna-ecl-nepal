# SENNA ECL Nepal — Complete User Guide

> A plain-language guide to Expected Credit Loss (ECL) under NFRS 9 / IFRS 9, the
> Nepal Rastra Bank (NRB) guidelines, and how this system calculates it.
> Written for risk officers, finance teams, auditors, and anyone new to ECL.

---

## 1. What is Expected Credit Loss (ECL)?

When a bank lends money, some borrowers may not repay. **ECL is the amount the bank
expects to lose** on its loans, calculated *before* the loss actually happens.

Under the old rules, banks only recognised losses after a borrower defaulted (incurred
loss). Under **NFRS 9 (Nepal Financial Reporting Standards 9)**, banks must recognise
losses **from day one** — forward-looking, probability-weighted, and discounted.

```
ECL = PD × LGD × EAD
```

- **PD** = Probability of Default (will the borrower fail to pay?)
- **LGD** = Loss Given Default (how much will we lose if they default?)
- **EAD** = Exposure at Default (how much money is at risk?)

---

## 2. Regulatory framework in Nepal

### 2.1 Who must comply
All banks and financial institutions (BFIs) licensed under the Bank and Financial
Institution Act, 2073 that prepare financial statements under NFRS.

### 2.2 Key NRB documents
| Document | Issued | Key content |
|---|---|---|
| NFRS 9 — ECL Related Guidelines, 2024 | Jan/May 2024 | Staging, PD/LGD/EAD, floors, governance, reporting |
| First Amendment (2082/83) | Jul 2025 | Calendar-month delinquency backstops, POCI rule |
| Guidance Note on Interest Income Recognition, 2025 | Jul 2025 | Quarterly, previous-quarter stage |
| Unified Directives (Class D) | Ongoing | Prudential provision, NPL classification |

### 2.3 Applicability timeline
- ICAN carve-out deferred full NFRS 9 implementation until FY 2080/81.
- From FY 2081/82: all BFIs must use the ECL impairment model.
- CET1 transition: 80% → 60% → 40% → 20% → 0% add-back over 5 years.

---

## 3. How ECL is calculated (step by step)

### Step 1 — Stage classification
Every loan is placed in one of three stages based on credit risk:

| Stage | Condition | ECL horizon |
|---|---|---|
| **Stage 1** | Performing, no significant increase in credit risk (SICR) | 12-month ECL |
| **Stage 2** | SICR since origination (but not yet defaulted) | Lifetime ECL |
| **Stage 3** | Credit-impaired / defaulted | Lifetime ECL (with recovery assessment) |

### Step 2 — NRB calendar-month backstops (2082/83 amendment)
| Days past due (DPD) | Stage backstop |
|---|---|
| Up to 30 days (1 month) | Stage 1 |
| 31–90 days (1–3 months) | Stage 2 |
| 91+ days (more than 3 months) | Stage 3 |

> DPD is a **backstop**, not the whole policy. Qualitative triggers (watchlist,
> forbearance, covenant breach, bankruptcy, etc.) can also move a loan to Stage 2/3.

### Step 3 — Calculate PD (Probability of Default)
Infinity's PD model (per SAR Advisors methodology) works in 6 steps:

1. **Define default** and build the default history (observed default rates by segment and year).
2. **Estimate TTC PD** (through-the-cycle, long-run default rate) = average of annual default rates over 5+ years.
3. **Calibrate Vasicek**: asset correlation (ρ) and credit cycle index (Z).
4. **Link Z to macroeconomic variables** (GDP, inflation, credit growth, sector indicators) via regression.
5. **Project scenarios** (base/best/worst) and convert TTC→PIT PD for each year.
6. **Build term structure** (12-month and lifetime) and apply the 2.5% NRB floor.

**Vasicek formula (standard form):**
```
PIT_PD = Φ( (Φ⁻¹(TTC_PD) + √ρ · Z) / √(1 − ρ) )
```
- Φ = standard normal CDF
- TTC_PD = through-the-cycle default rate
- ρ = asset correlation
- Z = credit cycle index (positive = downturn/adverse conditions → higher PIT PD)

> Note: at Z=0 the PIT PD is NOT equal to TTC PD. TTC PD is the expectation over Z~N(0,1).

- **12-month PD**: likelihood of default within 12 months.
- **Lifetime PD**: likelihood of default over the remaining life of the loan.
- PD must use historical data + forward-looking macro information (no proxies).
- **NRB floor**: minimum 2.5% PD for all exposures.

### Step 4 — Calculate LGD (Loss Given Default)
- LGD = 1 − Recovery Rate.
- First use **observed historical recovery** experience.
- If no history: use collateral value with prudential haircut (25% amended).
- Collateral not realized within 5 years of default cannot be used.
- **NRB floor**: minimum 45% LGD if no reliable history (board approval required).
- GoN-guaranteed exposures: minimum 0% LGD (20% for FX).
- Subordinated claims: minimum 75% LGD.

### Step 5 — Calculate EAD (Exposure at Default)
- EAD = Outstanding balance + Undrawn limit × Credit Conversion Factor (CCF).
- Includes accrued interest and fees.
- For revolving facilities, model expected future drawdowns.

### Step 6 — Discount to present value
- ECL is discounted using the **Effective Interest Rate (EIR)**.
- Formula: ECL = Σ [ PD(t) × (1 − cumulative PD) × LGD(t) × EAD(t) × DF(t) ]

### Step 7 — Scenario weighting
Run the calculation under 3 macro scenarios:
| Scenario | Typical weight | Adjustments |
|---|---|---|
| Optimistic | 20% | PD × 0.7, LGD × 0.9 |
| Base | 50% | PD × 1.0, LGD × 1.0 |
| Pessimistic | 30% | PD × 1.4, LGD × 1.15 |

**Final ECL = weighted average of all three.**

### Step 8 — Apply overlays (PMA)
Management overlays (post-model adjustments) for factors not captured by the model:
- Sector stress, pandemic, natural disaster, regulatory changes.
- Each overlay requires documented reason and approval.

### Step 9 — Compare with prudential provision
NRB requires: **Provision = max(Calculated ECL, NRB Prudential Provision)**.
The "higher-of" rule ensures ECL never falls below the prudential floor.

### Step 10 — Interest income recognition (NRB 2025)
| Stage | Method | Basis |
|---|---|---|
| Stage 1 & 2 | Effective Interest Rate (EIR) | Gross carrying amount |
| Stage 3 | Cash basis | Actual cash received |

- Uses the **previous quarter's stage** for the current quarter's interest recognition.
- Requires quarterly account-level evidence from FY 2083/84.

---

## 4. Data requirements — what details are needed

### 4.1 Minimum required (V0.1 pilot)
| Field | Source | Description |
|---|---|---|
| account_id | CBS | Unique loan account number |
| customer_id | CBS | Customer identifier |
| outstanding | CBS | Current outstanding principal |
| origination_date | CBS | Loan disbursement date |
| maturity_date | CBS | Loan maturity date |
| dpd | CBS | Days past due |
| classification | CBS | NRB classification (Pass/Substandard/Doubtful/Loss) |

### 4.2 Recommended (V0.2+) — per SAR Advisors data request
| Field | Source | Why needed |
|---|---|---|
| undrawn_limit | CBS | For EAD calculation |
| interest_rate / EIR | CBS | Discounting |
| collateral_value + type + valuation date | CBS/Valuation | LGD calculation |
| cash collateral, guarantees | CBS | Recovery sources |
| sector | CBS | Segmentation |
| branch / geographical location | CBS | Branch-level reporting |
| watchlist flag | Risk system | SICR trigger |
| forbearance flag | Risk system | SICR trigger |
| repayment schedule | CBS | EAD term structure |
| transactions (with reversals) | CBS | Cash flow validation |
| macro indicators (GDP, inflation, credit growth, sector) | NRB/IMF/ADB | Forward-looking scenarios |
| historical stage/default/recovery | CBS | PD/LGD calibration |
| defaulted/closed accounts (date of first default, balance at default, recoveries with dates/sources, costs, write-offs) | CBS | LGD workout |
| off-balance sheet (undrawn limits, commitments, guarantees, utilization) | CBS | EAD/CCF |
| credit risk ratings (origination + current) | Risk system | SICR / segmentation |
| NRB provisioning by category, regulatory reserve, previous ECL workings | Finance | Reconciliation |
| investment/placement details | Treasury | Other exposures |

### 4.3 Period covered
- At least **5 years** of loan-level history (NRB requirement for PD).
- **7 years** recommended where the system holds it (more Vasicek observations).
- For LGD: all defaulted accounts closed or recovered.

### 4.3 NRB 2.2 report fields (Infinity's format)
The system reads Infinity's NRB 2.2 report directly:
- `AC_NO` → account_id
- `CUSTOMER_CODE` → customer_id
- `F_OUTSTANDING_PRICIPAL` → outstanding
- `F_APPROVED_LIMIT` → undrawn_limit (derived)
- `INT_RATE` → interest_rate
- `OVERDUE_DAYS` → dpd
- `CLASSIFICATION` → NRB classification (1=Pass, 1.1=Watchlist, 3=Substandard, 4=Doubtful, 5=Loss)
- `CAT_NAME` → sector
- `BR_NAME` → branch
- `F_TYPE_OF_CREDIT` → product

---

## 5. POCI (Purchased or Originated Credit Impaired)

A new loan disbursed in the current period to an account that was **Stage 3 at the previous reporting date**
is treated as POCI. This requires:
- Previous-quarter stage history.
- Old-to-new account linkage (top-up/renewal detection).
- Lifetime ECL from origination (not from SICR date).

---

## 6. NRB floors and overrides (versioned rule pack)

| Parameter | Floor | When applied |
|---|---|---|
| PD | 2.5% minimum | All exposures |
| LGD (no history) | 45% minimum | Board approval required |
| Collateral haircut | 25% | Amended wording |
| GoN-guaranteed LGD | 0% minimum | Government-guaranteed |
| FX GoN-guaranteed LGD | 20% minimum | Foreign currency |
| Subordinated claims LGD | 75% minimum | Subordinated debt |

> **Transparency rule**: the system always shows raw model output, floor applied, final parameter,
> and reason. It never silently replaces model estimates.

---

## 7. Reports generated by the system

| # | Report | Format |
|---|---|---|
| 1 | ECL Summary by Stage | Excel/CSV/JSON |
| 2 | Stage Migration Matrix | Excel/CSV/JSON |
| 3 | Account-level ECL Detail (with triggers) | Excel/CSV/JSON |
| 4 | PD/LGD/EAD by Segment | Excel/CSV/JSON |
| 5 | Scenario Analysis & Sensitivity | Excel/CSV/JSON |
| 6 | Provision Comparison (ECL vs Prudential) | Excel/CSV/JSON |
| 7 | IFRS 7 Disclosure Tables | Excel/CSV/JSON |
| 8 | Vintage Analysis | Excel/CSV/JSON |
| 9 | Branch/Sector Summaries | Excel/CSV/JSON |
| 10 | Interest Income Reconciliation | Excel/CSV/JSON |
| 11 | Data Quality & Validation Report | Excel/CSV/JSON |
| 12 | Audit Trail / Calculation Manifest | Excel/CSV/JSON |
| 13 | Movement Analysis (ECL Bridge) | Excel/CSV/JSON |

---

## 7b. SICR indicators (per NRB 2024 / SAR Advisors)

Quantitative (test each against institution data):
- More than 30 days past due
- Absolute lifetime PD of 5% or more
- Relative lifetime PD increase of 100% or more since origination
- Risk rating downgraded by 2 notches, or to non-investment grade

Qualitative:
- Deterioration in borrower's cash flows or financial position
- Expectation of forbearance/restructuring due to financial difficulty
- Modification of terms resulting in restructuring/rescheduling
- Deterioration of prospects for the borrower's sector
- Borrowers affected by adverse macroeconomic conditions (supportable forecasts)
- Weaker credit quality indicators in individual monitoring
- Management decision to strengthen collateral/covenants due to rising risk

> The 30 days past due indicator is a **backstop that cannot be overridden** by a
> favorable model result.

## 7c. Segmentation (collective vs individual)

- **Collective**: retail and small-ticket loans, business loans below the large-exposure threshold — grouped by shared risk characteristics.
- **Individual**: large exposures, Stage 3 exposures, exposures with borrower-specific information.
- Segment tests: homogeneity (default rates alike), data sufficiency (enough defaults), stability (consistent across years).
- Restructured/rescheduled loans tracked as a separate flag.
- Segmentation reviewed at least annually and on new products / material portfolio shifts.

## 7d. Probation and stage transfers

- Stage 2 → Stage 1: only with evidence of significant reduction in credit risk (Board-approved criteria).
- Stage 3 exit: minimum 180 days probation.
- Restructured Stage 3 exit: minimum 24 months probation.
- Restructured exposures: no move back to 12-month ECL without sufficient evidence of improved credit risk.

## 7e. Back-testing and model monitoring

- Compare predicted defaults, recoveries, and losses with actual outcomes at least annually.
- Recommend model adjustments where differences are material.
- Independent validation by a reviewer independent of the model-building team.
- Internal Audit independently reviews data integrity, policy compliance, and follow-up of findings.

## 7f. NRB quarterly reporting and transition

- **NRB Annexes 1–4**: submitted within 15 days of quarter end.
- **Day 1 impact & CET1 transition**: add-back over 5 years (85% / 65% / 50% / 30% / 15%).
- **NFRS 7 disclosures**: stage-wise carrying amounts, loss allowance reconciliation, stage migration, write-offs and recoveries.
- **Regulatory reserve**: institution recognizes the higher of ECL and NRB Unified Directives provisions; reconciled quarterly.

## 7g. Board-approved ECL policy (minimum contents)

Roles and responsibilities; control procedures for model development/validation;
criteria for individual and collective assessment (including large exposure definition);
SICR indicators; staging criteria (qualitative + quantitative); criteria for moving to a lower stage;
sources of forward-looking information (macro factors).

## 8. How to use the system (step by step)

1. **Prepare data**: Download the vendor template (`templates/SENNA_ECL_Vendor_Data_Template.xlsx`)
   or use Infinity's NRB 2.2 report directly.
2. **Open the frontend**: `streamlit run apps/frontend/app.py`
3. **Select data source**: Bundled sample / Full Infinity data / Upload file.
4. **Set parameters**: Tenant name, as-of date, institution ID.
5. **Click "Run ECL"**: The system runs 4 steps:
   - Ingest & validate (schema, types, control totals)
   - ECL calculation (staging → PD/LGD/EAD → scenarios)
   - Generate reports (Excel/CSV/JSON)
   - NRB provision comparison
6. **Review**: KPIs, stage summary, account table, provision comparison.
7. **Download**: Excel, CSV, JSON reports.
8. **Audit**: Check the pipeline trace and run history.

---

## 9. Glossary

| Term | Meaning |
|---|---|
| ECL | Expected Credit Loss — probability-weighted present value of cash shortfalls |
| PD | Probability of Default |
| LGD | Loss Given Default |
| EAD | Exposure at Default |
| SICR | Significant Increase in Credit Risk |
| POCI | Purchased or Originated Credit Impaired |
| DPD | Days Past Due |
| EIR | Effective Interest Rate |
| PMA | Post-Model Adjustment (overlay) |
| NRB | Nepal Rastra Bank |
| NFRS | Nepal Financial Reporting Standards |
| IFRS | International Financial Reporting Standards |
| CET1 | Common Equity Tier 1 capital |
| BS | Bikram Sambat (Nepal calendar) |
| AD | Anno Domini (Gregorian calendar) |

---

## 10. Important notes

- All outputs are **PRELIMINARY/RESEARCH** until the release gates are met.
- The system never silently replaces model estimates with floors — it shows raw, floor, final, and reason.
- No production customer data should be committed to Git.
- Independent model validation is required before statutory use.
