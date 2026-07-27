"""
Integration smoke test for the `linkd` Agent Skill CLI.

Drives the CLI as a subprocess (exactly how an agent would) and validates the
JSON contract + key fields of every subcommand, both scoring aggregators, and
graceful handling of unknown entities and invalid arguments.

Runs with plain Python (no pytest required):

    python3 tests/test_cli_smoke.py

Requires the LinkD data folder. If the data (or the CLI) is missing, the whole
suite SKIPS with exit code 0 so it is safe to run anywhere.
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(ROOT, ".claude", "skills", "linkd", "scripts", "linkd")
# Probe path used to decide whether the data is present.
_PROBE = os.path.join(os.getenv("DATABASE_DIR", os.path.join(ROOT, "Database")),
                      os.pardir, "DrugTargetMetrics", "target_binding_stats.csv")

passed = failed = 0


def _run(args):
    t = time.time()
    p = subprocess.run([sys.executable, CLI, *args], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr, time.time() - t


def check(name, args, want_keys=(), assertion=None, expect_rc=0, expect_json=True):
    global passed, failed
    rc, out, err, dt = _run(args)
    if rc != expect_rc:
        print(f"  FAIL  {name}: rc={rc} (want {expect_rc}) :: {err.strip().splitlines()[-1:] or out[:120]}")
        failed += 1
        return None
    if not expect_json:
        print(f"  PASS  {name}  ({dt:.1f}s)")
        passed += 1
        return None
    try:
        data = json.loads(out)
    except Exception as e:  # noqa: BLE001
        print(f"  FAIL  {name}: invalid JSON ({e})")
        failed += 1
        return None
    for k in want_keys:
        if k not in data:
            print(f"  FAIL  {name}: missing key '{k}'")
            failed += 1
            return data
    if assertion is not None:
        ok, msg = assertion(data)
        if not ok:
            print(f"  FAIL  {name}: {msg}")
            failed += 1
            return data
    print(f"  PASS  {name}  ({dt:.1f}s)")
    passed += 1
    return data


def main():
    if not os.path.exists(CLI):
        print(f"SKIP: CLI not found at {CLI}")
        return 0
    if not os.path.exists(os.path.normpath(_PROBE)):
        print("SKIP: LinkD data folder not found (set DATABASE_DIR to enable this test).")
        return 0

    print("== light commands ==")
    check("config", ["config"], want_keys=["aggregator", "weights"],
          assertion=lambda d: (d["aggregator"] == "strength_coverage", "default aggregator wrong"))
    check("target-info EGFR", ["target-info", "EGFR"], want_keys=["found", "target"],
          assertion=lambda d: (d["found"] and d["target"].get("TPI", 0) > 0, "EGFR not found / no TPI"))
    check("binding CHEMBL553 EGFR", ["binding", "CHEMBL553", "EGFR"], want_keys=["result"],
          assertion=lambda d: (d["result"] and d["result"]["binding_affinity"] > 9, "pKd not > 9"))
    check("drugs-for-target EGFR", ["drugs-for-target", "EGFR", "--limit", "3"], want_keys=["drugs"],
          assertion=lambda d: (len(d["drugs"]) == 3, "expected 3 drugs"))
    check("targets-for-drug CHEMBL553", ["targets-for-drug", "CHEMBL553", "--limit", "3"],
          want_keys=["targets"], assertion=lambda d: (len(d["targets"]) == 3, "expected 3 targets"))
    check("drug-info CHEMBL553", ["drug-info", "CHEMBL553", "--name", "Erlotinib"], want_keys=["found"])
    check("causal BRAF", ["causal", "BRAF", "--limit", "3"], want_keys=["count"],
          assertion=lambda d: (d["count"] > 0, "no causal rows for BRAF"))

    print("== medium commands ==")
    check("drug-response", ["drug-response", "--drug", "CHEMBL553", "--gene", "EGFR", "--sig"],
          want_keys=["count"], assertion=lambda d: (d["count"] > 0, "no CRISPR rows"))
    check("ehr", ["ehr", "--drug", "CHEMBL553"], want_keys=["count"],
          assertion=lambda d: (d["count"] > 0, "no EHR rows"))

    print("== weighted evidence ==")
    ev = check("evidence (default)",
               ["evidence", "CHEMBL553", "EGFR", "--disease", "lung cancer", "--icd", "C34",
                "--drug-name", "Erlotinib"],
               want_keys=["verdict", "strength_score", "coverage", "final_score", "missing",
                          "overall_strength"],
               assertion=lambda d: (d["verdict"] == "strong" and d["overall_strength"] == d["verdict"],
                                    "verdict != strong or legacy key mismatch"))
    pm = check("evidence (penalize_missing)",
               ["evidence", "CHEMBL553", "EGFR", "--icd", "C34", "--drug-name", "Erlotinib",
                "--aggregator", "penalize_missing"],
               want_keys=["aggregator", "final_score"],
               assertion=lambda d: (d["aggregator"] == "penalize_missing", "aggregator not applied"))
    if ev and pm:
        global passed, failed
        ok = ev["final_score"] >= pm["final_score"]
        print(f"  {'PASS' if ok else 'FAIL'}  aggregators differ "
              f"(strength_coverage {ev['final_score']} >= penalize_missing {pm['final_score']})")
        passed += int(ok); failed += int(not ok)

    check("deep-dive", ["deep-dive", "CHEMBL553", "EGFR", "--icd", "C34", "--drug-name", "Erlotinib"],
          want_keys=["triad", "evidence", "other_drugs_for_target", "gene_causal_diseases"])

    print("== edge cases ==")
    check("binding unknown pair", ["binding", "CHEMBL00000", "NOTAGENE"], want_keys=["result"],
          assertion=lambda d: (d["result"] is None, "expected null result"))
    check("target-info unknown", ["target-info", "NOTAGENE"], want_keys=["found"],
          assertion=lambda d: (d["found"] is False, "expected found=false"))
    check("evidence unknown triad", ["evidence", "CHEMBL00000", "NOTAGENE"],
          want_keys=["verdict", "coverage"],
          assertion=lambda d: (d["verdict"] == "none" and d["coverage"] == 0.0, "expected none/0"))
    # argparse rejects an invalid choice with rc=2 and a usage message (no JSON on stdout)
    check("invalid aggregator rejected", ["evidence", "CHEMBL553", "EGFR", "--aggregator", "bogus"],
          expect_rc=2, expect_json=False)

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


# pytest entry point (optional)
def test_cli_smoke():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
