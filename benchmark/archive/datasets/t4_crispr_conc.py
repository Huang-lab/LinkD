"""
T4' — CRISPR concordance discrimination (LinkD-Pheno), manuscript-aligned.

The manuscript validates LinkD-Pheno by drug-response↔CRISPR-dependency concordance: annotated
drug–target pairs show strong functional correlation (|ρ|≥0.40, FDR), recovering ChEMBL pairs
(Fig 3). We test that signal directly: positives are the screen's ChEMBL-annotated drug–target
pairs; negatives are the SAME drugs paired with another gene that is ALSO measured in the screen
(so both are measured — no coverage artifact). LinkD scores each pair by |AUC_corr|; AUROC measures
whether the annotated target out-correlates a random measured gene.

    python3 benchmark/datasets/t4_crispr_conc.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from benchmark.datasets.base_builder import write_scenario, banner, data_available, rng
from benchmark.schema import Item

SCENARIO = "t4_crispr_conc"
PER = int(os.getenv("BENCH_T4_PER", "120"))   # cap per class


def build():
    from agent.database_query_module import load_database_subset
    db = load_database_subset({"drug_response"})
    dr = db.dfs.get("drug_response")
    if dr is None or "ChEMBL_ID" not in dr.columns:
        print("  drug_response unavailable.")
        return []
    dr = dr.copy()
    dr["ChEMBL_ID"] = dr["ChEMBL_ID"].astype(str)
    dr = dr[dr["ChEMBL_ID"].str.startswith("CHEMBL")]
    name_by_chembl = dict(zip(dr["ChEMBL_ID"], dr.get("drugs", dr["ChEMBL_ID"]).astype(str)))
    # positives = annotated MoA pairs: rows with a populated resolved-target 'Gene' (sparse).
    ann = dr.dropna(subset=["Gene"]) if "Gene" in dr.columns else dr.iloc[0:0]
    pos_pairs = sorted(set(zip(ann["ChEMBL_ID"], ann["Gene"].astype(str))))
    # matched negatives drawn from 'genes' = EVERY measured gene for the drug (464k rows), so both
    # classes are measured in the screen (no coverage artifact).
    measured = {}
    for ch, grp in dr.groupby("ChEMBL_ID"):
        measured[ch] = set(grp["genes"].astype(str))

    r = rng(); r.shuffle(pos_pairs)
    pos_pairs = pos_pairs[:PER]
    pos_set = set(pos_pairs)
    items = []
    for ch, g in pos_pairs:
        items.append(_item(ch, name_by_chembl.get(ch, ch), g, 1))
        # matched negative: another measured gene for THIS drug that isn't an annotated target
        cand = [x for x in measured.get(ch, ()) if (ch, x) not in pos_set and x not in ("nan", g)]
        if cand:
            items.append(_item(ch, name_by_chembl.get(ch, ch), cand[r.randrange(len(cand))], 0))
    n_pos = sum(i.gold["label"] for i in items)
    print(f"  T4': {len(items)} (drug,gene) pairs over {len(set(c for c, _ in pos_pairs))} screen drugs "
          f"({n_pos} annotated / {len(items) - n_pos} matched-random)")
    return items


def _item(chembl, name, gene, label):
    return Item(
        id=f"{SCENARIO}-{chembl}-{gene}-{label}", scenario=SCENARIO, format="score_label",
        question=f"Does {name} functionally depend on {gene} (CRISPR concordance)?",
        gold={"label": label},
        gold_source="PRISM/GDSC drug-response × DepMap CRISPR; ChEMBL-annotated target (pos) vs measured non-target (neg)",
        split="test",
        context_free_prompt=f"On a scale from 0 to 1, how strongly does the anticancer activity of {name} "
                            f"depend on the gene {gene} (i.e., is {gene} its functional target)? Output only the number.",
        entities={"drug": chembl, "drug_name": name, "gene": gene},
        meta={"label": label})


if __name__ == "__main__":
    if not data_available():
        print(f"SKIP: LinkD data not found. Set DATABASE_DIR to enable {SCENARIO}.")
        raise SystemExit(0)
    items = build()
    if items:
        banner(SCENARIO, write_scenario(SCENARIO, items))
