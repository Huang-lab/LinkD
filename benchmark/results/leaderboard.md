# LinkD Drug-Discovery Benchmark — Leaderboard

_Auto-generated. External-gold, head-to-head LinkD vs other agents/LLMs._

- **T1** drug-target binding vs TDC DAVIS (Pearson/C-Index/RMSE) — *LinkD strong*
- **A2** target identification vs OpenTargets approved targets (recall@k/nDCG/MRR) — *LinkD competitive*
- **A3** target prioritization (LinkD TPI vs phase) vs same gold — *LinkD competitive*
- **C1** target-disease validation, hard decoys (AUROC) — *LinkD-fusion limitation*
- **T2** drug repurposing vs repoDB approved/failed (AUROC) — *LinkD EHR coverage-blocked*

Deterministic agents run offline from cache; base LLMs run live (gpt-4o-mini/4o/4.1)._


## a2_target_id

| Condition | Model | recall@10 | recall@20 | ndcg@20 | mrr | lat_s/item |
|---|---|---|---|---|---|---|
| LinkD (phase-evidence) | tools-only | 0.265 | 0.439 | 0.515 | 0.572 | 0.090 |
| ToolUniverse-agent (OpenTargets) | opentargets | 0.281 | 0.478 | 0.531 | 0.657 | 0.000 |
| orchestrator | gpt-5.4 | 0.273 | 0.405 | 0.506 | 0.685 | 4.450 |
| combined | gpt-5.4 | 0.236 | 0.385 | 0.497 | 0.798 | 2.730 |
| orchestrator | claude-sonnet-4-6 | 0.245 | 0.377 | 0.492 | 0.748 | 6.660 |
| combined | claude-sonnet-4-6 | 0.248 | 0.382 | 0.487 | 0.775 | 3.980 |
| combined | gpt-4.1 | 0.232 | 0.358 | 0.459 | 0.692 | 2.230 |
| Base LLM (closed-book) | gpt-5.4 | 0.165 | 0.220 | 0.350 | 0.801 | 2.880 |
| Base LLM (closed-book) | claude-sonnet-4-6 | 0.169 | 0.206 | 0.318 | 0.672 | 4.040 |
| Base LLM (closed-book) | gpt-4.1 | 0.144 | 0.164 | 0.289 | 0.687 | 1.790 |
| Base LLM (closed-book) | gpt-4o | 0.110 | 0.152 | 0.252 | 0.620 | 1.840 |
| PubMed literature agent | literature | 0.069 | 0.088 | 0.154 | 0.536 | 0.000 |
| Base LLM (closed-book) | gpt-4o-mini | 0.109 | 0.125 | 0.147 | 0.415 | 1.140 |
| OpenTargets genetics-only | ot-genetics | 0.033 | 0.050 | 0.069 | 0.237 | 0.000 |

## a3_priority

| Condition | Model | recall@10 | recall@20 | ndcg@20 | mrr | lat_s/item |
|---|---|---|---|---|---|---|
| LinkD (phase-evidence) | tools-only | 0.265 | 0.439 | 0.515 | 0.572 | 0.080 |
| LinkD (TPI) | tools-only | 0.240 | 0.359 | 0.408 | 0.532 | 0.000 |
| ToolUniverse-agent (OpenTargets) | opentargets | 0.281 | 0.478 | 0.531 | 0.657 | 0.000 |
| orchestrator | gpt-5.4 | 0.273 | 0.391 | 0.518 | 0.824 | 4.000 |
| orchestrator | claude-sonnet-4-6 | 0.258 | 0.352 | 0.503 | 0.823 | 6.290 |
| combined | gpt-5.4 | 0.248 | 0.368 | 0.479 | 0.754 | 2.820 |
| combined | gpt-4.1 | 0.233 | 0.358 | 0.473 | 0.725 | 2.070 |
| combined | claude-sonnet-4-6 | 0.235 | 0.378 | 0.473 | 0.727 | 3.830 |
| Base LLM (closed-book) | claude-sonnet-4-6 | 0.193 | 0.234 | 0.335 | 0.689 | 3.730 |
| Base LLM (closed-book) | gpt-5.4 | 0.147 | 0.205 | 0.335 | 0.813 | 2.690 |
| Base LLM (closed-book) | gpt-4.1 | 0.154 | 0.190 | 0.325 | 0.780 | 2.100 |
| Base LLM (closed-book) | gpt-4o | 0.116 | 0.149 | 0.270 | 0.706 | 1.940 |
| Base LLM (closed-book) | gpt-4o-mini | 0.093 | 0.123 | 0.207 | 0.572 | 2.360 |
| PubMed literature agent | literature | 0.069 | 0.088 | 0.154 | 0.536 | 0.000 |
| OpenTargets genetics-only | ot-genetics | 0.033 | 0.050 | 0.069 | 0.237 | 0.000 |

## c1_validate

| Condition | Model | auroc | auprc | pos | neg | lat_s/item |
|---|---|---|---|---|---|---|
| LinkD (multi-evidence fusion) | tools-only | 0.392 | 0.435 | 72 | 72 | 0.270 |
| orchestrator | gpt-5.4 | 0.850 | 0.808 | 72 | 72 | 4.130 |
| Base LLM (closed-book) | gpt-5.4 | 0.788 | 0.770 | 72 | 72 | 1.350 |
| combined | gpt-5.4 | 0.757 | 0.764 | 72 | 72 | 1.470 |
| OpenTargets association | opentargets | 0.705 | 0.734 | 72 | 72 | 0.000 |

## l2_binding_moa

| Condition | Model | recall@10 | recall@20 | ndcg@20 | mrr | lat_s/item |
|---|---|---|---|---|---|---|
| LinkD (binding→target) | tools-only | 0.482 | 0.507 | 0.465 | 0.607 | 2.720 |
| Base LLM (closed-book) | claude-sonnet-4-6 | 0.915 | 0.928 | 0.902 | 0.928 | 2.610 |
| orchestrator | gpt-5.4 | 0.808 | 0.819 | 0.837 | 0.956 | 6.030 |
| Base LLM (closed-book) | gpt-5.4 | 0.805 | 0.815 | 0.834 | 0.928 | 1.970 |
| Base LLM (closed-book) | gpt-4.1 | 0.798 | 0.802 | 0.825 | 0.951 | 1.100 |
| combined | gpt-5.4 | 0.861 | 0.908 | 0.825 | 0.881 | 5.200 |
| combined | claude-sonnet-4-6 | 0.873 | 0.919 | 0.815 | 0.863 | 5.160 |
| combined | gpt-4.1 | 0.812 | 0.845 | 0.778 | 0.859 | 3.910 |
| Base LLM (closed-book) | gpt-4o | 0.664 | 0.671 | 0.694 | 0.837 | 1.040 |
| orchestrator | claude-sonnet-4-6 | 0.754 | 0.853 | 0.586 | 0.524 | 13.330 |
| Base LLM (closed-book) | gpt-4o-mini | 0.564 | 0.577 | 0.546 | 0.598 | 1.950 |

## l3_selectivity

| Condition | Model | auroc | auprc | pos | neg | lat_s/item |
|---|---|---|---|---|---|---|
| LinkD (selectivity) | tools-only | 0.474 | 0.580 | 19 | 16 | 0.010 |
| Base LLM (closed-book) | gpt-4.1 | 0.908 | 0.951 | 19 | 16 | 0.850 |
| Base LLM (closed-book) | gpt-4o | 0.881 | 0.919 | 13 | 11 | 1.150 |
| Base LLM (closed-book) | claude-sonnet-4-6 | 0.849 | 0.902 | 19 | 16 | 1.690 |
| Base LLM (closed-book) | gpt-5.4 | 0.845 | 0.888 | 19 | 16 | 1.510 |
| orchestrator | gpt-5.4 | 0.834 | 0.880 | 19 | 16 | 3.050 |
| combined | gpt-4.1 | 0.819 | 0.866 | 19 | 16 | 0.950 |
| combined | gpt-5.4 | 0.806 | 0.851 | 19 | 16 | 1.480 |
| combined | claude-sonnet-4-6 | 0.803 | 0.856 | 19 | 16 | 1.460 |
| orchestrator | claude-sonnet-4-6 | 0.743 | 0.701 | 19 | 16 | 4.730 |
| Base LLM (closed-book) | gpt-4o-mini | 0.665 | 0.768 | 17 | 15 | 1.220 |

## l4_crispr_moa

| Condition | Model | recall@10 | recall@20 | ndcg@20 | mrr | lat_s/item |
|---|---|---|---|---|---|---|
| LinkD (CRISPR→target) | tools-only | 0.535 | 0.535 | 0.587 | 0.818 | 0.190 |
| combined | claude-sonnet-4-6 | 0.868 | 0.876 | 0.851 | 0.908 | 2.610 |
| Base LLM (closed-book) | claude-sonnet-4-6 | 0.846 | 0.889 | 0.840 | 0.866 | 2.510 |
| combined | gpt-5.4 | 0.847 | 0.863 | 0.836 | 0.908 | 1.870 |
| orchestrator | gpt-5.4 | 0.812 | 0.840 | 0.818 | 0.894 | 1.900 |
| Base LLM (closed-book) | gpt-5.4 | 0.819 | 0.842 | 0.808 | 0.880 | 1.810 |
| combined | gpt-4.1 | 0.741 | 0.741 | 0.752 | 0.859 | 1.340 |
| Base LLM (closed-book) | gpt-4.1 | 0.710 | 0.712 | 0.734 | 0.837 | 1.240 |
| Base LLM (closed-book) | gpt-4o | 0.708 | 0.717 | 0.730 | 0.854 | 0.950 |
| orchestrator | claude-sonnet-4-6 | 0.786 | 0.934 | 0.506 | 0.281 | 11.650 |
| Base LLM (closed-book) | gpt-4o-mini | 0.483 | 0.496 | 0.493 | 0.564 | 1.950 |

## l9_safety

| Condition | Model | auroc | auprc | pos | neg | lat_s/item |
|---|---|---|---|---|---|---|
| LinkD (EHR real-world) | tools-only | 0.360 | 0.526 | 27 | 27 | 0.030 |
| Base LLM (closed-book) | gpt-4o | 0.519 | 1.000 | 27 | 27 | 0.840 |
| Base LLM (closed-book) | gpt-4.1 | 0.516 | 0.836 | 27 | 27 | 0.860 |
| Base LLM (closed-book) | claude-sonnet-4-6 | 0.514 | 0.642 | 27 | 27 | 1.830 |
| Base LLM (closed-book) | gpt-5.4 | 0.481 | 0.499 | 27 | 27 | 1.170 |
| combined | gpt-5.4 | 0.410 | 0.527 | 27 | 27 | 1.370 |
| orchestrator | claude-sonnet-4-6 | 0.384 | 0.465 | 27 | 27 | 5.230 |
| Base LLM (closed-book) | gpt-4o-mini | 0.353 | 0.533 | 27 | 27 | 1.300 |
| combined | claude-sonnet-4-6 | 0.350 | 0.469 | 27 | 27 | 1.510 |
| combined | gpt-4.1 | 0.346 | 0.472 | 27 | 27 | 0.900 |
| orchestrator | gpt-5.4 | 0.239 | 0.375 | 27 | 27 | 3.400 |

## t1_dti

| Condition | Model | pearson | spearman | c_index | rmse | binary_acc | answered | lat_s/item |
|---|---|---|---|---|---|---|---|---|
| LinkD (tools-only) | tools-only | 0.754 | 0.764 | 0.819 | 0.838 | 0.846 | 78 | 0.750 |
| orchestrator | gpt-5.4 | 0.753 | 0.764 | 0.819 | 0.838 | 0.821 | 78 | 3.050 |
| combined | gpt-4.1 | 0.726 | 0.736 | 0.790 | 1.002 | 0.769 | 78 | 1.790 |
| combined | gpt-5.4 | 0.684 | 0.701 | 0.772 | 1.114 | 0.692 | 78 | 2.050 |
| orchestrator | claude-sonnet-4-6 | -0.098 | 0.481 | 0.692 | 345019.799 | 0.795 | 78 | 6.110 |
| combined | claude-sonnet-4-6 | 0.304 | 0.356 | 0.642 | 2.558 | 0.679 | 78 | 11.840 |
| Base LLM (closed-book) | gpt-4.1 | 0.365 | 0.211 | 0.628 | 1.498 | 0.462 | 78 | 1.030 |
| Base LLM (closed-book) | gpt-5.4 | -0.037 | -0.041 | 0.518 | 1.828 | 0.359 | 78 | 1.440 |
| Base LLM (closed-book) | claude-sonnet-4-6 | -0.309 | -0.548 | 0.392 | 4.994 | 0.667 | 78 | 11.030 |
| Base LLM (closed-book) | gpt-4o-mini |  |  |  |  | 0.679 | 0 | 0.820 |
| Base LLM (closed-book) | gpt-4o |  |  |  |  | 0.692 | 1 | 0.760 |

## t2_repurpose

| Condition | Model | auroc | auprc | pos | neg | lat_s/item |
|---|---|---|---|---|---|---|
| LinkD (EHR real-world) | tools-only | 0.500 | 0.545 | 90 | 90 | 0.030 |
| combined | gpt-4.1 | 0.751 | 0.756 | 90 | 90 | 0.990 |
| Base LLM (closed-book) | gpt-4.1 | 0.750 | 0.756 | 90 | 90 | 0.960 |
| Base LLM (closed-book) | gpt-5.4 | 0.745 | 0.718 | 90 | 90 | 1.250 |
| combined | gpt-5.4 | 0.743 | 0.715 | 90 | 90 | 1.160 |
| Base LLM (closed-book) | claude-sonnet-4-6 | 0.740 | 0.665 | 90 | 90 | 1.590 |
| Base LLM (closed-book) | gpt-4o-mini | 0.738 | 0.703 | 90 | 90 | 0.840 |
| combined | claude-sonnet-4-6 | 0.737 | 0.663 | 90 | 90 | 1.780 |
| orchestrator | claude-sonnet-4-6 | 0.728 | 0.669 | 90 | 90 | 4.980 |
| orchestrator | gpt-5.4 | 0.721 | 0.698 | 90 | 90 | 1.270 |
| Base LLM (closed-book) | gpt-4o | 0.710 | 0.706 | 90 | 90 | 0.870 |

## t4_crispr_conc

| Condition | Model |  |
|---|---|
| linkd_crispr_pair | tools-only |  |
| Base LLM (closed-book) | gpt-5.4 |  |
| Base LLM (closed-book) | claude-sonnet-4-6 |  |
| combined | gpt-5.4 |  |
| combined | claude-sonnet-4-6 |  |
| orchestrator | gpt-5.4 |  |
| orchestrator | claude-sonnet-4-6 |  |

## t5_concordance

| Condition | Model |  |
|---|---|
| linkd_fusion_pair | tools-only |  |
| Base LLM (closed-book) | gpt-5.4 |  |
| Base LLM (closed-book) | claude-sonnet-4-6 |  |
| combined | gpt-5.4 |  |
| combined | claude-sonnet-4-6 |  |
| orchestrator | gpt-5.4 |  |
| orchestrator | claude-sonnet-4-6 |  |

## t7_sel_retrieval

| Condition | Model |  |
|---|---|
| linkd_target_aff | tools-only |  |
| Base LLM (closed-book) | gpt-5.4 |  |
| Base LLM (closed-book) | claude-sonnet-4-6 |  |
| combined | gpt-5.4 |  |
| combined | claude-sonnet-4-6 |  |
| orchestrator | gpt-5.4 |  |
| orchestrator | claude-sonnet-4-6 |  |

## External benchmarks (context — reported by authors, not re-run here)

| System | Benchmark | Metric | Reference |
|---|---|---|---|
| TxAgent / ToolUniverse | DrugPC / BrandPC / GenericPC / TreatmentPC / DescriptionPC (3,168 drug-reasoning tasks) | correctness / tool-utilization / reasoning-quality | arXiv 2503.10970 (mims-harvard, 2025) |
| CURE-Bench (NeurIPS 2025) | therapeutic reasoning — MC / Open-Ended / OE-MC (val 459; test 2,097 / 2,491) | correctness / tool-utilization / reasoning-quality | arXiv 2512.11682 |
| MedAgentBench | virtual-EHR agent tasks | task success | NEJM AI (2025) |
| BixBench | 53 real computational-biology analysis scenarios | accuracy | arXiv 2503.00096 (Future-House) |
| DeepDTA / GraphDTA (DTI specialists) | DAVIS drug-target affinity (Concordance Index) | C-Index | Ozturk 2018 (Bioinformatics) / Nguyen 2021 (Bioinformatics) |
| Open Targets (target-disease association) | target identification — associated targets per disease | association score / recall of approved-drug targets | Ochoa 2023 (Nucleic Acids Res); platform.opentargets.org |
