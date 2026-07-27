"""
fig_combined.png — LinkD vs LLM (gpt-4.1) vs Combined (LinkD+gpt-4.1) across the 10
feature-isolated tasks. Grouped horizontal bars on each task's headline metric.

    python3 benchmark/report/fig_combined.py
"""
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from benchmark.report.performance_report import LAYERS, _load, _best   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "figures")
os.makedirs(OUT, exist_ok=True)
BLUE = "#0072B2"; GREY = "#9aa0a6"; PURPLE = "#7B3FA0"
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
                     "savefig.dpi": 300, "pdf.fonttype": 42})


def build():
    by_scn = _load()
    labels, L, E, C = [], [], [], []
    for lid, scn, feat, task, gold, mkey, _s, _h in LAYERS:
        rows = by_scn.get(scn, [])
        if not rows:
            continue
        linkd = _best(rows, mkey, lambda r: r["condition"].startswith("linkd"))
        llm = _best(rows, mkey, lambda r: r["condition"] == "closed_book" and r["model"] == "gpt-4.1") \
            or _best(rows, mkey, lambda r: r["condition"] == "closed_book")
        comb = _best(rows, mkey, lambda r: r["condition"] == "combined")
        labels.append(f"{lid} · {feat}\n({mkey})")
        L.append(linkd[mkey] if linkd else 0)
        E.append(llm[mkey] if llm else 0)
        C.append(comb[mkey] if comb else 0)

    y = np.arange(len(labels)); h = 0.26
    fig, ax = plt.subplots(figsize=(11.5, 7.2))
    ax.barh(y + h, L, h, color=BLUE, label="LinkD", zorder=3)
    ax.barh(y, E, h, color=GREY, label="LLM (gpt-4.1)", zorder=3)
    ax.barh(y - h, C, h, color=PURPLE, label="Combined (LinkD+gpt-4.1)", zorder=3)
    for yi, v in zip(y + h, L):
        ax.text(v + 0.008, yi, f"{v:.2f}", va="center", fontsize=7, color=BLUE)
    for yi, v in zip(y, E):
        ax.text(v + 0.008, yi, f"{v:.2f}", va="center", fontsize=7, color="#555")
    for yi, v in zip(y - h, C):
        ax.text(v + 0.008, yi, f"{v:.2f}", va="center", fontsize=7, fontweight="bold", color=PURPLE)
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.0); ax.set_xlabel("headline metric (higher = better)", fontsize=10)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(loc="lower right", fontsize=9, framealpha=0.9)
    ax.set_title("LinkD vs LLM vs Combined (LinkD + LLM) across 10 feature-isolated tasks",
                 fontsize=13.5, fontweight="bold", pad=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_combined.png"), facecolor="white")
    plt.close(fig)
    print("fig_combined.png ->", OUT)


if __name__ == "__main__":
    build()
