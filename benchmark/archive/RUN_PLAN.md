# LinkD Benchmark — Run Plan (LinkD vs other LLM/agent tools)

Goal: one comparable metrics row per task — **LinkD vs the same comparator roster** —
written to `results/leaderboard.md` + a figure, with bootstrap CIs and paired McNemar
(LinkD vs each comparator). External gold only; cancer-leaning where it matters.
Scope (locked): **everything runnable** — A-axis + B4/T2 + C1/C2 + attempt B3/B5.
LLM comparators (locked): **gpt-4o-mini / gpt-4o / gpt-4.1** (OpenAI key set).

## Comparator roster
LinkD (deterministic DB) · ToolUniverse-agent (OpenTargets) · OpenTargets genetics-only ·
PubMed literature agent · base LLMs ×3 tiers. Specialists (DeepDTA/GraphDTA, …) cited.
All deterministic agents run offline from cache → zero API cost; LLM spend bounded by `--quick`.

## Phase 0 — Harden T1 + A2 (done-tasks)  ·  ~free
- Fold bootstrap 95% CIs + paired McNemar (LinkD vs each agent) into the summary rows.
- Re-run the full A2 5-agent grid (3 LLM tiers) + T1; regenerate leaderboard/figures.

## Phase 1 — A-axis (target), cached OpenTargets/ChEMBL gold  ·  $ small
- **A5 Target MoA** — gold = ChEMBL/OpenTargets mechanism-of-action targets for a drug
  (`drug_targets(chembl)`). LinkD = `get_targets_for_drug_with_affinity` / mechanismOfAction.
  Agents: ToolUniverse-MoA, base LLMs. Metric = exact-match / Jaccard target recovery.
- **A3 Target prioritization** — gold = OpenTargets *clinical maturity*: targets with an
  approved/late-phase drug for the disease (`known_drug_targets` + maxClinicalStage). LinkD =
  **TPI** (target_priority score). Agents: OT-overall, base LLMs. Metric = AUROC(advanced-vs-not),
  Spearman(TPI vs phase), P@k. Cancer disease set reused from A2.

## Phase 2 — B4 / T2 Drug repurposing (phenotypic)  ·  $ small, plumbing
- Gold = **repoDB** approved (+) / failed (−) drug-disease pairs.
- Crosswalk (the missing piece): repoDB disease *name* → LinkD `subject_label`/ICD via fuzzy
  match (reuses LinkD's own disease vocab; avoids a UMLS license); drug DrugBank → ChEMBL
  (`drugbank_to_chembl`) → LinkD drugId.
- LinkD signal = EHR odds ratio (protective) + clinical phase + binding→causal-gene path.
- Agents: base LLMs ("is drug X indicated for disease Y?"), ToolUniverse. Metric = AUROC/AUPRC/P@k.
- First task fusing **target + phenotypic** — the differentiator.

## Phase 3 — C1 / C2 Integrative (fusion advantage)  ·  $ small
- **C1** target–disease validation: independent approved/failed *target* anchor (phase-4 +
  causal-gene positives vs low-phase non-causal negatives). LinkD = weighted `final_score`
  (`get_comprehensive_drug_target_evidence`). AUROC of final_score. Agents: OT-overall, base LLM.
- **C2** evidence-grounded repurposing: LinkD fused score as the repoDB ranker (Phase-2 gold).

## Phase 4 — B3 / B5 RWE & safety (attempt; new data)  ·  $ + network risk
- **B5 safety phenotype** — gold = **openFDA/FAERS** disproportionality (keyless API) or SIDER:
  does drug X have an adverse signal for condition Y? LinkD = EHR risk OR (logit_or>1, p<0.05).
  Metric = AUROC, sign-agreement. Agents: base LLMs.
- **B3 RWE direction** — external pharmaco-epi via openFDA where mappable; else documented as
  blocked. (B1 cell-line stays deferred — LinkD's CRISPR layer *is* GDSC/PRISM.)

## Cross-cutting
- Each task: builder → `tasks/*.jsonl` (cached gold) → conditions → scorer → `summary.*.jsonl`.
- `aggregate.py` adds CIs + McNemar; `leaderboard.py`/`figures.py` grow one block/panel per task.
- `run_benchmark.py ALL_SCENARIOS` extended; smoke test extended per task.
- Status tracked in `TASK_CATALOG.md` §0 master table.

## Reproduce (full grid)
```bash
# deterministic gold + agents (zero cost):
for t in a5_moa a3_priority t2_repurpose c1_validate; do python3 benchmark/datasets/$t.py; done
python3 benchmark/run_benchmark.py --scenarios a2_target_id,a5_moa,a3_priority,t2_repurpose,c1_validate \
    --conditions linkd,tooluniverse,ot_genetics,pubmed,closed_book \
    --models gpt-4o-mini,gpt-4o,gpt-4.1 --out benchmark/results --tag full
python3 benchmark/report/leaderboard.py && python3 benchmark/report/figures.py
```
