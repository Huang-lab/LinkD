"""
Run the LinkD benchmark: for each scenario × condition × model, produce
predictions, score them, and print a summary. Provider-agnostic and key-gated —
LLM conditions without a key are skipped (recorded as no_provider), so this runs
end-to-end with zero API cost using only the deterministic linkd_cli condition.

    # A2 target-ID, all five agent strategies (cancer):
    python3 benchmark/run_benchmark.py --scenarios a2_target_id \
        --conditions linkd,tooluniverse,ot_genetics,pubmed,closed_book --models gpt-4.1
    # T1 binding vs DAVIS, deterministic only (zero API cost):
    python3 benchmark/run_benchmark.py --scenarios t1_dti --conditions linkd_cli --quick
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmark.schema import load_items, write_jsonl  # noqa: E402
from benchmark.scoring import score_item  # noqa: E402
from benchmark.scoring.classification import accuracy, macro_f1  # noqa: E402
from benchmark.scoring.ranking import mean_metric  # noqa: E402
from benchmark.datasets.base_builder import TASKS_DIR, data_available  # noqa: E402
from benchmark.scoring.regression import aggregate_dti  # noqa: E402
from benchmark.scoring.ranking import aggregate_target_rank  # noqa: E402
from benchmark.aggregate import mcnemar, correct_of  # noqa: E402

# Supplementary T1–T7 (+ diagnostics D1/D2). ID map: benchmark/TASK_CATALOG.md
#   T1=t1_dti T2=a2_target_id T3=a3_priority T4=l4_crispr_moa
#   T5=c1_validate T6=l2_binding_moa T7=l3_selectivity
#   D1=t2_repurpose D2=l9_safety
ALL_SCENARIOS = ["t1_dti", "l2_binding_moa", "l3_selectivity", "l4_crispr_moa",
                 "a2_target_id", "a3_priority", "t2_repurpose", "l9_safety", "c1_validate"]
REFINED_SCENARIOS = []
# deterministic (no-LLM) conditions -> their fixed model label
DETERMINISTIC = {"linkd_cli": "tools-only", "linkd": "tools-only", "linkd_tpi": "tools-only",
                 "linkd_evidence": "tools-only", "linkd_rwe": "tools-only",
                 "linkd_selectivity": "tools-only", "linkd_binding_tgt": "tools-only",
                 "linkd_crispr_tgt": "tools-only", "linkd_target_aff": "tools-only",
                 "linkd_crispr_pair": "tools-only", "linkd_fusion_pair": "tools-only",
                 "tooluniverse": "opentargets", "ot_assoc": "opentargets",
                 "pubmed": "literature", "ot_genetics": "ot-genetics"}


def _condition(name, model):
    if name == "linkd_cli":
        from benchmark.conditions.linkd_cli import LinkdCliCondition
        return LinkdCliCondition()
    if name == "closed_book":
        from benchmark.conditions.closed_book import ClosedBookCondition
        return ClosedBookCondition(model=model)
    if name == "combined":
        from benchmark.conditions.combined import CombinedCondition
        return CombinedCondition(model=model)
    if name == "orchestrator":
        from benchmark.conditions.orchestrator import LinkdOrchestratorCondition
        return LinkdOrchestratorCondition(model=model)
    if name == "linkd":
        from benchmark.conditions.agents_a2 import LinkdTargetsCondition
        return LinkdTargetsCondition()
    if name == "linkd_tpi":
        from benchmark.conditions.agents_a2 import LinkdPriorityCondition
        return LinkdPriorityCondition()
    if name == "tooluniverse":
        from benchmark.conditions.agents_a2 import ToolUniverseCondition
        return ToolUniverseCondition()
    if name == "pubmed":
        from benchmark.conditions.agents_a2 import PubMedCondition
        return PubMedCondition()
    if name == "ot_genetics":
        from benchmark.conditions.agents_a2 import OTGeneticsCondition
        return OTGeneticsCondition()
    if name == "linkd_evidence":
        from benchmark.conditions.agents_integrative import LinkdEvidenceCondition
        return LinkdEvidenceCondition()
    if name == "linkd_rwe":
        from benchmark.conditions.agents_integrative import LinkdRweCondition
        return LinkdRweCondition()
    if name == "ot_assoc":
        from benchmark.conditions.agents_integrative import OTAssocScoreCondition
        return OTAssocScoreCondition()
    if name == "linkd_selectivity":
        from benchmark.conditions.agents_layers import LinkdSelectivityCondition
        return LinkdSelectivityCondition()
    if name == "linkd_binding_tgt":
        from benchmark.conditions.agents_layers import LinkdBindingTargetsCondition
        return LinkdBindingTargetsCondition()
    if name == "linkd_crispr_tgt":
        from benchmark.conditions.agents_layers import LinkdCrisprTargetsCondition
        return LinkdCrisprTargetsCondition()
    if name == "linkd_target_aff":
        from benchmark.conditions.agents_layers import LinkdTargetAffinityCondition
        return LinkdTargetAffinityCondition()
    if name == "linkd_crispr_pair":
        from benchmark.conditions.agents_layers import LinkdCrisprPairCondition
        return LinkdCrisprPairCondition()
    if name == "linkd_fusion_pair":
        from benchmark.conditions.agents_layers import LinkdFusionPairCondition
        return LinkdFusionPairCondition()
    raise ValueError(f"unknown condition {name}")


def _load(scenario, split):
    path = os.path.join(TASKS_DIR, f"{scenario}.{split}.jsonl")
    return load_items(path) if os.path.exists(path) else []


def _summarize(rows, scenario):
    """rows = list of per-item metric dicts for one (scenario,condition,model).
    Format-driven: route on the per-item signal so new tasks aggregate automatically."""
    err = sum(1 for r in rows if r.get("error"))
    if any(r.get("dti") for r in rows):
        out = aggregate_dti(rows)
    elif any(r.get("target_rank") for r in rows):
        out = aggregate_target_rank(rows)
    elif any(r.get("binary_score") for r in rows):
        from benchmark.scoring.auroc import aggregate_auroc
        out = aggregate_auroc(rows)
    else:
        out = {"n": len(rows), "abstained": sum(1 for r in rows if r.get("abstained"))}
    out["errors"] = err
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", default=",".join(ALL_SCENARIOS))
    ap.add_argument("--conditions", default="linkd_cli")
    ap.add_argument("--models", default="gpt-4o-mini")
    ap.add_argument("--split", default="test")
    ap.add_argument("--limit", type=int, default=0, help="cap items per scenario (0=all)")
    ap.add_argument("--quick", action="store_true", help="cap to 8 items per scenario")
    ap.add_argument("--out", default="", help="dir to write predictions/scores jsonl")
    ap.add_argument("--tag", default="run", help="label for output filenames")
    a = ap.parse_args()

    if not data_available():
        print("SKIP: LinkD data not found (set DATABASE_DIR).")
        return 0

    scenarios = [s for s in a.scenarios.split(",") if s]
    conditions = [c for c in a.conditions.split(",") if c]
    models = [m for m in a.models.split(",") if m]
    limit = 8 if a.quick else a.limit

    print(f"scenarios={scenarios} conditions={conditions} models={models} split={a.split}\n")
    table = []
    all_preds = []
    paired = []
    for scenario in scenarios:
        items = _load(scenario, a.split)
        if not items:
            print(f"  [{scenario}] no tasks for split={a.split} (run the builder first) — skipped")
            continue
        if limit:
            items = items[:limit]
        scenario_rows = {}
        for cond_name in conditions:
            model_list = [DETERMINISTIC[cond_name]] if cond_name in DETERMINISTIC else models
            for model in model_list:
                cond = _condition(cond_name, model)
                metrics_rows = []
                lat = 0.0
                for it in items:
                    pred = cond.run(it)
                    lat += pred.latency_s
                    metrics_rows.append(score_item(it, pred))
                    if a.out:
                        all_preds.append({**pred.to_dict(), "gold": it.gold})
                scenario_rows[(cond_name, model)] = metrics_rows
                summ = _summarize(metrics_rows, scenario)
                summ["lat_s/item"] = round(lat / max(len(items), 1), 2)
                row = {"scenario": scenario, "condition": cond_name, "model": model, **summ}
                table.append(row)
                # one-line print
                head = f"  {scenario:12} {cond_name:11} {model:24}"
                body = "  ".join(f"{k}={v}" for k, v in summ.items())
                # mark no_provider runs
                if summ.get("errors") == len(metrics_rows) and cond_name not in DETERMINISTIC:
                    body += "   (skipped: no provider key)"
                print(head + "  " + body)

        # paired significance: LinkD vs EACH comparator on the per-item "right action" signal
        keys = [k for k, rows in scenario_rows.items()
                if any(correct_of(r) is not None for r in rows)]
        linkd_keys = [k for k in keys if k[0] in ("linkd", "linkd_cli")]
        if linkd_keys:
            base = linkd_keys[0]
            for k2 in keys:
                if k2 == base:
                    continue
                a_c, b_c = [], []
                for x, y in zip(scenario_rows[base], scenario_rows[k2]):
                    ca, cb = correct_of(x), correct_of(y)
                    if ca is not None and cb is not None:
                        a_c.append(ca); b_c.append(cb)
                if a_c:
                    mc = mcnemar(a_c, b_c)
                    rec = {"scenario": scenario, "a": base[0], "b": f"{k2[0]}:{k2[1]}",
                           "linkd_only_right": mc["b10"], "other_only_right": mc["b01"],
                           "n_discordant": mc["n_discordant"], "mcnemar_p": mc["p_value"]}
                    paired.append(rec)
                    print(f"  [paired] linkd vs {k2[0]}({k2[1]}): "
                          f"linkd_only_right={mc['b10']} other_only_right={mc['b01']} "
                          f"n_disc={mc['n_discordant']} McNemar_p={mc['p_value']}")

    if a.out:
        if all_preds:
            write_jsonl(os.path.join(a.out, f"predictions.{a.tag}.{a.split}.jsonl"), all_preds)
        write_jsonl(os.path.join(a.out, f"summary.{a.tag}.{a.split}.jsonl"), table)
        if paired:
            write_jsonl(os.path.join(a.out, f"paired.{a.tag}.{a.split}.jsonl"), paired)
        print(f"\nwrote summary ({len(table)} rows) to {a.out}/summary.{a.tag}.{a.split}.jsonl")
    return 0


if __name__ == "__main__":
    sys.exit(main())
