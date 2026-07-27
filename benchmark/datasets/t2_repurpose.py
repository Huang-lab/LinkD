"""
T2 / B4 — Drug repurposing (phenotypic, EXTERNAL gold). repoDB approved (+) vs
failed/terminated/withdrawn (−) drug-indication pairs. Drugs are crosswalked
DrugBank -> ChEMBL via LinkD's EHR metadata; indications -> LinkD ICD by exact
disease-label match (avoids a UMLS license). LinkD scores each pair with its
real-world EHR signal (protective odds ratio -> high); base LLMs score from memory.

    python3 benchmark/datasets/t2_repurpose.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from benchmark.datasets.base_builder import write_scenario, banner, data_available, rng
from benchmark.schema import Item

SCENARIO = "t2_repurpose"
PER = int(os.getenv("BENCH_T2_PER", "90"))   # cap per class (approved / failed)


def build():
    from benchmark.external_data.repodb import load_repodb, drugbank_to_chembl
    from agent.database_query_module import load_database_subset
    df = load_repodb()
    if df is None:
        print("  repoDB not available.")
        return []
    db = load_database_subset({"ehr_mount_sinai", "ehr_uk_biobank", "drug_target_disease"})
    db2ch = drugbank_to_chembl(db)
    dtd = db.dfs.get("drug_target_disease")
    lab2icd = {}
    if dtd is not None and "subject_label" in dtd.columns and "ICD_Code" in dtd.columns:
        for s, i in zip(dtd["subject_label"].astype(str), dtd["ICD_Code"].astype(str)):
            lab2icd.setdefault(s.lower(), i)

    rows = []
    for t in df.itertuples():
        ch = db2ch.get(str(t.drug_id))
        icd = lab2icd.get(str(t.ind_name).lower())
        if not ch or not icd:
            continue
        rows.append((ch, str(t.drug_name), str(t.ind_name), icd, int(bool(t.approved))))
    # dedupe by (drug, disease); balance classes
    seen = set(); uniq = []
    for r0 in rows:
        key = (r0[0], r0[3])
        if key in seen:
            continue
        seen.add(key); uniq.append(r0)
    pos = [r0 for r0 in uniq if r0[4] == 1]
    neg = [r0 for r0 in uniq if r0[4] == 0]
    r = rng(); r.shuffle(pos); r.shuffle(neg)
    picked = pos[:PER] + neg[:PER]
    r.shuffle(picked)

    items = []
    for ch, dname, dis, icd, label in picked:
        items.append(Item(
            id=f"{SCENARIO}-{ch}-{icd}-{label}", scenario=SCENARIO, format="score_label",
            question=f"Is {dname} an effective (approved) treatment for {dis}?",
            gold={"label": label},
            gold_source="repoDB approved vs failed/terminated/withdrawn drug-indication",
            split="test",
            context_free_prompt=f"On a scale from 0 to 1, how confident are you that {dname} is an "
                                f"effective, approved treatment for {dis}?",
            entities={"drug": ch, "drug_name": dname, "disease": dis, "icd": icd},
            meta={"label": label, "direction": "protective"}))
    print(f"  crosswalked pairs: {len(uniq)} ({len(pos)} approved / {len(neg)} failed); "
          f"sampled {len(items)}")
    return items


if __name__ == "__main__":
    if not data_available():
        print(f"SKIP: LinkD data not found. Set DATABASE_DIR to enable {SCENARIO}.")
        raise SystemExit(0)
    items = build()
    if items:
        banner(SCENARIO, write_scenario(SCENARIO, items))
