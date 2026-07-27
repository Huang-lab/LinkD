#!/usr/bin/env python3
"""Validate the simplified reviewer payload, notebooks, and generated outputs."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
REVIEWER = REPO / "For_Reviewer"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import contracts  # noqa: E402

EXPECTED_OUTPUTS = [
    "fig1_b_rank_heatmap", "fig1_c_performance",
    "fig2_a_selectivity_landscape", "fig2_b_target_lollipop", "fig2_cd_recovery",
    "fig2_e_radar", "fig2_f_docking", "fig2_g_docking_recovery",
    "fig3_b_lineages", "fig3_c_canonical", "fig3_d_predicted_known", "fig3_e_breast",
    "fig3_f_recovery", "fig3_g_volcano", "fig3_h_network", "fig4_b_hierarchy",
    "fig5_a_adrb2_ranks", "fig5_d_receptor_heatmap", "fig5_ef_growth",
    "fig5_g_cohort_flow", "fig5_hi_cumulative_incidence", "fig5_j_seeded_cox",
    "fig5_k_subgroups", "figS2_benchmark", "figS3_tissue_affinity",
    "figS4_tissue_selectivity", "figS5_a_mount_sinai", "figS5_b_ukb",
    "figS5_c_azelastine", "figS5_d_tretinoin",
]

COMPUTATIONAL_COUNTS = {
    "Figure1.ipynb": 2, "Figure2.ipynb": 6, "Figure3.ipynb": 7,
    "Figure4.ipynb": 1, "Figure5.ipynb": 7, "FigureS2.ipynb": 1,
    "FigureS3.ipynb": 1, "FigureS4.ipynb": 1, "FigureS5.ipynb": 4,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print("PASS", message)


def read(data: Path, panel: str) -> pd.DataFrame:
    path = data / f"{panel}.csv"
    require(path.is_file() and path.stat().st_size > 0, f"{panel}.csv exists")
    return pd.read_csv(path)


def validate_data(data: Path) -> None:
    manifest_path = data / "manifest.json"
    require(manifest_path.is_file(), "data manifest exists")
    entries = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(
        {Path(entry["path"]).stem for entry in entries} == set(contracts.EXPECTED_PANEL_IDS),
        "manifest contains exactly the 27 required panel tables",
    )
    for entry in entries:
        path = data / entry["path"]
        require(path.is_file(), f"manifest file exists: {entry['path']}")
        require(path.stat().st_size == entry["bytes"], f"byte size matches: {entry['path']}")
        require(sha256(path) == entry["sha256"], f"checksum matches: {entry['path']}")
        frame = pd.read_csv(path)
        require(len(frame) == entry["rows"], f"row count matches: {entry['path']}")
        require(list(frame.columns) == entry["columns"], f"schema matches: {entry['path']}")

    rank = read(data, "fig1b")
    require(rank["method"].nunique() == 13, "Figure 1 has 13 methods")
    require(set(rank.query("method == 'LinkD-Bind'")["rank"]) == {1}, "LinkD-Bind ranks first")
    radar = read(data, "fig2e")
    require(set(radar["gene"]) == {"EGFR", "JAK1"}, "Figure 2 contains EGFR and JAK1")
    docking = read(data, "fig2g")
    for cutoff, expected in contracts.DOCKING_RECOVERY.items():
        got = float(docking.iloc[(docking["cutoff"] - cutoff).abs().argmin()]["percent_recovered"])
        require(math.isclose(got, expected, abs_tol=0.11), f"Figure 2 recovery at {cutoff:g}")
    heat = read(data, "fig5d")
    require(heat["receptor"].nunique() == 9, "Figure 5 has nine adrenergic receptors")
    require(int(read(data, "fig5a").query("drug_name == 'Carvedilol'")["rank"].iloc[0]) == 3, "Carvedilol is rank 3")


def notebook_code(path: Path) -> str:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    return "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code"
    )


def validate_notebooks() -> None:
    expected = set(contracts.FIGURE_NOTEBOOKS.values())
    found = {path.name for path in (REVIEWER / "notebooks").glob("*.ipynb")}
    require(found == expected, "notebook inventory is Data Preparation plus Figure 1–6 and S1–S6")
    for name in sorted(found):
        code = notebook_code(REVIEWER / "notebooks" / name)
        require(
            all(token not in code for token in ("linkd_repro", "panel_workflows", "notebook_ui", "panels.render(")),
            f"{name} has no repository-owned imports",
        )
        require("Data_Preparation.ipynb" in code or name == "Data_Preparation.ipynb", f"{name} names the recovery notebook")
        require(
            '"notebooks" / "Data_Preparation.ipynb"' in code,
            f"{name} locates For_Reviewer unambiguously",
        )
        count = COMPUTATIONAL_COUNTS.get(name, 0)
        if count:
            require(code.count("pd.read_csv(") >= count, f"{name} directly loads its panel tables")
            require(code.count("assert ") >= count, f"{name} exposes manuscript assertions")
            require(code.count("plt.subplots(") >= count, f"{name} contains Matplotlib construction")
            require(code.count(".savefig(") == 2 * count, f"{name} exports PDF and PNG")
            require(code.count(".to_csv(") == count, f"{name} exports plotted CSV data")


def validate_outputs(output: Path) -> None:
    for stem in EXPECTED_OUTPUTS:
        for folder, suffix in (("figures", ".pdf"), ("figures", ".png"), ("source_data", ".csv")):
            path = output / folder / f"{stem}{suffix}"
            require(path.is_file() and path.stat().st_size > 0, f"output exists: {path.relative_to(output)}")
    require(not (output / "figures" / "fig6_c_benchmark.pdf").exists(), "Figure 6c remains excluded")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=REVIEWER / "data")
    parser.add_argument("--output-dir", type=Path, default=REVIEWER / "outputs")
    parser.add_argument("--skip-data", action="store_true")
    parser.add_argument("--skip-outputs", action="store_true")
    args = parser.parse_args()
    if not args.skip_data:
        validate_data(args.data_dir.resolve())
    validate_notebooks()
    if not args.skip_outputs:
        validate_outputs(args.output_dir.resolve())
    print("All notebook-first reviewer-package checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
