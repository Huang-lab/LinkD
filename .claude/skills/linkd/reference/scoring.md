# LinkD weighted multi-evidence scoring

Implemented in `agent/evidence_scoring.py`; configured by `config/evidence_weights.yaml`
(or `.json`). Override the config path with `LINKD_EVIDENCE_WEIGHTS` or `--weights`.

## Why
The old scorer just counted how many layers were "found", so a triad missing from
some layers was unfairly demoted. This scorer separates **how strong** the evidence
is from **how complete** it is — so sparsely-covered diseases aren't penalised.

## How a triad is scored
1. **Normalize** each layer to a sub-score in [0, 1] (or `None` if absent):
   - clinical phase `/4`; pKd `(pKd-4)/6`; CRISPR `|AUC_corr|/0.5` gated by FDR<0.05;
     EHR `|ln(OR)|/ln 2` gated by p<0.05; genetic = 0.6 floor if causal link exists;
     TPI and selectivity pass through (already 0-1).
2. **Aggregate** with per-layer weights `w_i`. Two selectable aggregators:
   - **`strength_coverage` (default)** — fair to missing data:
     - `strength = Σ_present w_i·s_i / Σ_present w_i`  (renormalized over present layers)
     - `coverage = Σ_present w_i / Σ_all w_i`
     - `final = strength · (γ + (1−γ)·coverage)`,  γ = `gamma_confidence_floor` (0.5)
   - **`penalize_missing`** — Open Targets style: missing layers contribute 0 and the
     sum is normalised over ALL layers (presence == confidence).
3. **Verdict tiers** from `final`: `strong` (≥ `strong_threshold` **and**
   `coverage ≥ min_coverage_for_strong`), else `moderate` (≥ `moderate_threshold`),
   else `weak`, else `none`. The coverage guard stops a single strong layer from
   being called "strong" on its own.

## Default weights (literature-informed, user-adjustable)
| Layer | Weight | Rationale |
|---|---|---|
| genetic_causality | 1.0 | highest reliability (genetics upweighted) |
| clinical_phase | 1.0 | real clinical outcomes |
| functional_crispr | 0.8 | experimental, mechanistic |
| real_world_ehr | 0.7 | population signal, confounded |
| predicted_binding | 0.6 | model output |
| target_priority | 0.6 | tractability / safety composite |
| drug_selectivity | 0.3 | supporting context |

Basis: Open Targets weighted harmonic sum (user-adjustable, downweights indirect
sources); *Nat Rev Genet* 2025 — weight by context/reliability and carry a separate
confidence score. See `METHODS.md` (evidence-weight section) for citations.

## Output fields (`evidence` / `deep-dive`)
`strength_score`, `coverage`, `final_score`, `verdict`, `present`, `missing`,
`aggregator`, `weights`, and per-source detail under `sources`. The legacy
`overall_strength` key mirrors `verdict` for backward compatibility.

## Tuning
Edit `config/evidence_weights.yaml` (weights, `gamma_confidence_floor`, thresholds,
`aggregator`) — no code change needed. A bad/missing config silently falls back to
the built-in defaults.
