"""
Unified LLM client wrapper for OpenAI, Google Gemini, and Anthropic Claude.

Provides a single chat() interface that normalizes differences between providers.
Only the selected provider's package is imported (lazy loading).
"""

from typing import List, Dict, Optional
import json

# Provider registry: models and defaults
PROVIDERS = {
    "openai": {
        # any "gpt-*"/"o*" id also routes here via prefix fallback (see _llm.provider_of),
        # so new ids (e.g. gpt-5.4) work even if not listed.
        "models": ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1",
                   "gpt-5", "gpt-5-mini", "gpt-5.4"],
        "default": "gpt-4o-mini",
        "env_key": "OPENAI_API_KEY",
    },
    "gemini": {
        "models": ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro"],
        "default": "gemini-2.5-pro",
        "env_key": "GOOGLE_API_KEY",
    },
    "claude": {
        # Most recent Claude tiers (2026): Opus 4.8 ($5/$25), Sonnet 4.6 ($3/$15), Haiku 4.5 ($1/$5)
        "models": ["claude-opus-4-8", "claude-sonnet-4-6", "claude-haiku-4-5"],
        "default": "claude-haiku-4-5",
        "env_key": "ANTHROPIC_API_KEY",
    },
}


class LLMClient:
    """Thin wrapper normalizing chat completions across LLM providers.

    Usage:
        client = LLMClient(provider="openai", api_key="sk-...", model="gpt-4o-mini")
        text = client.chat(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"},
            ],
            temperature=0.3,
            json_mode=False,
        )
    """

    def __init__(self, provider: str, api_key: str, model: Optional[str] = None):
        if provider not in PROVIDERS:
            raise ValueError(f"Unknown provider '{provider}'. Choose from: {list(PROVIDERS.keys())}")
        self.provider = provider
        self.api_key = api_key
        self.model = model or PROVIDERS[provider]["default"]
        self._client = None
        self._init_client()

    def _init_client(self):
        if self.provider == "openai":
            try:
                from openai import OpenAI
            except ImportError:
                raise ImportError("openai package required. Install with: pip install openai")
            # timeout + bounded retries so a stalled proxy connection fails fast instead of
            # hanging a whole batch forever (the default client has no request timeout).
            self._client = OpenAI(api_key=self.api_key, timeout=90.0, max_retries=2)

        elif self.provider == "gemini":
            try:
                import google.generativeai as genai
            except ImportError:
                raise ImportError("google-generativeai package required. Install with: pip install google-generativeai")
            # REST transport (HTTPS) instead of the default gRPC — gRPC's ipv6 path fails
            # in restricted/sandboxed networks.
            genai.configure(api_key=self.api_key, transport="rest")
            self._client = genai  # store module ref; model created per-call for system instruction support

        elif self.provider == "claude":
            try:
                from anthropic import Anthropic
            except ImportError:
                raise ImportError("anthropic package required. Install with: pip install anthropic")
            self._client = Anthropic(api_key=self.api_key, timeout=90.0, max_retries=2)

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.3,
             json_mode: bool = False) -> str:
        """Send chat messages and return the response text.

        Args:
            messages: List of {"role": "system"|"user"|"assistant", "content": "..."}
            temperature: Sampling temperature (0.0 - 1.0)
            json_mode: If True, request JSON-formatted output

        Returns:
            Response text string
        """
        if self.provider == "openai":
            return self._chat_openai(messages, temperature, json_mode)
        elif self.provider == "gemini":
            return self._chat_gemini(messages, temperature, json_mode)
        elif self.provider == "claude":
            return self._chat_claude(messages, temperature, json_mode)

    def run_tools(self, system, user, tools, executor, max_rounds: int = 6,
                  max_tokens: int = 1024, temperature: float = 0.0):
        """Native function-calling loop. The model decides which tools to call; `executor(name,
        args) -> str` runs them; loop until the model returns a final text answer.

        tools: provider-agnostic list of {"name", "description", "parameters": <JSON schema>}.
        Returns (final_text, trace) where trace = [{"name", "args", "result"}].
        OpenAI + Anthropic only (Gemini geo-blocked here). Falls back to plain chat on others.
        """
        if self.provider == "openai":
            return self._run_tools_openai(system, user, tools, executor, max_rounds, temperature)
        if self.provider == "claude":
            return self._run_tools_claude(system, user, tools, executor, max_rounds, max_tokens, temperature)
        # no tool support -> single plain answer, empty trace
        return self.chat([{"role": "system", "content": system},
                          {"role": "user", "content": user}], temperature=temperature), []

    def _run_tools_openai(self, system, user, tools, executor, max_rounds, temperature):
        oai_tools = [{"type": "function", "function": {
            "name": t["name"], "description": t["description"],
            "parameters": t.get("parameters", {"type": "object", "properties": {}})}} for t in tools]
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        reasoning = self.model.startswith(("gpt-5", "o1", "o3", "o4"))
        trace = []
        for _ in range(max_rounds):
            kw = {"model": self.model, "messages": messages, "tools": oai_tools, "tool_choice": "auto"}
            if not reasoning:
                kw["temperature"] = temperature
            try:
                resp = self._client.chat.completions.create(**kw)
            except Exception:
                kw.pop("temperature", None)
                resp = self._client.chat.completions.create(**kw)
            msg = resp.choices[0].message
            if not getattr(msg, "tool_calls", None):
                return (msg.content or ""), trace
            messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls]})
            for tc in msg.tool_calls:
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except Exception:
                    args = {}
                result = str(executor(tc.function.name, args))
                trace.append({"name": tc.function.name, "args": args, "result": result[:300]})
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
        # ran out of rounds -> force a final answer
        final = self._client.chat.completions.create(model=self.model, messages=messages)
        return (final.choices[0].message.content or ""), trace

    def _run_tools_claude(self, system, user, tools, executor, max_rounds, max_tokens, temperature):
        cl_tools = [{"name": t["name"], "description": t["description"],
                     "input_schema": t.get("parameters", {"type": "object", "properties": {}})}
                    for t in tools]
        messages = [{"role": "user", "content": user}]
        trace = []
        for _ in range(max_rounds):
            resp = self._client.messages.create(model=self.model, max_tokens=max_tokens,
                                                system=system, messages=messages, tools=cl_tools)
            messages.append({"role": "assistant", "content": resp.content})
            tool_uses = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]
            if resp.stop_reason != "tool_use" or not tool_uses:
                return "".join(b.text for b in resp.content if getattr(b, "type", None) == "text"), trace
            results = []
            for tu in tool_uses:
                result = str(executor(tu.name, tu.input or {}))
                trace.append({"name": tu.name, "args": tu.input, "result": result[:300]})
                results.append({"type": "tool_result", "tool_use_id": tu.id, "content": result})
            messages.append({"role": "user", "content": results})
        final = self._client.messages.create(model=self.model, max_tokens=max_tokens,
                                              system=system, messages=messages)
        return "".join(b.text for b in final.content if getattr(b, "type", None) == "text"), trace

    def _chat_openai(self, messages, temperature, json_mode):
        kwargs = {"model": self.model, "messages": messages}
        # GPT-5 / o-series reasoning models reject a custom temperature (only default=1).
        reasoning = self.model.startswith(("gpt-5", "o1", "o3", "o4"))
        if not reasoning:
            kwargs["temperature"] = temperature
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        try:
            response = self._client.chat.completions.create(**kwargs)
        except Exception:
            # robust fallback: drop temperature, swap max_tokens naming for reasoning models
            kwargs.pop("temperature", None)
            response = self._client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    def _chat_gemini(self, messages, temperature, json_mode):
        # Separate system message from conversation
        system_msg = None
        contents = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({"role": role, "parts": [msg["content"]]})

        # Create model with system instruction (Gemini requires this at model level)
        model = self._client.GenerativeModel(
            self.model,
            system_instruction=system_msg,
        )

        generation_config = {"temperature": temperature}
        if json_mode:
            generation_config["response_mime_type"] = "application/json"

        response = model.generate_content(contents, generation_config=generation_config)
        return response.text

    def _chat_claude(self, messages, temperature, json_mode):
        # Claude uses a separate system parameter
        system_msg = None
        api_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                api_messages.append({"role": msg["role"], "content": msg["content"]})

        # Claude has no native JSON mode; enforce via system prompt
        if json_mode:
            json_instruction = "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no explanation, no extra text."
            if system_msg:
                system_msg += json_instruction
            else:
                system_msg = "You are a helpful assistant." + json_instruction

        kwargs = {
            "model": self.model,
            "messages": api_messages,
            "max_tokens": 4096,
        }
        # Opus 4.7/4.8 and Fable/Mythos reject sampling params (temperature/top_p) -> 400.
        if not (self.model.startswith(("claude-opus-4-7", "claude-opus-4-8",
                                       "claude-fable", "claude-mythos"))):
            kwargs["temperature"] = temperature
        if system_msg:
            kwargs["system"] = system_msg

        response = self._client.messages.create(**kwargs)
        return response.content[0].text
