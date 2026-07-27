# LinkD Agent Benchmark — Task Catalog

Consolidated reference: task categories, ground truth, data, comparator agents,
existing tools, and metrics. **Currently run** = the focused cancer external-gold
benchmark (T1 + A2); the rest is the roadmap from `AGENT_BENCHMARK_PLAN.md`.

---

## 0. Master table — complete task set

Legend: ✅ run now · 🟡 data prepared (follow-up) · ⬜ roadmap gap · ✖ removed (off-thesis)

| # | Task | Axis | Ground truth (public dataset) | LinkD signal | Metrics | Key comparators | Status |
|---|---|---|---|---|---|---|---|
| **T1 / A1** | Drug–target binding affinity (DTI) | Target | TDC **DAVIS** / BindingDB / KIBA (experimental Kd) | predicted pKd | Pearson, Spearman, C-Index, RMSE | base LLMs; DeepDTA/GraphDTA *(cited)*; DrugAgent | ✅ run |
| **A2** | Target identification for a disease | Target | **OpenTargets** approved-drug targets | causal_gene_disease + drug_target_disease | recall@10/20, nDCG@20, MRR | ToolUniverse-OT, OT-genetics, PubMed, base LLMs | ✅ run (25 cancers) |
| **A3** | Target prioritization / druggability | Target | OpenTargets approved targets | **TPI** + phase-evidence | recall@k, nDCG@20, MRR | ToolUniverse-OT, OT-genetics, PubMed, LLMs | ✅ run — LinkD ≫ LLM; phase>TPI |
| A4 | Drug selectivity / polypharmacology | Target | kinome selectivity panels (DAVIS full matrix, Karaman) | selectivity score + UMAP type | selectivity-score corr; selective-vs-promiscuous acc | base LLM, profiling baselines | ⬜ partial |
| A5 | Target-based mechanism of action | Target | ChEMBL/OpenTargets MoA | binding-ranked targets | recall@k / Jaccard | ToolUniverse-ChEMBL, base LLM | 🟡 scoped — needs `*_HUMAN`→gene resolver |
| B1 | Cell-line drug response / sensitivity | Phenotypic | **GDSC / PRISM / DepMap** (IC50/AUC) | CRISPR drug-response corr | per-drug Pearson/Spearman, ranking | base LLM | ⬜ deferred (self-referential) |
| B2 | Phenotypic MoA deconvolution (CRISPR×drug) | Phenotypic | integrated CRISPR + drug screens | drug-response correlations | target-recovery recall@k | BioDiscoveryAgent | ⬜ gap |
| B3 | Real-world / EHR phenotype association | Phenotypic | external pharmaco-epi / observational (FAERS) | EHR odds ratios | sign-agreement, macro-F1 | base LLM | ⬜ gap (S8 removed) |
| **B4 / T2** | Drug repurposing from phenotype | Phenotypic | **repoDB** (approved / failed) | EHR odds ratio | AUROC, AUPRC | base LLM | ✅ run — **coverage-blocked** (EHR∩repoDB=16); LLM 0.74 |
| B5 | Adverse-event / safety phenotype | Phenotypic | **openFDA FAERS / SIDER** | EHR risk OR | AUROC, sign-agreement | base LLM | 🟡 scoped — fetch + EHR-coverage limit |
| **C1** | Multi-evidence target–disease validation | Integrative | OT approved drug + MoA target (hard decoys) | weighted `final_score` | AUROC | OpenTargets assoc, base LLM | ✅ run — **limitation** (fusion 0.47 < LLM 0.78) |
| C2 | Evidence-grounded repurposing (mechanism + RWE) | Integrative | repoDB / clinical outcomes | binding→causal-gene + EHR | AUROC, P@k | OpenClaw, base LLM | ⬜ gap |
| C3 | Triangulation / convergence (target vs phenotypic) | Integrative | clinical success | cross-source agreement | AUROC, agreement rate | base LLM | ⬜ gap |
| C4 | Honesty / abstention under integration | Integrative | fabricated / absent probes | strength + coverage + abstain | abstention, hallucination, honesty | base LLM | ✖ removed (off-thesis) |
| C5 | Multi-step planning quality (tool use) | Integrative | rubric / calibrated LLM-judge | plan → execute → synthesize | judge score (κ-gated) | other agents | ⬜ deferred (judge) |

**Status (5 tasks run).** LinkD wins where its data is dense — **T1** binding (C-Index
0.819 ≫ LLM), **A2/A3** cancer target-ID (≈ ToolUniverse, ≫ genetics/LLM). It is limited
off its data: **C1** fusion ranks prominent disease genes over the drug's actual target
(AUROC 0.47 < LLM 0.78); **T2** EHR overlaps repoDB on only 16 pairs (coverage-blocked).
Verdict: a strong **specialist** to pair with an LLM for breadth — see
`benchmark/results/figures/fig_overview.png`. Next gaps: A5/B5 (scoped), C2/C3, broader RWE.

---

## 1. Task categories (target-based + phenotypic-based + integrative)

LinkD's thesis is the *integration* of both axes — target (binding/selectivity/
priority) and phenotypic (EHR/CRISPR real-world) — so the benchmark is organized along
those axes. ✅ = run now, 🟡 = data prepared (scoped follow-up), ⬜ = roadmap gap.

### A · Target-based — *does the drug hit a good target?*
| # | Task | Ground truth / dataset | LinkD signal | Status |
|---|---|---|---|---|
| **A1 / T1** | Drug–target binding affinity (DTI) | TDC **DAVIS** experimental Kd | predicted pKd | ✅ **run** (C-Index 0.819) |
| **A2** | Target identification for a disease | **OpenTargets** disease-approved drug targets | causal_gene_disease + drug_target_disease | ✅ **run** (25 cancers) |
| A3 | Target prioritization / druggability | max clinical phase, OT tractability | TPI (target priority index) | ⬜ gap |
| A4 | Drug selectivity / polypharmacology | curated kinome / selectivity profiles | selectivity score + UMAP type | ⬜ partial (internal) |
| A5 | Target-based mechanism of action | ChEMBL MoA, DrugBank | mechanismOfAction | ⬜ gap |

### B · Phenotypic-based — *what the drug does to cells/patients*
| # | Task | Ground truth / dataset | LinkD signal | Status |
|---|---|---|---|---|
| B1 | Cell-line drug response / sensitivity | **GDSC / PRISM / DepMap** | CRISPR drug-response (AUC/IC50 corr) | ⬜ deferred (self-referential) |
| B2 | Phenotypic MoA deconvolution (CRISPR×drug) | integrated CRISPR + drug screens | drug-response correlations | ⬜ gap |
| B3 | Real-world / EHR phenotype association | pharmaco-epi outcomes | EHR odds ratios (Mt Sinai / UKB) | ⬜ gap (needs external gold) |
| **B4 / T2** | Drug repurposing from phenotype | **repoDB** (approved/failed) | EHR + clinical phase | 🟡 data unblocked — needs CUI→ICD crosswalk |
| B5 | Adverse-event / safety phenotype | FAERS / SIDER | EHR risk OR | ⬜ gap |

### C · Integrative (target + phenotypic) — *LinkD's differentiator*
| # | Task | Ground truth | LinkD signal | Status |
|---|---|---|---|---|
| C1 | Multi-evidence target–disease validation | approved vs failed targets | comprehensive weighted verdict | ⬜ gap (needs independent anchor) |
| C2 | Evidence-grounded repurposing | repoDB / clinical outcomes | binding→causal-gene + EHR | ⬜ gap |
| C3 | Triangulation / convergence | clinical success | cross-source agreement | ⬜ gap |

> **Highest-value gaps for the agent comparison:** A2 ✅ (done), B1 cell-line, C1/C2
> integrative — where LinkD's target+phenotypic fusion should beat single-axis agents.

---

## 2. Currently-run tasks — ground truth, data, metrics

### T1 · Drug–target binding affinity (target-based)
- **Question:** predict pKd for a drug–target pair.
- **Ground truth:** **TDC DAVIS** — experimental dissociation constants (Kd), an
  independent public benchmark (no LinkD data).
- **Data used:** DAVIS drugs → ChEMBL via **UniChem**, targets → LinkD genes; **4,399
  overlapping pairs** (53 drugs × 83 kinases); stratified **78-pair held-out test set**.
- **Metrics:** Pearson r · Spearman ρ · **Concordance-Index** · RMSE · binary acc (pKd≥7).
- **Result:** LinkD **C-Index 0.819** (≈ specialist DTI models 0.88–0.90) ≫ gpt-4.1 r=0.35
  (smaller LLMs refuse to estimate pKd from SMILES).

### A2 · Target identification (target-based, cancer)
- **Question:** rank candidate gene targets for a disease.
- **Ground truth:** **OpenTargets disease-approved drug targets** — the union of targets
  of drugs that reached approval for that indication (clinical validation).
- **Data used:** **25 cancer indications** (carcinomas, leukaemias/lymphomas, melanoma,
  myeloma, glioblastoma, sarcoma, GIST, …); median **18 approved-target genes** per disease;
  EFO resolved via OpenTargets; all gold cached.
- **Metrics:** recall@10 · recall@20 · **nDCG@20** · MRR.
- **Result:** multi-evidence (ToolUniverse-OT 0.478 / LinkD 0.439 recall@20) ≫
  genetics-only (0.050), literature (0.088), base LLMs (≤0.162).

---

## 3. Agents / models compared

### A2 — five strategies (deterministic agents run offline, zero API cost)
| Agent (condition) | What it represents | Evidence axis | Data source |
|---|---|---|---|
| **LinkD** (`linkd`) | LinkD multi-evidence DB ranker | target + phenotypic (fused) | LinkD tables (binding, causal genes, EHR, CRISPR, phase, TPI) |
| **ToolUniverse-agent** (`tooluniverse`) | generic tool agent — OpenTargets *overall* association | multi-evidence (OT) | OpenTargets (via ToolUniverse, 2,524 tools) |
| **OpenTargets genetics** (`ot_genetics`) | single-evidence genetics baseline | genetics only | OpenTargets `genetic_association` (direct GraphQL) |
| **PubMed literature** (`pubmed`) | single-evidence literature baseline | literature co-mention | NCBI E-utilities (keyless, no install) |
| **Base LLMs** (`closed_book`) | parametric knowledge only | none (closed-book) | gpt-4o-mini / gpt-4o / gpt-4.1 |

### T1 — LinkD vs base LLMs
| Agent (condition) | What it represents | Data source |
|---|---|---|
| **LinkD** (`linkd_cli`) | predicted-pKd lookup (deterministic) | LinkD binding table |
| **Base LLMs** (`closed_book`) | estimate pKd from SMILES | gpt-4o-mini / gpt-4o / gpt-4.1 |

**Models:** OpenAI tiers gpt-4o-mini / gpt-4o / gpt-4.1-mini / gpt-4.1. Provider-agnostic —
Claude / Gemini activate automatically when their keys are present (`config/models.yaml`).

---

## 4. Existing tools & frameworks

### Used as comparators / infrastructure (run here)
| Tool | Role in benchmark | License |
|---|---|---|
| **ToolUniverse** (mims-harvard) | wraps OpenTargets/ChEMBL/FDA into the generic-tool-agent baseline | Apache-2.0 |
| **OpenTargets Platform** | A2 gold (approved-drug targets) + overall/genetics associations (GraphQL) | open |
| **NCBI E-utilities / PubMed** | literature-mining agent (keyless co-mention ranking) | open |
| **TDC / PyTDC (DAVIS)** | T1 experimental-Kd ground truth | MIT |
| **UniChem** | ID harmonization (PubChem CID → ChEMBL) | open (EBI) |

### Surveyed open-source drug-discovery agents (cited, not all re-run)
| Agent | Repo | Axis coverage | Comparator role |
|---|---|---|---|
| **TxAgent** | mims-harvard/TxAgent | target + treatment (broad) | best *direct* comparator (heavy: GPU + fine-tuned Llama) — cited |
| **Biomni** | snap-stanford/Biomni | broad biomedical (150+ tools) | general comparator (needs ~11 GB data lake) — cited |
| **OpenClaw-Medical-Skills** | FreedomIntelligence | target + compound + repurposing | comparable evidence aggregation — license unclear |
| **ChemCrow** | ur-whitelab/chemcrow-public | chemistry/target (18 tools) | chemistry-centric, weak phenotypic — cited |
| **DrugAgent** | forks (e.g. FermiQ/drugagent) | target (DTI via ML) | A1/DTI head-to-head — candidate |
| **BioDiscoveryAgent** | snap-stanford/BioDiscoveryAgent | phenotypic (CRISPR design) | niche B2 — cited |
| **PaperQA2 / Aviary** | Future-House | literature RAG / task-gym | literature baseline / harness — cited |

> **Field gap (LinkD's opening):** almost none of these natively combine target +
> phenotypic + real-world EHR evidence. TxAgent/OpenClaw lean on OpenTargets/ChEMBL
> (target + literature); Biomni is broad but not EHR-phenotypic; ChemCrow is chemistry.

---

## 5. External benchmarks cited for context (reported by authors, not re-run)
TxAgent/ToolUniverse (arXiv 2503.10970) · CURE-Bench (arXiv 2512.11682) · MedAgentBench
(NEJM AI 2025) · BixBench (arXiv 2503.00096) · DTI specialists DeepDTA (Öztürk 2018) /
GraphDTA (Nguyen 2021) for T1 context. See `report/external/published_results.yaml`.

---

## 6. Methodology controls
- **External gold only** — answers from independent datasets, never LinkD's own tables.
- **ID harmonization** — UniChem (CID→ChEMBL), OpenTargets EFO resolution, gene mapping.
- **Caching** — all OpenTargets/PubMed/UniChem/DAVIS responses cached under
  `external_data/cache/` → offline, reproducible runs.
- **Statistics** — bootstrap 95% CIs; McNemar paired test on identical items.
- **Caveat** — A2 gold is clinical-validation (approved-drug) targets, **not a fully
  prospective time-split**; a prospective snapshot test and the repoDB T2 task are
  scoped follow-ups.

_Pipeline + metrics summarized in `results/figures/fig_workflow.png`._
