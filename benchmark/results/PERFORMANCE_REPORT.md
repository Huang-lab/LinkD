# LinkD-Agent Supplementary Benchmark — Performance Report

_Auto-generated from `results/summary.*.jsonl`. Seven tasks aligned to LinkD's described modules (LinkD-Bind, causal/clinical target evidence, Target Priority Index, CRISPR drug-response, weighted multi-evidence fusion, selectivity), each scored against the most independent external gold. Tasks are grouped by **type**, defined a priori: **Prediction** = the answer must be computed from molecular/clinical data (LinkD's design target, not memorizable); **Mechanism/Integration** = infer or fuse evidence; **Knowledge** = the answer is a documented fact (LLM home turf). **Best LLM** / **Combined** pick the strongest model per task (named in cell); LLM tiers = gpt-5.4, claude-sonnet-4-6, gpt-4.1/4o/4o-mini. **SOTA tool-agent** = best of ToolUniverse(OpenTargets) / OT-genetics / OT-association / PubMed (where applicable). Router = per-task max(LinkD, LLM). Higher = better on every metric. Two gold-limited diagnostics (EHR repurposing, FAERS safety) are reported separately below and excluded from the headline averages — see the appendix for why._

| # | Type | LinkD feature | Metric | LinkD | Best LLM | Combined | **Orchestrator** | SOTA tool-agent | Router | orch−best |
|---|---|---|---|---|---|---|---|---|---|---|
| T1 | Prediction | LinkD-Bind predicted pKd | c_index | 0.819 | 0.628 (gpt-4.1) | 0.790 (gpt-4.1) | **0.819 (gpt-5.4)** | — | 0.819 | +0.000 |
| T2 | Prediction | Causal + clinical-phase evidence | ndcg@20 | 0.515 | 0.350 (gpt-5.4) | 0.497 (gpt-5.4) | **0.506 (gpt-5.4)** | 0.531 (ToolUniverse-agent) | 0.515 | -0.009 |
| T3 | Prediction | Target Priority Index (TPI) | ndcg@20 | 0.515 | 0.335 (claude-sonnet-4-6) | 0.479 (gpt-5.4) | **0.518 (gpt-5.4)** | 0.531 (ToolUniverse-agent) | 0.515 | +0.003 |
| T4 | Mechanism | CRISPR drug-response corr. | ndcg@20 | 0.587 | 0.840 (claude-sonnet-4-6) | 0.851 (claude-sonnet-4-6) | **0.818 (gpt-5.4)** | — | 0.840 | -0.022 |
| T5 | Integration | Weighted multi-evidence fusion | auroc | 0.467 | 0.759 (gpt-5.4) | 0.725 (gpt-5.4) | **0.806 (gpt-5.4)** | 0.652 (OpenTargets) | 0.759 | +0.047 |
| T6 | Knowledge | Binding → mechanism rank | ndcg@20 | 0.465 | 0.902 (claude-sonnet-4-6) | 0.825 (gpt-5.4) | **0.837 (gpt-5.4)** | — | 0.902 | -0.065 |
| T7 | Knowledge | Selectivity score | auroc | 0.474 | 0.908 (gpt-4.1) | 0.819 (gpt-4.1) | **0.834 (gpt-5.4)** | — | 0.908 | -0.074 |
| — | _Prediction mean (n=3)_ | — | — | _0.616_ | _0.438_ | _0.589_ | _**0.614**_ | — | _0.616_ | -0.002 |
| — | _Mechanism mean (n=1)_ | — | — | _0.587_ | _0.840_ | _0.851_ | _**0.818**_ | — | _0.840_ | -0.022 |
| — | _Integration mean (n=1)_ | — | — | _0.467_ | _0.759_ | _0.725_ | _**0.806**_ | — | _0.759_ | +0.047 |
| — | _Knowledge mean (n=2)_ | — | — | _0.470_ | _0.905_ | _0.822_ | _**0.835**_ | — | _0.905_ | -0.070 |
| — | **Overall** | **Average (n=7 tasks)** | — | **0.549** | **0.675** | **0.712** | **0.734** | — | **0.751** | +0.059 |

## Retained benchmark summary

Averaged over the 7 headline tasks: **LinkD 0.549** · **best-LLM 0.675** · **Combined (equal-weight) 0.712** · **Orchestrator (LLM-calls-LinkD) 0.734** · **Router-oracle 0.751**.

- On the three *Prediction* tasks, **LinkD alone (0.616) scored above the strongest retained closed-book LLM selected per task (0.438)**. This comparison is limited to the retained fixtures and metrics.

- **The LLM wins knowledge recall.** On the *Knowledge* tasks (naming a drug's MoA target, judging selectivity from the drug name) the answer is a documented fact, so a frontier LLM is far stronger — as expected for a database vs a knowledge model.

- The retained orchestrator had the highest evaluated aggregate among the deployable conditions (0.734) and was below the descriptive router-oracle (0.751). This does not establish superiority outside these tasks.

- **Caveat:** the agent is only as reliable as the model's tool-use + output formatting. Per-task detail below shows each model's behavior.


**Scope:** this is a retained supplementary benchmark, not a submitted figure panel or an application-wide accuracy estimate. See `agent_benchmark.py` and `TASK_CATALOG.md`.


## Appendix — gold-limited diagnostics (excluded from headline averages)

_These two EHR tasks are reported for completeness but **excluded from the averages above** because the external gold is structurally misaligned with LinkD's data scope — a measurement-alignment problem, not a capability gap:_

- **D1 repurposing:** repoDB approved/failed indications barely overlap LinkD's EHR cohorts — only **3 of 120** sampled pairs have any EHR odds-ratio, so LinkD is forced to 0.5 (chance) on the rest. The task measures cohort coverage, not the EHR signal's quality.

- **D2 safety:** FAERS encodes **MedDRA** adverse-event terms while LinkD's EHR encodes **ICD** disease odds ratios; only lexically-matchable conditions are usable, so the gold and the prediction live in different ontologies.

| # | Type | LinkD feature | Metric | LinkD | Best LLM | Combined | **Orchestrator** | SOTA tool-agent | Router | orch−best |
|---|---|---|---|---|---|---|---|---|---|---|
| D1 | Gold-limited | EHR real-world OR | auroc | 0.500 | 0.750 (gpt-4.1) | 0.751 (gpt-4.1) | **0.728 (claude-sonnet-4-6)** | — | 0.750 | -0.022 |
| D2 | Gold-limited | EHR risk OR | auroc | 0.360 | 0.519 (gpt-4o) | 0.410 (gpt-5.4) | **0.384 (claude-sonnet-4-6)** | — | 0.519 | -0.135 |

## Per-task detail

### T1 · LinkD-Bind predicted pKd — Drug–target binding affinity  *(type: Prediction)*
- **Definition:** Predict the binding affinity pKd for a drug (SMILES/ChEMBL) against a human kinase. *(unit = one (drug, kinase) pair, n = 78)*
- **Gold:** TDC DAVIS experimental Kd → pKd = −log10(Kd[M]); stratified 78-pair held-out test.
- **LinkD signal:** predicted pKd from the pan-target binding parquet (get_drug_target_binding_affinity).
- **LLM:** closed-book: 'estimate pKd for this SMILES + protein'.
- **Combined fusion:** MEAN of the two predicted pKd values (label = pKd≥7).
- **Metric:** c_index (+ pearson, rmse, binary_acc)
- **Combined vs best-single:** ⚠️ fusion HURTS (-0.029) — equal-weight value-mean blends 50/50 with no reliability gate, so the stronger source (LinkD, 0.819) is dragged toward the weaker (the LLM, 0.628) → 0.790.

| Condition | Model | c_index | pearson | rmse | binary_acc | n |
|---|---|---|---|---|---|---|
| LinkD (tools-only) | tools-only | 0.819 | 0.754 | 0.838 | 0.846 | 78 |
| orchestrator | gpt-5.4 | 0.819 | 0.753 | 0.838 | 0.821 | 78 |
| combined | gpt-4.1 | 0.790 | 0.726 | 1.002 | 0.769 | 78 |
| combined | gpt-5.4 | 0.772 | 0.684 | 1.114 | 0.692 | 78 |
| orchestrator | claude-sonnet-4-6 | 0.692 | -0.098 | 345019.799 | 0.795 | 78 |
| combined | claude-sonnet-4-6 | 0.642 | 0.304 | 2.558 | 0.679 | 78 |
| Base LLM (closed-book) | gpt-4.1 | 0.628 | 0.365 | 1.498 | 0.462 | 78 |
| Base LLM (closed-book) | gpt-5.4 | 0.518 | -0.037 | 1.828 | 0.359 | 78 |
| Base LLM (closed-book) | claude-sonnet-4-6 | 0.392 | -0.309 | 4.994 | 0.667 | 78 |
| Base LLM (closed-book) | gpt-4o-mini | — | — | — | 0.679 | 78 |
| Base LLM (closed-book) | gpt-4o | — | — | — | 0.692 | 78 |

### T2 · Causal + clinical-phase evidence — Disease target identification (cancer)  *(type: Prediction)*
- **Definition:** Rank candidate drug-target genes for a cancer. *(unit = one cancer (rank genes), n = 25)*
- **Gold:** OpenTargets approved-drug targets for the disease (25 cancers).
- **LinkD signal:** genes ranked by clinical-phase evidence + causal gene-disease (drug_target_disease).
- **LLM:** closed-book: 'list drug targets for disease D'.
- **Combined fusion:** reciprocal-rank fusion (RRF, k=60) of the two gene rankings.
- **Metric:** ndcg@20 (+ recall@20, mrr)
- **Combined vs best-single:** ⚠️ fusion HURTS (-0.018) — equal-weight RRF blends 50/50 with no reliability gate, so the stronger source (LinkD, 0.515) is dragged toward the weaker (the LLM, 0.350) → 0.497.

| Condition | Model | ndcg@20 | recall@20 | mrr | n |
|---|---|---|---|---|---|
| LinkD (phase-evidence) | tools-only | 0.515 | 0.439 | 0.572 | 25 |
| ToolUniverse-agent (OpenTargets) | opentargets | 0.531 | 0.478 | 0.657 | 25 |
| orchestrator | gpt-5.4 | 0.506 | 0.405 | 0.685 | 25 |
| combined | gpt-5.4 | 0.497 | 0.385 | 0.798 | 25 |
| orchestrator | claude-sonnet-4-6 | 0.492 | 0.377 | 0.748 | 25 |
| combined | claude-sonnet-4-6 | 0.487 | 0.382 | 0.775 | 25 |
| combined | gpt-4.1 | 0.459 | 0.358 | 0.692 | 25 |
| Base LLM (closed-book) | gpt-5.4 | 0.350 | 0.220 | 0.801 | 25 |
| Base LLM (closed-book) | claude-sonnet-4-6 | 0.318 | 0.206 | 0.672 | 25 |
| Base LLM (closed-book) | gpt-4.1 | 0.289 | 0.164 | 0.687 | 25 |
| Base LLM (closed-book) | gpt-4o | 0.252 | 0.152 | 0.620 | 25 |
| PubMed literature agent | literature | 0.154 | 0.088 | 0.536 | 25 |
| Base LLM (closed-book) | gpt-4o-mini | 0.147 | 0.125 | 0.415 | 25 |
| OpenTargets genetics-only | ot-genetics | 0.069 | 0.050 | 0.237 | 25 |

### T3 · Target Priority Index (TPI) — Druggable target prioritization  *(type: Prediction)*
- **Definition:** Prioritize drug-target genes for a cancer by druggability / clinical maturity. *(unit = one cancer (rank genes), n = 25)*
- **Gold:** OpenTargets approved-drug targets (25 cancers).
- **LinkD signal:** Target Priority Index (TPI) and the phase-evidence ranker.
- **LLM:** closed-book: 'prioritize druggable targets for disease D'.
- **Combined fusion:** reciprocal-rank fusion (RRF, k=60) of the two gene rankings.
- **Metric:** ndcg@20 (+ recall@20, mrr)
- **Combined vs best-single:** ⚠️ fusion HURTS (-0.036) — equal-weight RRF blends 50/50 with no reliability gate, so the stronger source (LinkD, 0.515) is dragged toward the weaker (the LLM, 0.335) → 0.479.

| Condition | Model | ndcg@20 | recall@20 | mrr | n |
|---|---|---|---|---|---|
| LinkD (phase-evidence) | tools-only | 0.515 | 0.439 | 0.572 | 25 |
| LinkD (TPI) | tools-only | 0.408 | 0.359 | 0.532 | 25 |
| ToolUniverse-agent (OpenTargets) | opentargets | 0.531 | 0.478 | 0.657 | 25 |
| orchestrator | gpt-5.4 | 0.518 | 0.391 | 0.824 | 25 |
| orchestrator | claude-sonnet-4-6 | 0.503 | 0.352 | 0.823 | 25 |
| combined | gpt-5.4 | 0.479 | 0.368 | 0.754 | 25 |
| combined | gpt-4.1 | 0.473 | 0.358 | 0.725 | 25 |
| combined | claude-sonnet-4-6 | 0.473 | 0.378 | 0.727 | 25 |
| Base LLM (closed-book) | claude-sonnet-4-6 | 0.335 | 0.234 | 0.689 | 25 |
| Base LLM (closed-book) | gpt-5.4 | 0.335 | 0.205 | 0.813 | 25 |
| Base LLM (closed-book) | gpt-4.1 | 0.325 | 0.190 | 0.780 | 25 |
| Base LLM (closed-book) | gpt-4o | 0.270 | 0.149 | 0.706 | 25 |
| Base LLM (closed-book) | gpt-4o-mini | 0.207 | 0.123 | 0.572 | 25 |
| PubMed literature agent | literature | 0.154 | 0.088 | 0.536 | 25 |
| OpenTargets genetics-only | ot-genetics | 0.069 | 0.050 | 0.237 | 25 |

### T4 · CRISPR drug-response corr. — Mechanism target from CRISPR rank  *(type: Mechanism)*
- **Definition:** Rank a drug's mechanism target genes from its CRISPR drug-response correlation. *(unit = one drug (rank its targets), n = 60)*
- **Gold:** ChEMBL/OpenTargets MoA targets for 60 drugs (pharmacology — independent of the GDSC/PRISM screen).
- **LinkD signal:** genes ranked by |CRISPR drug-response correlation| (get_drug_response_associations, AUC_corr).
- **LLM:** closed-book: 'list the molecular targets of drug X'.
- **Combined fusion:** reciprocal-rank fusion (RRF, k=60) of the two gene rankings.
- **Metric:** ndcg@20 (+ recall@20, mrr)
- **Combined vs best-single:** ✅ fusion HELPS (+0.011) — LinkD (0.587) and the LLM (0.840) are comparably strong and make different errors, so RRF adds signal.

| Condition | Model | ndcg@20 | recall@20 | mrr | n |
|---|---|---|---|---|---|
| LinkD (CRISPR→target) | tools-only | 0.587 | 0.535 | 0.818 | 60 |
| combined | claude-sonnet-4-6 | 0.851 | 0.876 | 0.908 | 60 |
| Base LLM (closed-book) | claude-sonnet-4-6 | 0.840 | 0.889 | 0.866 | 60 |
| combined | gpt-5.4 | 0.836 | 0.863 | 0.908 | 60 |
| orchestrator | gpt-5.4 | 0.818 | 0.840 | 0.894 | 60 |
| Base LLM (closed-book) | gpt-5.4 | 0.808 | 0.842 | 0.880 | 60 |
| combined | gpt-4.1 | 0.752 | 0.741 | 0.859 | 60 |
| Base LLM (closed-book) | gpt-4.1 | 0.734 | 0.712 | 0.837 | 60 |
| Base LLM (closed-book) | gpt-4o | 0.730 | 0.717 | 0.854 | 60 |
| orchestrator | claude-sonnet-4-6 | 0.506 | 0.934 | 0.281 | 60 |
| Base LLM (closed-book) | gpt-4o-mini | 0.493 | 0.496 | 0.564 | 60 |

### T5 · Weighted multi-evidence fusion — Target–disease validation (hard decoys)  *(type: Integration)*
- **Definition:** Score whether a gene is a drug's validated target, among the disease's other validated targets. *(unit = one (drug, gene, disease) triad, n = 152)*
- **Gold:** positive = approved drug's true MoA target; HARD negative = another validated target of the SAME disease, excluding all known targets of the same drug.
- **LinkD signal:** weighted multi-evidence final_score (get_comprehensive_drug_target_evidence).
- **LLM:** closed-book: 'confidence gene G is an established target in disease D (0–1)'.
- **Combined fusion:** MEAN of the two 0–1 scores.
- **Metric:** auroc (+ auprc)
- **Combined vs best-single:** ⚠️ fusion HURTS (-0.034) — equal-weight score-mean blends 50/50 with no reliability gate, so the stronger source (the LLM, 0.759) is dragged toward the weaker (LinkD, 0.467) → 0.725.

| Condition | Model | auroc | auprc | n |
|---|---|---|---|---|
| LinkD (multi-evidence fusion) | tools-only | 0.467 | 0.435 | 152 |
| orchestrator | gpt-5.4 | 0.806 | 0.808 | 152 |
| Base LLM (closed-book) | gpt-5.4 | 0.759 | 0.770 | 152 |
| combined | gpt-5.4 | 0.725 | 0.764 | 152 |
| OpenTargets association | opentargets | 0.652 | 0.734 | 152 |

### T6 · Binding → mechanism rank — Recover MoA target (knowledge recall)  *(type: Knowledge)*
- **Definition:** Rank a drug's molecular mechanism-of-action target genes. KNOWLEDGE-RECALL task — a drug's canonical MoA target is a documented fact, so a frontier LLM is expected to win; LinkD must rediscover it from predicted binding, which is noisier than memory. *(unit = one drug (rank its targets), n = 44)*
- **Gold:** ChEMBL/OpenTargets mechanism targets for 44 DAVIS drugs (gene set).
- **LinkD signal:** targets ranked by predicted binding affinity (get_targets_for_drug_with_affinity), UniProt-mnemonic→gene.
- **LLM:** closed-book: 'list the molecular targets of drug X'.
- **Combined fusion:** reciprocal-rank fusion (RRF, k=60) of the two gene rankings.
- **Metric:** ndcg@20 (+ recall@20, mrr)
- **Combined vs best-single:** ⚠️ fusion HURTS (-0.077) — equal-weight RRF blends 50/50 with no reliability gate, so the stronger source (the LLM, 0.902) is dragged toward the weaker (LinkD, 0.465) → 0.825.

| Condition | Model | ndcg@20 | recall@20 | mrr | n |
|---|---|---|---|---|---|
| LinkD (binding→target) | tools-only | 0.465 | 0.507 | 0.607 | 44 |
| Base LLM (closed-book) | claude-sonnet-4-6 | 0.902 | 0.928 | 0.928 | 44 |
| orchestrator | gpt-5.4 | 0.837 | 0.819 | 0.956 | 44 |
| Base LLM (closed-book) | gpt-5.4 | 0.834 | 0.815 | 0.928 | 44 |
| Base LLM (closed-book) | gpt-4.1 | 0.825 | 0.802 | 0.951 | 44 |
| combined | gpt-5.4 | 0.825 | 0.908 | 0.881 | 44 |
| combined | claude-sonnet-4-6 | 0.815 | 0.919 | 0.863 | 44 |
| combined | gpt-4.1 | 0.778 | 0.845 | 0.859 | 44 |
| Base LLM (closed-book) | gpt-4o | 0.694 | 0.671 | 0.837 | 44 |
| orchestrator | claude-sonnet-4-6 | 0.586 | 0.853 | 0.524 | 44 |
| Base LLM (closed-book) | gpt-4o-mini | 0.546 | 0.577 | 0.598 | 44 |

### T7 · Selectivity score — Selective vs promiscuous (knowledge recall)  *(type: Knowledge)*
- **Definition:** Classify a kinase inhibitor as selective vs promiscuous. KNOWLEDGE-RECALL task, AND gold-scope-mismatched: gold is KINOME promiscuity while LinkD's score is PROTEOME-wide. *(unit = one drug, n = 35)*
- **Gold:** TDC DAVIS full kinome matrix — # kinases bound at pKd≥7; selective = bottom tercile, promiscuous = top tercile.
- **LinkD signal:** LinkD precomputed Selectivity_Score (computed PROTEOME-wide over ~20k targets). It measures a different quantity than kinome promiscuity — confirmed weak alignment (Spearman ρ≈0.19 vs the DAVIS kinome count; the best-correlated column reaches only ρ≈0.38), so this is a scope mismatch, not a capability gap. Deriving selectivity from LinkD's predicted kinome profile (entropy of predicted pKd over the shared kinases) also stays weak (ρ≈0.25).
- **LLM:** closed-book: 'how selective (0–1) is drug X'.
- **Combined fusion:** MEAN of the two 0–1 selectivity scores.
- **Metric:** auroc (+ auprc)
- **Combined vs best-single:** ⚠️ fusion HURTS (-0.089) — equal-weight score-mean blends 50/50 with no reliability gate, so the stronger source (the LLM, 0.908) is dragged toward the weaker (LinkD, 0.474) → 0.819.

| Condition | Model | auroc | auprc | n |
|---|---|---|---|---|
| LinkD (selectivity) | tools-only | 0.474 | 0.580 | 35 |
| Base LLM (closed-book) | gpt-4.1 | 0.908 | 0.951 | 35 |
| Base LLM (closed-book) | gpt-4o | 0.881 | 0.919 | 35 |
| Base LLM (closed-book) | claude-sonnet-4-6 | 0.849 | 0.902 | 35 |
| Base LLM (closed-book) | gpt-5.4 | 0.845 | 0.888 | 35 |
| orchestrator | gpt-5.4 | 0.834 | 0.880 | 35 |
| combined | gpt-4.1 | 0.819 | 0.866 | 35 |
| combined | gpt-5.4 | 0.806 | 0.851 | 35 |
| combined | claude-sonnet-4-6 | 0.803 | 0.856 | 35 |
| orchestrator | claude-sonnet-4-6 | 0.743 | 0.701 | 35 |
| Base LLM (closed-book) | gpt-4o-mini | 0.665 | 0.768 | 35 |

### D1 · EHR real-world OR — Drug repurposing (EHR coverage-limited)  *(type: Gold-limited)*
- **Definition:** Predict whether a drug-disease pair is an approved indication (vs failed). *(unit = one (drug, disease) pair, n = 180)*
- **Gold:** repoDB approved (+) vs failed/terminated/withdrawn (−), 180 balanced; DrugBank→ChEMBL, indication→ICD via LinkD labels.
- **LinkD signal:** EHR real-world odds ratio (protective OR<1 → high score).
- **LLM:** closed-book: 'confidence drug X is an approved treatment for disease Y (0–1)'.
- **Combined fusion:** MEAN of the two 0–1 scores.
- **Metric:** auroc (+ auprc)
- **Combined vs best-single:** ✅ fusion HELPS (+0.001) — LinkD (0.500) and the LLM (0.750) are comparably strong and make different errors, so score-mean adds signal.

| Condition | Model | auroc | auprc | n |
|---|---|---|---|---|
| LinkD (EHR real-world) | tools-only | 0.500 | 0.545 | 180 |
| combined | gpt-4.1 | 0.751 | 0.756 | 180 |
| Base LLM (closed-book) | gpt-4.1 | 0.750 | 0.756 | 180 |
| Base LLM (closed-book) | gpt-5.4 | 0.745 | 0.718 | 180 |
| combined | gpt-5.4 | 0.743 | 0.715 | 180 |
| Base LLM (closed-book) | claude-sonnet-4-6 | 0.740 | 0.665 | 180 |
| Base LLM (closed-book) | gpt-4o-mini | 0.738 | 0.703 | 180 |
| combined | claude-sonnet-4-6 | 0.737 | 0.663 | 180 |
| orchestrator | claude-sonnet-4-6 | 0.728 | 0.669 | 180 |
| orchestrator | gpt-5.4 | 0.721 | 0.698 | 180 |
| Base LLM (closed-book) | gpt-4o | 0.710 | 0.706 | 180 |

### D2 · EHR risk OR — Adverse-event signal (ontology-misaligned)  *(type: Gold-limited)*
- **Definition:** Predict whether a condition is a reported adverse event of a drug. *(unit = one (drug, condition) pair, n = 54)*
- **Gold:** openFDA FAERS adverse-reaction terms vs LinkD EHR conditions, 54 balanced (only 27 of 1,719 EHR conditions lexically matched a FAERS term).
- **LinkD signal:** EHR risk odds ratio (OR>1 → high score).
- **LLM:** closed-book: 'likelihood condition Y is an adverse event of drug X (0–1)'.
- **Combined fusion:** MEAN of the two 0–1 scores.
- **Metric:** auroc (+ auprc)
- **Combined vs best-single:** ⚠️ fusion HURTS (-0.109) — equal-weight score-mean blends 50/50 with no reliability gate, so the stronger source (the LLM, 0.519) is dragged toward the weaker (LinkD, 0.360) → 0.410.

| Condition | Model | auroc | auprc | n |
|---|---|---|---|---|
| LinkD (EHR real-world) | tools-only | 0.360 | 0.526 | 54 |
| Base LLM (closed-book) | gpt-4o | 0.519 | 1.000 | 54 |
| Base LLM (closed-book) | gpt-4.1 | 0.516 | 0.836 | 54 |
| Base LLM (closed-book) | claude-sonnet-4-6 | 0.514 | 0.642 | 54 |
| Base LLM (closed-book) | gpt-5.4 | 0.481 | 0.499 | 54 |
| combined | gpt-5.4 | 0.410 | 0.527 | 54 |
| orchestrator | claude-sonnet-4-6 | 0.384 | 0.465 | 54 |
| Base LLM (closed-book) | gpt-4o-mini | 0.353 | 0.533 | 54 |
| combined | claude-sonnet-4-6 | 0.350 | 0.469 | 54 |
| combined | gpt-4.1 | 0.346 | 0.472 | 54 |
| orchestrator | gpt-5.4 | 0.239 | 0.375 | 54 |

