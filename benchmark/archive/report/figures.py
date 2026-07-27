"""
Academic figures for the benchmark leaderboard (Arial, Okabe-Ito, 300 dpi),
matching a simple manuscript figure style. Reads results/summary.*.jsonl.

    python3 benchmark/report/figures.py
"""
import glob
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULTS = os.path.join(ROOT, "benchmark", "results")
FIGDIR = os.path.join(RESULTS, "figures")

NAVY = "#1a1a1a"; BLUE = "#0072B2"; ORANGE = "#E69F00"; GREEN = "#117733"
VERM = "#D55E00"; GREY = "#7a7a7a"; PURPLE = "#CC79A7"; SKY = "#56B4E9"
plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "axes.edgecolor": "#333333", "axes.linewidth": 0.8, "axes.titlecolor": NAVY,
    "axes.titleweight": "bold", "axes.titlesize": 12, "axes.labelsize": 10, "text.color": NAVY,
    "xtick.color": NAVY, "ytick.color": NAVY, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "xtick.direction": "out", "ytick.direction": "out",
    "axes.grid": True, "axes.axisbelow": True, "grid.color": "#ececec", "grid.linewidth": 0.6,
    "legend.frameon": False, "legend.fontsize": 9, "savefig.dpi": 300, "pdf.fonttype": 42,
})


def load_rows():
    rows = []
    for f in sorted(glob.glob(os.path.join(RESULTS, "summary.*.jsonl"))):
        rows += [json.loads(l) for l in open(f) if l.strip()]
    return [r for r in rows if r.get("errors", 0) != r.get("n", -1)]


def _by(rows, scenario, condition):
    return {r["model"]: r for r in rows if r["scenario"] == scenario and r["condition"] == condition}


def fig_dti(rows):
    """T1 DTI on external DAVIS gold: LinkD prediction vs the LLM that attempted it."""
    dti = [r for r in rows if r["scenario"] == "t1_dti"]
    if not dti:
        return
    linkd = next((r for r in dti if r["condition"] == "linkd_cli"), None)
    # the strongest LLM that actually produced pKd estimates (answered>0, has pearson)
    llm = max((r for r in dti if r["condition"] == "closed_book" and r.get("pearson") is not None),
              key=lambda r: r.get("answered", 0), default=None)
    if not linkd:
        return
    metrics = [("Pearson r", "pearson"), ("Spearman", "spearman"),
               ("C-Index", "c_index"), ("Binary acc.", "binary_acc")]
    x = np.arange(len(metrics)); bw = 0.38
    fig, ax = plt.subplots(figsize=(7.6, 4.6), dpi=300)
    a = [linkd.get(k) or 0 for _, k in metrics]
    ax.bar(x - bw / 2, a, bw, color=GREEN, edgecolor="white", label="LinkD (predicted pKd)")
    if llm:
        b = [llm.get(k) or 0 for _, k in metrics]
        ax.bar(x + bw / 2, b, bw, color=GREY, edgecolor="white",
               label=f"Base LLM ({llm['model']})")
        for i in range(len(metrics)):
            ax.text(i + bw / 2, b[i] + 0.02, f"{b[i]:.2f}", ha="center", fontsize=8)
    for i in range(len(metrics)):
        ax.text(i - bw / 2, a[i] + 0.02, f"{a[i]:.2f}", ha="center", fontsize=9, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels([m[0] for m in metrics])
    ax.set_ylim(0, 1.05); ax.set_ylabel("score (higher = better)")
    ax.set_title("T1 — Drug-target binding vs external DAVIS gold")
    ax.grid(axis="x", visible=False); ax.legend(loc="upper right")
    ax.spines[["top", "right"]].set_visible(False)
    n_abstain = sum(1 for r in dti if r["condition"] == "closed_book" and (r.get("answered") or 0) == 0)
    if n_abstain:
        ax.text(0.0, -0.16, f"({n_abstain} smaller LLM tier(s) refused to predict pKd from SMILES — only binary shown there)",
                transform=ax.transAxes, fontsize=8, color=GREY, style="italic")
    fig.subplots_adjust(bottom=0.18)
    fig.savefig(os.path.join(FIGDIR, "fig_dti.png"), facecolor="white")
    plt.close(fig); print("fig_dti.png")


def fig_a2(rows):
    """A2 target identification: LinkD vs ToolUniverse-agent vs base LLMs."""
    a2 = [r for r in rows if r["scenario"] == "a2_target_id"]
    if not a2:
        return
    order = [("linkd", None, "LinkD", BLUE),
             ("tooluniverse", None, "ToolUniverse-agent\n(OT overall)", ORANGE),
             ("ot_genetics", None, "OpenTargets\ngenetics", PURPLE),
             ("pubmed", None, "PubMed\nliterature", GREEN),
             ("closed_book", "gpt-4.1", "Base LLM\n(gpt-4.1)", GREY)]
    picks = []
    for cond, model, label, color in order:
        cand = [r for r in a2 if r["condition"] == cond and (model is None or r["model"] == model)]
        if cand:
            picks.append((label, color, cand[0]))
    if not picks:
        return
    metrics = [("recall@10", "recall@10"), ("recall@20", "recall@20"),
               ("nDCG@20", "ndcg@20"), ("MRR", "mrr")]
    x = np.arange(len(metrics)); bw = 0.8 / len(picks)
    fig, ax = plt.subplots(figsize=(8.4, 4.7), dpi=300)
    for i, (label, color, r) in enumerate(picks):
        vals = [r.get(k) or 0 for _, k in metrics]
        off = (i - (len(picks) - 1) / 2) * bw
        ax.bar(x + off, vals, bw, color=color, edgecolor="white", label=label)
        for j, v in enumerate(vals):
            ax.text(x[j] + off, v + 0.008, f"{v:.2f}", ha="center", fontsize=7)
    n_dis = max((r.get("n") or 0) for _, _, r in picks)
    ax.set_xticks(x); ax.set_xticklabels([m[0] for m in metrics])
    ax.set_ylabel("score"); ax.set_ylim(0, max(0.85, max(r.get("mrr") or 0 for _, _, r in picks) + 0.1))
    ax.set_title(f"A2 — Target identification vs clinical-validation gold ({n_dis} cancers)")
    ax.grid(axis="x", visible=False); ax.legend(loc="upper left", fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(0.0, -0.15, f"Gold = disease-approved drug targets (OpenTargets). Capability comparison, not fully prospective (n={n_dis}).",
            transform=ax.transAxes, fontsize=7.5, color=GREY, style="italic")
    fig.subplots_adjust(bottom=0.2)
    fig.savefig(os.path.join(FIGDIR, "fig_a2.png"), facecolor="white")
    plt.close(fig); print("fig_a2.png")


_A2_AGENTS = [("linkd", "tools-only", "LinkD", BLUE),
              ("tooluniverse", "opentargets", "ToolUniverse (OT overall)", ORANGE),
              ("ot_genetics", "ot-genetics", "OpenTargets genetics", PURPLE),
              ("pubmed", "literature", "PubMed literature", GREEN),
              ("closed_book", "gpt-4.1", "Base LLM (gpt-4.1)", GREY)]


def fig_a2_scatter(rows):
    """Coverage (recall@20) vs top-hit quality (MRR): where each agent sits."""
    pts = []
    for cond, model, lbl, col in _A2_AGENTS:
        r = next((r for r in rows if r["scenario"] == "a2_target_id"
                  and r["condition"] == cond and r["model"] == model), None)
        if r:
            pts.append((lbl, col, r))
    if not pts:
        return
    fig, ax = plt.subplots(figsize=(7.6, 5.4), dpi=300)
    xmax = max((r.get("recall@20") or 0) for _, _, r in pts)
    # manual label offsets (dx, dy in points, ha) to avoid the LinkD/ToolUniverse overlap
    off = {"LinkD": (-10, 10, "right"), "ToolUniverse (OT overall)": (-10, -16, "right"),
           "OpenTargets genetics": (10, 4, "left"), "PubMed literature": (10, 4, "left"),
           "Base LLM (gpt-4.1)": (0, 12, "center")}
    for lbl, col, r in pts:
        x, y = r.get("recall@20") or 0, r.get("mrr") or 0
        ax.scatter(x, y, s=160, color=col, edgecolor="white", zorder=3)
        dx, dy, ha = off.get(lbl, (8, 4, "left"))
        ax.annotate(lbl, (x, y), xytext=(dx, dy), textcoords="offset points",
                    fontsize=9, color=NAVY, ha=ha)
    ax.set_xlabel("recall@20  →  target-list completeness")
    ax.set_ylabel("MRR  →  top-hit quality")
    ax.set_title("A2 — coverage vs top-hit: agent positioning")
    ax.set_xlim(-0.02, xmax + 0.13)
    ax.set_ylim(0, max(0.8, max((r.get("mrr") or 0) for _, _, r in pts) + 0.12))
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(os.path.join(FIGDIR, "fig_a2_scatter.png"), facecolor="white")
    plt.close(fig); print("fig_a2_scatter.png")


def fig_a2_per_disease():
    """Heatmap of recall@20 per disease per agent (recomputed from predictions)."""
    import glob
    files = sorted(glob.glob(os.path.join(RESULTS, "predictions.a2*.jsonl")))
    if not files:
        return
    preds = [json.loads(l) for l in open(files[-1]) if l.strip()]

    def recall20(rk, gold):
        g = {str(x).upper() for x in gold}
        seen = set(); p = [x.upper() for x in (str(y) for y in rk) if not (x.upper() in seen or seen.add(x.upper()))]
        return len(set(p[:20]) & g) / len(g) if g else 0.0

    diseases, cell = [], {}
    for pr in preds:
        dis = pr["item_id"].replace("a2_target_id-", "").replace("_", " ")
        cell[(dis, (pr["condition"], pr.get("model")))] = recall20(
            (pr.get("parsed") or {}).get("ranking", []), (pr.get("gold") or {}).get("targets", []))
        if dis not in diseases:
            diseases.append(dis)
    labels = [lbl for _, _, lbl, _ in _A2_AGENTS]
    M = np.array([[cell.get((d, (c, m)), 0.0) for d in diseases] for c, m, _, _ in _A2_AGENTS])
    fig, ax = plt.subplots(figsize=(max(9, len(diseases) * 0.42), 3.4), dpi=300)
    im = ax.imshow(M, aspect="auto", cmap="Blues", vmin=0, vmax=max(0.6, float(M.max())))
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=8.5)
    ax.set_xticks(range(len(diseases))); ax.set_xticklabels(diseases, rotation=60, ha="right", fontsize=6.2)
    ax.set_title("A2 — recall@20 per disease per agent")
    fig.colorbar(im, ax=ax, fraction=0.018, pad=0.01, label="recall@20")
    ax.tick_params(length=0)
    fig.tight_layout(); fig.savefig(os.path.join(FIGDIR, "fig_a2_per_disease.png"), facecolor="white")
    plt.close(fig); print("fig_a2_per_disease.png")


if __name__ == "__main__":
    rows = load_rows()
    if not rows:
        print("No results found. Run the grid (run_benchmark.py --out benchmark/results) first.")
        raise SystemExit(0)
    os.makedirs(FIGDIR, exist_ok=True)
    fig_a2(rows); fig_a2_scatter(rows); fig_a2_per_disease(); fig_dti(rows)
    print(f"figures -> {FIGDIR}")
