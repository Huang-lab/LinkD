"""
openFDA FAERS client (keyless) for the L9 safety task. Returns, per drug, the set of
reported adverse-reaction terms (MedDRA) with counts. Cached to disk for reproducibility.
"""
import json
import os
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache", "openfda_reactions.json")
_BASE = "https://api.fda.gov/drug/event.json"


def _load():
    return json.load(open(CACHE)) if os.path.exists(CACHE) else {}


def top_reactions(drug_name: str, limit: int = 60, retries: int = 4) -> dict:
    """Return {reaction_term_lower: count} for a drug, cached. {} if unreachable/none."""
    key = drug_name.lower().strip()
    cache = _load()
    if key in cache:
        return cache[key]
    q = urllib.parse.urlencode({
        "search": f'patient.drug.medicinalproduct:"{drug_name}"',
        "count": "patient.reaction.reactionmeddrapt.exact",
        "limit": limit,
    })
    out = {}
    for _ in range(retries):
        try:
            r = json.load(urllib.request.urlopen(f"{_BASE}?{q}", timeout=25))
            out = {x["term"].lower(): int(x["count"]) for x in r.get("results", [])}
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:      # no FAERS records for this drug
                out = {}
                break
            time.sleep(0.5)
        except Exception:
            time.sleep(0.5)
    cache[key] = out
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(cache, open(CACHE, "w"))
    return out
