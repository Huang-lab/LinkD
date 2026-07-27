"""
Shared dataset-builder utilities: load the partial LinkD DB (no 16 GB load),
deterministic sampling, Item construction with entity-disjoint split assignment,
and writing tasks/<scenario>.<split>.jsonl.
"""
from __future__ import annotations
import os
import random
import sys
from typing import Dict, List, Optional

# repo importable
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from agent.database_query_module import load_database_subset, SUBSET_DATASETS  # noqa: E402
from benchmark.schema import Item, write_jsonl  # noqa: E402
from benchmark.datasets.splits import assign_split, split_anchor  # noqa: E402

TASKS_DIR = os.path.join(REPO_ROOT, "benchmark", "tasks")
DB_DIR = os.getenv("DATABASE_DIR", os.path.join(REPO_ROOT, "Database"))
DATA_PROBE = os.path.join(os.path.dirname(DB_DIR), "DrugTargetMetrics", "target_binding_stats.csv") \
    if os.getenv("DATABASE_DIR") else os.path.join(REPO_ROOT, "DrugTargetMetrics", "target_binding_stats.csv")

SEED = 20260617

_DB_CACHE = {}


def data_available() -> bool:
    return os.path.exists(DATA_PROBE)


def get_db(datasets=None):
    """Cached partial DB. `datasets` = subset keys (default: all medium datasets)."""
    key = tuple(sorted(datasets)) if datasets else "ALL"
    if key not in _DB_CACHE:
        _DB_CACHE[key] = load_database_subset(datasets, database_dir=DB_DIR)
    return _DB_CACHE[key]


def rng() -> random.Random:
    return random.Random(SEED)


def make_item(item_id, scenario, fmt, question, gold, gold_source,
              entities, *, choices=None, context_free_prompt="", meta=None) -> Item:
    split = assign_split(split_anchor(entities))
    return Item(
        id=item_id, scenario=scenario, format=fmt, question=question,
        gold=gold, gold_source=gold_source, split=split,
        choices=choices, context_free_prompt=context_free_prompt or question,
        entities=entities, meta=meta or {},
    )


def write_scenario(scenario: str, items: List[Item]) -> Dict[str, int]:
    """Write items grouped by split to tasks/<scenario>.<split>.jsonl. Returns counts."""
    by_split: Dict[str, List[dict]] = {}
    for it in items:
        by_split.setdefault(it.split, []).append(it.to_dict())
    counts = {}
    for split, rows in by_split.items():
        path = os.path.join(TASKS_DIR, f"{scenario}.{split}.jsonl")
        write_jsonl(path, rows)
        counts[split] = len(rows)
    return counts


def banner(scenario: str, counts: Dict[str, int]) -> None:
    total = sum(counts.values())
    print(f"[{scenario}] wrote {total} items  " + "  ".join(f"{k}={v}" for k, v in sorted(counts.items())))
