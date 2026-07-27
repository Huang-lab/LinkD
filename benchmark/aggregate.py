"""
Statistics for the benchmark: bootstrap confidence intervals, the McNemar paired
test for A-vs-B on the same items, and multiple-comparison correction. Pure
stdlib (math + seeded random) — no scipy/sklearn dependency.
"""
from __future__ import annotations
import math
import random
from typing import Dict, List, Optional, Tuple

SEED = 20260617


def bootstrap_ci(values: List[float], n: int = 1000, alpha: float = 0.05) -> Tuple[float, float, float]:
    """Return (mean, lo, hi) percentile bootstrap CI for the mean of `values`."""
    vals = [v for v in values if v is not None]
    if not vals:
        return (0.0, 0.0, 0.0)
    rng = random.Random(SEED)
    m = len(vals)
    means = []
    for _ in range(n):
        s = sum(vals[rng.randrange(m)] for _ in range(m)) / m
        means.append(s)
    means.sort()
    lo = means[int((alpha / 2) * n)]
    hi = means[int((1 - alpha / 2) * n) - 1]
    return (round(sum(vals) / m, 4), round(lo, 4), round(hi, 4))


def mcnemar(a_correct: List[int], b_correct: List[int]) -> Dict:
    """Paired McNemar test on two conditions' per-item correctness (same items, aligned).
    Uses the exact binomial test on the discordant pairs (robust for small n)."""
    b01 = sum(1 for a, b in zip(a_correct, b_correct) if a == 0 and b == 1)  # B right, A wrong
    b10 = sum(1 for a, b in zip(a_correct, b_correct) if a == 1 and b == 0)  # A right, B wrong
    nd = b01 + b10
    if nd == 0:
        return {"b01": 0, "b10": 0, "n_discordant": 0, "p_value": 1.0}
    k = min(b01, b10)
    # two-sided exact binomial p at q=0.5
    p = 2 * sum(math.comb(nd, i) for i in range(0, k + 1)) / (2 ** nd)
    return {"b01": b01, "b10": b10, "n_discordant": nd, "p_value": round(min(1.0, p), 5)}


def holm_bonferroni(pvals: List[float]) -> List[float]:
    """Holm-Bonferroni adjusted p-values (family-wise error)."""
    idx = sorted(range(len(pvals)), key=lambda i: pvals[i])
    m = len(pvals)
    adj = [0.0] * m
    run = 0.0
    for rank, i in enumerate(idx):
        val = (m - rank) * pvals[i]
        run = max(run, val)
        adj[i] = min(1.0, run)
    return [round(x, 5) for x in adj]


def benjamini_hochberg(pvals: List[float]) -> List[float]:
    """BH-adjusted p-values (false discovery rate)."""
    m = len(pvals)
    idx = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    prev = 1.0
    for rank in range(m - 1, -1, -1):
        i = idx[rank]
        val = pvals[i] * m / (rank + 1)
        prev = min(prev, val)
        adj[i] = min(1.0, prev)
    return [round(x, 5) for x in adj]


def correct_of(row: Dict) -> Optional[int]:
    """Extract a 0/1 'did the right thing' signal from a scored row, or None if N/A."""
    if row.get("error"):
        return None
    for k in ("right_action", "correct"):
        if k in row:
            return int(row[k])
    return None
