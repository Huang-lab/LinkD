"""Readers for packaged source_data files."""
from __future__ import annotations

import pandas as pd

from . import paths


def read_table_s2() -> pd.DataFrame:
    return pd.read_excel(paths.source("TableS2_Benchmarking_LinkD.xlsx"))


def read_selectivity() -> pd.DataFrame:
    return pd.read_csv(paths.source("drug_selectivity_metrics.csv"))


def read_target_stats() -> pd.DataFrame:
    return pd.read_csv(paths.source("target_binding_stats.csv"))


def read_onco_genes() -> pd.DataFrame:
    return pd.read_csv(paths.source("onco_genes.csv"))


def read_known_dti() -> pd.DataFrame:
    return pd.read_csv(paths.source("opentarget_known_drug_pair.csv"))


def read_crispr() -> pd.DataFrame:
    return pd.read_csv(paths.source("known_drug_rank_crispr_cancer_driver_role.csv"))


def read_docking() -> pd.DataFrame:
    return pd.read_csv(paths.source("docking_scores_fig2fg.csv"))


def read_growth(drug: str) -> pd.DataFrame:
    name = {"propranolol": "Propranolol_growth.csv", "carvedilol": "Carvedilol_growth.csv"}[drug]
    return pd.read_csv(paths.source(name))


def read_vct(drug: str, table: str) -> pd.DataFrame:
    return pd.read_csv(paths.source(f"vct/{drug}/{table}"))


def read_ehr_ms() -> pd.DataFrame:
    return pd.read_csv(paths.source("TableS3_Mount_Sinai_Drug_Cancer.csv"))


def read_ehr_ukb() -> pd.DataFrame:
    return pd.read_csv(paths.source("TableS4_UK_Biobank_Drug_Disease.csv"))


def read_adrenergic() -> pd.DataFrame:
    return pd.read_csv(paths.source("adrenergic_selectivity_fig5.csv"))


def read_radar() -> pd.DataFrame:
    return pd.read_csv(paths.source("radar_egfr_jak1_fig2e.csv"))
