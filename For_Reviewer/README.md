# LinkD figure reproduction

This folder is the complete reviewer workflow for the submitted main and
supplementary figures. Every scientific assertion, pandas transformation,
Matplotlib command, and export operation is visible in the notebooks. The
notebooks do not import repository-owned analysis modules.

## Quick start

```bash
cd For_Reviewer
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter lab notebooks
```

Run `notebooks/Data_Preparation.ipynb` first with **Restart Kernel and Run
All**. It resolves the latest version of Zenodo concept DOI
[10.5281/zenodo.19241151](https://doi.org/10.5281/zenodo.19241151), downloads
`LinkD_Figure_Reproduction_Data.zip`, verifies all checksums and schemas, and
installs the inputs under `data/` and `static/`.

The live Zenodo record only needs to contain the ZIP. The notebook checks
Zenodo's published checksum and then verifies every bundled file against the
ZIP's internal SHA-256 manifest. If the ZIP is not published, the notebook can
use `../zenodo_upload/` as a prominently labelled author-only testing fallback.

## Figure notebooks

- `Figure1.ipynb` through `Figure6.ipynb`
- `FigureS1.ipynb` through `FigureS6.ipynb`

Each computational section loads its named CSV with `pd.read_csv()`, displays
the input, checks manuscript invariants, prepares the plotted data, constructs
the figure inline, and directly exports PDF, PNG, and CSV files. Submitted
schematics and molecular-pose panels are displayed as static published assets
with provenance notes.

Generated files are written to `outputs/figures/` and
`outputs/source_data/`. The installed `data/`, `static/`, and generated
`outputs/` directories can be recreated by rerunning the notebooks.

Figure 6 contains only submitted panels 6a–b; non-submitted panel 6c is
intentionally excluded. All distributed EHR and virtual-clinical-trial inputs
are aggregate and non-identifiable. Licensing, release identifiers,
provenance, checksums, row counts, and schemas are installed under `data/`.
