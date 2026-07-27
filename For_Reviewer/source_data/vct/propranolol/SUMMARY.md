# Propranolol — prostate cancer target-trial emulation

Factorial analysis across 4 follow-up windows (1y / 2y / 3y / 5y), 2 matching ratios (1:1 / 1:2), 2 PSM adjustment levels (complete 14-cov / simplified 6-demographics), 2 comparators (Arm B = metoprolol active comparator; Arm C = class-clean control).

Generated per Nature figure standards: Arial font, 300 dpi PNG + PDF (type-42).

## Per-seed-aggregate results (10 seeds for full PSM; 1 seed for simplified PSM)

| Cell | Window | Estimator | Median | Range | n seeds |
|---|---|---|---:|---|---:|
| AvsB_1to1_full | 1y | Cox HR | 0.905 | [0.840, 0.954] | 10 |
| AvsB_1to1_full | 1y | Logit OR | 0.408 | [0.242, 0.540] | 9 |
| AvsB_1to1_full | 2y | Cox HR | 0.883 | [0.836, 0.931] | 10 |
| AvsB_1to1_full | 2y | Logit OR | 0.452 | [0.363, 0.594] | 7 |
| AvsB_1to1_full | 3y | Cox HR | 0.869 | [0.839, 0.952] | 10 |
| AvsB_1to1_full | 3y | Logit OR | 0.516 | [0.458, 0.752] | 6 |
| AvsB_1to1_full | 5y | Cox HR | 0.865 | [0.816, 0.951] | 10 |
| AvsB_1to1_full | 5y | Logit OR | 0.567 | [0.526, 0.805] | 6 |
| AvsB_1to1_simple | 1y | Cox HR | 0.918 | [0.918, 0.918] | 1 |
| AvsB_1to1_simple | 1y | Logit OR | 0.419 | [0.419, 0.419] | 1 |
| AvsB_1to1_simple | 2y | Cox HR | 0.982 | [0.982, 0.982] | 1 |
| AvsB_1to1_simple | 2y | Logit OR | 0.875 | [0.875, 0.875] | 1 |
| AvsB_1to1_simple | 3y | Cox HR | 0.983 | [0.983, 0.983] | 1 |
| AvsB_1to1_simple | 3y | Logit OR | 0.915 | [0.915, 0.915] | 1 |
| AvsB_1to1_simple | 5y | Cox HR | 1.060 | [1.060, 1.060] | 1 |
| AvsB_1to1_simple | 5y | Logit OR | — | — | 0 |
| AvsB_1to2_full | 1y | Cox HR | 0.899 | [0.860, 0.940] | 10 |
| AvsB_1to2_full | 1y | Logit OR | 0.347 | [0.263, 0.466] | 9 |
| AvsB_1to2_full | 2y | Cox HR | 0.878 | [0.868, 0.908] | 10 |
| AvsB_1to2_full | 2y | Logit OR | 0.447 | [0.427, 0.536] | 9 |
| AvsB_1to2_full | 3y | Cox HR | 0.877 | [0.863, 0.914] | 10 |
| AvsB_1to2_full | 3y | Logit OR | 0.528 | [0.489, 0.633] | 9 |
| AvsB_1to2_full | 5y | Cox HR | 0.872 | [0.853, 0.911] | 10 |
| AvsB_1to2_full | 5y | Logit OR | 0.586 | [0.531, 0.689] | 9 |
| AvsB_1to2_simple | 1y | Cox HR | 0.909 | [0.909, 0.909] | 1 |
| AvsB_1to2_simple | 1y | Logit OR | 0.547 | [0.547, 0.547] | 1 |
| AvsB_1to2_simple | 2y | Cox HR | 0.871 | [0.871, 0.871] | 1 |
| AvsB_1to2_simple | 2y | Logit OR | — | — | 0 |
| AvsB_1to2_simple | 3y | Cox HR | 0.899 | [0.899, 0.899] | 1 |
| AvsB_1to2_simple | 3y | Logit OR | — | — | 0 |
| AvsB_1to2_simple | 5y | Cox HR | 0.957 | [0.957, 0.957] | 1 |
| AvsB_1to2_simple | 5y | Logit OR | 0.840 | [0.840, 0.840] | 1 |
| AvsC_1to1_full | 1y | Cox HR | 0.880 | [0.810, 0.950] | 10 |
| AvsC_1to1_full | 1y | Logit OR | 0.305 | [0.208, 0.517] | 8 |
| AvsC_1to1_full | 2y | Cox HR | 0.853 | [0.810, 0.947] | 10 |
| AvsC_1to1_full | 2y | Logit OR | 0.423 | [0.349, 0.642] | 6 |
| AvsC_1to1_full | 3y | Cox HR | 0.862 | [0.770, 0.953] | 10 |
| AvsC_1to1_full | 3y | Logit OR | 0.498 | [0.401, 0.739] | 7 |
| AvsC_1to1_full | 5y | Cox HR | 0.844 | [0.754, 0.979] | 10 |
| AvsC_1to1_full | 5y | Logit OR | 0.528 | [0.405, 0.864] | 8 |
| AvsC_1to1_simple | 1y | Cox HR | 1.062 | [1.062, 1.062] | 1 |
| AvsC_1to1_simple | 1y | Logit OR | — | — | 0 |
| AvsC_1to1_simple | 2y | Cox HR | 1.042 | [1.042, 1.042] | 1 |
| AvsC_1to1_simple | 2y | Logit OR | 1.464 | [1.464, 1.464] | 1 |
| AvsC_1to1_simple | 3y | Cox HR | 0.964 | [0.964, 0.964] | 1 |
| AvsC_1to1_simple | 3y | Logit OR | 0.819 | [0.819, 0.819] | 1 |
| AvsC_1to1_simple | 5y | Cox HR | 1.033 | [1.033, 1.033] | 1 |
| AvsC_1to1_simple | 5y | Logit OR | 1.158 | [1.158, 1.158] | 1 |
| AvsC_1to2_full | 1y | Cox HR | 0.878 | [0.812, 0.925] | 10 |
| AvsC_1to2_full | 1y | Logit OR | 0.307 | [0.228, 0.422] | 7 |
| AvsC_1to2_full | 2y | Cox HR | 0.860 | [0.794, 0.909] | 10 |
| AvsC_1to2_full | 2y | Logit OR | 0.420 | [0.395, 0.525] | 6 |
| AvsC_1to2_full | 3y | Cox HR | 0.851 | [0.758, 0.908] | 10 |
| AvsC_1to2_full | 3y | Logit OR | 0.481 | [0.450, 0.604] | 7 |
| AvsC_1to2_full | 5y | Cox HR | 0.840 | [0.761, 0.942] | 10 |
| AvsC_1to2_full | 5y | Logit OR | 0.538 | [0.406, 0.761] | 7 |
| AvsC_1to2_simple | 1y | Cox HR | 1.065 | [1.065, 1.065] | 1 |
| AvsC_1to2_simple | 1y | Logit OR | 11.399 | [11.399, 11.399] | 1 |
| AvsC_1to2_simple | 2y | Cox HR | 1.090 | [1.090, 1.090] | 1 |
| AvsC_1to2_simple | 2y | Logit OR | 2.828 | [2.828, 2.828] | 1 |
| AvsC_1to2_simple | 3y | Cox HR | 1.074 | [1.074, 1.074] | 1 |
| AvsC_1to2_simple | 3y | Logit OR | 1.642 | [1.642, 1.642] | 1 |
| AvsC_1to2_simple | 5y | Cox HR | 0.953 | [0.953, 0.953] | 1 |
| AvsC_1to2_simple | 5y | Logit OR | 0.820 | [0.820, 0.820] | 1 |

## Tables

- `tables/descriptive_stats.csv` — covariate means by arm in matched cohorts (seed 0)
- `tables/results_HR.csv` — per (cell, window, seed) Cox PH HR + 95% CI + p
- `tables/results_OR.csv` — per (cell, window, seed) logit OR (GLM Binomial) + 95% CI + p
- `tables/results_incidence.csv` — per-1,000 person-year rates and IRR
- `tables/results_subgroup.csv` — subgroup HR/OR with BH-FDR interaction p
- `tables/results_seeded_aggregates.csv` — per-cell × per-window median + range across 10 seeds

## Figures (`figures/`)

For each cell × window: KM curve, incidence-rate bar, subgroup forest, and (per cell) 4-window HR-forest and OR-forest summaries.
