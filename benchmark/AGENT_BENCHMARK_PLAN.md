# Benchmarking LinkD against other drug-discovery agents

Goal: compare LinkD with other **open-source agents** on drug-discovery tasks that
span **target-based** and **phenotypic-based** approaches. LinkD's thesis is the
*integration* of both axes (target: binding/selectivity/priority; phenotypic:
EHR/CRISPR/real-world), so the benchmark must cover both — and especially their
combination, where single-axis agents are weak.

Local exploration only (no GitHub commits).

---

## 1. Task categories

### A. Target-based — *what/whether the drug hits a target, and is the target good*
| # | Task | Gold / public dataset | LinkD signal | Our status |
|---|---|---|---|---|
| A1 | Drug–target binding affinity (DTI) | TDC **DAVIS/BindingDB/KIBA** (experimental Kd) | predicted pKd | ✅ **T1 done** (C-Index 0.819) |
| A2 | Target identification for a disease | **Open Targets**, causal genes, approved targets | causal_gene_disease, drug_target_disease | ✅ **A2 done** (25 cancers) |
| A3 | Target prioritization / druggability | max clinical phase reached, OT tractability | **TPI** (target priority index) | gap |
| A4 | Drug selectivity / polypharmacology | curated kinome / selectivity profiles | selectivity score + UMAP type | partial (internal) |
| A5 | Target-based mechanism of action | ChEMBL MoA, DrugBank | mechanismOfAction | partial (S7 role/MoA) |

### B. Phenotypic-based — *what the drug does to cells/patients, target-agnostic*
| # | Task | Gold / public dataset | LinkD signal | Our status |
|---|---|---|---|---|
| B1 | Cell-line drug response / sensitivity | **GDSC / PRISM / DepMap** | CRISPR drug-response (AUC/IC50 corr) | gap |
| B2 | Phenotypic MoA deconvolution (CRISPR×drug) | integrated CRISPR + drug screens | drug-response correlations | gap |
| B3 | Real-world / EHR phenotype association | pharmaco-epi, FAERS, repoDB outcomes | EHR odds ratios (Mt Sinai / UKB) | ⬜ gap (S8 removed — self-referential; needs external gold) |
| B4 | Drug repurposing from phenotype | **repoDB** (approved/failed) | EHR + clinical | 🟡 T2 (data unblocked, needs CUI→ICD) |
| B5 | Adverse-event / safety phenotype | **FAERS / SIDER** | EHR risk OR | gap |

### C. Integrative (target + phenotypic) — *LinkD's differentiator*
| # | Task | Gold | LinkD signal | Our status |
|---|---|---|---|---|
| C1 | Multi-evidence target–disease validation | approved vs failed targets | comprehensive weighted verdict | partial (internal) |
| C2 | Evidence-grounded repurposing (mechanism + real-world) | repoDB / clinical outcomes | binding-to-causal-gene + EHR | gap |
| C3 | Triangulation / convergence (do target & phenotypic agree?) | clinical success | cross-source agreement | gap |
| C4 | Honesty / abstention under integration | fabricated/absent probes | strength + coverage + abstain | ⬜ removed (S7 — self-referential, off-thesis) |
| C5 | Multi-step planning quality (tool use across both axes) | rubric / calibrated LLM-judge | plan → execute → synthesize | gap (judge deferred) |

**Coverage now:** A1 ✅ (T1), A2 ✅ (cancer), B4 🟡 (T2 in progress), A4/A5 partial.
Removed as self-referential/off-thesis: S3 (binding), S7 (honesty), S8 (RWE), T4 (QA).
**Highest-value gaps for an agent comparison:** A2 target-ID, B1 cell-line response, C1/C2 integrative — these are where LinkD's target+phenotypic fusion should beat single-axis agents.

---

## 2. Open-source agents to benchmark against (verified)

| Agent | Repo | License | ★ | Axis coverage | Runnable as comparator? |
|---|---|---|---|---|---|
| **TxAgent** | mims-harvard/TxAgent | MIT | 634 | target + treatment (broad, OpenTargets/FDA/Monarch) | Yes, but heavy: fine-tuned Llama-3.1-8B + GPU + ToolUniverse. Best *direct* comparator. |
| **ToolUniverse** | mims-harvard/ToolUniverse | Apache-2.0 | 1.5k | 211 tools (ChEMBL, OpenTargets, FDA…) | **Yes, easiest** — wrap any base LLM into a "generic tool agent" baseline on the same public data. |
| **Biomni** | snap-stanford/Biomni | Apache-2.0 | 3.2k | broad biomedical (150+ tools, DB+lit+analysis) | Yes (pip + API keys + ~11 GB data lake). Strong general comparator. |
| **OpenClaw-Medical-Skills** | FreedomIntelligence/OpenClaw-Medical-Skills | none stated | 2.7k | target + compound + disease repurposing (ChEMBL/OpenTargets/CT.gov) | Yes (skills lib). Directly comparable to LinkD evidence aggregation; **license unclear**. |
| **ChemCrow** | ur-whitelab/chemcrow-public | MIT | 927 | chemistry/target (18 tools) | Partial — chemistry-centric, weak phenotypic; stale (2024-12). |
| **DrugAgent** | paper + forks (e.g. FermiQ/drugagent) | varies | — | target (DTI via ML programming) | Maybe — for A1/DTI head-to-head. |
| **BioDiscoveryAgent** | snap-stanford/BioDiscoveryAgent | MIT | 110 | phenotypic (CRISPR perturbation design) | Niche — B2 / experimental target-ID. |
| **PaperQA2** | Future-House/paper-qa | Apache-2.0 | 8.7k | literature RAG | Literature-grounding baseline (QA). |
| **Aviary** | Future-House/aviary | Apache-2.0 | 272 | agent task-gym framework | Could host our tasks for other agents. |

**Key gap in the field (LinkD's opening):** almost none of these natively combine
**target + phenotypic + real-world EHR** evidence. TxAgent/OpenClaw lean on
OpenTargets/ChEMBL (target + literature); Biomni is broad but not phenotypic-EHR
specialized; ChemCrow is chemistry. So LinkD should differentiate on **B (EHR/CRISPR
phenotypic)** and **C (integration)** tasks.

---

## 3. Recommended comparator strategy
1. **Primary runnable baseline — "generic tool agent":** wrap a base LLM (our OpenAI
   tiers) with **ToolUniverse** (Apache-2.0, pip) so it has OpenTargets/ChEMBL/FDA
   tools — the *same public sources* other agents use. LinkD-Agent vs this isolates
   LinkD's added value (EHR/CRISPR phenotypic + integrated scoring) from "any tools."
2. **Cite reported numbers** for TxAgent/Biomni where task formats overlap (per prior
   decision); optionally run **Biomni** on a small slice if the data lake installs.
3. **Tasks first:** add A2 (target-ID), B1 (cell-line response, DepMap/GDSC), and
   C1/C2 (integrative) so the comparison exercises both axes and their fusion.

## 4. Status & feasibility findings (this session)

**Built & verified**
- `benchmark/external_data/opentargets.py` — cached OpenTargets client (retries handle
  flaky sandbox SSL). Produces correct ranked targets: melanoma → BRAF/CDKN2A/NRAS;
  lung → EGFR/KRAS/ALK; breast → BRCA1/2/PALB2/PIK3CA. This **is** the ToolUniverse-agent
  comparator's answer source.
- ToolUniverse: installs, 2,524 tools (OpenTargets/ChEMBL/FDA), `tu.run({"name","arguments"})` works.

**Blockers hit (honest)**
- **Prospective / temporal gold** (the chosen A2 gold): needs per-target drug
  *approval-year* data — not cleanly exposed by the OpenTargets tools tried
  (`associated_targets` returns only an overall score; `associated_drugs` needs extra
  parsing and may lack years). Deeper issue: LinkD is a **static 2024 snapshot** and the
  ToolUniverse-agent queries **live** OpenTargets, so neither can be made blind to
  post-cutoff approvals — a *true* prospective test needs historical snapshots
  (the "time-capsule" limitation). A *recent-target-recovery* stratum is the feasible
  approximation, with the leakage caveat stated.
- **B1 cell-line response:** LinkD's CRISPR data **is** PRISM/GDSC → using GDSC/DepMap as
  gold is self-referential for LinkD (fine for other agents, trivial for LinkD).
- **T2 repoDB:** data unblocked, drugs map, but needs a UMLS-CUI→ICD crosswalk; overlap
  is cancer-skewed/imbalanced.
- **Live external APIs** (UniChem, OpenTargets, ChEMBL) are intermittently SSL-flaky here
  → must cache (done for UniChem + OpenTargets).

**Feasible next step (recommended):** A2 as an *agent capability* comparison —
LinkD-Agent vs ToolUniverse-agent vs base-LLM ranking targets for a disease, gold =
**clinically-validated (approved-drug) targets**, ranking metrics (Recall@k, nDCG, MRR),
with an approximate recency stratum (not fully prospective; caveat noted). This is the
core LinkD-vs-other-agents result and is buildable on the cached foundation.

## 5. Open decisions for the user
- Accept the feasible A2 (approved-target gold + recency stratum w/ caveat), or hold for a
  fully-prospective design (needs historical OpenTargets/ChEMBL snapshots — a separate effort).
- B1: reframe as "does the agent retrieve known drug-response/MoA" (LinkD has GDSC) or drop.
