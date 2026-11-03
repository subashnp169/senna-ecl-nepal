# Research summary: building a standard professional ECL for Nepal

## 1. Is there a GitHub repo related to this?

Yes. Your GitHub account (`subashnp169`) already has an empty private repo:
- `subashnp169/ECL-PHASE` (created 2026-07-03, no commits).

There was **no** existing ECL code on GitHub for this project. All prior work lived locally:
- `D:\ECL` (starter + vendor-connectors builds + zips)
- `D:\subashprojects\14-senna-ecl` (full senna-ecl-cloud + notes + extras `ecl.html`)
- `D:\subashprojects\91-version-archives\ecl-versions` (archived copies)
- `D:\subashprojects\92-knowledge-base\architecture` (ADRs, competitor map, roadmap)
- `D:\subash\all items desktops\downloads\stitch (1)` (UI screens: calculation modeling, scenarios, PRD, technical logic)
- `D:\subash\all items desktops\ecl.html` and `D:\subashprojects\14-senna-ecl\extras\ecl.html` (NFRS 9 dashboards)

All of the above have been consolidated into `D:\ECL-ALL-PROJECTS`.

A new canonical repo has been created and pushed:
- `subashnp169/senna-ecl-nepal` (private) — https://github.com/subashnp169/senna-ecl-nepal
- Local project: `D:\senna-ecl-nepal`

## 2. What can be collected from others (research)

### Open-source IFRS 9 ECL references

| Repo / Package | Licence | Decision | Value |
|---|---|---|---|
| ShrishDhuria/IFRS9_ECL | MIT | ADAPT (selective) | PD term structures, SICR waterfall, macro overlays, Vasicek/ASRF PIT-PD, Excel mirror |
| gbadedata/ifrs9-ecl-engine | MIT | REFERENCE | End-to-end PD/LGD/EAD/staging/scenario on 1.35M loans |
| creditriskengine (PyPI) | Apache-2.0 | REFERENCE | Governance overlays (7 types), revolving-credit ECL, multi-jurisdiction floors, Ind AS 109 |
| naenumtou/ifrs9 | unspecified | REFERENCE only | PD/LGD/EAD/staging methodology |
| chetan-umbarje/IFRS9_ECL_Modeling | unspecified | REFERENCE only | Excel+Python ECL, back-testing, PSI/CSI |
| Purity-Creatives/ifrs9-ecl-model-kenya | unspecified | REFERENCE only | CBK-regulated ECL, macro overlays, Board reporting |
| Daniel11OSSE/ifrs9-ecl-modeling | unspecified | REFERENCE only | Scenario analysis template |

### NRB / Nepal regulatory sources

- NRB, *NFRS 9 – Expected Credit Loss Related Guidelines, 2024* (Jan 2024 / May 2024)
- NRB, First Amendment 2082/83: calendar-month delinquency backstops (1 / 3 months), POCI for new loans to previously Stage-3 accounts
- NRB, *Guidance Note on Interest Income Recognition, 2025* (quarterly, previous-quarter stage)
- NRB Unified Directives for Class D institutions (prudential provision floors, NPL classification)
- NFRS 9 as pronounced in Nepal (ICAN carve-out expired FY 2080/81)

### Key NRB parameters to parameterize (versioned)

- PD prudential floor: 2.5%
- LGD: observed historical recovery first; 45% minimum where no reliable history (board approval); 5-year collateral realization rule; 25% collateral haircut (amended); GoN-guaranteed exposures min 0% LGD (20% for FX); subordinated claims min 75% LGD
- Staging backstops: 1 month / 3 months (calendar)
- POCI determination for new loans to prior Stage-3 accounts
- Interest income: EIR on gross carrying amount (Stages 1&2), cash basis (Stage 3), using previous-quarter stage
- CET1 transition: 80/60/40/20/0% add-back over 5 years

### Market conclusion

No public repository combines all of: IFRS/NFRS 9 ECL engine + current NRB rule pack + Class D treatment + 2.2 ingestion + customer loan-chain/POCI logic + multi-tenant SaaS + maker-checker + governance/audit + NRB + interest-recognition reporting. That combination is the defensible product opportunity (SENNA ECL Cloud).

## 3. What was built

New project `D:\senna-ecl-nepal` (pushed to GitHub `subashnp169/senna-ecl-nepal`):

- `packages/ecl_core` — international core: types, staging (SICR waterfall, DPD backstops, qualitative triggers, low-credit-risk exemption), PD (term structures, amortisation, discounting, Vasicek PIT-PD), LGD, EAD, ECL (12m + lifetime, scenario weighting, portfolio aggregation), governance (overlays)
- `packages/regulatory_nepal` — versioned Nepal rule pack: calendar-month staging, PD/LGD floors, POCI, Class D mapping, interest income (NRB 2025), provision comparison, YAML rule pack file
- `connectors/excel_2_2` — 2.2 parser + mapping (reused from vendor-connectors build)
- `apps/api` — FastAPI scaffold (reused)
- `apps/dashboard` — Streamlit interactive dashboard (portfolio ECL, scenarios, Vasicek PIT-PD, NRB provision comparison)
- `tests/test_core.py` — 16 passing tests
- `docs` — architecture, release gates, research

## 4. Next steps to reach a standard professional ECL

1. Replace illustrative S&P PD tables with institution-calibrated PD (transition matrices, TTC/PIT).
2. Add historical snapshot store, repayment schedules, transactions, reversals, cure/default history.
3. Implement maker/checker/approver, model registry, parameter versioning, locked periods.
4. Add interest-income module wiring to quarterly account-level evidence.
5. Independent model validation, security/tenant-isolation tests, DR/backups.
6. Statutory-use release gate (OFFICIAL marking) per `docs/regulatory/release-gates.md`.
