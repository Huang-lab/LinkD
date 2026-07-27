"""
repoDB drug-repositioning gold (approved vs failed drug-indication pairs), read
from the cached CSV extracted from the project's shiny.RData via pyreadr.

Status: data is unblocked and drugs map to LinkD ChEMBL (via LinkD's EHR DrugBank
metadata), but a high-quality T2 needs a proper UMLS-CUI -> ICD crosswalk — LinkD's
built-in DISEASE_MAP is cancer-centric, so the clean overlap is small and
approval-imbalanced. The loader is provided so T2 can be completed once a CUI->ICD
mapping is added.
"""
from __future__ import annotations
import os

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache", "repodb.csv")
FAILED = {"Terminated", "Withdrawn", "Suspended"}


def load_repodb():
    """Return repoDB as a DataFrame with an added boolean `approved` column, or None."""
    if not os.path.exists(CACHE):
        return None
    import pandas as pd
    df = pd.read_csv(CACHE)
    df["approved"] = (df["status"] == "Approved")
    return df


def drugbank_to_chembl(db):
    """Build a DrugBank-ID -> ChEMBL map from LinkD's EHR drug metadata."""
    m = {}
    for key in ("ehr_mount_sinai", "ehr_uk_biobank"):
        d = db.dfs.get(key)
        if d is None or "DrugBank ID" not in d.columns:
            continue
        col = "Drug Chembl ID" if "Drug Chembl ID" in d.columns else "Chembl ID"
        for dbid, ch in zip(d["DrugBank ID"].astype(str), d[col].astype(str)):
            if dbid.startswith("DB") and ch.startswith("CHEMBL"):
                m[dbid] = ch
    return m
