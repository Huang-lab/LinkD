# Repository results and retained evidence

This file reports only values that can be read from the current repository
data or regenerated from retained benchmark summaries. It is not a substitute
for the submitted manuscript Results section.

## Application data inventory

At server startup, the current data checkout loads 12 named datasets. The
principal retained tables contain:

- 276,147 drug–target–disease association rows;
- 13,008 causal gene–disease rows;
- 1,029 cancer-gene annotations;
- 886,087 target-priority rows;
- 41,120 aggregate Mount Sinai EHR association rows;
- 693 aggregate UK Biobank association rows;
- 464,820 CRISPR drug-response correlation rows;
- 14,981 drug-selectivity rows;
- 1,068 target-binding summary rows; and
- 100 target-centric Parquet chunks indexed for on-demand access.

These are data-coverage counts, not measures of biological validity or
application accuracy.

## Figure-reproduction contracts

The reviewer validator checks the following manuscript-defining values directly
from the packaged panel tables:

- Figure 1 contains 13 methods and LinkD-Bind has rank 1 in all three displayed
  evaluation modes.
- Figure 2 contains EGFR and JAK1 radar records and docking recovery values of
  83.6%, 92.6%, and 95.3% at the displayed cutoffs.
- Figure 5 contains nine adrenergic receptors and ranks carvedilol third.
- Figure 6 contains submitted panels 6a–b only; no Figure 6c output is part of
  the manuscript-reproduction workflow.

The complete contracts and output inventory are executable in
`scripts/reviewer_data/validate_package.py`.

## Supplementary LinkD-Agent benchmark

The retained `benchmark/results/PERFORMANCE_REPORT.md` is generated from
`benchmark/results/summary.*.jsonl`. In the current retained summaries, the
seven-task means are LinkD 0.549, best closed-book LLM 0.675, equal-weight
combined 0.712, and LLM orchestrator 0.734. Metrics differ by task (C-index,
nDCG@20, or AUROC), so these averages are descriptive benchmark summaries
rather than a universal accuracy measure.

The prediction-task mean is 0.616 for LinkD and 0.438 for the strongest
closed-book LLM selected per task. The two diagnostic EHR tasks are excluded
from headline averages because of limited dataset overlap and ontology
misalignment. These results are supplementary agent evaluation and are not a
submitted manuscript figure panel.

## Interpretation limits

No repository evidence supports a general query-classification accuracy,
application success rate, fixed response-time guarantee, causal EHR
interpretation, or clinical recommendation. Earlier illustrative drug examples
and invented timing/accuracy statements have therefore been removed.
Application outputs must be checked against their source rows and independently
validated before scientific or clinical use.
