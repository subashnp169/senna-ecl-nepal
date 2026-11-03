# Architecture

Two independent layers:

## International ECL Core (`packages/ecl_core`)
- staging orchestration
- 12-month and lifetime PD
- LGD / recovery
- EAD and expected cash flows
- scenario weighting
- discounting
- overlays
- reconciliation and validation

## Versioned Nepal Rule Pack (`packages/regulatory_nepal`)
- calendar-month delinquency backstops
- PD/LGD floors
- collateral valuation restrictions
- POCI rule
- Class D regulatory classification mapping
- prudential provision comparison
- NRB annex outputs
- BS/AD calendar
- quarterly interest-income transition rules

Every calculation stores `core_version` and `rule_pack_version`.
