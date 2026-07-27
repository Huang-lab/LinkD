#!/bin/bash
# Package oversized For_Reviewer source tables for Zenodo (GitHub cannot host >100 MB files).
# Run from project root: bash scripts/prepare_for_reviewer_zenodo.sh
#
# Output: zenodo_upload/For_Reviewer_large_data.zip
# Does NOT touch Database/ or the web server download path.

set -e
cd "$(dirname "$0")/.."

OUT="zenodo_upload"
SRC="For_Reviewer/source_data"
ZIP="$OUT/For_Reviewer_large_data.zip"

mkdir -p "$OUT"

FILES=(
  "$SRC/known_drug_rank_crispr_cancer_driver_role.csv"
  "$SRC/docking_scores_fig2fg.csv"
)

for f in "${FILES[@]}"; do
  if [ ! -f "$f" ]; then
    echo "MISSING: $f"
    echo "Run For_Reviewer/setup/copy_and_extract_data.py first if needed."
    exit 1
  fi
done

echo "Creating $ZIP ..."
rm -f "$ZIP"
zip -j "$ZIP" "${FILES[@]}"

ls -lh "$ZIP"
echo ""
echo "Next: upload $ZIP to Zenodo record 21615191 (new version),"
echo "then set the file URL in For_Reviewer/setup/download_source_data.py"
echo ""
echo "NOTE: This zip is for figure notebooks only — not used by the web server."
