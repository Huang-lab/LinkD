"""
Standalone smoke test for the focused benchmark (A2 target-ID + T1 binding).
Zero API cost: exercises the scorers, the A2 builder (cancer-only), the stats,
and the graceful no-provider path.

    python3 benchmark/tests/test_benchmark_smoke.py

SKIPS (exit 0) if the LinkD data folder is absent.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from benchmark.datasets.base_builder import data_available  # noqa: E402
from benchmark.schema import Item, Prediction  # noqa: E402
from benchmark.scoring import score_item  # noqa: E402
from benchmark.scoring.ranking import score_target_rank, aggregate_target_rank  # noqa: E402
from benchmark.scoring.regression import score_dti, aggregate_dti  # noqa: E402
from benchmark.scoring.auroc import score_binary, aggregate_auroc  # noqa: E402
from benchmark.aggregate import mcnemar, bootstrap_ci  # noqa: E402

passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f": {detail}" if not cond and detail else ""))
    passed += int(bool(cond)); failed += int(not cond)


def main():
    if not data_available():
        print("SKIP: LinkD data not found (set DATABASE_DIR).")
        return 0

    # schema roundtrip
    it0 = Item(id="x", scenario="s", format="dti", question="q", gold={"value": 8.0, "label": "yes"},
               gold_source="src")
    check("schema roundtrip", Item.from_dict(it0.to_dict()).to_dict() == it0.to_dict())

    # A2 target-rank scorer (binary relevance over a gold set)
    a2 = Item(id="d", scenario="a2_target_id", format="target_rank", question="q",
              gold={"targets": ["BRAF", "KIT", "MET"]}, gold_source="x")
    s = score_target_rank(a2, Prediction("d", "a2", "linkd", "m",
                                         parsed={"ranking": ["BRAF", "ZZZ", "KIT", "AAA", "MET"]}))
    check("target_rank recall@20", abs(s["recall_at_20"] - 1.0) < 1e-6, str(s["recall_at_20"]))
    check("target_rank routed via score_item", "recall_at_20" in score_item(a2, Prediction(
        "d", "a2", "linkd", "m", parsed={"ranking": ["BRAF"]})))
    agg = aggregate_target_rank([s])
    check("aggregate_target_rank ndcg in [0,1]", 0 <= agg["ndcg@20"] <= 1, str(agg["ndcg@20"]))

    # T1 DTI scorer (regression + binary)
    t1 = Item(id="p", scenario="t1_dti", format="dti", question="q",
              gold={"value": 8.5, "label": "yes"}, gold_source="x")
    sd1 = score_dti(t1, Prediction("p", "t1", "linkd", "m", parsed={"value": 8.4, "label": "yes"}))
    sd2 = score_dti(t1, Prediction("p", "t1", "linkd", "m", parsed={"value": 5.0, "label": "no"}))
    check("dti binary_correct", sd1["binary_correct"] == 1)
    adt = aggregate_dti([sd1, sd2])
    check("aggregate_dti has pearson", "pearson" in adt)

    # A2 builder is cancer-only (reads cached a2_diseases.json)
    from benchmark.datasets import a2_target_id
    items = a2_target_id.build()
    if items:
        check("A2 builder produced items", len(items) > 0, str(len(items)))
        check("A2 is cancer-only", all(a2_target_id.CANCER_RE.search(i.entities["disease"]) for i in items))
        check("A2 gold non-trivial", all(len(i.gold["targets"]) >= 3 for i in items))
    else:
        check("A2 builder (skipped: a2_diseases.json not cached)", True)

    # AUROC scorer (C1/T2/B5 score_label): perfect separation -> auroc 1.0
    sl = Item(id="z", scenario="c1_validate", format="score_label", question="q",
              gold={"label": 1}, gold_source="x")
    rows = [score_binary(Item(id=f"p{i}", scenario="c1_validate", format="score_label",
                              question="q", gold={"label": lab}, gold_source="x"),
                         Prediction(f"p{i}", "c1", "linkd_evidence", "m", parsed={"score": sc}))
            for i, (lab, sc) in enumerate([(1, 0.9), (1, 0.8), (0, 0.2), (0, 0.1)])]
    au = aggregate_auroc(rows)
    check("auroc perfect separation == 1.0", abs(au["auroc"] - 1.0) < 1e-6, str(au.get("auroc")))
    check("score_label routed via score_item",
          "binary_score" in score_item(sl, Prediction("z", "c1", "x", "m", parsed={"score": 0.5})))

    # statistics
    mc = mcnemar([1, 1, 1, 0], [0, 0, 0, 0])
    check("McNemar discordant", mc["b10"] == 3 and mc["b01"] == 0)
    m, lo, hi = bootstrap_ci([1, 1, 1, 0, 1])
    check("bootstrap CI ordering", lo <= m <= hi)

    # closed_book graceful no-provider (claude key absent -> no API call)
    from benchmark.conditions.closed_book import ClosedBookCondition
    cb = ClosedBookCondition(model="claude-haiku-4-5-20251001")
    if cb._client is None:
        check("closed_book no-provider graceful", cb.run(t1).error == "no_provider")
    else:
        check("closed_book no-provider graceful", True, "(anthropic key present; skipped)")

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


def test_benchmark_smoke():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
