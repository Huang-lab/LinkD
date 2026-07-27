"""Nature-like plotting defaults and panel exporters."""
from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

from . import paths

NATURE = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 9,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "axes.spines.top": False,
    "axes.spines.right": False,
}

PALETTE = {
    "linkd": "#C44E52",
    "oncogene": "#E74C3C",
    "tsg": "#3498DB",
    "dual": "#27AE60",
    "known": "#E74C3C",
    "novel": "#3498DB",
    "affinity": "#4C72B0",
    "selectivity": "#DD8452",
    "combined": "#C44E52",
}


def apply() -> None:
    mpl.rcParams.update(NATURE)
    paths.ensure_output_dirs()


def save_panel(fig: plt.Figure, name: str, data: pd.DataFrame | None = None) -> dict:
    """Save PDF+PNG and optional source CSV. Returns output paths."""
    paths.ensure_output_dirs()
    pdf = paths.OUTPUT_FIG / f"{name}.pdf"
    png = paths.OUTPUT_FIG / f"{name}.png"
    fig.savefig(pdf, bbox_inches="tight")
    fig.savefig(png, bbox_inches="tight")
    out = {"pdf": pdf, "png": png}
    if data is not None:
        csv = paths.OUTPUT_DATA / f"{name}.csv"
        data.to_csv(csv, index=False)
        out["csv"] = csv
    return out
