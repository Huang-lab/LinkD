# Carvedilol — prostate cancer target-trial emulation

Factorial analysis across 4 follow-up windows (1y / 2y / 3y / 5y), 2 matching ratios (1:1 / 1:2), 2 PSM adjustment levels (complete 14-cov / simplified 6-demographics), 2 comparators (Arm B = metoprolol active comparator; Arm C = class-clean control).

Generated per Nature figure standards: Arial font, 300 dpi PNG + PDF (type-42).

## Per-seed-aggregate results (10 seeds for full PSM; 1 seed for simplified PSM)

| Cell | Window | Estimator | Median | Range | n seeds |
|---|---|---|---:|---|---:|
| AvsB_1to1_full | 1y | Cox HR | 0.924 | [0.897, 0.967] | 10 |
| AvsB_1to1_full | 1y | Logit OR | 0.777 | [0.702, 0.884] | 10 |
| AvsB_1to1_full | 2y | Cox HR | 0.900 | [0.864, 0.960] | 10 |
| AvsB_1to1_full | 2y | Logit OR | 0.759 | [0.702, 0.892] | 10 |
| AvsB_1to1_full | 3y | Cox HR | 0.896 | [0.865, 0.926] | 10 |
| AvsB_1to1_full | 3y | Logit OR | 0.779 | [0.732, 0.817] | 9 |
| AvsB_1to1_full | 5y | Cox HR | 0.921 | [0.866, 0.948] | 10 |
| AvsB_1to1_full | 5y | Logit OR | 0.836 | [0.760, 0.895] | 10 |
| AvsB_1to1_simple | 1y | Cox HR | 1.106 | [1.106, 1.106] | 1 |
| AvsB_1to1_simple | 1y | Logit OR | 1.456 | [1.456, 1.456] | 1 |
| AvsB_1to1_simple | 2y | Cox HR | 1.276 | [1.276, 1.276] | 1 |
| AvsB_1to1_simple | 2y | Logit OR | 2.201 | [2.201, 2.201] | 1 |
| AvsB_1to1_simple | 3y | Cox HR | 1.412 | [1.412, 1.412] | 1 |
| AvsB_1to1_simple | 3y | Logit OR | 2.804 | [2.804, 2.804] | 1 |
| AvsB_1to1_simple | 5y | Cox HR | 1.648 | [1.648, 1.648] | 1 |
| AvsB_1to1_simple | 5y | Logit OR | 3.877 | [3.877, 3.877] | 1 |
| AvsB_1to2_full | 1y | Cox HR | 0.943 | [0.918, 0.969] | 10 |
| AvsB_1to2_full | 1y | Logit OR | 0.803 | [0.751, 0.875] | 10 |
| AvsB_1to2_full | 2y | Cox HR | 0.922 | [0.895, 0.950] | 10 |
| AvsB_1to2_full | 2y | Logit OR | 0.806 | [0.743, 0.856] | 10 |
| AvsB_1to2_full | 3y | Cox HR | 0.908 | [0.890, 0.953] | 10 |
| AvsB_1to2_full | 3y | Logit OR | 0.793 | [0.759, 0.878] | 10 |
| AvsB_1to2_full | 5y | Cox HR | 0.925 | [0.892, 0.968] | 10 |
| AvsB_1to2_full | 5y | Logit OR | 0.842 | [0.793, 0.922] | 10 |
| AvsB_1to2_simple | 1y | Cox HR | 0.909 | [0.909, 0.909] | 1 |
| AvsB_1to2_simple | 1y | Logit OR | 0.752 | [0.752, 0.752] | 1 |
| AvsB_1to2_simple | 2y | Cox HR | 0.910 | [0.910, 0.910] | 1 |
| AvsB_1to2_simple | 2y | Logit OR | — | — | 0 |
| AvsB_1to2_simple | 3y | Cox HR | 0.876 | [0.876, 0.876] | 1 |
| AvsB_1to2_simple | 3y | Logit OR | — | — | 0 |
| AvsB_1to2_simple | 5y | Cox HR | 1.024 | [1.024, 1.024] | 1 |
| AvsB_1to2_simple | 5y | Logit OR | 1.046 | [1.046, 1.046] | 1 |
| AvsC_1to1_full | 1y | Cox HR | 0.988 | [0.882, 1.100] | 10 |
| AvsC_1to1_full | 1y | Logit OR | 1.018 | [0.830, 1.498] | 7 |
| AvsC_1to1_full | 2y | Cox HR | 0.968 | [0.896, 1.138] | 10 |
| AvsC_1to1_full | 2y | Logit OR | 0.937 | [0.803, 1.543] | 9 |
| AvsC_1to1_full | 3y | Cox HR | 0.948 | [0.748, 1.129] | 10 |
| AvsC_1to1_full | 3y | Logit OR | 1.062 | [0.584, 1.419] | 5 |
| AvsC_1to1_full | 5y | Cox HR | 0.996 | [0.813, 1.100] | 10 |
| AvsC_1to1_full | 5y | Logit OR | 1.030 | [0.711, 1.259] | 10 |
| AvsC_1to1_simple | 1y | Cox HR | 0.624 | [0.624, 0.624] | 1 |
| AvsC_1to1_simple | 1y | Logit OR | 0.332 | [0.332, 0.332] | 1 |
| AvsC_1to1_simple | 2y | Cox HR | 0.558 | [0.558, 0.558] | 1 |
| AvsC_1to1_simple | 2y | Logit OR | 0.327 | [0.327, 0.327] | 1 |
| AvsC_1to1_simple | 3y | Cox HR | 0.616 | [0.616, 0.616] | 1 |
| AvsC_1to1_simple | 3y | Logit OR | 0.416 | [0.416, 0.416] | 1 |
| AvsC_1to1_simple | 5y | Cox HR | 0.719 | [0.719, 0.719] | 1 |
| AvsC_1to1_simple | 5y | Logit OR | 0.575 | [0.575, 0.575] | 1 |
| AvsC_1to2_full | 1y | Cox HR | 0.979 | [0.857, 1.079] | 10 |
| AvsC_1to2_full | 1y | Logit OR | 0.925 | [0.699, 1.449] | 9 |
| AvsC_1to2_full | 2y | Cox HR | 0.952 | [0.824, 1.117] | 10 |
| AvsC_1to2_full | 2y | Logit OR | 0.954 | [0.774, 1.456] | 4 |
| AvsC_1to2_full | 3y | Cox HR | 0.961 | [0.802, 1.028] | 10 |
| AvsC_1to2_full | 3y | Logit OR | 0.923 | [0.658, 1.117] | 8 |
| AvsC_1to2_full | 5y | Cox HR | 0.938 | [0.854, 1.024] | 10 |
| AvsC_1to2_full | 5y | Logit OR | 0.920 | [0.782, 1.042] | 10 |
| AvsC_1to2_simple | 1y | Cox HR | 0.734 | [0.734, 0.734] | 1 |
| AvsC_1to2_simple | 1y | Logit OR | — | — | 0 |
| AvsC_1to2_simple | 2y | Cox HR | 0.705 | [0.705, 0.705] | 1 |
| AvsC_1to2_simple | 2y | Logit OR | 0.475 | [0.475, 0.475] | 1 |
| AvsC_1to2_simple | 3y | Cox HR | 0.776 | [0.776, 0.776] | 1 |
| AvsC_1to2_simple | 3y | Logit OR | 0.605 | [0.605, 0.605] | 1 |
| AvsC_1to2_simple | 5y | Cox HR | 0.689 | [0.689, 0.689] | 1 |
| AvsC_1to2_simple | 5y | Logit OR | 0.528 | [0.528, 0.528] | 1 |

## Tables

- `tables/descriptive_stats.csv` — covariate means by arm in matched cohorts (seed 0)
- `tables/results_HR.csv` — per (cell, window, seed) Cox PH HR + 95% CI + p
- `tables/results_OR.csv` — per (cell, window, seed) logit OR (GLM Binomial) + 95% CI + p
- `tables/results_incidence.csv` — per-1,000 person-year rates and IRR
- `tables/results_subgroup.csv` — subgroup HR/OR with BH-FDR interaction p
- `tables/results_seeded_aggregates.csv` — per-cell × per-window median + range across 10 seeds

## Figures (`figures/`)

For each cell × window: KM curve, incidence-rate bar, subgroup forest, and (per cell) 4-window HR-forest and OR-forest summaries.
