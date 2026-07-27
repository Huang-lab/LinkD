"""
D1' — Curated protective-association validation (LinkD-Pheno EHR), manuscript-aligned.

The manuscript validates LinkD-Pheno via protective drug–cancer associations (OR<1) confirmed by
target-trial emulation (e.g. azelastine–liver OR=0.69, tretinoin–thyroid OR=0.43, β-blockers–
prostate). A large-scale AUROC benchmark is NOT viable — the EHR cohorts are cancer-specific and
overlap external indication gold on too few (drug, cancer) pairs (≈3/120 for repoDB). So we report
a transparent CURATED validation: for a panel of literature-supported protective drug→cancer pairs,
does LinkD's real-world EHR odds ratio recover the expected protective signal (OR<1, p<0.05)?

    python3 benchmark/datasets/d1_protective.py        # prints a markdown validation table
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from benchmark.datasets.base_builder import data_available  # noqa: E402

# Literature-supported protective drug→cancer associations (pharmacoepidemiology + the manuscript).
# (drug_name, ICD-10 prefix, cancer label, short literature note)
CURATED = [
    ("propranolol", "C61", "prostate cancer", "β-blocker; Brohée 2018 (manuscript)"),
    ("carvedilol", "C61", "prostate cancer", "β-blocker; anti-tumor (manuscript)"),
    ("metoprolol", "C61", "prostate cancer", "β-blocker class effect"),
    ("propranolol", "C43", "melanoma", "β-blocker; reduced progression"),
    ("carvedilol", "C43", "melanoma", "β-blocker; Farhoumand 2022"),
    ("tretinoin", "C73", "thyroid cancer", "retinoid; OR=0.43 (manuscript)"),
    ("azelastine", "C22", "liver cancer", "OR=0.69 (manuscript)"),
    ("metformin", "C50", "breast cancer", "biguanide; meta-analyses protective"),
    ("metformin", "C18", "colorectal cancer", "biguanide; protective"),
    ("metformin", "C61", "prostate cancer", "biguanide; protective"),
    ("metformin", "C25", "pancreatic cancer", "biguanide; protective"),
    ("aspirin", "C18", "colorectal cancer", "NSAID; chemoprevention (strong)"),
    ("aspirin", "C20", "rectal cancer", "NSAID; chemoprevention"),
    ("aspirin", "C16", "gastric cancer", "NSAID; protective"),
    ("celecoxib", "C18", "colorectal cancer", "COX-2 inhibitor; chemoprevention"),
    ("atorvastatin", "C61", "prostate cancer", "statin; protective (mixed)"),
    ("simvastatin", "C18", "colorectal cancer", "statin; protective (mixed)"),
    ("hydroxychloroquine", "C50", "breast cancer", "autophagy; adjuvant interest"),
    ("itraconazole", "C61", "prostate cancer", "Hedgehog; repurposing candidate"),
    ("disulfiram", "C61", "prostate cancer", "ALDH; repurposing candidate"),
]


def validate():
    from agent.database_query_module import load_database_subset
    db = load_database_subset({"ehr_mount_sinai", "ehr_uk_biobank"})

    def best_or(name, icd):
        ehr = db.get_ehr_drug_disease_associations(drug_name=name, icd_code=icd)
        if ehr is None or ehr.empty:
            return None
        cols = [c for c in ("logit_or", "odds_ratio") if c in ehr.columns]
        best = None
        for _, row in ehr.iterrows():
            o = None
            for c in cols:
                try:
                    o = float(row.get(c)); break
                except (TypeError, ValueError):
                    pass
            if o is None or o != o or o <= 0:
                continue
            try:
                p = float(row.get("logit_p"))
            except (TypeError, ValueError):
                p = None
            if best is None or (p is not None and (best[1] is None or p < best[1])):
                best = (o, p)
        return best

    rows, covered, recovered = [], 0, 0
    for name, icd, label, note in CURATED:
        b = best_or(name, icd)
        if b is None:
            rows.append((name, label, icd, "—", "—", "no EHR data", note))
            continue
        covered += 1
        orv, p = b
        ok = orv < 1.0 and (p is not None and p < 0.05)
        recovered += int(ok)
        rows.append((name, label, icd, f"{orv:.2f}", ("%.1e" % p if p is not None else "—"),
                     "✓ protective" if ok else ("protective (n.s.)" if orv < 1 else "not protective"), note))

    print("## D1' — Curated protective-association validation (LinkD-Pheno EHR)\n")
    print(f"_Covered by LinkD EHR: {covered}/{len(CURATED)} curated pairs; "
          f"of those, {recovered}/{covered} show the expected protective signal (OR<1, p<0.05)._\n")
    print("| Drug | Cancer | ICD | LinkD OR | p | Recovered? | Literature |")
    print("|---|---|---|---|---|---|---|")
    for r in rows:
        print("| " + " | ".join(r) + " |")
    return rows


if __name__ == "__main__":
    if not data_available():
        print("SKIP: LinkD data not found (set DATABASE_DIR).")
        raise SystemExit(0)
    validate()
