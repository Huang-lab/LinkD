"""
Weighted, coverage-aware multi-evidence scoring for LinkD.

Replaces the old "count how many sources were found" heuristic with:

  * per-layer normalization to a sub-score in [0, 1] (or None when a layer
    has no data for this drug / target / disease),
  * per-layer reliability WEIGHTS (literature-informed defaults, user-adjustable),
  * two selectable aggregators:
      - "strength_coverage" (default): evidence STRENGTH is renormalized over the
        layers that are actually present, so a drug-target-disease triad is NOT
        penalised just because some layers are missing. A separate COVERAGE number
        reports how complete the evidence base is. final = strength * confidence_discount(coverage).
      - "penalize_missing": Open Targets style -- missing layers contribute 0 and the
        sum is normalised over ALL weighted layers (presence == confidence).

Design rationale and citations live in METHODS.md (evidence-weight section).
(Open Targets weighted harmonic sum; Nat Rev Genet 2025 context/reliability
weighting + separate confidence score).

The module has no hard third-party dependency: PyYAML is used only if a YAML
config file is supplied and importable; otherwise the in-code DEFAULT_CONFIG is used.
"""
from __future__ import annotations

import copy
import json
import math
import os
from typing import Dict, List, Optional, Any

# Canonical evidence layers. These keys are the contract shared by the weights
# config, the normalizers, and score_evidence().
LAYERS = (
    "genetic_causality",   # causal_gene_disease / Open Targets disease-target score
    "clinical_phase",      # ChEMBL max clinical trial phase
    "real_world_ehr",      # Mount Sinai / UK Biobank odds ratio + p-value
    "functional_crispr",   # CRISPR drug-response AUC correlation + FDR
    "predicted_binding",   # predicted pKd (drug-target)
    "target_priority",     # Target Priority Index (TPI)
    "drug_selectivity",    # drug-level selectivity score (supporting)
)

DEFAULT_CONFIG: Dict[str, Any] = {
    # "strength_coverage" (default) or "penalize_missing"
    "aggregator": "strength_coverage",
    "weights": {
        "genetic_causality": 1.0,   # highest reliability (genetics upweighted, cf. Open Targets)
        "clinical_phase":    1.0,   # real clinical outcomes
        "real_world_ehr":    0.7,   # population signal, but confounded
        "functional_crispr": 0.8,   # mechanistic, experimental
        "predicted_binding": 0.6,   # model output -> downweighted
        "target_priority":   0.6,   # composite tractability / safety
        "drug_selectivity":  0.3,   # supporting context (cf. Open Targets literature = 0.2)
    },
    "gamma_confidence_floor": 0.5,  # strength_coverage: final = S * (gamma + (1-gamma)*coverage)
    "strong_threshold": 0.6,
    "moderate_threshold": 0.35,
    "min_coverage_for_strong": 0.4,  # require >=~2 substantive layers to call it "strong"
}


# --------------------------------------------------------------------------- #
# small helpers
# --------------------------------------------------------------------------- #
def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def _is_num(x: Any) -> bool:
    return isinstance(x, (int, float)) and not (isinstance(x, float) and (math.isnan(x) or math.isinf(x)))


# --------------------------------------------------------------------------- #
# per-layer normalizers : raw query output -> sub-score in [0, 1] (or None)
# Each returns None when the input is missing/unusable, so the layer is treated
# as "not present" by the aggregator.
# --------------------------------------------------------------------------- #
def normalize_clinical_phase(max_phase: Optional[float]) -> Optional[float]:
    """ChEMBL phase 0.5..4.0 -> [0,1]; Phase 4 (approved) = 1.0."""
    if not _is_num(max_phase):
        return None
    return _clamp(float(max_phase) / 4.0)


def normalize_binding(pkd: Optional[float], lo: float = 4.0, hi: float = 10.0) -> Optional[float]:
    """Predicted pKd -> [0,1]. pKd 4 -> 0, pKd 7 -> ~0.5, pKd 10 -> 1.0."""
    if not _is_num(pkd):
        return None
    return _clamp((float(pkd) - lo) / (hi - lo))


def normalize_crispr(auc_corr: Optional[float], fdr: Optional[float] = None,
                     scale: float = 0.5) -> Optional[float]:
    """|AUC correlation| scaled, gated by significance (FDR < 0.05)."""
    if not _is_num(auc_corr):
        return None
    gate = 1.0
    if _is_num(fdr):
        gate = 1.0 if fdr < 0.05 else 0.3
    return _clamp(abs(float(auc_corr)) / scale) * gate


def normalize_ehr(odds_ratio: Optional[float], p_value: Optional[float] = None) -> Optional[float]:
    """|ln(OR)| scaled (OR 0.5 or 2.0 -> 1.0), gated by significance (p < 0.05)."""
    if not _is_num(odds_ratio) or odds_ratio <= 0:
        return None
    effect = _clamp(abs(math.log(float(odds_ratio))) / math.log(2.0))
    gate = 1.0
    if _is_num(p_value):
        gate = 1.0 if p_value < 0.05 else 0.3
    return effect * gate


def normalize_genetic(score: Optional[float] = None,
                      has_causal_mutation: bool = False) -> Optional[float]:
    """Open Targets disease-target score (already [0,1]); floor at 0.6 if a causal
    mutation is annotated. Returns None only if neither signal is present."""
    s = float(score) if _is_num(score) else None
    if has_causal_mutation:
        return max(0.6, s if s is not None else 0.0)
    if s is None:
        return None
    return _clamp(s)


def normalize_unit(value: Optional[float]) -> Optional[float]:
    """Pass-through clamp for values already in [0,1] (TPI, selectivity score)."""
    if not _is_num(value):
        return None
    return _clamp(float(value))


# Dispatch table so callers can normalize generically by layer name.
_NORMALIZERS = {
    "clinical_phase": lambda raw: normalize_clinical_phase(raw.get("max_phase")),
    "predicted_binding": lambda raw: normalize_binding(raw.get("pkd")),
    "functional_crispr": lambda raw: normalize_crispr(raw.get("auc_corr"), raw.get("fdr")),
    "real_world_ehr": lambda raw: normalize_ehr(raw.get("odds_ratio"), raw.get("p_value")),
    "genetic_causality": lambda raw: normalize_genetic(raw.get("score"), raw.get("has_causal_mutation", False)),
    "target_priority": lambda raw: normalize_unit(raw.get("tpi")),
    "drug_selectivity": lambda raw: normalize_unit(raw.get("selectivity_score")),
}


def normalize_layer(layer: str, raw: Dict[str, Any]) -> Optional[float]:
    """Normalize one layer from a dict of raw fields. Unknown layer -> None."""
    fn = _NORMALIZERS.get(layer)
    return fn(raw) if fn else None


# --------------------------------------------------------------------------- #
# config loading
# --------------------------------------------------------------------------- #
def _deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(path: Optional[str] = None) -> Dict[str, Any]:
    """Return scoring config = DEFAULT_CONFIG merged with an optional override file.

    Resolution order: explicit `path` arg -> $LINKD_EVIDENCE_WEIGHTS -> defaults only.
    Supports .json always; .yaml/.yml only if PyYAML is installed.
    """
    path = path or os.getenv("LINKD_EVIDENCE_WEIGHTS")
    if not path or not os.path.exists(path):
        return copy.deepcopy(DEFAULT_CONFIG)
    try:
        with open(path) as f:
            if path.endswith((".yaml", ".yml")):
                try:
                    import yaml  # optional
                except ImportError:
                    return copy.deepcopy(DEFAULT_CONFIG)
                override = yaml.safe_load(f) or {}
            else:
                override = json.load(f)
        return _deep_merge(DEFAULT_CONFIG, override)
    except Exception:
        # Never let a bad config break scoring; fall back to defaults.
        return copy.deepcopy(DEFAULT_CONFIG)


# --------------------------------------------------------------------------- #
# core scorer
# --------------------------------------------------------------------------- #
def _verdict(final: float, coverage: float, cfg: Dict[str, Any]) -> str:
    if final >= cfg["strong_threshold"] and coverage >= cfg["min_coverage_for_strong"]:
        return "strong"
    if final >= cfg["moderate_threshold"]:
        return "moderate"
    if final > 0:
        return "weak"
    return "none"


def score_evidence(sub_scores: Dict[str, Optional[float]],
                   config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Combine per-layer sub-scores into an overall weighted evidence assessment.

    Args:
        sub_scores: {layer_name: sub_score in [0,1] or None}. Layers absent from
            the dict or set to None are treated as missing. Keys outside the
            configured weights are ignored.
        config: scoring config (see DEFAULT_CONFIG). If None, defaults are used.

    Returns dict with: aggregator, weights, sub_scores (clamped, present only),
        present, missing, strength, coverage, final, verdict.
    """
    cfg = config or DEFAULT_CONFIG
    weights: Dict[str, float] = cfg["weights"]
    aggregator = cfg.get("aggregator", "strength_coverage")
    if aggregator not in ("strength_coverage", "penalize_missing"):
        raise ValueError(f"Unknown aggregator '{aggregator}'")

    # present = weighted layers with a usable, positive-weight sub-score
    present: Dict[str, float] = {}
    for layer, w in weights.items():
        v = sub_scores.get(layer)
        if _is_num(v) and w > 0:
            present[layer] = _clamp(float(v))
    missing = [layer for layer in weights if layer not in present]

    w_all = sum(w for w in weights.values() if w > 0)
    w_present = sum(weights[layer] for layer in present)
    coverage = (w_present / w_all) if w_all > 0 else 0.0

    if aggregator == "strength_coverage":
        strength = (
            sum(weights[layer] * present[layer] for layer in present) / w_present
            if w_present > 0 else 0.0
        )
        gamma = cfg["gamma_confidence_floor"]
        final = strength * (gamma + (1.0 - gamma) * coverage)
    else:  # penalize_missing  (missing -> 0, normalise over ALL weights)
        strength = (
            sum(weights[layer] * present.get(layer, 0.0) for layer in weights) / w_all
            if w_all > 0 else 0.0
        )
        final = strength  # missing already penalised inside the sum

    return {
        "aggregator": aggregator,
        "weights": dict(weights),
        "sub_scores": present,
        "present": list(present.keys()),
        "missing": missing,
        "strength": round(strength, 4),
        "coverage": round(coverage, 4),
        "final": round(final, 4),
        "verdict": _verdict(final, coverage, cfg),
    }
