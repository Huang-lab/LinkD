"""
Conditions for the binary-discrimination tasks (C1 validate, B4/T2 repurpose, B5 safety),
which emit a continuous score per item (scored by AUROC/AUPRC):

  - LinkdEvidenceCondition (linkd_evidence): LinkD's weighted multi-evidence `final_score`
    for a (drug, gene, disease) triad — the evidence-fusion signal.
  - LinkdRweCondition (linkd_rwe): LinkD's EHR real-world signal for a (drug, disease) pair
    (protective effect -> high repurposing score; used by T2/B5).
  - OTAssocScoreCondition (ot_assoc): OpenTargets (gene, disease) association score.
"""
from __future__ import annotations
import math
import os

from benchmark.conditions.base import ConditionAdapter, _Timer, REPO_ROOT
from benchmark.schema import Item, Prediction


class LinkdEvidenceCondition(ConditionAdapter):
    name = "linkd_evidence"
    model = "tools-only"
    _db = None

    def _get_db(self):
        if LinkdEvidenceCondition._db is None:
            from agent.database_query_module import load_database_subset
            dbdir = os.getenv("DATABASE_DIR") or os.path.join(REPO_ROOT, "Database")
            LinkdEvidenceCondition._db = load_database_subset(
                {"drug_target_disease", "causal_gene_disease", "onco_genes",
                 "ehr_mount_sinai", "ehr_uk_biobank", "drug_response"}, database_dir=dbdir)
        return LinkdEvidenceCondition._db

    def run(self, item: Item) -> Prediction:
        pred = Prediction(item.id, item.scenario, self.name, self.model)
        e = item.entities
        with _Timer() as tm:
            try:
                ev = self._get_db().get_comprehensive_drug_target_evidence(
                    drug_id=e.get("drug", ""), gene=e.get("gene", ""),
                    disease=e.get("disease"), icd_code=e.get("icd"))
                pred.parsed = {"score": ev.get("final_score")}
                pred.tool_calls = 1
                pred.raw_text = (f"final={ev.get('final_score')} strength={ev.get('strength_score')} "
                                 f"coverage={ev.get('coverage')} verdict={ev.get('verdict')}")
            except Exception as ex:  # noqa: BLE001
                pred.error = f"{type(ex).__name__}: {ex}"
        pred.latency_s = round(tm.dt, 3)
        return pred


class LinkdRweCondition(ConditionAdapter):
    """Repurposing/safety score from LinkD EHR: maps the disease-specific odds ratio to a
    [0,1] score. For repurposing (T2) a protective effect (OR<1) -> high score; the sign is
    flipped for safety (B5) via item.meta['direction']=='risk'."""
    name = "linkd_rwe"
    model = "tools-only"
    _db = None

    def _get_db(self):
        if LinkdRweCondition._db is None:
            from agent.database_query_module import load_database_subset
            dbdir = os.getenv("DATABASE_DIR") or os.path.join(REPO_ROOT, "Database")
            LinkdRweCondition._db = load_database_subset(
                {"ehr_mount_sinai", "ehr_uk_biobank", "drug_target_disease"}, database_dir=dbdir)
        return LinkdRweCondition._db

    def run(self, item: Item) -> Prediction:
        pred = Prediction(item.id, item.scenario, self.name, self.model)
        e = item.entities
        risk = item.meta.get("direction") == "risk"
        with _Timer() as tm:
            try:
                db = self._get_db()
                ehr = db.get_ehr_drug_disease_associations(
                    drug_id=e.get("drug", ""), drug_name=e.get("drug_name"),
                    icd_code=e.get("icd"), disease_name=e.get("disease"))
                score = 0.5
                if ehr is not None and not ehr.empty:
                    cols = [c for c in ("logit_or", "odds_ratio") if c in ehr.columns]
                    best = None
                    for _, row in ehr.iterrows():
                        o = next((row.get(c) for c in cols if _num(row.get(c)) is not None), None)
                        o = _num(o)
                        if o is None or o <= 0:
                            continue
                        p = _num(row.get("logit_p"))
                        if best is None or (p is not None and (best[1] is None or p < best[1])):
                            best = (o, p)
                    if best:
                        o = best[0]
                        # log-OR -> [0,1]; protective (OR<1) high for repurposing, risk (OR>1) high for safety
                        lo = math.log(o)
                        s = 1.0 / (1.0 + math.exp(2.0 * lo))   # OR<1 -> >0.5
                        score = (1.0 - s) if risk else s
                pred.parsed = {"score": round(score, 4)}
                pred.tool_calls = 1
                pred.raw_text = f"ehr_score={score}"
            except Exception as ex:  # noqa: BLE001
                pred.error = f"{type(ex).__name__}: {ex}"
        pred.latency_s = round(tm.dt, 3)
        return pred


class OTAssocScoreCondition(ConditionAdapter):
    """OpenTargets (gene, disease) overall-association score in [0,1] as the predictor."""
    name = "ot_assoc"
    model = "opentargets"
    _cache = {}

    def run(self, item: Item) -> Prediction:
        pred = Prediction(item.id, item.scenario, self.name, self.model)
        e = item.entities
        efo, gene = e.get("efo"), str(e.get("gene", "")).upper()
        with _Timer() as tm:
            try:
                from benchmark.external_data import opentargets as ot
                if efo not in OTAssocScoreCondition._cache:
                    OTAssocScoreCondition._cache[efo] = {g.upper(): s
                                                         for g, s in ot.associated_targets(efo, 200)}
                score = OTAssocScoreCondition._cache[efo].get(gene, 0.0)
                pred.parsed = {"score": float(score)}
                pred.tool_calls = 1
                pred.raw_text = f"ot_assoc={score}"
            except Exception as ex:  # noqa: BLE001
                pred.error = f"{type(ex).__name__}: {ex}"
        pred.latency_s = round(tm.dt, 3)
        return pred


def _num(v):
    try:
        f = float(v)
        return None if (f != f or f in (float("inf"), float("-inf"))) else f
    except (TypeError, ValueError):
        return None
