"""Show process + published illustration when a panel cannot be recomputed."""
from __future__ import annotations

from IPython.display import Markdown, Image, display
from pathlib import Path

from . import paths

PROCESS_TEXT = {
    "fig1_a": """
### Process (schematic — not regenerated from data)

LinkD integrates four modules:

1. **LinkD-Bind** — ChemBERTa (SMILES) + ESM2 (protein) → shared latent space → diffusion refinement → hybrid MLP/RF head predicting proteome-wide pKd.
2. **LinkD-Select** — entropy / gap / selectivity-ratio metrics → composite selectivity score.
3. **LinkD-Pheno** — drug-sensitivity × CRISPR dependency concordance across cancer cell lines; EHR odds/hazard ratios in Mount Sinai + UK Biobank.
4. **LinkD-Agent** — natural-language queries decomposed into auditable analytical steps.

The published composite panel below is the manuscript figure (Illustrator/Photoshop assembly).
""",
    "fig3_a": """
### Process (schematic — not regenerated from data)

LinkD-Pheno validation:

1. Intersect drug-response AUC profiles and CRISPR Chronos dependency scores across shared cell lines.
2. For each drug–gene pair compute Pearson concordance across cell lines.
3. Retain statistically significant concordant pairs as the validated drug–target set.
4. Stratify discoveries by LinkD-Select confidence tier and pathway class.

Published schematic shown below.
""",
    "fig4_a": """
### Process (schematic — not regenerated from data)

EHR validation framework:

1. Map drug exposures and disease outcomes in Mount Sinai (OMOP) and UK Biobank.
2. Propensity-score–matched logistic regression → odds ratios for drug–disease pairs.
3. Join LinkD drug–target predictions and Open Targets gene–disease scores.
4. Visualize triangulated drug–target–disease networks.

Patient-level records are not distributed; summary OR tables regenerate quantitative panels.
Published schematic shown below.
""",
    "fig5_b": """
### Process (structure panel — pose render not regenerated)

Molecular docking pipeline (Supplementary Information):

1. Drug preparation — RDKit MMFF94 conformers → Open Babel MOL2 → AutoDockTools Gasteiger charges.
2. Protein preparation — PDB retrieval → PDB2PQR (pH 7.4).
3. Binding-site detection — FPocket → P2Rank rescoring; top-5 pockets.
4. Docking — Smina/AutoDock Vina against each pocket.

**Panel b** shows propranolol docked into ADRB2 (PDB 2RH1); caption reports AutoDock Vina score **−8.0 kcal/mol**.
No PyMOL session file is packaged; the published illustration is shown below.
""",
    "fig5_c": """
### Process (structure panel — pose render not regenerated)

Same docking pipeline as panel b.

**Panel c** shows carvedilol docked into ADRB2 (PDB 2RH1); caption reports AutoDock Vina score **−9.9 kcal/mol**.
Published illustration shown below.
""",
    "fig6_a": """
### Process (schematic — not regenerated from data)

LinkD-Agent architecture: natural-language query → planner → modular tools (selectivity, gene dependency, EHR effects) via a Model Context Protocol–style tool server → structured execution trace → multi-evidence summary.

Published schematic shown below.
""",
    "fig6_b": """
### Process (schematic — not regenerated from data)

Example agent plan: a natural-language oncology query is decomposed into ordered function calls (binding, selectivity, CRISPR concordance, EHR), executed step-by-step, and summarized into a drug-repurposing score.

Published illustration shown below.
""",
    "figS1": """
### Process (schematic — not regenerated from data)

Supplementary Figure S1 summarizes BindingDB / Davis / KIBA dataset preparation, random / cold-drug / cold-protein splits, and evaluation metrics used for LinkD-Bind benchmarking.

Published schematic shown below.
""",
    "figS6_a": """
### Process (schematic — not regenerated from data)

Autonomous virtual-clinical-trial agent workflow: protocol designer → cohort builder → matching → outcome definition → estimation → reporting.

Published schematic shown below.
""",
}


def show_panel(panel_id: str, title: str | None = None) -> None:
    """Display process markdown and first image found in illustrations/<panel_id>/."""
    md = PROCESS_TEXT.get(panel_id, f"### Process\nNo process text registered for `{panel_id}`.")
    if title:
        display(Markdown(f"## {title}\n{md}"))
    else:
        display(Markdown(md))
    d = paths.illustration_dir(panel_id)
    if not d.exists():
        display(Markdown(f"*Illustration folder missing: `{d}`*"))
        return
    imgs = sorted([*d.glob("*.jpg"), *d.glob("*.png"), *d.glob("*.pdf")])
    # Prefer raster for notebook display
    rasters = [p for p in imgs if p.suffix.lower() in {".jpg", ".jpeg", ".png"}]
    pick = rasters[0] if rasters else (imgs[0] if imgs else None)
    if pick is None:
        display(Markdown(f"*No illustration file in `{d}`*"))
        return
    if pick.suffix.lower() == ".pdf":
        display(Markdown(f"*PDF illustration:* `{pick.name}` (open from `illustrations/{panel_id}/`)"))
    else:
        display(Image(filename=str(pick), width=720))
    process_md = d / "PROCESS.md"
    if not process_md.exists():
        process_md.write_text(md.strip() + "\n", encoding="utf-8")
