"""
Entity-disjoint split assignment (PyTDC-style cold split).

The same entity (gene / drug / disease) must never appear in two splits, so a
base LLM cannot benefit from having seen the entity in the judge-calibration or
dev slice. Assignment is a deterministic hash of the entity id — seed-pinned and
reproducible, no randomness.
"""
from __future__ import annotations
import hashlib

# fractions must sum to 1.0; calibration is carved from the same hash space
SPLIT_BUCKETS = [("calibration", 0.10), ("dev", 0.20), ("test", 0.70)]


def _hash_unit(key: str, salt: str = "linkd-bench-v1") -> float:
    """Stable hash of `key` -> float in [0, 1)."""
    h = hashlib.sha1(f"{salt}:{key}".encode()).hexdigest()
    return int(h[:12], 16) / float(16 ** 12)


def assign_split(entity_key: str, salt: str = "linkd-bench-v1") -> str:
    """Map an entity key (e.g. the gene or drug that anchors an item) to a split."""
    u = _hash_unit(str(entity_key), salt)
    acc = 0.0
    for name, frac in SPLIT_BUCKETS:
        acc += frac
        if u < acc:
            return name
    return SPLIT_BUCKETS[-1][0]


def split_anchor(entities: dict) -> str:
    """Pick the entity that defines disjointness for an item.

    Prefer the gene (targets recur most across scenarios); fall back to drug,
    then disease/icd. Keeps e.g. all EGFR items in one split.
    """
    for k in ("gene", "drug", "drug_name", "icd", "disease"):
        v = entities.get(k)
        if v:
            return f"{k}:{v}"
    return "none"
