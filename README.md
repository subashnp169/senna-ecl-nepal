# SENNA ECL Nepal

**Standard, professional Expected Credit Loss (ECL) engine for Nepal's banking and microfinance sector**, built on NFRS 9 / IFRS 9, the Nepal Rastra Bank (NRB) *NFRS 9 – Expected Credit Loss Related Guidelines, 2024* (with the 2082/83 first amendment) and the NRB *Guidance Note on Interest Income Recognition, 2025*.

This project is the consolidated, production-oriented successor to the earlier SENNA ECL Cloud pilots. It combines:

- an **international, jurisdiction-neutral ECL calculation core** (`packages/ecl_core`), and
- a **versioned Nepal regulatory rule pack** (`packages/regulatory_nepal`) — calendar-month delinquency backstops, PD/LGD floors, POCI handling, Class D mapping, interest-income transition rules and NRB annex outputs.

> Status: **Research / engineering baseline — not approved for statutory booking.** All outputs must display `RESEARCH`, `SIMULATION` or `PRELIMINARY` until the release gates in `docs/regulatory/release-gates.md` are met.

## Quick start

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

# Run the core demo
python -m packages.ecl_core.demo

# Run tests
pytest -q

# Streamlit dashboard
streamlit run apps/dashboard/app.py
```

## Layout

| Path | Purpose |
|---|---|
| `packages/ecl_core` | Jurisdiction-neutral IFRS 9 engine: staging, SICR, PD (term structure + Vasicek PIT), LGD, EAD, discounting, scenarios, overlays |
| `packages/regulatory_nepal` | Versioned NRB rule pack: calendar-month backstops, PD/LGD floors, POCI, Class D mapping, interest income, NRB annex outputs |
| `connectors/excel_2_2` | Upload-first parser for the CBS 2.2 portfolio report |
| `apps/api` | FastAPI tenant/upload/snapshot/calculation API |
| `apps/dashboard` | Streamlit interactive dashboard |
| `tests` | Deterministic unit + integration tests |
| `docs` | Architecture, regulatory, research |

## Key references

- NRB, *NFRS 9 – Expected Credit Loss Related Guidelines, 2024* (Jan/May 2024)
- NRB, First Amendment, 2082/83 (calendar-month delinquency; POCI for new loans to previously Stage-3 accounts)
- NRB, *Guidance Note on Interest Income Recognition, 2025*
- IFRS 9 (as pronounced in Nepal)
- Open-source references (MIT / Apache-2.0): ShrishDhuria/IFRS9_ECL, gbadedata/ifrs9-ecl-engine, creditriskengine (PyPI)

## License

MIT. See `LICENSE`. Third-party attributions in `THIRD_PARTY_NOTICES.md`.
