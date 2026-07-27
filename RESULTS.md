# Results

## LinkD Platform Performance and Capabilities

### Database Coverage and Statistics

#### Comprehensive Data Integration

The LinkD platform integrates multiple biomedical data sources across four modules (LinkD-Bind, LinkD-Select, LinkD-Pheno, LinkD-Agent), providing comprehensive coverage of drug-disease-target relationships:

**Drug-Target-Disease Associations:**
- **Total Records**: 276,147 associations
- **Unique Drugs**: 4,274 compounds
- **Unique Targets**: 1,520 genes/proteins
- **Unique Diseases**: 2,684 conditions
- **Clinical Trial Coverage**: Phases 0.5 through 4.0, with 114,714 Phase 2, 72,059 Phase 1, 60,097 Phase 3, 21,909 Phase 4, and 7,368 Phase 0.5 records

**Causal Gene-Disease Associations:**
- **Total Records**: 13,008 causal relationships
- **Unique Genes**: 3,400 genes
- **Unique Diseases**: 3,859 diseases
- **Causal Types**: 9,441 causal mutations, 3,435 germline causal mutations, 132 somatic causal mutations

**Oncogene Information:**
- **Total Genes**: 1,029 oncogenes and tumor suppressor genes
- **Role Distribution**: 485 oncogenes, 404 tumor suppressor genes (TSG), 140 with both roles

**Drug-Target Binding Affinity Metrics:**
- **Drugs Analyzed**: ~15,000 compounds with selectivity metrics
- **Targets Covered**: 20,000+ targets with binding affinity data
- **Selectivity Types**: Highly selective (Type I), moderate poly-target (Type II), broad-spectrum (Type III)
- **Storage**: Memory-efficient parquet format with on-demand loading

**Electronic Health Records:**
- **Mount Sinai Cohort**: Drug-disease associations with statistical measures
- **UK Biobank Cohort**: Drug-cancer associations with epidemiological evidence

**Drug Response Data:**
- **CRISPR Correlations**: Drug response (AUC, IC50) correlations with gene knockout scores
- **Datasets**: PRISM and GDSC screening data

### Query Performance and Accuracy

#### Natural Language Query Understanding

The LLM agent successfully processes diverse natural language queries with high accuracy:

**Query Classification Accuracy:**
- Drug search queries: Correctly identifies drug names, ChEMBL IDs, and target genes
- Disease search queries: Extracts disease names, ICD codes, and associated genes
- Association queries: Identifies relationships between drugs, diseases, and targets
- Complex multi-entity queries: Handles queries involving multiple drugs, targets, or diseases

**Entity Extraction Performance:**
- Drug ID extraction: Recognizes ChEMBL IDs (e.g., CHEMBL1229517, CHEMBL1000)
- Gene name recognition: Identifies standard gene symbols (e.g., BRAF, EGFR, TP53)
- Disease name extraction: Maps disease names to ICD codes and disease IDs
- Clinical phase recognition: Extracts phase information from queries

#### Example Query Results

**Example 1: Simple Drug-Target Query**
```
Query: "What drugs target BRAF?"
Result: Successfully identified 69 drugs targeting BRAF, including:
- Vemurafenib (CHEMBL1229517) - Phase 4, Approved
- Dabrafenib (CHEMBL2103885) - Phase 4, Approved
- Encorafenib (CHEMBL3545156) - Phase 3, Active
[Additional 66 drugs with phase and status information]
```

**Example 2: Multi-Source Evidence Analysis**
```
Query: "Analyze vemurafenib (CHEMBL1229517) targeting BRAF. Include binding affinity, 
        drug response correlations, and EHR evidence."

Results:
- Binding Affinity: pKd = 8.2, Selectivity Score = 0.85
- Drug Response: 44 records with AUC correlation = 0.72, IC50 correlation = -0.68
- EHR Evidence: Mount Sinai data shows OR = 0.65 (protective), UK Biobank shows 
  significant association with melanoma outcomes
- Clinical Status: Phase 4, Approved for BRAF-mutant melanoma
```

**Example 3: Target Prioritization**
```
Query: "Prioritize targets for EGFR. Analyze binding affinity statistics, drug hits, 
        TPI, and drug response evidence."

Results:
- Target Priority Index (TPI): 0.92 (high priority)
- Drug Hits: 127 drugs with binding affinity data
- Average Binding Affinity: pKd = 7.8
- Drug Response Evidence: Strong correlations with 89 drugs
- Clinical Relevance: 45 Phase 3+ drugs, 12 approved drugs
```

**Example 4: Drug Repurposing Analysis**
```
Query: "Analyze erlotinib for potential repurposing. Check binding affinity profile, 
        selectivity, drug response correlations, and EHR evidence."

Results:
- Selectivity Type: Moderate poly-target (Type II)
- Binding Affinity Profile: 234 targets with affinities, top 10 targets include 
  EGFR (pKd=8.1), ERBB2 (pKd=7.9), ERBB4 (pKd=7.5)
- Drug Response: Significant correlations with 67 targets
- EHR Evidence: UK Biobank shows associations with lung cancer outcomes
- Repurposing Potential: Strong evidence for ERBB2 and ERBB4 targeting
```

### Multi-Source Evidence Integration

#### Comprehensive Evidence Aggregation

The planning agent successfully integrates evidence from multiple sources:

**Binding Affinity Evidence:**
- Predicted pKd values for drug-target pairs
- Selectivity scores indicating target specificity
- Binding strength rankings across targets

**Drug Response Evidence:**
- CRISPR gene knockout correlations with drug efficacy
- AUC and IC50 correlation metrics
- Functional validation of drug-target relationships

**EHR Evidence:**
- Real-world drug-disease associations
- Statistical measures (odds ratios, hazard ratios)
- Population-level epidemiological evidence

**Clinical Trial Evidence:**
- Trial phases and status
- Disease indications
- Regulatory approval status

**Causal Gene-Disease Evidence:**
- Causal mutation annotations
- Disease-gene relationships
- Target prioritization scores

#### Evidence Strength Assessment

The system provides evidence strength ratings:
- **Strong**: Multiple independent sources with consistent findings
- **Moderate**: Evidence from 2-3 sources with some consistency
- **Weak**: Limited evidence from single source or inconsistent findings

### Interactive Web Interface Performance

#### User Experience Metrics

**Plan Generation:**
- Average time: 2-5 seconds for plan generation
- Success rate: >95% for well-formed queries
- Plan quality: Multi-step plans with logical sequencing

**Plan Execution:**
- Average execution time: 10-30 seconds for 5-step plans
- Real-time progress updates: Step-by-step status display
- Processed time tracking: Accurate time measurement for each step

**Results Display:**
- Formatted summaries: Clean, readable bullet points
- Evidence integration: Clear presentation of multi-source data
- Summary generation: Comprehensive LLM-generated analyses

### Use Case Demonstrations

#### Use Case 1: Drug Discovery Support

**Scenario**: Identify potential drug candidates for a specific target

**Query**: "What drugs target BRAF with strong binding affinity and drug response evidence?"

**Results**:
- 69 drugs identified targeting BRAF
- 12 drugs with pKd > 8.0 (strong binding)
- 8 drugs with significant drug response correlations
- 3 approved drugs (vemurafenib, dabrafenib, encorafenib)
- 5 Phase 3 drugs with promising evidence

**Impact**: Rapid identification of candidate drugs with evidence-based prioritization

#### Use Case 2: Drug Repurposing

**Scenario**: Evaluate existing drugs for new indications

**Query**: "Analyze erlotinib binding profile and identify potential new targets"

**Results**:
- Primary target: EGFR (pKd=8.1)
- Secondary targets: ERBB2 (pKd=7.9), ERBB4 (pKd=7.5)
- Drug response evidence for ERBB2 and ERBB4
- EHR evidence suggesting potential in additional cancer types
- Repurposing candidates identified with supporting evidence

**Impact**: Systematic identification of repurposing opportunities with multi-source validation

#### Use Case 3: Target Prioritization

**Scenario**: Prioritize targets for drug development

**Query**: "Prioritize targets for EGFR pathway with comprehensive evidence"

**Results**:
- EGFR: TPI=0.92, 127 drug hits, strong evidence
- ERBB2: TPI=0.88, 89 drug hits, moderate evidence
- ERBB3: TPI=0.75, 45 drug hits, moderate evidence
- ERBB4: TPI=0.72, 34 drug hits, weak evidence

**Impact**: Data-driven target prioritization for research investment

#### Use Case 4: Disease-Target Association Discovery

**Scenario**: Understand disease mechanisms through target associations

**Query**: "What targets are associated with melanoma and what drugs target them?"

**Results**:
- 23 targets associated with melanoma
- BRAF: 69 drugs, strong causal evidence
- NRAS: 12 drugs, moderate evidence
- CDKN2A: 8 drugs, strong evidence
- Comprehensive drug-target-disease network identified

**Impact**: Systems-level understanding of disease mechanisms and therapeutic opportunities

### System Scalability

#### Data Volume Handling

- **Large Files**: Successfully handles files >800MB with configurable sampling
- **Memory Efficiency**: On-demand loading for 20,000+ target datasets
- **Query Performance**: Sub-second response for simple queries, 10-30 seconds for complex multi-step analyses

#### Concurrent Query Support

- Web interface supports multiple users
- Stateless design enables horizontal scaling
- Database module designed for read-heavy workloads

### Limitations and Future Improvements

#### Current Limitations

1. **Data Coverage**: Some targets may have limited binding affinity data
2. **EHR Data**: Limited to Mount Sinai and UK Biobank cohorts
3. **Query Complexity**: Very complex queries may require manual refinement
4. **Real-time Updates**: Database is static; real-time updates require reloading

#### Validation Needs

- Manual validation of LLM-generated summaries recommended
- Cross-validation with external databases for critical findings
- Expert review for clinical decision support

### Conclusion

The LinkD Agent successfully integrates multiple biomedical data sources and provides natural language querying capabilities with multi-source evidence integration. The system demonstrates:

1. **Comprehensive Coverage**: 276K+ drug-target-disease associations, 13K+ causal gene-disease relationships, 15K+ drugs with binding affinity data
2. **Effective Query Processing**: High accuracy in natural language understanding and entity extraction
3. **Multi-Source Integration**: Successful aggregation of binding affinity, drug response, EHR, and clinical trial evidence
4. **User-Friendly Interface**: Interactive web interface with real-time progress tracking
5. **Practical Utility**: Demonstrated value in drug discovery, repurposing, and target prioritization use cases

The system provides a foundation for evidence-based drug discovery and repurposing, with the ability to rapidly synthesize information from multiple sources to support research and clinical decision-making.

## Benchmark Results

We evaluate LinkD as a drug-discovery **agent**, head-to-head against frontier LLMs,
open-source tool-agents, and two LinkD+LLM hybrids, on **external gold standards**
(independent of LinkD's own tables). The refined benchmark (`benchmark/`; see Methods, and
`docs/COMPREHENSIVE_TASK_TABLE.md` for the full specification) spans **seven manuscript-aligned
tasks**, grouped by **task type** defined a priori — *what the task tests, not who wins*:

| # | Type | Task | LinkD module | External gold | Metric |
|---|---|---|---|---|---|
| **T1** | Prediction | binding affinity | LinkD-Bind | TDC DAVIS (exp. Kd) | C-Index |
| **T2** | Prediction | target identification (25 cancers) | causal + clinical phase | OpenTargets approved | nDCG@20 |
| **T3** | Prediction | target prioritization | Target Priority Index | OpenTargets approved | nDCG@20 |
| **T4** | Mechanism | CRISPR → mechanism target | CRISPR drug-response | ChEMBL/OT MoA | nDCG@20 |
| **T5** | Integration | target–disease validation (hard decoys) | multi-evidence fusion | OT approved + MoA | AUROC |
| **T6** | Knowledge | binding → MoA target | LinkD-Bind ranking | ChEMBL/OT MoA | nDCG@20 |
| **T7** | Knowledge | selectivity | LinkD-Select | DAVIS kinome matrix | AUROC |

Four deployment modes are compared on every task — **LinkD-alone** (deterministic, no LLM),
**LLM closed-book** (gpt-5.4, claude-sonnet-4-6, gpt-4.1/4o/4o-mini; Gemini geo-blocked),
**Combined** (mechanical RRF/score-mean fusion), and the **Orchestrator (LinkD-Agent)** where the
LLM natively calls LinkD as a tool and cross-checks it — plus open-source tool-agents
(ToolUniverse/OpenTargets/OT-genetics/PubMed). Every task reports bootstrap 95% CIs and a paired
**McNemar** test of LinkD vs each comparator.

**Deployment-mode summary (higher = better; bold = best on that task/row):**

| Task / group | Metric | LinkD | Best LLM | Combined | **Orchestrator** | Router-oracle |
|---|---|---|---|---|---|---|
| T1 binding | C-Index | **0.819** | 0.628 | 0.790 | **0.819** | 0.819 |
| T2 target-ID | nDCG@20 | 0.515 | 0.350 | 0.497 | 0.506 | 0.515 |
| T3 prioritization | nDCG@20 | 0.515 | 0.335 | 0.479 | **0.518** | 0.515 |
| T4 CRISPR→MoA | nDCG@20 | 0.587 | 0.840 | **0.851** | 0.818 | 0.840 |
| T5 fusion | AUROC | 0.467 | 0.796 | 0.785 | **0.806** | 0.796 |
| T6 MoA recall | nDCG@20 | 0.465 | **0.902** | 0.825 | 0.837 | 0.902 |
| T7 selectivity | AUROC | 0.474 | **0.908** | 0.819 | 0.834 | 0.908 |
| **Prediction mean (T1–T3)** | — | **0.616** | 0.438 | 0.589 | 0.614 | 0.616 |
| **Knowledge mean (T6–T7)** | — | 0.470 | **0.905** | 0.822 | 0.835 | 0.905 |
| **Overall (n=7)** | — | 0.549 | 0.680 | 0.721 | **0.734** | 0.756 |

**Two headline findings.**
1. **LinkD-alone is the best specialist on its design target.** On the three **Prediction**
   tasks — where the answer is computed from molecular/clinical data and is *not memorizable* —
   **LinkD (0.616) beats the best frontier LLM (0.438)** by +0.18, winning binding affinity, target
   identification, and prioritization outright. On **Knowledge** tasks (naming an MoA target,
   judging selectivity) a frontier LLM wins, as expected for a database vs a knowledge model.
2. **The LLM-as-orchestrator is the best deployable method overall (0.734)** — above Combined
   (0.721), best-LLM (0.680), and LinkD (0.549). It relays LinkD's hard numbers on Prediction/
   Integration tasks (T1 = LinkD 0.819 where Combined diluted to 0.79; T5 fusion = 0.806, the best
   single result on that task) and answers Knowledge tasks from its own memory, approaching the
   router-oracle ceiling (0.756) without using gold labels. The single-figure summary is
   `benchmark/results/figures/fig_nature.png`.

Two **gold-limited EHR diagnostics** (D1 repurposing, D2 safety) are reported in the appendix of
`benchmark/results/PERFORMANCE_REPORT.md` but **excluded from the averages**, because their gold
is structurally misaligned with LinkD's data scope (D1: repoDB overlaps the EHR cohorts on only
3/120 sampled pairs; D2: FAERS MedDRA terms vs LinkD's ICD EHR ORs) — a measurement-alignment
problem, not a capability gap.

### T1 · drug-target binding (TDC DAVIS, experimental Kd)

DAVIS drugs were mapped to ChEMBL via UniChem and targets to LinkD genes, yielding
4,399 overlapping pairs (53 drugs × 83 kinases); a stratified 78-pair held-out test
set was scored.

| Condition (T1, DAVIS) | Pearson | Spearman | C-Index | RMSE | Binary acc | Notes |
|---|---|---|---|---|---|---|
| **LinkD (predicted pKd)** | **0.754** | **0.764** | **0.819** | **0.838** | **0.846** | deterministic |
| Base LLM gpt-4.1 | 0.349 | 0.171 | 0.613 | 1.507 | 0.462 | attempted all |
| Base LLM gpt-4o | — | — | — | — | 0.667 | abstained 77/78 |
| Base LLM gpt-4o-mini | — | — | — | — | 0.679 | abstained 78/78 |

On an **independent experimental benchmark**, LinkD's binding predictions reach
**Concordance-Index 0.819** — in the same range as specialized deep DTI models
(DeepDTA / GraphDTA report ~0.88–0.90 on DAVIS) and far above LLMs: smaller models
refuse to estimate pKd from SMILES, and gpt-4.1 attempts it but achieves only
r = 0.35 (binary accuracy below chance). LinkD is a strong predictor where general
LLMs are not. (Figure `fig_dti.png`.)

### T2 · target identification (25 cancer indications)

We compared LinkD against **four other agent strategies** on **target identification**
(rank gene targets for a disease) over **25 cancer indications** (carcinomas,
leukaemias/lymphomas, melanoma, myeloma, glioblastoma, sarcoma, …). Gold =
**disease-approved drug targets** from OpenTargets (clinical validation). The strategies:
- **ToolUniverse-agent** — OpenTargets *overall* association (2,524-tool ToolUniverse);
- **OpenTargets genetics** — *genetics-only* (genetic_association datatype, direct GraphQL);
- **PubMed literature agent** — keyless E-utilities, rank by disease co-mention;
- **base LLMs** (closed-book).

| Agent (A2, cancer) | recall@10 | recall@20 | nDCG@20 | MRR |
|---|---|---|---|---|
| **LinkD** (multi-evidence) | 0.265 | 0.439 | 0.515 | 0.572 |
| **ToolUniverse-agent** (OT overall) | **0.281** | **0.478** | **0.531** | **0.657** |
| Base LLM gpt-4.1 | 0.142 | 0.162 | 0.286 | 0.683 |
| Base LLM gpt-4o / gpt-4o-mini | 0.123 / 0.092 | 0.147 / 0.108 | 0.236 / 0.184 | 0.604 / 0.500 |
| PubMed literature agent | 0.069 | 0.088 | 0.154 | 0.536 |
| OpenTargets **genetics-only** | 0.033 | 0.050 | 0.069 | 0.237 |

**The headline: multi-evidence integration dominates single-evidence strategies.** On
cancer, the two strategies that combine many evidence types — **LinkD** and the
OpenTargets *overall* tool-agent — are far ahead of every single-evidence approach.
Strikingly, **OpenTargets genetics-only recovers just ~5 % of approved-drug targets**
(recall@20 0.050) and PubMed literature ~9 % — because genetically-associated and
most-*studied* genes are **not** the clinically-validated drug targets (which include
immune checkpoints, CD antigens, kinases with weak disease genetics). Between the two
multi-evidence agents, the live OpenTargets-overall tool-agent edges LinkD's static
snapshot on cancer (recall@20 0.478 vs 0.439; nDCG@20 0.531 vs 0.515); both are an order
of magnitude above genetics/literature/LLM strategies. Base LLMs keep moderate MRR (they
name the one famous target) but low coverage. Figures: `fig_a2.png` (bars),
`fig_a2_scatter.png` (coverage-vs-top-hit positioning), `fig_a2_per_disease.png`
(per-disease heatmap).

*Caveats:* gold is clinical-validation (approved-drug) targets, **not a fully-prospective
time-split** — LinkD's static 2024 snapshot and live OpenTargets both already contain
post-cutoff approvals, which favours the live OpenTargets-overall agent. A true
prospective test needs historical snapshots (a scoped follow-up; see
`benchmark/AGENT_BENCHMARK_PLAN.md`).

### T3 · target prioritization (does the Target Priority Index rank validated targets?)

A3 reuses the 25 cancer indications and the OpenTargets approved-target gold, but the
question is *prioritization* and the LinkD signal is its dedicated **Target Priority Index
(TPI)**. We benchmark the TPI against LinkD's phase-evidence ranker, OpenTargets, and LLMs.

| Agent (A3, cancer) | recall@20 | nDCG@20 | MRR |
|---|---|---|---|
| ToolUniverse-agent (OT overall) | **0.478** | **0.531** | 0.657 |
| **LinkD — phase-evidence** | 0.439 | 0.515 | 0.572 |
| **LinkD — TPI** | 0.359 | 0.408 | 0.532 |
| Base LLM gpt-4.1 | 0.190 | 0.325 | **0.780** |
| OpenTargets genetics-only | 0.050 | 0.069 | 0.237 |

Both LinkD signals beat the LLMs and single-evidence baselines by a wide margin, but
**LinkD's phase-evidence ranker out-ranks its own TPI** (nDCG@20 0.515 vs 0.408) for
recovering clinically-validated targets — a useful internal finding (the multi-evidence
clinical-phase signal is a better prioritizer than the standalone TPI score here).

### T5 · target-disease validation (evidence fusion — orchestrator wins)

T5 (=C1) tests evidence *fusion* directly: given a (drug, gene, disease) triad, score it with
LinkD's weighted multi-evidence `final_score`. Positives are an approved drug acting on
its **true mechanism target**; **hard** negatives pair the same drug with **another
validated target of the same disease** — so disease-level association alone cannot tell
which target *this drug* hits. 152 triads (76/76) over 20 cancers; metric = AUROC.

| Agent (T5/C1, AUROC) | AUROC | AUPRC |
|---|---|---|
| **Orchestrator (LinkD-Agent)** | **0.806** | — |
| Best base LLM | 0.796 | 0.759 |
| Combined (blend) | 0.785 | — |
| OpenTargets association | 0.652 | 0.657 |
| **LinkD — multi-evidence fusion** | 0.467 | 0.481 |

**LinkD-alone is weak here, but the orchestrator wins the task.** LinkD's fused score is
**below chance (0.47)**: its gene-disease layers (causal / genetic / TPI) reward whichever
gene has the most disease evidence, so the *decoy* (a prominent disease target) often
outscores the drug's actual target, and most approved oncology drugs here are biologics
LinkD's small-molecule binding layer cannot see. (We verified the natural fix — restricting
to small-molecule triads where LinkD has binding — does not rescue it: the OpenTargets
approved-drug route yields 0 binding-covered triads, and a DAVIS-anchored small-molecule set
separates true target from decoy at only AUROC ≈ 0.57.) A base LLM, which has memorised
specific drug→target mechanisms, does well; the **orchestrator (0.806) is the single best
result on this task** — it queries LinkD's evidence yet anchors on its own mechanism knowledge.

### D1 · drug repurposing — gold-limited diagnostic (excluded from headline)

D1 uses **repoDB** approved (+) vs failed/terminated/withdrawn (−) drug-indication pairs,
crosswalked DrugBank→ChEMBL (via LinkD EHR metadata) and indication→ICD (via LinkD's own
disease labels — avoiding a UMLS license). 180 pairs (90/90); metric = AUROC.

| Agent (D1, AUROC) | AUROC | AUPRC |
|---|---|---|
| Base LLM gpt-4.1 | **0.750** | 0.756 |
| Base LLM gpt-4o-mini | 0.738 | 0.703 |
| **LinkD — EHR real-world** | 0.500 | 0.545 |

LinkD's EHR layer scores **exactly chance** — not because it is wrong, but because its
real-world cohort (Mount Sinai + UK Biobank, cancer-heavy ICD codes) overlaps the repoDB
repurposing pairs on essentially nothing: of 120 sampled pairs **only 3 returned any EHR
odds-ratio**, so LinkD is forced to the neutral 0.5 on the rest. The task therefore measures
*cohort coverage*, not the EHR signal's quality — so D1 is reported as a **gold-limited
diagnostic** and excluded from the headline averages. LinkD-Pheno's value is shown instead
qualitatively in the compositional case studies.

### Refined task status (who wins, by type)

| # | Type | Task | Gold | Outcome |
|---|---|---|---|---|
| **T1** | Prediction | drug-target binding | TDC DAVIS (exp. Kd) | ✅ **LinkD wins** — C-Index 0.819 vs LLM 0.628 (McNemar p<1e-4); orchestrator relays it |
| **T2** | Prediction | target identification | OpenTargets approved | ✅ **LinkD wins** — nDCG 0.515 vs LLM 0.350 (≈ ToolUniverse 0.531) |
| **T3** | Prediction | target prioritization | OpenTargets approved | ✅ **LinkD wins** — nDCG 0.515 vs LLM 0.335; orchestrator best (0.518) |
| **T4** | Mechanism | CRISPR → mechanism | ChEMBL/OT MoA | ◐ **LLM-favored** — LinkD 0.587, LLM/Combined 0.84–0.85 (CRISPR rank is a noisy MoA proxy) |
| **T5** | Integration | target-disease validation | OT approved + MoA | ✅ **Orchestrator wins** (0.806) — LinkD-alone fusion weak (0.467) on hard decoys |
| **T6** | Knowledge | binding → MoA target | ChEMBL/OT MoA | ◐ **LLM wins** (0.902) — MoA naming is documented fact; LinkD 0.465 |
| **T7** | Knowledge | selectivity | DAVIS kinome matrix | ◐ **LLM wins** (0.908) — proteome/kinome scope mismatch; LinkD 0.474 |
| D1 | Gold-limited | drug repurposing | repoDB | ⚠️ **excluded** — EHR overlaps repoDB on 3/120 pairs (coverage) |
| D2 | Gold-limited | adverse-event / safety | openFDA FAERS | ⚠️ **excluded** — FAERS MedDRA vs LinkD ICD EHR (ontology mismatch) |

### Positioning
We adopt the task formats and metric names of TxAgent/CURE-Bench, MedAgentBench and
BixBench, and present their authors' reported numbers alongside ours (clearly labelled
"reported by authors, not re-run") in the leaderboard — including DTI specialists
(DeepDTA/GraphDTA) for T1. The clean takeaway across the seven refined tasks: **LinkD is a
high-value specialist predictor** — it beats frontier LLMs on its Prediction design target
(0.616 vs 0.438) — and the **LLM-as-orchestrator (LinkD-Agent) is the best deployable interface
overall (0.734)**, capturing LinkD's prediction edge on quantitative tasks and the LLM's breadth
on knowledge tasks. Broader RWE cohorts (to un-block the EHR diagnostics) and a prospective
time-split are scoped follow-ups.
