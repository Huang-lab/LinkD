# Author-only reviewer-data tools

These commands are intentionally outside `For_Reviewer/`; reviewers do not
need them.

To reconstruct the panel tables from the complete analysis checkout:

```bash
python scripts/reviewer_data/extract_figure_data.py \
  --source-root /path/to/Drug-Repo-scRNA \
  --legacy-root build/reviewer_legacy \
  --force
```

`reviewer_legacy` contains the three frozen historical extracts named by the
command's error messages. They are author inputs and are not distributed as
reviewer data. The extractor writes to `build/reviewer_source/`.

Build and validate the flattened, deterministic reviewer archive:

```bash
bash scripts/prepare_for_reviewer_zenodo.sh
python scripts/reviewer_data/validate_package.py
```

The packager takes newly extracted panel tables when present, combines them
with the licensed static assets and release metadata in
`build/reviewer_bundle/`, and writes the ZIP under `zenodo_upload/`. It also
writes a local SHA-256 companion for author-side verification; only the ZIP is
uploaded to Zenodo because the notebook verifies Zenodo's checksum and the
archive's internal SHA-256 manifest.
