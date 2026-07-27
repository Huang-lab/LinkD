"""LLM helpers shared by LLM-backed conditions and the judge."""
from __future__ import annotations
import importlib
import os
from typing import Optional, Tuple

from benchmark.conditions.base import REPO_ROOT  # noqa: F401  (ensures sys.path)
from agent.llm_client import LLMClient, PROVIDERS

_PKG = {"openai": "openai", "gemini": "google.generativeai", "claude": "anthropic"}


def provider_of(model: str) -> Optional[str]:
    for prov, spec in PROVIDERS.items():
        if model in spec["models"] or model == spec["default"]:
            return prov
    # prefix fallback so brand-new model IDs route without editing the registry
    if model.startswith(("gpt-", "o1", "o3", "o4", "chatgpt")):
        return "openai"
    if model.startswith("claude-"):
        return "claude"
    if model.startswith("gemini-"):
        return "gemini"
    return None


def key_for(provider: str) -> Optional[str]:
    env = PROVIDERS[provider]["env_key"]
    val = os.getenv(env)
    if not val and provider == "gemini":
        val = os.getenv("GEMINI_FREE_KEY")
    return val


def available(provider: str) -> bool:
    if not key_for(provider):
        return False
    try:
        importlib.import_module(_PKG[provider])
        return True
    except Exception:
        return False


def make_client(model: str) -> Optional[LLMClient]:
    prov = provider_of(model)
    if not prov or not available(prov):
        return None
    return LLMClient(provider=prov, api_key=key_for(prov), model=model)


def first_available_model(preferred=("gpt-4o-mini", "claude-haiku-4-5", "gemini-2.0-flash")) -> Optional[str]:
    for m in preferred:
        if make_client(m):
            return m
    for prov, spec in PROVIDERS.items():
        if available(prov):
            return spec["default"]
    return None
