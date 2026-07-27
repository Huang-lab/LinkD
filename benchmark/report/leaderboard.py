"""
Build the leaderboard (markdown + CSV) from results/summary.*.jsonl, with the
external published-results table appended for context.

    python3 benchmark/report/leaderboard.py
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULTS = os.path.join(ROOT, "benchmark", "results")
EXTERNAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "external", "published_results.yaml")

# columns shown per scenario (only those present are rendered)
_RANK = ["recall@10", "recall@20", "ndcg@20", "mrr", "lat_s/item"]
_AUROC = ["auroc", "auprc", "pos", "neg", "lat_s/item"]
COLS = {
    "t1_dti": ["pearson", "spearman", "c_index", "rmse", "binary_acc", "answered", "lat_s/item"],
    "l2_binding_moa": _RANK,
    "l3_selectivity": _AUROC,
    "l4_crispr_moa": _RANK,
    "a2_target_id": _RANK,
    "a3_priority": _RANK,
    "t2_repurpose": _AUROC,
    "l9_safety": _AUROC,
    "c1_validate": _AUROC,
}
SORT_KEY = {"t1_dti": "c_index", "a2_target_id": "ndcg@20", "a3_priority": "ndcg@20",
            "l2_binding_moa": "ndcg@20", "l4_crispr_moa": "ndcg@20",
            "c1_validate": "auroc", "t2_repurpose": "auroc", "l3_selectivity": "auroc",
            "l9_safety": "auroc"}
NICE = {"linkd_cli": "LinkD (tools-only)", "linkd": "LinkD (phase-evidence)",
        "linkd_tpi": "LinkD (TPI)", "linkd_evidence": "LinkD (multi-evidence fusion)",
        "linkd_rwe": "LinkD (EHR real-world)", "linkd_selectivity": "LinkD (selectivity)",
        "linkd_binding_tgt": "LinkD (binding→target)", "linkd_crispr_tgt": "LinkD (CRISPR→target)",
        "tooluniverse": "ToolUniverse-agent (OpenTargets)", "ot_assoc": "OpenTargets association",
        "ot_genetics": "OpenTargets genetics-only", "pubmed": "PubMed literature agent",
        "closed_book": "Base LLM (closed-book)"}


def load_rows():
    rows = []
    for f in sorted(glob.glob(os.path.join(RESULTS, "summary.*.jsonl"))):
        for line in open(f):
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    # drop all-error (no-provider) rows
    return [r for r in rows if r.get("errors", 0) != r.get("n", -1)]


def _fmt(v):
    return "" if v is None else (f"{v:.3f}" if isinstance(v, float) else str(v))


def render():
    rows = load_rows()
    md = ["# LinkD Drug-Discovery Benchmark — Leaderboard\n",
          "_Auto-generated. External-gold, head-to-head LinkD vs other agents/LLMs._\n\n"
          "- **T1** drug-target binding vs TDC DAVIS (Pearson/C-Index/RMSE) — *LinkD strong*\n"
          "- **A2** target identification vs OpenTargets approved targets (recall@k/nDCG/MRR) — *LinkD competitive*\n"
          "- **A3** target prioritization (LinkD TPI vs phase) vs same gold — *LinkD competitive*\n"
          "- **C1** target-disease validation, hard decoys (AUROC) — *LinkD-fusion limitation*\n"
          "- **T2** drug repurposing vs repoDB approved/failed (AUROC) — *LinkD EHR coverage-blocked*\n\n"
          "Deterministic agents run offline from cache; base LLMs run live (gpt-4o-mini/4o/4.1)._\n"]
    csv = ["scenario,condition,model," + ",".join(sorted({c for cs in COLS.values() for c in cs}))]
    by_scn = {}
    for r in rows:
        by_scn.setdefault(r["scenario"], []).append(r)

    for scn in sorted(by_scn):
        cols = [c for c in COLS.get(scn, []) if any(c in r for r in by_scn[scn])]
        md.append(f"\n## {scn}\n")
        md.append("| Condition | Model | " + " | ".join(cols) + " |")
        md.append("|" + "---|" * (2 + len(cols)))
        # sort: LinkD conditions first, then by the scenario's headline metric desc
        key = SORT_KEY.get(scn, "accuracy")
        srt = sorted(by_scn[scn], key=lambda r: (0 if r["condition"].startswith("linkd") else 1,
                                                 -(r.get(key) or 0)))
        for r in srt:
            md.append(f"| {NICE.get(r['condition'], r['condition'])} | {r['model']} | "
                      + " | ".join(_fmt(r.get(c)) for c in cols) + " |")
            allcols = sorted({c for cs in COLS.values() for c in cs})
            csv.append(f"{scn},{r['condition']},{r['model']}," + ",".join(_fmt(r.get(c)) for c in allcols))

    # external context
    md.append("\n## External benchmarks (context — reported by authors, not re-run here)\n")
    md.append("| System | Benchmark | Metric | Reference |")
    md.append("|---|---|---|---|")
    for e in _load_external():
        md.append(f"| {e.get('name')} | {e.get('benchmark')} | {e.get('metric','')} | {e.get('ref')} |")

    os.makedirs(RESULTS, exist_ok=True)
    open(os.path.join(RESULTS, "leaderboard.md"), "w").write("\n".join(md) + "\n")
    open(os.path.join(RESULTS, "leaderboard.csv"), "w").write("\n".join(csv) + "\n")
    print(f"wrote leaderboard.md + leaderboard.csv to {RESULTS}  ({len(rows)} result rows)")


def _load_external():
    try:
        import yaml
        return yaml.safe_load(open(EXTERNAL)) or []
    except Exception:
        return []


if __name__ == "__main__":
    if not glob.glob(os.path.join(RESULTS, "summary.*.jsonl")):
        print("No results found. Run benchmark/run_benchmark.py --out benchmark/results first.")
        raise SystemExit(0)
    render()
