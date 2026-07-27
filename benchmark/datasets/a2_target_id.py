"""
A2 — Target identification (agent comparison). For each disease, rank gene targets;
gold = clinically-validated targets (genes of APPROVED drugs for the disease, from
OpenTargets — independent of LinkD's tables). Conditions: LinkD vs ToolUniverse-agent
(OpenTargets) vs base LLM.

Caveat: this is a *capability* comparison against a clinical-validation gold, NOT a
fully-prospective test (LinkD's static 2024 snapshot and live OpenTargets both already
contain post-cutoff approvals). A true time-split needs historical snapshots — see
AGENT_BENCHMARK_PLAN.md.

    python3 benchmark/datasets/a2_target_id.py   (after the A2 prefetch builds a2_diseases.json)
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from benchmark.datasets.base_builder import write_scenario, banner
from benchmark.datasets.splits import assign_split
from benchmark.schema import Item

SCENARIO = "a2_target_id"
CACHE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "external_data", "cache", "a2_diseases.json")
# LinkD's best bet: cancer indications only (its EHR/oncogene/binding data is cancer-rich)
CANCER_RE = re.compile(r"carcinoma|lymphoma|leuk[a]?emia|melanoma|myeloma|glioblastoma|"
                       r"sarcoma|neuroblastoma|mesothelioma|stromal tumou?r|cancer|tumou?r",
                       re.I)


def build():
    if not os.path.exists(CACHE):
        print("  a2_diseases.json missing — run the A2 prefetch first.")
        return []
    data = json.load(open(CACHE))
    items = []
    for name, info in data.items():
        if not CANCER_RE.search(name):   # cancer-only focus
            continue
        gold = info.get("gold", [])
        if len(gold) < 3:
            continue
        items.append(Item(
            id=f"{SCENARIO}-{name.replace(' ', '_')}", scenario=SCENARIO, format="target_rank",
            question=f"List the gene/protein drug targets being therapeutically pursued for {name}, "
                     f"ranked by relevance.",
            gold={"targets": gold},
            gold_source="OpenTargets disease-approved drug targets (clinical validation)",
            split="test",  # small fixed disease set — evaluate on all
            context_free_prompt=f"List the most important human gene/protein drug targets for {name}.",
            entities={"disease": name, "efo": info["efo"], "icd": info["icd"]},
            meta={"n_gold": len(gold)}))
    return items


if __name__ == "__main__":
    items = build()
    if items:
        banner(SCENARIO, write_scenario(SCENARIO, items))
    else:
        print("  no A2 items (prefetch a2_diseases.json first).")
