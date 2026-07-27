"""
T7' — Selectivity / target-centric binder retrieval (LinkD-Select), manuscript-aligned.

The manuscript validates LinkD-Select *target-centrically*: it ranks all 14,981 drugs against a
target by selectivity-aware affinity, and the target's known (selective) binders rise to the top
(Fig 5a: ADRB2 → propranolol rank 1). We test exactly this: for a panel of well-studied targets,
each (drug, target) pair is labelled 1 if the drug is a KNOWN clinical binder of that target
(OpenTargets mechanism-of-action, independent of LinkD's binding training) and 0 for sampled
non-binder drugs. LinkD scores each pair by its predicted affinity; AUROC measures whether known
binders out-score random drugs across the full universe — something an LLM cannot do (it can only
name a handful of inhibitors, not rank the proteome).

    python3 benchmark/datasets/t7_sel_retrieval.py
"""
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from benchmark.datasets.base_builder import write_scenario, banner, data_available, rng, REPO_ROOT
from benchmark.schema import Item

SCENARIO = "t7_sel_retrieval"
N_TARGETS = int(os.getenv("BENCH_T7_TARGETS", "20"))
MAX_POS = int(os.getenv("BENCH_T7_POS", "12"))      # known binders per target
NEG_RATIO = int(os.getenv("BENCH_T7_NEGR", "3"))    # random negatives per positive


def build():
    from benchmark.datasets.a2_target_id import CACHE
    from benchmark.external_data import opentargets as ot
    from agent.database_query_module import load_database_subset
    if not os.path.exists(CACHE):
        print("  a2_diseases.json missing — run the A2 prefetch first.")
        return []
    db = load_database_subset({"target_binding_stats", "drug_umap"})
    genes_bind = set(db.dfs["target_binding_stats"]["Gene"].dropna().astype(str))
    umap = db.dfs.get("drug_umap")
    if umap is None or "Drug Chembl ID" not in umap.columns:
        print("  drug_umap unavailable.")
        return []
    name_by_chembl = {str(c): str(n) for c, n in zip(umap["Drug Chembl ID"], umap.get("Drug Name", umap["Drug Chembl ID"]))}
    universe = [c for c in name_by_chembl if c.startswith("CHEMBL")]
    uni_set = set(universe)

    # invert cached OT approved-drug MoA -> target gene -> known clinical drugs (chembl)
    data = json.load(open(CACHE))
    tgt2drugs = collections.defaultdict(set)
    for _name, info in data.items():
        efo = info.get("efo")
        if not efo:
            continue
        try:
            chembls = ot.approved_drug_chembls(efo)
        except Exception:
            continue
        for ch, _dn in chembls:
            try:
                for g in ot.drug_targets(ch):
                    tgt2drugs[g].add(ch)
            except Exception:
                continue
    cand = [(g, d & uni_set) for g, d in tgt2drugs.items() if g in genes_bind and len(d & uni_set) >= 4]
    cand.sort(key=lambda x: -len(x[1]))
    cand = cand[:N_TARGETS]

    r = rng()
    items = []
    for gene, gold in cand:
        gold = list(gold)[:MAX_POS]
        gold_set = set(gold)
        # negatives: random universe drugs that are NOT known binders of this target
        pool = [d for d in universe if d not in gold_set]
        r.shuffle(pool)
        negs = pool[:len(gold) * NEG_RATIO]
        for ch in gold + negs:
            label = 1 if ch in gold_set else 0
            name = name_by_chembl.get(ch, ch)
            items.append(Item(
                id=f"{SCENARIO}-{gene}-{ch}-{label}", scenario=SCENARIO, format="score_label",
                question=f"Is {name} a selective binder of {gene}?",
                gold={"label": label},
                gold_source="OpenTargets mechanism-of-action known drugs (positive) vs sampled non-binders",
                split="test",
                context_free_prompt=f"On a scale from 0 to 1, how likely is the drug {name} to be a "
                                    f"potent, selective binder of the human protein {gene}? Output only the number.",
                entities={"drug": ch, "drug_name": name, "gene": gene},
                meta={"label": label, "target": gene}))
    n_pos = sum(i.gold["label"] for i in items)
    print(f"  T7': {len(cand)} targets, {len(items)} (drug,target) pairs "
          f"({n_pos} known binders / {len(items) - n_pos} negatives)")
    return items


if __name__ == "__main__":
    if not data_available():
        print(f"SKIP: LinkD data not found. Set DATABASE_DIR to enable {SCENARIO}.")
        raise SystemExit(0)
    items = build()
    if items:
        banner(SCENARIO, write_scenario(SCENARIO, items))
