"""
C1 — Integrative target-disease validation (AUROC). Triads (drug, gene, disease):
  positive = an APPROVED drug for the disease acting on its TRUE mechanism target
             (OpenTargets approved drug + its mechanism-of-action gene);
  negative = the same approved drug paired with a DECOY gene (a real gene that is
             not a validated target for that disease).
LinkD scores the full triad with its weighted multi-evidence `final_score` (binding +
CRISPR + EHR + causal + clinical + TPI fusion); comparators score (gene, disease).
This is the test of evidence *fusion*: does combining layers separate true from decoy?

    python3 benchmark/datasets/c1_validate.py    (needs the A2 prefetch cache)
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from benchmark.datasets.base_builder import write_scenario, banner, data_available, rng, REPO_ROOT
from benchmark.datasets.a2_target_id import CACHE, CANCER_RE
from benchmark.schema import Item

SCENARIO = "c1_validate"
N_DIS = int(os.getenv("BENCH_C1_DIS", "20"))     # diseases
PER = int(os.getenv("BENCH_C1_PER", "4"))        # positives per disease (matched negatives)


def _gene_universe():
    import pandas as pd
    dbdir = os.getenv("DATABASE_DIR") or os.path.join(REPO_ROOT, "Database")
    root = os.path.dirname(dbdir)
    tbs = pd.read_csv(os.path.join(root, "DrugTargetMetrics", "target_binding_stats.csv"), usecols=["Gene"])
    return [str(g) for g in tbs["Gene"].dropna().unique()]


def build():
    if not os.path.exists(CACHE):
        print("  a2_diseases.json missing — run the A2 prefetch first.")
        return []
    from benchmark.external_data import opentargets as ot
    data = json.load(open(CACHE))
    universe = _gene_universe(); uni_set = set(universe)
    r = rng()
    items = []
    n_dis = 0
    for name, info in data.items():
        if not CANCER_RE.search(name) or n_dis >= N_DIS:
            continue
        efo, icd = info.get("efo"), info.get("icd")
        gold = set(info.get("gold", []))
        if not efo or len(gold) < 3:
            continue
        # approved drugs for this disease (chembl, name), and each drug's true MoA target genes
        try:
            chembls = ot.approved_drug_chembls(efo)
        except Exception:
            continue
        pos = []
        drug_targets_by_chembl = {}
        for ch, dname in chembls:
            try:
                tgts = [g for g in ot.drug_targets(ch) if g in uni_set]
            except Exception:
                tgts = []
            drug_targets_by_chembl[ch] = set(tgts)
            for g in tgts:
                pos.append((ch, dname, g))
        # unique by (chembl, gene), capped
        seen = set()
        pos = [p for p in pos if not ((p[0], p[2]) in seen or seen.add((p[0], p[2])))][:PER]
        if len(pos) < 2:
            continue
        n_dis += 1
        used_item_ids = set()
        for ch, dname, g in pos:
            # HARD decoy: another validated target OF THE SAME DISEASE (not this drug's target).
            # Disease-level association (OpenTargets / LLM) can't tell which target THIS drug
            # hits; only LinkD's drug-target-specific evidence (binding/CRISPR) can.
            true_drug_targets = drug_targets_by_chembl.get(ch, {g})
            decoy_pool = [x for x in gold if x not in true_drug_targets]
            if not decoy_pool:
                continue
            r.shuffle(decoy_pool)
            pos_item = _item(name, efo, icd, ch, dname, g, 1)
            neg_item = None
            for dg in decoy_pool:
                cand = _item(name, efo, icd, ch, dname, dg, 0)
                if cand.id not in used_item_ids:
                    neg_item = cand
                    break
            if neg_item is None:
                continue
            used_item_ids.add(pos_item.id)
            used_item_ids.add(neg_item.id)
            items.append(pos_item)
            items.append(neg_item)
    return items


def _item(name, efo, icd, chembl, dname, gene, label):
    return Item(
        id=f"{SCENARIO}-{name.replace(' ', '_')}-{chembl}-{gene}-{label}",
        scenario=SCENARIO, format="score_label",
        question=f"Is gene {gene} the validated drug target of {chembl} in {name}?",
        gold={"label": label},
        gold_source="OpenTargets approved drug + mechanism-of-action target (positive) vs decoy gene",
        split="test",
        context_free_prompt=f"On a scale from 0 to 1, how confident are you that the human gene "
                            f"{gene} is an established therapeutic drug target in {name}?",
        entities={"drug": chembl, "drug_name": dname, "gene": gene,
                  "disease": name, "efo": efo, "icd": icd},
        meta={"label": label})


if __name__ == "__main__":
    if not data_available():
        print(f"SKIP: LinkD data not found. Set DATABASE_DIR to enable {SCENARIO}.")
        raise SystemExit(0)
    items = build()
    if items:
        banner(SCENARIO, write_scenario(SCENARIO, items))
    else:
        print("  no C1 items (prefetch a2_diseases.json first).")
