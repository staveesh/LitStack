"""LLM provider abstraction. Add providers here; never scatter LLM calls in routers."""
from abc import ABC, abstractmethod
from typing import Any, Type
from pydantic import BaseModel
import json


class LLMProvider(ABC):
    @abstractmethod
    async def complete_structured(
        self,
        system: str,
        user: str,
        schema: Type[BaseModel],
        model: str | None = None,
    ) -> BaseModel:
        """Return a Pydantic model instance parsed from structured LLM output."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str: ...


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-sonnet-5"):
        import anthropic
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    @property
    def model_name(self) -> str:
        return self._model

    async def complete_structured(self, system: str, user: str, schema: Type[BaseModel], model: str | None = None) -> BaseModel:
        import anthropic
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        full_system = f"{system}\n\nRespond with valid JSON matching this schema:\n{schema_json}"
        msg = await self._client.messages.create(
            model=model or self._model,
            max_tokens=4096,
            system=full_system,
            messages=[{"role": "user", "content": user}],
        )
        raw = msg.content[0].text
        # strip markdown code fences if present
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return schema.model_validate_json(raw)


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: str | None = None):
        from openai import AsyncOpenAI
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    @property
    def model_name(self) -> str:
        return self._model

    async def complete_structured(self, system: str, user: str, schema: Type[BaseModel], model: str | None = None) -> BaseModel:
        resp = await self._client.beta.chat.completions.parse(
            model=model or self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format=schema,
        )
        return resp.choices[0].message.parsed


def get_provider() -> LLMProvider:
    from app.config import settings
    if settings.default_ai_provider == "anthropic" and settings.anthropic_api_key:
        return AnthropicProvider(api_key=settings.anthropic_api_key)
    if settings.default_ai_provider == "openai" and settings.openai_api_key:
        return OpenAIProvider(api_key=settings.openai_api_key)
    if settings.default_ai_provider == "local" and settings.local_llm_base_url:
        return OpenAIProvider(
            api_key="local",
            model=settings.local_llm_model or "local-model",
            base_url=settings.local_llm_base_url,
        )
    # fallback: try each in order
    if settings.anthropic_api_key:
        return AnthropicProvider(api_key=settings.anthropic_api_key)
    if settings.openai_api_key:
        return OpenAIProvider(api_key=settings.openai_api_key)
    raise RuntimeError("No AI provider configured. Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env")
