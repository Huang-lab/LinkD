"""
Generate the benchmark methodology workflow figure (fig_workflow.png): how the
external-gold, head-to-head agent comparison is run, and the metrics used.

    python3 benchmark/report/workflow_figure.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "figures")
os.makedirs(OUT, exist_ok=True)

NAVY = "#1a1a1a"; BLUE = "#0072B2"; ORANGE = "#E69F00"; GREEN = "#117733"
PURPLE = "#CC79A7"; GREY = "#7a7a7a"; TEAL = "#009E73"; LIGHT = "#f5f6f8"; WHITE = "#ffffff"
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"]})


def rbox(ax, x, y, w, h, fc, ec, lw=1.4, r=0.018):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.002,rounding_size={r}",
                 fc=fc, ec=ec, lw=lw, transform=ax.transAxes, mutation_aspect=0.6, zorder=2))


def arrow(ax, x1, y1, x2, y2, color=NAVY, lw=2.0, ms=14):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=ms,
                 color=color, lw=lw, transform=ax.transAxes, shrinkA=0, shrinkB=0, zorder=1))


def t(ax, x, y, s, size=10, color=NAVY, weight="normal", ha="left", va="center", style="normal"):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va, style=style,
            transform=ax.transAxes, zorder=4)


def build():
    fig = plt.figure(figsize=(13.33, 7.5), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="square,pad=0", fc=WHITE, ec="none", zorder=0,
                                transform=ax.transAxes))
    t(ax, 0.5, 0.955, "LinkD Drug-Discovery Agent Benchmark — Methodology", size=20, weight="bold", ha="center")
    t(ax, 0.5, 0.915, "External-gold, head-to-head comparison of LinkD vs other open-source agents",
      size=12.5, color=GREY, ha="center", style="italic")

    # ---- pipeline: 4 stages left to right ----
    stages = [
        ("1 · EXTERNAL GOLD", BLUE, [
            "TDC DAVIS — experimental Kd", "  (drug-target binding)  → T1",
            "OpenTargets disease-approved", "  drug targets, 25 cancers → A2",
            "→ independent of LinkD's tables"]),
        ("2 · HARMONIZE + CACHE", TEAL, [
            "UniChem  CID → ChEMBL", "gene-symbol mapping", "OpenTargets / PubMed cached",
            "→ offline, reproducible runs"]),
        ("3 · AGENTS (5 strategies)", PURPLE, [
            "LinkD — multi-evidence DB", "ToolUniverse — OpenTargets overall",
            "OpenTargets — genetics-only", "PubMed — literature mining",
            "Base LLMs — GPT-4o-mini/4o/4.1"]),
        ("4 · SCORE → LEADERBOARD", GREEN, [
            "each agent ranks / predicts", "per-item + aggregate metrics",
            "bootstrap CIs · paired tests", "→ leaderboard + figures"]),
    ]
    n = len(stages); cw = 0.215; gap = (0.94 - n * cw) / (n - 1)
    y, h = 0.40, 0.40
    xs = []
    for i, (title, c, lines) in enumerate(stages):
        x = 0.03 + i * (cw + gap); xs.append((x, x + cw))
        rbox(ax, x, y, cw, h, LIGHT, c, lw=1.8)
        rbox(ax, x, y + h - 0.052, cw, 0.052, c, c, lw=0)
        t(ax, x + cw / 2, y + h - 0.026, title, size=10.5, weight="bold", color="white", ha="center")
        ly = y + h - 0.085
        for ln in lines:
            is_out = ln.strip().startswith("→")
            t(ax, x + 0.012, ly, ln, size=8.7, color=(c if is_out else NAVY),
              weight=("bold" if is_out else "normal"))
            ly -= 0.045
    for i in range(n - 1):
        arrow(ax, xs[i][1] + 0.004, y + h / 2, xs[i + 1][0] - 0.004, y + h / 2, lw=2.2, ms=14)

    # ---- two task lanes (bottom) with their metrics ----
    rbox(ax, 0.03, 0.06, 0.45, 0.275, "#eef3f8", BLUE, lw=1.5)
    t(ax, 0.05, 0.305, "Task T1 · Drug-target binding affinity", size=11.5, weight="bold", color=BLUE)
    t(ax, 0.05, 0.272, "Predict pKd for a drug-target pair (vs experimental Kd).", size=9, color=NAVY)
    t(ax, 0.05, 0.245, "Gold: TDC DAVIS · 4,399 LinkD∩DAVIS pairs (53 drugs × 83 kinases)", size=8.6, color=GREY)
    t(ax, 0.05, 0.205, "Metrics:", size=9.3, weight="bold", color=NAVY)
    t(ax, 0.115, 0.205, "Pearson r · Spearman · Concordance-Index · RMSE · binary acc", size=8.8, color=NAVY)
    t(ax, 0.05, 0.135, "Result:", size=9.3, weight="bold", color=GREEN)
    t(ax, 0.105, 0.135, "LinkD C-Index 0.819  »  LLMs (gpt-4.1 r=0.35; smaller refuse)", size=9, color=NAVY)

    rbox(ax, 0.52, 0.06, 0.45, 0.275, "#fbf5ea", ORANGE, lw=1.5)
    t(ax, 0.54, 0.305, "Task A2 · Target identification", size=11.5, weight="bold", color="#9c6f1f")
    t(ax, 0.54, 0.272, "Rank gene targets for a disease (vs approved-drug targets).", size=9, color=NAVY)
    t(ax, 0.54, 0.245, "Gold: OpenTargets disease-approved targets · 25 cancer indications", size=8.6, color=GREY)
    t(ax, 0.54, 0.205, "Metrics:", size=9.3, weight="bold", color=NAVY)
    t(ax, 0.605, 0.205, "recall@10 · recall@20 · nDCG@20 · MRR", size=8.8, color=NAVY)
    t(ax, 0.54, 0.135, "Result:", size=9.3, weight="bold", color=GREEN)
    t(ax, 0.595, 0.135, "Multi-evidence (LinkD ≈ OpenTargets) » genetics-only / literature / LLMs", size=8.6, color=NAVY)

    t(ax, 0.5, 0.025, "All gold auto-built + cached · provider-agnostic · zero-API deterministic agents run offline",
      size=8.6, color=GREY, ha="center", style="italic")

    fig.savefig(os.path.join(OUT, "fig_workflow.png"), dpi=300, facecolor=WHITE)
    plt.close(fig); print("fig_workflow.png ->", OUT)


if __name__ == "__main__":
    build()
