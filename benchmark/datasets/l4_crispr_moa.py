"""
L4 — CRISPR correlation -> mechanism. Does LinkD's CRISPR drug-response correlation
ranking surface a drug's KNOWN mechanism target? Drugs = those with LinkD CRISPR
drug-response data; gold = ChEMBL/OpenTargets mechanism targets (pharmacology, NOT the
cell-line screen — so the test is independent of the GDSC/PRISM data LinkD ingested).

    python3 benchmark/datasets/l4_crispr_moa.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from benchmark.datasets.base_builder import write_scenario, banner, data_available, REPO_ROOT
from benchmark.schema import Item

SCENARIO = "l4_crispr_moa"
CAP = int(os.getenv("BENCH_L4_CAP", "60"))


def build():
    import pandas as pd
    from agent.database_query_module import load_database_subset
    from benchmark.external_data import opentargets as ot
    db = load_database_subset({"drug_response"})
    dr = db.dfs.get("drug_response")
    if dr is None or dr.empty:
        print("  no drug_response data.")
        return []
    root = os.path.dirname(os.getenv("DATABASE_DIR") or os.path.join(REPO_ROOT, "Database"))
    gene_uni = set(pd.read_csv(os.path.join(root, "DrugTargetMetrics", "target_binding_stats.csv"),
                               usecols=["Gene"])["Gene"].dropna().astype(str))
    # unique drugs with a ChEMBL id
    drugs = (dr[["drugs", "ChEMBL_ID"]].dropna().drop_duplicates())
    items = []
    for name, chembl in zip(drugs["drugs"].astype(str), drugs["ChEMBL_ID"].astype(str)):
        if len(items) >= CAP:
            break
        if not chembl.startswith("CHEMBL"):
            continue
        try:
            moa = [g for g in ot.drug_targets(chembl) if g in gene_uni]
        except Exception:
            moa = []
        if len(moa) < 1:
            continue
        items.append(Item(
            id=f"{SCENARIO}-{chembl}", scenario=SCENARIO, format="target_rank",
            question=f"Which human gene targets does {name} act on (its mechanism of action)?",
            gold={"targets": moa},
            gold_source="ChEMBL/OpenTargets mechanism-of-action targets",
            split="test",
            context_free_prompt=f"List the human gene/protein targets that the drug {name} acts on "
                                f"(its molecular mechanism). Output only gene symbols.",
            entities={"drug": chembl, "drug_name": name},
            meta={"n_gold": len(moa)}))
    print(f"  L4: {len(items)} drugs with CRISPR data + MoA gold")
    return items


if __name__ == "__main__":
    if not data_available():
        print(f"SKIP: LinkD data not found. Set DATABASE_DIR to enable {SCENARIO}.")
        raise SystemExit(0)
    items = build()
    if items:
        banner(SCENARIO, write_scenario(SCENARIO, items))
