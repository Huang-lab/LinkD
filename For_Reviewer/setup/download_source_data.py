#!/usr/bin/env python3
"""Download oversized For_Reviewer source tables from Zenodo.

These two files exceed GitHub's 100 MB limit and are therefore NOT in git.
They are packaged as zenodo_upload/For_Reviewer_large_data.zip by
scripts/prepare_for_reviewer_zenodo.sh.

Usage (from For_Reviewer/ or repo root):
    python setup/download_source_data.py
    python For_Reviewer/setup/download_source_data.py

This does NOT affect the web server or scripts/download_data.py.
"""
from __future__ import annotations

import hashlib
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # For_Reviewer/
SRC = ROOT / "source_data"

# Zenodo v2 deposit (includes For_Reviewer_large_data.zip).
# DOI: https://doi.org/10.5281/zenodo.21615191
ZENODO_RECORD_ID = "21615191"
_BASE = f"https://zenodo.org/records/{ZENODO_RECORD_ID}/files"
ZENODO_LARGE_URL = f"{_BASE}/For_Reviewer_large_data.zip?download=1"

REQUIRED = [
    "known_drug_rank_crispr_cancer_driver_role.csv",
    "docking_scores_fig2fg.csv",
]


def sha256(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def all_present() -> bool:
    return all((SRC / name).exists() for name in REQUIRED)


def main() -> int:
    SRC.mkdir(parents=True, exist_ok=True)
    if all_present():
        print("All large For_Reviewer source files already present. Skipping download.")
        for name in REQUIRED:
            p = SRC / name
            print(f"  {name}: {p.stat().st_size / 1e6:.1f} MB")
        return 0

    print(f"Downloading For_Reviewer_large_data.zip from Zenodo record {ZENODO_RECORD_ID}...")
    print(f"  URL: {ZENODO_LARGE_URL}")
    dest = SRC / "For_Reviewer_large_data.zip"
    try:
        def report(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                pct = min(100, downloaded * 100 // total_size)
                sys.stdout.write(f"\r  {downloaded/1e6:.1f}/{total_size/1e6:.1f} MB ({pct}%)")
                sys.stdout.flush()

        urllib.request.urlretrieve(ZENODO_LARGE_URL, dest, reporthook=report)
        print()
    except Exception as e:
        print(f"\nDownload failed: {e}")
        print("If the file is not yet on Zenodo, run locally:")
        print("  bash scripts/prepare_for_reviewer_zenodo.sh")
        print("  # then upload zenodo_upload/For_Reviewer_large_data.zip")
        print("Or copy the two CSVs into For_Reviewer/source_data/ manually.")
        return 1

    print(f"Extracting into {SRC} ...")
    with zipfile.ZipFile(dest, "r") as zf:
        zf.extractall(SRC)
    dest.unlink(missing_ok=True)

    if not all_present():
        print("ERROR: extract finished but required files are still missing.")
        return 1

    # Optional: verify against manifest if present
    man = SRC / "manifest.csv"
    if man.exists():
        import csv
        wanted = {r["filename"]: r.get("sha256") for r in csv.DictReader(man.open())}
        for name in REQUIRED:
            expected = wanted.get(name)
            if expected:
                got = sha256(SRC / name)
                if got != expected:
                    print(f"WARN: sha256 mismatch for {name}")
                else:
                    print(f"OK checksum {name}")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
