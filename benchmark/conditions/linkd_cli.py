"""
LinkD tools-only (deterministic, no LLM). Answers the T1 binding task directly
from the `linkd` CLI JSON, so it runs with zero API keys and serves as LinkD's
predicted-pKd condition for the DAVIS comparison.
"""
from __future__ import annotations
import json
import subprocess
import sys

from benchmark.conditions.base import ConditionAdapter, CLI_PATH, _Timer
from benchmark.schema import Item, Prediction


def _cli(*args):
    p = subprocess.run([sys.executable, CLI_PATH, *args], capture_output=True, text=True)
    try:
        return json.loads(p.stdout), None
    except Exception:
        return None, (p.stderr.strip().splitlines()[-1:] or ["no JSON"])[0]


class LinkdCliCondition(ConditionAdapter):
    name = "linkd_cli"
    model = "tools-only"

    def run(self, item: Item) -> Prediction:
        e = item.entities
        pred = Prediction(item_id=item.id, scenario=item.scenario, condition=self.name, model=self.model)
        with _Timer() as tm:
            try:
                if item.format == "dti":
                    data, err = _cli("binding", e["drug"], e["gene"])
                    pred.tool_calls = 1
                    res = (data or {}).get("result")
                    pkd = res.get("binding_affinity") if res else None
                    if pkd is not None:
                        pred.cited_values = [pkd]
                        pred.parsed = {"value": float(pkd), "label": "yes" if pkd >= 7 else "no"}
                        pred.raw_text = f"pKd={pkd}"
                    else:
                        pred.parsed = {"value": None, "label": None, "abstained": True}
                        pred.raw_text = err or "no prediction"
                else:
                    pred.error = f"unsupported scenario/format for linkd_cli: {item.scenario}/{item.format}"
            except Exception as ex:  # noqa: BLE001
                pred.error = f"{type(ex).__name__}: {ex}"
        pred.latency_s = round(tm.dt, 3)
        return pred
