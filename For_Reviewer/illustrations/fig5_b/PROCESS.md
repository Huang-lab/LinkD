### Process (structure panel — pose render not regenerated)

Molecular docking pipeline (Supplementary Information):

1. Drug preparation — RDKit MMFF94 conformers → Open Babel MOL2 → AutoDockTools Gasteiger charges.
2. Protein preparation — PDB retrieval → PDB2PQR (pH 7.4).
3. Binding-site detection — FPocket → P2Rank rescoring; top-5 pockets.
4. Docking — Smina/AutoDock Vina against each pocket.

**Panel b** shows propranolol docked into ADRB2 (PDB 2RH1); caption reports AutoDock Vina score **−8.0 kcal/mol**.
No PyMOL session file is packaged; the published illustration is shown below.
