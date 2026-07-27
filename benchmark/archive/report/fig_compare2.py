"""
Compact 2-panel figure for the core comparison (LinkD vs LLM vs Combined):
  a — per-task performance (all 9 tasks, named)
  b — overall mean ± s.e.m. with the router (oracle) ceiling
Nature-spec: 183 mm wide, Arial, Okabe-Ito palette, 300 dpi + vector PDF.

    python3 benchmark/report/fig_compare2.py
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
from benchmark.report.fig_nature import _data, _panel, LINKD, LLM, COMB, ORCH, ROUTER, OUT   # noqa: E402


def build():
    D = _data()
    lids = [f"{d['lid']}\n{d['name']}" for d in D]
    L = np.array([d["L"] for d in D]); E = np.array([d["E"] for d in D])
    C = np.array([d["C"] for d in D]); O = np.array([d["O"] for d in D])
    R = np.array([d["R"] if d["R"] is not None else np.nan for d in D])   # Orchestrator

    fig = plt.figure(figsize=(7.2, 3.0))   # 183 x 76 mm
    gs = gridspec.GridSpec(1, 3, width_ratios=[2.25, 0.05, 1.0], wspace=0.05,
                           left=0.075, right=0.975, top=0.80, bottom=0.24)

    # a — per-task bars
    ax = fig.add_subplot(gs[0, 0]); _panel(ax, "a")
    x = np.arange(len(D)); w = 0.2
    ax.bar(x - 1.5 * w, L, w, color=LINKD, linewidth=0)
    ax.bar(x - 0.5 * w, E, w, color=LLM, linewidth=0)
    ax.bar(x + 0.5 * w, C, w, color=COMB, linewidth=0)
    ax.bar(x + 1.5 * w, R, w, color=ORCH, linewidth=0)
    ax.set_xticks(x); ax.set_xticklabels(lids, fontsize=5.4)
    ax.set_ylim(0, 1.0); ax.set_ylabel("headline metric")
    ax.set_title("Per-task performance", pad=4)
    ax.axhline(0.5, color="#bbb", lw=0.5, ls=(0, (3, 3)), zorder=0); ax.margins(x=0.01)

    # b — overall + oracle
    ax = fig.add_subplot(gs[0, 2]); _panel(ax, "b")
    names = ["LinkD", "Best\nLLM", "Comb.", "Orch.", "Router\n(oracle)"]
    series = [L, E, C, R, O]
    means = [np.nanmean(a) for a in series]
    sems = [np.nanstd(a, ddof=1) / np.sqrt(np.sum(~np.isnan(a))) for a in series]
    ax.bar(range(5), means, 0.68, color=[LINKD, LLM, COMB, ORCH, ROUTER], yerr=sems, capsize=2,
           error_kw=dict(lw=0.6, capthick=0.6), linewidth=0)
    for i, m in enumerate(means):
        ax.text(i, m + sems[i] + 0.02, f"{m:.3f}", ha="center", fontsize=5.4)
    ax.set_xticks(range(5)); ax.set_xticklabels(names, fontsize=5.2)
    ax.set_ylim(0, 0.85); ax.set_ylabel("task-mean metric")
    ax.set_title("Overall (mean ± s.e.m., n = 9)", pad=4)
    ax.axhline(np.nanmean(O), color=ROUTER, lw=0.6, ls=(0, (3, 3)), zorder=0)

    leg_h = [Patch(color=LINKD, label="LinkD"), Patch(color=LLM, label="Best LLM"),
             Patch(color=COMB, label="Combined (blend)"),
             Patch(color=ORCH, label="Orchestrator (LLM calls LinkD)")]
    fig.legend(handles=leg_h, loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=4,
               frameon=False, handlelength=1.1, columnspacing=1.3, fontsize=6)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"fig_compare2.{ext}"), facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print("fig_compare2.png + fig_compare2.pdf ->", OUT)


if __name__ == "__main__":
    build()
