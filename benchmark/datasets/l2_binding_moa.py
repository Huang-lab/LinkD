"""
L2 — Binding -> mechanism. Does LinkD's predicted binding-affinity ranking surface a
drug's KNOWN mechanism-of-action target? Drugs = TDC DAVIS kinase inhibitors (LinkD has
binding data for them); gold = ChEMBL/OpenTargets mechanism targets (independent of
binding). LinkD ranks targets by predicted pKd; base LLMs name the targets from memory.

    python3 benchmark/datasets/l2_binding_moa.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from benchmark.datasets.base_builder import write_scenario, banner, data_available, REPO_ROOT
from benchmark.schema import Item

SCENARIO = "l2_binding_moa"
CAP = int(os.getenv("BENCH_L2_CAP", "45"))


def build():
    import pandas as pd
    from benchmark.external_data.davis import load_davis, tdc_available
    from benchmark.external_data.idmap import cid_to_chembl
    from benchmark.external_data import opentargets as ot
    if not tdc_available():
        print("  PyTDC unavailable — cannot build L2.")
        return []
    dv = load_davis()
    if dv is None:
        return []
    dbdir = os.getenv("DATABASE_DIR") or os.path.join(REPO_ROOT, "Database")
    root = os.path.dirname(dbdir)
    sel = pd.read_csv(os.path.join(root, "DrugTargetMetrics", "drug_selectivity_metrics.csv"),
                      usecols=["Drug Chembl ID", "Drug Name"])
    name_by_chembl = {str(c): str(n) for c, n in zip(sel["Drug Chembl ID"], sel["Drug Name"])}
    gene_uni = set(pd.read_csv(os.path.join(root, "DrugTargetMetrics", "target_binding_stats.csv"),
                               usecols=["Gene"])["Gene"].dropna().astype(str))

    items = []
    for cid in dv["Drug_ID"].astype(str).unique():
        if len(items) >= CAP:
            break
        chembl = cid_to_chembl(cid)
        if not chembl:
            continue
        try:
            moa = [g for g in ot.drug_targets(chembl) if g in gene_uni]
        except Exception:
            moa = []
        if len(moa) < 1:
            continue
        name = name_by_chembl.get(chembl, chembl)
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
    print(f"  L2: {len(items)} drugs with MoA gold")
    return items


if __name__ == "__main__":
    if not data_available():
        print(f"SKIP: LinkD data not found. Set DATABASE_DIR to enable {SCENARIO}.")
        raise SystemExit(0)
    items = build()
    if items:
        banner(SCENARIO, write_scenario(SCENARIO, items))
