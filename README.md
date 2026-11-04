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

## For the finance team — validation & review

This repository is the complete SENNA ECL Nepal system, shared with the finance team
for independent validation against Infinity Laghubitta's data.

### What is included
- Full source code (international ECL core + Nepal regulatory rule pack).
- Sample data: `sample_data/infinity_sample.xlsx` (120 anonymized Infinity loans) — safe to run immediately.
- User guide (Markdown + PDF): `docs/user-guide/ecl-guide.md` and `ecl-guide.pdf`.
- Release gates: `docs/regulatory/release-gates.md`.
- Tests: `tests/` (39 passing) — run with `pytest`.

### How to validate
1. Clone: `git clone https://github.com/subashnp169/senna-ecl-nepal.git`
2. Install: `pip install -r requirements.txt`
3. Run tests: `pytest` (expect 39 passed).
4. Run the system on the bundled sample:
   ```
   streamlit run apps/frontend/app.py
   ```
   Then in the browser: tick "Use bundled Infinity sample", click **Run ECL**.
5. To validate on real Infinity data: place the NRB 2.2 report (e.g.
   `NRB_2_2_REPORT_REVAMPED_000080__*.xlsx`) in `sample_data/` or upload via the UI
   ("Upload file"). The system auto-detects the Infinity format.
6. Review outputs in `output/reports/<run_id>/` (Excel/CSV/JSON) and the pipeline trace
   in the UI.

### Validation checklist for finance
- [ ] Source-to-report reconciliation (control totals match CBS).
- [ ] Staging logic matches institution policy (DPD backstops + qualitative triggers).
- [ ] PD/LGD/EAD parameters reviewed and approved.
- [ ] Scenario weights and macro overlays documented.
- [ ] Overlay (PMA) governance followed.
- [ ] Interest income recognition matches NRB 2025 guidance.
- [ ] Reports match NRB annex formats.
- [ ] Audit trail complete and reproducible.

### Access
This is a **private** repository. Contact the owner to be added as a collaborator.

## License

MIT. See `LICENSE`. Third-party attributions in `THIRD_PARTY_NOTICES.md`.
