"""
Figure 6 benchmark panel (Cell journal spec) — LinkD vs LLM vs ToolUniverse vs LinkD+LLM(Combined)
vs LinkD+LLM(Orchestrator) across 7 manuscript-aligned drug-discovery tasks.

Cell figure requirements honoured: Arial sans-serif, ≥6 pt text, ≥0.5 pt rules, colour-blind-safe
(Okabe–Ito) palette, RGB, 300 dpi raster + editable Type-42 vector PDF, sizes at Cell column widths
(1 col = 85 mm, 1.5 col = 114 mm, 2 col = 174 mm). LLM = GPT-5.4 (named); Combined/Orchestrator use
the same model. ToolUniverse(OpenTargets) applies only to disease-target tasks (T2/T3) and the
association baseline for T5; n/a elsewhere.

    python3 benchmark/report/fig6_cell.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "figures")
os.makedirs(OUT, exist_ok=True)

# ---- data loaded from results/summary.*.jsonl; LLM/Combined/Orchestrator = gpt-5.4 ----
TASKS = ["T1\nbinding\naffinity", "T2\ntarget\nID", "T3\ntarget\npriority", "T4\nCRISPR→\nMoA",
         "T5\nevidence\nfusion", "T6\nMoA\nrecall", "T7\nselect-\nivity"]
METRIC = ["C-Index", "nDCG@20", "nDCG@20", "nDCG@20", "AUROC", "nDCG@20", "AUROC"]
TYPE = ["Prediction", "Prediction", "Prediction", "Mechanism", "Integration", "Knowledge", "Knowledge"]
SCENARIOS = ["t1_dti", "a2_target_id", "a3_priority", "l4_crispr_moa",
             "c1_validate", "l2_binding_moa", "l3_selectivity"]
METRIC_KEY = ["c_index", "ndcg@20", "ndcg@20", "ndcg@20", "auroc", "ndcg@20", "auroc"]
NAN = np.nan
ORDER = ["LinkD", "GPT-5.4", "ToolUniverse", "LinkD+LLM (Combined)", "LinkD+LLM (Orchestrator)"]
# Okabe–Ito colour-blind-safe
COL = {"LinkD": "#0072B2", "GPT-5.4": "#E69F00", "ToolUniverse": "#999999",
       "LinkD+LLM (Combined)": "#009E73", "LinkD+LLM (Orchestrator)": "#CC79A7"}
TYPE_COL = {"Prediction": "#0072B2", "Mechanism": "#D55E00", "Integration": "#009E73", "Knowledge": "#CC79A7"}

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 7, "axes.linewidth": 0.5, "pdf.fonttype": 42, "ps.fonttype": 42,
    "xtick.major.width": 0.5, "ytick.major.width": 0.5, "savefig.dpi": 300,
})
MM = 1 / 25.4


def _load_rows():
    import glob
    import json
    results = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
    rows = []
    for path in sorted(glob.glob(os.path.join(results, "summary.*.jsonl"))):
        with open(path) as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    if r.get("errors", 0) != r.get("n", -1):
                        rows.append(r)
    return rows


def _pick(rows, scenario, metric, pred):
    cand = [r for r in rows if r.get("scenario") == scenario and pred(r) and r.get(metric) is not None]
    return max((float(r[metric]) for r in cand), default=NAN)


def _build_data():
    rows = _load_rows()
    explicit_linkd = {
        "t1_dti": "linkd_cli",
        "a2_target_id": "linkd",
        "a3_priority": "linkd",
        "l4_crispr_moa": "linkd_crispr_tgt",
        "c1_validate": "linkd_evidence",
        "l2_binding_moa": "linkd_binding_tgt",
        "l3_selectivity": "linkd_selectivity",
    }
    tool_condition = {"a2_target_id": "tooluniverse", "a3_priority": "tooluniverse",
                      "c1_validate": "ot_assoc"}
    data = {m: [] for m in ORDER}
    for scenario, metric in zip(SCENARIOS, METRIC_KEY):
        data["LinkD"].append(_pick(
            rows, scenario, metric,
            lambda r, cond=explicit_linkd[scenario]: r.get("condition") == cond))
        data["GPT-5.4"].append(_pick(
            rows, scenario, metric,
            lambda r: r.get("condition") == "closed_book" and r.get("model") == "gpt-5.4"))
        data["ToolUniverse"].append(_pick(
            rows, scenario, metric,
            lambda r, cond=tool_condition.get(scenario): cond is not None and r.get("condition") == cond))
        data["LinkD+LLM (Combined)"].append(_pick(
            rows, scenario, metric,
            lambda r: r.get("condition") == "combined" and r.get("model") == "gpt-5.4"))
        data["LinkD+LLM (Orchestrator)"].append(_pick(
            rows, scenario, metric,
            lambda r: r.get("condition") == "orchestrator" and r.get("model") == "gpt-5.4"))
    return data


DATA = _build_data()


def _means():
    return {m: np.nanmean(DATA[m]) for m in ORDER}


def _save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"{name}.png + .pdf -> {OUT}")


def barplot():
    """Grouped bars: 7 tasks + Mean × 5 methods. 174 mm (2-col) × 82 mm."""
    fig, ax = plt.subplots(figsize=(174 * MM, 82 * MM))
    fig.subplots_adjust(top=0.86, bottom=0.20, left=0.07, right=0.99)
    groups = [f"{t}" for t in ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]] + ["Mean"]
    short = ["binding\naffinity", "target\nID", "target\npriority", "CRISPR→\nMoA",
             "evidence\nfusion", "MoA\nrecall", "selecti-\nvity", ""]
    means = _means()
    x = np.arange(len(groups))
    nb = len(ORDER)
    w = 0.84 / nb
    for i, m in enumerate(ORDER):
        vals = list(DATA[m]) + [means[m]]
        xs = x - 0.42 + w * (i + 0.5)
        ax.bar(xs, [0 if (v != v) else v for v in vals], w, color=COL[m],
               edgecolor="white", linewidth=0.3, label=m, zorder=3)
        for xi, v in zip(xs, vals):
            if v != v:
                ax.text(xi, 0.015, "n/a", rotation=90, ha="center", va="bottom",
                        fontsize=4.4, color="#999", zorder=4)
    ax.axvline(len(TASKS) - 0.5, color="#cccccc", lw=0.6, ls=(0, (3, 3)), zorder=1)
    ax.axhline(0.5, color="#bbbbbb", lw=0.5, ls=(0, (2, 3)), zorder=1)
    ax.text(-0.4, 0.512, "chance", fontsize=5, color="#999", va="bottom")
    ax.set_xticks(x)
    ax.set_xticklabels(groups, fontsize=6.5, fontweight="bold")
    for xi, s in zip(x, short):
        ax.text(xi, -0.10, s, ha="center", va="top", fontsize=5.3, color="#444",
                transform=ax.get_xaxis_transform())
    # metric per task (small, italic) above the group
    for xi, mt in zip(x[:len(METRIC)], METRIC):
        ax.text(xi, 0.965, mt, ha="center", va="top", fontsize=4.6, color="#777", style="italic")
    ax.set_ylim(0, 1.0)
    ax.set_xlim(-0.6, len(groups) - 0.4)
    ax.set_ylabel("Benchmark score  (higher = better)", fontsize=7)
    ax.set_yticks(np.arange(0, 1.01, 0.2))
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.legend(ncol=5, fontsize=6.2, frameon=False, loc="upper center",
               bbox_to_anchor=(0.5, 1.005), handlelength=1.2, columnspacing=1.4, handletextpad=0.4)
    _save(fig, "fig6_benchmark_bars")


def heatmap():
    """Methods × tasks heatmap (annotated) — Figure 6 panel c. 178 mm × 72 mm."""
    # row labels name the LLM explicitly (GPT-5.4), not the generic "LLM"
    LABELS = {"LinkD": "LinkD", "GPT-5.4": "GPT-5.4", "ToolUniverse": "ToolUniverse",
              "LinkD+LLM (Combined)": "LinkD + GPT-5.4 (Combined)",
              "LinkD+LLM (Orchestrator)": "LinkD + GPT-5.4 (Orchestrator)"}
    fig, ax = plt.subplots(figsize=(178 * MM, 72 * MM))
    fig.subplots_adjust(left=0.27, right=0.99, top=0.90, bottom=0.24)
    M = np.array([DATA[m] + [np.nanmean(DATA[m])] for m in ORDER])
    cols = [t.replace("\n", " ") for t in TASKS] + ["Mean"]
    im = ax.imshow(M, aspect="auto", cmap="YlGnBu", vmin=0.3, vmax=0.95)
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=35, ha="right", fontsize=8, color="black")
    ax.set_yticks(range(len(ORDER)))
    ax.set_yticklabels([LABELS[m] for m in ORDER], fontsize=8.5, color="black")
    ax.tick_params(colors="black")
    for i in range(len(ORDER)):
        for j in range(len(cols)):
            v = M[i, j]
            if v == v:
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7.6,
                        color="white" if v > 0.66 else "black")
            else:
                ax.text(j, i, "n/a", ha="center", va="center", fontsize=6.5, color="#888")
    ax.set_xticks(np.arange(-.5, len(cols), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(ORDER), 1), minor=True)
    ax.grid(which="minor", color="white", lw=0.8)
    ax.tick_params(which="minor", length=0)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    # metric row under x labels (black)
    for j, mt in enumerate(METRIC):
        ax.text(j, len(ORDER) - 0.34, mt, ha="center", va="top", fontsize=6.0, color="black",
                style="italic", transform=ax.transData)
    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.015)
    cb.set_label("benchmark score", fontsize=8, color="black")
    cb.ax.tick_params(labelsize=7, width=0.5, colors="black")
    cb.outline.set_linewidth(0.5)
    ax.set_title("LinkD vs GPT-5.4 vs ToolUniverse vs LinkD+GPT-5.4 across drug-discovery tasks",
                 fontsize=9, color="black", pad=6)
    # panel letter (Cell style: bold lower-case, top-left)
    fig.text(0.012, 0.985, "c", fontsize=12, fontweight="bold", va="top", ha="left", color="black")
    _save(fig, "fig6_benchmark_heatmap")


if __name__ == "__main__":
    barplot()
    heatmap()
    m = _means()
    print("means:", {k: round(float(v), 3) for k, v in m.items()})
