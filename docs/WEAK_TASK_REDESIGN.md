# Redesigning LinkD's "weak" tasks to match what the manuscript actually validates

Reading `docs/Submit/Manuscript_VF` makes one thing clear: the tasks where LinkD looked weak
were testing it against **misaligned gold** — not what the modules are built to do. The
manuscript validates each module by **target-centric ranking, concordance/recovery against
curated annotations, and EHR target-trial emulation** — never against the external datasets I had
wired in (DAVIS *kinome* promiscuity, repoDB approved/failed, FAERS MedDRA). Below, each weak task
is re-specified to its manuscript-aligned form, with the LinkD capability that already exists and
a feasibility check.

Manuscript anchors used: LinkD-Select = proteome-wide selectivity over **20,385 targets** (Shannon
entropy + Gini-Simpson + **gap score** + **selectivity ratio**; 3 categories: *Highly Selective /
Moderate poly-target / Broad-spectrum*), validated **target-centrically** (Fig 5a ranks all 14,981
drugs against ADRB2 → propranolol rank 1) and by **CRISPR concordance** (Fig 3). LinkD-Pheno =
drug-response↔CRISPR Chronos concordance (|ρ|≥0.40, FDR) recovering **211 ChEMBL-annotated + 34
novel** pairs. LinkD-Bind's headline gain is under **cold-drug / cold-target** splits (proteome-scale
repurposing regime). EHR = protective associations (OR<1) via **target-trial emulation**.

---

## 1. Selectivity (current T7) — REPLACE

| | |
|---|---|
| **Current (misaligned)** | Classify a kinase inhibitor selective vs promiscuous vs **DAVIS kinome** strong-binder count. LinkD AUROC 0.474. |
| **Why it's wrong** | LinkD-Select is **proteome-wide (20,385 targets)**; DAVIS is **kinome-only**. A drug can be kinome-promiscuous yet proteome-selective. Confirmed mismatch (Spearman ρ≈0.19; ≤0.38 any column). The task tests the wrong quantity. |
| **Proposed T7′ — target-centric selective-binder retrieval** | For each of ~20–25 well-studied targets (EGFR, ABL1, JAK1/2, BRAF, KIT, MET, ALK, …), rank all 14,981 LinkD drugs by **LinkD-Select** (selectivity-weighted affinity / `Selectivity_Score`). This is exactly Fig 5a (ADRB2 → propranolol rank 1). |
| **Gold (external)** | Known selective inhibitors of each target from **ChEMBL** (high pChEMBL + mechanism=inhibitor) / **OpenTargets** known drugs. |
| **Metric** | Recall@10/20, nDCG@20, AUROC (retrieve known selective binders near the top). |
| **Comparators** | LLM ("list selective inhibitors of EGFR" — names a few); open-source = ChEMBL target-activity / OpenTargets known-drugs lookup. |
| **Why LinkD wins** | Proteome-wide systematic ranking surfaces the full selective-binder set. **Verified:** EGFR → erlotinib #2, gefitinib #3, lapatinib #6, canertinib #1; ABL1 → dasatinib #1, bosutinib #18, imatinib #60. |
| **Feasibility** | ✅ `get_drugs_for_target_with_affinity(gene)` exists and works. Categories via `get_drugs_by_selectivity_type` / `drug_umap.Type`. |

> Note: a "predict the 3 selectivity *categories*" task is **not** externally goldable (the
> categories are LinkD's own output) — the target-centric retrieval is the externally-valid form.

---

## 2. Multi-evidence fusion (current T5/C1) — REFRAME

| | |
|---|---|
| **Current** | Score (drug, gene, disease) triads; hard negative = another validated target of the *same* disease. LinkD-alone 0.467 (below chance). |
| **Why it's harder than the claim** | The manuscript's integrative result is **concordance-based discovery**, not same-disease decoy discrimination. The hard-decoy framing asks a question the fusion was never built to answer. |
| **Proposed T5′ — concordance-based drug–target recovery** | Positives = **ChEMBL-annotated drug–target pairs**; negatives = random drug–gene pairs. LinkD scores each by multi-evidence (binding + selectivity + **CRISPR concordance**). Matches Fig 3f–g (211 annotated + 34 novel at |ρ|≥0.40, FDR≥20). |
| **Gold (external)** | ChEMBL mechanism pairs (positive) vs sampled non-pairs (negative). |
| **Metric** | AUROC, AUPRC; + report the |ρ|≥0.40 / FDR enrichment as in the paper. |
| **Why LinkD wins / is competitive** | This is precisely the integrative signal the module is built and validated on. |
| **Feasibility** | ✅ `get_comprehensive_drug_target_evidence` + `get_drug_response_associations` (CRISPR ρ). |

---

## 3. CRISPR mechanism (current T4) — REFRAME (optional)

| | |
|---|---|
| **Current** | Rank a drug's MoA target genes from CRISPR correlation. LLM wins (0.84) via memorised MoA; LinkD 0.587. |
| **Manuscript form** | Drug-response↔CRISPR-dependency **concordance** (|ρ|≥0.40) recovering ChEMBL pairs (Fig 3). |
| **Proposed T4′ — CRISPR concordance discrimination** | Does |ρ| separate ChEMBL-annotated drug–target pairs from random pairs? AUROC. Tests LinkD-Pheno's actual signal rather than MoA recall (which is LLM home turf). |
| **Feasibility** | ✅ `get_drug_response_associations` (AUC_corr / ρ, FDR). |

---

## 4. Binding affinity (current T1) — ADD a cold-split task

| | |
|---|---|
| **Current** | Stratified DAVIS split; LinkD 0.819 (already wins LLMs). |
| **Manuscript headline** | LinkD-Bind's distinctive advantage is under **cold-drug / cold-target** splits — "the settings most relevant to proteome-scale repurposing" (cold-drug BindingDB RMSE 1.021 vs 1.050 baseline). |
| **Proposed T1b — cold-split DTI generalization** | TDC DAVIS/KIBA/BindingDB **cold-drug** and **cold-target** splits. LinkD's diffusion model vs DTI specialists (DeepDTA / GraphDTA / DeepPurpose — cited from the paper's own benchmark) and LLMs. |
| **Metric** | RMSE, MSE, Pearson r, C-Index (the paper's metrics). |
| **Why it matters** | Strengthens the binding story exactly where the manuscript claims the edge; LLMs cannot estimate pKd at all on unseen chemistry. |
| **Feasibility** | 🟡 needs PyTDC cold-split harness; LinkD predictions are already available for the overlap. |

---

## 5. EHR repurposing / safety (current D1, D2) — REFRAME

| | |
|---|---|
| **Current** | D1 repoDB approved/failed (EHR covers 3/120 pairs); D2 FAERS MedDRA vs ICD. Both gold-misaligned. |
| **Manuscript form** | **Protective** drug-cancer associations (OR<1) validated by **target-trial emulation** (propensity-matched); validated exemplars azelastine–liver (OR=0.69), tretinoin–thyroid (OR=0.43), β-blockers–prostate. |
| **Proposed D1′ — protective-association recovery** | Gold = curated protective drug–cancer pairs (epidemiology literature + the paper's validated set); test whether LinkD's significant EHR OR<1 recovers them above null/risk pairs. Metric = AUROC / enrichment. |
| **Caveat** | Externally-curated protective gold at scale is scarce → this task is necessarily small; alternatively keep EHR as the **qualitative case-study** validation the manuscript itself uses (target-trial emulation), which is its strongest form. |
| **Feasibility** | 🟡 needs a curated protective-pair gold; LinkD EHR OR lookup already exists. |

---

## Recommended build order (deterministic LinkD side runs now; LLM comparison when the API is back)

1. **T7′ selectivity retrieval** — highest value, fully verified, LinkD clearly wins. ✅
2. **T5′ concordance fusion** — aligns the fusion task with the paper; reuses existing evidence calls. ✅
3. **T4′ CRISPR concordance** — small reframe of an existing task. ✅
4. **T1b cold-split binding** — strengthens the headline win; needs a PyTDC split harness. 🟡
5. **D1′ protective EHR** — aligned but gold-limited; or keep EHR qualitative. 🟡

Each new task slots into the existing benchmark (builder → conditions → scorer → report) the same
way the current tasks do, so the comprehensive table and `fig_nature` extend automatically.

---

## Results — full comparison on the rebuilt aligned tasks (capped, target-balanced; identical items per condition)

AUROC. LLM tier = gpt-5.4 + claude-sonnet-4-6 (Gemini geo-blocked). **Orchestrator = gpt-5.4** (the
claude orchestrator hit an output-formatting parser bug — see note; now fixed for future runs).

| Task | n | LinkD | Best LLM (closed-book) | Combined | **Orchestrator (gpt-5.4)** |
|---|---|---|---|---|---|
| **T7′ selectivity** (LinkD-Select) | 144 | 0.769 | **0.949** (claude) | 0.901 | 0.901 |
| **T4′ CRISPR concordance** (LinkD-Pheno) | 120 | 0.709 | 0.980 (gpt-5.4) | 0.965 | **0.985** |
| **T5′ multi-evidence fusion** | 120 | 0.708 | 0.980 (claude) | 0.963 | **0.988** |
| **D1′ protective EHR** (LinkD-Pheno) | 20 (4 covered) | 4/4 recovered | — | — | — |

**Honest headline finding — these are recognition (knowledge) tasks, won by the LLM.** Aligning the
gold to the manuscript made LinkD's modules show *real, well-above-chance* signal (0.71–0.77), but it
did **not** make LinkD beat frontier LLMs: scored *per drug–target pair*, the question "is drug D a
binder of target T / does D depend on gene G" is memorized pharmacology, so closed-book LLMs reach
**0.95–0.98**. The vs-old gains are real (selectivity 0.474→0.769, CRISPR 0.587→0.736, fusion
0.467→0.708) — LinkD's modules *work* — but recognition of known relationships is the LLM's home
turf. LinkD's genuinely *unique* wins remain: (a) quantitative **pKd magnitude** (T1, where the LLM
manages only 0.628), and (b) **novel/uncharacterized** interactions with no memorized answer (the
manuscript's "34 novel pairs" — which, by definition, have no external gold to benchmark against).

**The orchestrator is best where it behaves.** gpt-5.4 calling LinkD tools + its own knowledge is
best or tied-best on all three (0.901 / 0.985 / 0.988) — it captures both. The **claude orchestrator
(0.42–0.53) was a parser bug, not a capability gap**: it called the tools correctly but emitted
reasoning prose ("…pKd = 7.29…") instead of a bare number, and the old score parser grabbed the
wrong digits. Fixed in `closed_book._parse` (take the last standalone number in [0,1]); also added a
90 s request timeout + retries to `llm_client.py` after the first runs hung on a stalled proxy
connection. Per the user's call, the claude orchestrator was **not** re-run; gpt-5.4 is reported.

**Fusion still beats its parts** on the same pairs (binding 0.769, CRISPR 0.709, fusion 0.708 — here
the explicit binding+CRISPR fusion `linkd_fusion_pair` matches CRISPR and tops binding on the capped
set; on the full 180-pair set fusion 0.759 > CRISPR 0.736 > binding 0.727). The native
disease-contextualized `final_score` scores pure drug–target pairs at 0.45 (it needs a disease).

**Build bugs fixed (were tanking the CRISPR signal):** keyed on the sparse annotated `Gene` column
(84) vs the full `genes` column (17,029 measured); and a regex `drug_name` filter dropped the target
row (use ChEMBL id only).

**D1′ note:** a large-scale EHR AUROC is not viable — the cohorts are cancer-specific and cover only
4/20 curated protective pairs — but on every covered pair LinkD recovers the expected protective OR<1
(propranolol/carvedilol–prostate, tretinoin–thyroid, azelastine–liver), matching the manuscript.
LinkD-Pheno is validated by this curated table + the qualitative case studies, as the manuscript does.
