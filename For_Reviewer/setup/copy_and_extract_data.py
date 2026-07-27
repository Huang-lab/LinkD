#!/usr/bin/env python3
"""Copy / extract all panel inputs into For Reviewer/source_data/.

Run once on the author machine. After this, notebooks must not read outside
For Reviewer/.
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]  # For Reviewer/
LINKD = ROOT.parent
DRS = Path("/Users/cheng.wang/Documents/Drug-Repo-scRNA")
SRC = ROOT / "source_data"
ILL = ROOT / "illustrations"

COPY_JOBS = [
    # (dest_rel, source_path, panels)
    ("TableS2_Benchmarking_LinkD.xlsx", LINKD / "docs/Figures_Tables/TableS2_Benchmarking_LinkD.xlsx", "1b,1c,S2"),
    ("TableS3_Mount_Sinai_Drug_Cancer.csv", LINKD / "docs/Figures_Tables/TableS3_Mount_Sinai_Drug_Cancer.csv", "4b,S5"),
    ("TableS4_UK_Biobank_Drug_Disease.csv", LINKD / "docs/Figures_Tables/TableS4_UK_Biobank_Drug_Disease.csv", "4b,S5"),
    ("Ensemble_result_concat_regression.csv", DRS / "Figures_Generation/1_BindingPrediction/Ensemble_result_concat_regression.csv", "1b,1c,S2"),
    ("drug_selectivity_metrics.csv", LINKD / "DrugTargetMetrics/drug_selectivity_metrics.csv", "2a,5a"),
    ("target_binding_stats.csv", LINKD / "DrugTargetMetrics/target_binding_stats.csv", "2b"),
    ("drug_umap_clustering.csv", LINKD / "DrugTargetMetrics/drug_umap_clustering.csv", "2a"),
    ("onco_genes.csv", LINKD / "Database/onco_genes.csv", "2b"),
    ("opentarget_known_drug_pair.csv", DRS / "DrugChemBL/opentarget_known_drug_pair.csv", "2c,2d,2e"),
    ("good_drug_ehr_scatter_1110.csv", DRS / "DrugChemBL/good_drug_ehr_scatter_1110.csv", "S5"),
    ("ukb_drug_ehr_scatter_1110.csv", DRS / "DrugChemBL/ukb_drug_ehr_scatter_1110.csv", "S5"),
    ("Propranolol_growth.csv", DRS / "Figures_Generation/Figure5/Propranolol_growth.csv", "5e"),
    ("Carvedilol_growth.csv", DRS / "Figures_Generation/Figure5/Carvedilol_growth.csv", "5f"),
    ("matched_cells.csv", DRS / "DrugCellLine/matched_cells.csv", "3b"),
    ("known_drug_rank_crispr_cancer_driver_role.csv", DRS / "DrugChemBL/known_drug_rank_crispr_cancer_driver_role.csv", "3c-h,S3,S4"),
    ("drug_phase_mapping.csv", LINKD / "DrugTargetMetrics/drug_phase_mapping.csv", "2a"),
]

VCT_TABLES = [
    "results_HR.csv",
    "results_incidence.csv",
    "results_subgroup.csv",
    "descriptive_stats.csv",
    "results_OR.csv",
    "results_seeded_aggregates.csv",
]

ILLUSTRATION_JOBS = [
    ("fig1_a", LINKD / "docs/Figures_Tables/Figure1.jpg"),
    ("fig3_a", LINKD / "docs/Figures_Tables/Figure3.jpg"),
    ("fig4_a", LINKD / "docs/Figures_Tables/Figure4.jpg"),
    ("fig5_b", LINKD / "docs/Figures_Tables/Figure5.jpg"),
    ("fig5_c", LINKD / "docs/Figures_Tables/Figure5.jpg"),
    ("fig6_a", LINKD / "docs/Figures_Tables/Figure6.jpg"),
    ("fig6_b", LINKD / "docs/Figures_Tables/Figure6.jpg"),
    ("figS1", LINKD / "docs/Figures_Tables/FigureS1.jpg"),
    ("figS6_a", LINKD / "docs/Figures_Tables/FigureS6.jpg"),
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


def copy_file(src: Path, dest: Path) -> dict | None:
    if not src.exists():
        print(f"  MISSING: {src}")
        return None
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return {
        "filename": str(dest.relative_to(SRC)),
        "origin": str(src),
        "bytes": dest.stat().st_size,
        "sha256": sha256(dest),
    }


def extract_docking_subset() -> dict | None:
    """Extract Fig 2f/2g columns from the 18 GB docking CSV (streaming)."""
    src = DRS / "MultiOmicsLLM2024/RareDisease/top_gene_dock.csv"
    dest = SRC / "docking_scores_fig2fg.csv"
    if dest.exists() and dest.stat().st_size > 1000:
        print(f"  SKIP extract (exists): {dest.name}")
        return {
            "filename": dest.name,
            "origin": str(src) + " [extracted]",
            "bytes": dest.stat().st_size,
            "sha256": sha256(dest),
            "panels": "2f,2g",
        }
    if not src.exists():
        print(f"  MISSING docking source: {src}")
        return None

    print(f"  Extracting docking subset from {src} (streaming)...")
    usecols = [
        "Docking Score",
        "Gene",
        "Gene Name",
        "Drug Chembl ID",
        "Drug Name_x",
        "Drug Name_y",
        "Type",
        "Selectivity_Score",
        "Rank_Select",
        "Entry Name",
        "Target_Affinity",
        "aff_n",
    ]
    # Sample every Nth row after keeping role-annotated oncology targets if Type present
    chunks = []
    n_kept = 0
    max_rows = 500_000  # enough for raincloud + recovery curve
    for chunk in pd.read_csv(src, usecols=lambda c: c in usecols, chunksize=200_000):
        # Prefer rows with a docking score
        if "Docking Score" in chunk.columns:
            chunk = chunk.dropna(subset=["Docking Score"])
        if chunk.empty:
            continue
        # Downsample large chunks
        if len(chunk) > 20_000:
            chunk = chunk.sample(n=20_000, random_state=42)
        chunks.append(chunk)
        n_kept += len(chunk)
        print(f"    kept {n_kept:,} rows...")
        if n_kept >= max_rows:
            break
    if not chunks:
        print("  WARN: no docking rows extracted")
        return None
    out = pd.concat(chunks, ignore_index=True)
    if len(out) > max_rows:
        out = out.sample(n=max_rows, random_state=42)
    out.to_csv(dest, index=False)
    print(f"  Wrote {dest.name}: {len(out):,} rows, {dest.stat().st_size/1e6:.1f} MB")
    return {
        "filename": dest.name,
        "origin": str(src) + " [extracted subset]",
        "bytes": dest.stat().st_size,
        "sha256": sha256(dest),
        "panels": "2f,2g",
    }


def extract_selectivity_slices() -> list[dict]:
    """Build panel-ready slices from parquet / CSVs without shipping 13 GB."""
    rows = []
    sel = SRC / "drug_selectivity_metrics.csv"
    known = SRC / "opentarget_known_drug_pair.csv"
    parquet_dir = LINKD / "DrugTargetMetrics/target_centric_pan"

    # Fig 5a/5d: ADRB family ranks from parquet (scan for ADRB*/ADRA*)
    dest_adr = SRC / "adrenergic_selectivity_fig5.csv"
    if dest_adr.exists():
        print(f"  SKIP adrenergic slice (exists)")
    elif parquet_dir.exists():
        print("  Extracting ADRB/ADRA selectivity from parquet chunks...")
        genes = {
            "ADRB1", "ADRB2", "ADRB3",
            "ADRA1A", "ADRA1B", "ADRA1D",
            "ADRA2A", "ADRA2B", "ADRA2C",
        }
        parts = []
        for pq in sorted(parquet_dir.glob("*.parquet")):
            try:
                import pyarrow.parquet as pq_mod
                t = pq_mod.read_table(
                    pq,
                    columns=["Drug", "Target", "Selectivity_Score", "Rank_Select", "aff_local", "aff_local_n"],
                )
                df = t.to_pandas()
            except Exception as e:
                print(f"    skip {pq.name}: {e}")
                continue
            # Target may be UniProt entry name; also try Gene-like strings
            m = df[df["Target"].astype(str).str.upper().isin(genes) |
                   df["Target"].astype(str).str.contains("ADRB|ADRA", case=False, na=False)]
            if not m.empty:
                parts.append(m)
                print(f"    {pq.name}: +{len(m)} rows")
        if parts:
            out = pd.concat(parts, ignore_index=True)
            out.to_csv(dest_adr, index=False)
            print(f"  Wrote {dest_adr.name}: {len(out):,} rows")
            rows.append({
                "filename": dest_adr.name,
                "origin": str(parquet_dir) + " [extracted ADR*]",
                "bytes": dest_adr.stat().st_size,
                "sha256": sha256(dest_adr),
                "panels": "5a,5d",
            })
        else:
            print("  WARN: no ADR* rows found in parquet; Fig 5a/5d will use drug_selectivity_metrics only")
    else:
        print(f"  MISSING parquet dir: {parquet_dir}")

    # Fig 2e radar helper: top drugs for EGFR / JAK1 from known pairs + selectivity
    dest_radar = SRC / "radar_egfr_jak1_fig2e.csv"
    if dest_radar.exists():
        print("  SKIP radar slice (exists)")
    elif sel.exists() and known.exists() and parquet_dir.exists():
        print("  Extracting EGFR/JAK1 radar candidates from parquet...")
        targets = {"EGFR", "JAK1", "EGFR_HUMAN", "JAK1_HUMAN"}
        parts = []
        for pq in sorted(parquet_dir.glob("*.parquet"))[:30]:  # limit scan
            try:
                import pyarrow.parquet as pq_mod
                t = pq_mod.read_table(
                    pq,
                    columns=[
                        "Drug", "Target", "Selectivity_Score", "Rank_Select",
                        "aff_local", "aff_local_n", "entropy_sel_n", "gap_local_n", "sr_local_n",
                    ],
                )
                df = t.to_pandas()
            except Exception as e:
                continue
            m = df[df["Target"].astype(str).str.upper().str.contains("EGFR|JAK1", na=False)]
            if not m.empty:
                parts.append(m)
        if parts:
            out = pd.concat(parts, ignore_index=True)
            # Keep top 200 per target by Selectivity_Score
            out = (
                out.sort_values("Selectivity_Score", ascending=False)
                .groupby(out["Target"].astype(str).str.upper().str.extract(r"(EGFR|JAK1)")[0])
                .head(200)
            )
            out.to_csv(dest_radar, index=False)
            print(f"  Wrote {dest_radar.name}: {len(out):,} rows")
            rows.append({
                "filename": dest_radar.name,
                "origin": str(parquet_dir) + " [extracted EGFR/JAK1]",
                "bytes": dest_radar.stat().st_size,
                "sha256": sha256(dest_radar),
                "panels": "2e",
            })
    return rows


def copy_benchmark() -> list[dict]:
    bdir = LINKD / "benchmark/results"
    dest_dir = SRC / "benchmark"
    dest_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    patterns = ["summary*.jsonl", "predictions*.jsonl", "leaderboard.csv", "PERFORMANCE_REPORT.md"]
    for pat in patterns:
        for src in bdir.glob(pat):
            dest = dest_dir / src.name
            info = copy_file(src, dest)
            if info:
                info["panels"] = "6c"
                rows.append(info)
                print(f"  OK {info['filename']}")
    # also copy fig6 published numbers if present
    fig_dir = bdir / "figures"
    if fig_dir.exists():
        for name in ["fig6_benchmark_heatmap.pdf", "fig6_benchmark_bars.pdf",
                     "fig6_benchmark_heatmap.png", "fig6_benchmark_bars.png"]:
            src = fig_dir / name
            if src.exists():
                info = copy_file(src, dest_dir / name)
                if info:
                    info["panels"] = "6c"
                    rows.append(info)
    return rows


def copy_vct() -> list[dict]:
    rows = []
    for drug in ("propranolol", "carvedilol"):
        tdir = DRS / f"AI-Agent-VCT/figures_and_tables/{drug}/tables"
        if not tdir.exists():
            print(f"  MISSING VCT tables: {tdir}")
            continue
        dest_dir = SRC / "vct" / drug
        dest_dir.mkdir(parents=True, exist_ok=True)
        for name in VCT_TABLES:
            src = tdir / name
            info = copy_file(src, dest_dir / name)
            if info:
                info["panels"] = "5g-k"
                rows.append(info)
                print(f"  OK vct/{drug}/{name}")
        summary = tdir.parent / "SUMMARY.md"
        if summary.exists():
            info = copy_file(summary, dest_dir / "SUMMARY.md")
            if info:
                info["panels"] = "5g-k"
                rows.append(info)
    return rows


def copy_illustrations() -> None:
    for panel_id, src in ILLUSTRATION_JOBS:
        dest_dir = ILL / panel_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        if src.exists():
            dest = dest_dir / src.name
            shutil.copy2(src, dest)
            print(f"  ILL {panel_id}: {src.name}")
        else:
            print(f"  MISSING illustration for {panel_id}: {src}")


def main() -> int:
    SRC.mkdir(parents=True, exist_ok=True)
    ILL.mkdir(parents=True, exist_ok=True)
    manifest = []

    print("=== Copy small/medium tables ===")
    for dest_rel, src, panels in COPY_JOBS:
        info = copy_file(src, SRC / dest_rel)
        if info:
            info["panels"] = panels
            manifest.append(info)
            print(f"  OK {dest_rel} ({info['bytes']/1e6:.1f} MB)")

    print("=== Copy VCT summary tables ===")
    manifest.extend(copy_vct())

    print("=== Copy benchmark results ===")
    manifest.extend(copy_benchmark())

    print("=== Extract docking subset ===")
    info = extract_docking_subset()
    if info:
        if "panels" not in info:
            info["panels"] = "2f,2g"
        manifest.append(info)

    print("=== Extract selectivity / ADR / radar slices ===")
    manifest.extend(extract_selectivity_slices())

    print("=== Copy illustrations ===")
    copy_illustrations()

    man = pd.DataFrame(manifest)
    if not man.empty:
        man.to_csv(SRC / "manifest.csv", index=False)
        print(f"\nManifest: {len(man)} files, {man['bytes'].sum()/1e6:.1f} MB total")
    else:
        print("WARN: empty manifest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
