# LinkD-Agent supplementary benchmark task catalog

This is the canonical seven-task (T1–T7) supplementary evaluation. The labels
are benchmark IDs, not submitted manuscript panel labels.

## Headline tasks

| ID | Code scenario | Task file | Primary metric | n |
|---|---|---|---|---:|
| T1 binding affinity | `t1_dti` | `tasks/t1_dti.test.jsonl` | C-index | 78 |
| T2 target identification | `a2_target_id` | `tasks/a2_target_id.test.jsonl` | nDCG@20 | 25 |
| T3 target prioritization | `a3_priority` | `tasks/a3_priority.test.jsonl` | nDCG@20 | 25 |
| T4 CRISPR → MoA | `l4_crispr_moa` | `tasks/l4_crispr_moa.test.jsonl` | nDCG@20 | 60 |
| T5 evidence fusion | `c1_validate` | `tasks/c1_validate.test.jsonl` | AUROC | 144 |
| T6 binding → MoA | `l2_binding_moa` | `tasks/l2_binding_moa.test.jsonl` | nDCG@20 | 44 |
| T7 selectivity | `l3_selectivity` | `tasks/l3_selectivity.test.jsonl` | AUROC | 35 |

## Diagnostics excluded from headline means

| ID | Code scenario | Task file | Limitation |
|---|---|---|---|
| D1 repurposing | `t2_repurpose` | `tasks/t2_repurpose.test.jsonl` | repoDB–EHR coverage |
| D2 safety | `l9_safety` | `tasks/l9_safety.test.jsonl` | FAERS MedDRA–ICD ontology mismatch |

## Conditions

| Displayed method | Code condition(s) |
|---|---|
| LinkD tools-only | `linkd_cli`, `linkd`, `linkd_evidence`, and layer-specific deterministic conditions |
| Closed-book LLM | `closed_book` |
| External tool baseline | `tooluniverse`, `ot_genetics`, `ot_assoc`, `pubmed` |
| Combined | `combined` |
| LinkD-Agent orchestrator | `orchestrator` |

The primary retained LLM identifier is `gpt-5.4`; other retained comparisons
are listed in the result JSONL. Current values are generated from the on-disk
fixtures and summaries. Do not combine them with values from superseded runs.
