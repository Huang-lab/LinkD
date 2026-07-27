---
name: linkd
description: Query the LinkD multi-evidence drug-discovery database and score drug-target-disease associations. Use when the user asks about drug-target binding affinity (pKd), drug selectivity, gene/target priority, CRISPR drug-response, EHR (real-world) drug-disease associations, causal gene-disease links, clinical trial phase, drug repurposing, target prioritization, or wants a weighted multi-evidence verdict for a drug-target(-disease) triad (e.g. "how strong is the evidence that erlotinib targets EGFR in lung cancer?").
---

# LinkD data CLI

LinkD integrates six evidence layers for drug discovery. This skill exposes them
through one JSON CLI, `scripts/linkd`, which wraps the project's `agent/` query
layer and loads only the data each command needs (fast despite ~16 GB total).

## Running

```bash
python3 .claude/skills/linkd/scripts/linkd <subcommand> [args]   # or ./scripts/linkd
```

Every command prints a JSON object. Data lives under the repo by default; set
`DATABASE_DIR` to the `Database` folder to point elsewhere (matches the web app).
Identifiers: drugs are ChEMBL IDs (e.g. `CHEMBL553`); targets are gene symbols
(e.g. `EGFR`); diseases are names or ICD-10 codes (e.g. `C34`).

## Commands

| Command | Purpose |
|---|---|
| `binding DRUG GENE` | predicted pKd + selectivity + rank for a pair |
| `drugs-for-target GENE [--limit]` | top drugs binding a gene |
| `targets-for-drug DRUG [--limit] [--min-affinity]` | top targets of a drug |
| `target-info GENE` | oncogene role, Target Priority Index (TPI), binding stats |
| `drug-info DRUG [--name]` | selectivity score + type |
| `drug-response [--drug] [--gene] [--sig]` | CRISPR AUC/IC50 correlations |
| `ehr [--drug] [--disease] [--icd]` | real-world odds ratios + p-values |
| `causal GENE [--disease]` | causal gene-disease links |
| **`evidence DRUG GENE [--disease] [--icd] [--drug-name]`** | **weighted multi-evidence score** |
| **`deep-dive DRUG GENE [--disease] [--icd] [--drug-name]`** | **full report for a triad** |
| `config` | print the resolved scoring weights/config |

`evidence` and `deep-dive` accept `--aggregator {strength_coverage,penalize_missing}`
and `--weights PATH` to override scoring.

## Typical workflow

For "how strong is the evidence that DRUG works on GENE in DISEASE?":
```bash
./scripts/linkd evidence CHEMBL553 EGFR --disease "lung cancer" --icd C34 --drug-name Erlotinib
```
Read `verdict`, `strength_score`, `coverage`, and `missing`. **Interpretation matters:**

- **strength_score** (0-1): how strong the evidence that *exists* is.
- **coverage** (0-1): what fraction of the weighted evidence layers had data for
  this triad. **Low coverage = missing layers, NOT weak evidence.** Report
  `missing` layers as gaps to fill, not negative findings.
- **final_score** = strength gently discounted by coverage; **verdict** is the tier.

For broader exploration (drug repurposing, target prioritization), start with
`drugs-for-target` / `ehr --disease` / `causal`, then run `evidence` on candidates.

## More detail
- `reference/data_dictionary.md` — the six layers, key columns, ID formats, value interpretation.
- `reference/scoring.md` — the weighting method, default weights, and how missing data is handled.
