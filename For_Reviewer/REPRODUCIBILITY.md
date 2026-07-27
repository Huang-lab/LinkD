# Reproducibility matrix

Status: **compute** = regenerated from `source_data/`; **illustrate** = process + published image.

| Panel | Notebook | Section | Status | Primary input |
|-------|----------|---------|--------|---------------|
| 1a | Figure1… | Panel a | illustrate | `illustrations/fig1_a/` |
| 1b | Figure1… | Panel b | compute | `TableS2_Benchmarking_LinkD.xlsx` |
| 1c | Figure1… | Panel c | compute | `TableS2_Benchmarking_LinkD.xlsx` |
| 2a | Figure2… | Panel a | compute | `drug_selectivity_metrics.csv` |
| 2b | Figure2… | Panel b | compute | `target_binding_stats.csv`, `onco_genes.csv` |
| 2c–d | Figure2… | Panels c–d | compute | CRISPR concordance + known flags |
| 2e | Figure2… | Panel e | compute | `radar_egfr_jak1_fig2e.csv` |
| 2f | Figure2… | Panel f | compute | `docking_scores_fig2fg.csv` |
| 2g | Figure2… | Panel g | compute | `docking_scores_fig2fg.csv` |
| 3a | Figure3… | Panel a | illustrate | `illustrations/fig3_a/` |
| 3b–h | Figure3… | Panels b–h | compute | `known_drug_rank_crispr_…csv` |
| 4a | Figure4… | Panel a | illustrate | `illustrations/fig4_a/` |
| 4b | Figure4… | Panel b | compute | `TableS3_…csv` |
| 5a | Figure5… | Panel a | compute | `adrenergic_selectivity_fig5.csv` |
| 5b–c | Figure5… | Panels b–c | illustrate | `illustrations/fig5_b/`, `fig5_c/` |
| 5d | Figure5… | Panel d | compute | `adrenergic_selectivity_fig5.csv` |
| 5e–f | Figure5… | Panels e–f | compute | growth CSVs |
| 5g–k | Figure5… | Panels g–k | compute | `vct/*/results_*.csv` |
| 6a–b | Figure6… | Panels a–b | illustrate | `illustrations/fig6_*` |
| 6c | Figure6… | Panel c | compute | `source_data/benchmark/` |
| S2 | FigureS2… | — | compute | TableS2 |
| S3–S4 | FigureS3_S4… | — | compute | CRISPR concordance |
| S5 | FigureS5… | — | compute | TableS3 / TableS4 |
| S1, S6a | — | via illustrate helper | illustrate | `illustrations/figS1`, `figS6_a` |

## Contract

Regenerated panels are **numerically** aligned with packaged tables, not pixel-identical to Photoshop composites. Use `python validation/validate_claims.py` after `execute_all.py`.
