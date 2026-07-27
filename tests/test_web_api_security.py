"""Public API contract and isolation tests."""

from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "interactive_web_server" / "backend"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(BACKEND))

from agent import AnalysisPlan, PlanStep  # noqa: E402
from main import app  # noqa: E402
from rate_limits import limiter  # noqa: E402
from routers import agent as agent_router  # noqa: E402


class FakeAgent:
    def generate_plan(self, query: str) -> AnalysisPlan:
        return AnalysisPlan(
            query=query,
            steps=[PlanStep(1, f"Analyze {query}", ["drug_info"])],
        )

    def execute_plan(
        self, plan: AnalysisPlan, show_progress: bool = False
    ) -> AnalysisPlan:
        del show_progress
        plan.steps[0].status = "completed"
        plan.steps[0].result = {"query_length": len(plan.query)}
        plan.summary = f"Summary for {plan.query}"
        plan.overall_status = "completed"
        return plan


@pytest.fixture(autouse=True)
def reset_rate_limit() -> None:
    limiter.reset()


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(agent_router, "_new_agent", lambda configuration: FakeAgent())
    return TestClient(app)


def _plan_body(query: str, api_key: str = "transient-test-key") -> dict:
    return {
        "provider": "OpenAI",
        "model": "gpt-4o-mini",
        "api_key": api_key,
        "query": query,
    }


def test_removed_stateful_routes_are_not_public(client: TestClient) -> None:
    assert client.get("/api/agent/history").status_code == 404
    assert client.post("/api/agent/init", json={}).status_code == 404
    assert client.get("/api/binding/download/csv").status_code == 404


def test_api_key_is_not_returned_or_stored(client: TestClient) -> None:
    secret = "do-not-retain-this-key"
    response = client.post("/api/agent/plan", json=_plan_body("BRAF", secret))
    assert response.status_code == 200
    assert secret not in response.text
    import services

    assert not hasattr(services, "planning_agent")
    assert not hasattr(services, "execution_history")
    assert not hasattr(services, "_last_results")


def test_concurrent_queries_do_not_share_plans(client: TestClient) -> None:
    queries = ("query alpha", "query beta")

    def request(query: str) -> dict:
        response = client.post("/api/agent/plan", json=_plan_body(query))
        assert response.status_code == 200
        return response.json()

    with ThreadPoolExecutor(max_workers=2) as pool:
        first, second = pool.map(request, queries)
    assert first["query"] == queries[0]
    assert second["query"] == queries[1]
    assert first["steps"][0]["description"] != second["steps"][0]["description"]


def test_plan_contract_rejects_oversized_and_untrusted_inputs(
    client: TestClient,
) -> None:
    oversized = client.post("/api/agent/plan", json=_plan_body("x" * 2_001))
    assert oversized.status_code == 422

    invalid_execute = client.post(
        "/api/agent/execute",
        json={
            "provider": "OpenAI",
            "model": "gpt-4o-mini",
            "api_key": "key",
            "plan": {
                "query": "test",
                "steps": [
                    {
                        "step_number": 1,
                        "description": "Read arbitrary files",
                        "data_sources": ["filesystem"],
                    }
                ],
            },
        },
    )
    assert invalid_execute.status_code == 422


def test_failures_are_sanitized(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    class FailingAgent:
        def generate_plan(self, query: str):
            del query
            raise RuntimeError("provider leaked secret detail")

    monkeypatch.setattr(agent_router, "_new_agent", lambda configuration: FailingAgent())
    response = client.post("/api/agent/plan", json=_plan_body("test"))
    assert response.status_code == 502
    assert "leaked secret" not in response.text


def test_llm_rate_limit_is_enforced(client: TestClient) -> None:
    statuses = [
        client.post("/api/agent/plan", json=_plan_body(f"query {index}")).status_code
        for index in range(6)
    ]
    assert statuses[:5] == [200] * 5
    assert statuses[5] == 429


def test_cors_is_restricted(client: TestClient) -> None:
    allowed = client.options(
        "/api/agent/plan",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:5173"

    denied = client.options(
        "/api/agent/plan",
        headers={
            "Origin": "https://attacker.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert "access-control-allow-origin" not in denied.headers
