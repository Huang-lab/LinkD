# Nature Portfolio Reporting Summary — draft answers

Paste into [`nr-reporting-summary-ChengWang.pdf`](nr-reporting-summary-ChengWang.pdf) in **Adobe Reader**.  
Source: `docs/Submit/Manuscript_Submission.pdf`, SI, and `For_Reviewer/`.  
Do **not** enter “n/a” in free-text boxes; use the wording below (or Nature help-text equivalents).

---

## Gaps to resolve before pasting (authors)

Tentative resolutions below. Items marked `[TENTATIVE — confirm]` need author verification (especially IRB/UKB IDs) before Adobe paste / manuscript update.

### 1. Ethics oversight — tentative paste

```
[TENTATIVE — confirm committee names and protocol IDs]
Analyses of Mount Sinai Data Warehouse (MSDW) electronic health records were conducted under Icahn School of Medicine at Mount Sinai Institutional Review Board oversight / approval (protocol ID: REPLACE_WITH_MS_IRB_ID). UK Biobank analyses used de-identified data under UK Biobank ethics approval and participant consent for research use, accessed under application REPLACE_WITH_UKB_APPLICATION_ID. This work did not involve prospective recruitment; only secondary analysis of existing records. Full ethics details will be stated in the manuscript Methods.
```

Still required after confirm: copy the finalized sentence into manuscript Methods.

### 2. Software / model version pins — tentative

```
ChemBERTa (Hugging Face / DeepChem pretrained SMILES encoder as used for LinkD-Bind training; confirm checkpoint ID, e.g. seyonec/ChemBERTa-zinc-base-v1 or equivalent);
ESM2 (Meta protein LM; confirm size, e.g. esm2_t33_650M_UR50D);
RDKit ≥2022.09 (confirm exact); Open Babel ≥3.1; AutoDockTools / MGLTools as installed for PDBQT prep;
PDB2PQR ≥3.x; FPocket; P2Rank; Smina (AutoDock Vina fork; confirm build);
Python 3.12; pandas≥2.0, numpy≥1.24, scipy≥1.11, matplotlib≥3.7, seaborn≥0.13 (For_Reviewer/requirements-repro.txt).
```

### 3. Corresponding author / last-updated date — tentative

| Field | Value |
|-------|--------|
| Corresponding author(s) | Kuan-lin Huang |
| Last updated by author(s) | 2026-07-26 |

*(Cover letter dated 2026-07-07; use either submission or fill date.)*

### 4. Statistics checkboxes — tentative confirmation

Retain existing Confirmed / n/a selections. Figure/table legends and Methods report sample sizes (n), two-sided Pearson and logistic tests, Benjamini–Hochberg FDR, odds ratios with 95% CIs, and Bind metrics (RMSE, Pearson *r*). No checkbox changes unless final legends diverge.

---

## Header

| Field | Paste |
|-------|--------|
| Corresponding author(s) | Kuan-lin Huang |
| Last updated by author(s) | 2026-07-26 |

---

## Statistics

Confirm that the following are present in figure/table legends, main text, or Methods (match current PDF fill):

| Item | Selection |
|------|-----------|
| Exact sample size (n) for each group/condition | **Confirmed** |
| Distinct samples vs repeated measures statement | **Confirmed** |
| Statistical test(s) and one-/two-sided | **Confirmed** |
| Description of all covariates tested | **Confirmed** |
| Assumptions / corrections (normality, multiple comparisons) | **Confirmed** |
| Full description of statistical parameters (central tendency + variation / CIs) | **Confirmed** |
| Null hypothesis testing: test statistic, CIs, effect sizes, df, *P* | **Confirmed** |
| Bayesian analysis (priors, MCMC) | **n/a** (no Bayesian analyses) |
| Hierarchical / complex designs | **n/a** (no hierarchical mixed models as primary reporting) |
| Effect sizes (e.g. Cohen’s *d*, Pearson’s *r*) and how calculated | **Confirmed** |

---

## Software and code

### Data collection

```
No custom software was used to generate primary experimental measurements. Public and institutional datasets were obtained from their providers and processed with standard open-source tools and custom LinkD scripts (https://github.com/Huang-lab/LinkD). Sources include BindingDB (2025-03), Therapeutics Data Commons Davis and KIBA binding-affinity benchmarks (https://tdcommons.ai/), UniProt reference proteomes, Protein Data Bank (PDB) structures, ChEMBL, Open Targets, GDSC/PRISM drug-response and CRISPR dependency resources, the Mount Sinai Data Warehouse (MSDW; OMOP EHR), and UK Biobank linked health records. Interactive queries use the public LinkD-Agent interface (https://linkd-agent.net/). Individual-level EHR were accessed under institutional data-use agreements; only aggregate statistics are redistributed.
```

### Data analysis

```
Custom LinkD and LinkD-Agent code (https://github.com/Huang-lab/LinkD) was used for diffusion-based drug–target affinity prediction (ChemBERTa drug embeddings — confirm checkpoint, e.g. seyonec/ChemBERTa-zinc-base-v1 or equivalent; ESM2 protein embeddings — confirm size, e.g. esm2_t33_650M_UR50D; denoising diffusion + MLP/Random Forest prediction head), proteome-scale selectivity scoring, CRISPR–drug concordance analyses, EHR association and propensity-score matching analyses, and multi-evidence agent orchestration. Molecular docking (Supplementary Information) used RDKit ≥2022.09 (MMFF94 conformers; confirm exact version), Open Babel ≥3.1, AutoDockTools/MGLTools, PDB2PQR ≥3.x, FPocket, P2Rank, and Smina (AutoDock Vina fork; confirm build). Statistical and figure analyses used Python 3.12 with pandas≥2.0, numpy≥1.24, scipy≥1.11, matplotlib≥3.7, seaborn≥0.13, and related packages (see For_Reviewer/requirements-repro.txt and repository requirements.txt). LLM APIs (OpenAI / Google Gemini / Anthropic Claude as configured) support agent planning/interpretation only; model weights and API keys are not redistributed. Figure-panel regeneration for review uses the For_Reviewer notebooks (no GPU or network required for packaged panels). [TENTATIVE — confirm checkpoint IDs and exact docking tool versions]
```

---

## Data

### Data availability statement

```
All data used in this study were obtained from publicly available resources or generated as part of this work. Clinical trial-derived drug–target–disease associations, causal gene–disease relationships, and oncogene annotations were obtained from publicly accessible databases, as described in the Methods. Drug–protein binding-affinity and selectivity predictions generated by LinkD, together with processed drug-response data and aggregate electronic-health-record summary statistics, are available at Zenodo: https://zenodo.org/records/19241152 (DOI: 10.5281/zenodo.19241152). Source code, configuration files, documentation and example queries are available at https://github.com/Huang-lab/LinkD, and the interactive platform is available at https://linkd-agent.net/. Individual-level EHR data cannot be publicly shared because of participant privacy requirements and data-use agreements; only aggregate, de-identified statistical results are provided.
```

*(This text is already present in the PDF datasets field; replace only if you want the longer manuscript wording.)*

---

## Research involving human participants, their data, or biological material

### Reporting on sex and gender

```
Sex was included as a covariate in propensity-score matching and logistic regression models of drug–disease associations in Mount Sinai and UK Biobank EHR analyses (Methods). Sex was determined from EHR/biobank demographic fields. Analyses were not designed or powered for sex-stratified inference as a primary endpoint; where subgroup summaries are reported (e.g. virtual clinical trial panels), they follow the Methods. Gender identity was not separately analysed.
```

### Reporting on race, ethnicity, or other socially relevant groupings

```
Race/ethnicity categories available in the EHR demographic fields were included as covariates in propensity-score estimation for Mount Sinai drug–disease association analyses (Methods). Categories follow the coding present in the source EHR/biobank; no new social classifications were constructed. These variables were used for confounding control, not as primary effect modifiers unless noted in figure/table legends.
```

### Population characteristics

```
Two observational cohorts were analysed: (1) Mount Sinai Data Warehouse OMOP-formatted EHR (cancer cases defined by ICD-9/10 malignant neoplasm codes with specificity rules; controls without cancer diagnosis and ≥1 year follow-up); (2) UK Biobank participants (n = 501,978) with linked primary care, diagnostic, and hospital data. Across MSDW and UKB drug–disease analyses the study comprised approximately 11.5 million individuals, 1,394 compounds, and 1,783 diseases (Methods). Age, sex, and race/ethnicity were used for matching/adjustment as described. Prostate cancer incidence analyses for β-blockers used the cohorts and exposure definitions detailed in Methods and figure legends.
```

### Recruitment

```
No prospective recruitment was performed. This was a secondary analysis of existing Mount Sinai Health System EHR (MSDW) and UK Biobank data under institutional data-use agreements. Cohort entry, index dates, exposure, and outcome definitions are described in Methods (Disease cohort definition using electronic health records; Drug–disease association analysis in EHR). Selection into analyses required meeting exposure/outcome count thresholds (e.g. >5 disease cases among exposed for model stability).
```

### Ethics oversight

```
[TENTATIVE — confirm committee names and protocol IDs]
Analyses of Mount Sinai Data Warehouse (MSDW) electronic health records were conducted under Icahn School of Medicine at Mount Sinai Institutional Review Board oversight / approval (protocol ID: REPLACE_WITH_MS_IRB_ID). UK Biobank analyses used de-identified data under UK Biobank ethics approval and participant consent for research use, accessed under application REPLACE_WITH_UKB_APPLICATION_ID. This work did not involve prospective recruitment; only secondary analysis of existing records. Full ethics details will be stated in the manuscript Methods.
```

---

## Field-specific reporting

**Select:** Life sciences

---

## Life sciences study design

### Sample size

```
No a priori power calculation determined the computational sample sizes. Binding-affinity benchmarks used the full BindingDB, Davis, and KIBA datasets with 8:1:1 train/validation/test splits under random, cold-drug, and cold-protein regimes (Methods). Selectivity and docking evaluations used the LinkD proteome-scale prediction panel (14,981 drugs × 20,385 human targets) and docking subsets described in Results/SI. CRISPR–drug concordance required ≥15 matched cell lines per drug–target pair. EHR drug–disease pairs required >5 disease cases among exposed individuals. Cell viability assays used LNCaP cultures sized as described in Methods (2.5 × 10³ cells/well; eight wells per condition). Sample sizes are reported in figure legends, tables, and Methods.
```

### Data exclusions

```
Drug–target pairs lacking unambiguous target mapping or valid chemical structures were excluded from affinity modelling. CRISPR concordance excluded pairs with fewer than 15 matched cell lines. In EHR analyses, individuals with disease documented before first drug exposure were excluded; drug–disease pairs below the >5 exposed-case threshold were excluded. Binding-affinity and benchmark filtering criteria are described in Methods and Supplementary Table S1.
```

### Replication

```
LinkD-Bind benchmark results are reported as means over five independent runs with different random seeds. Cell growth (MTT) experiments were performed in biological duplicates with eight technical wells per condition. EHR associations that passed FDR thresholds were further assessed with 10-fold permutation of exposure labels within matched cohorts. Computational figure panels can be regenerated from packaged extracts in the For_Reviewer package (execute_all.py).
```

### Randomization

```
For affinity benchmarks, drug–target pairs (or drugs/proteins in cold splits) were assigned to train/validation/test sets as described in Methods. EHR analyses used propensity-score matching (1:2 exposed:unexposed) based on age, sex, and race/ethnicity rather than experimental randomization. Observational EHR analyses do not use random treatment assignment. Cell-culture wells were allocated to treatment conditions as described in Methods; no clinical trial randomization was performed.
```

### Blinding

```
Blinding was not applicable to the computational modelling, docking, or observational EHR analyses. Experimental cell-viability plate reading was not formally blinded; treatments were applied as labelled conditions described in Methods.
```

---

## Behavioural & social sciences / Ecological sections

Leave blank (Life sciences selected). Do not enter “n/a”.

---

## Reporting for specific materials, systems and methods

### Materials & experimental systems

| Item | Involved? |
|------|-----------|
| Antibodies | **No** (n/a) |
| Eukaryotic cell lines | **Yes** |
| Palaeontology and archaeology | **No** |
| Animals and other organisms | **No** |
| Clinical data (clinical trials / CONSORT) | **No** — observational EHR only; not a clinical trial |
| Dual use research of concern | **No** |
| Plants | **No** |

### Methods

| Item | Involved? |
|------|-----------|
| ChIP-seq | **No** |
| Flow cytometry | **No** |
| MRI-based neuroimaging | **No** |

---

## Eukaryotic cell lines

### Cell line source(s)

```
Human prostate cancer LNCaP cells were obtained from ATCC (Manassas, VA).
```

### Authentication

```
Cells were authenticated by human short tandem repeat (STR) profiling.
```

### Mycoplasma contamination

```
Mycoplasma testing was performed using the MycoAlert PLUS Assay. Cells used in reported experiments tested negative for Mycoplasma contamination.
```

### Commonly misidentified lines (ICLAC)

```
LNCaP is not listed as a commonly misidentified cell line in the ICLAC register. No commonly misidentified lines were used.
```

---

## Sections not used in this study

Leave the following modules blank (not involved): Antibodies; Palaeontology; Animals; Clinical data (trial registration/CONSORT); Dual use research of concern; Plants; ChIP-seq; Flow cytometry; MRI.

---

## Notes for Adobe fill

1. Open `docs/nr-reporting-summary-ChengWang.pdf` in Adobe Reader (not Preview/Chrome).
2. Paste free-text blocks above into the matching fields.
3. Tick Life sciences; tick Eukaryotic cell lines under materials; leave other materials/methods unticked (n/a).
4. Replace `REPLACE_WITH_MS_IRB_ID` / `REPLACE_WITH_UKB_APPLICATION_ID` and confirm ChemBERTa/ESM2/docking versions before final submission.
5. After ethics text is finalized, add the same sentence to manuscript Methods.
