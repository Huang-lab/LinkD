# LinkD agent benchmark — task catalog (Manuscript / SI)

Canonical **7-task** oncology agent benchmark for Figure 6c and SI Tables S1–S5.
Legacy code scenario IDs are kept as filenames; use the **Manuscript ID** column in prose.

## Headline tasks (Fig 6c)

| Manuscript | Code scenario | Task file | Metric | n (on disk) |
|---|---|---|---|---|
| **T1** binding affinity | `t1_dti` | `tasks/t1_dti.test.jsonl` | C-Index | 78 |
| **T2** target identification | `a2_target_id` | `tasks/a2_target_id.test.jsonl` | nDCG@20 | 25 |
| **T3** target prioritization | `a3_priority` | `tasks/a3_priority.test.jsonl` | nDCG@20 | 25 |
| **T4** CRISPR → MoA | `l4_crispr_moa` | `tasks/l4_crispr_moa.test.jsonl` | nDCG@20 | 60 |
| **T5** evidence fusion | `c1_validate` | `tasks/c1_validate.test.jsonl` | AUROC | 144 |
| **T6** binding → MoA | `l2_binding_moa` | `tasks/l2_binding_moa.test.jsonl` | nDCG@20 | 44 |
| **T7** selectivity | `l3_selectivity` | `tasks/l3_selectivity.test.jsonl` | AUROC | 35 |

## SI diagnostics (excluded from headline means)

| SI label | Code scenario | Task file | Note |
|---|---|---|---|
| **D1** repurposing | `t2_repurpose` | `tasks/t2_repurpose.test.jsonl` | Gold-limited (repoDB ↔ EHR coverage) |
| **D2** safety | `l9_safety` | `tasks/l9_safety.test.jsonl` | Gold-limited (FAERS MedDRA ↔ ICD) |

Do **not** call D1 “T2” — manuscript **T2** is target identification (`a2_target_id`).

## Legacy alias cheat-sheet

| Alias in older docs | Manuscript |
|---|---|
| A2 | T2 |
| A3 | T3 |
| C1 / `c1_validate` | T5 |
| L2 / `l2_binding_moa` | T6 |
| L3 / `l3_selectivity` | T7 |
| L4 / `l4_crispr_moa` | T4 |
| “T2 repurposing” (old catalog) | **D1** |

## Conditions (Fig 6c)

| Method (SI) | Code condition(s) |
|---|---|
| LinkD (tools-only) | `linkd_cli` (T1), `linkd` / `linkd_evidence` / layer agents |
| LLM closed-book | `closed_book` (Fig 6 lock: **gpt-5.4**) |
| ToolUniverse / OT | `tooluniverse`, `ot_genetics`, `ot_assoc` |
| Combined | `combined` |
| Orchestrator (LinkD-Agent) | `orchestrator` |

## Numeric freeze (Submission / SI)

Authoritative manuscript numbers ([`docs/FIG6_BENCHMARK_SI.md`](../docs/FIG6_BENCHMARK_SI.md),
METHODS/RESULTS):

- Orchestrator overall mean **0.734**
- T5 LinkD / Orchestrator **0.467 / 0.806**, T5 **n = 152**

On-disk regenerable summaries (`results/summary.c1*.jsonl`,
`For_Reviewer/source_data/benchmark/`) currently reflect a later regen:
**T5 AUROC 0.392 / 0.850**, **n = 144**, overall orch **0.740**.
Submission-era `summary.*.jsonl` for n=152 were **not found** under
`benchmark/results/` or `For_Reviewer/source_data/benchmark/`.

Until those inputs are restored, treat **task definitions + this ID map** as
canonical for code alignment; do **not** silently replace manuscript tables
with the 0.740 regen.

## Archived material

Redesign diagnostics (T4′/T5′/T7′) and extra figure scripts:
[`archive/`](archive/).
