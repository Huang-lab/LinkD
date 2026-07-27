# LinkD Drug-Discovery Agent Benchmark

A reproducible, external-gold benchmark that compares LinkD **head-to-head with other
open-source agents** on **cancer** indications — LinkD's strongest use case. All gold
comes from independent public datasets (never LinkD's own tables). Methodology and
metric names follow TxAgent/CURE-Bench, BixBench, and MedAgentBench; see
[AGENT_BENCHMARK_PLAN.md](AGENT_BENCHMARK_PLAN.md) and [../METHODS.md](../METHODS.md).
The pipeline + metrics are summarised in `results/figures/fig_workflow.png`.

## Tasks (external gold)
- **T1 · drug-target binding affinity** — predict pKd for a drug-target pair, scored
  against **TDC DAVIS** experimental Kd (4,399 LinkD∩DAVIS pairs; 78-pair held-out test).
- **A2 · target identification** — rank gene targets for a disease, scored against
  **OpenTargets disease-approved drug targets** over **25 cancer indications**.

## Agents compared (A2)
- **linkd** — LinkD multi-evidence database ranker (deterministic, no LLM).
- **tooluniverse** — OpenTargets *overall* association (ToolUniverse, 2,524 tools).
- **ot_genetics** — OpenTargets *genetics-only* (genetic_association via direct GraphQL).
- **pubmed** — keyless NCBI E-utilities literature-mining agent (no install).
- **closed_book** — base LLMs (gpt-4o-mini / gpt-4o / gpt-4.1).

For T1 the deterministic **linkd_cli** (predicted-pKd lookup) is compared with the base LLMs.

## Quick start
```bash
# Build / refresh the external gold (cached; A2 needs network once, then offline):
python3 benchmark/external_data/a2_prefetch.py        # OpenTargets approved-target gold
python3 benchmark/datasets/a2_target_id.py            # -> tasks/a2_target_id.test.jsonl
python3 benchmark/datasets/t1_dti.py                  # -> tasks/t1_dti.test.jsonl (TDC DAVIS)

# A2: all five agent strategies (deterministic agents are zero-cost; LLMs need OPENAI_API_KEY):
python3 benchmark/run_benchmark.py --scenarios a2_target_id \
    --conditions linkd,tooluniverse,ot_genetics,pubmed,closed_book --models gpt-4.1 \
    --out benchmark/results --tag a2

# T1: LinkD predicted pKd vs DAVIS (deterministic, zero API cost):
python3 benchmark/run_benchmark.py --scenarios t1_dti --conditions linkd_cli \
    --out benchmark/results --tag t1

# Leaderboard + figures (incl. fig_workflow):
python3 benchmark/report/leaderboard.py
python3 benchmark/report/figures.py
python3 benchmark/report/workflow_figure.py

# Standalone smoke test (zero cost; skips gracefully without data/keys):
python3 benchmark/tests/test_benchmark_smoke.py
```

## Layout
`schema.py` (Item/Prediction + JSONL) · `datasets/` (builders → `tasks/*.jsonl`) ·
`external_data/` (TDC DAVIS, OpenTargets, PubMed, UniChem — all cached) ·
`conditions/` (agent adapters) · `scoring/` (ranking, regression) · `run_benchmark.py` ·
`report/` (leaderboard, figures, workflow_figure) · `tests/test_benchmark_smoke.py`.

Everything is key-gated and skips gracefully: with no keys, the four deterministic agents +
scoring + figures still run end-to-end at zero API cost from cached gold.
