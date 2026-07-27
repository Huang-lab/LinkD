# Methods

## LinkD: Multi-Evidence Supported Drug Discovery Platform

### System Overview

LinkD is an AI-powered platform designed to integrate and query multi-source biomedical data for drug-disease-target associations. The platform provides four interconnected modules:

- **LinkD-Bind**: Drug-target interaction binding affinity analysis (1,068 targets with pKd values)
- **LinkD-Select**: Drug selectivity profiling via UMAP clustering (14,981 drugs)
- **LinkD-Pheno**: Phenotype-drug associations from electronic health records (41K+ associations)
- **LinkD-Agent**: AI-powered multi-step analysis using LLMs (OpenAI, Google Gemini, Anthropic Claude)

The system combines structured database queries with large language model capabilities to enable natural language querying and multi-step analysis planning. The web interface is built with FastAPI (Python backend) and React with TypeScript (frontend), serving interactive Plotly.js visualizations.

### Core Modules

#### 1. Database Query Module (`database_query_module.py`)

The database query module serves as the foundational data access layer, providing programmatic access to multiple integrated data sources.

**Data Sources Integrated:**

- **Drug-Target-Disease Associations**: Clinical trial data including 276,147 records covering 4,274 unique drugs, 1,520 targets, and 2,684 diseases across clinical phases (0.5-4.0)
- **Causal Gene-Disease Associations**: 13,008 records linking 3,400 genes to 3,859 diseases with causal mutation annotations
- **Oncogene Information**: 1,029 oncogenes and tumor suppressor genes with role classifications
- **Drug-Target Binding Affinity Metrics**: Predicted binding affinities (pKd values) and selectivity scores for ~15,000 drugs across 20,000+ targets, stored in memory-efficient parquet format
- **Electronic Health Records (EHR)**: 
  - Mount Sinai cohort: Drug-disease associations with statistical measures (odds ratios, hazard ratios)
  - UK Biobank cohort: Drug-cancer associations with epidemiological evidence
- **Drug Response Data**: CRISPR gene knockout correlations with drug response metrics (AUC, IC50) from PRISM and GDSC datasets

**Key Functions:**

The module implements 30+ query functions organized into categories:
- Drug queries: `search_drugs()`, `get_drugs_by_target()`, `get_drugs_by_disease()`
- Disease queries: `search_diseases()`, `get_diseases_by_gene()`
- Target queries: `search_targets()`, `get_target_info()`
- Association queries: `get_drug_disease_associations()`, `get_disease_target_associations()`, `get_causal_gene_disease_associations()`
- Binding affinity queries: `get_drug_target_binding_affinity()`, `get_targets_for_drug_with_affinity()`, `get_target_binding_stats()`
- Selectivity queries: `get_drug_selectivity_info()`, `get_drugs_by_selectivity_type()`
- EHR queries: `get_ehr_drug_disease_associations()`, `assess_prevention_risk()`
- Drug response queries: `get_drug_response_associations()`, `get_drug_target_evidence()`
- Evidence aggregation: `get_comprehensive_drug_target_evidence()`

**Memory Management:**

For large datasets (>200MB), the module implements configurable loading strategies:
- Full data loading: Complete dataset in memory for comprehensive queries
- On-demand loading: Parquet files loaded only when specific queries require them
- Sampling mode: Optional 100,000-row sampling for rapid exploration

#### 2. LLM Agent Module (`llm_agent.py`)

The LLM agent module provides natural language understanding and query routing using OpenAI's GPT models.

**Architecture:**

- **Query Classification**: Uses GPT-4o or GPT-4o-mini to classify queries into types:
  - `drug_search`: Find drugs by target, disease, or properties
  - `disease_search`: Find diseases by gene or name
  - `target_search`: Find targets/genes by name or disease
  - `association`: Find relationships between entities
  - `binding_affinity`: Query drug-target binding affinities
  - `selectivity`: Query drug selectivity metrics
- **Entity Extraction**: Extracts drug IDs (ChEMBL), gene names, disease names, ICD codes, and clinical trial phases from natural language
- **Query Routing**: Automatically routes classified queries to appropriate database functions
- **Result Formatting**: Uses GPT to format structured database results into natural language summaries

**Fallback Mechanism:**

When GPT is unavailable, the module uses rule-based classification with:
- Pattern matching for common query structures
- Gene name extraction from curated lists
- Keyword-based classification

**Web Search Integration:**

Optional web search capability (via `web_search_helper.py`) supports multiple providers:
- DuckDuckGo (no API key required)
- SerpAPI
- Google Custom Search
- Bing Search

#### 3. LLM Planning Agent Module (`llm_planning_agent.py`)

The planning agent extends the LLM agent with multi-step analysis capabilities.

**Planning Process:**

1. **Plan Generation**: Given a natural language query, GPT generates a structured analysis plan with:
   - Step-by-step analysis tasks
   - Required data sources for each step
   - Logical sequencing of queries

2. **Plan Execution**: Executes steps sequentially, tracking:
   - Step status (pending, in_progress, completed, failed)
   - Step results
   - Error handling

3. **Multi-Source Integration**: Combines evidence from:
   - Binding affinity data (predicted pKd values, selectivity scores)
   - EHR data (real-world associations, odds ratios)
   - Drug response data (CRISPR correlations, AUC/IC50)
   - Clinical trial data (phases, status)
   - Causal gene-disease associations

4. **Summary Generation**: Uses GPT to synthesize results from all steps into a comprehensive analysis summary

**Data Structure:**

- `AnalysisPlan`: Container for query and list of `PlanStep` objects
- `PlanStep`: Individual step with description, data sources, status, and results

#### 4. Interactive Web Server (`interactive_web_server/app.py`)

The web server provides a user-friendly interface built with Gradio.

**Features:**

- **Query Interface**: Natural language query input with example queries
- **Plan Visualization**: Real-time display of generated analysis plans
- **Execution Tracking**: Live progress updates showing:
  - Current step being executed
  - Completed steps
  - Processed time for each step and total execution
- **Results Display**: Formatted results with:
  - Analysis results summary (bullet points with findings)
  - LLM-generated comprehensive summary
  - Processing details and timing information
- **History**: Execution history tracking for previous queries

**Technical Implementation:**

- Built with Gradio 6.0+ for web interface
- Custom CSS for styling (Helvetica font, color-coded status)
- Generator functions for real-time updates
- Markdown-to-HTML conversion for formatted summaries
- Configurable port and public link sharing

### Data Integration Pipeline

#### Data Loading Strategy

1. **Initialization**: Database module loads all CSV files into pandas DataFrames
2. **Large File Handling**: Files >200MB can be sampled (100K rows) or loaded fully based on `load_full_data` parameter
3. **Parquet File Handling**: Target-centric binding affinity data stored in 100 parquet files, loaded on-demand for specific queries
4. **Memory Efficiency**: On-demand loading prevents memory overflow for 20,000+ target datasets

#### Data Normalization

- Drug IDs standardized to ChEMBL format
- Gene names normalized to standard symbols
- Disease names mapped to ICD codes where applicable
- Clinical trial phases standardized (0.5, 1.0, 2.0, 3.0, 4.0)

### Query Processing Pipeline

#### Natural Language Query Flow

1. **Input**: User provides natural language query (e.g., "Analyze vemurafenib targeting BRAF with binding affinity and EHR evidence")

2. **LLM Processing**:
   - Query classification via GPT
   - Entity extraction (drug IDs, genes, diseases)
   - Intent understanding

3. **Plan Generation** (Planning Agent):
   - GPT generates step-by-step plan
   - Identifies required data sources
   - Sequences logical analysis steps

4. **Execution**:
   - Each step queries appropriate database functions
   - Results aggregated per step
   - Status tracked in real-time

5. **Synthesis**:
   - GPT generates comprehensive summary
   - Results formatted for display
   - Evidence from multiple sources integrated

#### Query Types Supported

- **Simple Queries**: Single-entity lookups (e.g., "What drugs target BRAF?")
- **Association Queries**: Relationship discovery (e.g., "What diseases are associated with TP53?")
- **Multi-Source Queries**: Evidence aggregation (e.g., "Analyze erlotinib with binding affinity, drug response, and EHR data")
- **Complex Analysis**: Multi-step investigations (e.g., "Prioritize targets for EGFR with comprehensive evidence")

### Technical Specifications

**Programming Language**: Python 3.7+

**Core Dependencies**:
- pandas: Data manipulation and querying
- numpy: Numerical computations
- openai: GPT model integration
- gradio: Web interface framework

**Data Formats**:
- CSV: Primary data storage format
- Parquet: Efficient storage for large binding affinity datasets
- JSON: Configuration and API responses

**LLM Models**:
- Primary: GPT-4o-mini (cost-effective, fast)
- Alternative: GPT-4o (higher quality, slower)

### Validation and Quality Assurance

**Data Validation**:
- File existence checks before loading
- Column presence validation
- Data type consistency checks
- Missing value handling

**Error Handling**:
- Graceful degradation when GPT unavailable
- Fallback to rule-based classification
- Error messages for missing data
- Step failure tracking in planning agent

**Performance Optimization**:
- Configurable data sampling for large files
- On-demand parquet file loading
- Memory-efficient query execution
- Caching of frequently accessed data structures

### Reproducibility

**Configuration**:
- Environment variables for API keys
- Configurable model selection
- Adjustable data loading strategies
- Customizable web server settings

**Documentation**:
- Comprehensive README with usage examples
- Jupyter notebooks for exploration
- Code comments and docstrings
- Technology log for change tracking

### Drug-Discovery Agent Benchmark (`benchmark/`)

To evaluate LinkD as a drug-discovery **agent** we built a reproducible,
provider-agnostic benchmark that compares LinkD **head-to-head with other
open-source agents** on **external gold standards** — answers drawn from independent
public datasets, never from LinkD's own tables — and on **cancer** indications,
LinkD's strongest use case. The design adopts task formats and metric names from
recent agentic-biomedicine work: TxAgent / ToolUniverse and CURE-Bench [1,2],
MedAgentBench [3], BixBench [4], and contamination controls from target-prioritization
benchmarking (entity-disjoint / cold splits) [5,6]. The methodology and metrics are
summarised in `benchmark/results/figures/fig_workflow.png`.

**Tasks (refined, manuscript-aligned).** Seven headline tasks, each mapped to a LinkD
module/layer and grouped by **task type** defined a priori — *what the task tests, not who
wins*. **Prediction** = the answer must be computed from molecular/clinical data and is not
in any text corpus (LinkD's design target); **Mechanism/Integration** = infer or fuse
evidence; **Knowledge** = the answer is a documented fact (LLM home turf). Full specification:
`docs/FIG6_BENCHMARK_SI.md` and [`benchmark/TASK_CATALOG.md`](benchmark/TASK_CATALOG.md).

- **T1 · binding affinity** *(Prediction; LinkD-Bind)* — predict pKd for a drug–kinase pair,
  scored against experimental Kd from **TDC DAVIS** (DAVIS CID→ChEMBL via UniChem, targets→LinkD
  genes; stratified 78-pair held-out test).
- **T2 · target identification** *(Prediction; causal + clinical-phase evidence)* — rank gene
  targets for a cancer vs **OpenTargets approved-drug** targets (25 cancers).
- **T3 · target prioritization** *(Prediction; Target Priority Index)* — same gold/diseases,
  testing whether the TPI ranks validated targets near the top.
- **T4 · CRISPR → mechanism** *(Mechanism; CRISPR drug-response)* — recover a drug's MoA gene
  from its PRISM/GDSC CRISPR-response correlation, vs ChEMBL/OpenTargets MoA.
- **T5 · target–disease validation** *(Integration; weighted multi-evidence fusion)* — score
  (drug, gene, disease) triads with LinkD's `final_score`; positives = approved drug on its true
  mechanism target, **hard** negatives = the same drug paired with another validated target of
  the disease; AUROC.
- **T6 · binding → MoA target** *(Knowledge; LinkD-Bind ranking)* — rank a drug's MoA target
  from predicted binding, vs ChEMBL/OpenTargets MoA. The MoA is a documented fact, so this is a
  knowledge-recall task.
- **T7 · selectivity** *(Knowledge; LinkD-Select)* — classify a kinase inhibitor as selective
  vs promiscuous, vs the DAVIS kinome matrix.

Two **gold-limited diagnostics** (LinkD-Pheno EHR) are reported but **excluded from headline
averages** because the external gold is structurally misaligned with LinkD's data scope, not a
capability gap: **D1 repurposing** (repoDB approved/failed — only **3 of 120** sampled pairs have
any EHR odds-ratio; the task measures cohort coverage), and **D2 safety** (openFDA **FAERS**
MedDRA adverse-event terms vs LinkD's **ICD** EHR disease ORs — different ontologies). We verified
these are not prompt- or column-fixable; likewise **T7** selectivity stays weak because LinkD's
`Selectivity_Score` is **proteome-wide (~20k targets)** while DAVIS is **kinome-only** (Spearman
ρ≈0.19 for the score in use, ≤0.38 for any column, ρ≈0.25 even when re-derived from LinkD's
predicted kinome profile).

**Conditions.** Each item is answered under uniform adapters: **LinkD-alone** (deterministic
database ranker / predicted-pKd lookup, no LLM); **LLM closed-book** (gpt-5.4, claude-sonnet-4-6,
gpt-4.1/4o/4o-mini — Gemini is geo-blocked at our location and excluded); **Combined** (mechanical
fusion of LinkD + LLM: RRF for rankings, mean for scores); **Orchestrator (LinkD-Agent)** — a
real function-calling agent where the LLM natively *calls LinkD as a tool*, cross-checks the
result against its own knowledge, and answers; and open-source tool-agents **ToolUniverse**
(OpenTargets overall association), **OpenTargets genetics-only**, **OpenTargets association**, and
a keyless **PubMed** literature-mining agent. The non-LLM agents are deterministic and run offline
from cached gold at zero API cost.

**Metrics.** T1 (regression vs experimental Kd): Pearson r, Spearman ρ, Concordance (C-)Index,
RMSE, binary accuracy at pKd≥7. T2/T3/T4/T6 (ranking vs approved/MoA target set): recall@10/20,
nDCG@20, MRR. T5/T7 + diagnostics (binary discrimination): AUROC, AUPRC with a stratified
bootstrap CI. Latency per item is recorded throughout.

**Findings (honest, both directions).**
- **LinkD-alone is the best specialist on its design target.** On the three **Prediction** tasks
  LinkD averages **0.616 vs the best frontier LLM's 0.438** — it wins binding affinity (C-Index
  0.819 vs 0.628; McNemar p<1e-4), target identification (nDCG 0.515 vs 0.350), and prioritization
  (0.515 vs 0.335). These answers are computed from data and are not memorizable.
- **The LLM wins Knowledge recall** (T6 MoA naming 0.902, T7 selectivity 0.908) — as expected for
  a database vs a knowledge model.
- **The LLM-as-orchestrator is the best deployable method overall (0.734)** — above Combined
  (0.721), best-LLM (0.680) and LinkD (0.549) — by relaying LinkD's hard numbers on Prediction/
  Integration tasks (T1 = LinkD 0.819 where Combined diluted to 0.79; T5 fusion = 0.806, the single
  best on that task) and answering Knowledge tasks from its own memory. It approaches the
  router-oracle ceiling (0.756) without using gold labels.

**ID harmonization & caching.** Cross-source identifiers are reconciled with UniChem
(PubChem CID → ChEMBL, cached) for T1, and OpenTargets EFO resolution for A2. All
external API responses (OpenTargets, PubMed, UniChem) are cached under
`benchmark/external_data/cache/`, so runs are offline and reproducible despite a
flaky sandbox network.

**Statistics.** Per-metric bootstrap 95% confidence intervals and the McNemar paired
test for agent-vs-agent comparison on identical items (pure-stdlib implementation).

**Reproducibility.** Gold and task sets are auto-built and cached as JSONL; the runner
and smoke test are provider-agnostic and exit gracefully (with a SKIP) when data or
API keys are absent, so the deterministic agents run end-to-end at zero API cost.

**Caveats.** T2/T3 gold is clinical-validation (approved-drug) targets, **not a
fully-prospective time-split** — both LinkD's static 2024 snapshot and the live
OpenTargets API already contain post-cutoff approvals, which favours the live
OpenTargets-overall agent. A true prospective test needs historical snapshots (scoped
follow-up). The EHR diagnostics (D1/D2) are gold-limited by cohort coverage and ontology
mismatch (above); LinkD-Pheno's value is instead shown qualitatively in the compositional
case studies (`benchmark/case_studies.py`, figures `fig_case1..3`).

**References.** [1] TxAgent / ToolUniverse, arXiv:2503.10970. [2] CURE-Bench,
arXiv:2512.11682. [3] MedAgentBench, NEJM AI 2025. [4] BixBench, arXiv:2503.00096.
[5] Genomics of drug target prioritization for complex diseases, Nat. Rev. Genet.
2025. [6] PyTDC / Therapeutics Data Commons, arXiv:2505.05577. DTI specialists for
T1 context: DeepDTA (Öztürk 2018), GraphDTA (Nguyen 2021).
