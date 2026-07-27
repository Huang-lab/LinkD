"""Stateless LLM planning and execution endpoints."""

from __future__ import annotations

import logging
import os
from typing import Literal

import pandas as pd
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, SecretStr, field_validator, model_validator

from agent import AnalysisPlan, LLMClient, LLMPlanningAgent, PlanStep
from rate_limits import limiter
from services import PROVIDER_MAP, PROVIDERS, db


router = APIRouter()
logger = logging.getLogger("linkd.agent")
LLM_RATE_LIMIT = "5/minute"
ALLOWED_DATA_SOURCES = frozenset(
    {
        "drug_info",
        "target_info",
        "binding_affinity",
        "drug_response",
        "ehr",
        "comprehensive",
    }
)
PlanStatus = Literal["pending", "in_progress", "completed", "failed"]


class ProviderConfiguration(BaseModel):
    provider: str = Field(default="OpenAI", min_length=1, max_length=40)
    model: str = Field(default="gpt-4o-mini", min_length=1, max_length=100)
    api_key: SecretStr | None = Field(default=None, repr=False)

    @model_validator(mode="after")
    def validate_provider_and_model(self) -> "ProviderConfiguration":
        if self.provider not in PROVIDER_MAP:
            raise ValueError("Unsupported LLM provider")
        provider_key, models = PROVIDER_MAP[self.provider]
        if self.model not in models:
            raise ValueError(
                f"Unsupported model for {self.provider}; choose one of: {', '.join(models)}"
            )
        if provider_key not in PROVIDERS:
            raise ValueError("Unsupported LLM provider")
        return self


class PlanRequest(ProviderConfiguration):
    query: str = Field(min_length=1, max_length=2_000)

    @field_validator("query")
    @classmethod
    def clean_query(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Query must not be blank")
        return cleaned


class PlanStepPayload(BaseModel):
    step_number: int = Field(ge=1, le=6)
    description: str = Field(min_length=1, max_length=500)
    data_sources: list[str] = Field(min_length=1, max_length=6)
    status: PlanStatus = "pending"

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Step description must not be blank")
        return cleaned

    @field_validator("data_sources")
    @classmethod
    def validate_sources(cls, values: list[str]) -> list[str]:
        unique = list(dict.fromkeys(values))
        unsupported = sorted(set(unique) - ALLOWED_DATA_SOURCES)
        if unsupported:
            raise ValueError("Unsupported LinkD data source: " + ", ".join(unsupported))
        return unique


class PlanPayload(BaseModel):
    query: str = Field(min_length=1, max_length=2_000)
    steps: list[PlanStepPayload] = Field(min_length=1, max_length=6)

    @model_validator(mode="after")
    def validate_step_numbers(self) -> "PlanPayload":
        numbers = [step.step_number for step in self.steps]
        if numbers != list(range(1, len(numbers) + 1)):
            raise ValueError("Plan steps must be numbered consecutively from 1")
        return self


class ExecuteRequest(ProviderConfiguration):
    plan: PlanPayload


def _api_key(configuration: ProviderConfiguration) -> str:
    supplied = (
        configuration.api_key.get_secret_value().strip()
        if configuration.api_key is not None
        else ""
    )
    if supplied:
        return supplied
    provider_key = PROVIDER_MAP[configuration.provider][0]
    configured = os.getenv(PROVIDERS[provider_key]["env_key"], "").strip()
    if not configured and configuration.provider == "Google Gemini":
        configured = os.getenv("GEMINI_FREE_KEY", "").strip()
    if not configured:
        raise HTTPException(
            status_code=400,
            detail=f"An API key is required for {configuration.provider}.",
        )
    return configured


def _new_agent(configuration: ProviderConfiguration) -> LLMPlanningAgent:
    provider_key = PROVIDER_MAP[configuration.provider][0]
    client = LLMClient(
        provider=provider_key,
        api_key=_api_key(configuration),
        model=configuration.model,
    )
    return LLMPlanningAgent(llm_client=client, db=db)


def _payload_from_plan(plan: AnalysisPlan) -> PlanPayload:
    steps = [
        PlanStepPayload(
            step_number=index,
            description=step.description,
            data_sources=step.data_sources,
            status="pending",
        )
        for index, step in enumerate(plan.steps[:6], start=1)
    ]
    if not steps:
        raise ValueError("The model returned an empty analysis plan")
    return PlanPayload(query=plan.query, steps=steps)


def _analysis_plan(payload: PlanPayload) -> AnalysisPlan:
    return AnalysisPlan(
        query=payload.query,
        steps=[
            PlanStep(
                step_number=step.step_number,
                description=step.description,
                data_sources=step.data_sources,
                status="pending",
            )
            for step in payload.steps
        ],
    )


def _format_result(result: object) -> str:
    """Format a bounded, non-sensitive summary of one execution result."""
    if result is None:
        return "No data returned."
    if isinstance(result, pd.DataFrame):
        names: list[str] = []
        for column in ("Drug Name", "Drug Chembl ID", "Gene", "Disease Description"):
            if column in result.columns:
                values = result[column].dropna().astype(str).unique()[:5]
                if len(values):
                    names.append(f"{column}: {', '.join(values)}")
        preview = "; ".join(names) or ", ".join(map(str, result.columns[:5]))
        return f"Found {len(result)} records. {preview}"
    if isinstance(result, dict):
        parts: list[str] = []
        for key, value in list(result.items())[:20]:
            if isinstance(value, pd.DataFrame):
                parts.append(f"{key}: {len(value)} records")
            elif isinstance(value, list):
                parts.append(f"{key}: {len(value)} items")
            elif isinstance(value, (int, float)):
                parts.append(f"{key}: {value}")
            elif isinstance(value, str) and len(value) < 100:
                parts.append(f"{key}: {value}")
        return "; ".join(parts) or f"{len(result)} fields returned"
    if isinstance(result, list):
        return f"Found {len(result)} items"
    return str(result)[:200]


@router.post("/agent/plan")
@limiter.limit(LLM_RATE_LIMIT)
def agent_plan(request: Request, body: PlanRequest):
    """Generate a validated, bounded LinkD analysis plan."""
    del request
    try:
        plan = _new_agent(body).generate_plan(body.query)
        validated = _payload_from_plan(plan)
        return {"status": "ok", **validated.model_dump()}
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Planning request failed (%s)", type(exc).__name__)
        raise HTTPException(
            status_code=502,
            detail="Planning request failed. Verify the provider configuration and try again.",
        ) from None


@router.post("/agent/execute")
@limiter.limit(LLM_RATE_LIMIT)
def agent_execute(request: Request, body: ExecuteRequest):
    """Execute only the validated plan supplied in this HTTPS request."""
    del request
    try:
        executed = _new_agent(body).execute_plan(
            _analysis_plan(body.plan), show_progress=False
        )
        steps = []
        for step in executed.steps:
            item = {
                "step_number": step.step_number,
                "description": step.description,
                "data_sources": step.data_sources,
                "status": step.status,
                "error": (
                    "This analysis step could not be completed."
                    if step.error
                    else None
                ),
            }
            if step.result is not None:
                item["result_summary"] = _format_result(step.result)
            steps.append(item)
        return {
            "status": "ok",
            "query": executed.query,
            "steps": steps,
            "summary": executed.summary or "",
            "overall_status": executed.overall_status,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Execution request failed (%s)", type(exc).__name__)
        raise HTTPException(
            status_code=502,
            detail="Plan execution failed. Verify the plan and provider configuration.",
        ) from None


@router.get("/agent/providers")
def agent_providers():
    """Return the fixed provider/model allowlist; no credentials are returned."""
    return {
        display_name: {
            "key": key,
            "models": models,
            "default": PROVIDERS[key]["default"],
        }
        for display_name, (key, models) in PROVIDER_MAP.items()
    }
