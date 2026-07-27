# Benchmark Rerun Guide

Reproduce `benchmark/results/PERFORMANCE_REPORT.md` and Figure 6c
(`report/fig6_cell.py`) for the manuscript **T1–T7** suite.
Task ID map and numeric-freeze notes: [TASK_CATALOG.md](TASK_CATALOG.md).

## Environment

```bash
# From the repository root (directory that contains benchmark/ and Database/)
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
export DATABASE_DIR="${DATABASE_DIR:-$PWD/Database}"
python3 -m pip install -r requirements.txt
python3 -m pip install -r requirements-benchmark.txt
```

LinkD tables via Zenodo if missing:

```bash
python3 scripts/download_data.py   # DOI 10.5281/zenodo.21615191; respects DATABASE_DIR
```

LLM-backed conditions:

```bash
export OPENAI_API_KEY=...          # gpt-5.4 = Fig 6c lock
export ANTHROPIC_API_KEY=...       # claude-sonnet-4-6 secondary tier
export GOOGLE_API_KEY=...          # optional; Gemini excluded from SI
```

## Build task files (T1–T7 + D1/D2)

Fetcher modules: `benchmark/external_data/*.py` (tracked).
Caches: `benchmark/external_data/cache/` (gitignored).

```bash
python3 benchmark/external_data/a2_prefetch.py
python3 benchmark/external_data/tpi_prefetch.py

for t in t1_dti a2_target_id a3_priority l2_binding_moa l3_selectivity l4_crispr_moa c1_validate t2_repurpose l9_safety; do
  python3 benchmark/datasets/$t.py
done
```

## Run into a clean result directory

Archive old summaries or write to a fresh directory, then copy only intended
`summary.*.jsonl` / `predictions.*.jsonl` into `benchmark/results`.

**Headline tags** (Fig 6c / SI): `t1`, `a2`, `a3`, `l2`, `l3`, `l4`, `c1` /
`c1_llm` / `c1_orch`, `combined`, `orch` / `orch_l1`, `recent`, plus diagnostics
`t2`, `l9`.

**Non-headline** (ignore for Fig 6c): `aligned_*`, `rT*`, `orch_l9b`, `recent1`,
`paired.*`.

```bash
mkdir -p benchmark/results_rerun

python3 benchmark/run_benchmark.py --scenarios t1_dti --conditions linkd_cli,closed_book --models gpt-4o-mini,gpt-4o,gpt-4.1,gpt-5.4 --out benchmark/results_rerun --tag t1
python3 benchmark/run_benchmark.py --scenarios a2_target_id --conditions linkd,tooluniverse,ot_genetics,pubmed,closed_book --models gpt-4o-mini,gpt-4o,gpt-4.1,gpt-5.4,claude-sonnet-4-6 --out benchmark/results_rerun --tag a2
python3 benchmark/run_benchmark.py --scenarios a3_priority --conditions linkd,linkd_tpi,tooluniverse,ot_genetics,pubmed,closed_book --models gpt-4o-mini,gpt-4o,gpt-4.1,gpt-5.4,claude-sonnet-4-6 --out benchmark/results_rerun --tag a3

SCNS=t1_dti,l2_binding_moa,l3_selectivity,l4_crispr_moa,a2_target_id,a3_priority,t2_repurpose,l9_safety,c1_validate
python3 benchmark/run_benchmark.py --scenarios $SCNS --conditions closed_book,combined --models gpt-4.1,gpt-5.4,claude-sonnet-4-6 --out benchmark/results_rerun --tag recent
python3 benchmark/run_benchmark.py --scenarios $SCNS --conditions orchestrator --models gpt-5.4,claude-sonnet-4-6 --out benchmark/results_rerun --tag orch
```

## Audit and regenerate

```bash
python3 benchmark/report/audit_results.py --results benchmark/results_rerun --strict

# After copying intended rerun files into benchmark/results:
python3 benchmark/report/performance_report.py
python3 benchmark/report/leaderboard.py
python3 benchmark/report/fig6_cell.py
```

## Numeric freeze vs current regen

Manuscript / SI (`docs/FIG6_BENCHMARK_SI.md`): orchestrator mean **0.734**,
T5 **0.467 / 0.806**, n **152**.

On-disk `summary.c1*.jsonl` (and For_Reviewer copies) are a later regen:
T5 **0.392 / 0.850**, n **144**, orch mean **0.740**. Submission-era n=152
summaries were not found in this tree. Do not treat auto-regen as the paper
freeze until restored; Fig 6c for submission should match Submission numbers.

## No-cost smoke checks

```bash
python3 benchmark/tests/test_benchmark_smoke.py
python3 benchmark/run_benchmark.py --scenarios t1_dti --conditions linkd_cli --quick --out /tmp/linkd_agent_audit_results --tag audit
```

Reviewer path without re-running the grid:
`For_Reviewer/source_data/benchmark/` (see [`docs/FOR_REVIEWER.md`](../docs/FOR_REVIEWER.md)).

Historical redesign tasks / extra figures: [`archive/`](archive/).
