"""Per-item + aggregate scoring for binary and 3-way classification."""
from __future__ import annotations
from typing import Dict, List


def score_binary(item, pred) -> Dict:
    gold = item.gold.get("label")
    p = pred.parsed.get("label")
    return {"correct": int(p == gold), "predicted": p, "gold": gold, "parsed_ok": p is not None}


def score_classification(item, pred) -> Dict:
    gold = item.gold.get("sign") or item.gold.get("label")
    p = pred.parsed.get("sign") or pred.parsed.get("label")
    return {"correct": int(p == gold), "predicted": p, "gold": gold, "parsed_ok": p is not None}


# --------------------------- aggregation ----------------------------------- #
def accuracy(scored: List[Dict]) -> float:
    rel = [s for s in scored if not s.get("error") and "correct" in s]
    return sum(s["correct"] for s in rel) / len(rel) if rel else 0.0


def macro_f1(scored: List[Dict]) -> float:
    rel = [s for s in scored if not s.get("error") and "gold" in s]
    labels = sorted({s["gold"] for s in rel if s["gold"] is not None})
    if not labels:
        return 0.0
    f1s = []
    for lab in labels:
        tp = sum(1 for s in rel if s["predicted"] == lab and s["gold"] == lab)
        fp = sum(1 for s in rel if s["predicted"] == lab and s["gold"] != lab)
        fn = sum(1 for s in rel if s["predicted"] != lab and s["gold"] == lab)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1s.append(2 * prec * rec / (prec + rec) if (prec + rec) else 0.0)
    return sum(f1s) / len(f1s)


def confusion(scored: List[Dict]) -> Dict:
    rel = [s for s in scored if not s.get("error") and "gold" in s]
    out: Dict = {}
    for s in rel:
        out.setdefault(s["gold"], {}).setdefault(s["predicted"], 0)
        out[s["gold"]][s["predicted"]] += 1
    return out
