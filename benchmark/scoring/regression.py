"""Regression + ranking metrics for the DTI task (T1): Pearson, Spearman, RMSE,
Concordance Index (standard for binding-affinity prediction), plus binary accuracy."""
from __future__ import annotations
import math
from typing import Dict, List


def score_dti(item, pred) -> Dict:
    gv = item.gold.get("value"); gl = item.gold.get("label")
    pv = pred.parsed.get("value"); pl = pred.parsed.get("label")
    out = {"dti": True, "error": bool(pred.error), "abstained": bool(pred.parsed.get("abstained")),
           "pred_value": pv, "gold_value": gv,
           "binary_correct": int(pl is not None and pl == gl), "predicted": pl, "gold": gl}
    if pl is not None:  # binary per-item signal for paired McNemar (omitted when abstained)
        out["right_action"] = int(pl == gl)
    return out


def _pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    dx = math.sqrt(sum((a - mx) ** 2 for a in xs)); dy = math.sqrt(sum((b - my) ** 2 for b in ys))
    return cov / (dx * dy) if dx and dy else 0.0


def _ranks(x):
    order = sorted(range(len(x)), key=lambda i: x[i]); r = [0.0] * len(x)
    for rank, i in enumerate(order):
        r[i] = rank
    return r


def _spearman(xs, ys):
    return _pearson(_ranks(xs), _ranks(ys))


def _rmse(xs, ys):
    n = len(xs)
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(xs, ys)) / n) if n else 0.0


def _concordance_index(gold, pred):
    """Fraction of comparable pairs ranked in the correct order (ties=0.5)."""
    s = w = 0.0
    n = len(gold)
    for i in range(n):
        for j in range(i + 1, n):
            if gold[i] == gold[j]:
                continue
            w += 1
            hi, lo = (i, j) if gold[i] > gold[j] else (j, i)
            if pred[hi] > pred[lo]:
                s += 1
            elif pred[hi] == pred[lo]:
                s += 0.5
    return s / w if w else 0.0


def aggregate_dti(scored: List[Dict]) -> Dict:
    rel = [s for s in scored if s.get("dti") and not s.get("error")
           and s.get("pred_value") is not None and s.get("gold_value") is not None]
    answered = len(rel)
    total = len([s for s in scored if s.get("dti")])
    out = {"n": total, "answered": answered, "abstained": sum(1 for s in scored if s.get("abstained"))}
    if answered >= 2:
        pv = [float(s["pred_value"]) for s in rel]; gv = [float(s["gold_value"]) for s in rel]
        out["pearson"] = round(_pearson(pv, gv), 3)
        out["spearman"] = round(_spearman(pv, gv), 3)
        out["rmse"] = round(_rmse(pv, gv), 3)
        out["c_index"] = round(_concordance_index(gv, pv), 3)
    binr = [s for s in scored if s.get("dti") and not s.get("error") and s.get("predicted") is not None]
    if binr:
        out["binary_acc"] = round(sum(s["binary_correct"] for s in binr) / len(binr), 3)
    return out
