# LinkD-Agent supplementary benchmark

This folder contains a supplementary external-gold oncology evaluation of
LinkD-Agent: seven headline tasks (T1–T7) and two coverage/ontology
diagnostics. It is not a submitted Figure 6c panel and is separate from the
`For_Reviewer` manuscript-figure workflow.

The headline tasks cover binding prediction, disease-target identification,
target prioritization, CRISPR-to-mechanism ranking, multi-evidence validation,
mechanism-target recall, and selectivity classification. Definitions, gold
standards, metrics, and legacy IDs are recorded in
[TASK_CATALOG.md](TASK_CATALOG.md).

## Retained results

The checked-in report is regenerated from `results/summary.*.jsonl`. Current
retained seven-task means are LinkD **0.549**, best closed-book LLM **0.675**,
Combined **0.712**, and Orchestrator **0.734**. See
[PERFORMANCE_REPORT.md](results/PERFORMANCE_REPORT.md). Metrics differ by task,
so the mean is a descriptive benchmark summary, not application-wide accuracy.

The retained LLM identifier for the primary run is `gpt-5.4`. LLM outputs are
provider- and date-dependent and should not be interpreted as deterministic.

## Deterministic smoke run

From the repository root:

```bash
export DATABASE_DIR="${DATABASE_DIR:-$PWD/Database}"
python3 scripts/download_data.py  # resolves https://doi.org/10.5281/zenodo.19241151

python3 benchmark/datasets/t1_dti.py
python3 benchmark/run_benchmark.py --scenarios t1_dti --conditions linkd_cli \
  --out benchmark/results_rerun --tag t1
python3 benchmark/tests/test_benchmark_smoke.py
```

For the complete retained grid and report commands, see [RERUN.md](RERUN.md).
External caches and API logs are intentionally ignored; frozen task fixtures,
the prediction evidence required for the retained run, and summary JSONL files
remain versioned.

## Layout

- `tasks/`: frozen task fixtures.
- `datasets/`: deterministic fixture builders.
- `conditions/`, `scoring/`, `run_benchmark.py`: evaluation harness.
- `external_data/`: fetchers; downloaded caches are not versioned.
- `results/`: retained predictions, summaries, leaderboard, and report.
- `report/`: report, audit, and supplementary visualization generators.
