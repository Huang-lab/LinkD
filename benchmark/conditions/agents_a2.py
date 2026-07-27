"""
A2 target-identification conditions (deterministic agents — no LLM):
  - LinkdTargetsCondition: ranks genes for a disease from LinkD (drug-target clinical
    phase + causal genes).
  - ToolUniverseCondition: ranks genes from cached OpenTargets associations (the
    generic-tool-agent comparator's answer).
The base-LLM condition reuses closed_book with the `target_rank` format.
"""
from __future__ import annotations
import os

from benchmark.conditions.base import ConditionAdapter, _Timer, REPO_ROOT
from benchmark.schema import Item, Prediction


class ToolUniverseCondition(ConditionAdapter):
    name = "tooluniverse"
    model = "opentargets"

    def run(self, item: Item) -> Prediction:
        pred = Prediction(item.id, item.scenario, self.name, self.model)
        with _Timer() as tm:
            try:
                from benchmark.external_data import opentargets as ot
                efo = item.entities.get("efo")
                genes = [g for g, _ in ot.associated_targets(efo, 60)] if efo else []
                pred.parsed = {"ranking": genes}
                pred.tool_calls = 1
                pred.raw_text = ", ".join(genes[:30])
                if not genes:
                    pred.error = "no_opentargets_data"
            except Exception as e:  # noqa: BLE001
                pred.error = f"{type(e).__name__}: {e}"
        pred.latency_s = round(tm.dt, 3)
        return pred


class OTGeneticsCondition(ConditionAdapter):
    """Genetics-only agent: rank targets by OpenTargets genetic_association evidence."""
    name = "ot_genetics"
    model = "ot-genetics"

    def run(self, item: Item) -> Prediction:
        pred = Prediction(item.id, item.scenario, self.name, self.model)
        with _Timer() as tm:
            try:
                from benchmark.external_data import opentargets as ot
                efo = item.entities.get("efo")
                genes = ot.genetics_targets(efo) if efo else []
                pred.parsed = {"ranking": genes}
                pred.tool_calls = 1
                pred.raw_text = ", ".join(genes[:30])
                if not genes:
                    pred.error = "no_genetics_data"
            except Exception as e:  # noqa: BLE001
                pred.error = f"{type(e).__name__}: {e}"
        pred.latency_s = round(tm.dt, 3)
        return pred


class PubMedCondition(ConditionAdapter):
    """Literature-mining agent: rank genes by co-mention with the disease in PubMed."""
    name = "pubmed"
    model = "literature"
    _vocab = None

    def _get_vocab(self):
        if PubMedCondition._vocab is None:
            import pandas as pd
            dbdir = os.getenv("DATABASE_DIR") or os.path.join(REPO_ROOT, "Database")
            root = os.path.dirname(dbdir)
            tbs = pd.read_csv(os.path.join(root, "DrugTargetMetrics", "target_binding_stats.csv"),
                              usecols=["Gene"])
            PubMedCondition._vocab = {str(g) for g in tbs["Gene"].dropna()}
        return PubMedCondition._vocab

    def run(self, item: Item) -> Prediction:
        pred = Prediction(item.id, item.scenario, self.name, self.model)
        with _Timer() as tm:
            try:
                from benchmark.external_data import pubmed
                genes = pubmed.target_mentions(item.entities.get("disease", ""), self._get_vocab())
                pred.parsed = {"ranking": genes}
                pred.tool_calls = 2
                pred.raw_text = ", ".join(genes[:30])
                if not genes:
                    pred.error = "no_pubmed_data"
            except Exception as e:  # noqa: BLE001
                pred.error = f"{type(e).__name__}: {e}"
        pred.latency_s = round(tm.dt, 3)
        return pred


class LinkdTargetsCondition(ConditionAdapter):
    name = "linkd"
    model = "tools-only"
    _db = None

    def _get_db(self):
        if LinkdTargetsCondition._db is None:
            from agent.database_query_module import load_database_subset
            dbdir = os.getenv("DATABASE_DIR") or os.path.join(REPO_ROOT, "Database")
            LinkdTargetsCondition._db = load_database_subset(
                {"causal_gene_disease", "drug_target_disease", "onco_genes"}, database_dir=dbdir)
        return LinkdTargetsCondition._db

    def run(self, item: Item) -> Prediction:
        pred = Prediction(item.id, item.scenario, self.name, self.model)
        with _Timer() as tm:
            try:
                genes = self._rank(self._get_db(), item.entities.get("disease", ""),
                                   item.entities.get("icd", ""))
                pred.parsed = {"ranking": genes}
                pred.tool_calls = 1
                pred.raw_text = ", ".join(genes[:30])
            except Exception as e:  # noqa: BLE001
                pred.error = f"{type(e).__name__}: {e}"
        pred.latency_s = round(tm.dt, 3)
        return pred

    @staticmethod
    def _rank(db, name, icd):
        import pandas as pd
        dtd = db.dfs.get("drug_target_disease")
        ranked = []
        if dtd is not None:
            m = pd.Series(False, index=dtd.index)
            if icd and "ICD_Code" in dtd.columns:
                m |= dtd["ICD_Code"].astype(str).str.upper() == str(icd).upper()
            if name and "subject_label" in dtd.columns:
                m |= dtd["subject_label"].astype(str).str.contains(name, case=False, na=False)
            sub = dtd[m]
            if not sub.empty:
                sub = sub.assign(phase=pd.to_numeric(sub["phase"], errors="coerce"))
                agg = sub.groupby("Gene").agg(maxphase=("phase", "max"),
                                              n=("drugId", "nunique")).reset_index()
                agg = agg.sort_values(["maxphase", "n"], ascending=False)
                ranked = agg["Gene"].astype(str).tolist()
        # append causal genes not already present
        causal = db.dfs.get("causal_gene_disease")
        extra = []
        if causal is not None:
            cm = pd.Series(False, index=causal.index)
            if icd and "ICD_Code" in causal.columns:
                cm |= causal["ICD_Code"].astype(str).str.upper().str.startswith(str(icd).upper())
            if name and "Disease Name" in causal.columns:
                cm |= causal["Disease Name"].astype(str).str.contains(name, case=False, na=False)
            cg = causal[cm]["Gene"].astype(str).unique().tolist()
            have = set(ranked)
            extra = [g for g in cg if g not in have]
        return (ranked + extra)[:60]


class LinkdPriorityCondition(ConditionAdapter):
    """A3: rank genes for a disease by LinkD's Target Priority Index (TPI). Reads the
    cached per-ICD TPI ranking (benchmark/external_data/tpi_prefetch.py)."""
    name = "linkd_tpi"
    model = "tools-only"
    _tpi = None

    def _get_tpi(self):
        if LinkdPriorityCondition._tpi is None:
            import json
            from benchmark.external_data.tpi_prefetch import CACHE
            LinkdPriorityCondition._tpi = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
        return LinkdPriorityCondition._tpi

    def run(self, item: Item) -> Prediction:
        pred = Prediction(item.id, item.scenario, self.name, self.model)
        with _Timer() as tm:
            try:
                genes = self._get_tpi().get(str(item.entities.get("icd", "")), [])
                pred.parsed = {"ranking": genes}
                pred.tool_calls = 1
                pred.raw_text = ", ".join(genes[:30])
                if not genes:
                    pred.error = "no_tpi_data"
            except Exception as e:  # noqa: BLE001
                pred.error = f"{type(e).__name__}: {e}"
        pred.latency_s = round(tm.dt, 3)
        return pred
