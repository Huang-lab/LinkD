# Changelog

## 2026-06-29 (d): Cell-spec Figure 6 benchmark panel + SI tables + draft text

- **`benchmark/report/fig6_cell.py`** → `fig6_benchmark_bars.{png,pdf}` (grouped bars, 7 tasks +
  Mean × 5 methods) and `fig6_benchmark_heatmap.{png,pdf}` (methods × tasks). Cell journal spec:
  Arial ≥6 pt, ≥0.5 pt rules, Okabe–Ito colour-blind-safe palette, 300 dpi PNG + editable Type-42
  vector PDF, 2-column (174 mm) width. Compares **LinkD / GPT-5.4 / ToolUniverse / LinkD+LLM
  (Combined) / LinkD+LLM (Orchestrator)**; LLM specified as gpt-5.4. Means: LinkD 0.549, GPT-5.4
  0.636, ToolUniverse 0.571*, Combined 0.706, **Orchestrator 0.734** (best).
- **`docs/FIG6_BENCHMARK_SI.md`** — Tables S1 (task spec), S2 (methods/models), S3 (results matrix)
  for the supporting information, plus brief draft **Results** and **Discussion** paragraphs.

## 2026-06-29 (c): LLM comparison on the aligned tasks + two infra fixes

- **Ran the full grid** (closed-book / combined / orchestrator × gpt-5.4 + claude-sonnet-4-6) on the
  three aligned tasks (capped target-balanced sets, 144/120/120, identical items per condition).
  **Honest result: these are recognition tasks the LLM wins.** Per drug–target pair, the LLM knows
  the pharmacology → closed-book **0.95–0.98** vs LinkD **0.71–0.77**. The gpt-5.4 **orchestrator is
  best/tied** on all three (0.901 / 0.985 / 0.988). So the manuscript-aligned reframe gives LinkD
  real, well-above-chance signal but does NOT flip selectivity/CRISPR/fusion into LinkD wins —
  recognition is the LLM's home turf; LinkD's unique edge stays quantitative pKd + novel interactions.
  Full numbers in `docs/WEAK_TASK_REDESIGN.md` and `docs/COMPREHENSIVE_TASK_TABLE.md`.
- **Fix 1 — request timeout.** `llm_client.py` built the OpenAI/Anthropic clients with no timeout;
  the first two background grids hung ~75 min on a stalled localhost-proxy connection (flat CPU, zero
  rows). Added `timeout=90s` + `max_retries=2` to both clients.
- **Fix 2 — score_label parser.** `closed_book._parse` grabbed the FIRST number, so a verbose
  (tool-using) model's prose ("…pKd = 7.29…") yielded `.29` → the claude orchestrator scored
  0.42–0.53 (near-random). Now takes the LAST standalone number in [0,1] (rejects decimal tails and
  list markers). Per the user's call, the claude orchestrator was not re-run; gpt-5.4 is reported.

## 2026-06-29 (b): Rebuilt the weak modules to the manuscript's own validation form

Read `docs/Submit/Manuscript_VF` and found the "weak" tasks used gold misaligned with what the
modules do. Rebuilt them (see `docs/WEAK_TASK_REDESIGN.md`); on aligned gold LinkD's weak modules
become strong (LinkD-alone deterministic AUROC; LLM/Combined/Orchestrator comparisons deferred to
API availability — conditions + maps already wired):

- **T7′ selectivity** (LinkD-Select, target-centric known-binder retrieval, Fig 5a): **0.474 → 0.727**.
  New builder `t7_sel_retrieval.py` + condition `linkd_target_aff`. Gold = OpenTargets MoA known
  drugs per target (independent of binding training); 724 pairs / 20 targets.
- **T4′ CRISPR concordance** (LinkD-Pheno, Fig 3): **0.587 → 0.736**. New builder `t4_crispr_conc.py`
  + condition `linkd_crispr_pair`. Gold = screen-annotated target vs measured non-target |AUC_corr|.
- **T5′ multi-evidence fusion** (Fig 3): **0.467 → 0.759**. New builder `t5_concordance.py` +
  condition `linkd_fusion_pair` (binding + CRISPR). **Fusion > both parts** (binding 0.727, CRISPR
  0.736, fusion 0.759) — reproduces the manuscript's multi-evidence thesis. The native
  disease-contextualized `final_score` scores pure drug–target pairs at 0.45 (needs a disease).
- **D1′ protective EHR** (LinkD-Pheno, Fig 4): curated validation `d1_protective.py` — **4/4 covered
  literature-protective pairs recovered** (propranolol/carvedilol–prostate, tretinoin–thyroid,
  azelastine–liver). A large-scale AUROC isn't viable (cancer-cohort coverage 4/20); LinkD-Pheno is
  validated by this curated table + the qualitative case studies, as the manuscript does.
- **Bugs fixed (both were tanking the CRISPR signal):** keyed on the sparse `Gene` column (84) vs the
  full `genes` column (17,029 measured); and a regex `drug_name` filter dropped the target row.
- Wired `combined.py::_LINKD`, `orchestrator.py::SCN_TOOLS`, and `run_benchmark.py` for the three new
  scenarios so the LLM-side comparison runs without further changes.

## 2026-06-29: Refined, manuscript-aligned task set + comprehensive task table

- **Re-anchored the benchmark to LinkD's described modules and re-grouped by task TYPE**
  (defined a priori — what the task tests, not who wins): **Prediction** (answer computed from
  data, not memorizable — LinkD's design target), **Mechanism/Integration**, **Knowledge**
  (documented fact — LLM home turf). Headline = **7 tasks**: T1 binding (LinkD-Bind), T2 target-ID
  (causal+clinical), T3 prioritization (TPI), T4 CRISPR→MoA, T5 multi-evidence fusion, T6 MoA
  recall, T7 selectivity (LinkD-Select).
- **New deliverable `docs/COMPREHENSIVE_TASK_TABLE.md`** — task description × LinkD signal × LLM
  comparators (gpt-5.4 / claude-sonnet-4-6 / gpt-4.1) × open-source comparators (ToolUniverse /
  OpenTargets / OT-genetics / PubMed; DeepDTA/GraphDTA cited for DTI) × example query × metric ×
  result, with the manuscript-module→task coverage map.
- **Moved the two broken EHR tasks to a gold-limited diagnostic appendix, excluded from headline
  averages** (honest, after verifying they are not fixable): **D1 repurposing** — repoDB overlaps
  LinkD's EHR cohorts on only **3/120** sampled pairs (cohort coverage, not signal quality);
  **D2 safety** — FAERS **MedDRA** adverse-event terms vs LinkD's **ICD** EHR ORs (ontology
  mismatch).
- **Investigated and ruled out "fixes" the data doesn't support** (no result-gaming): (a) selectivity
  realignment — LinkD's `Selectivity_Score` is proteome-wide while DAVIS is kinome-only (Spearman
  ρ≈0.19; ≤0.38 for any column; ρ≈0.25 even from LinkD's predicted kinome profile); (b) a
  binding-profile-recovery task — within-drug ordering ρ≈0.37, recall@20≈0.41 (LinkD's 0.819 comes
  from *cross-pair* discrimination, which T1 already measures); (c) small-molecule-scoped fusion —
  AUROC≈0.57 (OT approved-drug route yields 0 binding-covered triads).
- **Findings (refined set):** Prediction mean **LinkD 0.616 > best-LLM 0.438** (LinkD wins its
  design target); Overall **Orchestrator 0.734 > Combined 0.721 > LLM 0.680 > LinkD 0.549**, the
  orchestrator approaching the router-oracle ceiling (0.756). Regenerated
  `benchmark/results/PERFORMANCE_REPORT.md` (7 headline + 2 diagnostic) and
  `benchmark/results/figures/fig_nature.{png,pdf}` (7-task, type-coloured). Updated METHODS/RESULTS.
- **No GitHub commit** — all changes kept local for continued testing/exploration (per standing
  instruction). LLM tier = gpt-5.4 + claude-sonnet-4-6 (Gemini geo-blocked: "User location is not
  supported").

## 2026-06-26: Orchestrator — L9 prompt-tuning (failed, honest) + compositional case studies

- **(a) L9 cross-check tuning failed — and that's the finding.** Added 'distrust sparse/
  non-significant EHR, fall back to your own knowledge' to the prompt and re-ran L9: it got
  *worse* (gpt-5.4 0.239→0.149, claude 0.384→0.326). Root cause is not the prompt — L9's FAERS
  adverse-event gold is ontology-misaligned with LinkD's EHR (disease-association ORs), so making
  the agent reason *more* over the EHR amplifies the mismatch. Reverted the benchmark prompt to
  the version that produced the 0.694 grid; kept the reliability-weighing guidance only in the
  case-study harness (where it helped). L9 stands as a broken task no method fixes (LLM-alone
  least-bad at ~chance).
- **Fixed a real bug:** the `get_drug_selectivity` tool passed `--drug` to `drug-info` (which
  takes a positional arg) → it errored every call; the agent had been silently falling back to
  its own knowledge. Fixed in `orchestrator.py` + `case_studies.py`.
- **(b) Compositional case studies** (`benchmark/case_studies.py` → `results/case_studies.md`):
  free-form, multi-tool queries where the orchestrator shines. gpt-5.4 autonomously chained
  4–9 LinkD tool calls per query and genuinely cross-checked: imatinib/CML (treats empty EHR as
  *missing*, not negative), erlotinib/EGFR (**overrides** LinkD's 'Type I: Highly Selective' label
  as inconsistent with its 0.33 score + off-target panel), melanoma triage (**compares binding +
  evidence for BRAF/KIT/KDR** across 9 calls, overrides LinkD's noisy vemurafenib target list).
  This is the orchestrator's real value — compositional reasoning + LinkD-grounding + correction —
  that atomic per-task scoring can't capture.
- **Per-case figures** (`report/fig_case_studies.py` → `fig_case{1,2,3}.{png,pdf}`, Nature-style,
  data-driven from deterministic LinkD CLI fetches): panel a = the agent's autonomous tool-call
  workflow with the key value from each call + the verdict/override; panel b = the LinkD evidence
  that drove it (case 1: 6-layer multi-evidence subscores + coverage; case 2: erlotinib off-target
  binding panel showing EGFR top but close kinases → justifies the selectivity override; case 3:
  BRAF/KIT/KDR candidate comparison by pKd + final_score → why BRAF was picked). All local.

## 2026-06-26: LLM-as-orchestrator — LLM calls LinkD as a tool, cross-checks, answers

- Built a **real function-calling agent** (not blending): `agent/llm_client.py::run_tools`
  drives a native tool-use loop for OpenAI + Anthropic; `benchmark/conditions/orchestrator.py`
  exposes the LinkD CLI subcommands as **entity-bound tools** (executor injects the item's
  drug/gene/disease/icd via `cli_json`), with a cross-check system prompt; added a
  `targets-for-disease` CLI subcommand (the one missing tool). The model decides which LinkD
  tool to call, reasons over the JSON, and emits the task format.
- Ran the full 9-task grid × claude-sonnet-4-6 + gpt-5.4: **102 min, 0 errors**, tool loop
  fired on 100% of items. 4-way task-mean: **LinkD 0.522 · best-LLM 0.670 · Combined-blend
  0.690 · Orchestrator 0.694 · router-oracle 0.729.**
- **The orchestrator is the best deployable strategy** — it recovers the strong source's full
  value instead of paying the blend's dilution tax: L1 binding **0.819 = LinkD** (vs Combined
  0.79), L6 0.518 / L5 0.506 ≈ LinkD (vs blend 0.479/0.497), and **L10 0.806 beats *both***
  base sources via cross-checking. It matches the LLM on memorized-fact tasks (L2/L3/L8).
  One regression: **L9 safety −0.135** (the ICD↔MedDRA broken-ontology task — calling+trusting
  the noisy EHR tool hurt vs the LLM's memory). claude's value formatting wobbled on L1 (RMSE),
  gpt-5.4 was clean. Report + `fig_nature`/`fig_compare2` now show the 4-way + oracle. All local.

## 2026-06-26: Recent-model grid (claude-sonnet-4-6 + gpt-5.4) + SOTA tool-agents

- Wired cross-vendor models (key file `config/api_keys.env`, git-ignored). Installed `anthropic`
  + `google-generativeai`; made routing prefix-based (`gpt-*`/`claude-*`/`gemini-*`), guarded the
  OpenAI client for GPT-5 reasoning (omits `temperature`), and forced the Gemini SDK onto REST
  transport. **Gemini is geo-blocked** in this environment ("User location is not supported") —
  excluded. **claude-sonnet-4-6 and gpt-5.4 both run cleanly.**
- Ran the full 9-task grid (closed_book + combined) for both new models: **106 min, 0 errors**
  across 36 condition×model rows. Reports/figures now pick the **best LLM per task** (named) and
  add a **SOTA tool-agent** column (ToolUniverse/OpenTargets/PubMed, where applicable).
- **Result (task-mean):** LinkD **0.522** · best-LLM **0.670** · Combined **0.690** · router-oracle
  **0.729**. Stronger LLMs lifted every LLM-based column (best-LLM 0.64→0.67, Combined 0.66→0.69)
  while LinkD (deterministic) held; LinkD still wins the 3 prediction tasks (L1 binding, L5/L6
  target-ID & prioritization), newer LLMs widened their lead on memorized-fact tasks (L2 0.90,
  L3 0.91). Per task the best LLM splits across vendors: claude-sonnet-4-6 (L2/L4/L10),
  gpt-5.4 (L5/L6 combined), gpt-4.1 (L1/L3/L8). DTI ML specialists (DeepDTA/DeepPurpose) stay
  cited — torch/rdkit not easy-installable here. Figures regenerated (`fig_nature`, `fig_compare2`,
  `fig_combined`, `fig_performance`). All local.

## 2026-06-25: LinkD + LLM hybrid — 3-way comparison across all tasks

- Added a **Combined** condition (`conditions/combined.py`) that fuses LinkD + gpt-4.1 per
  task: reciprocal-rank fusion for ranking tasks, score-mean for AUROC/regression. Ran it on
  all 9 tasks for a three-way LinkD / LLM / Combined comparison (`report/{performance_report,
  fig_combined}.py`, `results/fig_combined.png`).
- **Result (task-mean of the headline metric):** LinkD 0.522 · LLM 0.640 · **Combined 0.661**
  · Router-oracle 0.707. The hybrid is the best *single* strategy on average — it carries
  LinkD's edge on prediction tasks (L1/L4/L5/L6) and the LLM's on memorized-fact tasks
  (L2/L3). Equal-weight fusion wins outright only on **L4** (CRISPR+LLM complementary, +0.02);
  elsewhere it regresses toward the middle when one side dominates.
- **Takeaway:** a **coverage-gated router** (pick the stronger source per task; oracle 0.707)
  beats blending (0.661) — the recommended deployment. LinkD already emits the gating signal
  (`coverage`/`final_score`; data-presence for binding/CRISPR). All local.
- **Publication figures** (Nature-spec: Arial, Okabe-Ito colorblind palette, Type-42 vector
  PDF, 300 dpi; LLM = OpenAI gpt-4.1 throughout):
  - `report/fig_nature.py` → `fig_nature.{png,pdf}` — **6-panel** with named tasks:
    (a) per-task bars, (b) category means, (c) overall mean±s.e.m. + router-oracle ceiling,
    (d) complementarity scatter, (e) fusion-lift vs method-disagreement, (f) tasks×methods
    metric heatmap.
  - `report/fig_compare2.py` → `fig_compare2.{png,pdf}` — compact **2-panel** (per-task +
    overall) for slides / single-result use.
  - Plus `fig_combined.png` (grouped bars) and `fig_performance.png` (diverging LinkD−LLM).

## 2026-06-25: Feature-coordinated benchmark — 9 tasks, one per LinkD layer

- Refactored the benchmark around **LinkD's data layers** (L1–L10): each task isolates one
  feature (binding, selectivity, CRISPR correlation, causal gene, clinical phase, TPI, EHR,
  fusion) against the most *independent* external gold. New tasks built + run:
  - **L2 binding→MoA** (`l2_binding_moa`) — recover a drug's ChEMBL/OT mechanism target from
    LinkD's predicted-binding ranking (UniProt-mnemonic→gene map via target_binding_stats).
  - **L3 selectivity** (`l3_selectivity`) — selective vs promiscuous from the full TDC DAVIS
    kinome matrix vs LinkD's `Selectivity_Score`.
  - **L4 CRISPR→MoA** (`l4_crispr_moa`) — recover MoA target from CRISPR drug-response
    correlation (gold = pharmacology, *not* the GDSC screen → dodges self-reference).
  - **L9 safety** (`l9_safety`) — openFDA FAERS adverse events vs LinkD EHR risk-OR.
  New: `conditions/agents_layers.py`, `external_data/openfda.py`, `report/performance_report.py`,
  `report/fig_performance.png`, `results/PERFORMANCE_REPORT.md`.
- **Result (LinkD vs best base-LLM):** LinkD wins the 3 prediction tasks — **L1 binding**
  (C-Index 0.819 vs 0.63), **L5/L6 target-ID & prioritization** (≫ LLM, ≈ OpenTargets). It
  trails LLMs on the 6 memorized-fact / mismatched tasks — **L2** (0.47 vs 0.83), **L3** (0.47
  vs 0.91), **L4** (0.59 vs 0.73; CRISPR still recovers MoA, MRR 0.82), **L8** (0.50 vs 0.75,
  coverage), **L9** (~chance, ICD↔MedDRA ontology gap, 27 matched pairs), **L10** (0.47, fusion
  conflates prominent disease gene with the drug's target).
- **Takeaway:** LinkD's value is **prediction where LLM memorization fails** (binding affinity,
  novel target ranking, CRISPR mechanism); pair it with an LLM for memorized pharmacology.
  All local (no commits); base LLMs = OpenAI tiers (Claude/Gemini wired, key-gated).

## 2026-06-18: Benchmark expanded to 5 tasks (LinkD vs LLM/agent tools)

- Grew the external-gold benchmark from 2 to **5 tasks** spanning target / phenotypic /
  integrative axes, each reporting bootstrap CIs + paired **McNemar (LinkD vs each
  comparator)**, with base LLMs across 3 OpenAI tiers (gpt-4o-mini/4o/4.1):
  - **A3 target prioritization** — LinkD's **TPI** vs its phase-evidence ranker vs
    OpenTargets vs LLMs (same 25-cancer OT gold). Both LinkD signals ≫ LLM; the
    phase-evidence ranker beats the standalone TPI (nDCG@20 0.515 vs 0.408).
    New: `datasets/a3_priority.py`, `conditions.LinkdPriorityCondition`,
    `external_data/tpi_prefetch.py` (cached per-ICD TPI from the 900 MB table).
  - **C1 target-disease validation** (AUROC, hard decoys) — LinkD's multi-evidence
    `final_score` vs OpenTargets-assoc vs LLMs. **Honest negative:** fusion is below
    chance (0.47) — gene-disease layers reward the most-evidenced disease gene over the
    drug's actual target; LLM 0.78. New: `conditions/agents_integrative.py`,
    `scoring/auroc.py` (shared AUROC/AUPRC + CI), `datasets/c1_validate.py`.
  - **T2/B4 drug repurposing** (repoDB approved/failed, AUROC) — crosswalk DrugBank→ChEMBL
    + indication→ICD via LinkD's own labels (no UMLS license). **Coverage-blocked:** LinkD
    EHR ∩ repoDB = 16 pairs → LinkD 0.50, LLM 0.74. New: `datasets/t2_repurpose.py`,
    `conditions.LinkdRweCondition`.
- New scorer routing is **format-driven** (`score_label` → AUROC) so future binary tasks
  drop in without runner changes. Per-item McNemar signal added to ranking + regression.
- New figure `fig_overview.png` (LinkD vs comparators across all 5 tasks + takeaways);
  unified `leaderboard.md` (28 rows). Run plan in `benchmark/RUN_PLAN.md`.
- **Headline:** LinkD is a strong **specialist** (binding, cancer target-ID) that should be
  **paired with an LLM** for the broad approved-drug / repurposing space its layers don't
  cover. A5 (needs `*_HUMAN`→gene resolver) and B5 (openFDA) scoped. All local (no commits).

## 2026-06-18: Benchmark refocus — cancer-only, external-gold, two tasks

- **Focused the benchmark on its thesis:** an external-gold, head-to-head agent
  comparison on **cancer** (LinkD's strongest use case). Kept only the two tasks with
  truly independent gold — **T1** (binding vs TDC DAVIS) and **A2** (target-ID vs
  OpenTargets approved targets).
- **Removed the self-referential scenarios** whose gold came from LinkD's own tables:
  **S7** (factuality/abstention/honesty), **S3** (binding), **S8** (real-world-evidence
  direction), and **T4** (PubMedQA, which only characterised the base LLMs). Deleted
  their builders, the `hallucination` scorer, the grounding/honesty/safety figures
  (`fig_honesty`, `fig_safety_panel`, `fig_grounding_lift`), and their result/task files.
- **A2 restricted to 25 cancer indications.** On cancer, the two multi-evidence agents
  dominate single-evidence ones: ToolUniverse OT-overall (recall@20 0.478, nDCG@20 0.531)
  and **LinkD** (0.439 / 0.515) ≫ OpenTargets genetics-only (0.050 — ~5% of approved-drug
  targets), PubMed literature (0.088), and base LLMs. The live OT-overall agent edges
  LinkD's static snapshot on cancer (favoured by snapshot leakage).
- **New methodology figure** `fig_workflow.png` depicting the test pipeline (external gold
  → harmonise+cache → 5 agent strategies → score) and the per-task metrics.
- Slimmed `run_benchmark.py`/`leaderboard.py`/`scoring` to the two tasks; rewrote the
  smoke test (now 12 zero-cost checks over the A2/T1 scorers, cancer-only builder, stats,
  and no-provider path). RESULTS.md/METHODS.md updated; all local (no commits).

## 2026-06-18: External-Gold Benchmark Tasks (head-to-head vs other models)

- Added **external-gold** tasks so LinkD is compared with other models on common
  public benchmarks (not LinkD's own tables). New `benchmark/external_data/`:
  UniChem CID→ChEMBL (cached), TDC loader, repoDB (pyreadr) + PubMedQA loaders.
- **T1 drug-target binding (TDC DAVIS, experimental Kd):** LinkD's predicted pKd
  reaches **Pearson 0.75 / C-Index 0.819** on a held-out test set — in the range of
  specialized DTI models (DeepDTA/GraphDTA ~0.88–0.90, cited) and far above LLMs
  (gpt-4.1 r=0.35; smaller tiers refuse to predict pKd from SMILES). 4,399
  LinkD∩DAVIS pairs via UniChem mapping.
- **T4 biomedical QA (PubMedQA):** base-LLM characterization (balanced no-context);
  LinkD's structured tools are out of scope for free-text QA.
- New scorer `regression.py` (Pearson/Spearman/RMSE/Concordance-Index), DTI + qa3
  formats, leaderboard/figures (`fig_dti.png`) + DTI/PubMedQA specialist citations.
- **T2 repurposing (repoDB):** data unblocked (6,677 approved / 4,123 failed) and
  drugs map to ChEMBL; needs a UMLS-CUI→ICD crosswalk — scoped follow-up. T3 deferred.
- **A2 target identification — head-to-head vs four agent strategies (35 diseases).** Compared
  LinkD vs a **ToolUniverse generic-tool agent** (OpenTargets overall, 2,524 tools), an
  **OpenTargets genetics-only** agent (genetic_association datatype via direct GraphQL), a
  lightweight **PubMed literature-mining agent** (keyless E-utilities, no install), and base
  LLMs, over 35 cancers + autoimmune/metabolic indications (gold = OpenTargets disease-approved
  drug targets). **Headline: multi-evidence integration dominates single-evidence strategies** —
  LinkD (nDCG@20 0.635, MRR 0.695) and OT-overall (recall@20 0.517) far exceed genetics-only
  (recall@20 0.057 — recovers ~6% of approved-drug targets) and literature (0.077); LLMs keep
  high MRR/low coverage. Three new figures (`fig_a2`, `fig_a2_scatter`, `fig_a2_per_disease`).
  New: `external_data/{opentargets,pubmed,a2_prefetch}.py`, `conditions/agents_a2.py`,
  `datasets/a2_target_id.py`, `scoring/ranking.score_target_rank`. Agent taxonomy + open-source
  agent survey in `benchmark/AGENT_BENCHMARK_PLAN.md`. Removed 5 superseded non-academic deck figures.
  Caveat: capability comparison vs clinical-validation gold, **not fully prospective**
  (static-snapshot leakage); B1 (GDSC self-referential), C2/T3, fully-prospective gold deferred.

## 2026-06-17: Multi-Scenario Drug-Discovery Benchmark (`benchmark/`)

- **Reproducible, provider-agnostic benchmark** measuring grounding lift + honesty
  of the LinkD agent vs base LLMs. Gold standards auto-derived from LinkD tables.
- Scenarios: **S3** binding (binary + ranking), **S8** real-world-evidence direction,
  **S7** factuality/abstention/hallucination (safety headline, HalluLens taxonomy).
  Conditions: LinkD tools-only, LinkD-Agent (tool-grounded LLM), base LLM closed-book.
- Scorers (classification, ranking, hallucination/honesty, grounding), entity-disjoint
  splits, statistics (bootstrap CIs, McNemar, Holm/BH), calibrated LLM-as-judge scaffold
  (gated κ>0.6 & α≥0.8; calibration set generator), and an academic leaderboard + figures.
- **Result:** tool-grounding yields honesty 1.0 across all OpenAI tiers vs 0.54–0.57
  closed-book; base models over-refuse and larger ones hallucinate. S3/S8 tools 1.0 vs
  base 0.56/0.00 (McNemar p=0.016 / 2×10⁻⁵). Methods + Results written up in
  METHODS.md / RESULTS.md with references (TxAgent/CURE-Bench, BixBench, MedAgentBench, HalluLens).

## 2026-06-15: Weighted Evidence Scoring + `linkd` Agent Skill

- **Weighted, coverage-aware multi-evidence scoring** (`agent/evidence_scoring.py`).
  Replaces the old "count found sources" heuristic. Each of seven evidence layers
  is normalized to [0,1], combined with per-layer reliability weights, and reported
  as separate **strength** (over present layers) and **coverage** (fraction of layers
  with data) scores so sparsely-covered diseases are no longer unfairly penalised.
  Two selectable aggregators: `strength_coverage` (default) and `penalize_missing`
  (Open Targets style). Weights are user-adjustable in `config/evidence_weights.yaml`
  (`LINKD_EVIDENCE_WEIGHTS` env override). Literature basis in `docs/feature_plan.md`.
- `get_comprehensive_drug_target_evidence()` now disease-aware (`disease`/`icd_code`),
  delegates to the weighted scorer, and is backward compatible (`overall_strength`
  retained, now equal to the weighted verdict). Planner summary + agent API surface
  strength/coverage/missing layers.
- **`linkd` Agent Skill** (`.claude/skills/linkd/`): a JSON CLI over the data layers
  (`binding`, `target-info`, `drug-response`, `ehr`, `causal`, `evidence`, `deep-dive`, …)
  with lazy per-command loading, plus `SKILL.md` and reference docs.
- Tests: `tests/test_evidence_scoring.py` (19, run with plain `python3`).

## 2026-06-06: Module Rename — LinkD-DTI → LinkD-Bind

- Renamed module **LinkD-DTI → LinkD-Bind** across the web server (nav bar, Home, Overview, Binding page heading, Docs) and documentation. Route (`/binding`) and API paths (`/api/binding/*`) are unchanged.

## 2026-03-26: LinkD Branding + Publication Prep

- Renamed modules: Binding → **LinkD-DTI**, Selectivity → **LinkD-Select**, EHR → **LinkD-Pheno**, AI Agent → **LinkD-Agent**
- Platform name: "LinkD: Multi-Evidence Supported Drug Discovery Platform"
- EHR volcano plot: X = Odds Ratio, Y = -log₁₀(P-value) with drug/disease hover
- EHR deduplication: removed 59% duplicates, cancer-focused default, ICD-10/ATC category panels
- Free Gemini 2.5 Flash mode for LinkD-Agent (no API key needed)
- README rewritten with Figshare + Render deployment workflow
- All documentation updated with LinkD module branding

---

## 2026-03-25: NAR Publication Readiness

### Completed
- HTML meta tags: title, description, keywords, Open Graph tags
- Contact info + institution + hosting commitment on About page
- MIT License statement added
- Data versioning: version number, load timestamp, source versions on About page and API
- Input validation: Pydantic field validators for gene symbols, ChEMBL IDs, affinity ranges
- Rate limiting: slowapi middleware (60 req/min per IP)
- Structured logging: Python logging module + global exception handler
- Comparison table vs Open Targets, DrugBank, STRING-db on Docs page
- Documentation consolidated: 10 markdown files reduced to 5

### Deployment Setup
- `render.yaml` — Render deployment config (web service + 20GB persistent disk)
- `scripts/download_data.py` — Figshare data download script
- `DATABASE_DIR` env var support in services.py — configurable data path for cloud deployment
- Deployment workflow: GitHub (code) + Figshare (data, ~16GB) + Render (hosting, $11/mo)

### Next Steps (Infrastructure — requires deployment decisions)
- [ ] **Deploy to public URL** with HTTPS (Render, AWS, or GCP)
- [ ] **Create Dockerfile** + docker-compose.yml for reproducible deployment
- [ ] **Add ARIA accessibility labels** and test with WAVE/axe
- [ ] **Create data validation test suite** (verify known drug-target pairs)
- [ ] **Add shareable result URLs** (query params, persistent IDs)
- [ ] **Add robots.txt and sitemap.xml** for SEO
- [ ] **Add privacy policy** page
- [ ] **Mount Sinai EHR citation** — add proper reference or data sharing URL
- [ ] **Performance benchmarks** — document query times and concurrent user limits
- [ ] **Browser compatibility testing** — Chrome, Firefox, Safari, Edge

---

## 2026-03-25: FastAPI + React Web Server

- Replaced Gradio with FastAPI backend + React + TypeScript + Vite frontend
- Interactive Plotly.js charts with hover tooltips, zoom, pan (replaced matplotlib)
- Paginated database explorer with server-side filtering for Binding (1,068 genes), Selectivity (14,981 drugs), EHR (41K+ associations)
- Pre-run agent examples viewable without API key
- Added Home, About, and Documentation pages
- Download buttons for analysis results (MD, PDF)
- Parquet query speed: 120s → 0.02s via pyarrow predicate pushdown + pre-built indexes
- External database links in tables (ChEMBL, UniProt, ICD-10)
- Gradio interface kept as fallback (`./start.sh gradio`)
- Consolidated 10 markdown files down to 5

## 2025-03-25: Multi-Model Support and Cleanup

- Added multi-model LLM support (OpenAI, Google Gemini, Anthropic Claude) via `llm_client.py`
- Database Explorer now works without any API key
- Added database-only example buttons in Agent tab
- Moved all Jupyter notebooks to `notebooks/` directory
- Consolidated integration logs into this CHANGELOG
- Added `.env` support for local API key management

## 2024-12-19: Drug-Target Metrics Integration

### Data Overview
- Integrated `DrugTargetMetrics/` folder with drug-target binding affinity and selectivity metrics
- 100 parquet files in `target_centric_pan/` for per-target binding data (loaded on-demand)

### File Renames
| Original | New | Description |
|----------|-----|-------------|
| `drug_centric_pan_uniprot.csv` | `drug_selectivity_metrics.csv` | Drug selectivity scores |
| `drug_centric_pan_uniprot_umap.csv` | `drug_umap_clustering.csv` | UMAP clustering and types |
| `target_stats_sorted_onco.csv` | `target_binding_stats.csv` | Target binding statistics |
| `drug_name_clin_phase.csv` | `drug_phase_mapping.csv` | Drug-to-phase mapping |

### New Query Functions
- `get_drug_selectivity_info()` -- selectivity score, entropy, drug type
- `get_target_binding_stats()` -- avg pKd, max pKd, N_hit, TPI
- `get_drug_target_binding_affinity()` -- on-demand parquet loading for specific pairs
- `get_targets_for_drug_with_affinity()` -- all targets for a drug sorted by pKd
- `get_drugs_by_selectivity_type()` -- filter by Highly Selective / Moderate / Broad-spectrum
- `get_comprehensive_drug_target_evidence()` -- multi-source evidence aggregation

### Key Metrics
- **pKd > 7**: Strong binding (Kd < 100 nM); **> 8**: Very strong; **> 9**: Extremely strong
- **Selectivity Score**: Higher = more selective (fewer targets)
- **Drug Types**: I = Highly Selective, II = Moderate poly-target, III = Broad-spectrum
- **TPI**: Target Prioritization Index (higher = higher priority)

---

## 2024-12-19: Drug Response Data Integration

### File Rename
| Original | New |
|----------|-----|
| `result_sig_merged_prism_gdsc_1112.csv` | `drug_response_crispr_correlation.csv` |

### New Functions
- `get_drug_response_associations()` -- query by drug/gene, filter by significance/source
- `get_drug_target_evidence()` -- evidence summary with correlation analysis

### Interpretation
- **Positive correlation** (AUC/IC50 > 0): Gene knockout increases drug sensitivity (resistance factor)
- **Negative correlation** (AUC/IC50 < 0): Gene may be the drug target
- **Significant** (FDR < 0.05): Strong evidence after multiple testing correction
- Data sources: PRISM (Broad Institute), GDSC

---

## 2024-12-19: EHR Data Integration

### File Renames
| Original | New |
|----------|-----|
| `good_drug_ehr_atc_1110.csv` | `mount_sinai_drug_disease.csv` |
| `ukb_drug_ehr_atc_1110.csv` | `uk_biobank_drug_disease.csv` |

### New Functions
- `get_ehr_drug_disease_associations()` -- query by drug ID/name, ICD code, disease name, source
- `assess_prevention_risk()` -- protective vs risk-increasing counts with OR stats
- `get_drug_name_from_id()`, `get_disease_name_from_icd()` -- lookup helpers

### Interpretation
- **OR < 1**: Drug may be protective; **OR > 1**: May increase risk; **OR = 1**: No association

---

## 2024-12-19: File Reorganization

### Moves
| From | To |
|------|----|
| `Database/disease_target_gene_opentarget_by_source_1027.csv` | `Target_Disease_Association/disease_target_by_source.csv` |
| `Database/disease_target_gene_opentarget_overall_1027.csv` | `Target_Disease_Association/disease_target_overall.csv` |
| `Database/gtdb_causal_gene_disease_1027.csv` | `Target_Disease_Association/causal_gene_disease.csv` |
| `Database/known_drug_sim_icd_open_target_1027.csv` | `Target_Disease_Association/drug_target_disease.csv` |
| `Database/target_priority_gene_1107.csv` | `Target_Disease_Association/target_priority.csv` |
| `Database/onco_gene_info_1027.csv` | `Database/onco_genes.csv` |

All date suffixes removed for cleaner naming.
