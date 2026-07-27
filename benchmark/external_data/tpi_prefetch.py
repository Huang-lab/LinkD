"""
One-time prefetch of LinkD's Target Priority Index (TPI) for the A2/A3 cancer
indications. target_priority.csv is ~900 MB, so we read only the needed columns
once and cache a small {icd: [genes ranked by TPI]} map for the linkd_tpi agent.

    python3 benchmark/external_data/tpi_prefetch.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache", "a3_tpi.json")
A2 = os.path.join(HERE, "cache", "a2_diseases.json")


def _tp_path():
    dbdir = os.getenv("DATABASE_DIR") or os.path.join(
        os.path.dirname(os.path.dirname(HERE)), "Database")
    return os.path.join(os.path.dirname(dbdir), "Target_Disease_Association", "target_priority.csv")


def build(top: int = 60):
    import pandas as pd
    if not os.path.exists(A2):
        print("  a2_diseases.json missing — run a2_prefetch first.")
        return None
    icds = {v["icd"] for v in json.load(open(A2)).values() if v.get("icd")}
    path = _tp_path()
    if not os.path.exists(path):
        print(f"  target_priority.csv not found at {path}")
        return None
    print(f"  reading TPI columns for {len(icds)} ICD codes (large file, one pass)...")
    out = {}
    cols = ["Gene", "score", "ICD_Code"]
    # chunked read keeps memory bounded on the ~900 MB file
    frames = []
    for chunk in pd.read_csv(path, usecols=cols, chunksize=500_000, low_memory=False):
        c = chunk[chunk["ICD_Code"].astype(str).isin(icds)]
        if not c.empty:
            frames.append(c)
    if frames:
        df = pd.concat(frames)
        df["score"] = pd.to_numeric(df["score"], errors="coerce")
        for icd, g in df.groupby("ICD_Code"):
            ranked = (g.groupby("Gene")["score"].max().sort_values(ascending=False)
                      .head(top).index.astype(str).tolist())
            out[str(icd)] = ranked
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(out, open(CACHE, "w"))
    print(f"  wrote TPI rankings for {len(out)} ICD codes -> {CACHE}")
    return out


if __name__ == "__main__":
    build()
