"""
Prefetch A2 disease data (cached): for each disease resolve EFO, get the
clinical-validation gold (disease-approved drug targets) and the OpenTargets
association ranking (the ToolUniverse-agent's answer). Writes cache/a2_diseases.json.
Network is hit once (with retries); subsequent runs are offline.

    python3 benchmark/external_data/a2_prefetch.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from benchmark.external_data import opentargets as ot

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache", "a2_diseases.json")

# (name OpenTargets resolves, ICD-10 for LinkD) — solid tumours + heme with targeted Rx
DISEASES = [
    ("melanoma", "C43"), ("non-small cell lung carcinoma", "C34"), ("breast carcinoma", "C50"),
    ("prostate carcinoma", "C61"), ("colorectal carcinoma", "C18"), ("pancreatic carcinoma", "C25"),
    ("ovarian carcinoma", "C56"), ("glioblastoma", "C71"), ("renal cell carcinoma", "C64"),
    ("gastric adenocarcinoma", "C16"), ("urinary bladder carcinoma", "C67"),
    ("hepatocellular carcinoma", "C22"), ("thyroid carcinoma", "C73"),
    ("head and neck squamous cell carcinoma", "C10"), ("cervical carcinoma", "C53"),
    ("endometrial carcinoma", "C54"), ("esophageal carcinoma", "C15"),
    ("chronic myeloid leukemia", "C92"), ("acute myeloid leukemia", "C92"),
    ("multiple myeloma", "C90"), ("non-Hodgkin lymphoma", "C85"),
    ("chronic lymphocytic leukemia", "C91"), ("neuroblastoma", "C74"), ("soft tissue sarcoma", "C49"),
    # more cancers
    ("small cell lung carcinoma", "C34"), ("mantle cell lymphoma", "C85"), ("follicular lymphoma", "C82"),
    ("gastrointestinal stromal tumor", "C26"), ("cholangiocarcinoma", "C22"), ("mesothelioma", "C45"),
    ("Hodgkin lymphoma", "C81"), ("medullary thyroid carcinoma", "C73"),
    # non-cancer with approved targeted therapies (broadens beyond oncology)
    ("rheumatoid arthritis", "M06"), ("psoriasis", "L40"), ("Crohn's disease", "K50"),
    ("ulcerative colitis", "K51"), ("asthma", "J45"), ("multiple sclerosis", "G35"),
    ("systemic lupus erythematosus", "M32"), ("atopic dermatitis", "L20"),
    ("type 2 diabetes mellitus", "E11"), ("ankylosing spondylitis", "M45"),
]


def main():
    out = {}
    for name, icd in DISEASES:
        efo = ot.disease_to_efo(name)
        if not efo:
            print(f"{name}: no EFO"); continue
        gold = ot.validated_targets(efo)
        ott = [g for g, _ in ot.associated_targets(efo, 60)]
        out[name] = {"efo": efo, "icd": icd, "gold": gold, "ot_top": ott}
        print(f"{name} [{efo}] icd={icd}: gold={len(gold)} ot_assoc={len(ott)} | {gold[:6]}")
    json.dump(out, open(OUT, "w"), indent=1)
    n_ok = sum(1 for v in out.values() if len(v["gold"]) >= 3)
    print(f"\nwrote {OUT}: {len(out)} diseases, {n_ok} with usable gold (>=3 targets)")


if __name__ == "__main__":
    main()
