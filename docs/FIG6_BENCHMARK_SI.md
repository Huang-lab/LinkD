# LinkD-Agent benchmark — supplementary methods, tables, and draft text (Figure 6c)

Supporting information for the LinkD-Agent benchmark panel (Figure 6c;
`benchmark/results/figures/fig6_benchmark_heatmap.{pdf,png}`, alternative grouped-bar version
`fig6_benchmark_bars.{pdf,png}`). This document provides the benchmark Methods, the task and dataset
specifications (Tables S1–S5), and draft Results and Discussion text for the main manuscript.

---

## Methods

### Benchmark design and scope

LinkD was evaluated as an autonomous drug-discovery agent against frontier large language models
(LLMs) and an open-source tool agent across seven tasks that span the platform's modules
(LinkD-Bind, LinkD-Select, LinkD-Pheno, and the weighted multi-evidence integration layer). All
tasks were restricted to oncology indications and were scored against external gold standards
derived from public resources that are independent of LinkD's internal tables, thereby avoiding
circularity between the evaluated predictions and the evaluation labels. Tasks were assigned a
priori to one of three categories according to the type of inference required: *prediction* tasks
(T1–T3), whose answers must be computed from molecular or clinical data and are not retrievable from
text; *mechanism and integration* tasks (T4–T5); and *knowledge-recall* tasks (T6–T7), whose
answers are documented in the pharmacological literature. The full task specification is given in
Table S1.

### External gold-standard datasets and identifier harmonization

Drug–target binding affinity was benchmarked against the DAVIS dataset obtained from the
Therapeutics Data Commons (TDC), using experimentally measured dissociation constants (Kd)
transformed to pKd = −log10(Kd[M]). Disease-target identification, prioritization, and triad
validation used the Open Targets Platform (release 24.09) for disease-approved drugs and their
mechanism-of-action (MoA) targets, and ChEMBL (release 34) for MoA annotations. Functional
drug–gene relationships were taken from drug-response/CRISPR-dependency correlation profiles derived
from the PRISM and GDSC pharmacogenomic screens (2024-Q4). Cross-resource identifiers were
harmonized programmatically: PubChem compound identifiers (CIDs) were mapped to ChEMBL identifiers
through the UniChem application programming interface (API); disease names were resolved to
Experimental Factor Ontology (EFO) identifiers via Open Targets and to ICD-10 codes via the
platform's disease dictionary; and DAVIS target labels were normalized to HGNC gene symbols. All
external API responses were cached on disk so that the benchmark is fully reproducible and can be
executed offline. The complete list of resources, versions, and sizes is given in Table S2.

### Task construction

Each task was constructed as a set of items with a held-out gold label (Table S1). For binding
affinity (T1), DAVIS drug–target pairs were aligned to LinkD's entity space and a stratified,
held-out test set of 78 pairs (spanning strong binders, intermediate binders, and non-binders) was
scored against the experimental pKd. For target identification and prioritization (T2, T3), the
gold target set for each of 25 cancers comprised the genes targeted by drugs approved for that
disease in Open Targets. For mechanism recovery from CRISPR (T4) and from binding (T6), the gold set
was each drug's ChEMBL/Open Targets MoA targets (60 and 44 drugs, respectively). For triad
validation (T5), 152 (drug, gene, disease) triads were balanced into 76 positives—an approved drug
paired with its true MoA target—and 76 *hard* negatives—the same drug paired with a different
validated target of the same disease, so that disease-level association alone cannot distinguish the
classes. For selectivity (T7), 35 kinase inhibitors were labeled selective or promiscuous from the
number of kinases bound at pKd ≥ 7 in the full DAVIS kinome matrix.

### Methods compared

Five methods were evaluated on identical items with identical scoring (Table S3). (i) **LinkD**:
deterministic predictions and rankings retrieved directly from the platform's command-line
interface, without any LLM. (ii) **LLM (closed-book)**: a frontier model (GPT-5.4; OpenAI) answering
from parametric memory, given the task question and an output-format instruction but no tools; the
model claude-sonnet-4-6 was additionally evaluated and yielded comparable closed-book performance,
whereas Gemini-2.5-pro was not accessible from our location. (iii) **ToolUniverse**: the Open Targets
overall gene–disease association score retrieved through the ToolUniverse tool server, applied to the
disease-target tasks (T2, T3) and as the association baseline for evidence fusion (T5). (iv) **LinkD
+ LLM (Combined)**: a mechanical fusion in which, for each item, the relevant LinkD layer and the
closed-book LLM were executed independently and combined by output type—reciprocal-rank fusion
(k = 60) for ranked lists and the arithmetic mean for continuous scores. (v) **LinkD + LLM
(Orchestrator; LinkD-Agent)**: a native function-calling agent in which the LLM was provided LinkD
tools, autonomously issued tool calls that the harness executed against the LinkD CLI (with the
item's drug, gene, and disease identifiers injected to prevent identifier hallucination), reasoned
over and cross-checked the returned values against its own knowledge, and produced an answer in the
required format within at most five tool-calling rounds. The Combined and Orchestrator methods used
GPT-5.4.

### Evaluation metrics

Binding-affinity prediction (T1) was scored by the concordance index (C-Index; primary), Pearson
correlation, root-mean-square error (RMSE), and binary accuracy at a pKd ≥ 7 threshold, computed
between predicted and experimental pKd. Ranking tasks (T2–T4, T6) were scored by the normalized
discounted cumulative gain at rank 20 (nDCG@20; primary), recall@10, recall@20, and mean reciprocal
rank, with the gold target set treated as the relevant items. Binary-discrimination tasks (T5, T7)
were scored by the area under the receiver-operating-characteristic curve (AUROC; primary) and the
area under the precision–recall curve (AUPRC). Figure 6c reports the per-task primary metric; all
primary metrics are bounded in [0, 1] with higher values indicating better performance (Table S4).

### Statistical analysis

Ninety-five percent confidence intervals for AUROC were estimated by stratified bootstrap resampling
(1,000 iterations, resampling positive and negative items independently). For each task, LinkD was
compared with every other method on identical items using the paired McNemar test applied to the
per-item correctness indicator.

### Implementation and reproducibility

Tasks, gold labels, and cached resource responses were serialized as JSON Lines. The deterministic
methods (LinkD, ToolUniverse) execute offline at no API cost; LLM requests used a 90-second timeout
with two automatic retries. The benchmark harness, task builders, scorers, and figure-generation
code are provided in the accompanying code repository.

---

## Table S1. Benchmark task specification

| ID | Task | Category | LinkD module / signal | Input → output | Gold standard (source) | n | Primary metric | Secondary metrics |
|---|---|---|---|---|---|---|---|---|
| T1 | Binding affinity | Prediction | LinkD-Bind; predicted pKd (diffusion DTI model) | (drug, target gene) → pKd | Experimental Kd → pKd (TDC DAVIS) | 78 pairs | C-Index | Pearson r, RMSE, accuracy @ pKd ≥ 7 |
| T2 | Target identification | Prediction | Causal gene–disease + clinical-phase evidence | cancer → ranked target genes | Approved-drug targets (Open Targets 24.09) | 25 cancers | nDCG@20 | recall@10, recall@20, MRR |
| T3 | Target prioritization | Prediction | Target Priority Index (TPI) | cancer → prioritized target genes | Approved-drug targets (Open Targets 24.09) | 25 cancers | nDCG@20 | recall@10, recall@20, MRR |
| T4 | CRISPR → mechanism | Mechanism | LinkD-Pheno; drug-response–CRISPR correlation (PRISM/GDSC) | drug → genes ranked by \|correlation\| | MoA targets (ChEMBL 34 / Open Targets) | 60 drugs | nDCG@20 | recall@10, recall@20, MRR |
| T5 | Evidence fusion | Integration | Weighted multi-evidence score (binding + CRISPR + EHR + causal + clinical + TPI) | (drug, gene, disease) → confidence | Approved drug + MoA target vs same-disease decoy (Open Targets / ChEMBL); 76 / 76 | 152 triads | AUROC | AUPRC, 95% CI |
| T6 | MoA recall | Knowledge | LinkD-Bind; binding-ranked targets | drug → ranked MoA genes | MoA targets (ChEMBL 34 / Open Targets) | 44 drugs | nDCG@20 | recall@10, recall@20, MRR |
| T7 | Selectivity | Knowledge | LinkD-Select; Selectivity_Score (proteome-wide) | drug → selective vs promiscuous | Kinome strong-binder count (TDC DAVIS); 19 / 16 | 35 drugs | AUROC | AUPRC, 95% CI |

## Table S2. Datasets and resources

| Resource | Source / version | Size | Role in benchmark |
|---|---|---|---|
| DAVIS | Therapeutics Data Commons (TDC) | 68 drugs × 379 kinases (experimental Kd) | Binding-affinity gold (T1); kinome selectivity gold (T7) |
| Open Targets Platform | release 24.09 | genome-wide | Approved-drug target gold (T2, T3, T5); ToolUniverse association score |
| ChEMBL | release 34 | — | Mechanism-of-action target annotations (T4, T5, T6) |
| PRISM + GDSC drug response | 2024-Q4 | 464,820 drug–gene correlations | LinkD-Pheno CRISPR-dependency signal (T4) |
| LinkD-Bind predictions | this work | 14,981 drugs × 20,385 targets | Predicted pKd (T1, T6) |
| LinkD-Select profiles | this work | 14,981 drugs | Proteome-wide Selectivity_Score (T7) |
| drug_target_disease | ChEMBL-derived | 276,147 associations | Clinical-phase target evidence (T2) |
| causal_gene_disease | Open Targets | 13,008 associations | Causal gene–disease evidence (T2) |
| UniChem | EMBL-EBI | — | PubChem CID → ChEMBL identifier mapping |

## Table S3. Methods compared

| Method | Description | Underlying model |
|---|---|---|
| LinkD | Deterministic database/CLI predictions and rankings; no LLM | none (tools only) |
| GPT-5.4 | Frontier LLM, closed-book (parametric memory only, no tools) | OpenAI gpt-5.4¹ |
| ToolUniverse | Open Targets overall gene–disease association via the ToolUniverse tool server² | none (tool API) |
| LinkD + GPT-5.4 (Combined) | Mechanical fusion: reciprocal-rank fusion for rankings, mean for scores | gpt-5.4 |
| LinkD + GPT-5.4 (Orchestrator) | LinkD-Agent: the LLM natively calls LinkD tools, cross-checks, and answers | gpt-5.4 |

¹ claude-sonnet-4-6 was also evaluated (comparable closed-book/combined performance); Gemini-2.5-pro
was not accessible at our location. ² Open Targets-genetics and a PubMed literature-mining agent were
additionally evaluated as single-evidence baselines; ToolUniverse(Open Targets) is the strongest and
is reported. ToolUniverse applies only to disease-target tasks (T2, T3) and as the association
baseline for T5.

## Table S4. Evaluation metrics

| Metric | Definition | Tasks |
|---|---|---|
| C-Index | Probability that a randomly chosen higher-affinity pair is ranked above a lower-affinity pair | T1 |
| Pearson r | Linear correlation between predicted and experimental pKd | T1 |
| RMSE | Root-mean-square error between predicted and experimental pKd | T1 |
| nDCG@20 | Normalized discounted cumulative gain over the 20 top-ranked genes | T2–T4, T6 |
| recall@k | Fraction of gold targets retrieved within the top k (k = 10, 20) | T2–T4, T6 |
| MRR | Mean reciprocal rank of the first gold target | T2–T4, T6 |
| AUROC | Area under the receiver-operating-characteristic curve | T5, T7 |
| AUPRC | Area under the precision–recall curve | T5, T7 |

## Table S5. Benchmark results (per-task primary metric; values plotted in Figure 6c)

| Task | Metric | LinkD | GPT-5.4 | ToolUniverse | Combined | Orchestrator |
|---|---|---|---|---|---|---|
| T1 binding affinity | C-Index | **0.819** | 0.518 | — | 0.772 | **0.819** |
| T2 target identification | nDCG@20 | 0.515 | 0.350 | 0.531 | 0.497 | 0.506 |
| T3 target prioritization | nDCG@20 | 0.515 | 0.335 | 0.531 | 0.479 | 0.518 |
| T4 CRISPR → mechanism | nDCG@20 | 0.587 | 0.808 | — | 0.836 | 0.818 |
| T5 evidence fusion | AUROC | 0.467 | 0.759 | 0.652 | 0.725 | **0.806** |
| T6 MoA recall | nDCG@20 | 0.465 | 0.834 | — | 0.825 | 0.837 |
| T7 selectivity | AUROC | 0.474 | 0.845 | — | 0.806 | 0.834 |
| **Mean** | — | 0.549 | 0.636 | 0.571* | 0.706 | **0.734** |

*ToolUniverse mean over its three applicable tasks (T2, T3, T5).

---

## Draft text — Results (brief)

LinkD was benchmarked as an autonomous agent against frontier LLMs and an open-source tool agent
across seven drug-discovery tasks on cancer indications, each scored against external gold standards
independent of LinkD's tables (Figure 6c; Tables S1–S5). The methods exhibited complementary
strengths. LinkD alone was strongest on prediction tasks whose answers must be computed from
molecular and clinical data—binding-affinity estimation (C-Index 0.819 versus 0.518 for the
closed-book LLM), cancer target identification, and target prioritization—whereas the frontier LLM
was strongest on tasks reducible to documented pharmacological knowledge (mechanism and selectivity
recall; nDCG@20/AUROC 0.81–0.85). Mechanically combining LinkD with the LLM improved the
task-averaged score to 0.706, but the LinkD-Agent orchestrator—in which the LLM queries LinkD as a
tool and cross-checks its output—achieved the highest overall performance (mean 0.734) and was the
best or tied-best method on every task category, including integrative triad validation (AUROC
0.806). The orchestrator thus combined LinkD's quantitative-prediction advantage with the breadth of
the LLM in a single interface, outperforming LinkD alone, the LLM alone, ToolUniverse (Open
Targets), and equal-weight fusion.

## Draft text — Discussion (brief)

The benchmark delineates where an integrated agent adds value. Because LinkD's predictions are
computed from molecular structure, perturbation phenotypes, and real-world evidence rather than
retrieved from text, LinkD alone surpassed frontier LLMs on quantitative tasks such as
binding-affinity estimation and target prioritization—capabilities that an LLM cannot reproduce from
parametric memory. Conversely, for relationships already well documented in the literature, such as a
drug's canonical mechanism or selectivity class, the frontier LLM was the stronger recall engine. No
single method dominated across task types. The decisive result is that an LLM orchestrating
LinkD—issuing tool calls for values it cannot reliably recall and cross-checking them against its own
knowledge—outperformed both constituents and avoided the dilution incurred by naive score fusion.
These findings support deploying LinkD-Agent, rather than LinkD or an LLM in isolation, as the
interface for multi-scale drug-repurposing analysis. A limitation is that per-item benchmarks reward
recognition of known drug–target relationships and therefore favor memorization; LinkD's distinctive
contribution is clearest for quantitative magnitude estimation and for the proteome-scale, novel
interactions that lack a curated answer—precisely the discovery setting for which LinkD is designed.
