"""
LinkD single-layer conditions for the feature-coordinated benchmark:
  - LinkdSelectivityCondition (linkd_selectivity): per-drug selectivity score (L3).
  - LinkdBindingTargetsCondition (linkd_binding_tgt): rank a drug's targets by predicted
    binding affinity, mapped back to gene symbols (L2).
  - LinkdCrisprTargetsCondition (linkd_crispr_tgt): rank a drug's genes by CRISPR
    drug-response correlation (L4).
"""
from __future__ import annotations
import os

from benchmark.conditions.base import ConditionAdapter, _Timer, REPO_ROOT
from benchmark.schema import Item, Prediction


class LinkdSelectivityCondition(ConditionAdapter):
    name = "linkd_selectivity"
    model = "tools-only"
    _db = None

    def _get_db(self):
        if LinkdSelectivityCondition._db is None:
            from agent.database_query_module import load_database_subset
            dbdir = os.getenv("DATABASE_DIR") or os.path.join(REPO_ROOT, "Database")
            LinkdSelectivityCondition._db = load_database_subset({"drug_selectivity"}, database_dir=dbdir)
        return LinkdSelectivityCondition._db

    def run(self, item: Item) -> Prediction:
        pred = Prediction(item.id, item.scenario, self.name, self.model)
        with _Timer() as tm:
            try:
                info = self._get_db().get_drug_selectivity_info(drug_id=item.entities.get("drug", ""))
                score = None
                if info:
                    score = info.get("Selectivity_Score", info.get("selectivity_score"))
                pred.parsed = {"score": (float(score) if score is not None else None)}
                pred.tool_calls = 1
                pred.raw_text = f"selectivity={score}"
                if score is None:
                    pred.error = "no_selectivity_data"
            except Exception as e:  # noqa: BLE001
                pred.error = f"{type(e).__name__}: {e}"
        pred.latency_s = round(tm.dt, 3)
        return pred


class LinkdBindingTargetsCondition(ConditionAdapter):
    """L2: rank a drug's targets by predicted binding affinity; map UniProt-mnemonic
    target names (e.g. EGFR_HUMAN, PGFRB_HUMAN) back to gene symbols via target_binding_stats."""
    name = "linkd_binding_tgt"
    model = "tools-only"
    _db = None
    _t2g = None

    def _get_db(self):
        if LinkdBindingTargetsCondition._db is None:
            from agent.database_query_module import load_database_subset
            dbdir = os.getenv("DATABASE_DIR") or os.path.join(REPO_ROOT, "Database")
            LinkdBindingTargetsCondition._db = load_database_subset(set(), database_dir=dbdir)
        return LinkdBindingTargetsCondition._db

    def _target_to_gene(self):
        if LinkdBindingTargetsCondition._t2g is None:
            import pandas as pd
            dbdir = os.getenv("DATABASE_DIR") or os.path.join(REPO_ROOT, "Database")
            root = os.path.dirname(dbdir)
            tbs = pd.read_csv(os.path.join(root, "DrugTargetMetrics", "target_binding_stats.csv"),
                              usecols=["Gene", "Target"])
            LinkdBindingTargetsCondition._t2g = {str(t): str(g) for t, g in
                                                 zip(tbs["Target"], tbs["Gene"]) if pd.notna(t)}
        return LinkdBindingTargetsCondition._t2g

    def run(self, item: Item) -> Prediction:
        pred = Prediction(item.id, item.scenario, self.name, self.model)
        with _Timer() as tm:
            try:
                df = self._get_db().get_targets_for_drug_with_affinity(item.entities.get("drug", ""), limit=60)
                t2g = self._target_to_gene()
                genes = []
                if df is not None and not df.empty:
                    for tname in df["Target"].astype(str).tolist():
                        g = t2g.get(tname)
                        if g and g not in genes:
                            genes.append(g)
                pred.parsed = {"ranking": genes}
                pred.tool_calls = 1
                pred.raw_text = ", ".join(genes[:30])
                if not genes:
                    pred.error = "no_binding_targets"
            except Exception as e:  # noqa: BLE001
                pred.error = f"{type(e).__name__}: {e}"
        pred.latency_s = round(tm.dt, 3)
        return pred


class LinkdTargetAffinityCondition(ConditionAdapter):
    """T7' selectivity retrieval: score a (drug, target) pair by LinkD's predicted binding
    affinity — the quantity Fig 5a ranks the 14,981-drug proteome by. Higher predicted pKd =>
    more likely a (selective) binder of the target. pKd (2.9–10.95) is min-max scaled to [0,1]."""
    name = "linkd_target_aff"
    model = "tools-only"
    _db = None

    def _get_db(self):
        if LinkdTargetAffinityCondition._db is None:
            from agent.database_query_module import load_database_subset
            dbdir = os.getenv("DATABASE_DIR") or os.path.join(REPO_ROOT, "Database")
            LinkdTargetAffinityCondition._db = load_database_subset({"target_binding_stats"}, database_dir=dbdir)
        return LinkdTargetAffinityCondition._db

    def run(self, item: Item) -> Prediction:
        pred = Prediction(item.id, item.scenario, self.name, self.model)
        e = item.entities
        with _Timer() as tm:
            try:
                info = self._get_db().get_drug_target_binding_affinity(e.get("drug", ""), e.get("gene", ""))
                pkd = (info or {}).get("binding_affinity")
                score = None
                if pkd is not None and pkd == pkd:
                    score = max(0.0, min(1.0, (float(pkd) - 2.9) / (10.95 - 2.9)))
                pred.parsed = {"score": score}
                if score is None:
                    pred.parsed["abstained"] = True
                pred.tool_calls = 1
                pred.raw_text = f"pKd={pkd}"
            except Exception as ex:  # noqa: BLE001
                pred.error = f"{type(ex).__name__}: {ex}"
        pred.latency_s = round(tm.dt, 3)
        return pred


class LinkdCrisprPairCondition(ConditionAdapter):
    """T4' CRISPR concordance: score a (drug, gene) pair by |drug-response↔CRISPR correlation|
    (|AUC_corr|, the LinkD-Pheno functional signal). Pairs not measured in the screen score 0
    (no detected concordance)."""
    name = "linkd_crispr_pair"
    model = "tools-only"
    _db = None

    def _get_db(self):
        if LinkdCrisprPairCondition._db is None:
            from agent.database_query_module import load_database_subset
            dbdir = os.getenv("DATABASE_DIR") or os.path.join(REPO_ROOT, "Database")
            LinkdCrisprPairCondition._db = load_database_subset({"drug_response"}, database_dir=dbdir)
        return LinkdCrisprPairCondition._db

    def run(self, item: Item) -> Prediction:
        pred = Prediction(item.id, item.scenario, self.name, self.model)
        e = item.entities
        with _Timer() as tm:
            try:
                # drug_id only — passing drug_name triggers a regex `contains` that corrupts the
                # filter and drops the target row. ChEMBL IDs match cleanly.
                df = self._get_db().get_drug_response_associations(drug_id=e.get("drug"))
                score = 0.0
                if df is not None and not df.empty and "AUC_corr" in df.columns:
                    # 'genes' = every measured gene (464k rows); 'Gene' = annotated-only (sparse).
                    gcol = "genes" if "genes" in df.columns else "Gene"
                    g = str(e.get("gene", ""))
                    sub = df[df[gcol].astype(str).str.upper() == g.upper()]
                    if not sub.empty:
                        vals = sub["AUC_corr"].dropna()
                        if not vals.empty:
                            score = float(abs(vals.astype(float)).max())
                pred.parsed = {"score": score}
                pred.tool_calls = 1
                pred.raw_text = f"|AUC_corr|={score:.3f}"
            except Exception as ex:  # noqa: BLE001
                pred.error = f"{type(ex).__name__}: {ex}"
        pred.latency_s = round(tm.dt, 3)
        return pred


class LinkdFusionPairCondition(ConditionAdapter):
    """T5' multi-evidence fusion: combine the two drug–target evidence layers the manuscript
    fuses — predicted binding affinity AND CRISPR drug-response concordance — into one score
    (mean of min-max-scaled pKd and |AUC_corr|). Demonstrates that fusing functional + molecular
    evidence recovers drug–target pairs better than either alone."""
    name = "linkd_fusion_pair"
    model = "tools-only"
    _db = None

    def _get_db(self):
        if LinkdFusionPairCondition._db is None:
            from agent.database_query_module import load_database_subset
            dbdir = os.getenv("DATABASE_DIR") or os.path.join(REPO_ROOT, "Database")
            LinkdFusionPairCondition._db = load_database_subset(
                {"target_binding_stats", "drug_response"}, database_dir=dbdir)
        return LinkdFusionPairCondition._db

    def run(self, item: Item) -> Prediction:
        pred = Prediction(item.id, item.scenario, self.name, self.model)
        e = item.entities
        g = str(e.get("gene", ""))
        with _Timer() as tm:
            try:
                db = self._get_db()
                info = db.get_drug_target_binding_affinity(e.get("drug", ""), g)
                pkd = (info or {}).get("binding_affinity")
                bind = max(0.0, min(1.0, (float(pkd) - 2.9) / (10.95 - 2.9))) if (pkd is not None and pkd == pkd) else 0.0
                df = db.get_drug_response_associations(drug_id=e.get("drug"))
                cris = 0.0
                if df is not None and not df.empty and "AUC_corr" in df.columns:
                    gcol = "genes" if "genes" in df.columns else "Gene"
                    sub = df[df[gcol].astype(str).str.upper() == g.upper()]
                    v = sub["AUC_corr"].dropna() if not sub.empty else None
                    if v is not None and not v.empty:
                        cris = float(abs(v.astype(float)).max())
                pred.parsed = {"score": round((bind + cris) / 2.0, 4)}
                pred.tool_calls = 2
                pred.raw_text = f"bind={bind:.2f} crispr={cris:.2f}"
            except Exception as ex:  # noqa: BLE001
                pred.error = f"{type(ex).__name__}: {ex}"
        pred.latency_s = round(tm.dt, 3)
        return pred


class LinkdCrisprTargetsCondition(ConditionAdapter):
    """L4: rank a drug's genes by CRISPR drug-response correlation strength (|AUC_corr|)."""
    name = "linkd_crispr_tgt"
    model = "tools-only"
    _db = None

    def _get_db(self):
        if LinkdCrisprTargetsCondition._db is None:
            from agent.database_query_module import load_database_subset
            dbdir = os.getenv("DATABASE_DIR") or os.path.join(REPO_ROOT, "Database")
            LinkdCrisprTargetsCondition._db = load_database_subset({"drug_response"}, database_dir=dbdir)
        return LinkdCrisprTargetsCondition._db

    def run(self, item: Item) -> Prediction:
        pred = Prediction(item.id, item.scenario, self.name, self.model)
        with _Timer() as tm:
            try:
                df = self._get_db().get_drug_response_associations(
                    drug_id=item.entities.get("drug", ""), drug_name=item.entities.get("drug_name"),
                    significant_only=True)
                genes = []
                if df is not None and not df.empty and "Gene" in df.columns and "AUC_corr" in df.columns:
                    d = df.assign(_a=df["AUC_corr"].abs()).sort_values("_a", ascending=False)
                    for g in d["Gene"].astype(str).tolist():
                        if g and g != "nan" and g not in genes:
                            genes.append(g)
                pred.parsed = {"ranking": genes}
                pred.tool_calls = 1
                pred.raw_text = ", ".join(genes[:30])
                if not genes:
                    pred.error = "no_crispr_data"
            except Exception as e:  # noqa: BLE001
                pred.error = f"{type(e).__name__}: {e}"
        pred.latency_s = round(tm.dt, 3)
        return pred
