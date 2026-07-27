# LinkD Feature Plan

Two additive features, designed to reuse the existing `agent/` query layer and the
FastAPI/React app rather than replace them.

1. **LinkD Skills** — package LinkD's capabilities as integrable Agent Skills (and an optional MCP server) so Claude (Code / Desktop / SDK) can drive LinkD natively.
2. **Weighted, coverage-aware evidence integration** — replace the current "count how many sources were found" scoring with per-layer weights and explicit handling of diseases/pairs that are missing from some layers.

---

## 0. Where things live today (grounding)

| Concern | File | Notes |
|---|---|---|
| Data access (30+ query fns) | `agent/database_query_module.py` | `DrugDiseaseTargetDB`, `load_database()` |
| Current evidence aggregation | `agent/database_query_module.py:1016` | `get_comprehensive_drug_target_evidence()` — **counts** found sources: ≥3 strong, ≥2 moderate, ≥1 weak |
| Multi-step planner | `agent/llm_planning_agent.py` | `generate_plan → execute_plan → _generate_summary` |
| Multi-model LLM | `agent/llm_client.py` | OpenAI / Gemini / Claude behind `chat()` |
| API | `interactive_web_server/backend/routers/agent.py` | `/api/agent/plan`, `/execute`, … |
| Package exports | `agent/__init__.py` | already exposes the classes we'll wrap |

Both features plug into these existing seams; no rewrite of the data layer.

---

## Feature 1 — LinkD as integrable Skills

### Goal
Let an agent call LinkD without bespoke glue: "what's the multi-evidence support for drug X on target Y in disease Z?" should resolve through a documented skill that wraps the existing query functions and the new weighted scorer (Feature 2).

### Design principle
A Skill = `SKILL.md` (name + description + instructions) + bundled resources + scripts that the model runs via Bash. We follow **progressive disclosure**: a short SKILL.md that points to a data dictionary and a thin CLI, so the model only loads detail when needed. The CLI **imports the existing `agent` package** — no logic is duplicated.

### Proposed structure (recommended: one cohesive skill + thin CLI)
```
.claude/skills/linkd/
├── SKILL.md                  # when-to-use, capability map, CLI usage examples
├── reference/
│   ├── data_dictionary.md    # 6 layers, columns, ID formats, ICD map, coverage notes
│   └── scoring.md            # weighted-evidence method + default weights (Feature 2)
└── scripts/
    └── linkd                 # argparse CLI over agent.database_query_module (JSON out)
```

### CLI surface (each subcommand → existing function, returns JSON)
| Subcommand | Wraps | Returns |
|---|---|---|
| `linkd drugs-for-target GENE` | `get_drugs_for_target_with_affinity` | ranked drugs + pKd |
| `linkd targets-for-drug DRUG` | `get_targets_for_drug_with_affinity` | ranked targets + pKd |
| `linkd binding DRUG GENE` | `get_drug_target_binding_affinity` | pKd, selectivity, rank |
| `linkd target-info GENE` | `get_target_info` + `get_target_binding_stats` | role, TPI, N_hit |
| `linkd drug-response [--drug --gene]` | `get_drug_response_associations` | CRISPR AUC/IC50 corr |
| `linkd ehr [--drug --disease --icd]` | `get_ehr_drug_disease_associations` | OR/HR/p, source split |
| `linkd causal GENE` / `disease-targets DISEASE` | causal & disease-target fns | genetic links |
| `linkd evidence DRUG GENE [--disease]` | **new weighted scorer (Feature 2)** | per-layer sub-scores, weighted strength, coverage, verdict |
| `linkd deep-dive DRUG GENE DISEASE` | orchestrates all of the above | full report (the case-study workflow) |

JSON-only output keeps it model-friendly and testable.

### Integration surface — **DECIDED: Agent Skill only**
- **Agent Skill** (`SKILL.md` + bundled CLI) — works in Claude Code, Claude Desktop, and the Agent SDK's skill loader. **This is the one surface we build.**
- *Out of scope (future):* MCP server and `/linkd-deep-dive` slash command. The CLI core is written so either can wrap it later without refactor.

### Why a skill (vs. only the existing web API)
The web app stays for humans; the skill makes the *same data* first-class for agents, with the data dictionary + scoring method inlined so the model uses the columns correctly (e.g., OR<1 = protective, pKd>7 = strong).

### Phases
1. **P1** — `linkd` CLI (argparse over existing fns) + JSON contract + smoke tests.
2. **P2** — `SKILL.md` + `reference/` docs (progressive disclosure).
3. **P3** — wire `linkd evidence` to Feature 2 scorer; add `deep-dive`.
4. **P4 (opt)** — MCP server + slash command; packaging notes in README.

### Risk / cost
- Startup: full DB load is 10–30 s. Mitigation: CLI supports `--lazy` (load only the layers a subcommand needs) and a persistent `linkd serve` mode for repeated calls.
- Data path: respects `DATABASE_DIR` env (same as the app).

---

## Feature 2 — Weighted, coverage-aware multi-evidence scoring

### Problem with the current scorer
`get_comprehensive_drug_target_evidence()` treats every layer equally and just **counts** how many were found. Consequences:
- A weak hit in 3 layers outranks a very strong hit in 2.
- Diseases/pairs absent from some layers are **silently penalized** (fewer "found" → lower tier), even when the evidence that *does* exist is strong. This is your core pain point ("not all diseases have results in LinkD").

### What the literature says (2024–2025)
- **Open Targets** computes per-source scores in [0,1] then a **user-adjustable weighted harmonic sum**; most sources weight 1.0, weaker/indirect ones are downweighted (Europe PMC/Expression Atlas/IMPC = 0.2; OTAR/Cancer Biomarkers = 0.5). It **upweights high-confidence sources and downweights literature mining** — but it does **not renormalize for missing sources**, so sparsely-covered diseases score lower by construction. ([docs](https://platform-docs.opentargets.org/associations), [community](https://community.opentargets.org/t/how-are-associations-scores-calculated-in-the-open-targets-platform/1113))
- **Genomics of drug target prioritization for complex diseases**, *Nat Rev Genet* 2025 — recommends weighting evidence **by context and reliability**, **triangulating complementary sources** to raise confidence, and **carrying a separate confidence score** through to ranking; notes the right weights are **disease-context-dependent**. ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12816132/), [Nature](https://www.nature.com/articles/s41576-025-00904-4))
- **GPS / ML-GPS** — weights can be **learned empirically** (logistic regression / gradient boosting) from known approved drug-target pairs instead of hand-picked. ([Nat Rev Genet 2025])
- **Weighted Bayesian integration** — probabilistic weighting avoids double-counting correlated sources. ([J Transl Med 2024](https://link.springer.com/article/10.1186/s12967-024-05660-3))

**Takeaway adopted here:** weight by reliability (Open Targets-style, user-adjustable), but **separate "evidence strength" from "coverage/confidence"** so missing layers reduce *confidence* rather than unfairly tanking the *score* — and leave a hook to *learn* weights later (GPS-style).

### Design

**Step A — normalize each layer to a sub-score `s_i ∈ [0,1]` (or `None` if absent):**

| Layer | Sub-score `s_i` (proposed) |
|---|---|
| Genetic causality (causal_gene_disease / Open Targets `score`) | OT `score` (already 0–1); floor 0.6 if a causal mutation is annotated |
| Clinical (ChEMBL phase) | `max_phase / 4` (Phase 4 → 1.0) |
| Target priority (TPI) | TPI (already 0–1) |
| Predicted binding (pKd) | `clamp((pKd − 4)/6, 0, 1)` → pKd 7 ≈ 0.5, pKd 10 = 1.0 |
| Functional genomics (CRISPR) | `gate(FDR) · clamp(|AUC_corr|/0.5, 0, 1)`, gate = 1 if FDR<0.05 else 0.3 |
| Real-world EHR | `gate(p) · clamp(|ln(OR)|/ln 2, 0, 1)` (OR 0.5 or 2 → 1.0) |
| Drug selectivity | `Selectivity_Score` (supporting) |

**Step B — combine with per-layer weights `w_i` (config, user-adjustable):**
- **Evidence strength** (renormalized over *present* layers — does **not** punish missing data):
  `S = Σ_{present} w_i·s_i / Σ_{present} w_i`
- **Coverage / confidence** (how much of the weighted evidence base exists):
  `C = Σ_{present} w_i / Σ_{all} w_i`
- **Final, confidence-discounted** (tunable floor γ, default 0.5):
  `S_final = S · (γ + (1−γ)·C)` → full coverage ⇒ `S_final = S`; sparse coverage gently discounts.
- **Verdict tiers:** strong / moderate / weak from `S_final` thresholds, **with a coverage guard** (e.g., "strong" requires `C ≥ 0.4`, i.e. ≥2 substantive layers).

**DECIDED: ship both aggregators behind a config flag**, default to `strength_coverage`:
- `aggregator: strength_coverage` (default) — strength renormalized over present layers + separate coverage (above).
- `aggregator: penalize_missing` — Open Targets-style weighted sum with missing = 0, no renormalization (presence = confidence).
Both return the same result shape (`strength`, `coverage`, `final`, `verdict`) so downstream code is agnostic; only the `final`/`strength` computation differs.

This directly answers "not all diseases have results": you get an honest **strength** from whatever exists, plus an explicit **coverage** number telling you how complete that picture is — instead of one conflated tier.

### Proposed default weights (literature-informed, user-adjustable)
**DECIDED: literature defaults, user-adjustable via config.** (Learned/GPS-style weights are out of scope; the config + normalization are structured so a learned weight vector can be dropped in later.)
```yaml
# config/evidence_weights.yaml
aggregator: strength_coverage   # or: penalize_missing
weights:
  genetic_causality: 1.0   # highest reliability (OT upweights genetics)
  clinical_phase:    1.0   # real clinical outcomes
  real_world_ehr:    0.7   # population signal, but confounded
  functional_crispr: 0.8   # mechanistic, experimental
  predicted_binding: 0.6   # model output → downweighted
  target_priority:   0.6   # composite tractability/safety
  drug_selectivity:  0.3   # supporting context (cf. OT literature = 0.2)
gamma_confidence_floor: 0.5
strong_threshold: 0.6
moderate_threshold: 0.35
min_coverage_for_strong: 0.4
```

### Code changes
- New module `agent/evidence_scoring.py`:
  - `normalize_layer(name, raw) -> Optional[float]`
  - `score_evidence(layers: dict, weights, cfg) -> {sub_scores, strength S, coverage C, final, verdict, present, missing}`
  - `load_weights(path|dict)` (YAML/JSON; env override).
- Refactor `get_comprehensive_drug_target_evidence()` to collect the same sources, then **delegate** to `score_evidence()` (keep old `overall_strength` key for backward compat, add `strength`, `coverage`, `weights_version`).
- `LLMPlanningAgent._generate_summary` reports strength **and** coverage, and lists which layers were missing (transparency).
- Surface in API (`routers/agent.py`) and in the `linkd evidence` CLI subcommand.

### Validation
- **Unit:** synthetic layer dicts → assert renormalization, coverage math, tier guards, missing-layer behavior.
- **Sanity:** Erlotinib/EGFR/NSCLC (full coverage) ⇒ strong, C≈1.0; Vemurafenib/BRAF (no CRISPR/EHR) ⇒ still strong on strength, C lower — demonstrates the fix on a real, known-good pair.
- **Optional (stretch):** learn weights via logistic regression on approved ChEMBL Phase-4 drug-target pairs vs. negatives (GPS-style), compare AUROC to hand-set weights.

### Phases
1. **P1** — `evidence_scoring.py` + weights config + unit tests.
2. **P2** — refactor `get_comprehensive_drug_target_evidence` to delegate (backward compatible).
3. **P3** — expose strength+coverage in planner summary, API, and CLI/skill.
4. **P4 (opt)** — per-disease-area weight overrides; learned weights.

---

## Sequencing (shared)
Feature 2 first (the scorer is the valuable core), then Feature 1 wraps it:
1. `evidence_scoring.py` + config + tests  (F2-P1/P2)
2. `linkd` CLI over existing fns + the scorer  (F1-P1)
3. `SKILL.md` + reference docs  (F1-P2/P3)
4. API/summary wiring  (F2-P3)
5. Optional: MCP server, learned weights, context-dependent weights

## Locked decisions
- **Integration surface:** Agent Skill only (MCP + slash command deferred; CLI core stays wrapper-ready).
- **Aggregation:** ship **both** `strength_coverage` (default) and `penalize_missing`, config-selectable, identical result shape.
- **Weights:** literature defaults in `config/evidence_weights.yaml`, user-adjustable; learned weights out of scope.

## Build-ready task list
**F2 — scoring core (do first)**
1. `agent/evidence_scoring.py`: `normalize_layer()`, `score_evidence(layers, cfg)` with both aggregators, `load_weights()`.
2. `config/evidence_weights.yaml` (above) + env override (`LINKD_EVIDENCE_WEIGHTS`).
3. `tests/test_evidence_scoring.py`: renormalization, coverage math, both aggregators, coverage guard, missing-layer cases.
4. Refactor `get_comprehensive_drug_target_evidence()` → delegate to `score_evidence()`; keep `overall_strength`, add `strength`/`coverage`/`final`/`aggregator`.
5. Report strength + coverage + missing layers in `LLMPlanningAgent._generate_summary`; surface in `routers/agent.py`.

**F1 — skill (wraps F2)**
6. `.claude/skills/linkd/scripts/linkd` CLI (argparse → existing fns + `evidence` + `deep-dive`), JSON out, `--lazy` load.
7. `.claude/skills/linkd/SKILL.md` + `reference/data_dictionary.md` + `reference/scoring.md`.
8. CLI smoke tests; README "Skills" section.

**Validation gate:** Erlotinib/EGFR/NSCLC ⇒ strong, C≈1.0; Vemurafenib/BRAF ⇒ strong strength, lower C (proves missing-data fix on real pairs).

## Sources
- Open Targets association scoring — https://platform-docs.opentargets.org/associations · https://community.opentargets.org/t/how-are-associations-scores-calculated-in-the-open-targets-platform/1113
- Genomics of drug target prioritization for complex diseases, *Nat Rev Genet* 2025 — https://pmc.ncbi.nlm.nih.gov/articles/PMC12816132/ · https://www.nature.com/articles/s41576-025-00904-4
- Weighted Bayesian integration (heterogeneous data), *J Transl Med* 2024 — https://link.springer.com/article/10.1186/s12967-024-05660-3
- Adaptive multi-view learning for drug repurposing, 2025 — https://pmc.ncbi.nlm.nih.gov/articles/PMC12268076/
