# Replication package: Directional Evidence on Workforce Reallocation in China's Manufacturing Digital Transformation

**Author:** Haibo Yi (易海博) — Shenzhen Technology University (深圳职业技术大学)

**Status:** Manuscript prepared for submission (Asian Economic Journal template).

## Abstract (short)

This paper provides directional evidence on how digital transformation reallocates
labor across sectors and skill levels in Chinese manufacturing. Using a
reallocation accounting framework applied to National Bureau of Statistics (NBS)
migrant-worker survey data and Ministry of Finance / Ministry of Industry and
Information Technology 101-city pilot data, the paper decomposes the 5.66 million
net increase in manufacturing employment into (i) pool growth, (ii) cross-sector
composition change, and (iii) within-industry skill upgrading. The generalized
directional index gamma = 0.586 (> 0.5) indicates that manufacturing digital
transformation is associated with a net *reallocation toward* manufacturing rather
than a mechanical job-destruction story. Skill upgrading contributes about 84% of
the quality-adjusted increment. An illustrative international panel (IACI x AUTO
interaction = 0.054, p = 0.0002) is reported as supporting evidence only, because
the underlying IACI index cannot be independently reproduced from fully public data.

## Repository contents

```
data/                  Publicly reproducible data (CSV/JSON)
  ept/                 OECD / Statizoid temporary-contract employment protection
                       strictness (EPT) series by country
  legacy_c_version/    Legacy "C-version" panel used in an earlier draft (see note)
code/                  Analysis scripts (Python 3)
docs/                  Audit and data-dictionary documentation
manuscript/            Latest manuscript (AEJ template) .tex + compiled .pdf,
                       including supplementary material
README.md              This file
```

## Reproducibility notes

- **Fully reproducible:** The Chinese domestic accounting decomposition
  (Sections 3-4), the NBS migrant-worker series, the 101-city pilot analysis,
  and the domestic data tables can be regenerated from the `.csv` files in
  `data/` using the scripts in `code/`.

- **Illustrative only:** The international panel regression (Table 6) and the
  IACI (Institutional Automation Capacity Index) are *illustrative*. The IACI
  index combines labor-market institutions and automation exposure; its
  construction depends on a mix of sources that cannot all be re-derived from
  fully public data. The published interaction coefficient (0.054, p = 0.0002)
  is therefore presented as supporting evidence, not as a causally identified
  estimate. See `docs/data_code_audit_20261115.md` and `docs/audit_remediation_20261115.md`.

- **Licensed data:** IFR World Robotics (VDMA) installation data used in part
  of the analysis are licensed and are NOT redistributed here. `data/ifr_*`
  and `data/owid_ifr_raw.csv` contain public aggregate series only. See the
  `Data Availability Statement` in the manuscript.

- **Legacy "C-version" data:** The files under `data/legacy_c_version/`
  (`iaciauto_panel.csv`, `ifr_rodensity.xlsx`, `oecd_epl.xlsx`, ...) were used
  in an earlier draft. An audit (see `docs/data_code_audit_20261115.md`)
  found that the C-version country panel is a synthetic linear-ramp series and
  that its real-country `UNEMP` column is entirely missing. These files are
  retained **only for audit transparency**; they must NOT be used as evidence
  in the paper.

## How to reproduce

```bash
# 1. Domestic accounting decomposition (Sections 3-4)
python code/audit_consistency.py

# 2. Real 2020-2024 country panel (illustrative, EPT-based)
python code/real_panel.py

# 3. L30 alternative panel (EPL-only IACI, 2020-2025)
python code/l30_alt_panel.py

# 4. L34 open IFR cross-validation (public installations vs Comtrade imports)
python code/l34_alt_ifr_open.py

# 5. Audit transparency: synthetic-series detection on the C version
python code/verify_synthetic.py
```

## License

Research code and data are provided for replication and review purposes.
Please cite the manuscript and contact the author for any reuse questions.
Licensed third-party data (e.g. IFR World Robotics) remain subject to their
own terms.

---

*Generated for the GitHub repository*
[`YI-HAIBO/workforce-reallocation-replication`](https://github.com/YI-HAIBO/workforce-reallocation-replication).
