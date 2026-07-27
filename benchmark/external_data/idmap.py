"""
Identifier harmonization between external benchmarks and LinkD's entity space.

- PubChem CID -> ChEMBL via the UniChem v1 API (on-disk cached; the legacy REST is
  retired). Retries handle transient SSL timeouts.
- DAVIS-style target labels -> base gene symbol.
- Disease name -> ICD-10 prefix (reuses the planning agent's DISEASE_MAP).
"""
from __future__ import annotations
import json
import os
import re
import time
import urllib.request

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
_CID_CACHE = os.path.join(CACHE_DIR, "cid2chembl.json")


def _load_cache(path):
    return json.load(open(path)) if os.path.exists(path) else {}


def _save_cache(path, obj):
    json.dump(obj, open(path, "w"))


def cid_to_chembl(cid: str, cache: dict = None, retries: int = 3) -> str:
    """Map a PubChem CID to a ChEMBL ID (cached). Returns None if unmapped/offline."""
    cid = str(cid)
    own = cache is None
    cache = _load_cache(_CID_CACHE) if own else cache
    if cid in cache:
        return cache[cid]
    body = json.dumps({"type": "sourceID", "compound": cid, "sourceID": 22}).encode()
    val = None
    for _ in range(retries):
        try:
            req = urllib.request.Request(
                "https://www.ebi.ac.uk/unichem/api/v1/compounds",
                data=body, headers={"Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=25))
            for c in r.get("compounds", []):
                for s in c.get("sources", []):
                    if s.get("shortName") == "chembl":
                        val = s.get("compoundId")
            break
        except Exception:
            time.sleep(0.4)
    cache[cid] = val
    if own:
        _save_cache(_CID_CACHE, cache)
    return val


def map_cids(cids, save_every: int = 10) -> dict:
    """Batch CID->ChEMBL with persistent caching."""
    cache = _load_cache(_CID_CACHE)
    for i, cid in enumerate(cids):
        cid_to_chembl(cid, cache=cache)
        if i % save_every == 0:
            _save_cache(_CID_CACHE, cache)
    _save_cache(_CID_CACHE, cache)
    return {str(c): cache.get(str(c)) for c in cids}


def normalize_gene(target_id: str, known_genes: set) -> str:
    """DAVIS-style target label (e.g. 'ABL1p', 'JAK2(JH1domain)') -> base gene symbol."""
    b = re.split(r"[(\-]", str(target_id))[0].strip()
    if b.endswith("p") and b[:-1].upper() in known_genes:
        b = b[:-1]
    return b.upper()
