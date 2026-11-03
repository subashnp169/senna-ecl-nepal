# Open-source ECL assessment

## Decision scale

- **ADOPT** — use as a dependency after security/licence review.
- **ADAPT** — selectively port tested logic with attribution and validation.
- **REFERENCE** — study methodology only; do not import production code.
- **REJECT** — unrelated or unsuitable.

| Repository | Decision | Reason |
|---|---|---|
| `naenumtou/ifrs9` | REFERENCE / selective ADAPT | Strong educational coverage of PD, LGD, EAD, staging and ECL; notebook-oriented, not a production service. |
| `naenumtou` focused PD/LGD repositories | REFERENCE / selective ADAPT | Useful migration/PIT and workout-LGD patterns; requires independent formula and licence verification per repository. |
| `rosannelai/Expected-Credit-Loss` | REFERENCE | Clear lifetime-ECL example on Prosper data; old, narrow and not governed. |
| `DTMhango/ifrs9_ecl_shiny` | REJECT for engine; REFERENCE for UI | Public app skeleton, but README marks key PD/LGD/EAD sections TBC. |
| `ShrishDhuria/IFRS9_ECL` | RESEARCH CANDIDATE | Very recent practitioner-style project; immature public history and validation require review before any reuse. |
| `gbadedata/ifrs9-ecl-engine` | RESEARCH CANDIDATE | Recent large-loan notebook project; provenance, licence and reproducibility must be checked. |
| `ekmungai/python-accounting` | OPTIONAL LATER | Accounting/subledger concepts, not an ECL model. |
| `ekmungai/eloquent-ifrs` | OPTIONAL LATER | Laravel accounting/reporting, not an ECL model. |
| IFRS 17 engines | REJECT | Insurance-contract standard, not IFRS 9 credit impairment. |

## Mandatory acceptance checks

Before importing any open-source code:

1. identify an explicit licence;
2. preserve required notices;
3. pin the reviewed commit SHA;
4. reproduce formulas independently;
5. add deterministic unit tests;
6. test edge cases and numerical stability;
7. remove sample institution parameters;
8. validate against synthetic and Infinity-approved test portfolios;
9. document modifications and model limitations;
10. obtain independent model review before official use.

## Product rule

No public notebook becomes the regulatory source of truth. NRB source paragraphs and institution-approved policy remain authoritative. Open source may accelerate implementation, not substitute for governance.
