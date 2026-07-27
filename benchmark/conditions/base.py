"""
Condition adapters: each turns an Item into a Prediction under one evaluation
condition. Shared parsing/normalization helpers live here so every adapter emits
a `parsed` dict that mirrors the gold shape.
"""
from __future__ import annotations
import json
import os
import re
import subprocess
import sys
import time
from typing import Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from benchmark.schema import Item, Prediction  # noqa: E402

CLI_PATH = os.path.join(REPO_ROOT, ".claude", "skills", "linkd", "scripts", "linkd")


class ConditionAdapter:
    name = "base"
    model = "tools-only"

    def run(self, item: Item) -> Prediction:  # pragma: no cover - abstract
        raise NotImplementedError


# --------------------------- parsing helpers ------------------------------- #
_ABSTAIN_RE = re.compile(r"\b(no data|not (?:available|found|in linkd)|cannot|can't|unknown|"
                         r"insufficient|no (?:record|evidence)|n/?a)\b", re.I)


def is_abstention(text: str) -> bool:
    return bool(_ABSTAIN_RE.search(text or ""))


def parse_yesno(text: str) -> Optional[str]:
    t = (text or "").strip().lower()
    # first standalone yes/no wins
    m = re.search(r"\b(yes|no)\b", t)
    return m.group(1) if m else None


def parse_3way(text: str) -> Optional[str]:
    t = (text or "").lower()
    if re.search(r"\bno (significant )?(change|association|effect)\b|\bnull\b|\bno change\b", t):
        return "no change"
    if re.search(r"\bdecreas|\bprotect|\blower|\breduc", t):
        return "decreased"
    if re.search(r"\bincreas|\brisk|\bhigher|\belevat", t):
        return "increased"
    return None


_THREEWAY_TO_SIGN = {"decreased": "protective", "increased": "risk", "no change": "null"}


def threeway_to_sign(label: Optional[str]) -> Optional[str]:
    return _THREEWAY_TO_SIGN.get(label) if label else None


def parse_chembl_ids(text: str, limit: int = 10) -> list:
    ids = re.findall(r"CHEMBL\d+", text or "", re.I)
    out, seen = [], set()
    for x in ids:
        x = x.upper()
        if x not in seen:
            seen.add(x); out.append(x)
        if len(out) >= limit:
            break
    return out


def parse_floats(text: str) -> list:
    return [float(x) for x in re.findall(r"-?\d+\.?\d*", text or "") if x not in (".", "-")]


def parse_role(text: str) -> Optional[str]:
    t = (text or "").lower()
    if re.search(r"\bboth\b", t):
        return "both"
    if re.search(r"tumou?r[\s-]*suppress|\btsg\b", t):
        return "tumor suppressor"
    if re.search(r"oncogen", t):
        return "oncogene"
    return None


def parse_numeric(text: str) -> Optional[float]:
    m = re.search(r"-?\d+\.?\d*", text or "")
    try:
        return float(m.group(0)) if m and m.group(0) not in (".", "-") else None
    except ValueError:
        return None


def parse_genes(text: str, limit: int = 40) -> list:
    """Extract gene-symbol-like tokens (uppercase alnum) from an LLM list."""
    import re as _re
    out, seen = [], set()
    for tok in _re.findall(r"\b[A-Z][A-Z0-9]{1,7}\b", text or ""):
        if tok in seen or tok in ("DNA", "RNA", "FDA", "MOA", "EC50", "IC50", "ATP", "GTP"):
            continue
        seen.add(tok); out.append(tok)
        if len(out) >= limit:
            break
    return out


def parse_qa3(text: str) -> Optional[str]:
    """PubMedQA yes/no/maybe."""
    t = (text or "").lower()
    if re.search(r"\bmaybe\b|\buncertain\b|\binconclusive\b|\bunclear\b", t):
        return "maybe"
    if re.search(r"\byes\b", t):
        return "yes"
    if re.search(r"\bno\b", t):
        return "no"
    return None


def parse_dti(text: str) -> dict:
    """Parse a DTI answer into {value: pKd float|None, label: yes/no|None}."""
    return {"value": parse_numeric(text), "label": parse_yesno(text),
            "abstained": is_abstention(text) and parse_numeric(text) is None}


def parse_s7(fmt: str, text: str) -> dict:
    """Parse an S7 answer into {abstained, label, value}. A concrete asserted
    value/label means NOT abstained, even if 'no data' is also present."""
    label = parse_role(text) if fmt == "s7_role" else None
    value = None if fmt == "s7_role" else parse_numeric(text)
    abstained = is_abstention(text) and value is None and label is None
    return {"abstained": abstained, "label": label, "value": value}


def cli_json(*args) -> Tuple[Optional[dict], Optional[str]]:
    """Run the linkd CLI with the same interpreter and parse its JSON stdout."""
    p = subprocess.run([sys.executable, CLI_PATH, *args], capture_output=True, text=True)
    try:
        return json.loads(p.stdout), None
    except Exception:
        return None, (p.stderr.strip().splitlines()[-1:] or ["no JSON"])[0]


class _Timer:
    def __enter__(self):
        self.t = time.time(); self.dt = 0.0; return self

    def __exit__(self, *a):
        self.dt = time.time() - self.t
