# SENNA ECL Cloud — Final Nepal ECL Research Baseline

Status: **Research baseline for product development; not accounting or legal sign-off**  
Cut-off: 3 July 2026

## 1. Regulatory conclusion

Nepal Rastra Bank's *NFRS 9 — Expected Credit Loss Related Guidelines, 2024* requires NFRS-applicable licensed banks and financial institutions to adopt the NFRS 9 expected-credit-loss impairment model after expiry of the ICAN carve-out through FY 2080/81. The guideline establishes supervisory objectives, prudential floors, staging guidance, model governance, reporting and audit expectations.

The 2082/83 amendment changes the delinquency language from fixed day counts to calendar-month wording:

- Stage 1 quantitative backstop: current or overdue up to **one month**.
- Stage 2 quantitative backstop: overdue more than **one month** but not exceeding **three months**.
- Stage 3 quantitative backstop: overdue more than **three months**.

The engine must therefore calculate both exact DPD and calendar-month delinquency. It must not permanently hard-code 30/90-day assumptions as the Nepal regulatory rule.

The amendment also treats a new loan disbursed in the current reporting period to an account that was Stage 3 at the previous reporting date as purchased or originated credit impaired (POCI) for the guideline's purposes. This makes previous-quarter customer/account history and old-to-new loan linkage strategically important.

## 2. Core ECL measurement

ECL is the probability-weighted present value of contractual cash shortfalls. PD × LGD × EAD is the principal implementation framework, but the platform must retain:

- contractual cash flows;
- expected cash flows;
- timing of default and recovery;
- discount rate/EIR;
- scenario probabilities;
- staging and SICR rationale;
- model and overlay versions.

## 3. NRB prudential requirements to parameterize

- PD must be estimated using appropriate historical data and forward-looking information.
- A prudential PD floor of 2.5% is part of the guideline baseline for credit exposures.
- LGD should first use observed historical recovery experience.
- Where historical recovery is unavailable, eligible collateral/other recoverable sources may be used after prudential valuation, disposal time and cost adjustments.
- Collateral that has not been realized within five years after default cannot be used in the specified recovery determination.
- Where reliable LGD cannot be computed, board approval is required and a minimum 45% LGD applies.
- Assumptions must be back-tested against observed experience.
- Other collateral or legally recoverable sources are subject to the applicable haircut, including the amended 25% wording.

All floors must be versioned and override-controlled. The software must never silently replace model estimates: it must show raw model output, floor applied, final parameter and reason.

## 4. Staging design

### Stage 1

- No SICR since initial recognition.
- Current or overdue up to one month under the amended quantitative backstop.
- 12-month ECL.

### Stage 2

- SICR since initial recognition.
- Overdue more than one month but not exceeding three months.
- Watchlist and relevant qualitative indicators.
- Relevant performing restructure/reschedule treatment.
- Lifetime ECL.

### Stage 3

- Credit impaired/defaulted.
- Overdue more than three months.
- NPL/unlikely-to-pay and qualitative default indicators.
- Lifetime ECL, generally with account-specific recovery assessment where material.

DPD is a backstop, not the entire staging policy. The rule engine must support institution-approved qualitative SICR and default triggers, customer contagion and manual overrides with approval and audit evidence.

## 5. Interest-income requirements

The NRB *Guidance Note on Interest Income Recognition, 2025* is supplementary to the ECL guideline. It requires quarterly account-level records and uses the stage at the **previous quarter end** for interest recognition during the current quarter. From FY 2083/84, institutions must maintain quarterly account-level evidence capable of being demonstrated to supervisors and auditors.

The product therefore requires a separate interest-recognition module containing:

- previous-quarter stage;
- current-quarter stage;
- gross carrying amount;
- amortised cost;
- coupon rate;
- effective or deemed effective interest rate;
- accrued interest receivable;
- interest suspense;
- cash interest collected;
- POCI indicator;
- quarter-level journal reconciliation.

ECL and interest recognition share data but must remain separately reproducible calculations.

## 6. Data conclusion for Class D MFIs

The current 2.2 portfolio report is a valid primary period-end snapshot. It is not enough for a fully calibrated ECL model. The minimum viable pilot can begin with:

1. current/historical 2.2 snapshots;
2. loan master, including closed and written-off accounts;
3. contractual repayment schedules;
4. complete loan transactions including reversals;
5. reporting-period control totals.

The production model should subsequently add:

- restructure/reschedule/renewal/top-up events;
- old-to-new account linkage;
- classification/default/cure history;
- write-off and post-default recovery history;
- collateral, guarantee and insurance recovery data;
- EIR/integral fee data;
- qualitative SICR/default indicators.

Old-to-new linkage is not a blocker for V0.1, but it is required for reliable POCI, evergreening, cure, lifetime PD and customer-lifecycle analysis.

## 7. Nepal market conclusion

The Nepal market contains consultancy-led models, institution-specific Excel/Python implementations and commercial platforms. Publicly visible examples include NBI consulting activity, NIFRA's procurement for an interoperable NFRS 9 solution, Global IME's announced implementation arrangement with vizuaMatix/partners, and FineIT's marketed Estimator 9 product. Public claims must be validated through named references, demonstrations and reconciliation tests.

No public repository was found that combines all of the following:

- IFRS/NFRS 9 ECL engine;
- current NRB rule pack and amendment history;
- Class D portfolio treatment;
- 2.2 ingestion;
- customer loan-chain/POCI logic;
- multi-tenant SaaS isolation;
- maker-checker approval;
- model governance and audit evidence;
- NRB and interest-recognition reporting.

That combination is the defensible product opportunity for SENNA ECL Cloud.

## 8. Product decision

Build a Nepal-focused SaaS with two independent layers:

### International ECL Core

- staging orchestration;
- 12-month and lifetime PD;
- LGD/recovery curves;
- EAD and expected cash flows;
- scenario weighting;
- discounting;
- overlays;
- reconciliation and validation.

### Versioned Nepal Rule Pack

- calendar-month delinquency backstops;
- PD/LGD floors;
- collateral valuation restrictions;
- POCI rule;
- Class D regulatory classification mapping;
- prudential provision comparison;
- NRB annex outputs;
- BS/AD calendar;
- quarterly interest-income transition rules.

## 9. Release gates

A calculation may be marked `OFFICIAL` only when all of the following are approved:

- source-to-report reconciliation;
- staging/default/SICR policy;
- segmentation;
- PD methodology and calibration;
- LGD methodology and recovery evidence;
- EAD/cash-flow method;
- scenario methodology;
- overlay governance;
- regulatory rule-pack sign-off;
- Finance/Risk/Internal Audit review;
- independent/external validation where applicable.

Until then, all outputs must display `RESEARCH`, `SIMULATION` or `PRELIMINARY`.

## 10. Primary sources

- Nepal Rastra Bank, *NFRS 9 — Expected Credit Loss Related Guidelines, 2024*.
- Nepal Rastra Bank, 2082/83 amendment to the ECL Guidelines.
- Nepal Rastra Bank, *Guidance Note on Interest Income Recognition, 2025*.
- Current NRB Unified Directives for Class D institutions.
- NFRS 9 as pronounced in Nepal and applicable institutional accounting policy.
