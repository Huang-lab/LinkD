# LinkD Drug-Discovery Agent Benchmark

External-gold oncology agent benchmark for **Manuscript Figure 6c** and SI Tables S1–S5:
seven headline tasks (**T1–T7**) plus two gold-limited diagnostics (D1/D2).

Full ID map, legacy aliases, and numeric-freeze notes:
[TASK_CATALOG.md](TASK_CATALOG.md). End-to-end re-run: [RERUN.md](RERUN.md).
SI draft: [`docs/FIG6_BENCHMARK_SI.md`](../docs/FIG6_BENCHMARK_SI.md).

## Manuscript ↔ code (headline)

| Manuscript | Code scenario | Metric |
|---|---|---|
| T1 binding | `t1_dti` | C-Index |
| T2 target-ID | `a2_target_id` | nDCG@20 |
| T3 priority | `a3_priority` | nDCG@20 |
| T4 CRISPR→MoA | `l4_crispr_moa` | nDCG@20 |
| T5 fusion | `c1_validate` | AUROC |
| T6 MoA recall | `l2_binding_moa` | nDCG@20 |
| T7 selectivity | `l3_selectivity` | AUROC |

Fig 6c methods: LinkD · closed-book LLM (**gpt-5.4** lock) · ToolUniverse/OT · Combined · Orchestrator.

## Numeric freeze

Submission / SI scores (orchestrator mean **0.734**; T5 **0.467→0.806**, n **152**) are the
manuscript freeze in `results/summary.c1*.jsonl` and `For_Reviewer/source_data/benchmark/`.
See [TASK_CATALOG.md](TASK_CATALOG.md). A later n=144 regen is archived under
[`archive/submission_regen_144/`](archive/submission_regen_144/).

## Quick start (deterministic slice)

From the repository root:

```bash
export DATABASE_DIR="${DATABASE_DIR:-$PWD/Database}"
# If LinkD tables are missing: python3 scripts/download_data.py  # DOI 10.5281/zenodo.21615191

python3 benchmark/external_data/a2_prefetch.py
python3 benchmark/datasets/a2_target_id.py
python3 benchmark/datasets/t1_dti.py

# Zero-cost deterministic runs
python3 benchmark/run_benchmark.py --scenarios t1_dti --conditions linkd_cli \
    --out benchmark/results --tag t1
python3 benchmark/run_benchmark.py --scenarios a2_target_id \
    --conditions linkd,tooluniverse,ot_genetics,pubmed \
    --out benchmark/results --tag a2

python3 benchmark/report/leaderboard.py
python3 benchmark/report/fig6_cell.py          # Fig 6c heatmap/bars
python3 benchmark/tests/test_benchmark_smoke.py
```

Full LLM/orchestrator grid and PERFORMANCE_REPORT: [RERUN.md](RERUN.md).
Frozen reviewer copies: `For_Reviewer/source_data/benchmark/`.

## Layout

`schema.py` · `datasets/` (T1–T7 + D1/D2 builders) · `tasks/*.jsonl` ·
`external_data/` (fetchers in git; caches under `cache/`) · `conditions/` · `scoring/` ·
`run_benchmark.py` · `report/{fig6_cell,performance_report,leaderboard,audit_results}.py` ·
`archive/` (historical plans + non-headline extras).

Everything is key-gated and skips gracefully when API keys are absent.
