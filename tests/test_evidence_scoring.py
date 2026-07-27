"""
Tests for agent/evidence_scoring.py.

Runs with plain Python (no pytest required):

    python3 tests/test_evidence_scoring.py

It also works under pytest if installed (test_* functions, assert-based).
"""
import os
import sys
import json
import math
import tempfile

# Make the repo root importable when run as a script from the repo root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.evidence_scoring import (  # noqa: E402
    DEFAULT_CONFIG, load_config, score_evidence,
    normalize_clinical_phase, normalize_binding, normalize_crispr,
    normalize_ehr, normalize_genetic, normalize_unit, normalize_layer,
)

TOL = 1e-3


def approx(a, b, tol=TOL):
    return a is not None and b is not None and abs(a - b) <= tol


# --------------------------------------------------------------------------- #
# normalizers
# --------------------------------------------------------------------------- #
def test_normalize_clinical_phase():
    assert approx(normalize_clinical_phase(4.0), 1.0)
    assert approx(normalize_clinical_phase(2.0), 0.5)
    assert approx(normalize_clinical_phase(0.5), 0.125)
    assert normalize_clinical_phase(None) is None
    assert normalize_clinical_phase(float("nan")) is None


def test_normalize_binding():
    assert approx(normalize_binding(10.0), 1.0)
    assert approx(normalize_binding(7.0), 0.5)
    assert approx(normalize_binding(4.0), 0.0)
    assert approx(normalize_binding(13.0), 1.0)   # clamp high
    assert approx(normalize_binding(2.0), 0.0)    # clamp low
    assert normalize_binding(None) is None


def test_normalize_crispr():
    assert approx(normalize_crispr(0.5, 0.01), 1.0)
    assert approx(normalize_crispr(0.25, 0.01), 0.5)
    assert approx(normalize_crispr(0.5, 0.5), 0.3)   # not significant -> gated
    assert approx(normalize_crispr(-0.5, 0.01), 1.0)  # magnitude
    assert normalize_crispr(None) is None


def test_normalize_ehr():
    assert approx(normalize_ehr(2.0, 0.01), 1.0)
    assert approx(normalize_ehr(0.5, 0.01), 1.0)     # protective, same magnitude
    assert approx(normalize_ehr(1.0, 0.01), 0.0)     # OR=1 -> no effect
    assert approx(normalize_ehr(2.0, 0.5), 0.3)      # not significant -> gated
    assert normalize_ehr(0.0) is None                # invalid OR
    assert normalize_ehr(None) is None


def test_normalize_genetic():
    assert approx(normalize_genetic(0.8), 0.8)
    assert approx(normalize_genetic(0.1, has_causal_mutation=True), 0.6)   # floor
    assert approx(normalize_genetic(0.9, has_causal_mutation=True), 0.9)   # above floor kept
    assert approx(normalize_genetic(None, has_causal_mutation=True), 0.6)
    assert normalize_genetic(None) is None


def test_normalize_unit_and_dispatch():
    assert approx(normalize_unit(0.83), 0.83)
    assert approx(normalize_unit(1.5), 1.0)
    assert normalize_unit(None) is None
    # dispatcher
    assert approx(normalize_layer("predicted_binding", {"pkd": 7.0}), 0.5)
    assert approx(normalize_layer("target_priority", {"tpi": 0.83}), 0.83)
    assert normalize_layer("nonexistent_layer", {"x": 1}) is None


# --------------------------------------------------------------------------- #
# score_evidence : strength_coverage (default)
# --------------------------------------------------------------------------- #
def test_full_coverage_all_strong():
    subs = {k: 1.0 for k in DEFAULT_CONFIG["weights"]}
    r = score_evidence(subs)
    assert approx(r["strength"], 1.0)
    assert approx(r["coverage"], 1.0)
    assert approx(r["final"], 1.0)
    assert r["verdict"] == "strong"
    assert r["missing"] == []


def test_missing_data_not_penalized_in_strength():
    # Only 2 of 7 layers present, but both maximal.
    subs = {"genetic_causality": 1.0, "clinical_phase": 1.0}
    r = score_evidence(subs)
    # w_all = 5.0, w_present = 2.0
    assert approx(r["strength"], 1.0)              # renormalized over present -> not penalized
    assert approx(r["coverage"], 0.4)             # 2.0 / 5.0
    assert approx(r["final"], 0.7)                # 1.0 * (0.5 + 0.5*0.4)
    assert r["verdict"] == "strong"               # coverage exactly meets guard
    assert set(r["missing"]) == set(DEFAULT_CONFIG["weights"]) - {"genetic_causality", "clinical_phase"}


def test_coverage_guard_blocks_strong():
    # One strong layer: high final but coverage below guard -> not "strong".
    r = score_evidence({"genetic_causality": 1.0})
    assert approx(r["strength"], 1.0)
    assert approx(r["coverage"], 0.2)             # 1.0 / 5.0
    assert approx(r["final"], 0.6)                # 1.0 * (0.5 + 0.5*0.2)
    assert r["verdict"] == "moderate"             # final>=0.6 but coverage 0.2 < 0.4 guard
    assert r["coverage"] < DEFAULT_CONFIG["min_coverage_for_strong"]


def test_all_missing():
    r = score_evidence({})
    assert approx(r["strength"], 0.0)
    assert approx(r["coverage"], 0.0)
    assert approx(r["final"], 0.0)
    assert r["verdict"] == "none"


def test_none_and_unknown_keys_ignored():
    subs = {"clinical_phase": None, "predicted_binding": 0.6, "junk_layer": 0.99}
    r = score_evidence(subs)
    assert r["present"] == ["predicted_binding"]
    assert "junk_layer" not in r["sub_scores"]
    assert "clinical_phase" in r["missing"]


def test_subscore_clamped():
    r = score_evidence({"clinical_phase": 5.0})  # out-of-range sub-score
    assert approx(r["sub_scores"]["clinical_phase"], 1.0)


# --------------------------------------------------------------------------- #
# score_evidence : penalize_missing aggregator
# --------------------------------------------------------------------------- #
def test_penalize_missing_differs():
    cfg = load_config()
    cfg["aggregator"] = "penalize_missing"
    subs = {"genetic_causality": 1.0, "clinical_phase": 1.0}
    r = score_evidence(subs, cfg)
    # strength = (1*1 + 1*1) / 5.0 = 0.4 ; missing penalised
    assert approx(r["strength"], 0.4)
    assert approx(r["final"], 0.4)
    assert approx(r["coverage"], 0.4)             # coverage still reported
    assert r["verdict"] == "moderate"
    # contrast: same input under default aggregator is stronger
    r_default = score_evidence(subs)
    assert r_default["final"] > r["final"]


def test_bad_aggregator_raises():
    cfg = load_config()
    cfg["aggregator"] = "nope"
    try:
        score_evidence({"clinical_phase": 1.0}, cfg)
    except ValueError:
        return
    raise AssertionError("expected ValueError for unknown aggregator")


# --------------------------------------------------------------------------- #
# config loading
# --------------------------------------------------------------------------- #
def test_load_config_defaults():
    cfg = load_config("/nonexistent/path.yaml")
    assert cfg["aggregator"] == "strength_coverage"
    assert cfg["weights"]["genetic_causality"] == 1.0


def test_load_config_json_override_deep_merge():
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"aggregator": "penalize_missing",
                   "weights": {"drug_selectivity": 0.9}}, f)
        path = f.name
    try:
        cfg = load_config(path)
        assert cfg["aggregator"] == "penalize_missing"
        assert cfg["weights"]["drug_selectivity"] == 0.9      # overridden
        assert cfg["weights"]["genetic_causality"] == 1.0     # default preserved (deep merge)
    finally:
        os.unlink(path)


def test_shipped_config_file_loads():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    jpath = os.path.join(root, "config", "evidence_weights.json")
    if os.path.exists(jpath):
        cfg = load_config(jpath)
        assert set(cfg["weights"]) == set(DEFAULT_CONFIG["weights"])
        assert cfg["weights"] == DEFAULT_CONFIG["weights"]


# --------------------------------------------------------------------------- #
# realistic end-to-end sanity (matches the validation gate in the plan)
# --------------------------------------------------------------------------- #
def test_realistic_erlotinib_egfr_full():
    """Erlotinib/EGFR/NSCLC: all layers present and strong -> strong, high coverage."""
    subs = {
        "genetic_causality": normalize_genetic(0.7, has_causal_mutation=True),
        "clinical_phase":    normalize_clinical_phase(3.0),
        "predicted_binding": normalize_binding(9.51),
        "functional_crispr": normalize_crispr(0.46, 4.6e-34),
        "target_priority":   normalize_unit(0.831),
        "drug_selectivity":  normalize_unit(0.33),
        "real_world_ehr":    normalize_ehr(0.40, 9.6e-4),
    }
    r = score_evidence(subs)
    assert r["verdict"] == "strong"
    assert r["coverage"] >= 0.9
    assert r["final"] >= 0.6


def test_realistic_vemurafenib_braf_sparse():
    """Vemurafenib/BRAF: no CRISPR / EHR -> still strong strength, lower coverage."""
    subs = {
        "genetic_causality": normalize_genetic(None, has_causal_mutation=True),
        "clinical_phase":    normalize_clinical_phase(4.0),
        "predicted_binding": normalize_binding(6.78),
        "target_priority":   normalize_unit(0.751),
        "drug_selectivity":  normalize_unit(0.177),
        # functional_crispr and real_world_ehr missing
    }
    r = score_evidence(subs)
    assert "functional_crispr" in r["missing"]
    assert "real_world_ehr" in r["missing"]
    assert r["coverage"] < 0.9      # demonstrably lower coverage
    assert r["strength"] >= 0.5     # but strength holds up on present evidence


# --------------------------------------------------------------------------- #
# runner
# --------------------------------------------------------------------------- #
def _run_all():
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    passed = failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
            passed += 1
        except Exception as e:  # noqa: BLE001
            print(f"  FAIL  {fn.__name__}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed ({len(fns)} total)")
    return failed


if __name__ == "__main__":
    sys.exit(1 if _run_all() else 0)
