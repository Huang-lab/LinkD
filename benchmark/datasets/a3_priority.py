"""
A3 — Target prioritization / druggability. Same cancer indications and clinical-
validation gold as A2 (OpenTargets disease-approved drug targets), but the question
is *prioritization*: rank targets by therapeutic promise. This benchmarks LinkD's
dedicated **Target Priority Index (TPI)** signal (linkd_tpi) against the phase-based
LinkD ranker, OpenTargets association, and base LLMs — i.e. "does the TPI rank the
clinically-validated targets near the top?"

    python3 benchmark/datasets/a3_priority.py   (needs the A2 prefetch cache)
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from benchmark.datasets.base_builder import write_scenario, banner
from benchmark.datasets.a2_target_id import CACHE, CANCER_RE
from benchmark.schema import Item

SCENARIO = "a3_priority"


def build():
    if not os.path.exists(CACHE):
        print("  a2_diseases.json missing — run the A2 prefetch first.")
        return []
    data = json.load(open(CACHE))
    items = []
    for name, info in data.items():
        if not CANCER_RE.search(name):
            continue
        gold = info.get("gold", [])
        if len(gold) < 3:
            continue
        items.append(Item(
            id=f"{SCENARIO}-{name.replace(' ', '_')}", scenario=SCENARIO, format="target_rank",
            question=f"Prioritize human gene/protein drug targets for {name}: list the most "
                     f"promising, clinically advanced / druggable targets first.",
            gold={"targets": gold},
            gold_source="OpenTargets disease-approved drug targets (clinical-maturity gold)",
            split="test",
            context_free_prompt=f"Rank the most druggable, clinically advanced drug targets for {name} "
                                f"(most promising first).",
            entities={"disease": name, "efo": info["efo"], "icd": info["icd"]},
            meta={"n_gold": len(gold), "linkd_signal": "TPI"}))
    return items


if __name__ == "__main__":
    items = build()
    if items:
        banner(SCENARIO, write_scenario(SCENARIO, items))
    else:
        print("  no A3 items (prefetch a2_diseases.json first).")
