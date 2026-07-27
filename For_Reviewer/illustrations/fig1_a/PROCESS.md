### Process (schematic — not regenerated from data)

LinkD integrates four modules:

1. **LinkD-Bind** — ChemBERTa (SMILES) + ESM2 (protein) → shared latent space → diffusion refinement → hybrid MLP/RF head predicting proteome-wide pKd.
2. **LinkD-Select** — entropy / gap / selectivity-ratio metrics → composite selectivity score.
3. **LinkD-Pheno** — drug-sensitivity × CRISPR dependency concordance across cancer cell lines; EHR odds/hazard ratios in Mount Sinai + UK Biobank.
4. **LinkD-Agent** — natural-language queries decomposed into auditable analytical steps.

The published composite panel below is the manuscript figure (Illustrator/Photoshop assembly).
