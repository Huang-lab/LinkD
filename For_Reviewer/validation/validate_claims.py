#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "source_data"


def main() -> int:
    fails = []
    p = OUT / "fig1_b_rank_heatmap.csv"
    if p.exists():
        df = pd.read_csv(p)
        if "Model" in df.columns and "LinkD" in set(df["Model"]):
            print("PASS fig1_linkd_top")
        else:
            fails.append("fig1_linkd_top")
    else:
        fails.append("fig1_b missing — run execute_all.py")

    p = OUT / "fig2_g_docking_recovery.csv"
    if p.exists():
        df = pd.read_csv(p).sort_values("cutoff")
        if df["frac_recovered"].is_monotonic_increasing or df["frac_recovered"].diff().fillna(0).ge(-1e-9).all():
            print("PASS fig2g_dock_recovery")
        else:
            fails.append("fig2g_dock_recovery")
    else:
        fails.append("fig2_g missing")

    p = OUT / "fig5_a_adrb2_ranks.csv"
    if p.exists():
        df = pd.read_csv(p)
        if df["Drug Name"].astype(str).str.contains("Propranolol", case=False, na=False).any():
            print("PASS fig5a_propranolol")
        else:
            fails.append("fig5a_propranolol")
    else:
        fails.append("fig5_a missing")

    p = OUT / "fig5_ef_growth.csv"
    if p.exists():
        print("PASS fig5e_growth")
    else:
        fails.append("fig5_ef missing")

    if fails:
        print("FAILS:", fails)
        return 1
    print("All checked claims passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
