# Figure reproduction for reviewers

The submitted LinkD figures are reproduced with the notebooks in
`For_Reviewer/` and one Zenodo download,
`LinkD_Figure_Reproduction_Data.zip`, published under stable concept DOI
[10.5281/zenodo.19241151](https://doi.org/10.5281/zenodo.19241151).

```bash
git clone https://github.com/Huang-lab/LinkD.git
cd LinkD/For_Reviewer
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter lab notebooks
```

Run `notebooks/Data_Preparation.ipynb` first. Then run any main notebook
`Figure1.ipynb`–`Figure6.ipynb` or supplementary notebook
`FigureS1.ipynb`–`FigureS6.ipynb` with **Restart Kernel and Run All**.

Every computational notebook directly loads the distributed CSV files,
validates manuscript invariants, performs visible pandas transformations,
constructs its Matplotlib plots, and exports PDF, PNG, and plotted CSV files
under `For_Reviewer/outputs/`. Static submitted panels are displayed with
provenance notes. No GPU, API key, patient-level EHR data, or access to the
author's `Drug-Repo-scRNA` directory is required.

The live Zenodo version must contain the reproduction ZIP and its `.sha256`
companion before reviewer release. Author extraction and deterministic
packaging commands live under `scripts/reviewer_data/` and
`scripts/prepare_for_reviewer_zenodo.py`, outside the reviewer package.
