# Later benchmark regen (n=144 T5) — not the manuscript freeze

These files are a **later regeneration** of the T5 (`c1_validate`) benchmark with **144**
triads (orchestrator mean **0.740**, T5 LinkD/Orchestrator **0.392 / 0.850**).

The **Nature submission / SI freeze** uses **152** triads and Table S5 scores
(orchestrator mean **0.734**, T5 **0.467 / 0.806**). Active reviewer copies under
`benchmark/results/` and `For_Reviewer/source_data/benchmark/` were restored to the
submission summary freeze on 2026-07-27.

Item-level predictions for the original 152 triads were not recoverable from git or local
backups; Fig 6c reproduction uses the submission **summary** JSONL aligned to
[`docs/FIG6_BENCHMARK_SI.md`](../../../docs/FIG6_BENCHMARK_SI.md) Table S5.
