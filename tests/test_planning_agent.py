"""
End-to-end test of the LLM planning-agent path (plan -> execute -> synthesize),
exercising the new weighted evidence wiring through the agent.

Uses a partial database (load_database_subset) so it does not load the full
~16 GB corpus, and a real LLM via whichever provider key is in the environment.

Runs with plain Python (no pytest required):

    python3 tests/test_planning_agent.py

SKIPS gracefully (exit 0) when the data folder is missing OR no LLM provider key
+ package is available, so it is safe to run anywhere. It DOES make real API
calls (3 small completions) when a key is present.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from agent.database_query_module import load_database_subset  # noqa: E402

DB_DIR = os.getenv("DATABASE_DIR", os.path.join(ROOT, "Database"))
_PROBE = os.path.join(DB_DIR, os.pardir, "DrugTargetMetrics", "target_binding_stats.csv")

# provider -> (env keys to try, importable package)
_PROVIDERS = [
    ("openai", ["OPENAI_API_KEY"], "openai", "gpt-4o-mini"),
    ("claude", ["ANTHROPIC_API_KEY"], "anthropic", "claude-haiku-4-5-20251001"),
    ("gemini", ["GOOGLE_API_KEY", "GEMINI_FREE_KEY"], "google.generativeai", "gemini-2.0-flash"),
]


def _pick_provider():
    import importlib
    for provider, env_keys, pkg, model in _PROVIDERS:
        key = next((os.getenv(k) for k in env_keys if os.getenv(k)), None)
        if not key:
            continue
        try:
            importlib.import_module(pkg)
        except Exception:
            continue
        return provider, key, model
    return None


def main():
    if not os.path.exists(os.path.normpath(_PROBE)):
        print("SKIP: LinkD data folder not found (set DATABASE_DIR to enable this test).")
        return 0
    picked = _pick_provider()
    if not picked:
        print("SKIP: no LLM provider key + package available "
              "(set OPENAI_API_KEY / ANTHROPIC_API_KEY / GOOGLE_API_KEY).")
        return 0
    provider, key, model = picked
    print(f"Using provider={provider} model={model}")

    from agent import LLMClient, LLMPlanningAgent

    print("Loading partial database (medium datasets only)...")
    db = load_database_subset(database_dir=DB_DIR)  # all medium datasets
    print(f"  loaded {len(db.dfs)} datasets: {sorted(db.dfs)}")

    client = LLMClient(provider=provider, api_key=key, model=model)
    agent = LLMPlanningAgent(db=db, llm_client=client)

    query = ("Analyze erlotinib (CHEMBL553) targeting EGFR in lung cancer. "
             "Include binding affinity, drug response, EHR evidence, and a "
             "comprehensive weighted evidence assessment.")
    print(f"\nQuery: {query}\n")

    plan = agent.analyze_query(query, show_progress=False)

    failed = 0

    def expect(name, cond, detail=""):
        nonlocal failed
        print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f": {detail}" if not cond and detail else ""))
        failed += int(not cond)

    # 1. plan generation
    expect("plan has steps", len(plan.steps) >= 1, f"{len(plan.steps)} steps")
    for s in plan.steps:
        print(f"      step {s.step_number}: [{s.status}] {s.description}  sources={s.data_sources}")

    # 2. execution
    expect("plan completed", plan.overall_status == "completed", plan.overall_status)
    completed = sum(1 for s in plan.steps if s.status == "completed")
    expect("at least one step completed", completed >= 1, f"{completed}/{len(plan.steps)}")

    # 3. real data flowed into at least one step
    got_data = any(isinstance(s.result, dict) and s.result for s in plan.steps if s.status == "completed")
    expect("a step returned data", got_data)

    # 4. weighted comprehensive evidence surfaced through the agent (when planned)
    comp = None
    for s in plan.steps:
        if isinstance(s.result, dict) and "comprehensive_evidence" in s.result:
            comp = s.result["comprehensive_evidence"]
            break
    if comp is not None:
        expect("comprehensive evidence has weighted keys",
               all(k in comp for k in ("strength_score", "coverage", "verdict", "missing")),
               list(comp))
        expect("legacy overall_strength == verdict", comp.get("overall_strength") == comp.get("verdict"))
        print(f"      verdict={comp.get('verdict')} strength={comp.get('strength_score')} "
              f"coverage={comp.get('coverage')} missing={comp.get('missing')}")
    else:
        print("      NOTE: the LLM plan did not request comprehensive evidence this run "
              "(weighted path is covered by test_cli_smoke.py / test_evidence_scoring.py).")

    # 5. synthesis
    summary = plan.summary or ""
    expect("summary is non-trivial", len(summary) > 80, f"len={len(summary)}")
    expect("summary is not the bare fallback", "steps completed successfully." not in summary[:60])
    print("\n----- summary (first 600 chars) -----")
    print(summary[:600])
    print("-------------------------------------")

    print(f"\n{'ALL CHECKS PASSED' if not failed else str(failed) + ' CHECK(S) FAILED'}")
    return 1 if failed else 0


# pytest entry point (optional)
def test_planning_agent():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
