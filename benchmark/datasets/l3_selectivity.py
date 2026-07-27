"""
L3 — Drug selectivity (LinkD selectivity layer). Gold = experimental promiscuity from
the full TDC DAVIS kinome matrix (how many of ~379 kinases each drug binds at pKd>=7).
Label: selective (bottom tercile of strong-binders) vs promiscuous (top tercile). LinkD's
precomputed `Selectivity_Score` predicts it; base LLMs estimate it from the drug name.

    python3 benchmark/datasets/l3_selectivity.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from benchmark.datasets.base_builder import write_scenario, banner, data_available, REPO_ROOT
from benchmark.schema import Item

SCENARIO = "l3_selectivity"


def build():
    import pandas as pd
    from benchmark.external_data.davis import load_davis, tdc_available
    from benchmark.external_data.idmap import cid_to_chembl
    if not tdc_available():
        print("  PyTDC unavailable — cannot build L3.")
        return []
    dv = load_davis()
    if dv is None:
        return []
    # experimental selectivity per drug from the FULL matrix
    g = (dv.groupby("Drug_ID")
           .agg(n_strong=("pkd_exp", lambda s: int((s >= 7).sum())), n_tot=("Target_ID", "nunique"))
           .reset_index())
    g = g[g["n_tot"] >= 50]                     # need a real profile
    q1, q2 = g["n_strong"].quantile([0.34, 0.66])
    # LinkD drug names + chembl (also guarantees LinkD selectivity coverage)
    dbdir = os.getenv("DATABASE_DIR") or os.path.join(REPO_ROOT, "Database")
    root = os.path.dirname(dbdir)
    sel = pd.read_csv(os.path.join(root, "DrugTargetMetrics", "drug_selectivity_metrics.csv"),
                      usecols=["Drug Chembl ID", "Drug Name"])
    name_by_chembl = {str(c): str(n) for c, n in zip(sel["Drug Chembl ID"], sel["Drug Name"])}
    have_sel = set(name_by_chembl)

    items = []
    for row in g.itertuples():
        if q1 < row.n_strong < q2:             # keep only clear selective/promiscuous
            continue
        chembl = cid_to_chembl(str(row.Drug_ID))
        if not chembl or chembl not in have_sel:
            continue
        label = 1 if row.n_strong <= q1 else 0   # selective = 1
        name = name_by_chembl.get(chembl, chembl)
        items.append(Item(
            id=f"{SCENARIO}-{chembl}", scenario=SCENARIO, format="score_label",
            question=f"Is {name} a selective kinase inhibitor (binds few kinases)?",
            gold={"label": label},
            gold_source="TDC DAVIS full kinome matrix — strong-binder count (selective vs promiscuous)",
            split="test",
            context_free_prompt=f"On a scale from 0 to 1, how SELECTIVE is the kinase inhibitor "
                                f"{name}? 1 = binds very few kinases (highly selective), "
                                f"0 = binds many kinases (promiscuous). Output only the number.",
            entities={"drug": chembl, "drug_name": name},
            meta={"label": label, "n_strong": int(row.n_strong), "n_tot": int(row.n_tot)}))
    n_pos = sum(i.gold["label"] for i in items)
    print(f"  L3: {len(items)} drugs ({n_pos} selective / {len(items)-n_pos} promiscuous)")
    return items


if __name__ == "__main__":
    if not data_available():
        print(f"SKIP: LinkD data not found. Set DATABASE_DIR to enable {SCENARIO}.")
        raise SystemExit(0)
    items = build()
    if items:
        banner(SCENARIO, write_scenario(SCENARIO, items))
