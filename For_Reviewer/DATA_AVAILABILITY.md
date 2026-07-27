# Data availability

All notebook inputs live under `For_Reviewer/source_data/` (or `illustrations/` for non-computable panels).  
See `source_data/manifest.csv` for per-file `sha256`, byte size, and originating path on the author machine.

## Copied / extracted tables (summary)

| File | Approx. size | Used by |
|------|-------------:|---------|
| `TableS2_Benchmarking_LinkD.xlsx` | 50 KB | Fig 1b, 1c, S2 |
| `Ensemble_result_concat_regression.csv` | 100 KB | Fig 1 / S2 (alternate) |
| `TableS3_Mount_Sinai_Drug_Cancer.csv` | 2.6 MB | Fig 4b, S5 |
| `TableS4_UK_Biobank_Drug_Disease.csv` | 0.9 MB | Fig 4b, S5 |
| `drug_selectivity_metrics.csv` | 5.2 MB | Fig 2a, 5a |
| `target_binding_stats.csv` | 1.1 MB | Fig 2b |
| `drug_umap_clustering.csv` | 3.2 MB | Fig 2a (optional) |
| `onco_genes.csv` | 16 KB | Fig 2b, 2f |
| `opentarget_known_drug_pair.csv` | 0.3 MB | Fig 2c–e |
| `known_drug_rank_crispr_cancer_driver_role.csv` | 174 MB | Fig 3, S3, S4 |
| `matched_cells.csv` | 45 KB | Fig 3b |
| `docking_scores_fig2fg.csv` | 42 MB | Fig 2f, 2g (**extracted** from 18 GB `top_gene_dock.csv`) |
| `adrenergic_selectivity_fig5.csv` | ~MB | Fig 5a, 5d (**extracted** from parquet) |
| `radar_egfr_jak1_fig2e.csv` | small | Fig 2e (**extracted**) |
| `Propranolol_growth.csv` / `Carvedilol_growth.csv` | <1 KB | Fig 5e, 5f |
| `vct/propranolol/*.csv`, `vct/carvedilol/*.csv` | small | Fig 5g–k |
| `good_drug_ehr_scatter_1110.csv`, `ukb_drug_ehr_scatter_1110.csv` | small | Fig S5 (alt) |
| `source_data/benchmark/*` | variable | Fig 6c (LinkD-Agent) |

## Not packaged (with reason)

| Asset | Reason | Notebook handling |
|-------|--------|-------------------|
| Patient-level OMOP EHR | PHI | Fig 5g–k use VCT **summary** tables only |
| Full `top_gene_dock.csv` (18 GB) | Size | Panel-ready extract shipped |
| Full `target_centric_pan/` parquet (13 GB) | Size | ADRB / EGFR–JAK1 extracts shipped |
| PyMOL pose sessions for Fig 5b/5c | Not available | Process + published illustration |

## Illustrations

`illustrations/<panel_id>/` contains the published JPG and `PROCESS.md` for schematic / pose panels (1a, 3a, 4a, 5b, 5c, 6a, 6b, S1, S6a).
