# LinkD data dictionary

Six integrated evidence layers (~16 GB). Versions: ChEMBL 34, Open Targets 24.09,
DisGeNET, PRISM/GDSC 2024-Q4, Mount Sinai EHR 2024-11, UK Biobank 2024-11.

## Identifiers
- **Drug**: ChEMBL ID, e.g. `CHEMBL553` (erlotinib), `CHEMBL1229517` (vemurafenib).
- **Target**: HGNC gene symbol, e.g. `EGFR`, `BRAF`. In the binding matrix the
  target is a UniProt protein name, e.g. `EGFR_HUMAN` (resolved automatically).
- **Disease**: free-text name or ICD-10 code (e.g. `C34` lung, `C43` melanoma,
  `C50` breast, `C61` prostate, `C18` colon).

## Layers & key columns

| Layer | CLI command | Source | Key fields | How to read |
|---|---|---|---|---|
| Clinical | `target-info`, `evidence` | ChEMBL v34 | `phase` (0.5-4.0), `status`, `mechanismOfAction` | Phase 4 = approved |
| Genetic causality | `causal` | Open Targets / DisGeNET | `CausalType`, `Disease Name`, `ICD_Code` | presence = gene causally linked to disease |
| Predicted binding | `binding`, `drugs-for-target`, `targets-for-drug` | LinkD pKd model (Parquet) | `aff_local` (pKd), `Selectivity_Score`, `Rank_Select` | **pKd > 7 = strong**; lower Rank_Select = stronger |
| Target priority | `target-info` | LinkD | `TPI`, `N_hit`, `Avg_pKd`, `Max_pKd`, `Role` | TPI 0-1, higher = more tractable/validated |
| Drug selectivity | `drug-info` | LinkD (UMAP) | `Selectivity_Score`, `drug_type` | Type I highly selective / II moderate / III broad |
| Functional (CRISPR) | `drug-response` | PRISM + GDSC | `AUC_corr`, `AUC_FDR`, `IC50_corr` | significant if FDR < 0.05; sign indicates target vs resistance |
| Real-world (EHR) | `ehr` | Mount Sinai (11.5M pts) + UK Biobank | `logit_or`/`odds_ratio`, `logit_p`, `cox_hr` | **OR < 1 = protective**, OR > 1 = risk |

## Value interpretation cheatsheet
- pKd > 7 → strong binding; 5-7 → moderate; < 5 → weak.
- Odds ratio < 1 → protective / reduced risk; > 1 → increased risk.
- CRISPR FDR < 0.05 → significant functional correlation.
- TPI and all `*_Score`/`*_n` fields are already normalized to [0, 1].

## Coverage caveat
Not every drug-target-disease triad appears in every layer. EHR and CRISPR in
particular are sparse and disease-specific (a drug may have EHR data, but not for
the queried ICD code). Treat absent layers as **missing coverage**, not as
evidence against the association. The `evidence`/`deep-dive` commands quantify
this as a `coverage` score and list `missing` layers explicitly.
