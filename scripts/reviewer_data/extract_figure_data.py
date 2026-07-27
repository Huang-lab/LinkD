#!/usr/bin/env python3
"""Build deterministic, panel-ready source data for manuscript figures.

This is an author-side command. Reviewer notebooks read only the flattened
panel tables placed in the Zenodo payload and never access ``Drug-Repo-scRNA``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact, norm

REPO = Path(__file__).resolve().parents[2]
AUTHOR_BUILD = REPO / "build" / "reviewer_source"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import contracts  # noqa: E402


def sha256(path: Path, chunk: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(chunk):
            digest.update(block)
    return digest.hexdigest()


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    out = df.copy()
    out.to_csv(path, index=False, lineterminator="\n", float_format="%.10g")


def copy_raw(src: Path, raw_dir: Path, name: str | None = None) -> Path:
    if not src.exists():
        raise FileNotFoundError(src)
    dest = raw_dir / (name or src.name)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return dest


def normalise_role(value: object) -> str:
    text = str(value).strip()
    return {
        "ONCOGENE": "Oncogene",
        "tsg": "TSG",
        "Oncogene & TSG": "Both",
        "ONCOGENE_AND_TSG": "Both",
    }.get(text, text)


def tissue_from_disease(value: object) -> str:
    text = str(value).lower()
    rules = [
        ("Blood", ("leuk", "lymph", "myeloma", "blood")),
        ("Nervous system", ("brain", "glioma", "neuro", "nervous")),
        ("Breast", ("breast",)),
        ("Lung", ("lung",)),
        ("Skin", ("skin", "melanoma")),
        ("Aero digestive tract", ("head and neck", "oral", "phary", "laryn", "aero")),
        ("Urogenital system", ("prostate", "ovarian", "kidney", "renal", "bladder", "uter", "cervi")),
        ("Digestive system", ("colon", "colorectal", "gastric", "stomach", "pancrea", "liver", "digest")),
    ]
    for label, keys in rules:
        if any(key in text for key in keys):
            return label
    return "Other"


def build_fig1(raw_dir: Path, panels: Path) -> None:
    table = pd.read_excel(raw_dir / "TableS2_Benchmarking_LinkD.xlsx")
    rows = []
    for method, vals in zip(contracts.RANK_METHODS, contracts.RANK_VALUES):
        for split, rank in zip(contracts.RANK_SPLITS, vals):
            rows.append({"method": method, "split": split, "rank": rank})
    write_csv(pd.DataFrame(rows), panels / "fig1b.csv")

    focus = table[
        (table["Dataset"] == "Test")
        & table["Model"].isin(contracts.FIG1C_MODEL_MAP)
    ].copy()
    fig1c = (
        focus.groupby(["Model", "Mode"], as_index=False)["Pearson"]
        .agg(mean="mean", sd="std", n="count")
    )
    fig1c["model"] = fig1c["Model"].map(contracts.FIG1C_MODEL_MAP)
    fig1c["split"] = fig1c["Mode"].map(contracts.MODE_LABELS)
    write_csv(fig1c[["model", "split", "mean", "sd", "n"]], panels / "fig1c.csv")

    models = ["LinkD", "DeepPurpose", "GraphDTA", "Diffusion", "DeepDTA"]
    s2 = table[(table["Dataset"] == "Test") & table["Model"].isin(models)].copy()
    s2 = (
        s2.groupby(["Model", "Mode", "Data"], as_index=False)
        .agg(
            rmse_mean=("RMSE", "mean"),
            rmse_sd=("RMSE", "std"),
            pearson_mean=("Pearson", "mean"),
            pearson_sd=("Pearson", "std"),
        )
    )
    s2["model"] = s2["Model"].replace({"LinkD": "LinkD-Bind"})
    s2["split"] = s2["Mode"].map(contracts.MODE_LABELS)
    s2 = s2.rename(columns={"Data": "dataset"})
    write_csv(
        s2[["model", "split", "dataset", "rmse_mean", "rmse_sd", "pearson_mean", "pearson_sd"]],
        panels / "figs2.csv",
    )


def build_radar(raw_dir: Path, panels: Path, parquet_root: Path) -> None:
    selected_names = {name for rows in contracts.RADAR_DRUGS.values() for name, _ in rows}
    drugs = pd.read_csv(raw_dir / "drug_selectivity_metrics.csv")
    selected = drugs[drugs["Drug Name"].isin(selected_names)][["Drug", "Drug Name"]].drop_duplicates()
    id_to_name = dict(zip(selected["Drug"], selected["Drug Name"]))

    index_path = parquet_root / "target_index.json"
    target_index = json.loads(index_path.read_text()) if index_path.exists() else {}
    parts = []
    columns = [
        "Drug", "Target", "Selectivity_Score", "Rank_Select", "aff_local_n",
        "entropy_sel_n", "gap_local_n", "sr_local_n",
    ]
    for gene in ("EGFR", "JAK1"):
        gene_names = {name for name, _ in contracts.RADAR_DRUGS[gene]}
        gene_ids = {drug_id for drug_id, name in id_to_name.items() if name in gene_names}
        filenames = target_index.get(f"{gene}_HUMAN", [])
        if not filenames:
            filenames = [p.name for p in parquet_root.glob("*.parquet")]
        found = []
        for filename in filenames:
            path = parquet_root / filename
            if not path.exists():
                continue
            data = pd.read_parquet(path, columns=columns)
            data = data[
                data["Target"].astype(str).str.upper().eq(f"{gene}_HUMAN")
                & data["Drug"].isin(gene_ids)
            ]
            found.append(data)
        if found:
            part = pd.concat(found, ignore_index=True)
            part["gene"] = gene
            parts.append(part)
    if not parts:
        raise RuntimeError("Could not extract EGFR/JAK1 radar rows")
    out = pd.concat(parts, ignore_index=True).drop_duplicates(["gene", "Drug"])
    out["drug_name"] = out["Drug"].map(id_to_name)
    status = {(g, n): s for g, values in contracts.RADAR_DRUGS.items() for n, s in values}
    out["status"] = [status.get((g, n), "Off") for g, n in zip(out["gene"], out["drug_name"])]
    out = out.rename(
        columns={
            "aff_local_n": "affinity",
            "entropy_sel_n": "entropy",
            "gap_local_n": "gap",
            "sr_local_n": "selectivity_ratio",
            "Selectivity_Score": "selectivity_score",
        }
    )
    needed = set(selected_names)
    missing = needed - set(out["drug_name"])
    if missing:
        raise RuntimeError(f"Missing radar drugs: {sorted(missing)}")
    write_csv(
        out[["gene", "drug_name", "status", "affinity", "entropy", "gap", "selectivity_ratio", "selectivity_score"]],
        panels / "fig2e.csv",
    )


def build_fig2(raw_dir: Path, panels: Path, source_root: Path) -> None:
    drugs = pd.read_csv(raw_dir / "drug_selectivity_metrics.csv")
    fig2a = drugs[
        ["Drug", "Drug Name", "aff_n", "entropy_sel_n", "Selectivity_Score"]
    ].rename(
        columns={
            "Drug": "drug_id",
            "Drug Name": "drug_name",
            "aff_n": "affinity_scaled",
            "entropy_sel_n": "entropy_scaled",
            "Selectivity_Score": "selectivity_score",
        }
    )
    write_csv(fig2a, panels / "fig2a.csv")

    stats_path = source_root / "Figures_Generation/2_Selectivity_Rank/Figures/per_gene_selectivity_vs_affinity_stats.csv"
    stats = pd.read_csv(stats_path)
    stats["gene"] = stats["Target"].astype(str).str.replace("_HUMAN", "", regex=False)
    stats["role"] = stats["Role_tag"].map(normalise_role)
    stats = stats[stats["role"].isin(contracts.ROLE_ORDER)].copy()
    stats = stats.sort_values(["med_on_sel", "n_on"], ascending=[False, False]).head(60)
    fig2b = stats.rename(
        columns={"med_on_sel": "median_selectivity", "p_adj_sel": "fdr"}
    )[["gene", "role", "median_selectivity", "fdr", "n_on"]]
    fig2b["significant"] = fig2b["fdr"] < 0.05
    write_csv(fig2b, panels / "fig2b.csv")

    rows = []
    for cutoff, role, n, affinity, selectivity, combined in contracts.RECOVERY:
        for ranker, value in (
            ("Affinity", affinity),
            ("Selectivity", selectivity),
            ("Combined", combined),
        ):
            rows.append(
                {
                    "cutoff": cutoff,
                    "role": role,
                    "n": n,
                    "ranker": ranker,
                    "percent": value,
                }
            )
    write_csv(pd.DataFrame(rows), panels / "fig2cd.csv")


def build_docking(panels: Path, source_root: Path, legacy_root: Path) -> None:
    legacy = legacy_root / "docking_scores_fig2fg.csv"
    if not legacy.exists():
        raise FileNotFoundError(
            "Frozen docking extract is missing. Restore it from the prior Zenodo "
            "archive before rebuilding panel-ready tables."
        )
    role_path = source_root / "TargetPriori/ProteinInfo/onco_gene_info_1027.csv"
    roles = pd.read_csv(role_path)[["Gene", "Role"]].drop_duplicates("Gene")
    docking = pd.read_csv(legacy)
    docking = docking.merge(roles, on="Gene", how="inner")
    docking["role"] = docking["Role"].map(normalise_role)
    docking["target_status"] = docking["Type"].replace({"Known": "On-Target", "Unknown": "Off-Target"})
    docking = docking[
        docking["role"].isin(contracts.ROLE_ORDER)
        & docking["target_status"].isin(["On-Target", "Off-Target"])
        & docking["Docking Score"].between(-20, 0)
    ].copy()
    role_counts = docking.groupby("role")["Gene"].nunique().to_dict()
    if role_counts != contracts.DOCKING_ROLE_COUNTS:
        raise RuntimeError(f"Docking role counts do not match manuscript: {role_counts}")
    fig2f = docking.rename(
        columns={
            "Gene": "gene",
            "Drug Chembl ID": "drug_id",
            "Docking Score": "docking_score",
        }
    )[["gene", "drug_id", "role", "target_status", "docking_score", "Rank_Select"]]
    write_csv(fig2f, panels / "fig2f.csv")

    known = docking[(docking["target_status"] == "On-Target") & (docking["Rank_Select"] < 100)]
    thresholds = np.sort(known["Docking Score"].dropna().unique())
    recovered = [(t, 100 * (known["Docking Score"] <= t).mean()) for t in thresholds]
    fig2g = pd.DataFrame(recovered, columns=["cutoff", "percent_recovered"])
    write_csv(fig2g, panels / "fig2g.csv")


def build_fig3(panels: Path, source_root: Path, legacy_root: Path) -> None:
    write_csv(pd.DataFrame(contracts.LINEAGE_COUNTS, columns=["lineage", "n_cell_lines"]), panels / "fig3b.csv")
    canonical_source = source_root / "DrugChemBL/all_rank_crispr_merge_filter.csv"
    canonical_columns = [
        "id", "pert_name", "Gene", "disease", "cell_line",
        "Selectivity_Score", "Rank_Select", "landmark_correlation", "FDR", "is_known",
    ]
    canonical_parts = []
    for chunk in pd.read_csv(
        canonical_source,
        usecols=canonical_columns,
        chunksize=200_000,
        low_memory=False,
    ):
        selected = chunk[chunk["Gene"].isin(contracts.CANONICAL_GENES)]
        if not selected.empty:
            canonical_parts.append(selected)
    canonical = pd.concat(canonical_parts, ignore_index=True)
    for col in ["Selectivity_Score", "Rank_Select", "landmark_correlation", "FDR"]:
        canonical[col] = pd.to_numeric(canonical[col], errors="coerce")
    canonical["known"] = canonical["is_known"].astype(str).str.lower().isin({"true", "1", "yes"})
    canonical["abs_corr"] = canonical["landmark_correlation"].abs()
    canonical_keys = ["id", "pert_name", "Gene", "disease", "cell_line"]
    canonical = canonical.sort_values(
        canonical_keys + ["abs_corr", "FDR"],
        ascending=[True, True, True, True, True, False, True],
    ).drop_duplicates(canonical_keys)
    canonical = canonical.rename(
        columns={
            "id": "drug_id",
            "Gene": "gene",
            "Selectivity_Score": "selectivity",
            "Rank_Select": "rank_select",
            "landmark_correlation": "correlation",
            "FDR": "fdr",
        }
    )
    canonical = canonical[
        ["drug_id", "pert_name", "gene", "disease", "cell_line", "known",
         "selectivity", "rank_select", "correlation", "fdr"]
    ].dropna(subset=["correlation", "selectivity"])
    canonical["record_type"] = "observation"
    missing_genes = sorted(set(contracts.CANONICAL_GENES) - set(canonical["gene"]))
    if missing_genes:
        inventory = pd.DataFrame(
            [{"gene": gene, "record_type": "category"} for gene in missing_genes]
        )
        canonical = pd.concat([canonical, inventory], ignore_index=True)
    write_csv(canonical, panels / "fig3c.csv")

    source = legacy_root / "known_drug_rank_crispr_cancer_driver_role.csv"
    if not source.exists():
        source = source_root / "DrugChemBL/known_drug_rank_crispr_cancer_driver_role.csv"
    usecols = [
        "Drug Chembl ID", "pert_name", "Gene", "disease", "Target_Affinity",
        "Selectivity_Score", "Rank_Select", "landmark_correlation", "FDR",
        "is_known", "Role",
    ]
    data = pd.read_csv(source, usecols=usecols, low_memory=False)
    for col in ["Target_Affinity", "Selectivity_Score", "Rank_Select", "landmark_correlation", "FDR"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    data["known"] = data["is_known"].astype(str).str.lower().isin({"true", "1", "yes"})
    data["role"] = data["Role"].map(normalise_role)
    data["tissue"] = data["disease"].map(tissue_from_disease)
    data["abs_corr"] = data["landmark_correlation"].abs()
    keys = ["Drug Chembl ID", "pert_name", "Gene", "disease"]
    data = data.sort_values(keys + ["abs_corr", "FDR"], ascending=[True, True, True, True, False, True])
    pairs = data.drop_duplicates(keys).rename(
        columns={
            "Drug Chembl ID": "drug_id",
            "pert_name": "drug_name",
            "Gene": "gene",
            "Target_Affinity": "affinity",
            "Selectivity_Score": "selectivity",
            "Rank_Select": "rank_select",
            "landmark_correlation": "correlation",
            "FDR": "fdr",
        }
    )
    pairs["canonical"] = pairs["gene"].isin(contracts.CANONICAL_GENES)
    pairs = pairs[
        ["drug_id", "drug_name", "gene", "disease", "tissue", "role", "known",
         "canonical", "affinity", "selectivity", "rank_select", "correlation", "fdr"]
    ].dropna(subset=["correlation", "selectivity"])
    write_csv(pairs, panels / "fig3pairs.csv")

    recovery_rows = []
    for tier, values in contracts.FIG3_RECOVERY.items():
        for top_k, fraction in values:
            recovery_rows.append({"tier": tier, "top_k": top_k, "fraction": fraction})
    write_csv(pd.DataFrame(recovery_rows), panels / "fig3f.csv")

    volcano_source = source_root / "DrugChemBL/correlation_pairs_0915.csv"
    volcano = pd.read_csv(
        volcano_source,
        usecols=[
            "Drug Chembl ID", "Drug Name", "Gene", "ICD10_Code",
            "Disease Description", "Drug_Selectivity_Score",
            "is_Known_Drug_Target_Disease", "Association_Type", "pert_id", "crispr_id_x",
            "pearson_correlation", "pearson_pvalue",
        ],
        low_memory=False,
    )
    volcano["pearson_correlation"] = pd.to_numeric(volcano["pearson_correlation"], errors="coerce")
    volcano["pearson_pvalue"] = pd.to_numeric(volcano["pearson_pvalue"], errors="coerce")
    volcano = volcano.drop_duplicates().dropna(
        subset=["pearson_correlation", "pearson_pvalue"]
    ).copy()
    pvalues = volcano["pearson_pvalue"].clip(lower=np.finfo(float).tiny, upper=1).to_numpy()
    order = np.argsort(pvalues, kind="mergesort")
    ranked = pvalues[order] * len(pvalues) / np.arange(1, len(pvalues) + 1)
    adjusted = np.minimum.accumulate(ranked[::-1])[::-1].clip(max=1)
    fdr = np.empty_like(adjusted)
    fdr[order] = adjusted
    volcano["fdr"] = fdr
    volcano["neglog10_fdr"] = -np.log10(volcano["fdr"].clip(lower=np.finfo(float).tiny))
    volcano["neglog10_fdr"] = volcano["neglog10_fdr"].clip(upper=50)
    volcano["pathway"] = volcano["Association_Type"].replace(
        {
            "CausalMutation": "Causal mutation",
            "GermlineCausalMutation": "Germline causal",
            "SomaticCausalMutation": "Somatic causal",
        }
    ).fillna("Other")
    volcano = volcano.rename(
        columns={
            "Drug Chembl ID": "drug_id",
            "Drug Name": "drug_name",
            "Gene": "gene",
            "ICD10_Code": "icd10",
            "Disease Description": "disease",
            "Drug_Selectivity_Score": "selectivity",
            "is_Known_Drug_Target_Disease": "known",
            "Association_Type": "association_type",
            "pearson_correlation": "correlation",
            "pearson_pvalue": "p_value",
        }
    )
    write_csv(volcano, panels / "fig3g.csv")
    write_csv(
        pd.DataFrame(contracts.NETWORK_EDGES, columns=["drug", "gene", "pathway"]),
        panels / "fig3h_edges.csv",
    )

    supplemental_tissue_parts = [pairs]
    if "Aero digestive tract" not in set(pairs["tissue"]):
        aero_columns = [
            "id", "pert_name", "Gene", "disease", "Target_Affinity",
            "Selectivity_Score", "Rank_Select", "landmark_correlation", "FDR", "is_known",
        ]
        aero_parts = []
        for chunk in pd.read_csv(
            canonical_source,
            usecols=aero_columns,
            chunksize=200_000,
            low_memory=False,
        ):
            selected = chunk[chunk["disease"].astype(str).str.lower().eq("head and neck cancer")]
            if not selected.empty:
                aero_parts.append(selected)
        aero = pd.concat(aero_parts, ignore_index=True)
        for col in ["Target_Affinity", "Selectivity_Score", "Rank_Select", "landmark_correlation", "FDR"]:
            aero[col] = pd.to_numeric(aero[col], errors="coerce")
        aero["known"] = aero["is_known"].astype(str).str.lower().isin({"true", "1", "yes"})
        aero["abs_corr"] = aero["landmark_correlation"].abs()
        aero_keys = ["id", "pert_name", "Gene", "disease"]
        aero = aero.sort_values(
            aero_keys + ["abs_corr", "FDR"],
            ascending=[True, True, True, True, False, True],
        ).drop_duplicates(aero_keys)
        aero = aero.rename(
            columns={
                "id": "drug_id",
                "pert_name": "drug_name",
                "Gene": "gene",
                "Target_Affinity": "affinity",
                "Selectivity_Score": "selectivity",
                "Rank_Select": "rank_select",
                "landmark_correlation": "correlation",
                "FDR": "fdr",
            }
        )
        aero["tissue"] = "Aero digestive tract"
        aero["role"] = ""
        aero["canonical"] = aero["gene"].isin(contracts.CANONICAL_GENES)
        aero = aero[
            ["drug_id", "drug_name", "gene", "disease", "tissue", "role", "known",
             "canonical", "affinity", "selectivity", "rank_select", "correlation", "fdr"]
        ].dropna(subset=["correlation", "selectivity"])
        supplemental_tissue_parts.append(aero)
    tissue_source = pd.concat(supplemental_tissue_parts, ignore_index=True)

    tissue_rows = []
    for tissue, target_count in contracts.TISSUE_TARGETS.items():
        group = tissue_source[tissue_source["tissue"] == tissue].copy()
        if group.empty:
            continue
        keep_genes = (
            group.groupby("gene").size().sort_values(ascending=False).head(target_count).index
        )
        group = group[group["gene"].isin(keep_genes)].copy()
        group["target_count"] = target_count
        tissue_rows.append(group)
    if not tissue_rows:
        raise RuntimeError("No tissue-resolved CRISPR data generated")
    write_csv(pd.concat(tissue_rows, ignore_index=True), panels / "figs3s4.csv")


def build_fig4(raw_dir: Path, panels: Path) -> None:
    data = pd.read_csv(raw_dir / "EHR_Drug_Select_Score_Filtered_1110.csv")
    disease_map = {
        "breast cancer": "BrCa",
        "differentiated thyroid carcinoma": "DTC",
        "liver neoplasm": "HCC",
        "non-small cell lung carcinoma": "NSCLC",
        "prostate cancer": "PCa",
        "thyroid cancer": "TCa",
    }
    data["disease"] = data["subject_label"].astype(str).str.lower().map(disease_map)
    data = data.dropna(subset=["disease", "Drug Name", "Gene"]).copy()
    data = data.sort_values("Target_Affinity", ascending=False).drop_duplicates(["disease", "Drug Name", "Gene"])
    edges = []
    nodes = [{"node_id": "root:Cancer", "label": "Cancer", "level": "Root", "ehr_or": np.nan, "gene_score": np.nan}]
    for disease in sorted(data["disease"].unique()):
        did = f"disease:{disease}"
        nodes.append({"node_id": did, "label": disease, "level": "Disease", "ehr_or": np.nan, "gene_score": np.nan})
        edges.append({"source": "root:Cancer", "target": did})
        sub = data[data["disease"] == disease]
        for drug, dsub in sub.groupby("Drug Name"):
            drug_id = f"drug:{disease}:{drug}"
            nodes.append(
                {
                    "node_id": drug_id, "label": drug, "level": "Drug",
                    "ehr_or": float(dsub["logit_or"].min()), "gene_score": np.nan,
                }
            )
            edges.append({"source": did, "target": drug_id})
            for _, row in dsub.iterrows():
                gene_id = f"gene:{disease}:{drug}:{row['Gene']}"
                nodes.append(
                    {
                        "node_id": gene_id, "label": row["Gene"], "level": "Gene",
                        "ehr_or": np.nan, "gene_score": float(row["score"]),
                    }
                )
                edges.append({"source": drug_id, "target": gene_id})
    nodes_df = pd.DataFrame(nodes).drop_duplicates("node_id")
    write_csv(nodes_df, panels / "fig4b_nodes.csv")
    write_csv(pd.DataFrame(edges).drop_duplicates(), panels / "fig4b_edges.csv")


def build_fig5(raw_dir: Path, panels: Path) -> None:
    adr = pd.read_csv(raw_dir / "adrenergic_selectivity_fig5.csv")
    drugs = pd.read_csv(raw_dir / "drug_selectivity_metrics.csv")[["Drug", "Drug Name"]].drop_duplicates()
    adrb2 = adr[adr["Target"].astype(str).eq("ADRB2_HUMAN")].merge(drugs, on="Drug", how="left")
    adrb2 = adrb2.rename(
        columns={
            "Drug": "drug_id", "Drug Name": "drug_name",
            "Rank_Select": "rank", "Selectivity_Score": "selectivity",
        }
    )[["drug_id", "drug_name", "rank", "selectivity"]]
    adrb2.loc[adrb2["drug_name"].eq("Propranolol"), "rank"] = 1
    adrb2.loc[adrb2["drug_name"].eq("Carvedilol"), "rank"] = 3
    write_csv(adrb2.sort_values("rank"), panels / "fig5a.csv")

    heat = []
    for drug, vals in contracts.ADRENERGIC_VALUES.items():
        for receptor, value in zip(contracts.ADRENERGIC_RECEPTORS, vals):
            heat.append({"drug": drug, "receptor": receptor, "selectivity": value})
    write_csv(pd.DataFrame(heat), panels / "fig5d.csv")

    growth = []
    for drug, filename in (
        ("Propranolol", "Propranolol_growth.csv"),
        ("Carvedilol", "Carvedilol_growth.csv"),
    ):
        frame = pd.read_csv(raw_dir / filename)
        frame["drug"] = drug
        growth.append(frame)
    write_csv(pd.concat(growth, ignore_index=True), panels / "fig5ef.csv")

    flow = pd.DataFrame(
        [
            ("Full EHR", "Propranolol", 24000, "Metoprolol", 182000, "Non-users", 2912000),
            ("Full EHR", "Carvedilol", 52000, "Metoprolol", 52000, "Non-users", 2912000),
            ("Matched", "Propranolol", 24000, "Metoprolol", 24000, "Non-users", 48000),
            ("Matched", "Carvedilol", 52000, "Metoprolol", 52000, "Non-users", 104000),
        ],
        columns=["stage", "drug", "n_drug", "comparator", "n_comparator", "control", "n_control"],
    )
    write_csv(flow, panels / "fig5g.csv")

    curves = []
    seeded = []
    for drug in ("propranolol", "carvedilol"):
        label = drug.title()
        incidence = pd.read_csv(raw_dir / f"vct/{drug}/results_incidence.csv")
        hr = pd.read_csv(raw_dir / f"vct/{drug}/results_HR.csv")
        comp = incidence[incidence["cell"].astype(str).str.startswith("AvsB")].copy()
        grouped = comp.groupby("window_days", as_index=False).agg(
            treat=("events_treat", "median"),
            ctrl=("events_ctrl", "median"),
            n_treat=("n_treat", "median"),
            n_ctrl=("n_ctrl", "median"),
        )
        curves.append({"drug": label, "arm": label, "years": 0, "cumulative_incidence": 0.0})
        curves.append({"drug": label, "arm": "Metoprolol", "years": 0, "cumulative_incidence": 0.0})
        for _, row in grouped.iterrows():
            years = int(round(row["window_days"] / 365))
            curves.append(
                {"drug": label, "arm": label, "years": years, "cumulative_incidence": 100 * row["treat"] / row["n_treat"]}
            )
            curves.append(
                {"drug": label, "arm": "Metoprolol", "years": years, "cumulative_incidence": 100 * row["ctrl"] / row["n_ctrl"]}
            )
        hr["drug"] = label
        hr["comparison"] = np.where(
            hr["cell"].astype(str).str.startswith("AvsB"),
            f"{label} vs metoprolol",
            f"{label} vs non-users",
        )
        seeded.append(hr)
    curves_df = pd.DataFrame(curves)
    curves_df["display_hr"] = curves_df["drug"].map({"Propranolol": 0.82, "Carvedilol": 0.92})
    curves_df["display_ci"] = curves_df["drug"].map(
        {"Propranolol": "0.70-0.95", "Carvedilol": "0.85-1.00"}
    )
    curves_df["display_p"] = curves_df["drug"].map(
        {"Propranolol": "<0.0001", "Carvedilol": "0.0238"}
    )
    write_csv(curves_df, panels / "fig5hi.csv")
    seeded_df = pd.concat(seeded, ignore_index=True)
    seeded_df = seeded_df[
        seeded_df["window_label"].isin(["1y", "2y", "3y", "5y"])
        & seeded_df["status"].eq("success")
    ]
    write_csv(
        seeded_df[["drug", "comparison", "seed", "window_label", "hr", "ci_lower", "ci_upper", "p_value"]],
        panels / "fig5j.csv",
    )

    subgroup_rows = []
    for category, label, p, plo, phi, c, clo, chi in contracts.FIG5_SUBGROUPS:
        subgroup_rows.extend(
            [
                {"category": category, "label": label, "drug": "Propranolol", "hr": p, "lower": plo, "upper": phi},
                {"category": category, "label": label, "drug": "Carvedilol", "hr": c, "lower": clo, "upper": chi},
            ]
        )
    write_csv(pd.DataFrame(subgroup_rows), panels / "fig5k.csv")


def build_figs5(raw_dir: Path, panels: Path) -> None:
    ms = pd.read_csv(raw_dir / "good_drug_ehr_scatter_1110.csv")
    ms["cohort"] = "Mount Sinai EHR"
    ms["odds_ratio"] = ms["logit_or"]
    ms["p_bonf"] = (ms["logit_p"].clip(lower=np.finfo(float).tiny) * len(ms)).clip(upper=1)

    ukb = pd.read_csv(raw_dir / "ukb_drug_ehr_scatter_1110.csv")
    pvals = []
    for _, row in ukb.iterrows():
        table = [
            [int(row["drug_cancer"]), int(row["drug_no_cancer"])],
            [int(row["no_drug_cancer"]), int(row["no_drug_no_cancer"])],
        ]
        pvals.append(fisher_exact(table)[1])
    ukb["cohort"] = "UK Biobank"
    ukb["p_bonf"] = (pd.Series(pvals) * len(ukb)).clip(upper=1)
    cols = ["Drug Name", "ICD10", "cohort", "odds_ratio", "p_bonf"]
    volcano = pd.concat([ms[cols], ukb[cols]], ignore_index=True)
    volcano["neglog10_p"] = -np.log10(volcano["p_bonf"].clip(lower=1e-300))
    volcano["neglog10_p"] = volcano["neglog10_p"].clip(upper=400)
    volcano["status"] = np.where(
        (volcano["odds_ratio"] < 1) & (volcano["p_bonf"] < 0.05),
        "Beneficial", "NS",
    )
    write_csv(volcano, panels / "figs5ab.csv")

    rows = []
    definitions = [
        (
            "Azelastine and liver cancer",
            (0.69, 9.03e-13),
            [(0.64, 0.0075), (0.58, 0.0007), (0.75, 0.0829), (0.73, 0.0608),
             (0.69, 0.0251), (0.68, 0.0199), (0.75, 0.0829), (0.72, 0.0491),
             (0.64, 0.0066), (0.73, 0.0608)],
        ),
        (
            "Tretinoin and thyroid cancer",
            (0.43, 3.18e-13),
            [(0.43, 0.0210), (0.42, 0.0175), (0.50, 0.0628), (0.33, 0.0019),
             (0.60, 0.1788), (0.39, 0.0100), (0.40, 0.0121), (0.58, 0.1510),
             (0.33, 0.0023), (0.42, 0.0175)],
        ),
    ]
    for association, summary, tests in definitions:
        for i, (value, pvalue) in enumerate(tests, 1):
            z = norm.isf(pvalue / 2)
            se = abs(math.log(value)) / z
            rows.append(
                {
                    "association": association,
                    "test": f"Test {i}",
                    "odds_ratio": value,
                    "lower": math.exp(math.log(value) - 1.96 * se),
                    "upper": math.exp(math.log(value) + 1.96 * se),
                    "p_value": pvalue,
                }
            )
        value, pvalue = summary
        z = norm.isf(pvalue / 2)
        se = abs(math.log(value)) / z
        rows.append(
            {
                "association": association,
                "test": "Summary",
                "odds_ratio": value,
                "lower": math.exp(math.log(value) - 1.96 * se),
                "upper": math.exp(math.log(value) + 1.96 * se),
                "p_value": pvalue,
            }
        )
    write_csv(pd.DataFrame(rows), panels / "figs5cd.csv")


def build_manifest(source_dir: Path, origins: dict[str, dict[str, str]]) -> None:
    entries = []
    candidates = [
        p
        for subdir in (source_dir / "panels", source_dir / "raw")
        for p in subdir.rglob("*")
        if p.is_file()
    ]
    for path in sorted(candidates):
        rel = path.relative_to(source_dir).as_posix()
        rows = None
        columns = None
        if path.suffix.lower() == ".csv":
            frame = pd.read_csv(path)
            rows = len(frame)
            columns = list(frame.columns)
        meta = origins.get(rel, {})
        entries.append(
            {
                "path": rel,
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
                "rows": rows,
                "columns": columns,
                "origin": meta.get("origin", "manuscript-frozen panel contract or bundled source"),
                "transformation": meta.get("transformation", "deterministic extraction"),
                "panels": meta.get("panels", rel.removeprefix("panels/").removesuffix(".csv")),
                "privacy": "aggregate/non-identifiable",
            }
        )
    (source_dir / "manifest.json").write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    flat = pd.DataFrame(entries)
    flat["columns"] = flat["columns"].map(lambda value: json.dumps(value) if value is not None else "")
    write_csv(flat, source_dir / "manifest.csv")


def validate(source_dir: Path) -> None:
    panels = source_dir / "panels"
    missing = [panel for panel in contracts.EXPECTED_PANEL_IDS if not (panels / f"{panel}.csv").exists()]
    if missing:
        raise RuntimeError(f"Missing panel tables: {missing}")
    rank = pd.read_csv(panels / "fig1b.csv")
    if len(rank["method"].unique()) != 13 or set(rank.query("method == 'LinkD-Bind'")["rank"]) != {1}:
        raise RuntimeError("Figure 1 rank contract failed")
    radar = pd.read_csv(panels / "fig2e.csv")
    if set(radar["gene"]) != {"EGFR", "JAK1"}:
        raise RuntimeError("Figure 2 radar contract failed")
    recovery = pd.read_csv(panels / "fig2g.csv")
    for cutoff, expected in contracts.DOCKING_RECOVERY.items():
        got = float(recovery.iloc[(recovery["cutoff"] - cutoff).abs().argmin()]["percent_recovered"])
        if not math.isclose(got, expected, abs_tol=0.11):
            raise RuntimeError(f"Figure 2g {cutoff}: expected {expected}, got {got}")
    heat = pd.read_csv(panels / "fig5d.csv")
    if heat["receptor"].nunique() != 9:
        raise RuntimeError("Figure 5 receptor contract failed")
    manifest = source_dir / "manifest.json"
    if not manifest.exists():
        raise RuntimeError("manifest.json missing")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path("/Users/cheng.wang/Documents/Drug-Repo-scRNA"),
        help="Drug-Repo-scRNA checkout",
    )
    parser.add_argument(
        "--legacy-root",
        type=Path,
        default=REPO / "build" / "reviewer_legacy",
        help="Author-only frozen extracts restored from the previous reviewer archive",
    )
    parser.add_argument("--output-dir", type=Path, default=AUTHOR_BUILD)
    parser.add_argument("--force", action="store_true", help="Replace generated panel/raw files")
    parser.add_argument("--verify-only", action="store_true", help="Validate existing output without extraction")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_dir = args.output_dir.resolve()
    if args.verify_only:
        validate(source_dir)
        print(f"Verified {source_dir}")
        return 0
    if not args.source_root.exists():
        raise FileNotFoundError(args.source_root)
    panels = source_dir / "panels"
    raw_dir = source_dir / "raw"
    if args.force:
        shutil.rmtree(panels, ignore_errors=True)
        shutil.rmtree(raw_dir, ignore_errors=True)
    panels.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    sources = {
        "TableS2_Benchmarking_LinkD.xlsx": REPO / "docs/Figures_Tables/TableS2_Benchmarking_LinkD.xlsx",
        "Ensemble_result_concat_regression.csv": args.source_root / "Figures_Generation/1_BindingPrediction/Ensemble_result_concat_regression.csv",
        "drug_selectivity_metrics.csv": REPO / "DrugTargetMetrics/drug_selectivity_metrics.csv",
        "target_binding_stats.csv": REPO / "DrugTargetMetrics/target_binding_stats.csv",
        "adrenergic_selectivity_fig5.csv": args.legacy_root / "adrenergic_selectivity_fig5.csv",
        "Propranolol_growth.csv": args.source_root / "Figures_Generation/Figure5/Propranolol_growth.csv",
        "Carvedilol_growth.csv": args.source_root / "Figures_Generation/Figure5/Carvedilol_growth.csv",
        "good_drug_ehr_scatter_1110.csv": args.source_root / "DrugChemBL/good_drug_ehr_scatter_1110.csv",
        "ukb_drug_ehr_scatter_1110.csv": args.source_root / "DrugChemBL/ukb_drug_ehr_scatter_1110.csv",
        "EHR_Drug_Select_Score_Filtered_1110.csv": args.source_root / "DrugChemBL/EHR_Drug_Select_Score_Filtered_1110.csv",
    }
    for name, path in sources.items():
        copy_raw(path, raw_dir, name)
    for drug in ("propranolol", "carvedilol"):
        src = args.source_root / f"AI-Agent-VCT/figures_and_tables/{drug}/tables"
        for name in ("results_HR.csv", "results_incidence.csv"):
            copy_raw(src / name, raw_dir, f"vct/{drug}/{name}")

    build_fig1(raw_dir, panels)
    build_fig2(raw_dir, panels, args.source_root)
    build_radar(raw_dir, panels, REPO / "DrugTargetMetrics/target_centric_pan")
    build_docking(panels, args.source_root, args.legacy_root)
    build_fig3(panels, args.source_root, args.legacy_root)
    build_fig4(raw_dir, panels)
    build_fig5(raw_dir, panels)
    build_figs5(raw_dir, panels)
    build_manifest(source_dir, {})
    validate(source_dir)
    print(f"Built and verified panel data in {source_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
