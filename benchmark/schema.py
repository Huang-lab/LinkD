"""
Core data structures + JSONL I/O for the LinkD benchmark.

An *Item* is one benchmark question with auto-derived gold. A *Prediction* is one
condition/model's answer to an item. A *ScoredResult* is the metrics for a
(prediction, gold) pair. Everything serializes to plain dicts so task sets are
plain JSONL and reproducible.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


# --------------------------------------------------------------------------- #
# data structures
# --------------------------------------------------------------------------- #
@dataclass
class Item:
    id: str
    scenario: str                       # "a2_target_id" | "t1_dti"
    format: str                         # "target_rank" | "dti"
    question: str                       # human-readable question
    gold: Dict[str, Any]                # {label|ranking|value|abstain|sign|...}
    gold_source: str                    # provenance, e.g. "parquet aff_local via get_drug_target_binding_affinity"
    split: str = "test"                 # "train" | "dev" | "test" | "calibration"
    choices: Optional[List[str]] = None
    context_free_prompt: str = ""       # prompt used for closed-book (no LinkD context)
    entities: Dict[str, Any] = field(default_factory=dict)   # {drug, gene, disease, icd, drug_name}
    meta: Dict[str, Any] = field(default_factory=dict)       # {difficulty, stratum, construction, ...}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Item":
        return Item(**d)


@dataclass
class Prediction:
    item_id: str
    scenario: str
    condition: str                      # "linkd" | "linkd_cli" | "tooluniverse" | "ot_genetics" | "pubmed" | "closed_book"
    model: str                          # "tools-only" for deterministic conditions
    parsed: Dict[str, Any] = field(default_factory=dict)   # normalized answer mirroring gold shape
    raw_text: str = ""
    tool_calls: int = 0
    latency_s: float = 0.0
    tokens: Dict[str, int] = field(default_factory=dict)   # {in, out}
    cited_values: List[Any] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Prediction":
        return Prediction(**d)


@dataclass
class ScoredResult:
    item_id: str
    scenario: str
    condition: str
    model: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    judge: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# --------------------------------------------------------------------------- #
# JSONL I/O
# --------------------------------------------------------------------------- #
def write_jsonl(path: str, rows: List[Dict[str, Any]]) -> None:
    import os
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, default=_json_default) + "\n")


def read_jsonl(path: str) -> List[Dict[str, Any]]:
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_items(path: str) -> List[Item]:
    return [Item.from_dict(d) for d in read_jsonl(path)]


def _json_default(o):
    try:
        import numpy as np
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            f = float(o)
            return None if (f != f) else f
        if isinstance(o, np.ndarray):
            return o.tolist()
    except Exception:
        pass
    if isinstance(o, float) and o != o:   # NaN
        return None
    return str(o)
