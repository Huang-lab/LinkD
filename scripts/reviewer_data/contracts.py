"""Manuscript-frozen figure contracts.

These constants are transcribed from the submitted figure pages and captions.
They are intentionally small: the numerical observations still come from the
author-side source files, while these contracts fix category order, displayed
labels, and manuscript-version summary values.
"""
from __future__ import annotations

FIGURE_NOTEBOOKS = {
    "data": "Data_Preparation.ipynb",
    **{f"figure{i}": f"Figure{i}.ipynb" for i in range(1, 7)},
    **{f"figure_s{i}": f"FigureS{i}.ipynb" for i in range(1, 7)},
}

RANK_METHODS = [
    "LinkD-Bind",
    "FNN",
    "DCN",
    "MLP",
    "GraphDTA",
    "GCN",
    "Random Forest",
    "XGBoost",
    "DeepPurpose",
    "DeepDTA",
    "GBM",
    "SVR",
    "Linear Regression",
]
RANK_SPLITS = ["Random", "Cold-protein", "Cold-drug"]
RANK_VALUES = [
    [1, 1, 1],
    [2, 2, 6],
    [3, 5, 11],
    [4, 6, 9],
    [5, 12, 4],
    [6, 8, 13],
    [7, 4, 8],
    [8, 3, 2],
    [9, 7, 3],
    [10, 11, 7],
    [11, 9, 5],
    [12, 10, 10],
    [13, 13, 12],
]

FIG1C_MODEL_MAP = {
    "LinkD": "LinkD-Bind",
    "Diffusion": "Diffusion backbone only",
    "FNN": "Head only (no diffusion)",
    "GraphDTA": "GraphDTA",
    "DeepPurpose": "DeepPurpose",
    "DeepDTA": "DeepDTA",
}
MODE_LABELS = {
    "random": "Random",
    "cold_drug": "Cold-drug",
    "cold_protein": "Cold-protein",
}

ROLE_ORDER = ["Oncogene", "TSG", "Both"]
ROLE_COLORS = {"Oncogene": "#E45756", "TSG": "#4C78A8", "Both": "#54A24B"}
RECOVERY = [
    ("top-5%", "Oncogene", 1674, 25.1, 25.6, 32.3),
    ("top-5%", "TSG", 142, 6.3, 11.3, 8.5),
    ("top-5%", "Both", 267, 19.9, 13.1, 19.5),
    ("top-10%", "Oncogene", 1674, 33.6, 35.5, 40.6),
    ("top-10%", "TSG", 142, 12.7, 15.5, 14.1),
    ("top-10%", "Both", 267, 24.7, 19.5, 29.2),
]
DOCKING_ROLE_COUNTS = {"Oncogene": 154, "TSG": 36, "Both": 33}
DOCKING_RECOVERY = {-8.0: 83.6, -7.0: 92.6, -6.0: 95.3}

RADAR_DRUGS = {
    "EGFR": [
        ("Canertinib", "On"),
        ("Gefitinib", "On"),
        ("Afatinib", "On"),
        ("Mifanertinib", "Off"),
        ("Erlotinib", "On"),
    ],
    "JAK1": [
        ("Nintedanib", "Off"),
        ("Ruxolitinib", "On"),
        ("Fedratinib", "Off"),
        ("Midostaurin", "Off"),
        ("Lestaurtinib", "Off"),
    ],
}

LINEAGE_COUNTS = [
    ("Lung", 178),
    ("Blood", 170),
    ("Urogenital system", 104),
    ("Digestive system", 95),
    ("Nervous system", 87),
    ("Aero digestive tract", 76),
    ("Skin", 58),
    ("Breast", 52),
    ("Bone", 38),
    ("Kidney", 34),
    ("Pancreas", 31),
    ("Soft tissue", 21),
    ("Thyroid", 16),
]
CANONICAL_GENES = [
    "EGFR", "FLT3", "ABL1", "BCR", "MET", "ERBB2", "TYMS", "FGFR1",
    "JAK1", "JAK2", "PIK3CD", "CDK6", "FGFR2", "BCL2", "HDAC2",
    "HDAC1", "MAP2K1", "MAP2K2", "AKT1", "AKT2", "MTOR", "PIK3CA",
    "BRAF", "ERBB3", "TOP2A",
]
TISSUE_TARGETS = {
    "Blood": 99,
    "Nervous system": 95,
    "Breast": 88,
    "Digestive system": 81,
    "Lung": 62,
    "Skin": 25,
    "Urogenital system": 22,
    "Aero digestive tract": 13,
}

NETWORK_EDGES = [
    ("Refametinib", "MAPK1", "MAPK"),
    ("Dabrafenib", "BRAF", "MAPK"),
    ("Alisertib", "CDIN1", "DNA-damage"),
    ("Cp-724714", "MIEN1", "HER2 / EGFR"),
    ("Imatinib", "STAT5B", "BCR-ABL"),
    ("Cytarabine", "GCLC", "DNA-damage"),
    ("Cytarabine", "MYB", "TF / epigenetic / other"),
    ("Nilotinib", "MCL1", "BCR-ABL"),
    ("Selumetinib", "MAP2K1", "MAPK"),
    ("Mk-2206", "RICTOR", "AKT / mTORC2"),
    ("Osimertinib", "ERBB3", "HER2 / EGFR"),
    ("Ceralasertib", "RAD1", "DNA-damage"),
    ("Molibresib", "EP300", "TF / epigenetic / other"),
    ("Mirdametinib", "MAPK1", "MAPK"),
    ("Barasertib", "CBFB", "TF / epigenetic / other"),
    ("Ipatasertib", "RICTOR", "AKT / mTORC2"),
    ("Vincristine", "FURIN", "TF / epigenetic / other"),
]

FIG3_RECOVERY = {
    "Tier 1": [(1, 0.05), (2, 0.12), (5, 0.25), (10, 0.40), (20, 0.62), (50, 0.85), (100, 0.92), (200, 0.96), (500, 0.99)],
    "Tier 2": [(1, 0.03), (2, 0.08), (5, 0.18), (10, 0.32), (20, 0.51), (50, 0.77), (100, 0.87), (200, 0.93), (500, 0.98)],
    "Tier 3": [(1, 0.02), (2, 0.05), (5, 0.12), (10, 0.23), (20, 0.39), (50, 0.65), (100, 0.78), (200, 0.88), (500, 0.96)],
    "random": [(1, 0.002), (2, 0.004), (5, 0.010), (10, 0.020), (20, 0.040), (50, 0.10), (100, 0.20), (200, 0.40), (500, 1.0)],
}

ADRENERGIC_RECEPTORS = [
    "ADRB1", "ADRB2", "ADRB3", "ADRA1A", "ADRA1B", "ADRA1D",
    "ADRA2A", "ADRA2B", "ADRA2C",
]
ADRENERGIC_VALUES = {
    "Propranolol": [0.56, 0.62, 0.49, 0.55, 0.50, 0.53, 0.50, 0.43, 0.54],
    "Carvedilol": [0.57, 0.59, 0.51, 0.55, 0.54, 0.55, 0.52, 0.53, 0.56],
    "Metoprolol": [0.46, 0.43, 0.36, 0.46, 0.45, 0.46, 0.45, 0.45, 0.47],
}
FIG5_SUBGROUPS = [
    ("Age", "Age <65 yr", 0.93, 0.76, 1.14, 1.03, 0.84, 1.26),
    ("Age", "Age >=65 yr", 0.69, 0.56, 0.86, 0.91, 0.83, 1.00),
    ("Self-identified race", "Self-identified White", 0.81, 0.66, 0.98, 0.80, 0.70, 0.91),
    ("Self-identified race", "Self-identified Black", 0.67, 0.40, 1.11, 0.86, 0.73, 1.02),
    ("Self-identified race", "Other / unknown", 0.88, 0.68, 1.13, 1.08, 0.95, 1.24),
    ("Cardiovascular", "Hypertension", 0.82, 0.66, 1.03, 0.92, 0.84, 1.00),
    ("Metabolic", "Diabetes mellitus", 0.81, 0.62, 1.07, 0.89, 0.81, 0.98),
    ("Metabolic", "Obesity (BMI >=30)", 0.95, 0.70, 1.30, 0.85, 0.74, 0.97),
    ("Prostate-specific", "Benign prostatic hyperplasia", 0.74, 0.55, 0.99, 0.80, 0.70, 0.92),
]

EXPECTED_PANEL_IDS = [
    "fig1b", "fig1c", "fig2a", "fig2b", "fig2cd", "fig2e", "fig2f",
    "fig2g", "fig3b", "fig3c", "fig3pairs", "fig3f", "fig3g", "fig3h_edges",
    "fig4b_nodes", "fig4b_edges", "fig5a", "fig5d", "fig5ef", "fig5g",
    "fig5hi", "fig5j", "fig5k", "figs2", "figs3s4", "figs5ab",
    "figs5cd",
]
