"""Scoring: per-item metric dicts + scenario-level aggregation."""
from benchmark.scoring.ranking import score_target_rank
from benchmark.scoring.regression import score_dti
from benchmark.scoring.auroc import score_binary


def score_item(item, pred) -> dict:
    """Route an (item, prediction) to the right per-item scorer by format. Returns a
    metrics dict that always includes `error` and `abstained` flags.
        dti          -> T1 binding (regression + binary)
        target_rank  -> A2/A3/A5 ranking (recall@k / nDCG / MRR)
        score_label  -> C1/B4/B5 binary discrimination (AUROC / AUPRC)
    """
    base = {"error": bool(pred.error), "abstained": bool(pred.parsed.get("abstained"))}
    if item.format == "dti":
        base.update(score_dti(item, pred))
    elif item.format == "target_rank":
        base.update(score_target_rank(item, pred))
    elif item.format == "score_label":
        base.update(score_binary(item, pred))
    return base
