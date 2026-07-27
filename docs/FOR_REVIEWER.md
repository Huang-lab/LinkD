# Figure reproduction for reviewers

*LinkD: An Agentic Platform for Drug Repurposing Unified across Molecular, Phenotypic, and Clinical Scales*

> **Required before Fig 2f–g / Fig 3:** run `python setup/download_source_data.py`
> (Zenodo [10.5281/zenodo.21615191](https://doi.org/10.5281/zenodo.21615191)).
> Without it, ~206 MB of panel CSVs are missing and those notebooks will fail.

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

Figure 6c (LinkD-Agent benchmark panel) uses the frozen summaries under
`For_Reviewer/source_data/benchmark/` (see notebook `Figure6_LinkD_Agent.ipynb`).

## Authors: publish the large zip

```bash
bash scripts/prepare_for_reviewer_zenodo.sh
# → zenodo_upload/For_Reviewer_large_data.zip
# Already published on Zenodo v2 (record 21615191 / DOI 10.5281/zenodo.21615191);
# download_source_data.py points at that record.
```

This zip is **independent of the web server**. The app still uses `scripts/download_data.py` and the 15 main dataset zips only.

## Related docs

- [`For_Reviewer/README.md`](../For_Reviewer/README.md)
- [`For_Reviewer/DATA_AVAILABILITY.md`](../For_Reviewer/DATA_AVAILABILITY.md)
- [`For_Reviewer/REPRODUCIBILITY.md`](../For_Reviewer/REPRODUCIBILITY.md)
- Main dataset: [Zenodo DOI 10.5281/zenodo.21615191](https://doi.org/10.5281/zenodo.21615191)
