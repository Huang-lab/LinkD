# Nature Research Code and Software Submission Checklist — draft answers

Paste into [`nr-software-policy.pdf`](nr-software-policy.pdf) (**nature research | software submission checklist**, June 2017) using **Adobe Reader**.  
Companion guidance: https://www.nature.com/documents/GuidelinesCodePublication.pdf  
Sources: manuscript Code availability, root `README.md`, `For Reviewer/`, Zenodo deposit.

---

## Gaps to resolve before pasting (authors)

Tentative resolutions below. Items marked `[TENTATIVE — confirm]` need author verification. Default code license: **MIT**.

### 1. LICENSE — tentative paste

```
LinkD source code is released under the MIT License (see LICENSE in https://github.com/Huang-lab/LinkD). The interactive website https://linkd-agent.net/ is freely accessible in a modern web browser; authors will maintain public access for the foreseeable future. Third-party LLM APIs remain subject to provider terms; API keys and proprietary model weights are not redistributed. Aggregate research data are available under the Zenodo record terms (DOI 10.5281/zenodo.19241152). Individual-level EHR are not redistributable.
```

MIT `LICENSE` is in the repository root (commit `ef481b9`). After push, add one MIT sentence to manuscript Code availability.

### 2. Pinned dependency / tool versions — tentative

```
Python 3.12 (For Reviewer environment.yml; root README).
For Reviewer: pandas≥2.0, numpy≥1.24, matplotlib≥3.7, seaborn≥0.13, openpyxl≥3.1, pyarrow≥14.0, scipy≥1.11, jupyter, nbclient, ipykernel.
Full app (requirements.txt): fastapi≥0.100, uvicorn≥0.23, gradio≥4, openai≥1, google-generativeai≥0.4, anthropic≥0.20, plus core data/viz packages.
Docking (SI): RDKit ≥2022.09, Open Babel ≥3.1, AutoDockTools/MGLTools, PDB2PQR ≥3.x, FPocket, P2Rank, Smina (confirm builds).
OS tested [TENTATIVE]: macOS 15 (darwin) and/or Ubuntu 22.04.
Submission code version: git commit `ef481b96318b2c87920c149d1a134d803095d7b4` (short: `ef481b9`) on local `main` (tip after checklist note: `37e2f9421b87300a91b8bb77e816fe652a31db14`). Push to https://github.com/Huang-lab/LinkD when credentials are available (`git push -u origin main`), then confirm the SHA is visible on GitHub.
Node.js and browser versions: record from author machine when pasting (frontend build + https://linkd-agent.net/).
```

### 3. Typical install / demo run times — tentative (desktop estimates)

| Step | Tentative time |
|------|----------------|
| For Reviewer venv + pip | ~10 minutes |
| Full app install (no Zenodo) | ~30 minutes |
| Zenodo ~16 GB download/extract | ~30–120 minutes (network-dependent) |
| `execute_all.py` on packaged extracts | ~15–45 minutes |
| Live website query | seconds to ~2 minutes |

### 4. Colleague install test — tentative

```
[TENTATIVE] Installation of the For Reviewer package and/or local web app will be tested by a colleague unfamiliar with LinkD prior to or during revision (name/date: REPLACE). Feedback will be used to clarify README steps.
```

### 5. Public access — tentative confirmation

GitHub `https://github.com/Huang-lab/LinkD`, Zenodo `https://zenodo.org/records/19241152`, and `https://linkd-agent.net/` are publicly reachable without institutional login. Local LLM agent features still require user-supplied API keys.

---

## Header

| Field | Paste |
|-------|--------|
| Corresponding author(s) | Kuan-lin Huang |

---

## Required content (check all that apply / describe)

### Compiled standalone software and/or source code

```
Yes — full source code for LinkD / LinkD-Agent (database integration, affinity/selectivity/phenotype/EHR analysis utilities, agent planning, and web interface) is available at:

https://github.com/Huang-lab/LinkD

Interactive deployment: https://linkd-agent.net/

Version details: git commit `ef481b96318b2c87920c149d1a134d803095d7b4` (`ef481b9`) on https://github.com/Huang-lab/LinkD. Repository README lists modules and how to launch the app. MIT License file is at repository root (`LICENSE`).
```

### A small (simulated or real) dataset to demo the software/code

```
Yes — two tiers:

1) Full redistributable prediction and summary tables: Zenodo DOI 10.5281/zenodo.19241152 (https://zenodo.org/records/19241152), including drug–protein affinity/selectivity products, processed drug-response summaries, and aggregate EHR statistics.

2) Figure-panel demo extracts for peer review (no PHI, no GPU): For Reviewer/source_data/ with checksums in For Reviewer/source_data/manifest.csv. Run For Reviewer/notebooks/00_Setup_and_Data_Check.ipynb or For Reviewer/execute_all.py.

Individual-level Mount Sinai / UK Biobank EHR cannot be shared; demos use aggregate odds ratios and VCT summary tables only.
```

### A README file that includes:

#### 1. System requirements

**All software dependencies and operating systems (including version numbers)**

```
Primary platform: macOS or Linux (Windows via WSL also typical). Python 3.10+ (3.12 recommended).

Figure-reproduction environment (For Reviewer):
- pip install -r For Reviewer/requirements-repro.txt
  (pandas≥2.0, numpy≥1.24, matplotlib≥3.7, seaborn≥0.13, openpyxl≥3.1, pyarrow≥14.0, scipy≥1.11, jupyter, nbclient, ipykernel)
- Optional: conda env create -f For Reviewer/environment.yml && conda activate linkd-repro

Full LinkD-Agent application (repository root README):
- conda create -n ttdrug python=3.12; pip install -r requirements.txt
- Node.js for frontend build (interactive_web_server/frontend)
- Optional LLM API keys in .env (Gemini / OpenAI / Anthropic) for agent features

Docking pipeline tools (SI; for regenerating docking—not required for packaged figure extracts): RDKit ≥2022.09, Open Babel ≥3.1, AutoDockTools/MGLTools, PDB2PQR ≥3.x, FPocket, P2Rank, Smina (confirm exact builds).

OS tested [TENTATIVE]: macOS 15 (darwin) and/or Ubuntu 22.04.
```

**Versions the software has been tested on**

```
[TENTATIVE — confirm from author machine] Python 3.12.x; packages at or above For Reviewer/requirements-repro.txt and root requirements.txt minima; Node.js as used for interactive_web_server/frontend build; browsers used to test https://linkd-agent.net/ (Chrome/Safari/Firefox as applicable). Record `pip freeze` / Node version when finalizing.
```

**Any required non-standard hardware**

```
No special hardware for For Reviewer figure regeneration (no GPU, no network). Full model training / proteome-scale docking historically used HPC resources; reviewers can rely on packaged predictions and Zenodo extracts. Optional LLM agent demos need network access to provider APIs.
```

#### 2. Installation guide

**Instructions**

```
Figure reproduction (recommended for reviewers of Results figures):
  cd "For Reviewer"
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements-repro.txt
  jupyter notebook notebooks/00_Setup_and_Data_Check.ipynb
  # or: python execute_all.py

Full agent / web app (repository root):
  conda create -n ttdrug python=3.12 && conda activate ttdrug
  conda install nodejs   # or use system Node
  pip install -r requirements.txt
  cd interactive_web_server/frontend && npm install && npm run build && cd ../..
  cp .env.example .env   # add API keys if testing LLM agent
  cd interactive_web_server && ./start.sh
  # Opens at http://localhost:8000

Data for the full app: python scripts/download_data.py (Zenodo) or manual extract of DOI 10.5281/zenodo.19241152.
```

**Typical install time on a “normal” desktop computer**

```
[TENTATIVE desktop estimates]
For Reviewer venv + pip install: ~10 minutes (network-dependent).
Full app (Python + npm build) without downloading the ~16 GB Zenodo bundle: ~30 minutes.
Zenodo data download/extract (~16 GB): typically ~30–120 minutes depending on bandwidth.
```

#### 3. Demo

**Instructions to run on data**

```
1) Figure panels: from For Reviewer/, run python execute_all.py (or open individual Figure*.ipynb notebooks). Outputs: outputs/figures/ and outputs/source_data/.

2) Agent skill CLI examples (repository):
  .claude/skills/linkd/scripts/linkd target-info EGFR
  .claude/skills/linkd/scripts/linkd evidence CHEMBL553 EGFR --disease "lung cancer" --icd C34 --drug-name Erlotinib

3) Live web demo: https://linkd-agent.net/ (public); or local ./start.sh after install.
```

**Expected output**

```
For Reviewer: PDF/PNG panels under outputs/figures/ and CSV source data under outputs/source_data/; optional validation via python validation/validate_claims.py.
Agent/web: structured multi-evidence summaries (binding, selectivity, CRISPR concordance, EHR odds ratios) for queried drug–target–disease entities.
```

**Expected run time for demo on a “normal” desktop computer**

```
[TENTATIVE desktop estimates]
For Reviewer execute_all.py on packaged extracts: ~15–45 minutes (no GPU). Single-notebook panels usually complete faster.
Live website queries: seconds to ~2 minutes depending on LLM backend.
```

#### 4. Instructions for use

**How to run the software on your data**

```
See repository README.md (Quick Start, Data, Agent Skill) and For Reviewer/README.md, ENVIRONMENT.md, DATA_AVAILABILITY.md, REPRODUCIBILITY.md, MANUSCRIPT_MAP.md.

To analyse new queries against the shipped LinkD tables, use LinkD-Agent (web or CLI) after placing Zenodo extracts in the expected directories. To regenerate manuscript figures from the reviewer package, use only For Reviewer/source_data/ paths (enforced by linkd_repro.paths). Custom docking or full model retraining requires the SI pipeline and training code/data beyond the reviewer extracts.
```

**(OPTIONAL) Reproduction instructions**

```
We encourage reproduction of quantitative figure panels via For Reviewer notebooks and validation/validate_claims.py. Manuscript Methods describe LinkD-Bind training/evaluation, selectivity scoring, CRISPR concordance, EHR logistic regression with propensity-score matching, and agent architecture. SI details the docking pipeline. Packaged panels are numerically aligned with source tables (not necessarily pixel-identical to publication composites).
```

---

## Provide a link to the code in an open source repository (when available)

```
https://github.com/Huang-lab/LinkD

Frozen data products: https://doi.org/10.5281/zenodo.19241152
Interactive tool: https://linkd-agent.net/
```

---

## Manuscript location of complete algorithm / functionality description (pseudocode)

| Location | Check |
|----------|--------|
| Main text | Partial (high-level module description) |
| Methods section | **Yes — primary** (diffusion DTI equations, selectivity, CRISPR concordance, EHR models, agent design, cell assay) |
| Elsewhere (specify) | **Supplementary Information** — molecular docking pipeline (RDKit → Smina); LinkD-Agent benchmark design |

```
Paste: Methods section (Materials and Methods) and Supplementary Information (docking pipeline; agent benchmark). Key operations: ChemBERTa/ESM2 embedding → diffusion latent refinement → affinity regression; proteome-wide selectivity metrics; CRISPR–drug Pearson concordance with BH-FDR; EHR logistic OR with 1:2 propensity-score matching; LLM planner over structured LinkD databases.
```

---

## License of use

```
LinkD source code is released under the MIT License (see LICENSE in https://github.com/Huang-lab/LinkD). The interactive website https://linkd-agent.net/ is freely accessible in a modern web browser; authors will maintain public access for the foreseeable future. Third-party LLM APIs remain subject to provider terms; API keys and proprietary model weights are not redistributed. Aggregate research data are available under the Zenodo record terms (DOI 10.5281/zenodo.19241152). Individual-level EHR are not redistributable.
```

---

## Additional notes (not formal checklist fields)

- Nature guidelines ask for a single zip **or** a link where editors/reviewers can access all required content. Prefer the GitHub + Zenodo + For Reviewer package links above rather than uploading a huge zip if editors accept URLs.
- Code availability statement already in the manuscript (GitHub + linkd-agent.net; LLM keys/weights excluded) — add MIT once the LICENSE file is on GitHub.
- Colleague install test: record name/date in Gaps item 4 when done.
- Examples of well-structured packages cited on the form (for author reference only): neurodata MGC/LOL GitHub repos; Nature/NBT software supplements listed on the PDF.

---

## Adobe fill checklist

1. Open `docs/nr-software-policy.pdf` in Adobe Reader.
2. Enter corresponding author.
3. Tick / describe each Required content item using the blocks above.
4. Paste repository URL, Methods/SI location, and MIT license text (after LICENSE exists on GitHub).
5. Optionally attach or link the `For Reviewer/` tree as the peer-review demo bundle.
