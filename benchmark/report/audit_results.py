"""
Audit benchmark result summaries for reproducibility hazards.

Checks the result directory for duplicate scenario/condition/model groups, missing
headline rows, all-error LLM rows, and duplicate task item IDs. It does not modify
files.

    python3 benchmark/report/audit_results.py
    python3 benchmark/report/audit_results.py --strict
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULTS = os.path.join(ROOT, "benchmark", "results")
TASKS = os.path.join(ROOT, "benchmark", "tasks")

EXPECTED = [
    ("T1", "t1_dti", "c_index", {
        "LinkD": lambda r: r.get("condition") == "linkd_cli",
        "GPT-5.4": lambda r: r.get("condition") == "closed_book" and r.get("model") == "gpt-5.4",
        "Combined": lambda r: r.get("condition") == "combined" and r.get("model") == "gpt-5.4",
        "Orchestrator": lambda r: r.get("condition") == "orchestrator" and r.get("model") == "gpt-5.4",
    }),
    ("T2", "a2_target_id", "ndcg@20", {
        "LinkD": lambda r: r.get("condition") == "linkd",
        "GPT-5.4": lambda r: r.get("condition") == "closed_book" and r.get("model") == "gpt-5.4",
        "ToolUniverse": lambda r: r.get("condition") == "tooluniverse",
        "Combined": lambda r: r.get("condition") == "combined" and r.get("model") == "gpt-5.4",
        "Orchestrator": lambda r: r.get("condition") == "orchestrator" and r.get("model") == "gpt-5.4",
    }),
    ("T3", "a3_priority", "ndcg@20", {
        "LinkD": lambda r: r.get("condition") == "linkd",
        "GPT-5.4": lambda r: r.get("condition") == "closed_book" and r.get("model") == "gpt-5.4",
        "ToolUniverse": lambda r: r.get("condition") == "tooluniverse",
        "Combined": lambda r: r.get("condition") == "combined" and r.get("model") == "gpt-5.4",
        "Orchestrator": lambda r: r.get("condition") == "orchestrator" and r.get("model") == "gpt-5.4",
    }),
    ("T4", "l4_crispr_moa", "ndcg@20", {
        "LinkD": lambda r: r.get("condition") == "linkd_crispr_tgt",
        "GPT-5.4": lambda r: r.get("condition") == "closed_book" and r.get("model") == "gpt-5.4",
        "Combined": lambda r: r.get("condition") == "combined" and r.get("model") == "gpt-5.4",
        "Orchestrator": lambda r: r.get("condition") == "orchestrator" and r.get("model") == "gpt-5.4",
    }),
    ("T5", "c1_validate", "auroc", {
        "LinkD": lambda r: r.get("condition") == "linkd_evidence",
        "GPT-5.4": lambda r: r.get("condition") == "closed_book" and r.get("model") == "gpt-5.4",
        "ToolUniverse": lambda r: r.get("condition") == "ot_assoc",
        "Combined": lambda r: r.get("condition") == "combined" and r.get("model") == "gpt-5.4",
        "Orchestrator": lambda r: r.get("condition") == "orchestrator" and r.get("model") == "gpt-5.4",
    }),
    ("T6", "l2_binding_moa", "ndcg@20", {
        "LinkD": lambda r: r.get("condition") == "linkd_binding_tgt",
        "GPT-5.4": lambda r: r.get("condition") == "closed_book" and r.get("model") == "gpt-5.4",
        "Combined": lambda r: r.get("condition") == "combined" and r.get("model") == "gpt-5.4",
        "Orchestrator": lambda r: r.get("condition") == "orchestrator" and r.get("model") == "gpt-5.4",
    }),
    ("T7", "l3_selectivity", "auroc", {
        "LinkD": lambda r: r.get("condition") == "linkd_selectivity",
        "GPT-5.4": lambda r: r.get("condition") == "closed_book" and r.get("model") == "gpt-5.4",
        "Combined": lambda r: r.get("condition") == "combined" and r.get("model") == "gpt-5.4",
        "Orchestrator": lambda r: r.get("condition") == "orchestrator" and r.get("model") == "gpt-5.4",
    }),
]


def load_rows(results_dir: str):
    rows = []
    for path in sorted(glob.glob(os.path.join(results_dir, "summary.*.jsonl"))):
        with open(path) as f:
            for lineno, line in enumerate(f, 1):
                if not line.strip():
                    continue
                r = json.loads(line)
                r["_file"] = os.path.basename(path)
                r["_line"] = lineno
                rows.append(r)
    return rows


def audit_task_ids(tasks_dir: str):
    task_files = sorted(glob.glob(os.path.join(tasks_dir, "*.jsonl")))
    duplicates = []
    label_conflicts = []
    malformed = []
    test_counts = collections.Counter()
    total = 0
    for path in task_files:
        by_id = collections.defaultdict(list)
        by_entity_label = collections.defaultdict(list)
        is_test_file = os.path.basename(path).endswith(".test.jsonl")
        with open(path) as f:
            for lineno, line in enumerate(f, 1):
                if not line.strip():
                    continue
                total += 1
                try:
                    item = json.loads(line)
                except json.JSONDecodeError as exc:
                    malformed.append((os.path.basename(path), lineno, f"invalid json: {exc}"))
                    continue
                item_id = item.get("id")
                if not item_id:
                    malformed.append((os.path.basename(path), lineno, "missing id"))
                    continue
                if is_test_file:
                    test_counts[item.get("scenario")] += 1
                by_id[item_id].append(lineno)
                gold = item.get("gold") or {}
                entities = item.get("entities") or {}
                label = gold.get("label")
                entity_key = tuple(entities.get(k) for k in ("drug", "gene", "disease"))
                if label is not None and all(v is not None for v in entity_key):
                    by_entity_label[entity_key].append((lineno, label, item_id))
        for item_id, lines in by_id.items():
            if len(lines) > 1:
                duplicates.append((os.path.basename(path), item_id, lines))
        for entity_key, rows in by_entity_label.items():
            if len({label for _, label, _ in rows}) > 1:
                label_conflicts.append((os.path.basename(path), entity_key, rows))
    return task_files, total, test_counts, duplicates, label_conflicts, malformed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=RESULTS)
    ap.add_argument("--tasks", default=TASKS)
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero when duplicates or expected-row gaps are found")
    args = ap.parse_args()

    rows = load_rows(args.results)
    print(f"results_dir={args.results}")
    print(f"summary_rows={len(rows)} files={len(set(r['_file'] for r in rows))}")

    failures = 0
    all_error = [r for r in rows if r.get("errors", 0) == r.get("n", -1)]
    if all_error:
        print(f"\nall-error rows skipped by reports: {len(all_error)}")
        for r in all_error[:20]:
            print(f"  {r['_file']}:{r['_line']} {r.get('scenario')} {r.get('condition')} {r.get('model')}")

    grouped = collections.defaultdict(list)
    for r in rows:
        grouped[(r.get("scenario"), r.get("condition"), r.get("model"))].append(r)
    duplicates = {k: v for k, v in grouped.items() if len(v) > 1}
    if duplicates:
        failures += 1
        print(f"\nduplicate scenario/condition/model groups: {len(duplicates)}")
        for key, vals in sorted(duplicates.items()):
            metric = next((m for m in ("c_index", "ndcg@20", "auroc", "recall@20")
                           if any(m in r for r in vals)), None)
            print(f"  {key}")
            for r in vals:
                value = f" {metric}={r.get(metric)}" if metric else ""
                print(f"    {r['_file']}:{r['_line']}{value} n={r.get('n')} errors={r.get('errors')}")
    else:
        print("\nduplicate scenario/condition/model groups: 0")

    task_files, task_rows, task_test_counts, duplicate_ids, label_conflicts, malformed_tasks = audit_task_ids(args.tasks)
    print(f"\ntask_files={len(task_files)} task_rows={task_rows}")
    if malformed_tasks:
        failures += 1
        print(f"malformed task rows: {len(malformed_tasks)}")
        for file_name, lineno, reason in malformed_tasks[:20]:
            print(f"  {file_name}:{lineno} {reason}")
    if duplicate_ids:
        failures += 1
        print(f"duplicate task item IDs: {len(duplicate_ids)}")
        for file_name, item_id, lines in duplicate_ids[:20]:
            joined = ",".join(str(x) for x in lines)
            print(f"  {file_name}:{joined} {item_id}")
    else:
        print("duplicate task item IDs: 0")
    if label_conflicts:
        failures += 1
        print(f"conflicting task labels for same entities: {len(label_conflicts)}")
        for file_name, entity_key, rows in label_conflicts[:20]:
            parts = ", ".join(f"{lineno}:label={label}:{item_id}" for lineno, label, item_id in rows)
            print(f"  {file_name} {entity_key} -> {parts}")
    else:
        print("conflicting task labels for same entities: 0")

    n_mismatches = []
    for r in rows:
        scenario = r.get("scenario")
        expected_n = task_test_counts.get(scenario)
        if expected_n and r.get("n") is not None and r.get("n") != expected_n:
            n_mismatches.append(r)
    if n_mismatches:
        failures += 1
        print(f"summary n mismatches current task counts: {len(n_mismatches)}")
        for r in n_mismatches[:20]:
            print(f"  {r['_file']}:{r['_line']} {r.get('scenario')} "
                  f"{r.get('condition')} {r.get('model')} n={r.get('n')} "
                  f"task_n={task_test_counts.get(r.get('scenario'))}")
    else:
        print("summary n mismatches current task counts: 0")

    print("\nheadline GPT-5.4 Figure 6 coverage:")
    active = [r for r in rows if r.get("errors", 0) != r.get("n", -1)]
    for lid, scenario, metric, methods in EXPECTED:
        parts = []
        for name, pred in methods.items():
            cand = [r for r in active if r.get("scenario") == scenario and pred(r) and r.get(metric) is not None]
            if not cand:
                failures += 1
                parts.append(f"{name}=MISSING")
            else:
                best = max(cand, key=lambda r: r[metric])
                parts.append(f"{name}={best[metric]:.3f}")
        print(f"  {lid} {scenario} {metric}: " + ", ".join(parts))

    if args.strict and failures:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
