"""
CombinedCondition (combined): LinkD + base-LLM hybrid. For each item it runs the task's
LinkD layer condition AND the closed-book LLM, then fuses by format:
  - dti         -> mean of the two predicted pKd values (label by >=7)
  - target_rank -> reciprocal-rank fusion (RRF) of the two gene rankings
  - score_label -> mean of the two [0,1] scores
If one side abstains/errors, the other is used alone.
"""
from __future__ import annotations

from benchmark.conditions.base import _Timer
from benchmark.conditions.closed_book import ClosedBookCondition
from benchmark.schema import Item, Prediction

# scenario -> LinkD layer condition for that task
_LINKD = {
    "t1_dti": "linkd_cli",
    "l2_binding_moa": "linkd_binding_tgt",
    "l3_selectivity": "linkd_selectivity",
    "l4_crispr_moa": "linkd_crispr_tgt",
    "a2_target_id": "linkd",
    "a3_priority": "linkd",
    "t2_repurpose": "linkd_rwe",
    "l9_safety": "linkd_rwe",
    "c1_validate": "linkd_evidence",
    # refined, manuscript-aligned tasks
    "t7_sel_retrieval": "linkd_target_aff",
    "t4_crispr_conc": "linkd_crispr_pair",
    "t5_concordance": "linkd_fusion_pair",
}


def _make_linkd(name):
    if name == "linkd_cli":
        from benchmark.conditions.linkd_cli import LinkdCliCondition
        return LinkdCliCondition()
    if name == "linkd":
        from benchmark.conditions.agents_a2 import LinkdTargetsCondition
        return LinkdTargetsCondition()
    if name == "linkd_binding_tgt":
        from benchmark.conditions.agents_layers import LinkdBindingTargetsCondition
        return LinkdBindingTargetsCondition()
    if name == "linkd_crispr_tgt":
        from benchmark.conditions.agents_layers import LinkdCrisprTargetsCondition
        return LinkdCrisprTargetsCondition()
    if name == "linkd_selectivity":
        from benchmark.conditions.agents_layers import LinkdSelectivityCondition
        return LinkdSelectivityCondition()
    if name == "linkd_rwe":
        from benchmark.conditions.agents_integrative import LinkdRweCondition
        return LinkdRweCondition()
    if name == "linkd_evidence":
        from benchmark.conditions.agents_integrative import LinkdEvidenceCondition
        return LinkdEvidenceCondition()
    if name == "linkd_target_aff":
        from benchmark.conditions.agents_layers import LinkdTargetAffinityCondition
        return LinkdTargetAffinityCondition()
    if name == "linkd_crispr_pair":
        from benchmark.conditions.agents_layers import LinkdCrisprPairCondition
        return LinkdCrisprPairCondition()
    if name == "linkd_fusion_pair":
        from benchmark.conditions.agents_layers import LinkdFusionPairCondition
        return LinkdFusionPairCondition()
    raise ValueError(name)


def _rrf(a, b, k: int = 60):
    """Reciprocal-rank fusion of two ranked gene lists -> fused ranking."""
    score = {}
    for lst in (a, b):
        for i, g in enumerate(lst):
            g = str(g)
            score[g] = score.get(g, 0.0) + 1.0 / (k + i + 1)
    return [g for g, _ in sorted(score.items(), key=lambda kv: kv[1], reverse=True)]


class CombinedCondition:
    name = "combined"

    def __init__(self, model: str):
        self.model = model
        self._llm = ClosedBookCondition(model)
        self._linkd = {}

    def _linkd_for(self, scenario):
        if scenario not in self._linkd:
            self._linkd[scenario] = _make_linkd(_LINKD.get(scenario, "linkd"))
        return self._linkd[scenario]

    def run(self, item: Item) -> Prediction:
        pred = Prediction(item.id, item.scenario, self.name, self.model)
        with _Timer() as tm:
            lp = self._linkd_for(item.scenario).run(item)
            ep = self._llm.run(item)
            lpar, epar = lp.parsed or {}, ep.parsed or {}
            fmt = item.format
            if fmt == "dti":
                lv, ev = lpar.get("value"), epar.get("value")
                vals = [v for v in (lv, ev) if v is not None]
                val = sum(vals) / len(vals) if vals else None
                pred.parsed = ({"value": val, "label": ("yes" if val >= 7 else "no")}
                               if val is not None else {"abstained": True, "value": None, "label": None})
            elif fmt == "target_rank":
                pred.parsed = {"ranking": _rrf([str(x) for x in lpar.get("ranking", [])],
                                               [str(x) for x in epar.get("ranking", [])])}
            elif fmt == "score_label":
                ls, es = lpar.get("score"), epar.get("score")
                ss = [s for s in (ls, es) if s is not None]
                pred.parsed = {"score": (sum(ss) / len(ss) if ss else None)}
            else:
                pred.parsed = lpar or epar
            pred.tool_calls = (lp.tool_calls or 0) + (ep.tool_calls or 0)
            pred.raw_text = f"linkd={lp.raw_text[:60]} | llm={ep.raw_text[:60]}"
            if lp.error and ep.error:
                pred.error = f"both_failed:{lp.error}/{ep.error}"
        pred.latency_s = round(tm.dt, 3)
        return pred
