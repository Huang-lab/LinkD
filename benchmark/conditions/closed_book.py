"""
Condition B — base LLM, closed-book (no LinkD context). The A-minus-B gap is the
grounding-lift contrast. Emits an error-Prediction (never crashes) when no
provider key is available, so the runner skips it gracefully.
"""
from __future__ import annotations
from benchmark.conditions.base import (
    ConditionAdapter, _Timer, parse_yesno, parse_3way, threeway_to_sign,
    parse_chembl_ids, parse_s7, parse_dti, parse_qa3, parse_genes, is_abstention,
)
from benchmark.conditions._llm import make_client
from benchmark.schema import Item, Prediction

_FORMAT_INSTR = {
    "binary": "Answer with exactly one word: yes or no. If you do not know, answer: no data.",
    "classification": "Answer with exactly one of: increased / decreased / no change. "
                      "If you do not know, answer: no data.",
    "ranking": "Answer with a comma-separated list of up to 10 ChEMBL drug IDs, strongest first. "
               "If you do not know, answer: no data.",
    "dti": "Reply with the estimated pKd as a single number, then 'yes' or 'no' for strong binder (pKd>=7).",
    "qa3": "Answer the research question with exactly one word: yes, no, or maybe.",
    "target_rank": "List up to 25 human gene symbols (e.g. EGFR, BRAF, TP53), comma-separated, "
                   "ranked by therapeutic relevance to the disease. Output only the gene list.",
    "score_label": "Reply with a single number between 0 and 1 = your confidence the statement is "
                   "true (1 = certainly true, 0 = certainly false). Output only the number.",
    "s7_role": "Answer with one of: oncogene / tumor suppressor / both. If you do not know, answer: no data.",
    "s7_pkd": "Answer with a single number (pKd). If you do not know, answer: no data.",
    "s7_abstain": "Answer with a single number. If you do not know, answer: no data.",
    "open_ended": "Answer concisely. If LinkD/you have no data, say: no data.",
}


class ClosedBookCondition(ConditionAdapter):
    name = "closed_book"

    def __init__(self, model: str):
        self.model = model
        self._client = make_client(model)

    def run(self, item: Item) -> Prediction:
        pred = Prediction(item_id=item.id, scenario=item.scenario, condition=self.name, model=self.model)
        if self._client is None:
            pred.error = "no_provider"
            return pred
        instr = _FORMAT_INSTR.get(item.format, _FORMAT_INSTR["open_ended"])
        messages = [
            {"role": "system", "content": "You are a drug-discovery assistant. Be precise. "
                                          "Do not fabricate; if unsure, say 'no data'."},
            {"role": "user", "content": f"{item.context_free_prompt}\n\n{instr}"},
        ]
        with _Timer() as tm:
            try:
                text = self._client.chat(messages, temperature=0.0)
            except Exception as ex:  # noqa: BLE001
                pred.error = f"{type(ex).__name__}: {ex}"
                pred.latency_s = round(tm.dt, 3)
                return pred
        pred.raw_text = text
        pred.latency_s = round(tm.dt, 3)
        pred.parsed = self._parse(item.format, text)
        return pred

    @staticmethod
    def _parse(fmt, text):
        if fmt == "dti":
            return parse_dti(text)
        if fmt == "qa3":
            return {"label": parse_qa3(text)}
        if fmt == "target_rank":
            return {"ranking": parse_genes(text)}
        if fmt == "score_label":
            import re as _re
            # Take the LAST standalone number in [0,1] — the final answer after any reasoning.
            # Lookarounds reject the decimal tail of a larger number (e.g. ".29" in "pKd 7.29")
            # and list markers (e.g. "1." in "1. Potency"), which the old first-match regex grabbed
            # — that bug made verbose (tool-using) models like claude score near-random.
            cands = _re.findall(r"(?<![\d.])(?:1(?:\.0+)?|0(?:\.\d+)?|\.\d+)(?![\d.])", text)
            if not cands:
                return {"abstained": True} if is_abstention(text) else {"score": None}
            return {"score": max(0.0, min(1.0, float(cands[-1])))}
        if fmt.startswith("s7"):
            return parse_s7(fmt, text)
        if is_abstention(text) and fmt != "binary":
            return {"abstained": True}
        if fmt == "binary":
            yn = parse_yesno(text)
            if yn is None and is_abstention(text):
                return {"abstained": True}
            return {"label": yn}
        if fmt == "classification":
            lab = parse_3way(text)
            return {"label": lab, "sign": threeway_to_sign(lab)}
        if fmt == "ranking":
            return {"ranking": parse_chembl_ids(text)}
        return {"text": text}
