#!/usr/bin/env python3
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "source_data"

PKGS = ["pandas", "numpy", "matplotlib", "scipy", "openpyxl", "pyarrow", "nbformat", "nbclient"]


def main() -> int:
    bad = []
    for p in PKGS:
        try:
            importlib.import_module(p)
            print(f"OK package {p}")
        except ImportError:
            print(f"MISSING package {p}")
            bad.append(p)
    required = [
        "TableS2_Benchmarking_LinkD.xlsx",
        "drug_selectivity_metrics.csv",
        "known_drug_rank_crispr_cancer_driver_role.csv",
        "docking_scores_fig2fg.csv",
        "manifest.csv",
    ]
    for r in required:
        ok = (SRC / r).exists()
        print(("OK" if ok else "MISSING"), "data", r)
        if not ok:
            bad.append(r)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
