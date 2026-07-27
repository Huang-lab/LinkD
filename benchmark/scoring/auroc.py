"""
Shared scorer for binary-discrimination tasks (C1 integrative validation, B4/T2
repurposing, B5 safety): an agent emits a continuous score per (drug,target,disease)
or (drug,disease) item; gold is a 0/1 label. We report AUROC + AUPRC (+ bootstrap CI).
Pure stdlib.
"""
from __future__ import annotations
from typing import Dict, List


def score_binary(item, pred) -> Dict:
    """Record (score, label) for one item. score may be None when the agent abstains."""
    label = item.gold.get("label")
    score = pred.parsed.get("score")
    out = {"binary_score": True, "error": bool(pred.error),
           "score": (None if score is None else float(score)),
           "label": (None if label is None else int(label))}
    return out


def _auroc(scores: List[float], labels: List[int]) -> float:
    pos = [s for s, l in zip(scores, labels) if l == 1]
    neg = [s for s, l in zip(scores, labels) if l == 0]
    if not pos or not neg:
        return 0.0
    wins = 0.0
    for p in pos:
        for n in neg:
            wins += 1.0 if p > n else (0.5 if p == n else 0.0)
    return wins / (len(pos) * len(neg))


def _auprc(scores: List[float], labels: List[int]) -> float:
    """Average precision (area under precision-recall), interpolated stepwise."""
    order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    P = sum(labels)
    if P == 0:
        return 0.0
    tp = 0
    ap = 0.0
    for rank, i in enumerate(order, 1):
        if labels[i] == 1:
            tp += 1
            ap += tp / rank          # precision at this recall step
    return ap / P


def aggregate_auroc(scored: List[Dict]) -> Dict:
    rel = [s for s in scored if s.get("binary_score") and not s.get("error")
           and s.get("score") is not None and s.get("label") is not None]
    n = len([s for s in scored if s.get("binary_score")])
    answered = len(rel)
    pos = sum(1 for s in rel if s["label"] == 1)
    out = {"n": n, "answered": answered, "pos": pos, "neg": answered - pos}
    if pos and (answered - pos):
        scores = [s["score"] for s in rel]; labels = [s["label"] for s in rel]
        out["auroc"] = round(_auroc(scores, labels), 3)
        out["auprc"] = round(_auprc(scores, labels), 3)
        out["auroc_ci"] = _auroc_ci(scores, labels)
    return out


def _auroc_ci(scores, labels, n_boot: int = 1000, alpha: float = 0.05):
    """Stratified bootstrap CI for AUROC (resample positives and negatives)."""
    import random
    rng = random.Random(20260617)
    pos_i = [i for i, l in enumerate(labels) if l == 1]
    neg_i = [i for i, l in enumerate(labels) if l == 0]
    aucs = []
    for _ in range(n_boot):
        ps = [scores[pos_i[rng.randrange(len(pos_i))]] for _ in pos_i]
        ns = [scores[neg_i[rng.randrange(len(neg_i))]] for _ in neg_i]
        wins = 0.0
        for p in ps:
            for nn in ns:
                wins += 1.0 if p > nn else (0.5 if p == nn else 0.0)
        aucs.append(wins / (len(ps) * len(ns)))
    aucs.sort()
    lo = aucs[int((alpha / 2) * n_boot)]
    hi = aucs[int((1 - alpha / 2) * n_boot) - 1]
    return [round(lo, 3), round(hi, 3)]
