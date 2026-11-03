# Third-party notices

This project adapts ideas and selected logic from the following open-source
projects. Licences are respected; production code is re-implemented and
validated rather than vendored verbatim.

| Project | Licence | Use |
|---|---|---|
| ShrishDhuria/IFRS9_ECL (github.com/ShrishDhuria/IFRS9_ECL) | MIT | PD term structures, SICR waterfall, macro overlays, Vasicek PIT-PD patterns (REFERENCE / selective ADAPT) |
| gbadedata/ifrs9-ecl-engine (github.com/gbadedata/ifrs9-ecl-engine) | MIT | End-to-end PD/LGD/EAD/staging/scenario pipeline structure (REFERENCE) |
| creditriskengine (PyPI, github.com/ankitjha67/baselkit) | Apache-2.0 | Governance overlay framework, revolving-credit ECL patterns, multi-jurisdiction floor design (REFERENCE) |
| naenumtou/ifrs9 (github.com/naenumtou/ifrs9) | not specified | Methodology reference only — no code imported |
| chetan-umbarje/IFRS9_ECL_Modeling | not specified | Methodology reference only — no code imported |
| Purity-Creatives/ifrs9-ecl-model-kenya | not specified | Kenya CBK-regulated ECL reference (methodology) |

Before any production use, follow the mandatory acceptance checks in
`docs/research/open-source-assessment.md`.
