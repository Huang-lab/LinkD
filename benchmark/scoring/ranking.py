"""Per-item ranking metrics: P@k, Recall@k, MRR, nDCG@k, Spearman vs gold order."""
from __future__ import annotations
import math
from typing import Dict, List


def _precision_at_k(pred: List[str], gold_set: set, k: int) -> float:
    if k == 0:
        return 0.0
    hits = sum(1 for x in pred[:k] if x in gold_set)
    return hits / k


def _recall_at_k(pred: List[str], gold: List[str], k: int) -> float:
    if not gold:
        return 0.0
    gold_set = set(gold)
    hits = sum(1 for x in pred[:k] if x in gold_set)
    return hits / min(k, len(gold))


def _mrr(pred: List[str], gold_set: set) -> float:
    for i, x in enumerate(pred, 1):
        if x in gold_set:
            return 1.0 / i
    return 0.0


def _ndcg_at_k(pred: List[str], gold: List[str], k: int) -> float:
    """Graded relevance = position weight in the gold ranking (top gold = highest)."""
    rel = {g: (len(gold) - i) for i, g in enumerate(gold)}
    dcg = sum(rel.get(x, 0) / math.log2(i + 2) for i, x in enumerate(pred[:k]))
    ideal = sorted(rel.values(), reverse=True)[:k]
    idcg = sum(r / math.log2(i + 2) for i, r in enumerate(ideal))
    return dcg / idcg if idcg else 0.0


def _spearman_vs_gold(pred: List[str], gold: List[str]) -> float:
    """Spearman rho between predicted order and gold order over the shared ids."""
    gold_rank = {g: i for i, g in enumerate(gold)}
    shared = [(i, gold_rank[x]) for i, x in enumerate(pred) if x in gold_rank]
    n = len(shared)
    if n < 2:
        return 0.0
    d2 = sum((a - b) ** 2 for a, b in shared)
    return 1 - (6 * d2) / (n * (n * n - 1))


def score_ranking(item, pred, k: int = 10) -> Dict:
    gold = [str(x) for x in item.gold.get("ranking", [])]
    p = [str(x) for x in pred.parsed.get("ranking", [])]
    gold_set = set(gold)
    return {
        "p_at_5": round(_precision_at_k(p, gold_set, 5), 4),
        "recall_at_10": round(_recall_at_k(p, gold, 10), 4),
        "mrr": round(_mrr(p, gold_set), 4),
        "ndcg_at_10": round(_ndcg_at_k(p, gold, k), 4),
        "spearman": round(_spearman_vs_gold(p, gold), 4),
        "n_pred": len(p),
        "parsed_ok": len(p) > 0,
    }


def score_target_rank(item, pred, k: int = 20) -> Dict:
    """A2: rank genes vs a gold SET of validated targets (binary relevance)."""
    gold = {str(g).upper() for g in item.gold.get("targets", [])}
    p = [str(g).upper() for g in pred.parsed.get("ranking", [])]
    if not gold:
        return {"target_rank": True, "skip": True, "error": bool(pred.error)}
    seen = set()
    p = [x for x in p if not (x in seen or seen.add(x))]
    hits_k = len(set(p[:k]) & gold)
    # binary-relevance nDCG@k
    dcg = sum(1.0 / math.log2(i + 2) for i, g in enumerate(p[:k]) if g in gold)
    idcg = sum(1.0 / math.log2(i + 2) for i in range(min(len(gold), k)))
    mrr = 0.0
    for i, g in enumerate(p, 1):
        if g in gold:
            mrr = 1.0 / i
            break
    return {"target_rank": True, "error": bool(pred.error),
            "recall_at_10": round(len(set(p[:10]) & gold) / len(gold), 4),
            "recall_at_20": round(hits_k / len(gold), 4),
            "ndcg_at_20": round(dcg / idcg if idcg else 0.0, 4),
            "mrr": round(mrr, 4), "n_gold": len(gold), "n_pred": len(p),
            # binary per-item signal for paired McNemar: did we surface a gold target in top-20?
            "right_action": int(hits_k > 0)}


# --------------------------- aggregation ----------------------------------- #
def mean_metric(scored: List[Dict], key: str) -> float:
    rel = [s[key] for s in scored if not s.get("error") and not s.get("skip") and key in s]
    return sum(rel) / len(rel) if rel else 0.0


def aggregate_target_rank(scored: List[Dict]) -> Dict:
    from benchmark.aggregate import bootstrap_ci
    rel = [s for s in scored if s.get("target_rank") and not s.get("skip")]
    _, r20_lo, r20_hi = bootstrap_ci([s["recall_at_20"] for s in rel if "recall_at_20" in s])
    _, n20_lo, n20_hi = bootstrap_ci([s["ndcg_at_20"] for s in rel if "ndcg_at_20" in s])
    return {"n": len(rel),
            "recall@10": round(mean_metric(rel, "recall_at_10"), 3),
            "recall@20": round(mean_metric(rel, "recall_at_20"), 3),
            "recall@20_ci": [r20_lo, r20_hi],
            "ndcg@20": round(mean_metric(rel, "ndcg_at_20"), 3),
            "ndcg@20_ci": [n20_lo, n20_hi],
            "mrr": round(mean_metric(rel, "mrr"), 3)}
