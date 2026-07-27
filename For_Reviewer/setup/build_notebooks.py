#!/usr/bin/env python3
"""Generate For Reviewer figure notebooks (one figure per notebook, one section per panel)."""
from __future__ import annotations

import json
from pathlib import Path

NB_DIR = Path(__file__).resolve().parents[1] / "notebooks"


def cell_md(src: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": src.splitlines(keepends=True)}


def cell_code(src: str) -> dict:
    return {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": src.splitlines(keepends=True),
    }


def notebook(cells: list[dict]) -> dict:
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "cells": cells,
    }


SETUP = r'''
import sys
from pathlib import Path
ROOT = Path.cwd()
if ROOT.name == "notebooks":
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Markdown

from linkd_repro import paths, style, io, illustrate
style.apply()
paths.ensure_output_dirs()
print("For Reviewer root:", paths.ROOT)
print("source_data OK:", paths.SOURCE.exists())
'''.strip()


DATA_HEADER = """
## Data availability

All inputs for this notebook are **copied into** `For Reviewer/source_data/` (or shown from `illustrations/` when a panel cannot be recomputed).

- No Zenodo download is required.
- No paths outside `For Reviewer/` are used after packaging.
- See `DATA_AVAILABILITY.md` and `source_data/manifest.csv` for origins and checksums.

**Files used below** are listed in each panel section.
""".strip()


def write(name: str, cells: list[dict]) -> None:
    p = NB_DIR / name
    p.write_text(json.dumps(notebook(cells), indent=1))
    print("wrote", p.name)


def nb_setup():
    cells = [
        cell_md("# 00 — Setup and data check\n\nValidate the self-contained `For Reviewer/` package before regenerating figures."),
        cell_md(DATA_HEADER),
        cell_code(SETUP),
        cell_code(r'''
import pandas as pd
man = pd.read_csv(paths.SOURCE / "manifest.csv")
display(Markdown(f"**Manifest:** {len(man)} files, {man['bytes'].sum()/1e6:.1f} MB"))
display(man[["filename","bytes","panels"]].head(40))

required = [
    "TableS2_Benchmarking_LinkD.xlsx",
    "drug_selectivity_metrics.csv",
    "known_drug_rank_crispr_cancer_driver_role.csv",
    "docking_scores_fig2fg.csv",
    "Propranolol_growth.csv",
    "vct/propranolol/results_HR.csv",
    "adrenergic_selectivity_fig5.csv",
]
rows = []
for r in required:
    p = paths.SOURCE / r
    rows.append({"file": r, "present": p.exists(), "MB": round(p.stat().st_size/1e6, 2) if p.exists() else None})
ready = pd.DataFrame(rows)
display(ready)
assert ready["present"].all(), "Missing required source files — re-run setup/copy_and_extract_data.py"
print("All required files present.")
'''),
    ]
    write("00_Setup_and_Data_Check.ipynb", cells)


def nb_fig1():
    cells = [
        cell_md("""# Figure 1 — LinkD-Bind framework and affinity benchmarking

**Caption (abridged):** The LinkD framework integrates proteome-wide affinity prediction, selectivity scoring, phenotypic validation, and clinical evidence. LinkD-Bind outperforms established drug-target affinity predictors on BindingDB, Davis, and KIBA under random, cold-drug, and cold-protein splits.
"""),
        cell_md(DATA_HEADER + "\n\n- `source_data/TableS2_Benchmarking_LinkD.xlsx`\n- `source_data/Ensemble_result_concat_regression.csv`"),
        cell_code(SETUP),
        cell_md("## Panel a — Framework schematic\n*Not regenerated from tabular data.*"),
        cell_code("illustrate.show_panel('fig1_a', title='Panel a')"),
        cell_md("## Panel b — Rank heatmap across models and splits\nEach cell is the rank of a model in a split (1 = best). Built from TableS2 test-set Pearson correlations."),
        cell_code(r'''
df = io.read_table_s2()
test = df[df["Dataset"] == "Test"].copy()
# Average Pearson across BindDB/Davis/Kiba within each Mode; then rank models (higher Pearson = better = rank 1)
pivot = test.pivot_table(index="Model", columns="Mode", values="Pearson", aggfunc="mean")
# Keep models with all three modes when possible; drop pure-missing
pivot = pivot.dropna(how="all")
ranks = pivot.rank(ascending=False, method="min")
# Manuscript cites ~13 models; keep models present in random split
keep = ranks.dropna(subset=["random"]).index.tolist()
ranks = ranks.loc[keep]
# Order models by mean rank
order = ranks.mean(axis=1).sort_values().index
ranks = ranks.loc[order]

fig, ax = plt.subplots(figsize=(4.2, 5.2))
im = ax.imshow(ranks.values, cmap="viridis_r", aspect="auto", vmin=1, vmax=max(13, ranks.max().max()))
ax.set_xticks(range(len(ranks.columns)))
ax.set_xticklabels(ranks.columns, rotation=30, ha="right")
ax.set_yticks(range(len(ranks.index)))
ax.set_yticklabels(ranks.index)
ax.set_title("Fig 1b — mean Pearson rank (1=best)")
cbar = fig.colorbar(im, ax=ax, fraction=0.046)
cbar.set_label("Rank")
for i in range(ranks.shape[0]):
    for j in range(ranks.shape[1]):
        v = ranks.values[i, j]
        if np.isfinite(v):
            ax.text(j, i, f"{int(v)}", ha="center", va="center", color="white" if v > ranks.values.max()/2 else "black", fontsize=6)
fig.tight_layout()
out = style.save_panel(fig, "fig1_b_rank_heatmap", ranks.reset_index())
plt.show()
print(out)
# Claim: LinkD should be among top ranks
if "LinkD" in ranks.index:
    print("LinkD ranks:", ranks.loc["LinkD"].to_dict())
'''),
        cell_md("## Panel c — Mean test Pearson: LinkD vs ablations and deep baselines"),
        cell_code(r'''
df = io.read_table_s2()
test = df[df["Dataset"] == "Test"].copy()
focus = ["LinkD", "Diffusion", "MLP", "DeepDTA", "DeepPurpose", "GraphDTA"]
sub = test[test["Model"].isin(focus)]
mean_r = sub.groupby(["Model", "Mode"])["Pearson"].mean().reset_index()
wide = mean_r.pivot(index="Mode", columns="Model", values="Pearson")
# order modes
mode_order = [m for m in ["random", "cold_protein", "cold_drug"] if m in wide.index]
wide = wide.loc[mode_order]

fig, ax = plt.subplots(figsize=(5.5, 3.2))
x = np.arange(len(wide.index))
for model in [m for m in focus if m in wide.columns]:
    ax.plot(x, wide[model].values, marker="o", label=model, linewidth=1.2, markersize=4)
ax.set_xticks(x)
ax.set_xticklabels(wide.index)
ax.set_ylabel("Mean test Pearson r")
ax.set_title("Fig 1c — LinkD vs ablations / deep baselines")
ax.legend(frameon=False, ncol=2)
fig.tight_layout()
out = style.save_panel(fig, "fig1_c_ablation_lines", wide.reset_index())
plt.show()
print(out)
'''),
    ]
    write("Figure1_LinkD_Bind_Benchmark.ipynb", cells)


def nb_figs2():
    cells = [
        cell_md("# Figure S2 — Quantitative LinkD-Bind benchmarking\n\nRMSE and Pearson for representative methods across datasets and splits."),
        cell_md(DATA_HEADER + "\n\n- `source_data/TableS2_Benchmarking_LinkD.xlsx`"),
        cell_code(SETUP),
        cell_md("## Panels — RMSE and Pearson grids"),
        cell_code(r'''
df = io.read_table_s2()
test = df[df["Dataset"] == "Test"].copy()
methods = ["LinkD", "Diffusion", "DeepDTA", "DeepPurpose", "GraphDTA"]
test = test[test["Model"].isin(methods)]
metrics = ["RMSE", "Pearson"]
modes = ["random", "cold_protein", "cold_drug"]
datasets = ["BindDB", "Davis", "Kiba"]

fig, axes = plt.subplots(2, 3, figsize=(9, 5.5), sharey=False)
for col, mode in enumerate(modes):
    for row, metric in enumerate(metrics):
        ax = axes[row, col]
        sub = test[test["Mode"] == mode]
        piv = sub.pivot_table(index="Model", columns="Data", values=metric, aggfunc="mean")
        piv = piv.reindex(methods)
        piv = piv[[d for d in datasets if d in piv.columns]]
        piv.plot(kind="bar", ax=ax, width=0.8, legend=(row==0 and col==2))
        ax.set_title(f"{metric} | {mode}")
        ax.set_xlabel("")
        ax.tick_params(axis="x", rotation=45)
        if col == 2 and row == 0:
            ax.legend(frameon=False, fontsize=6, title="Dataset")
fig.suptitle("Fig S2 — test-set RMSE / Pearson", y=1.02)
fig.tight_layout()
out = style.save_panel(fig, "figS2_rmse_pearson", test)
plt.show()
print(out)
'''),
    ]
    write("FigureS2_Bind_Quantitative.ipynb", cells)


def nb_fig2():
    cells = [
        cell_md("# Figure 2 — LinkD-Select drug selectivity\n\nProteome-wide selectivity, oncogene enrichment, known-DTI recovery, radar profiles, and docking validation."),
        cell_md(DATA_HEADER + """

- `drug_selectivity_metrics.csv`, `target_binding_stats.csv`, `onco_genes.csv`
- `opentarget_known_drug_pair.csv`, `radar_egfr_jak1_fig2e.csv`
- `docking_scores_fig2fg.csv` (extracted subset)
"""),
        cell_code(SETUP),
        cell_md("## Panel a — Affinity vs entropy scatter (14,981 drugs)"),
        cell_code(r'''
sel = io.read_selectivity()
# Prefer normalized columns when present
xcol = "aff_n" if "aff_n" in sel.columns else "Selectivity_Score"
ycol = "entropy_sel_n" if "entropy_sel_n" in sel.columns else "entropy_norm"
fig, ax = plt.subplots(figsize=(4.5, 3.8))
sc = ax.scatter(sel[xcol], sel[ycol], c=sel["Selectivity_Score"], s=3, cmap="viridis", alpha=0.35, linewidths=0)
ax.set_xlabel(xcol)
ax.set_ylabel(ycol)
ax.set_title("Fig 2a — affinity vs entropy (colored by Selectivity_Score)")
fig.colorbar(sc, ax=ax, label="Selectivity_Score", fraction=0.046)
fig.tight_layout()
out = style.save_panel(fig, "fig2_a_scatter", sel[[xcol, ycol, "Selectivity_Score", "Drug Chembl ID"]].dropna())
plt.show()
print(out)
'''),
        cell_md("## Panel b — Median selectivity by cancer gene role (lollipop)"),
        cell_code(r'''
def bh_fdr(pvals):
    p = np.asarray(pvals, dtype=float)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order]
    q = ranked * n / (np.arange(1, n + 1))
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(n)
    out[order] = np.clip(q, 0, 1)
    return out

tbs = io.read_target_stats()
onco = io.read_onco_genes()
# Merge role
if "Role" not in tbs.columns or tbs["Role"].isna().all():
    tbs = tbs.merge(onco, left_on="Gene", right_on="Gene", how="left", suffixes=("", "_onco"))
    if "Role_onco" in tbs.columns:
        tbs["Role"] = tbs["Role"].fillna(tbs["Role_onco"])
score = "Avg_Selectivity_Score" if "Avg_Selectivity_Score" in tbs.columns else "Selectivity_Score"
bg = tbs[score].dropna()
# Keep cancer-relevant annotated genes
sub = tbs[tbs["Role"].isin(["oncogene", "TSG", "both", "Oncogene", "Tumor Suppressor", "Dual"])].copy()
# Normalize role labels
role_map = {"Oncogene": "oncogene", "Tumor Suppressor": "TSG", "Dual": "both", "both": "both", "oncogene": "oncogene", "TSG": "TSG"}
sub["Role"] = sub["Role"].map(lambda x: role_map.get(x, x))
pvals = []
for _, r in sub.iterrows():
    p = (bg >= r[score]).mean() if pd.notna(r[score]) else 1.0
    pvals.append(max(p, 1e-12))
sub["p_raw"] = pvals
sub["p_fdr"] = bh_fdr(sub["p_raw"])
sub = sub.sort_values(score, ascending=False).head(60)

colors = {"oncogene": style.PALETTE["oncogene"], "TSG": style.PALETTE["tsg"], "both": style.PALETTE["dual"]}
fig, ax = plt.subplots(figsize=(7.5, 3.2))
x = np.arange(len(sub))
for role, g in sub.groupby("Role"):
    idx = [i for i, rr in enumerate(sub["Role"]) if rr == role]
    ax.vlines(idx, 0, sub.iloc[idx][score], color=colors.get(role, "gray"), linewidth=0.8)
    sig = sub.iloc[idx]["p_fdr"] < 0.05
    ax.scatter(np.array(idx)[sig], sub.iloc[idx][score][sig], color=colors.get(role, "gray"), s=18, label=f"{role} FDR<0.05")
    ax.scatter(np.array(idx)[~sig], sub.iloc[idx][score][~sig], facecolors="none", edgecolors=colors.get(role, "gray"), s=18, label=f"{role} n.s.")
ax.set_xticks(x)
ax.set_xticklabels(sub["Gene"].fillna(sub.get("Target", "")), rotation=90, fontsize=5)
ax.set_ylabel("Median / Avg Selectivity")
ax.set_title("Fig 2b — selectivity by gene role")
ax.legend(frameon=False, fontsize=5, ncol=3)
fig.tight_layout()
out = style.save_panel(fig, "fig2_b_lollipop", sub[["Gene", "Role", score, "p_fdr"]])
plt.show()
print(out)
'''),
        cell_md("## Panels c–d — Known DTI recovery at top 5% / 10%"),
        cell_code(r'''
# Approximate recovery using target_binding_stats + known pairs when full pair matrix unavailable.
# Prefer CRISPR file which already joins known status with selectivity/affinity ranks when available.
cr = io.read_crispr()
# Per-drug ranking by Selectivity_Score / aff_n / combined
need = {"Drug Chembl ID", "Selectivity_Score", "is_known"}
if need.issubset(cr.columns):
    d = cr.dropna(subset=["Selectivity_Score"]).copy()
    d["is_known"] = d["is_known"].astype(str).str.lower().isin(["1", "true", "yes", "known"])
    aff = "aff_n" if "aff_n" in d.columns else "Target_Affinity"
    d["combined"] = d["Selectivity_Score"].rank(pct=True) + d[aff].rank(pct=True)
    rows = []
    for thr, lab in [(0.05, "top5"), (0.10, "top10")]:
        for score_name, col in [("affinity", aff), ("selectivity", "Selectivity_Score"), ("combined", "combined")]:
            # within each drug, take top thr fraction
            def top_frac(g):
                k = max(1, int(np.ceil(thr * len(g))))
                return g.nlargest(k, col)
            tops = d.groupby("Drug Chembl ID", group_keys=False).apply(lambda g: top_frac(g))
            known_all = d[d["is_known"]]
            known_rec = tops[tops["is_known"]]
            # recovery = fraction of known pairs recovered
            denom = known_all.drop_duplicates(["Drug Chembl ID", "Gene"]).shape[0]
            num = known_rec.drop_duplicates(["Drug Chembl ID", "Gene"]).shape[0]
            rows.append({"threshold": lab, "strategy": score_name, "recovered": num, "known_total": denom, "frac": num / denom if denom else np.nan})
    rec = pd.DataFrame(rows)
else:
    rec = pd.DataFrame({"threshold": [], "strategy": [], "frac": []})
    print("CRISPR file missing expected columns; writing empty recovery table")

fig, axes = plt.subplots(1, 2, figsize=(7, 3), sharey=True)
for ax, thr in zip(axes, ["top5", "top10"]):
    sub = rec[rec["threshold"] == thr]
    if sub.empty:
        ax.text(0.5, 0.5, "n/a", ha="center")
    else:
        ax.bar(sub["strategy"], sub["frac"], color=[style.PALETTE["affinity"], style.PALETTE["selectivity"], style.PALETTE["combined"]])
        ax.axhline(float(thr.replace("top", ""))/100 if False else 0.05 if thr=="top5" else 0.10, ls="--", color="gray", lw=0.8, label="random")
    ax.set_title(f"Fig 2{'c' if thr=='top5' else 'd'} — {thr}")
    ax.set_ylabel("Fraction known DTIs recovered")
fig.tight_layout()
out = style.save_panel(fig, "fig2_cd_recovery", rec)
plt.show()
print(out)
display(rec)
'''),
        cell_md("## Panel e — EGFR / JAK1 radar profiles"),
        cell_code(r'''
radar = io.read_radar()
# Normalize metrics 0-1 per column for radar
metrics = [c for c in ["Selectivity_Score", "entropy_sel_n", "gap_local_n", "sr_local_n", "aff_local_n"] if c in radar.columns]
if not metrics:
    metrics = [c for c in radar.columns if radar[c].dtype != object][:5]
# Identify target
tcol = "Target"
radar["_gene"] = radar[tcol].astype(str).str.upper().str.extract(r"(EGFR|JAK1)")[0]
fig, axes = plt.subplots(1, 2, figsize=(8, 3.5), subplot_kw=dict(polar=True))
for ax, gene in zip(axes, ["EGFR", "JAK1"]):
    g = radar[radar["_gene"] == gene].copy()
    if g.empty:
        ax.set_title(gene + " (no data)")
        continue
    g = g.nlargest(5, "Selectivity_Score")
    angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]
    for _, row in g.iterrows():
        vals = []
        for m in metrics:
            col = g[m]
            v = (row[m] - col.min()) / (col.max() - col.min() + 1e-12)
            vals.append(v)
        vals += vals[:1]
        ax.plot(angles, vals, linewidth=1, label=str(row.get("Drug", ""))[:12])
        ax.fill(angles, vals, alpha=0.05)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics, fontsize=6)
    ax.set_title(gene)
    ax.legend(fontsize=5, loc="upper right", bbox_to_anchor=(1.35, 1.1))
fig.suptitle("Fig 2e — radar profiles")
fig.tight_layout()
out = style.save_panel(fig, "fig2_e_radar", radar)
plt.show()
print(out)
'''),
        cell_md("## Panel f — Docking score on-target vs off-target by role"),
        cell_code(r'''
dock = io.read_docking()
onco = io.read_onco_genes()
dock = dock.merge(onco, left_on="Gene", right_on="Gene", how="left")
dock["on_target"] = dock["Type"].astype(str).str.lower().eq("known")
dock = dock.dropna(subset=["Docking Score"])
# Role cleanup
dock["Role"] = dock["Role"].fillna("unknown")
fig, ax = plt.subplots(figsize=(5.5, 3.5))
roles = [r for r in ["oncogene", "TSG", "both", "Oncogene", "Tumor Suppressor"] if r in set(dock["Role"])]
if not roles:
    roles = sorted(dock["Role"].value_counts().head(3).index)
data_rows = []
positions = []
pos = 0
labels = []
for role in roles:
    for ot, name in [(True, "on"), (False, "off")]:
        vals = dock[(dock["Role"] == role) & (dock["on_target"] == ot)]["Docking Score"].values
        if len(vals) == 0:
            continue
        ax.violinplot([vals], positions=[pos], showmeans=False, showmedians=True, widths=0.8)
        data_rows.append({"Role": role, "class": name, "n": len(vals), "median": np.median(vals)})
        labels.append(f"{role}\n{name}")
        positions.append(pos)
        pos += 1
ax.set_xticks(positions)
ax.set_xticklabels(labels, fontsize=6)
ax.set_ylabel("Docking Score (kcal/mol)")
ax.set_title("Fig 2f — docking on vs off target")
fig.tight_layout()
out = style.save_panel(fig, "fig2_f_docking_raincloud", pd.DataFrame(data_rows))
plt.show()
print(out)
'''),
        cell_md("## Panel g — Cumulative recovery vs docking cutoff"),
        cell_code(r'''
dock = io.read_docking()
known = dock[dock["Type"].astype(str).str.lower().eq("known")].dropna(subset=["Docking Score"])
cutoffs = np.arange(-12, -1.5, 0.5)
fracs = []
for c in cutoffs:
    fracs.append((known["Docking Score"] <= c).mean())
rec = pd.DataFrame({"cutoff": cutoffs, "frac_recovered": fracs})
fig, ax = plt.subplots(figsize=(4.2, 3.2))
ax.plot(rec["cutoff"], rec["frac_recovered"], color=style.PALETTE["linkd"], lw=1.5)
for c in [-8, -7, -6]:
    y = (known["Docking Score"] <= c).mean()
    ax.axvline(c, color="gray", ls=":", lw=0.7)
    ax.text(c, y, f"{y*100:.1f}%", fontsize=6)
ax.set_xlabel("Docking score cutoff (kcal/mol)")
ax.set_ylabel("Fraction known pairs recovered")
ax.set_title("Fig 2g — cumulative docking recovery")
fig.tight_layout()
out = style.save_panel(fig, "fig2_g_docking_recovery", rec)
plt.show()
print(out)
'''),
    ]
    write("Figure2_LinkD_Select.ipynb", cells)


def nb_fig3():
    cells = [
        cell_md("# Figure 3 — LinkD-Pheno phenotypic validation\n\nDrug-sensitivity × CRISPR concordance stratified by LinkD-Select."),
        cell_md(DATA_HEADER + "\n\n- `known_drug_rank_crispr_cancer_driver_role.csv`\n- `matched_cells.csv`"),
        cell_code(SETUP),
        cell_md("## Panel a — Framework schematic"),
        cell_code("illustrate.show_panel('fig3_a', title='Panel a')"),
        cell_md("## Panel b — Cell lines across tissue lineages"),
        cell_code(r'''
cr = io.read_crispr()
# disease column encodes tissue / cancer type
if "disease" in cr.columns:
    counts = cr.groupby("disease")["cell_line"].nunique().sort_values(ascending=False).head(13)
else:
    counts = pd.Series(dtype=float)
fig, ax = plt.subplots(figsize=(5.5, 3.2))
if len(counts):
    ax.barh(counts.index[::-1], counts.values[::-1], color="#4C72B0")
ax.set_xlabel("N cell lines")
ax.set_title("Fig 3b — cell lines by disease / lineage")
fig.tight_layout()
out = style.save_panel(fig, "fig3_b_tissue_counts", counts.rename("n_cell_lines").reset_index())
plt.show()
print(out)
'''),
        cell_md("## Panel c — Concordance vs Selectivity (25 oncology genes)"),
        cell_code(r'''
cr = io.read_crispr()
# pick top 25 genes by known frequency
top_genes = cr.loc[cr["is_known"].astype(str).str.lower().isin(["1","true","yes","known"]), "Gene"].value_counts().head(25).index
sub = cr[cr["Gene"].isin(top_genes)].copy()
x = "landmark_correlation" if "landmark_correlation" in sub.columns else "AUC_corr"
fig, ax = plt.subplots(figsize=(4.2, 3.6))
ax.scatter(sub[x], sub["Selectivity_Score"], s=6, alpha=0.35, c="#4C72B0")
ax.set_xlabel(x)
ax.set_ylabel("Selectivity_Score")
ax.set_title("Fig 3c — concordance vs selectivity (25 genes)")
fig.tight_layout()
out = style.save_panel(fig, "fig3_c_scatter", sub[[x, "Selectivity_Score", "Gene", "Drug Chembl ID"]])
plt.show()
print(out)
'''),
        cell_md("## Panel d — All pairs with known overlay"),
        cell_code(r'''
cr = io.read_crispr()
x = "landmark_correlation"
cr = cr.dropna(subset=[x, "Selectivity_Score"]).copy()
cr["known_flag"] = cr["is_known"].astype(str).str.lower().isin(["1","true","yes","known"])
samp = cr.sample(n=min(30000, len(cr)), random_state=0)
fig, ax = plt.subplots(figsize=(4.2, 3.6))
pred = samp[~samp["known_flag"]]
ax.scatter(pred[x], pred["Selectivity_Score"], s=2, alpha=0.15, c="#4C72B0", label="predicted")
k = cr[cr["known_flag"]]
if len(k):
    k = k.sample(n=min(5000, len(k)), random_state=0)
    ax.scatter(k[x], k["Selectivity_Score"], s=4, alpha=0.35, c=style.PALETTE["known"], label="known")
ax.legend(frameon=False)
ax.set_xlabel(x)
ax.set_ylabel("Selectivity_Score")
ax.set_title("Fig 3d — all pairs + known overlay")
fig.tight_layout()
out = style.save_panel(fig, "fig3_d_overlay", cr[[x, "Selectivity_Score", "known_flag"]].sample(n=min(50000, len(cr)), random_state=0))
plt.show()
print(out)
'''),
        cell_md("## Panel e — Breast-cancer tissue slice"),
        cell_code(r'''
cr = io.read_crispr()
breast = cr[cr["disease"].astype(str).str.contains("breast", case=False, na=False)].copy()
x = "landmark_correlation"
fig, ax = plt.subplots(figsize=(4.2, 3.6))
if len(breast):
    ax.scatter(breast[x], breast["Selectivity_Score"], s=8, alpha=0.4)
ax.set_xlabel(x)
ax.set_ylabel("Selectivity_Score")
ax.set_title(f"Fig 3e — breast (n={breast['Gene'].nunique()} genes, {breast['cell_line'].nunique()} lines)")
fig.tight_layout()
out = style.save_panel(fig, "fig3_e_breast", breast[[x, "Selectivity_Score", "Gene", "cell_line"]])
plt.show()
print(out)
'''),
        cell_md("## Panel f — Cumulative recovery by Selectivity tier"),
        cell_code(r'''
cr = io.read_crispr().dropna(subset=["Selectivity_Score", "landmark_correlation"])
cr["is_known"] = cr["is_known"].astype(str).str.lower().isin(["1","true","yes","known"])
cr["tier"] = pd.qcut(cr["Selectivity_Score"], 3, labels=["Tier3", "Tier2", "Tier1"])
# For each drug, rank genes by concordance; compute cumulative known recovery
def recovery_curve(g, ks=range(1, 51)):
    g = g.sort_values("landmark_correlation", ascending=False)
    known = g["is_known"].to_numpy()
    out = []
    for k in ks:
        out.append(known[:k].sum() / max(known.sum(), 1))
    return out
ks = list(range(1, 51))
fig, ax = plt.subplots(figsize=(4.2, 3.4))
rows = []
for tier in ["Tier1", "Tier2", "Tier3"]:
    sub = cr[cr["tier"] == tier]
    curves = []
    for _, g in sub.groupby("Drug Chembl ID"):
        if g["is_known"].sum() == 0:
            continue
        curves.append(recovery_curve(g, ks))
    if not curves:
        continue
    mean = np.mean(curves, axis=0)
    ax.plot(ks, mean, label=tier)
    for k, v in zip(ks, mean):
        rows.append({"tier": tier, "K": k, "mean_recovery": v})
ax.plot(ks, np.array(ks)/cr.groupby("Drug Chembl ID").size().median(), ls="--", color="gray", label="random-ish")
ax.legend(frameon=False)
ax.set_xlabel("K")
ax.set_ylabel("Mean fraction known recovered")
ax.set_title("Fig 3f — recovery by Selectivity tier")
fig.tight_layout()
out = style.save_panel(fig, "fig3_f_recovery", pd.DataFrame(rows))
plt.show()
print(out)
'''),
        cell_md("## Panels g–h — Discovery volcano and novel network (approximate)"),
        cell_code(r'''
cr = io.read_crispr()
cr["is_known"] = cr["is_known"].astype(str).str.lower().isin(["1","true","yes","known"])
# volcano: x = concordance, y = -log10 FDR
if "FDR" in cr.columns:
    cr = cr.dropna(subset=["landmark_correlation", "FDR"])
    cr["neglog10p"] = -np.log10(cr["FDR"].clip(lower=1e-300))
else:
    cr["neglog10p"] = np.nan
novel = cr[(~cr["is_known"]) & (cr["landmark_correlation"] > 0.2) & (cr.get("FDR", 1) < 0.05)].copy()
fig, axes = plt.subplots(1, 2, figsize=(8.5, 3.5))
ax = axes[0]
ax.scatter(cr["landmark_correlation"], cr["neglog10p"], s=2, alpha=0.1, c="#bbbbbb")
ax.scatter(novel["landmark_correlation"], novel["neglog10p"], s=8, alpha=0.5, c=style.PALETTE["linkd"])
ax.set_xlabel("landmark_correlation")
ax.set_ylabel("-log10 FDR")
ax.set_title("Fig 3g — discovery volcano")
# network-like degree plot for top novel pairs
ax = axes[1]
top = novel.nlargest(34, "Selectivity_Score")
if len(top):
    deg = pd.concat([top["Drug Chembl ID"], top["Gene"]]).value_counts().head(20)
    ax.barh(deg.index.astype(str)[::-1], deg.values[::-1], color=style.PALETTE["linkd"])
ax.set_title("Fig 3h — top nodes among 34 novel-like pairs")
fig.tight_layout()
out = style.save_panel(fig, "fig3_gh_volcano_network", top if len(novel) else cr.head(0))
plt.show()
print("novel-like pairs:", len(novel))
print(out)
'''),
    ]
    write("Figure3_LinkD_Pheno.ipynb", cells)


def nb_fig4():
    cells = [
        cell_md("# Figure 4 — Population-scale EHR validation"),
        cell_md(DATA_HEADER + "\n\n- `TableS3_Mount_Sinai_Drug_Cancer.csv`\n- `TableS4_UK_Biobank_Drug_Disease.csv`"),
        cell_code(SETUP),
        cell_md("## Panel a — Framework schematic"),
        cell_code("illustrate.show_panel('fig4_a', title='Panel a')"),
        cell_md("## Panel b — Drug–disease OR network (top protective / risk edges)"),
        cell_code(r'''
ms = io.read_ehr_ms()
# Use logit_or and logit_p
ms = ms.dropna(subset=["logit_or", "logit_p"]).copy()
ms["neglog10p"] = -np.log10(ms["logit_p"].clip(lower=1e-300))
# Keep strongest associations
top = pd.concat([
    ms.nsmallest(40, "logit_or"),
    ms.nlargest(40, "logit_or"),
]).drop_duplicates()
# Simple bipartite layout
drugs = top["Drug Name"].astype(str).unique()
diseases = top["Disease Description"].astype(str).unique()
drug_y = {d: i for i, d in enumerate(drugs)}
dis_y = {d: i for i, d in enumerate(diseases)}
fig, ax = plt.subplots(figsize=(7.5, 5))
for _, r in top.iterrows():
    y0 = drug_y[str(r["Drug Name"])]
    y1 = dis_y[str(r["Disease Description"])]
    color = "#C44E52" if r["logit_or"] < 0 else "#4C72B0"
    ax.plot([0, 1], [y0, y1], color=color, alpha=0.25, lw=0.8)
ax.scatter(np.zeros(len(drugs)), range(len(drugs)), s=10, c="k")
ax.scatter(np.ones(len(diseases)), range(len(diseases)), s=10, c="k")
ax.set_xticks([0, 1])
ax.set_xticklabels(["Drug", "Disease"])
ax.set_yticks([])
ax.set_title("Fig 4b — top Mount Sinai drug–disease edges (red=protective logit_or<0)")
fig.tight_layout()
out = style.save_panel(fig, "fig4_b_network", top[["Drug Name", "Disease Description", "logit_or", "logit_p", "ICD10"]])
plt.show()
print(out)
'''),
    ]
    write("Figure4_EHR_Validation.ipynb", cells)


def nb_figs5():
    cells = [
        cell_md("# Figure S5 — EHR volcano plots (Mount Sinai + UK Biobank)"),
        cell_md(DATA_HEADER),
        cell_code(SETUP),
        cell_md("## Mount Sinai volcano"),
        cell_code(r'''
ms = io.read_ehr_ms().dropna(subset=["logit_or", "logit_p"])
ms["neglog10p"] = -np.log10(ms["logit_p"].clip(lower=1e-300))
fig, ax = plt.subplots(figsize=(4.5, 3.5))
ax.scatter(ms["logit_or"], ms["neglog10p"], s=4, alpha=0.3, c="#4C72B0")
ax.axvline(0, color="gray", lw=0.6)
ax.set_xlabel("logit OR")
ax.set_ylabel("-log10 p")
ax.set_title("Fig S5 — Mount Sinai")
fig.tight_layout()
out = style.save_panel(fig, "figS5_ms_volcano", ms[["Drug Name", "ICD10", "logit_or", "logit_p", "neglog10p"]])
plt.show()
print(out)
'''),
        cell_md("## UK Biobank volcano"),
        cell_code(r'''
uk = io.read_ehr_ukb().dropna(subset=["odds_ratio"])
# derive a pseudo p from counts if needed; plot OR vs exposure support
uk["log_or"] = np.log(uk["odds_ratio"].clip(lower=1e-6))
uk["support"] = uk[["drug_cancer", "drug_no_cancer"]].sum(axis=1)
fig, ax = plt.subplots(figsize=(4.5, 3.5))
ax.scatter(uk["log_or"], np.log10(uk["support"] + 1), s=8, alpha=0.4, c="#DD8452")
ax.axvline(0, color="gray", lw=0.6)
ax.set_xlabel("log odds ratio")
ax.set_ylabel("log10(exposed n)")
ax.set_title("Fig S5 — UK Biobank")
fig.tight_layout()
out = style.save_panel(fig, "figS5_ukb_volcano", uk[["Drug Name", "ICD10", "odds_ratio", "log_or", "support"]])
plt.show()
print(out)
'''),
    ]
    write("FigureS5_EHR_Volcano.ipynb", cells)


def nb_fig5():
    cells = [
        cell_md("# Figure 5 — β-blocker / ADRB2 / prostate cancer case study"),
        cell_md(DATA_HEADER + """

- `adrenergic_selectivity_fig5.csv`
- `Propranolol_growth.csv`, `Carvedilol_growth.csv`
- `vct/propranolol/*.csv`, `vct/carvedilol/*.csv`
"""),
        cell_code(SETUP),
        cell_md("## Panel a — LinkD-Select ranks for ADRB2"),
        cell_code(r'''
adr = io.read_adrenergic()
adrb2 = adr[adr["Target"].astype(str).str.contains("ADRB2", case=False)].copy()
adrb2 = adrb2.sort_values("Selectivity_Score", ascending=False).reset_index(drop=True)
adrb2["rank"] = np.arange(1, len(adrb2) + 1)
# map chembl names if possible
sel = io.read_selectivity()
name_map = sel.set_index("Drug Chembl ID")["Drug Name"].to_dict() if "Drug Name" in sel.columns else {}
adrb2["Drug Name"] = adrb2["Drug"].map(name_map)
fig, ax = plt.subplots(figsize=(5, 3.4))
ax.scatter(adrb2["rank"], adrb2["Selectivity_Score"], s=3, alpha=0.3, c="#888888")
for drug, color in [("Propranolol", "#C44E52"), ("Carvedilol", "#1ABC9C"), ("Metoprolol", "#7F8C8D")]:
    m = adrb2["Drug Name"].astype(str).str.contains(drug, case=False, na=False)
    if m.any():
        r = adrb2[m].iloc[0]
        ax.scatter([r["rank"]], [r["Selectivity_Score"]], s=40, c=color, label=f"{drug} (rank {int(r['rank'])})")
ax.legend(frameon=False)
ax.set_xlabel("Rank")
ax.set_ylabel("Selectivity_Score")
ax.set_title("Fig 5a — ADRB2 selectivity ranks")
fig.tight_layout()
out = style.save_panel(fig, "fig5_a_adrb2_ranks", adrb2[["rank", "Drug", "Drug Name", "Selectivity_Score", "Rank_Select"]])
plt.show()
print(out)
'''),
        cell_md("## Panels b–c — Docked poses (illustration + process)"),
        cell_code("illustrate.show_panel('fig5_b', title='Panel b — propranolol / ADRB2')\nillustrate.show_panel('fig5_c', title='Panel c — carvedilol / ADRB2')"),
        cell_md("## Panel d — Adrenergic receptor selectivity heatmap"),
        cell_code(r'''
adr = io.read_adrenergic()
sel = io.read_selectivity()
name_map = sel.set_index("Drug Chembl ID")["Drug Name"].to_dict() if "Drug Name" in sel.columns else {}
adr["Drug Name"] = adr["Drug"].map(name_map)
focus = ["Propranolol", "Carvedilol", "Metoprolol"]
sub = adr[adr["Drug Name"].astype(str).str.contains("|".join(focus), case=False, na=False)].copy()
# normalize drug label
def canon(n):
    n = str(n).lower()
    for f in focus:
        if f.lower() in n:
            return f
    return n
sub["drug_label"] = sub["Drug Name"].map(canon)
sub["receptor"] = sub["Target"].astype(str).str.replace("_HUMAN", "", regex=False)
piv = sub.pivot_table(index="drug_label", columns="receptor", values="Selectivity_Score", aggfunc="mean")
piv = piv.reindex([f for f in focus if f in piv.index])
fig, ax = plt.subplots(figsize=(5.5, 2.2))
im = ax.imshow(piv.values, aspect="auto", cmap="magma")
ax.set_xticks(range(len(piv.columns)))
ax.set_xticklabels(piv.columns, rotation=45, ha="right")
ax.set_yticks(range(len(piv.index)))
ax.set_yticklabels(piv.index)
ax.set_title("Fig 5d — adrenergic selectivity heatmap")
fig.colorbar(im, ax=ax, fraction=0.046)
fig.tight_layout()
out = style.save_panel(fig, "fig5_d_heatmap", piv.reset_index())
plt.show()
print(out)
print("Note: packaged extract currently includes ADRB1/2/3; ADRA subtypes may be absent.")
'''),
        cell_md("## Panels e–f — LNCaP growth inhibition assays"),
        cell_code(r'''
from scipy.stats import mannwhitneyu
fig, axes = plt.subplots(1, 2, figsize=(7.5, 3.4), sharey=True)
for ax, drug, fname in [
    (axes[0], "Propranolol", "propranolol"),
    (axes[1], "Carvedilol", "carvedilol"),
]:
    g = io.read_growth(fname)
    g.columns = [c.strip() for c in g.columns]
    # melt
    long = g.melt(var_name="condition", value_name="viability").dropna()
    order = list(g.columns)
    data = [long.loc[long["condition"] == c, "viability"].values for c in order]
    ax.boxplot(data, labels=order, showfliers=False)
    for i, vals in enumerate(data, start=1):
        ax.scatter(np.random.normal(i, 0.05, size=len(vals)), vals, s=10, alpha=0.7, c="#333333")
    # stats vs DMSO
    if len(data) >= 2:
        for i in range(1, len(data)):
            try:
                p = mannwhitneyu(data[0], data[i], alternative="two-sided").pvalue
            except Exception:
                p = np.nan
            ax.text(i+1, max(data[i]) if len(data[i]) else 0, f"p={p:.2g}", ha="center", fontsize=6)
    ax.set_title(f"Fig 5{'e' if drug=='Propranolol' else 'f'} — {drug}")
    ax.tick_params(axis="x", rotation=30)
    ax.set_ylabel("% viability" if drug=="Propranolol" else "")
fig.tight_layout()
# save combined source
src = pd.concat([
    io.read_growth("propranolol").assign(drug="Propranolol"),
    io.read_growth("carvedilol").assign(drug="Carvedilol"),
])
out = style.save_panel(fig, "fig5_ef_growth", src)
plt.show()
print(out)
'''),
        cell_md("## Panels g–k — EHR target-trial results (from VCT summary tables)\nPatient-level PHI is not packaged; these panels regenerate from propensity-matched summary outputs."),
        cell_code(r'''
# Panel h/i style: cumulative incidence / HR for propranolol vs metoprolol (AvsB)
hr_p = io.read_vct("propranolol", "results_HR.csv")
hr_c = io.read_vct("carvedilol", "results_HR.csv")
inc_p = io.read_vct("propranolol", "results_incidence.csv")
# Prefer AvsB_1to1_full seed0
def pick(df):
    m = df[(df["cell"].astype(str).str.contains("AvsB_1to1_full")) & (df.get("seed", 0) == 0)].copy()
    if m.empty:
        m = df[df["cell"].astype(str).str.contains("AvsB_1to1_full")].copy()
    return m.sort_values("window_days")

hp = pick(hr_p)
hc = pick(hr_c)
ip = pick(inc_p)

fig, axes = plt.subplots(1, 3, figsize=(10, 3.2))
# incidence-like bars for 5y if available
ax = axes[0]
sub = ip[ip["window_label"] == "5y"]
if len(sub):
    r = sub.iloc[0]
    ax.bar(["treat", "ctrl"], [r["ir_treat"], r["ir_ctrl"]], color=["#C44E52", "#7F8C8D"])
    ax.set_title(f"Fig 5h — Prop vs Met IR 5y\nHR={hp[hp.window_label=='5y'].iloc[0]['hr']:.2f}" if len(hp[hp.window_label=='5y']) else "Fig 5h")
else:
    ax.set_title("Fig 5h — no 5y row")
ax.set_ylabel("Incidence rate")

ax = axes[1]
# carvedilol HR forest across windows
if len(hc):
    ax.errorbar(hc["hr"], np.arange(len(hc)), xerr=[hc["hr"]-hc["ci_lower"], hc["ci_upper"]-hc["hr"]], fmt="o", color="#1ABC9C")
    ax.axvline(1, color="gray", lw=0.7)
    ax.set_yticks(range(len(hc)))
    ax.set_yticklabels(hc["window_label"])
ax.set_title("Fig 5i — Carvedilol vs Met HR")
ax.set_xlabel("Hazard ratio")

ax = axes[2]
# panel j: HR across windows for both drugs
for lab, df, color in [("Propranolol", hp, "#C44E52"), ("Carvedilol", hc, "#1ABC9C")]:
    if len(df):
        ax.plot(df["window_label"], df["hr"], marker="o", label=lab, color=color)
ax.axhline(1, color="gray", lw=0.7)
ax.legend(frameon=False, fontsize=6)
ax.set_title("Fig 5j — HR by follow-up window")
ax.set_ylabel("HR")
fig.tight_layout()
out = style.save_panel(fig, "fig5_hij_ehr", pd.concat([hp.assign(drug="propranolol"), hc.assign(drug="carvedilol")], ignore_index=True))
plt.show()
print(out)
'''),
        cell_code(r'''
# Panel k — subgroup forest for propranolol
sg = io.read_vct("propranolol", "results_subgroup.csv")
sg = sg[(sg["cell"].astype(str).str.contains("AvsB_1to1_full")) & (sg["window_label"] == "5y")].copy()
if sg.empty:
    sg = io.read_vct("propranolol", "results_subgroup.csv")
    sg = sg[sg["window_label"] == "5y"].copy()
fig, ax = plt.subplots(figsize=(5.5, 4.5))
if len(sg):
    y = np.arange(len(sg))
    ax.errorbar(sg["hr_in_group"], y, xerr=[sg["hr_in_group"]-sg["hr_ci_lower_in_group"], sg["hr_ci_upper_in_group"]-sg["hr_in_group"]], fmt="o", color="#C44E52")
    ax.axvline(1, color="gray", lw=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels(sg["label"].astype(str), fontsize=6)
ax.set_xlabel("HR")
ax.set_title("Fig 5k — propranolol subgroup HR (5y)")
fig.tight_layout()
out = style.save_panel(fig, "fig5_k_subgroup", sg)
plt.show()
print(out)
'''),
        cell_md("## Panel g — PSM design (illustration from descriptive balance)"),
        cell_code(r'''
desc = io.read_vct("propranolol", "descriptive_stats.csv")
desc = desc[desc["cell"].astype(str).str.contains("AvsB_1to1_full")].copy()
fig, ax = plt.subplots(figsize=(4.5, 3.5))
d = desc[desc["covariate"] != "n_matched"].dropna(subset=["smd"])
ax.axvline(0.1, color="gray", ls="--", lw=0.7)
ax.axvline(-0.1, color="gray", ls="--", lw=0.7)
ax.scatter(d["smd"], np.arange(len(d)), s=20, c="#4C72B0")
ax.set_yticks(range(len(d)))
ax.set_yticklabels(d["covariate"], fontsize=6)
ax.set_xlabel("Standardized mean difference")
ax.set_title("Fig 5g — covariate balance after PSM (SMD)")
fig.tight_layout()
out = style.save_panel(fig, "fig5_g_psm_balance", d)
plt.show()
print(out)
display(Markdown("Full PSM design narrative is in `source_data/vct/propranolol/SUMMARY.md`."))
'''),
    ]
    write("Figure5_BetaBlocker_ADRB2.ipynb", cells)


def nb_fig6():
    cells = [
        cell_md("# Figure 6 — LinkD-Agent interactive analysis & benchmark"),
        cell_md(DATA_HEADER + "\n\n- `source_data/benchmark/` summary JSONL + leaderboard"),
        cell_code(SETUP),
        cell_md("## Panels a–b — Architecture / planning schematics"),
        cell_code("illustrate.show_panel('fig6_a', title='Panel a')\nillustrate.show_panel('fig6_b', title='Panel b')"),
        cell_md("## Panel c — Agent benchmark heatmap"),
        cell_code(r'''
import json
# Aggregate summary.*.jsonl into a method x task score matrix when possible
rows = []
for p in sorted((paths.SOURCE / "benchmark").glob("summary.*.jsonl")):
    with p.open() as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            rows.append(rec)
sumdf = pd.DataFrame(rows)
display(Markdown(f"Loaded {len(sumdf)} summary records from benchmark JSONL"))
# Heuristic column detection
score_col = next((c for c in ["primary_score", "score", "metric_value", "ndcg", "auroc", "cindex"] if c in sumdf.columns), None)
method_col = next((c for c in ["condition", "method", "agent", "model"] if c in sumdf.columns), None)
task_col = next((c for c in ["scenario", "task", "task_id"] if c in sumdf.columns), None)
fig, ax = plt.subplots(figsize=(6.5, 3.8))
if score_col and method_col and task_col and len(sumdf):
    piv = sumdf.pivot_table(index=method_col, columns=task_col, values=score_col, aggfunc="mean")
    im = ax.imshow(piv.values, aspect="auto", cmap="YlOrRd")
    ax.set_xticks(range(len(piv.columns)))
    ax.set_xticklabels(piv.columns, rotation=45, ha="right", fontsize=6)
    ax.set_yticks(range(len(piv.index)))
    ax.set_yticklabels(piv.index, fontsize=6)
    fig.colorbar(im, ax=ax, fraction=0.046)
    src = piv.reset_index()
else:
    # Fallback: show leaderboard.csv
    lb = paths.SOURCE / "benchmark" / "leaderboard.csv"
    if lb.exists():
        ldb = pd.read_csv(lb)
        display(ldb.head())
        ax.axis("off")
        ax.table(cellText=ldb.head(12).values, colLabels=list(ldb.columns), loc="center", fontsize=6)
        src = ldb
    else:
        ax.text(0.5, 0.5, "No benchmark matrix columns found", ha="center")
        src = sumdf.head(0)
ax.set_title("Fig 6c — benchmark summary")
fig.tight_layout()
out = style.save_panel(fig, "fig6_c_benchmark", src if isinstance(src, pd.DataFrame) else pd.DataFrame())
plt.show()
print(out)
# Also note pre-rendered reference figures were copied if present
for name in ["fig6_benchmark_heatmap.png", "fig6_benchmark_bars.png"]:
    p = paths.SOURCE / "benchmark" / name
    if p.exists():
        display(Markdown(f"Reference render available: `{p.relative_to(paths.ROOT)}`"))
'''),
    ]
    write("Figure6_LinkD_Agent.ipynb", cells)


def nb_figs34():
    cells = [
        cell_md("# Figures S3–S4 — Tissue-resolved concordance landscapes\n\nBuilt from the packaged CRISPR concordance table (`cell_line`, `disease` columns)."),
        cell_md(DATA_HEADER),
        cell_code(SETUP),
        cell_md("## Figure S3 — Affinity–concordance landscapes for canonical oncology genes"),
        cell_code(r'''
cr = io.read_crispr().dropna(subset=["landmark_correlation", "Target_Affinity"])
genes = cr["Gene"].value_counts().head(25).index
sub = cr[cr["Gene"].isin(genes)]
# facet-like small multiples for first 6 genes
show = list(genes[:6])
fig, axes = plt.subplots(2, 3, figsize=(9, 5.5), sharex=True, sharey=True)
for ax, g in zip(axes.ravel(), show):
    gg = sub[sub["Gene"] == g]
    ax.scatter(gg["landmark_correlation"], gg["Target_Affinity"], s=6, alpha=0.35)
    ax.set_title(g, fontsize=8)
axes[1,0].set_xlabel("concordance")
axes[0,0].set_ylabel("Target_Affinity")
fig.suptitle("Fig S3 — affinity vs concordance")
fig.tight_layout()
out = style.save_panel(fig, "figS3_affinity_concordance", sub[sub["Gene"].isin(show)][["Gene","landmark_correlation","Target_Affinity","Selectivity_Score"]])
plt.show()
print(out)
'''),
        cell_md("## Figure S4 — Selectivity–concordance across lineages"),
        cell_code(r'''
cr = io.read_crispr().dropna(subset=["landmark_correlation", "Selectivity_Score", "disease"])
tissues = cr.groupby("disease")["cell_line"].nunique().sort_values(ascending=False).head(7).index
fig, axes = plt.subplots(2, 4, figsize=(10, 5), sharex=True, sharey=True)
axes = axes.ravel()
for i, t in enumerate(tissues):
    ax = axes[i]
    gg = cr[cr["disease"] == t]
    if len(gg) > 8000:
        gg = gg.sample(8000, random_state=0)
    ax.scatter(gg["landmark_correlation"], gg["Selectivity_Score"], s=3, alpha=0.2)
    ax.set_title(str(t)[:28], fontsize=7)
for j in range(i+1, len(axes)):
    axes[j].axis("off")
fig.suptitle("Fig S4 — selectivity vs concordance by tissue")
fig.tight_layout()
out = style.save_panel(fig, "figS4_tissue_selectivity", cr[cr["disease"].isin(tissues)][["disease","landmark_correlation","Selectivity_Score"]].sample(n=min(30000, len(cr)), random_state=0))
plt.show()
print(out)
'''),
    ]
    write("FigureS3_S4_Tissue_Resolved.ipynb", cells)


def main():
    NB_DIR.mkdir(parents=True, exist_ok=True)
    nb_setup()
    nb_fig1()
    nb_figs2()
    nb_fig2()
    nb_fig3()
    nb_fig4()
    nb_figs5()
    nb_fig5()
    nb_fig6()
    nb_figs34()
    print("Done. Notebooks in", NB_DIR)


if __name__ == "__main__":
    main()
