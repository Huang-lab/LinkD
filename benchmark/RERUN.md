# Benchmark Rerun Guide

Reproduce `benchmark/results/PERFORMANCE_REPORT.md` and the supplementary
benchmark visualization (`report/agent_benchmark.py`) for the **T1–T7** suite.
This evaluation is not a submitted Figure 6c panel.
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
python3 scripts/download_data.py   # resolves https://doi.org/10.5281/zenodo.19241151
```

LLM-backed conditions:

```bash
export OPENAI_API_KEY=...          # gpt-5.4 = retained primary run
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

**Headline tags:** `t1`, `a2`, `a3`, `l2`, `l3`, `l4`, `c1` /
`c1_llm` / `c1_orch`, `combined`, `orch` / `orch_l1`, `recent`, plus diagnostics
`t2`, `l9`.

The report generator selects eligible retained rows by scenario, condition, and
metric rather than by filename. Keep a rerun in a separate directory until its
task inventory has been audited; do not combine partial historical runs.

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
python3 benchmark/report/agent_benchmark.py
```

## Retained run

Treat the checked-in JSONL summaries and generated performance report as one
retained supplementary run. Regenerate the report after replacing any summary
file; do not mix values from older runs.

## No-cost smoke checks

```bash
python3 benchmark/tests/test_benchmark_smoke.py
python3 benchmark/run_benchmark.py --scenarios t1_dti --conditions linkd_cli --quick --out /tmp/linkd_agent_audit_results --tag audit
```

The manuscript reviewer workflow is documented separately in
[`docs/FOR_REVIEWER.md`](../docs/FOR_REVIEWER.md).
