"""
L9 — Adverse-event / safety (LinkD EHR risk layer). For drugs in LinkD's EHR cohorts,
each EHR drug-disease association is labelled by whether that condition is a
FAERS-reported adverse event for the drug (openFDA). LinkD's EHR risk odds-ratio
(OR>1 = increased risk) is the predictor; base LLMs estimate it from the drug name.
Metric = AUROC. (Honest caveat: LinkD EHR encodes ICD disease-associations while FAERS
encodes MedDRA adverse-event terms — only lexically-matchable conditions are usable.)

    python3 benchmark/datasets/l9_safety.py
"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from benchmark.datasets.base_builder import write_scenario, banner, data_available, REPO_ROOT
from benchmark.schema import Item

SCENARIO = "l9_safety"
CAP_DRUGS = int(os.getenv("BENCH_L9_DRUGS", "60"))


def _match(disease: str, reactions: dict) -> bool:
    """Lexical match of a LinkD ICD disease name to a FAERS MedDRA reaction term."""
    d = {t for t in disease.lower().replace(",", " ").split() if len(t) > 3}
    if not d:
        return False
    for term, cnt in reactions.items():
        if cnt < 20:
            continue
        rt = set(term.split())
        if d & rt and (d <= rt or rt <= d or len(d & rt) >= 2):
            return True
    return False


def build():
    from agent.database_query_module import load_database_subset
    from benchmark.external_data import openfda
    db = load_database_subset({"ehr_mount_sinai", "ehr_uk_biobank"})
    ukb = db.dfs.get("ehr_uk_biobank")
    if ukb is None or "Drug Name" not in ukb.columns:
        print("  no EHR drug names.")
        return []
    drugs = (ukb[["Drug Name", "Drug Chembl ID"]].dropna().drop_duplicates())
    items = []
    n_drugs = 0
    for name, chembl in zip(drugs["Drug Name"].astype(str), drugs["Drug Chembl ID"].astype(str)):
        if n_drugs >= CAP_DRUGS:
            break
        reactions = openfda.top_reactions(name)
        if not reactions:
            continue
        ehr = db.get_ehr_drug_disease_associations(drug_id=chembl, drug_name=name)
        if ehr is None or ehr.empty:
            continue
        n_drugs += 1
        cols = [c for c in ("logit_or", "odds_ratio") if c in ehr.columns]
        seen = set()
        for _, row in ehr.iterrows():
            icd = str(row.get("ICD10", row.get("ICD_Code", "")))
            disease = db.get_disease_name_from_icd(icd) or ""
            if not disease or icd in seen:
                continue
            orv = next((row.get(c) for c in cols if _num(row.get(c)) is not None), None)
            orv = _num(orv)
            if orv is None or orv <= 0:
                continue
            seen.add(icd)
            label = 1 if _match(disease, reactions) else 0
            items.append(Item(
                id=f"{SCENARIO}-{chembl}-{icd}", scenario=SCENARIO, format="score_label",
                question=f"Is {disease} a reported adverse event of {name}?",
                gold={"label": label},
                gold_source="openFDA FAERS reported adverse reactions (MedDRA) vs LinkD EHR conditions",
                split="test",
                context_free_prompt=f"On a scale from 0 to 1, how likely is {disease} to be a reported "
                                    f"adverse event / safety risk of the drug {name}? Output only the number.",
                entities={"drug": chembl, "drug_name": name, "icd": icd, "disease": disease},
                meta={"label": label, "odds_ratio": round(orv, 3), "direction": "risk"}))
    # balance classes (FAERS gives far more negatives than lexical-positive matches)
    pos = [i for i in items if i.gold["label"] == 1]
    neg = [i for i in items if i.gold["label"] == 0]
    k = min(len(pos), len(neg))
    out = pos[:k] + neg[:k]
    print(f"  L9: {len(items)} EHR-conditions over {n_drugs} drugs -> "
          f"{len(pos)} AE-positive / {len(neg)} negative; balanced to {len(out)}")
    return out


def _num(v):
    try:
        f = float(v)
        return None if f != f else f
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    if not data_available():
        print(f"SKIP: LinkD data not found. Set DATABASE_DIR to enable {SCENARIO}.")
        raise SystemExit(0)
    items = build()
    if items:
        banner(SCENARIO, write_scenario(SCENARIO, items))
    else:
        print("  no L9 items (openFDA unreachable or no lexical matches).")
