"""
T5' — Multi-evidence concordance / drug–target recovery (LinkD fusion), manuscript-aligned.

The manuscript's integrative result is concordance-based discovery: drug–target pairs are
recovered by combining binding, selectivity, and CRISPR drug-response concordance (Fig 3; 211
ChEMBL-annotated + 34 novel pairs at |ρ|≥0.40, FDR≥20). We test the fusion directly: positives are
ChEMBL/OpenTargets-annotated drug–target pairs; negatives are the same drugs paired with a random
human gene. LinkD scores each pair with its weighted multi-evidence final_score; AUROC measures
whether the fusion separates real pairs from random.

    python3 benchmark/datasets/t5_concordance.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from benchmark.datasets.base_builder import write_scenario, banner, data_available, rng
from benchmark.schema import Item

SCENARIO = "t5_concordance"
PER = int(os.getenv("BENCH_T5_PER", "90"))   # cap per class (positive pairs / negative pairs)


def build():
    from benchmark.datasets.a2_target_id import CACHE
    from benchmark.external_data import opentargets as ot
    from agent.database_query_module import load_database_subset
    if not os.path.exists(CACHE):
        print("  a2_diseases.json missing — run the A2 prefetch first.")
        return []
    db = load_database_subset({"target_binding_stats", "drug_umap"})
    genes_bind = sorted(set(db.dfs["target_binding_stats"]["Gene"].dropna().astype(str)))
    gene_set = set(genes_bind)
    umap = db.dfs.get("drug_umap")
    name_by_chembl = {str(c): str(n) for c, n in zip(umap["Drug Chembl ID"], umap.get("Drug Name", umap["Drug Chembl ID"]))}
    uni_set = {c for c in name_by_chembl if c.startswith("CHEMBL")}

    data = json.load(open(CACHE))
    pos_pairs = set()
    for _name, info in data.items():
        efo = info.get("efo")
        if not efo:
            continue
        try:
            chembls = ot.approved_drug_chembls(efo)
        except Exception:
            continue
        for ch, _dn in chembls:
            if ch not in uni_set:
                continue
            try:
                for g in ot.drug_targets(ch):
                    if g in gene_set:
                        pos_pairs.add((ch, g))
            except Exception:
                continue
    pos_pairs = list(pos_pairs)
    r = rng(); r.shuffle(pos_pairs)
    pos_pairs = pos_pairs[:PER]
    known = set(pos_pairs)
    drugs = [c for c, _ in pos_pairs]

    items = []
    for ch, g in pos_pairs:
        items.append(_item(ch, name_by_chembl.get(ch, ch), g, 1))
    # negatives: same drugs × random gene that is NOT a known target of that drug
    for ch in drugs:
        for _ in range(6):
            g = genes_bind[r.randrange(len(genes_bind))]
            if (ch, g) not in known:
                items.append(_item(ch, name_by_chembl.get(ch, ch), g, 0))
                break
    n_pos = sum(i.gold["label"] for i in items)
    print(f"  T5': {len(items)} (drug,gene) tri_pairs ({n_pos} ChEMBL-annotated / {len(items) - n_pos} random)")
    return items


def _item(chembl, name, gene, label):
    return Item(
        id=f"{SCENARIO}-{chembl}-{gene}-{label}", scenario=SCENARIO, format="score_label",
        question=f"Is {gene} a validated target of {name}?",
        gold={"label": label},
        gold_source="ChEMBL/OpenTargets mechanism-of-action drug–target pair (positive) vs random gene",
        split="test",
        context_free_prompt=f"On a scale from 0 to 1, how confident are you that the human gene {gene} "
                            f"is a validated molecular target of the drug {name}? Output only the number.",
        entities={"drug": chembl, "drug_name": name, "gene": gene},
        meta={"label": label})


if __name__ == "__main__":
    if not data_available():
        print(f"SKIP: LinkD data not found. Set DATABASE_DIR to enable {SCENARIO}.")
        raise SystemExit(0)
    items = build()
    if items:
        banner(SCENARIO, write_scenario(SCENARIO, items))
