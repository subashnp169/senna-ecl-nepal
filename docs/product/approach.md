# Best approach: building a professional ECL system (Nepal)

## 0. Design goal

A bank/MFI uploads data in its own (or vendor) format; the platform normalises it, validates it, runs the ECL engine, and produces **all required reports in all formats** (Excel, PDF, CSV, JSON, XBRL-ready), with **clean detail** and **tenant-level customisation** (branding, KPIs, layouts, parameters). Multi-tenant SaaS with role-based access and audit trails.

## 1. Patterns observed from leading ECL platforms (FineIT Estimator 9, SAS IFRS 9, ECL Square, ECL Pulse, ECL Suite, ElysianNxt)

| Capability | How leaders do it | Our adoption |
|---|---|---|
| Data ingestion | Governed ingestion: templates, mapping, validation, exception review, approved immutable snapshots; API + flat-file connectors | Upload wizard + template download + mapping + validation + snapshot + exceptions |
| Canonical data model | Portfolio snapshot schema; loan master, collateral, customer, macro, historical, repayment schedule | `schemas/portfolio_snapshot.schema.json` + vendor template |
| Configurability | Segmentation, PD/LGD/EAD models, scenarios, cure rates, collateral types, calculation settings, annual snapshots | Versioned rule pack + parameter registry + per-tenant config |
| Staging | SICR (quantitative + qualitative), DPD backstops, migration matrix, low-credit-risk exemption | `ecl_core.staging` (already) |
| Calculation | 12m & lifetime ECL, scenario weighting, discounting, overlays/PMA, revolving credit | `ecl_core.ecl` (extend revolving) |
| Governance | Maker-checker, version control, audit trail, model registry, locked periods | `ecl_core.governance` (extend) |
| Reporting | Regulator templates, IFRS 7 disclosures, vintage, stage migration, ECL reconciliation, sensitivity, branch summaries; Excel/PDF/XBRL; customizable KPIs | `reporting` module (new) |
| Multi-tenant SaaS | Role-based access, subscription/billing, impersonation, audit logging, tenant branding | `apps/api` + tenant config |
| Deployment | Cloud + on-prem, 14-day deployment, data stays in tenant perimeter | Docker + tenant isolation |

## 2. Canonical data contract (vendor-facing requirement)

Vendors must supply data conforming to a published schema. We provide an **Excel template** (`templates/SENNA_ECL_Vendor_Data_Template.xlsx`) with sheets:

1. `README` — instructions, data dictionary, units, date formats
2. `Loan_Master` — account_id, customer_id, product, sector, origination_date, maturity_date, outstanding, undrawn_limit, interest_rate, eir, dpd, classification, nrb_classification, status, branch, currency
3. `Collateral` — account_id, collateral_type, valuation_date, fair_value, forced_sale_value, haircut
4. `Customer` — customer_id, segment, risk_grade, watchlist_flag, forbearance_flag, npl_history
5. `Repayment_Schedule` — account_id, period, due_date, principal_due, interest_due
6. `Transactions` — account_id, txn_date, amount, type (disbursement/repayment/reversal/writeoff/recovery)
7. `Macro` — period, gdp_growth, inflation, interest_rate, unemployment, scenario weights
8. `Historical` — account_id, period, stage, default_flag, recovery_amount (for PD/LGD calibration)

Validation rules: required fields, types, ranges, uniqueness, referential integrity, control totals (sum of outstanding = reported total), date consistency, no negatives.

## 3. End-to-end flow

```
Vendor data (own format)
   -> Download template OR map own columns (mapping wizard)
   -> Upload (Excel/CSV/API)
   -> Parse & validate (schema, types, ranges, FKs, control totals)
   -> Exception report (missing/invalid rows) -> maker review
   -> Approved snapshot (immutable, versioned, checksummed)
   -> ECL engine (staging -> PD/LGD/EAD -> scenario weighting -> overlays)
   -> Governance (maker-checker-approver)
   -> Reporting (all formats, tenant-branded)
   -> Export / regulator submission / audit pack
```

## 4. Tenant customisation

- **Parameters**: PD/LGD/EAD models, scenario weights, floors, collateral haircuts, segmentation, cure rules — per tenant, versioned.
- **Branding**: logo, colours, report headers/footers, language (EN/NP).
- **Reports**: selectable report set, column layouts, KPIs, thresholds, grouping (branch/sector/product).
- **Workflows**: approval chains, notification rules, SLAs.
- **Calendars**: BS/AD, fiscal year boundaries.

## 5. Reporting catalogue (all formats)

Core reports (Excel multi-sheet + PDF + CSV + JSON):
1. ECL Summary by Stage
2. Stage Migration Matrix (period-over-period)
3. Account-level ECL detail (with triggers & explainability)
4. PD/LGD/EAD by segment
5. Scenario analysis & sensitivity
6. Provision comparison (ECL vs prudential)
7. IFRS 7 disclosure tables
8. Vintage analysis
9. Branch/sector summaries
10. Interest income reconciliation (NRB 2025)
11. Data quality & validation report
12. Audit trail / calculation manifest
13. Movement analysis (period-over-period ECL bridge)

## 6. Implementation plan (phased)

- **Phase A (done)**: core engine + Nepal rule pack + tests + dashboard.
- **Phase B**: canonical schema + vendor template + ingestion/validation pipeline + exception reporting.
- **Phase C**: report generator (multi-format) + tenant config + branding.
- **Phase D**: governance (maker-checker, model registry, locked periods) + interest income module.
- **Phase E**: multi-tenant SaaS (auth, RBAC, billing, audit) + API connectors.
- **Phase F**: validation, DR, security, statutory release gate.

## 7. Immediate next deliverables

Build Phase B + C now: vendor template generator, ingestion pipeline, report generator, tenant config, tests.
