"""
T1 — Drug-target binding affinity (EXTERNAL gold). Pairs from TDC DAVIS aligned to
LinkD's entity space; gold is the experimental Kd (-> pKd), NOT LinkD's own data.
Stratified sample (binders / mid / non-binders) keeps LLM cost bounded while the
deterministic LinkD condition can also score the full overlap.

    python3 benchmark/datasets/t1_dti.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from benchmark.datasets.base_builder import get_db, make_item, write_scenario, banner, data_available, rng

SCENARIO = "t1_dti"
N = int(os.getenv("BENCH_N", "60"))   # per stratum cap


def build():
    from benchmark.external_data.davis import load_davis, align_to_linkd, tdc_available
    if not tdc_available():
        print("  PyTDC unavailable — cannot build T1 (install PyTDC==0.4.1 + huggingface_hub).")
        return []
    db = get_db({"target_binding_stats"})
    davis = load_davis()
    if davis is None:
        return []
    aligned = align_to_linkd(davis, db)
    print(f"  DAVIS aligned to LinkD: {len(aligned)} pairs "
          f"({aligned['gene'].nunique()} targets, {aligned['chembl'].nunique()} drugs)")

    r = rng()
    binders = aligned[aligned.pkd_exp >= 7.0]
    mid = aligned[(aligned.pkd_exp >= 6.0) & (aligned.pkd_exp < 7.0)]
    nonb = aligned[aligned.pkd_exp < 6.0]

    def sample(d, n):
        idx = list(range(len(d))); r.shuffle(idx)
        return d.iloc[idx[:n]]

    picked = []
    for strat in (binders, mid, nonb):
        if not strat.empty:
            picked.append(sample(strat, N))
    import pandas as pd
    sub = pd.concat(picked).drop_duplicates(subset=["chembl", "gene"])

    items = []
    for row in sub.itertuples():
        smiles = str(row.Drug)
        label = "yes" if row.pkd_exp >= 7 else "no"
        q = (f"For the molecule with SMILES `{smiles}` and the human protein "
             f"{row.gene}: (a) estimate the drug-target binding affinity as pKd "
             f"(a single number, usually 5-10); (b) is it a strong binder (pKd >= 7)? "
             f"Reply with the pKd number, then yes or no.")
        items.append(make_item(
            f"{SCENARIO}-{row.chembl}-{row.gene}", SCENARIO, "dti", q,
            {"value": round(float(row.pkd_exp), 2), "label": label},
            "TDC DAVIS experimental Kd (-> pKd)",
            {"drug": str(row.chembl), "gene": str(row.gene), "smiles": smiles},
            meta={"cid": str(row.Drug_ID), "target_id": str(row.Target_ID),
                  "kd_nM": round(float(row.Y), 3)}))
    return items


if __name__ == "__main__":
    if not data_available():
        print(f"SKIP: LinkD data not found. Set DATABASE_DIR to enable {SCENARIO}.")
        raise SystemExit(0)
    items = build()
    if items:
        banner(SCENARIO, write_scenario(SCENARIO, items))
