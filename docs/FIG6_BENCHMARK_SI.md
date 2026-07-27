# LinkD-Agent supplementary benchmark

The agent benchmark is a supplementary software evaluation and is not a
submitted Figure 6c panel. Submitted Figure 6 contains panels 6a–b only.

Seven headline tasks evaluate binding prediction, disease-target
identification, target prioritization, CRISPR-to-mechanism ranking,
multi-evidence validation, mechanism-target recall, and selectivity
classification. Two additional EHR diagnostics are excluded from headline
means because of limited gold-standard overlap and ontology mismatch.

The authoritative task definitions, sample counts, conditions, and metrics are
in [`benchmark/TASK_CATALOG.md`](../benchmark/TASK_CATALOG.md). The retained
numeric results and limitations are generated from the checked-in summaries in
[`benchmark/results/PERFORMANCE_REPORT.md`](../benchmark/results/PERFORMANCE_REPORT.md).
The primary retained OpenAI model identifier is `gpt-5.4`; raw benchmark
records place execution between 26 June and 1 July 2026.

Because primary metrics differ across tasks, cross-task means are descriptive.
They are not estimates of general LinkD accuracy, clinical validity, or causal
performance. LLM-backed results are model-, provider-, and date-dependent.
