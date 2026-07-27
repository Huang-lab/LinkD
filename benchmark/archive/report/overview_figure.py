"""
Consolidated benchmark overview (fig_overview.png): LinkD vs other agents/LLMs across
all tasks. Reads results/summary.*.jsonl; one panel per task with its headline metric.

    python3 benchmark/report/overview_figure.py
"""
import glob
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RESULTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
OUT = os.path.join(RESULTS, "figures")
os.makedirs(OUT, exist_ok=True)

BLUE = "#0072B2"; ORANGE = "#E69F00"; GREEN = "#117733"; GREY = "#9aa0a6"; PURPLE = "#CC79A7"
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
                     "savefig.dpi": 300, "pdf.fonttype": 42})

# (scenario, headline metric key, panel title, chance line or None)
PANELS = [
    ("t1_dti", "c_index", "T1 · binding affinity\n(Concordance-Index vs DAVIS)", 0.5),
    ("a2_target_id", "recall@20", "A2 · target identification\n(recall@20 vs OpenTargets)", None),
    ("a3_priority", "ndcg@20", "A3 · target prioritization\n(nDCG@20 vs OpenTargets)", None),
    ("c1_validate", "auroc", "C1 · target-disease validation\n(AUROC, hard decoys)", 0.5),
    ("t2_repurpose", "auroc", "T2 · drug repurposing\n(AUROC vs repoDB)", 0.5),
]
NICE = {"linkd": "LinkD", "linkd_cli": "LinkD", "linkd_tpi": "LinkD-TPI",
        "linkd_evidence": "LinkD-fusion", "linkd_rwe": "LinkD-EHR",
        "tooluniverse": "ToolUniverse(OT)", "ot_assoc": "OpenTargets", "ot_genetics": "OT-genetics",
        "pubmed": "PubMed", "closed_book": "Best LLM"}


def _load():
    rows = []
    for f in glob.glob(os.path.join(RESULTS, "summary.*.jsonl")):
        for line in open(f):
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _color(cond):
    if cond.startswith("linkd"):
        return BLUE
    if cond.startswith("ot") or cond == "tooluniverse":
        return ORANGE
    if cond == "pubmed":
        return GREEN
    return GREY


def build():
    rows = _load()
    fig, axes = plt.subplots(2, 3, figsize=(13.6, 7.6))
    axes = axes.ravel()
    for ax, (scn, key, title, chance) in zip(axes, PANELS):
        srows = [r for r in rows if r["scenario"] == scn and r.get(key) is not None]
        # collapse base LLM to its best tier
        bars = {}
        for r in srows:
            c = r["condition"]
            if c == "closed_book":
                if "closed_book" not in bars or r[key] > bars["closed_book"][0]:
                    bars["closed_book"] = (r[key], f"{NICE[c]}\n({r['model']})")
            else:
                bars[c] = (r[key], NICE.get(c, c))
        items = sorted(bars.items(), key=lambda kv: kv[1][0], reverse=True)
        vals = [v[0] for _, v in items]; labs = [v[1] for _, v in items]
        cols = [_color(c) for c, _ in items]
        y = list(range(len(items)))[::-1]
        ax.barh(y, vals, color=cols, edgecolor="white", height=0.72)
        for yi, v in zip(y, vals):
            ax.text(v + 0.01, yi, f"{v:.2f}", va="center", fontsize=9, color="#222")
        ax.set_yticks(y); ax.set_yticklabels(labs, fontsize=8.5)
        ax.set_xlim(0, 1.0)
        ax.set_title(title, fontsize=10.5, fontweight="bold", pad=6)
        ax.tick_params(axis="x", labelsize=8)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        if chance is not None:
            ax.axvline(chance, color="#c0392b", ls="--", lw=1.1, zorder=0)
            ax.text(chance, len(items) - 0.4, " chance", color="#c0392b", fontsize=7.5, va="top")

    # 6th panel: takeaways
    ax = axes[5]; ax.axis("off")
    ax.text(0.0, 1.0, "Takeaways", fontsize=12, fontweight="bold", va="top", color="#111")
    lines = [
        ("#117733", "LinkD wins where its data is dense:"),
        ("#333333", "  • T1 binding — C-Index 0.819 vs LLM 0.63 (p<1e-4)"),
        ("#333333", "  • A2/A3 cancer target-ID — ≫ genetics / LLM"),
        ("#9c2c2c", "LinkD limited off its data:"),
        ("#333333", "  • C1 fusion ranks prominent disease genes,"),
        ("#333333", "    not the specific drug's target (AUROC 0.47)"),
        ("#333333", "  • T2 EHR ∩ repoDB = 16 pairs (coverage-blocked);"),
        ("#333333", "    LLMs recall indications from memory (~0.74)"),
        ("#555555", "Specialist, not generalist: pair LinkD's"),
        ("#555555", "binding/target signals with an LLM for breadth."),
    ]
    yy = 0.88
    for col, ln in lines:
        ax.text(0.0, yy, ln, fontsize=9 if ln.startswith("  ") else 9.6,
                fontweight=("bold" if not ln.startswith("  ") else "normal"), color=col, va="top")
        yy -= 0.092

    fig.suptitle("LinkD vs other agents / LLMs — drug-discovery benchmark",
                 fontsize=15, fontweight="bold", y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(OUT, "fig_overview.png"), facecolor="white")
    plt.close(fig)
    print("fig_overview.png ->", OUT)


if __name__ == "__main__":
    build()
