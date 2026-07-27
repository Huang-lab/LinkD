"""
Compositional case studies for the LinkD-as-tool orchestrator. Unlike the per-task
benchmark (one signal per item), these are free-form, multi-step queries where the agent
must autonomously call SEVERAL LinkD tools, cross-check them, and synthesize a verdict.
Prints the full tool-call transcript for each.

    set -a; source config/api_keys.env; set +a
    python3 benchmark/case_studies.py [--model gpt-5.4]
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from benchmark.conditions.base import cli_json            # noqa: E402
from benchmark.conditions._llm import make_client          # noqa: E402

SYSTEM = (
    "You are a drug-discovery analyst with access to LinkD tools (predicted binding affinity, "
    "drug target rankings, selectivity, CRISPR drug-response, ranked disease targets, real-world "
    "EHR associations, and a weighted multi-evidence score). Answer the question by CALLING the "
    "tools you need — typically several — then reason over the results. Cross-check each tool "
    "result and weigh its reliability: trust strong, well-covered values over your memory; treat "
    "sparse or non-significant EHR/observational results (few rows, p not < 0.05, odds ratio near "
    "1) as weak evidence and fall back on your own knowledge; if a value looks implausible, "
    "override it and say so. Finish with a concise structured verdict: a recommendation plus the "
    "1–3 LinkD numbers that drove it and any point where you overrode LinkD."
)

# arg-taking tool schemas (the agent supplies entities resolved from the query)
def _p(props, required):
    return {"type": "object", "properties": props, "required": required}

TOOLS = [
    {"name": "linkd_binding", "description": "LinkD predicted binding affinity (pKd) for a drug–target pair.",
     "parameters": _p({"drug_chembl": {"type": "string"}, "gene": {"type": "string"}}, ["drug_chembl", "gene"])},
    {"name": "linkd_targets_for_drug", "description": "LinkD top predicted binding targets (genes) for a drug, by affinity.",
     "parameters": _p({"drug_chembl": {"type": "string"}}, ["drug_chembl"])},
    {"name": "linkd_selectivity", "description": "LinkD selectivity score / type for a drug (high = selective).",
     "parameters": _p({"drug_chembl": {"type": "string"}, "drug_name": {"type": "string"}}, [])},
    {"name": "linkd_crispr", "description": "Genes whose CRISPR-knockout response correlates with the drug.",
     "parameters": _p({"drug_chembl": {"type": "string"}, "drug_name": {"type": "string"}}, [])},
    {"name": "linkd_targets_for_disease", "description": "LinkD ranked gene targets for a disease (phase + causal evidence).",
     "parameters": _p({"disease": {"type": "string"}, "icd": {"type": "string"}}, [])},
    {"name": "linkd_ehr", "description": "LinkD real-world EHR drug–disease odds ratios (OR<1 protective, >1 risk).",
     "parameters": _p({"drug_name": {"type": "string"}, "icd": {"type": "string"}, "disease": {"type": "string"}}, [])},
    {"name": "linkd_evidence", "description": "LinkD weighted multi-evidence final_score (0–1) for a drug–gene–disease triad.",
     "parameters": _p({"drug_chembl": {"type": "string"}, "gene": {"type": "string"},
                       "disease": {"type": "string"}, "icd": {"type": "string"}}, ["drug_chembl", "gene"])},
]
_CLI = {
    "linkd_binding": lambda a: ["binding", a.get("drug_chembl", ""), a.get("gene", "")],
    "linkd_targets_for_drug": lambda a: ["targets-for-drug", a.get("drug_chembl", ""), "--limit", "15"],
    "linkd_selectivity": lambda a: ["drug-info", a.get("drug_chembl", ""), "--name", a.get("drug_name", "")],
    "linkd_crispr": lambda a: ["drug-response", "--drug", a.get("drug_chembl", ""), "--name", a.get("drug_name", ""),
                               "--sig", "--limit", "15"],
    "linkd_targets_for_disease": lambda a: ["targets-for-disease", "--disease", a.get("disease", ""),
                                            "--icd", a.get("icd", ""), "--limit", "15"],
    "linkd_ehr": lambda a: ["ehr", "--drug", a.get("drug_chembl", ""), "--name", a.get("drug_name", ""),
                            "--icd", a.get("icd", ""), "--disease", a.get("disease", "")],
    "linkd_evidence": lambda a: ["evidence", a.get("drug_chembl", ""), a.get("gene", ""),
                                 "--disease", a.get("disease", ""), "--icd", a.get("icd", "")],
}


def _executor(trace):
    def ex(name, args):
        b = _CLI.get(name)
        if not b:
            return json.dumps({"error": f"unknown tool {name}"})
        data, err = cli_json(*[str(x) for x in b(args)])
        out = json.dumps(data) if data is not None else json.dumps({"error": err or "no data"})
        trace.append((name, args, out))
        return out
    return ex


CASES = [
    ("Imatinib for chronic myeloid leukemia",
     "Assess imatinib (ChEMBL CHEMBL941) as a therapy for chronic myeloid leukemia (ICD C92), "
     "focusing on its canonical target ABL1. Consider LinkD's predicted binding to ABL1, the "
     "drug's selectivity, any real-world EHR association, and the overall multi-evidence score. "
     "Then give a recommendation."),
    ("Erlotinib mechanism + EGFR support in lung cancer",
     "What is the mechanism of erlotinib (ChEMBL CHEMBL553) — is it a selective EGFR inhibitor? "
     "Check LinkD's top binding targets and selectivity, then how strong the multi-evidence support "
     "is for EGFR in non-small-cell lung carcinoma (ICD C34). Cross-check LinkD against what you know."),
    ("Melanoma — disease-first target triage",
     "For melanoma (ICD C43), what are LinkD's top drug-target genes? Pick the most actionable one, "
     "check the predicted binding of vemurafenib (ChEMBL CHEMBL1229517) to it and the multi-evidence "
     "score, and recommend whether it is a strong target."),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gpt-5.4")
    a = ap.parse_args()
    client = make_client(a.model)
    if client is None:
        print(f"No client for {a.model} (key/SDK missing).")
        return 1
    for title, query in CASES:
        print("\n" + "=" * 88 + f"\nCASE: {title}\nQUERY: {query}\n" + "-" * 88)
        trace = []
        text, _ = client.run_tools(SYSTEM, query, TOOLS, _executor(trace), max_rounds=8, max_tokens=1500)
        for i, (name, args, out) in enumerate(trace, 1):
            print(f"  [tool {i}] {name}({', '.join(f'{k}={v}' for k, v in args.items())})")
            print(f"           -> {out[:160]}")
        print(f"\n  VERDICT ({a.model}, {len(trace)} tool calls):\n  " + (text or "").replace("\n", "\n  "))
    return 0


if __name__ == "__main__":
    sys.exit(main())
