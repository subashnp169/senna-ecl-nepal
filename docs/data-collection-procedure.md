# Data Collection Procedure — SENNA ECL Nepal (Infinity Laghubitta)

> Purpose: document every data element required for a full NFRS 9 / NRB-compliant ECL
> model, what we already have, what is missing, and how to obtain it.

---

## 1. Data we ALREADY HAVE

| Source file | Location | Rows | Key fields | Used for |
|---|---|---|---|---|
| NRB 2.2 Report (REVAMPED) | `D:\data\NRB_2_2_REPORT_REVAMPED_000080__*.xlsx` | 33,180 | AC_NO, CUSTOMER_CODE, BR_CODE/BR_NAME, F_OUTSTANDING_PRICIPAL, F_APPROVED_LIMIT, INT_RATE, OVERDUE_DAYS, CLASSIFICATION, CAT_NAME, F_TYPE_OF_CREDIT, INVESTMENT_NDATE, LOAN_EXPIRY_DATE | Loan master, staging, EAD, sector/branch |
| Collateral (FID) | `D:\subash\Desktop\downloads backup c\FID Collateral Loan.xlsx` (sheet "all security") | 3,649 | member_id, cbs_mem_id, securities_id, fmv, dv | Collateral value, LGD |
| Recovery data | `D:\subash\DESKTOPS ITEMS\2081.82 Recovery Data.xlsx` | 418,434 | CUSTOMER_CODE, PRINCIPAL_PAID, REGULAR_INTERSEST_PAID, PAID_DATE_NEP, ENG_DATE | LGD recovery, cash flows |
| Repayment schedule | `D:\subash\all items desktops\downloads\Installment_Wise_Loan_Repayment_Report__LOCAL__*.xlsx` | varies | installment-wise principal/interest due | EAD term structure |
| Loan schedule | `D:\subash\Desktop\downloads backup c\rptLoanScheduleReport-CP.xls` | varies | payment schedule | EAD |
| Transactions | `D:\subash\Desktop\downloads backup c\Infinity DFS/Utility Transaction Status*.xlsx` | varies | transaction status | cash flow validation |
| Willful defaulters | `D:\subash\all items desktops\downloads\Willful Defaulter*.xlsx` | varies | defaulter list | Stage 3 / default definition |
| Write-off committee | `D:\subash\DESKTOPS ITEMS\4 th write off comitee excel for bod.xlsx` | varies | write-off decisions | Stage 3, LGD |
| Repayment report | `D:\subash\NRB INSPECTION\external audit new\rptLoanRepaymentReport.xlsx` | varies | repayment status | staging |

---

## 2. Data still MISSING (required for full ECL model)

### 2.1 Historical default migration data (CRITICAL for PD)
- **What**: Quarterly/monthly snapshots of the loan book for at least 5 years (7 preferred), with default flags per account per period.
- **Why**: TTC PD = average annual default rate over 5+ years. Vasicek calibration needs annual default observations.
- **Where to get**: Core banking system (CBS) — export "Loan Master as of period-end" for each quarter from FY 2078/79 to date. Alternatively, NRB 2.2 reports archived per quarter (we have some in `D:\data\` and `D:\subash\all items desktops\downloads\`).
- **Format needed**: account_id, period, outstanding, dpd, classification, default_flag (1/0), write_off_flag.
- **Frequency**: quarterly (minimum), monthly (preferred).
- **Status**: ⚠️ PARTIAL — we have multiple NRB 2.2 snapshots across periods but not systematically archived. Need to collect all quarterly 2.2 reports.

### 2.2 Repayment schedules (CRITICAL for EAD)
- **What**: Contractual repayment schedule per loan — due dates, principal due, interest due, installment amount.
- **Why**: EAD term structure (amortisation profile) for lifetime ECL. Without it, we assume 3-year bullet (inaccurate).
- **Where to get**: CBS → "Loan Schedule Report" or "Installment-wise Repayment Report". We found `Installment_Wise_Loan_Repayment_Report__LOCAL__*.xlsx` — verify it covers all accounts and is current.
- **Format needed**: account_id, period_no, due_date, principal_due, interest_due, installment_amount, remaining_balance.
- **Frequency**: as-of each reporting date (or static from origination).
- **Status**: ⚠️ PARTIAL — one file found; need full coverage and current period.

### 2.3 Collateral details (CRITICAL for LGD)
- **What**: Collateral type, valuation date, fair value, forced sale value, valuation basis (market/forced sale).
- **Why**: LGD = 1 − (collateral × (1 − haircut) − costs) / EAD. NRB requires prudential valuation with 25% haircut; collateral not realized within 5 years cannot be used.
- **Where to get**: CBS collateral module or "Collateral Register". We found `FID Collateral Loan.xlsx` with `all security` sheet (3,649 records with fmv, dv).
- **Format needed**: account_id, collateral_type, valuation_date, fair_value, forced_sale_value, valuation_basis.
- **Frequency**: as-of each reporting date (updated on revaluation).
- **Status**: ⚠️ PARTIAL — collateral file exists but needs mapping to account_id and refresh.

### 2.4 Defaulted/closed accounts with recovery detail (CRITICAL for LGD)
- **What**: For every defaulted/closed account: date of first default, balance at default, all post-default recoveries (date, amount, source: collateral sale/collection/settlement/legal), recovery costs, write-off amount and date.
- **Why**: LGD = discounted recoveries / EAD at default. NRB requires historical recovery experience.
- **Where to get**: CBS write-off/recovery module. We found `2081.82 Recovery Data.xlsx` (418K rows of payments) and `4 th write off comitee excel` — need to link payments to defaulted accounts.
- **Format needed**: account_id, default_date, balance_at_default, recovery_date, recovery_amount, recovery_source, recovery_cost, write_off_date, write_off_amount.
- **Frequency**: cumulative (all historical defaults).
- **Status**: ⚠️ PARTIAL — payment data exists but not linked to default events. Need a recovery-linking exercise.

### 2.5 Credit risk ratings (for SICR)
- **What**: Internal credit risk rating at origination and current, for each account (or at least for large exposures).
- **Why**: SICR triggers include 2-notch downgrade and downgrade to non-investment grade. Segmentation by rating.
- **Where to get**: Risk department / CBS rating module. Infinity currently uses NRB classification (1-5) as a proxy.
- **Format needed**: account_id, origination_rating, current_rating, rating_date, rating_agency (internal/external).
- **Frequency**: as-of each reporting date.
- **Status**: ❌ MISSING — Infinity does not have an internal rating system beyond NRB classification. Options: (a) use NRB classification as proxy (current approach), (b) build a simple scoring model, (c) adopt external ratings for large exposures.

### 2.6 Macro-economic data (for forward-looking scenarios)
- **What**: GDP growth, inflation, credit growth, sector indicators, interest rates — at least 5 years quarterly.
- **Why**: Vasicek credit cycle index (Z) linked to macro variables; scenario projection (base/best/worst).
- **Where to get**: NRB (quarterly economic bulletin), IMF (WEO), World Bank, ADB. Infinity's PD model design uses IMF data (MEV Data sheet, 2005-2023).
- **Format needed**: period, gdp_growth, inflation, credit_growth, interest_rate, unemployment, sector_index.
- **Frequency**: quarterly (updated each quarter).
- **Status**: ⚠️ PARTIAL — Infinity has IMF MEV data (2005-2023) in the PD model Excel. Need to update to current period quarterly.

### 2.7 Off-balance sheet exposures
- **What**: Undrawn limits, loan commitments, financial guarantees, utilization history.
- **Why**: EAD includes off-balance sheet via CCF. NRB requires CCF-based conversion.
- **Where to get**: CBS → "Undrawn Limit Report" / "Commitment Register".
- **Format needed**: account_id, limit_type, limit_amount, drawn_amount, utilization_history, expiry_date.
- **Frequency**: as-of each reporting date.
- **Status**: ⚠️ PARTIAL — F_APPROVED_LIMIT exists in 2.2 report but utilization history is missing.

### 2.8 Restructure/reschedule flags
- **What**: Whether a loan was restructured/rescheduled, date, reason, and whether it's still in probation.
- **Why**: SICR trigger (restructured loans), Stage 3 probation (24 months for restructured), stage transfer rules.
- **Where to get**: CBS → "Restructured Loan Report".
- **Format needed**: account_id, restructure_date, restructure_type, restructure_reason, probation_end_date, status.
- **Frequency**: as-of each reporting date.
- **Status**: ❌ MISSING — not in the 2.2 report. Need to request from CBS/risk department.

### 2.9 Investment securities & placements
- **What**: Bank balances, placements with other FIs, investment securities (amortized cost or FVOCI).
- **Why**: ECL scope includes these (per NRB Guidelines).
- **Where to get**: Treasury/Finance department.
- **Format needed**: instrument_id, type, counterparty, amount, rating, maturity, classification.
- **Frequency**: as-of each reporting date.
- **Status**: ❌ MISSING — not in 2.2 report.

### 2.10 Core banking system linkage (account continuity)
- **What**: Mapping of old account numbers to new (after CBS migrations or branch mergers).
- **Why**: Track accounts across years for default migration and cure analysis. POCI detection (new loan to previously Stage-3 account).
- **Where to get**: CBS migration logs / IT department.
- **Format needed**: old_account_id, new_account_id, migration_date, reason.
- **Status**: ❌ MISSING — critical for POCI and historical tracking.

---

## 3. Data collection procedure (step-by-step)

### Phase 1: One-time historical data collection (for PD/LGD calibration)
1. **Identify the period**: FY 2078/79 to FY 2082/83 (5 years minimum, 7 preferred).
2. **Export quarterly 2.2 reports**: From CBS, export the NRB 2.2 report for each quarter-end. Store in `D:\data\history\YYYY_QN\`.
3. **Export recovery data**: From CBS, export all recovery transactions (principal + interest) with account linkage, from the earliest available date.
4. **Export write-off data**: From the write-off committee records, compile all write-offs with account, date, amount, reason.
5. **Export collateral register**: From CBS collateral module, export all collateral with valuation details.
6. **Export restructure register**: From CBS, export all restructured/rescheduled loans.
7. **Export macro data**: Download quarterly GDP, inflation, credit growth from NRB/IMF/World Bank.
8. **Link accounts**: Work with IT to create an account continuity mapping (old → new account numbers).

### Phase 2: Quarterly recurring data collection (for ECL computation)
1. **Week 1 (T+1 to T+2)**: Export current period NRB 2.2 report from CBS. Reconcile to GL (outstanding, interest in suspense).
2. **Week 1**: Export collateral valuations (updated revaluations).
3. **Week 1**: Export recovery transactions for the quarter.
4. **Week 1**: Export restructure/reschedule register for the quarter.
5. **Week 1**: Download latest macro indicators (GDP, inflation, etc.).
6. **Week 2 (T+2 to T+3)**: Run staging and ECL computation in the system.
7. **Week 2**: Review and approve (maker-checker-approver).
8. **Week 3 (T+3 to T+5)**: Submit NRB Annexes 1-4.

### Phase 3: Data quality checks (before every ECL run)
1. Control total: sum of outstanding = reported portfolio total.
2. No negative outstanding or DPD.
3. Unique account IDs.
4. Date consistency (origination ≤ maturity).
5. DPD vs classification consistency.
6. Collateral coverage (at least for Stage 2/3).
7. Macro data completeness (no missing quarters).

---

## 4. Data source contacts

| Data | Department | Contact | Frequency |
|---|---|---|---|
| NRB 2.2 report | CBS / IT | CBS admin | Quarterly |
| Collateral register | Credit / Risk | Risk officer | Quarterly |
| Recovery data | Finance / Recovery | Recovery team | Quarterly |
| Restructure register | Credit / Risk | Credit officer | Quarterly |
| Macro data | Research / Treasury | Economist | Quarterly |
| Account continuity mapping | IT | IT manager | One-time + updates |
| Credit ratings | Risk | Risk officer | Quarterly |

---

## 5. Data gap summary

| Data element | Status | Impact on ECL | Action |
|---|---|---|---|
| Loan master (2.2) | ✅ Available | Core EAD | Use as-is |
| Collateral | ⚠️ Partial | LGD accuracy | Map all security sheet to accounts; refresh valuations |
| Recovery data | ⚠️ Partial | LGD accuracy | Link payments to defaulted accounts |
| Repayment schedule | ⚠️ Partial | EAD accuracy | Verify full coverage |
| Transactions | ⚠️ Partial | Cash flow validation | Export from CBS |
| Restructure flags | ❌ Missing | SICR accuracy | Request from CBS |
| Credit ratings | ❌ Missing | SICR accuracy | Use NRB classification as proxy (interim) |
| Macro data | ⚠️ Partial | Forward-looking | Update to current quarter |
| Historical snapshots (5yr) | ⚠️ Partial | PD accuracy | Collect quarterly 2.2 reports |
| Account continuity | ❌ Missing | POCI detection | Request from IT |
| Investment securities | ❌ Missing | ECL scope | Request from Treasury |
| Off-balance sheet (utilization) | ⚠️ Partial | EAD/CCF | Export utilization history |

---

## 6. Recommended priority actions

1. **Immediate (Week 1)**: Collect all available quarterly 2.2 reports from `D:\data\` and `D:\subash\all items desktops\downloads\` into a structured archive.
2. **Week 2**: Map collateral "all security" sheet to account IDs; verify coverage.
3. **Week 2**: Link recovery payments to defaulted accounts (using CUSTOMER_CODE).
4. **Week 3**: Request restructure register and account continuity mapping from IT.
5. **Week 3**: Update macro data (IMF/NRB) to current quarter.
6. **Week 4**: Build PD calibration using 5+ years of default migration data.
7. **Ongoing**: Establish quarterly data collection routine (Phase 2 above).

---

## 7. Data governance

- **Confidentiality**: All data handled under confidentiality terms. Customer identifiers can be masked.
- **Data accuracy**: Institution is responsible for accuracy and completeness of data provided.
- **Version control**: Each data extract is versioned with date and source system.
- **Retention**: Historical data retained for at least 7 years (NRB requirement).
- **Access**: Role-based access (admin, analyst, viewer) — see `tenants/models.py`.
- **Audit trail**: All data ingestion and processing logged (`db.py`, `logging_setup.py`).
