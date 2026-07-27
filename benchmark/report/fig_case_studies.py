"""
One figure per compositional case study: panel a = the orchestrator's autonomous LinkD
tool-call workflow (with the key value from each call), panel b = the LinkD evidence that
drove the verdict. Data is fetched deterministically from the LinkD CLI, so the figures are
reproducible regardless of the agent's (stochastic) run.

    python3 benchmark/report/fig_case_studies.py
"""
import json
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from benchmark.conditions.base import cli_json   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "figures")
os.makedirs(OUT, exist_ok=True)
LINKD = "#0072B2"; ORCH = "#CC79A7"; GREEN = "#117733"; GREY = "#9aa0a6"; ORANGE = "#E69F00"
NAVY = "#1a1a1a"; RED = "#9c2c2c"
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
                     "font.size": 7, "axes.linewidth": 0.5, "savefig.dpi": 300, "pdf.fonttype": 42})


def _cli(*a):
    d, _ = cli_json(*[str(x) for x in a])
    return d or {}


def _panel(ax, letter):
    ax.text(-0.06, 1.06, letter, transform=ax.transAxes, fontsize=9, fontweight="bold",
            va="top", ha="right")


def _flow(ax, title, steps, verdict, override):
    """Vertical workflow: query -> tool calls (label + key value) -> cross-check -> verdict."""
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off"); ax.set_title(title, fontsize=8, pad=2)
    n = len(steps)
    top, bot = 0.97, 0.06
    ys = np.linspace(top, bot, n + 2)
    # query
    _box(ax, ys[0], "QUERY (free-form)", LINKD, "white", bold=True)
    for i, (tool, val) in enumerate(steps):
        _box(ax, ys[i + 1], f"call  {tool}", "#eef3f8", NAVY, sub=val, ec=LINKD)
        _arrow(ax, ys[i] - 0.028, ys[i + 1] + 0.028)
    _arrow(ax, ys[n] - 0.028, ys[n + 1] + 0.028)
    _box(ax, ys[n + 1], verdict, GREEN, "white", bold=True, sub=override)


def _box(ax, y, text, fc, tc, sub=None, ec="none", bold=False):
    h = 0.052 if not sub else 0.076
    ax.add_patch(FancyBboxPatch((0.06, y - h / 2), 0.88, h, boxstyle="round,pad=0.004,rounding_size=0.02",
                 fc=fc, ec=ec, lw=1.0, transform=ax.transAxes, mutation_aspect=0.5, zorder=2))
    ax.text(0.5, y + (0.012 if sub else 0), text, ha="center", va="center", fontsize=6.6,
            color=tc, fontweight=("bold" if bold else "normal"), transform=ax.transAxes, zorder=3)
    if sub:
        ax.text(0.5, y - 0.018, sub, ha="center", va="center", fontsize=5.8,
                color=(tc if tc != "white" else "white"), style="italic", transform=ax.transAxes, zorder=3)


def _arrow(ax, y1, y2):
    ax.add_patch(FancyArrowPatch((0.5, y1), (0.5, y2), arrowstyle="-|>", mutation_scale=8,
                 color="#555", lw=1.0, transform=ax.transAxes, shrinkA=0, shrinkB=0, zorder=1))


def _save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), facecolor="white", bbox_inches="tight")
    plt.close(fig); print(f"{name}.png + .pdf ->", OUT)


def case1():
    ev = _cli("evidence", "CHEMBL941", "ABL1", "--icd", "C92")
    ss = ev.get("sub_scores", {})
    fig = plt.figure(figsize=(7.2, 3.3))
    axA = fig.add_axes([0.02, 0.05, 0.40, 0.86]); _panel(axA, "a")
    _flow(axA, "Orchestrator workflow", [
        ("binding(ABL1)", "pKd 8.90"), ("drug-info", "selectivity 0.35"),
        ("ehr(C92)", "0 rows → missing"), ("evidence", "final 0.69 · strong")],
        "VERDICT: strongly support", "EHR treated as missing, not negative")
    axB = fig.add_axes([0.55, 0.20, 0.42, 0.66]); _panel(axB, "b")
    lab = {"predicted_binding": "binding", "functional_crispr": "CRISPR", "target_priority": "TPI",
           "clinical_phase": "clinical phase", "genetic_causality": "genetic", "drug_selectivity": "selectivity"}
    items = sorted(((lab.get(k, k), v) for k, v in ss.items()), key=lambda x: x[1])
    y = range(len(items))
    axB.barh(list(y), [v for _, v in items], color=LINKD, height=0.66)
    for yi, (_, v) in zip(y, items):
        axB.text(v + 0.01, yi, f"{v:.2f}", va="center", fontsize=6)
    axB.set_yticks(list(y)); axB.set_yticklabels([k for k, _ in items], fontsize=6.5)
    axB.set_xlim(0, 1.0); axB.axvline(ev.get("final_score", 0), color=GREEN, ls="--", lw=1)
    axB.text(ev.get("final_score", 0), len(items) - 0.4, f" final {ev.get('final_score'):.2f}",
             color=GREEN, fontsize=6, va="top")
    for s in ("top", "right"):
        axB.spines[s].set_visible(False)
    axB.set_title(f"Multi-evidence: imatinib–ABL1–CML (coverage {ev.get('coverage')})", fontsize=7.5, pad=3)
    axB.set_xlabel("evidence sub-score", fontsize=6.5)
    fig.suptitle("Case 1 · Imatinib for chronic myeloid leukemia", fontsize=9, fontweight="bold", y=1.0)
    _save(fig, "fig_case1")


def case2():
    tg = _cli("targets-for-drug", "CHEMBL553", "--limit", "8").get("targets", [])
    names = [t["Target"].replace("_HUMAN", "") for t in tg]
    pkd = [t["aff_local"] for t in tg]
    fig = plt.figure(figsize=(7.2, 3.3))
    axA = fig.add_axes([0.02, 0.05, 0.40, 0.86]); _panel(axA, "a")
    _flow(axA, "Orchestrator workflow", [
        ("targets-for-drug", "EGFR top + off-targets"), ("drug-info", "selectivity 0.33"),
        ("binding(EGFR)", "pKd 9.51"), ("evidence(C34)", "final 0.70 · strong")],
        "VERDICT: EGFR-directed", "OVERRIDE LinkD 'Highly Selective' label")
    axB = fig.add_axes([0.55, 0.18, 0.42, 0.68]); _panel(axB, "b")
    yy = range(len(names))[::-1]
    cols = [ORANGE if n == "EGFR" else GREY for n in names]
    axB.barh(list(yy), pkd, color=cols, height=0.7)
    for yi, p, n in zip(yy, pkd, names):
        axB.text(p + 0.03, yi, f"{p:.2f}", va="center", fontsize=6,
                 color=(NAVY if n == "EGFR" else "#666"))
    axB.set_yticks(list(yy)); axB.set_yticklabels(names, fontsize=6.5)
    axB.set_xlim(8.4, 9.8)
    for s in ("top", "right"):
        axB.spines[s].set_visible(False)
    axB.set_title("Erlotinib predicted binding (pKd): EGFR is top,\nbut off-target kinases sit close",
                  fontsize=7.2, pad=3)
    axB.set_xlabel("predicted pKd", fontsize=6.5)
    fig.suptitle("Case 2 · Erlotinib mechanism + EGFR support in lung cancer",
                 fontsize=9, fontweight="bold", y=1.0)
    _save(fig, "fig_case2")


def case3():
    cands = ["BRAF", "KIT", "KDR"]
    pkd, fin = [], []
    for g in cands:
        ev = _cli("evidence", "CHEMBL1229517", g, "--icd", "C43")
        pkd.append(ev.get("sources", {}).get("binding_affinity", {}).get("pkd") or 0)
        fin.append(ev.get("final_score") or 0)
    fig = plt.figure(figsize=(7.2, 3.3))
    axA = fig.add_axes([0.02, 0.05, 0.40, 0.86]); _panel(axA, "a")
    _flow(axA, "Orchestrator workflow", [
        ("targets-for-disease(C43)", "KDR,KIT,…,BRAF"), ("binding+evidence ×3", "BRAF / KIT / KDR"),
        ("drug-info", "selectivity"), ("compare candidates", "rank by evidence")],
        "VERDICT: BRAF strong target", "OVERRIDE noisy 'targets-for-drug' list")
    axB = fig.add_axes([0.55, 0.20, 0.42, 0.66]); _panel(axB, "b")
    x = np.arange(len(cands)); w = 0.36
    axB.bar(x - w / 2, np.array(pkd) / 10, w, color=LINKD, label="pKd ÷10")
    axB.bar(x + w / 2, fin, w, color=ORCH, label="evidence final_score")
    for xi, p, f in zip(x, pkd, fin):
        axB.text(xi - w / 2, p / 10 + 0.01, f"{p:.1f}", ha="center", fontsize=5.8, color=LINKD)
        axB.text(xi + w / 2, f + 0.01, f"{f:.2f}", ha="center", fontsize=5.8, color=ORCH)
    axB.set_xticks(x); axB.set_xticklabels([f"{c}\n{'(picked)' if c == 'BRAF' else ''}" for c in cands], fontsize=6.5)
    axB.set_ylim(0, 0.95); axB.legend(fontsize=5.6, frameon=False, loc="upper right")
    for s in ("top", "right"):
        axB.spines[s].set_visible(False)
    axB.set_title("Vemurafenib → melanoma: candidate target comparison", fontsize=7.2, pad=3)
    fig.suptitle("Case 3 · Melanoma — disease-first target triage",
                 fontsize=9, fontweight="bold", y=1.0)
    _save(fig, "fig_case3")


if __name__ == "__main__":
    case1(); case2(); case3()
