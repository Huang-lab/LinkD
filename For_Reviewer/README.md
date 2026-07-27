# For_Reviewer — LinkD manuscript figure reproduction

Package for regenerating **Manuscript_VF** figure panels (Nature Cancer submission).

## Quick start (reviewers)

```bash
cd For_Reviewer
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-repro.txt

# Oversized tables are on Zenodo (not in git) — skips if already present
python setup/download_source_data.py

jupyter notebook notebooks/00_Setup_and_Data_Check.ipynb
# or
python execute_all.py
```

Outputs land in:

- `outputs/figures/` — PDF + PNG per panel
- `outputs/source_data/` — CSV of plotted values (Source Data style)

## What is in git vs Zenodo

| In GitHub | On Zenodo (`For_Reviewer_large_data.zip`) |
|-----------|-------------------------------------------|
| Notebooks, `linkd_repro/`, docs, illustrations | `known_drug_rank_crispr_cancer_driver_role.csv` (~166 MB) |
| Small/medium `source_data/` tables | `docking_scores_fig2fg.csv` (~40 MB) |

See [`docs/FOR_REVIEWER.md`](../docs/FOR_REVIEWER.md) for the full reviewer + author workflow.

## Design

| Rule | How it is enforced |
|------|--------------------|
| Data are inside this folder | Notebooks read only `source_data/` and `illustrations/` via `linkd_repro.paths` |
| Produce data + figures | Each computable panel writes CSV + PDF/PNG |
| Missing shareable data | Notebook section shows **process** (`PROCESS.md`) + **published illustration** |

## Notebooks

| Notebook | Panels |
|----------|--------|
| `00_Setup_and_Data_Check.ipynb` | Environment + manifest check |
| `Figure1_LinkD_Bind_Benchmark.ipynb` | 1a (illustrate), 1b, 1c |
| `Figure2_LinkD_Select.ipynb` | 2a–2g |
| `Figure3_LinkD_Pheno.ipynb` | 3a (illustrate), 3b–3h |
| `Figure4_EHR_Validation.ipynb` | 4a (illustrate), 4b |
| `Figure5_BetaBlocker_ADRB2.ipynb` | 5a, 5b–c (illustrate), 5d–k |
| `Figure6_LinkD_Agent.ipynb` | 6a–b (illustrate), 6c (from `source_data/benchmark/`) |
| `FigureS2_Bind_Quantitative.ipynb` | S2 |
| `FigureS3_S4_Tissue_Resolved.ipynb` | S3, S4 |
| `FigureS5_EHR_Volcano.ipynb` | S5 |

## Documentation

- [`DATA_AVAILABILITY.md`](DATA_AVAILABILITY.md) — copied inputs, sizes, origins
- [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) — panel → notebook → status
- [`MANUSCRIPT_MAP.md`](MANUSCRIPT_MAP.md) — caption ↔ regenerating section
- [`ENVIRONMENT.md`](ENVIRONMENT.md) — Python environment notes

## Authors only

- Rebuild panel extracts: `python setup/copy_and_extract_data.py`
- Publish large zip: `bash scripts/prepare_for_reviewer_zenodo.sh` → upload `zenodo_upload/For_Reviewer_large_data.zip`
