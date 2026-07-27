# Figure reproduction for reviewers

The full **For Reviewer** notebook package (figure regeneration from packaged extracts) is **not** stored in this GitHub repository because several input tables exceed GitHub file-size limits (e.g. CRISPR concordance ~166 MB, docking extract ~40 MB).

## Where to get it

1. **Primary data products (LinkD predictions + aggregate EHR summaries):**  
   Zenodo DOI [10.5281/zenodo.19241152](https://doi.org/10.5281/zenodo.19241152)  
   https://zenodo.org/records/19241152

2. **Figure-panel package:** distributed to editors/reviewers as a companion archive (or updated Zenodo deposit) containing:
   - `notebooks/` — one notebook per main/supplementary figure
   - `source_data/` — panel-ready CSVs/XLSX (checksums in `manifest.csv`)
   - `linkd_repro/` — shared helpers
   - `requirements-repro.txt`, `environment.yml`
   - `README.md`, `DATA_AVAILABILITY.md`, `REPRODUCIBILITY.md`, `MANUSCRIPT_MAP.md`, `ENVIRONMENT.md`

Authors keep the complete tree locally under `For Reviewer/` (gitignored).

## Quick check (when you have the package)

```bash
cd "For Reviewer"
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-repro.txt
python execute_all.py
# optional: python validation/validate_claims.py
```

No GPU or network is required for packaged figure panels. Individual-level EHR are never included—only aggregate statistics.
