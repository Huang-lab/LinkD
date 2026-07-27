"""
Cached OpenTargets client via ToolUniverse. The sandbox has flaky external SSL,
so every call retries and is cached to disk — the API is hit once, then runs are
offline and reproducible. Powers both the ToolUniverse-agent comparator and the
A2/C2 gold (approved-drug targets + first-approval year for the temporal split).
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import time

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache", "opentargets")
os.makedirs(CACHE_DIR, exist_ok=True)
_TU = None


def _tu():
    global _TU
    if _TU is None:
        from tooluniverse import ToolUniverse
        _TU = ToolUniverse()
        _TU.load_tools()
    return _TU


def available() -> bool:
    try:
        import tooluniverse  # noqa: F401
        return True
    except Exception:
        return False


def ot_call(name, args, retries=5):
    """Cached, retrying ToolUniverse call. Returns parsed dict or None on failure."""
    key = hashlib.sha1(f"{name}:{json.dumps(args, sort_keys=True)}".encode()).hexdigest()[:16]
    path = os.path.join(CACHE_DIR, f"{key}.json")
    if os.path.exists(path):
        return json.load(open(path))
    last = None
    for _ in range(retries):
        try:
            r = _tu().run({"name": name, "arguments": args})
        except Exception as e:  # noqa: BLE001
            last = {"status": "error", "error": str(e)}
            time.sleep(1.0); continue
        s = json.dumps(r)
        if isinstance(r, dict) and r.get("status") == "error" and ("SSL" in s or "unavailable" in s or "Max retries" in s):
            last = r; time.sleep(1.0); continue
        json.dump(r, open(path, "w"))
        return r
    return last


# ---- direct OpenTargets GraphQL (for genetics datatype, which the wrapped tool omits) ----
_GQL_URL = "https://api.platform.opentargets.org/api/v4/graphql"
_GQL_HEADERS = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
_GENETICS_Q = ("query($efo:String!){ disease(efoId:$efo){ associatedTargets(page:{index:0,size:80})"
               "{ rows{ target{approvedSymbol} datatypeScores{ id score } } } } }")


def _gql(query, variables, cache_key, retries=6):
    path = os.path.join(CACHE_DIR, f"gql_{cache_key}.json")
    if os.path.exists(path):
        return json.load(open(path))
    import requests
    for _ in range(retries):
        try:
            r = requests.post(_GQL_URL, json={"query": query, "variables": variables},
                              headers=_GQL_HEADERS, timeout=30)
            if r.status_code == 200:
                j = r.json()
                if (j.get("data") or {}).get("disease"):
                    json.dump(j, open(path, "w"))
                    return j
        except Exception:
            time.sleep(0.8)
    return None


def genetics_targets(efo):
    """Genetics-only ranking: targets sorted by OpenTargets genetic_association datatype score."""
    key = hashlib.sha1(f"gen:{efo}".encode()).hexdigest()[:14]
    j = _gql(_GENETICS_Q, {"efo": efo}, key)
    if not j:
        return []
    rows = j["data"]["disease"]["associatedTargets"]["rows"]
    scored = [(x["target"]["approvedSymbol"],
               next((s["score"] for s in x.get("datatypeScores", []) if s["id"] == "genetic_association"), 0))
              for x in rows]
    return [g for g, s in sorted(scored, key=lambda t: -t[1]) if s > 0]


def disease_to_efo(name):
    r = ot_call("OpenTargets_get_disease_id_description_by_name", {"diseaseName": name})
    m = re.search(r'(EFO_\d+|MONDO_\d+|HP_\d+|Orphanet_\d+)', json.dumps(r or {}))
    return m.group(1) if m else None


def associated_targets(efo, size=60):
    """Ranked [(gene, overall_score)] for a disease — the ToolUniverse-agent's answer."""
    r = ot_call("OpenTargets_get_associated_targets_by_disease_efoId", {"efoId": efo, "size": size})
    s = json.dumps(r or {})
    genes = re.findall(r'"approvedSymbol":\s*"([^"]+)"', s)
    scores = re.findall(r'"score":\s*([0-9.]+)', s)
    out, seen = [], set()
    for i, g in enumerate(genes):
        if g not in seen:
            seen.add(g)
            out.append((g, float(scores[i]) if i < len(scores) else None))
    return out


def approved_drug_chembls(efo):
    """ChEMBL IDs of drugs APPROVED *for this disease* (disease-specific maxClinicalStage
    == APPROVAL) — drops comorbidity/supportive drugs that are only trialed at low phase."""
    r = ot_call("OpenTargets_get_associated_drugs_by_disease_efoId", {"efoId": efo})
    rows = (((r or {}).get("data") or {}).get("disease") or {}).get("drugAndClinicalCandidates", {}).get("rows", [])
    out = []
    for row in rows:
        drug = row.get("drug") or {}
        if row.get("maxClinicalStage") == "APPROVAL" and drug.get("id"):
            out.append((drug["id"], drug.get("name")))
    return out


def drug_targets(chembl):
    """Target gene symbols for a drug via OpenTargets mechanism-of-action."""
    r = ot_call("OpenTargets_get_drug_mechanisms_of_action_by_chemblId", {"chemblId": chembl})
    s = json.dumps(r or {})
    return sorted(set(re.findall(r'"approvedSymbol":\s*"([^"]+)"', s)))


def validated_targets(efo):
    """GOLD for A2: genes that are targets of APPROVED drugs for the disease (clinical
    validation; OpenTargets-sourced). Independent of LinkD's tables."""
    genes = set()
    for chembl, _ in approved_drug_chembls(efo):
        genes.update(drug_targets(chembl))
    return sorted(genes)


def known_drug_targets(efo, size=200):
    """Gold helper: targets of drugs in clinical use for the disease, with the drug's
    max phase and year-of-first-approval where OpenTargets reports it.
    Returns list of {gene, drug, phase, year}."""
    r = ot_call("OpenTargets_get_associated_drugs_by_disease_efoId", {"efoId": efo, "size": size})
    s = json.dumps(r or {})
    # parse knownDrugs rows: target symbol, drug, phase, (year if present)
    rows = []
    for m in re.finditer(r'\{[^{}]*?"approvedSymbol"\s*:\s*"([^"]+)"[^{}]*?\}', s):
        rows.append(m.group(1))
    # fallback: collect symbols + phases positionally
    genes = re.findall(r'"approvedSymbol":\s*"([^"]+)"', s)
    phases = re.findall(r'"phase":\s*([0-9.]+)', s)
    years = re.findall(r'"yearOfFirstApproval":\s*(\d{4})', s)
    out = []
    for i, g in enumerate(genes):
        out.append({"gene": g,
                    "phase": float(phases[i]) if i < len(phases) else None,
                    "year": int(years[i]) if i < len(years) else None})
    return out
