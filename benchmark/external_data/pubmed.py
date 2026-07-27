"""
Lightweight PubMed literature-mining client (NCBI E-utilities, keyless, cached).
Used to build a *literature agent* target-ID baseline: rank candidate genes by
co-mention frequency with the disease in PubMed abstracts. No install, no model —
a genuinely different strategy (text mining) vs structured-DB agents.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import time
import urllib.parse
import urllib.request
from collections import Counter

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache", "pubmed")
os.makedirs(CACHE_DIR, exist_ok=True)
_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def _get(url, retries=4, parse_json=False):
    for _ in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=25) as r:
                data = r.read().decode("utf-8", "ignore")
            return json.loads(data) if parse_json else data
        except Exception:
            time.sleep(0.5)
    return None


def _abstracts(disease, n=80):
    """Cached PubMed abstract text blob for a disease's target literature."""
    key = hashlib.sha1(f"{disease}:{n}".encode()).hexdigest()[:14]
    path = os.path.join(CACHE_DIR, f"{key}.txt")
    if os.path.exists(path):
        return open(path, encoding="utf-8").read()
    term = f'"{disease}" AND (therapeutic target OR drug target OR molecular target OR oncogene)'
    es = _get(f"{_BASE}/esearch.fcgi?db=pubmed&term={urllib.parse.quote(term)}&retmax={n}&retmode=json",
              parse_json=True)
    ids = (((es or {}).get("esearchresult") or {}).get("idlist")) or []
    if not ids:
        open(path, "w").write(""); return ""
    time.sleep(0.4)
    txt = _get(f"{_BASE}/efetch.fcgi?db=pubmed&id={','.join(ids)}&rettype=abstract&retmode=text") or ""
    open(path, "w", encoding="utf-8").write(txt)
    return txt


def target_mentions(disease, vocab, n_abstracts=80):
    """Ranked [gene, ...] by co-mention count with the disease in PubMed abstracts,
    restricted to a candidate `vocab` (set of gene symbols)."""
    blob = _abstracts(disease, n_abstracts)
    if not blob:
        return []
    toks = Counter(re.findall(r"\b[A-Z][A-Z0-9]{1,7}\b", blob))
    ranked = [(g, c) for g, c in toks.most_common() if g in vocab]
    return [g for g, _ in ranked]
