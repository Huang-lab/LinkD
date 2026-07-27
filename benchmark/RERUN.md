# Benchmark Rerun Guide

This is the clean path for reproducing `benchmark/results/PERFORMANCE_REPORT.md`
and the Figure 6 benchmark panel.

## Environment

```bash
cd /Users/cheng.wang/Documents/LinkD_Agent
export DATABASE_DIR=/Users/cheng.wang/Documents/LinkD_Agent/Database
python3 -m pip install -r requirements.txt
python3 -m pip install -r requirements-benchmark.txt
```

LLM-backed conditions require the corresponding key:

```bash
export OPENAI_API_KEY=...
export ANTHROPIC_API_KEY=...
export GOOGLE_API_KEY=...
```

## Build Task Files

```bash
python3 benchmark/external_data/a2_prefetch.py
python3 benchmark/external_data/tpi_prefetch.py

for t in t1_dti a2_target_id a3_priority l2_binding_moa l3_selectivity l4_crispr_moa c1_validate t2_repurpose l9_safety t4_crispr_conc t5_concordance t7_sel_retrieval; do
  python3 benchmark/datasets/$t.py
done
```

## Run Into A Clean Result Directory

Before a manuscript-quality rerun, archive old summaries or write to a fresh
directory and copy only the intended `summary.*.jsonl` / `predictions.*.jsonl`
files into `benchmark/results`.

```bash
mkdir -p benchmark/results_rerun

python3 benchmark/run_benchmark.py --scenarios t1_dti --conditions linkd_cli,closed_book --models gpt-4o-mini,gpt-4o,gpt-4.1,gpt-5.4 --out benchmark/results_rerun --tag t1
python3 benchmark/run_benchmark.py --scenarios a2_target_id --conditions linkd,tooluniverse,ot_genetics,pubmed,closed_book --models gpt-4o-mini,gpt-4o,gpt-4.1,gpt-5.4,claude-sonnet-4-6 --out benchmark/results_rerun --tag a2
python3 benchmark/run_benchmark.py --scenarios a3_priority --conditions linkd,linkd_tpi,tooluniverse,ot_genetics,pubmed,closed_book --models gpt-4o-mini,gpt-4o,gpt-4.1,gpt-5.4,claude-sonnet-4-6 --out benchmark/results_rerun --tag a3

SCNS=t1_dti,l2_binding_moa,l3_selectivity,l4_crispr_moa,a2_target_id,a3_priority,t2_repurpose,l9_safety,c1_validate
python3 benchmark/run_benchmark.py --scenarios $SCNS --conditions closed_book,combined --models gpt-4.1,gpt-5.4,claude-sonnet-4-6 --out benchmark/results_rerun --tag recent
python3 benchmark/run_benchmark.py --scenarios $SCNS --conditions orchestrator --models gpt-5.4,claude-sonnet-4-6 --out benchmark/results_rerun --tag orch
```

Aligned manuscript-module diagnostics:

```bash
python3 benchmark/run_benchmark.py --scenarios t7_sel_retrieval,t5_concordance,t4_crispr_conc --conditions linkd_target_aff,linkd_fusion_pair,linkd_crispr_pair --out benchmark/results_rerun --tag aligned_linkd
python3 benchmark/run_benchmark.py --scenarios t7_sel_retrieval,t5_concordance,t4_crispr_conc --conditions closed_book,combined,orchestrator --models gpt-5.4,claude-sonnet-4-6 --out benchmark/results_rerun --tag aligned_llm
```

## Audit And Regenerate

```bash
python3 benchmark/report/audit_results.py --results benchmark/results_rerun --strict

# After copying the intended rerun files into benchmark/results:
python3 benchmark/report/performance_report.py
python3 benchmark/report/leaderboard.py
python3 benchmark/report/fig_nature.py
python3 benchmark/report/fig6_cell.py
python3 benchmark/case_studies.py
```

## No-Cost Smoke Checks

```bash
python3 benchmark/tests/test_benchmark_smoke.py
python3 benchmark/run_benchmark.py --scenarios t1_dti --conditions linkd_cli --quick --out /tmp/linkd_agent_audit_results --tag audit
```

