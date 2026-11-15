# GitHub replication upload — 2026-11-15

## Repository

- **Repo:** [`YI-HAIBO/workforce-reallocation-replication`](https://github.com/YI-HAIBO/workforce-reallocation-replication)
- **Clone:** `https://github.com/YI-HAIBO/workforce-reallocation-replication.git`
- **Owner:** `YI-HAIBO` (Haibo Yi, Shenzhen Technology University)
- **Visibility:** public
- **Default branch:** `main`
- **Description:** *Replication data and code for: Directional Evidence on Workforce Reallocation in China's Manufacturing Digital Transformation*

## What was uploaded

| Top-level | Contents | Count |
|---|---|---|
| `data/` | Publicly reproducible CSV/JSON + `ept/` + `legacy_c_version/` | 37 |
| `code/` | Analysis scripts (Python 3) | 26 |
| `docs/` | Audit, remediation, data-dictionary documentation | 3 |
| `manuscript/` | AEJ main `.tex`/`.pdf` + supplementary `.tex`/`.pdf` | 4 |
| root | `README.md`, `.gitignore` | 2 |
| **Total** | | **73** |

- **Total bytes:** 1,836,039
- **Uploaded via:** GitHub Contents API (`PUT /repos/{owner}/{repo}/contents/{path}`, base64, branch `main`)
- **Credential:** GitHub PAT retrieved from the WorkBuddy library document `论文投稿相关信息`; token never written to disk in plaintext beyond the scratch file and never printed.

## Verification (after upload)

- API tree (`git/trees/main?recursive=1`): **73 blobs**, 1,836,039 bytes — matches local upload directory.
- Contents API decoded size == GitHub stored `size` for sampled key files (README.md, .gitignore, `code/real_panel.py`, `data/epl_panel_11.csv`, `manuscript/manuscript_AEJ.tex`, `docs/data_code_audit_20261115.md`, `data/legacy_c_version/iaciauto_panel.csv`).
- Repository page publicly reachable; README renders correctly (confirmed via public fetch).
- GitHub-hosted `manuscript_AEJ.tex` contains `https://github.com/YI-HAIBO/workforce-reallocation-replication`; no `gitee.com` remains.

## Manuscript update (Data Availability URL)

- Replaced `https://gitee.com/franksztyfy/paper-data-code-audit` with the GitHub repository URL in:
  - `manuscript_AEJ.tex` (main `\section*{Data Availability Statement}`)
  - `Cover_Letter_AEJ.txt` (DATA AND CODE AVAILABILITY paragraph)
  - both in the working tree and in `2026-11-15_AEJ_Submission/`
- After the change:
  - **Word count:** MAIN 7822 / REFS 1752 / TOTAL **9574** (AEJ cap 9600) — unchanged, still compliant.
  - **Recompile:** `manuscript_AEJ.tex` → 37 pages, 0 errors, 0 undefined refs/citations; `supplementary_AEJ.tex` → 5 pages, 0 errors, 0 undefined.
  - Submission folder re-synced and re-compiled successfully (both PDFs regenerate).

## Transparency notes captured in `README.md`

- Domestic accounting decomposition (Sections 3–4) fully reproducible.
- International panel / IACI reported as **illustrative**; interaction 0.054 (p = 0.0002) is supporting, not causal.
- IFR World Robotics (VDMA) data are **licensed**, not redistributed; only public aggregate series included.
- `data/legacy_c_version/` retained **only for audit transparency** (synthetic C-version panel); must not be used as evidence.

## Safety

- Sensitive scratch files (`_subinfo.txt` with the PAT, `_instabox.txt` with an unrelated API key) were **not** uploaded; `.gitignore` excludes `*token*`, `*secret*`, `*key*`, `.env`, etc. A pre-upload scan of the upload directory found **0** credential hits.
