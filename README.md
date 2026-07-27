# LinkD: An Agentic Platform for Drug Repurposing

LinkD unifies molecular, phenotypic, and clinical evidence for cancer drug discovery —
binding affinity and selectivity, CRISPR drug-response, and EHR associations — behind an
AI agent (**LinkD-Agent**) that plans and executes multi-step analyses from natural language.

**License:** [MIT](LICENSE)  
**Code:** [https://github.com/Huang-lab/LinkD](https://github.com/Huang-lab/LinkD)  
**Submission release:** [v1.0-submission](https://github.com/Huang-lab/LinkD/releases/tag/v1.0-submission)  
**Interactive:** [https://linkd-agent.net/](https://linkd-agent.net/)  
**Data:** [Zenodo DOI 10.5281/zenodo.21615191](https://doi.org/10.5281/zenodo.21615191) (~16 GB)

## Live demo

> **URL**: [https://linkd-agent.net/](https://linkd-agent.net/)
>
> **Manuscript figure reproduction (reviewers):** [`For_Reviewer/`](For_Reviewer/) — see
> [docs/FOR_REVIEWER.md](docs/FOR_REVIEWER.md). Oversized panel tables download from Zenodo.
>
> **Figure 6c (LinkD-Agent benchmark):** frozen inputs in
> `For_Reviewer/source_data/benchmark/`; full harness in [`benchmark/`](benchmark/).

## Modules

| Module | Description | Key data |
|--------|-------------|----------|
| **LinkD-Bind** | Drug–target binding affinity explorer | 1,068 targets with pKd, 20K+ binding pairs |
| **LinkD-Select** | Drug selectivity profiling (UMAP) | 14,981 drugs, selectivity scores |
| **LinkD-Pheno** | Phenotype–drug associations from EHR | Mount Sinai + UK Biobank cancer associations |
| **LinkD-Agent** | Multi-step NL analysis agent | OpenAI, Google Gemini, or Anthropic APIs |

## Quick start

```bash
# 1. Environment
conda create -n ttdrug python=3.12
conda activate ttdrug
conda install nodejs

# 2. Dependencies
pip install -r requirements.txt
cd interactive_web_server/frontend && npm install && npm run build && cd ../..

# 3. Optional LLM keys for LinkD-Agent
cp .env.example .env
# Edit .env — GEMINI_FREE_KEY and/or OPENAI_API_KEY / ANTHROPIC_API_KEY / GOOGLE_API_KEY

# 4. Launch
cd interactive_web_server && ./start.sh
# http://localhost:8000
```

Other modes: `./start.sh dev` (hot reload) · `./start.sh gradio` (legacy UI on 7860).

## Data

```bash
# Auto-download (also used on Render)
python scripts/download_data.py

# Or extract Zenodo archives into the project root:
# Database/, DrugTargetMetrics/, EHR_Results/, DrugResponse/, Target_Disease_Association/
```

| Directory | Highlights |
|-----------|------------|
| `Database/` | Oncogene annotations |
| `Target_Disease_Association/` | ChEMBL drug–target–disease; Open Targets causal links |
| `DrugTargetMetrics/` | Selectivity scores; per-target pKd parquet |
| `EHR_Results/` | Mount Sinai + UK Biobank aggregate associations |
| `DrugResponse/` | CRISPR drug-response correlations (PRISM + GDSC) |

Versions: ChEMBL 34 · Mount Sinai / UKB EHR 2024-11 · PRISM/GDSC 2024-Q4 · Open Targets 24.09.

## LinkD-Agent

LinkD-Agent decomposes biomedical questions into tool-using plans over the LinkD database
(binding, selectivity, CRISPR, EHR, clinical-phase evidence) and returns structured
multi-evidence summaries. Use it in the web UI (`/agent`) or via the Python package under
[`agent/`](agent/).

Weighted multi-evidence scoring lives in [`agent/evidence_scoring.py`](agent/evidence_scoring.py)
(weights in [`config/evidence_weights.yaml`](config/evidence_weights.yaml)).

A JSON CLI over the same layers is available at
[`.claude/skills/linkd/scripts/linkd`](.claude/skills/linkd/scripts/linkd):

```bash
.claude/skills/linkd/scripts/linkd target-info EGFR
.claude/skills/linkd/scripts/linkd evidence CHEMBL553 EGFR --disease "lung cancer" --icd C34 --drug-name Erlotinib
```

## Manuscript figures & agent benchmark

| Audience | Path |
|----------|------|
| Reviewers regenerating figures | [`For_Reviewer/`](For_Reviewer/) |
| Fig 6c frozen scores / heat | `For_Reviewer/source_data/benchmark/` |
| Full agent-eval harness (T1–T7) | [`benchmark/`](benchmark/) — see `benchmark/README.md` |

## Deployment (Render)

Frontend `dist/` is committed; Render installs Python deps and serves the prebuilt bundle.

1. Connect the GitHub repo as a web service  
2. **Build:** `pip install -r requirements.txt`  
3. **Start:** `python scripts/download_data.py && cd interactive_web_server/backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT`  
4. Env: `DATABASE_DIR=/opt/render/project/src/data/Database`, `GEMINI_FREE_KEY`, optional other LLM keys  
5. Persistent disk (~20 GB) at `/opt/render/project/src/data`

After frontend source changes, rebuild and commit `interactive_web_server/frontend/dist/`.

Data deposit staging: `bash scripts/prepare_zenodo.sh` (and optionally
`prepare_for_reviewer_zenodo.sh`) → upload to
[DOI 10.5281/zenodo.21615191](https://doi.org/10.5281/zenodo.21615191). Staging folder
`zenodo_upload/` is gitignored and never read by the web server.

## Architecture

```
React frontend  →  FastAPI (/api/*)  →  agent/ (DB query + LLM planner)
                                      →  CSV/Parquet (Zenodo-hosted)
```

## Project structure

```
LinkD/
├── agent/                     # Query module, evidence scoring, LLM planner
├── interactive_web_server/    # FastAPI + React (LinkD-Bind/Select/Pheno/Agent)
├── For_Reviewer/              # Manuscript figure reproduction package
├── benchmark/                 # LinkD-Agent evaluation (Figure 6c)
├── scripts/download_data.py   # Zenodo download
├── config/                    # Evidence weights, etc.
├── requirements.txt
└── render.yaml
```

## API (selected)

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health + loaded datasets |
| `GET /api/overview` | Database statistics |
| `POST /api/binding/search` | Binding landscape |
| `POST /api/selectivity/search` | Selectivity detail |
| `GET /api/ehr/preload` | EHR associations |
| `POST /api/agent/plan` · `/execute` | LinkD-Agent plan + run |

Swagger UI: `http://localhost:8000/docs`

## Configuration

| Variable | Description |
|----------|-------------|
| `PORT` | Server port (default 8000) |
| `DATABASE_DIR` | Path to `Database/` (default `./Database`) |
| `GEMINI_FREE_KEY` | Free-tier Gemini for LinkD-Agent |
| `OPENAI_API_KEY` / `GOOGLE_API_KEY` / `ANTHROPIC_API_KEY` | Optional LLM providers |

## License

MIT License. Source code and data-processing pipelines are freely available for academic use.

## Contact

- **Institution**: Icahn School of Medicine at Mount Sinai
- **Email**: chengwangosu@gmail.com
- **GitHub**: [github.com/Huang-lab/LinkD](https://github.com/Huang-lab/LinkD)
