# Figure reproduction for reviewers

The **`For_Reviewer/`** package regenerates manuscript figure panels from packaged extracts.

## Layout

| Location | Contents |
|----------|----------|
| **GitHub** `For_Reviewer/` | Notebooks, helpers, small `source_data/` tables, illustrations, docs |
| **Zenodo** `For_Reviewer_large_data.zip` | Oversized CSVs that exceed GitHub’s 100 MB limit |

Large files (not in git):

- `known_drug_rank_crispr_cancer_driver_role.csv` (~166 MB)
- `docking_scores_fig2fg.csv` (~40 MB)

## Reviewer quick start

```bash
git clone https://github.com/Huang-lab/LinkD.git
cd LinkD/For_Reviewer
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-repro.txt

# Fetch oversized tables from Zenodo (skips if already present)
python setup/download_source_data.py

python execute_all.py
# optional: python validation/validate_claims.py
```

Or open individual notebooks under `notebooks/` after the download step.

No GPU is required. Individual-level EHR are never included — only aggregate statistics.

## Authors: publish the large zip

```bash
bash scripts/prepare_for_reviewer_zenodo.sh
# → zenodo_upload/For_Reviewer_large_data.zip
# Upload that file to Zenodo record 19241152 (new version), then confirm
# the URL in For_Reviewer/setup/download_source_data.py
```

This zip is **independent of the web server**. The app still uses `scripts/download_data.py` and the 15 main dataset zips only.

## Related docs

- [`For_Reviewer/README.md`](../For_Reviewer/README.md)
- [`For_Reviewer/DATA_AVAILABILITY.md`](../For_Reviewer/DATA_AVAILABILITY.md)
- [`For_Reviewer/REPRODUCIBILITY.md`](../For_Reviewer/REPRODUCIBILITY.md)
- Main dataset: [Zenodo DOI 10.5281/zenodo.19241152](https://doi.org/10.5281/zenodo.19241152)
