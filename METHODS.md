# Repository methods

This document describes the implementation represented by this repository. The
submitted manuscript and its frozen PDFs remain the authority for the
scientific analyses and submitted figure inventory.

## LinkD data layers

LinkD exposes four read-only analysis layers:

- **LinkD-Bind:** predicted drug–target binding affinities and per-target
  summaries.
- **LinkD-Select:** drug selectivity metrics and the UMAP representation.
- **LinkD-Pheno:** aggregate Mount Sinai and UK Biobank drug–disease
  associations.
- **LinkD-Agent:** an LLM planner that calls allowlisted query operations over
  the preceding layers.

The application loader reads CSV tables into pandas and accesses the
target-centric binding collection from 100 Parquet chunks. Large CSV inputs can
be sampled at server start when `load_full_data=False`; target-centric Parquet
data are loaded only for relevant queries. Drug IDs, gene symbols, and
disease/ICD fields are normalized by the query functions in
`agent/database_query_module.py`.

## Public application

The current application is a FastAPI backend with a React/TypeScript frontend.
Requests to LinkD-Agent are stateless. A planning request contains a provider,
an allowlisted model, an optional transient API key, and a query of at most
2,000 characters. The returned plan contains at most six consecutively
numbered steps and only allowlisted LinkD data sources. Execution receives that
validated plan and the same transient provider configuration.

API keys are not stored in process-global state, response history, or
server-generated download files. Result tables are returned in the active
response and CSV files are created in the browser. LLM routes are rate-limited;
pagination and search strings are bounded; CORS is limited to configured
development origins (same-origin production requests require no CORS header).

The original historical interface used Gradio, but its exact historical
version was not retained. That interface is not part of the current runnable
application.

## Figure reproduction

`For_Reviewer/notebooks/Data_Preparation.ipynb` resolves the latest version of
[Zenodo concept DOI 10.5281/zenodo.19241151](https://doi.org/10.5281/zenodo.19241151),
downloads `LinkD_Figure_Reproduction_Data.zip`, verifies Zenodo's checksum and
the bundle's internal SHA-256 manifest, rejects unsafe or duplicate ZIP paths,
and installs `data/` and `static/` atomically.

Each Figure 1–6 and Figure S1–S6 notebook is self-contained: it loads the named
aggregate table directly with pandas, displays the input, asserts
manuscript-defining values, performs visible transformations, constructs the
Matplotlib figure, and exports PDF, PNG, and the plotted CSV. Submitted
schematics and pose images are preserved as static assets with provenance.
Figure 6 contains submitted panels 6a–b only.

The panel tables are aggregate and non-identifiable. Author-side extraction and
archive validation live under `scripts/reviewer_data/` and are not imported by
the reviewer notebooks.

## Supplementary agent evaluation

`benchmark/` is a supplementary evaluation harness for LinkD-Agent, not a
submitted Figure 6c panel. It defines seven headline tasks (T1–T7) against
external gold standards and two coverage/ontology diagnostics. The retained
task fixtures, prediction records, and summary JSONL files allow the checked-in
report to be audited and regenerated. LLM-backed results are model- and
date-dependent; they must not be interpreted as guarantees of application
accuracy.

## Historical analysis software

The evidence-backed historical software paragraph, including explicitly
unrecorded versions, is maintained in
`docs/_author/nr-reporting-summary-ANSWERS.md`. In summary, archived records
identify Python 3.12, PyTorch 2.5.1+cu124, scikit-learn 1.6.0, XGBoost 2.1.3,
NumPy 1.26.4, pandas 2.2.2, the
`seyonec/ChemBERTa-zinc-base-v1` and
`facebook/esm2_t33_650M_UR50D` checkpoints, and AutoDock Vina 1.1.2. Missing
historical pins are reported as not recorded rather than inferred from a
current environment.

## Interpretation

LinkD is for research use only. EHR associations are observational and do not
establish causality. Predicted binding, selectivity, and LLM-generated
summaries require independent experimental, statistical, and clinical
validation.
