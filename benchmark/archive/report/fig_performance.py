"""
fig_performance.png — LinkD vs best base-LLM across the 10 feature-isolated tasks.
Diverging bars = LinkD(headline) − best-LLM(headline); green = LinkD ahead (prediction
tasks), red = LLM ahead (memorized-fact / ontology-blocked tasks). Reads summaries.

    python3 benchmark/report/fig_performance.py
"""
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from benchmark.report.performance_report import LAYERS, _load, _best   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "figures")
os.makedirs(OUT, exist_ok=True)
GREEN = "#1a9850"; RED = "#d73027"; BLUE = "#0072B2"; GREY = "#888"
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
                     "savefig.dpi": 300, "pdf.fonttype": 42})


def build():
    by_scn = _load()
    rows = []
    for lid, scn, feat, task, gold, mkey, _sec, _hib in LAYERS:
        srows = by_scn.get(scn, [])
        if not srows:
            continue
        linkd = _best(srows, mkey, lambda r: r["condition"].startswith("linkd"))
        llm = _best(srows, mkey, lambda r: r["condition"] == "closed_book")
        if not linkd or not llm:
            continue
        rows.append((lid, feat, mkey, linkd[mkey], llm[mkey], linkd[mkey] - llm[mkey]))
    rows.sort(key=lambda r: r[5])           # most LLM-favoured at bottom

    fig, ax = plt.subplots(figsize=(11.5, 6.4))
    y = range(len(rows))
    deltas = [r[5] for r in rows]
    cols = [GREEN if d > 0 else RED for d in deltas]
    ax.barh(list(y), deltas, color=cols, edgecolor="white", height=0.66, zorder=3)
    ax.axvline(0, color="#333", lw=1.2, zorder=2)
    for i, (lid, feat, mkey, lv, ev, d) in enumerate(rows):
        ax.text(d + (0.012 if d >= 0 else -0.012), i, f"{d:+.2f}", va="center",
                ha="left" if d >= 0 else "right", fontsize=8.5, color="#222", zorder=4)
        # left-side label: LinkD vs LLM absolute, with metric
        ax.text(-0.86, i, f"{lid} · {feat}", va="center", ha="left", fontsize=9, color="#111")
        ax.text(0.86, i, f"LinkD {lv:.2f} / LLM {ev:.2f}  ({mkey})", va="center", ha="right",
                fontsize=8, color=GREY)
    ax.set_yticks([]); ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.set_xlim(-0.9, 0.9)
    ax.set_xlabel("LinkD − best base-LLM   (headline metric, higher = LinkD better)", fontsize=10)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="x", labelsize=8)
    ax.set_title("LinkD vs best base-LLM across 10 feature-isolated tasks", fontsize=14,
                 fontweight="bold", pad=30)
    ax.text(0.0, 1.045, "green = LinkD wins (prediction LLMs can't memorize)   ·   "
            "red = LLM wins (memorized drug facts / ontology-blocked)",
            transform=ax.transAxes, ha="center", fontsize=9.5, color="#444")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_performance.png"), facecolor="white")
    plt.close(fig)
    print("fig_performance.png ->", OUT, f"({len(rows)} tasks)")


if __name__ == "__main__":
    build()
