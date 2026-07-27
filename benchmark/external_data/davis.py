"""
Load the TDC DAVIS drug-target binding benchmark and align it to LinkD's entity
space (ChEMBL drug IDs + gene-named targets). Experimental Kd (nM) -> pKd.
"""
from __future__ import annotations
import math
import os

TDC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache", "tdc")


def tdc_available() -> bool:
    try:
        import tdc  # noqa: F401
        return True
    except Exception:
        return False


def load_davis():
    """Return DAVIS as a DataFrame with columns Drug_ID(CID), Drug(SMILES),
    Target_ID(gene), Y(Kd nM), pkd_exp. None if PyTDC is unavailable/offline."""
    if not tdc_available():
        return None
    from tdc.multi_pred import DTI
    df = DTI(name="DAVIS", path=TDC_PATH).get_data().copy()
    df["pkd_exp"] = df["Y"].apply(lambda v: 9.0 - math.log10(max(float(v), 1e-4)))
    return df


def align_to_linkd(df, db):
    """Add `chembl` (mapped from CID) and `gene` (normalized) columns and keep only
    rows whose drug is in LinkD's binding matrix and whose target maps to a LinkD gene.
    """
    from benchmark.external_data.idmap import map_cids, normalize_gene
    drug_idx = set(db._parquet_drug_index.keys())
    known_genes = {g.upper() for g in db.dfs["target_binding_stats"]["Gene"].dropna().astype(str)}

    cmap = map_cids(df["Drug_ID"].astype(str).unique().tolist())
    df = df.copy()
    df["chembl"] = df["Drug_ID"].astype(str).map(cmap.get)
    df["gene"] = df["Target_ID"].astype(str).map(lambda t: normalize_gene(t, known_genes))
    keep = df["chembl"].isin(drug_idx) & df["gene"].isin(known_genes)
    return df[keep].reset_index(drop=True)
