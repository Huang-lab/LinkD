#!/usr/bin/env python3
"""Execute all For Reviewer notebooks headlessly (nbclient)."""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

NOTEBOOKS = [
    "00_Setup_and_Data_Check.ipynb",
    "Figure1_LinkD_Bind_Benchmark.ipynb",
    "FigureS2_Bind_Quantitative.ipynb",
    "Figure2_LinkD_Select.ipynb",
    "Figure3_LinkD_Pheno.ipynb",
    "Figure4_EHR_Validation.ipynb",
    "FigureS5_EHR_Volcano.ipynb",
    "Figure5_BetaBlocker_ADRB2.ipynb",
    "Figure6_LinkD_Agent.ipynb",
    "FigureS3_S4_Tissue_Resolved.ipynb",
]


def main() -> int:
    try:
        import nbformat
        from nbclient import NotebookClient
    except ImportError:
        print("Install deps: pip install -r requirements-repro.txt")
        return 1

    import matplotlib
    matplotlib.use("Agg")

    log_path = ROOT / "outputs" / "run_log.txt"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    ok, fail = [], []
    with log_path.open("w") as log:
        for name in NOTEBOOKS:
            nb_path = ROOT / "notebooks" / name
            print(f"=== {name} ===")
            log.write(f"=== {name} ===\n")
            try:
                nb = nbformat.read(nb_path, as_version=4)
                client = NotebookClient(
                    nb,
                    timeout=1200,
                    kernel_name="python3",
                    resources={"metadata": {"path": str(ROOT / "notebooks")}},
                )
                client.execute()
                nbformat.write(nb, nb_path)
                ok.append(name)
                log.write("OK\n")
                print("OK")
            except Exception as e:
                fail.append(name)
                msg = f"FAIL: {e}\n{traceback.format_exc()}"
                log.write(msg + "\n")
                print(msg)
    print(f"\nDone. OK={len(ok)} FAIL={len(fail)}")
    print("Log:", log_path)
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
