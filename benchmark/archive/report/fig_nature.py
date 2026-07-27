"""
Nature-style multi-panel figure for the LinkD vs LLM vs Combined benchmark.
Width 183 mm (double column), Arial/Helvetica, Okabe-Ito colorblind-safe palette,
0.5 pt spines, 300 dpi raster + editable vector PDF (Type-42 fonts).

  LinkD            = deterministic LinkD data layers
  LLM              = OpenAI gpt-4.1 (closed-book)
  Combined         = LinkD + gpt-4.1 (rank-fusion / score-mean)
  Router (oracle)  = per-task best of {LinkD, LLM} (deployable upper bound)

    python3 benchmark/report/fig_nature.py
"""
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.patches import Patch
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from benchmark.report.performance_report import LAYERS, _load, _best   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "figures")
os.makedirs(OUT, exist_ok=True)

# Okabe-Ito colorblind-safe palette
LINKD = "#0072B2"   # blue
LLM = "#E69F00"     # orange
COMB = "#009E73"    # bluish green
ORCH = "#CC79A7"    # reddish purple
ROUTER = "#444444"  # near-black
# colour by task TYPE (defined a priori in performance_report.LAYERS)
CAT_COL = {"Prediction": "#0072B2", "Mechanism": "#D55E00",
           "Integration": "#009E73", "Knowledge": "#CC79A7"}
# specific (short) task names per layer
TASKNAME = {
    "t1_dti": "Binding\naffinity", "a2_target_id": "Target\nidentification",
    "a3_priority": "Target\nprioritization", "l4_crispr_moa": "CRISPR→\nMoA target",
    "c1_validate": "Evidence\nfusion", "l2_binding_moa": "Binding→\nMoA target",
    "l3_selectivity": "Drug\nselectivity",
}

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 7, "axes.linewidth": 0.5, "axes.labelsize": 7, "axes.titlesize": 7.5,
    "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "legend.fontsize": 6.5,
    "xtick.major.width": 0.5, "ytick.major.width": 0.5, "xtick.major.size": 2.5,
    "ytick.major.size": 2.5, "savefig.dpi": 300, "pdf.fonttype": 42, "ps.fonttype": 42,
})


def _panel(ax, letter):
    ax.text(-0.02, 1.12, letter, transform=ax.transAxes, fontsize=9, fontweight="bold",
            va="top", ha="right")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def _data():
    by = _load()
    rows = []
    for lid, scn, feat, task, gold, mkey, sec, hib, typ in LAYERS:
        srows = by.get(scn, [])
        if not srows:
            continue
        ld = _best(srows, mkey, lambda r: r["condition"].startswith("linkd"))
        lm = _best(srows, mkey, lambda r: r["condition"] == "closed_book")     # best LLM, any model
        cb = _best(srows, mkey, lambda r: r["condition"] == "combined")        # best Combined, any model
        ob = _best(srows, mkey, lambda r: r["condition"] == "orchestrator")    # best Orchestrator
        if not (ld and lm and cb):
            continue
        rows.append(dict(lid=lid, feat=feat.replace(" ", "\n", 1), cat=typ, mkey=mkey,
                         name=TASKNAME[scn], llm_model=lm.get("model", "?"),
                         L=ld[mkey], E=lm[mkey], C=cb[mkey], R=(ob[mkey] if ob else None),
                         O=max(ld[mkey], lm[mkey])))
    return rows


def build():
    D = _data()
    lids = [d["lid"] for d in D]
    L = np.array([d["L"] for d in D]); E = np.array([d["E"] for d in D])
    C = np.array([d["C"] for d in D]); O = np.array([d["O"] for d in D])
    R = np.array([d["R"] if d["R"] is not None else np.nan for d in D])   # Orchestrator

    fig = plt.figure(figsize=(7.2, 9.7))   # 183 mm wide (full page)
    gs = gridspec.GridSpec(4, 2, height_ratios=[1.0, 0.92, 0.92, 0.74], hspace=0.78, wspace=0.28,
                           left=0.08, right=0.965, top=0.89, bottom=0.055)
    names = [f"{d['lid']}\n{d['name']}" for d in D]

    # ---- a: per-task grouped bars ----
    ax = fig.add_subplot(gs[0, :]); _panel(ax, "a")
    x = np.arange(len(D)); w = 0.2
    ax.bar(x - 1.5 * w, L, w, color=LINKD, label="LinkD", linewidth=0)
    ax.bar(x - 0.5 * w, E, w, color=LLM, label="Best LLM", linewidth=0)
    ax.bar(x + 0.5 * w, C, w, color=COMB, label="Combined (blend)", linewidth=0)
    ax.bar(x + 1.5 * w, R, w, color=ORCH, label="Orchestrator (LLM calls LinkD)", linewidth=0)
    ax.set_xticks(x); ax.set_xticklabels(names, fontsize=5.6)
    ax.set_ylim(0, 1.0); ax.set_ylabel("headline metric")
    ax.set_title("Per-task performance across 7 manuscript-aligned tasks", pad=6)
    ax.axhline(0.5, color="#bbb", lw=0.5, ls=(0, (3, 3)), zorder=0)
    ax.margins(x=0.01)

    # ---- b: category means ----
    ax = fig.add_subplot(gs[1, 0]); _panel(ax, "b")
    cats = ["Prediction", "Mechanism", "Integration", "Knowledge"]
    cm = {c: ([], [], [], []) for c in cats}
    for d in D:
        cm[d["cat"]][0].append(d["L"]); cm[d["cat"]][1].append(d["E"])
        cm[d["cat"]][2].append(d["C"]); cm[d["cat"]][3].append(d["R"] if d["R"] is not None else np.nan)
    xb = np.arange(len(cats)); wb = 0.2
    mL = [np.nanmean(cm[c][0]) for c in cats]; mE = [np.nanmean(cm[c][1]) for c in cats]
    mC = [np.nanmean(cm[c][2]) for c in cats]; mR = [np.nanmean(cm[c][3]) for c in cats]
    ax.bar(xb - 1.5 * wb, mL, wb, color=LINKD, linewidth=0)
    ax.bar(xb - 0.5 * wb, mE, wb, color=LLM, linewidth=0)
    ax.bar(xb + 0.5 * wb, mC, wb, color=COMB, linewidth=0)
    ax.bar(xb + 1.5 * wb, mR, wb, color=ORCH, linewidth=0)
    ax.set_xticks(xb); ax.set_xticklabels(cats, fontsize=5.8)
    ax.set_ylim(0, 1.0); ax.set_ylabel("mean metric")
    ax.set_title("Performance by task category", pad=4)

    # ---- c: overall average + oracle ceiling ----
    ax = fig.add_subplot(gs[1, 1]); _panel(ax, "c")
    names = ["LinkD", "Best\nLLM", "Combined", "Orchestr.", "Router\n(oracle)"]
    series = [L, E, C, R, O]
    means = [np.nanmean(a) for a in series]
    sems = [np.nanstd(a, ddof=1) / np.sqrt(np.sum(~np.isnan(a))) for a in series]
    cols = [LINKD, LLM, COMB, ORCH, ROUTER]
    ax.bar(range(5), means, 0.66, color=cols, yerr=sems, capsize=2,
           error_kw=dict(lw=0.6, capthick=0.6), linewidth=0)
    for i, m in enumerate(means):
        ax.text(i, m + sems[i] + 0.02, f"{m:.3f}", ha="center", fontsize=5.6)
    ax.set_xticks(range(5)); ax.set_xticklabels(names, fontsize=5.4)
    ax.set_ylim(0, 0.85); ax.set_ylabel("task-mean metric")
    ax.set_title("Overall (mean ± s.e.m., n = 7)", pad=4)
    ax.axhline(np.nanmean(O), color=ROUTER, lw=0.6, ls=(0, (3, 3)), zorder=0)

    # ---- d: complementarity scatter (LinkD vs LLM) ----
    ax = fig.add_subplot(gs[2, 0]); _panel(ax, "d")
    ax.plot([0, 1], [0, 1], color="#999", lw=0.6, ls="--", zorder=1)
    for d in D:
        ax.scatter(d["L"], d["E"], s=26, color=CAT_COL[d["cat"]], edgecolor="white",
                   linewidth=0.4, zorder=3)
        ax.annotate(d["lid"], (d["L"], d["E"]), fontsize=5, xytext=(2.5, 2.5),
                    textcoords="offset points", color="#333")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel("LinkD score"); ax.set_ylabel("best-LLM score")
    ax.set_title("Complementarity (above line: LLM better)", pad=4)
    handles = [plt.Line2D([0], [0], marker="o", ls="", mfc=CAT_COL[c], mec="white",
                          ms=4.5, label=c.replace("\n", " ")) for c in cats]
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=5, handletextpad=0.3,
              borderpad=0.2, labelspacing=0.25)

    # ---- e: fusion lift vs method gap ----
    ax = fig.add_subplot(gs[2, 1]); _panel(ax, "e")
    gap = np.abs(L - E); lift = C - O
    ax.axhline(0, color="#999", lw=0.6, ls="--")
    for d, g, lf in zip(D, gap, lift):
        ax.scatter(g, lf, s=26, color=CAT_COL[d["cat"]], edgecolor="white", linewidth=0.4, zorder=3)
        ax.annotate(d["lid"], (g, lf), fontsize=5, xytext=(2.5, 2.5), textcoords="offset points",
                    color="#333")
    if len(gap) > 2:
        b, a = np.polyfit(gap, lift, 1)
        xs = np.linspace(gap.min(), gap.max(), 20)
        ax.plot(xs, a + b * xs, color="#666", lw=0.7, zorder=2)
    ax.set_xlabel("|LinkD − LLM|  (method disagreement)")
    ax.set_ylabel("fusion lift  (Combined − best single)")
    ax.set_title("Fusion helps when methods are balanced", pad=4)

    # ---- f: tasks x methods heatmap ----
    ax = fig.add_subplot(gs[3, :]); _panel(ax, "f")
    M = np.vstack([L, E, C, R])                     # 4 methods x ntasks
    nm = M.shape[0]
    im = ax.imshow(M, aspect="auto", cmap="YlGnBu", vmin=0.2, vmax=0.95)
    ax.set_yticks(range(nm)); ax.set_yticklabels(["LinkD", "Best LLM", "Combined", "Orchestrator"],
                                                 fontsize=6.5)
    ax.set_xticks(range(len(D)))
    ax.set_xticklabels([f"{d['lid']} {d['name'].replace(chr(10), ' ')}" for d in D],
                       rotation=33, ha="right", fontsize=5.6)
    for i in range(nm):
        for j in range(len(D)):
            if not np.isnan(M[i, j]):
                ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", fontsize=5.6,
                        color=("white" if M[i, j] > 0.62 else "#222"))
    ax.set_xticks(np.arange(-.5, len(D), 1), minor=True)
    ax.set_yticks(np.arange(-.5, nm, 1), minor=True)
    ax.grid(which="minor", color="white", lw=0.8); ax.tick_params(which="minor", length=0)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.set_title("Metric heatmap (all tasks × methods)", pad=4)
    cb = fig.colorbar(im, ax=ax, fraction=0.018, pad=0.012)
    cb.set_label("metric", fontsize=6); cb.ax.tick_params(labelsize=5.5, width=0.5)
    cb.outline.set_linewidth(0.5)

    fig.suptitle("LinkD vs best LLM vs Combined vs Orchestrator across drug-discovery tasks",
                 fontsize=9, fontweight="bold", y=0.965)
    leg_h = [Patch(color=LINKD, label="LinkD"), Patch(color=LLM, label="Best LLM"),
             Patch(color=COMB, label="Combined (blend)"),
             Patch(color=ORCH, label="Orchestrator (LLM calls LinkD)")]
    fig.legend(handles=leg_h, loc="upper center", bbox_to_anchor=(0.5, 0.935), ncol=4,
               frameon=False, handlelength=1.1, columnspacing=1.3, fontsize=6)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"fig_nature.{ext}"), facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print("fig_nature.png + fig_nature.pdf ->", OUT)


if __name__ == "__main__":
    build()
