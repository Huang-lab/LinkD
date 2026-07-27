"""
LinkdOrchestratorCondition (orchestrator): a real function-calling agent. The LLM is given
the task question + the LinkD tools relevant to it, and natively decides which to call. The
harness executes each call against the LinkD CLI (entity-bound — the executor injects the
item's drug/gene/disease/icd, so the model can't hallucinate IDs), feeds results back, and the
model reasons + cross-checks LinkD before answering in the task format.
"""
from __future__ import annotations
import json

from benchmark.conditions.base import ConditionAdapter, _Timer, cli_json
from benchmark.conditions.closed_book import ClosedBookCondition, _FORMAT_INSTR
from benchmark.conditions._llm import make_client
from benchmark.schema import Item, Prediction

# tool name -> (description, builder(entities) -> LinkD CLI argv)
TOOL_SPECS = {
    "get_predicted_binding_affinity": (
        "LinkD's PREDICTED binding affinity (pKd) for the drug–target pair. Use it for the pKd "
        "value — you cannot estimate this reliably from a SMILES string.",
        lambda e: ["binding", e.get("drug", ""), e.get("gene", "")]),
    "get_drug_binding_targets": (
        "LinkD's top predicted binding targets (gene symbols) for the drug, ranked by affinity.",
        lambda e: ["targets-for-drug", e.get("drug", ""), "--limit", "40"]),
    "get_drug_selectivity": (
        "LinkD's selectivity score (0–1, higher = more selective) for the drug.",
        lambda e: ["drug-info", e.get("drug", ""), "--name", e.get("drug_name", "")]),
    "get_crispr_response_genes": (
        "Genes whose CRISPR-knockout cell-line response correlates with the drug (mechanism hints).",
        lambda e: ["drug-response", "--drug", e.get("drug", ""), "--sig", "--limit", "40"]),
    "get_disease_targets": (
        "LinkD's ranked gene targets for the disease (clinical-phase + causal-gene evidence).",
        lambda e: ["targets-for-disease", "--disease", e.get("disease", ""), "--icd", e.get("icd", ""),
                   "--limit", "40"]),
    "get_ehr_evidence": (
        "LinkD real-world EHR drug–disease association (odds ratios; OR<1 protective, OR>1 risk).",
        lambda e: ["ehr", "--drug", e.get("drug", ""), "--icd", e.get("icd", ""),
                   "--disease", e.get("disease", "")]),
    "get_multi_evidence_score": (
        "LinkD's weighted multi-evidence final_score (0–1) for the drug–gene–disease triad.",
        lambda e: ["evidence", e.get("drug", ""), e.get("gene", ""), "--disease", e.get("disease", ""),
                   "--icd", e.get("icd", "")]),
}
SCN_TOOLS = {
    "t1_dti": ["get_predicted_binding_affinity"],
    "l2_binding_moa": ["get_drug_binding_targets"],
    "l3_selectivity": ["get_drug_selectivity"],
    "l4_crispr_moa": ["get_crispr_response_genes"],
    "a2_target_id": ["get_disease_targets"],
    "a3_priority": ["get_disease_targets"],
    "t2_repurpose": ["get_ehr_evidence"],
    "l9_safety": ["get_ehr_evidence"],
    "c1_validate": ["get_multi_evidence_score"],
    # refined, manuscript-aligned tasks
    "t7_sel_retrieval": ["get_predicted_binding_affinity", "get_drug_selectivity"],
    "t4_crispr_conc": ["get_crispr_response_genes"],
    "t5_concordance": ["get_predicted_binding_affinity", "get_crispr_response_genes"],
}
SYSTEM = (
    "You are a precise drug-discovery assistant with access to LinkD tools — a curated database "
    "of predicted drug–target binding affinity, target rankings, selectivity, CRISPR drug-response, "
    "real-world EHR evidence, and weighted multi-evidence scores. When the question needs a value "
    "you cannot reliably recall or estimate from memory (a predicted pKd, a ranked target list, an "
    "evidence score), CALL the relevant LinkD tool rather than guessing. Cross-check tool results "
    "against your own knowledge: if a value looks implausible you may override it, but say so. "
    "Answer the parts you know directly. Finally, give ONLY the answer in exactly the requested format."
    # NOTE: an L9-targeted variant adding 'distrust sparse/non-significant EHR' was tested and did
    # NOT help — L9's FAERS gold is ontology-misaligned with LinkD's EHR, so it can't be fixed by
    # prompting. The case-study harness keeps the reliability-weighing guidance (it helped there).
)


def _executor(entities):
    def ex(name, _args):
        spec = TOOL_SPECS.get(name)
        if not spec:
            return json.dumps({"error": f"unknown tool {name}"})
        data, err = cli_json(*[str(x) for x in spec[1](entities)])
        return json.dumps(data) if data is not None else json.dumps({"error": err or "no data"})
    return ex


class LinkdOrchestratorCondition(ConditionAdapter):
    name = "orchestrator"

    def __init__(self, model: str):
        self.model = model
        self._client = make_client(model)

    def run(self, item: Item) -> Prediction:
        pred = Prediction(item.id, item.scenario, self.name, self.model)
        if self._client is None:
            pred.error = "no_provider"
            return pred
        tools = [{"name": n, "description": TOOL_SPECS[n][0],
                  "parameters": {"type": "object", "properties": {}}}
                 for n in SCN_TOOLS.get(item.scenario, [])]
        e = item.entities
        ent = ", ".join(f"{k}={e[k]}" for k in ("drug_name", "drug", "gene", "disease", "icd") if e.get(k))
        instr = _FORMAT_INSTR.get(item.format, _FORMAT_INSTR["open_ended"])
        user = f"{item.context_free_prompt}\n\n{instr}\n\nEntities: {ent}"
        with _Timer() as tm:
            try:
                text, trace = self._client.run_tools(SYSTEM, user, tools, _executor(e), max_rounds=5)
                pred.raw_text = (text or "")[:500]
                pred.parsed = ClosedBookCondition._parse(item.format, text or "")
                pred.tool_calls = len(trace)
            except Exception as ex:  # noqa: BLE001
                pred.error = f"{type(ex).__name__}: {ex}"
        pred.latency_s = round(tm.dt, 3)
        return pred
