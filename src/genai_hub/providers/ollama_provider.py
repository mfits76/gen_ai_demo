from typing import Any

import httpx

from genai_hub.config import Settings
from genai_hub.providers.base import LLMMessage, LLMProvider, LLMResponse


class OllamaProvider(LLMProvider):
    """Local LLM via Ollama native chat API (POST /api/chat)."""

    name = "ollama"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._base_url = settings.ollama_base_url.rstrip("/")

    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        system_prompt: str | None = None,
    ) -> LLMResponse:
        api_messages: list[dict[str, str]] = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        api_messages.extend({"role": m.role, "content": m.content} for m in messages)

        payload = {
            "model": self._settings.ollama_model,
            "messages": api_messages,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{self._base_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()

        content = data.get("message", {}).get("content", "")
        eval_count = data.get("eval_count", 0)
        prompt_eval_count = data.get("prompt_eval_count", 0)
        return LLMResponse(
            content=content,
            provider=self.name,
            model=self._settings.ollama_model,
            usage={
                "prompt_tokens": prompt_eval_count,
                "completion_tokens": eval_count,
            },
        )

    async def health_check(self) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self._base_url}/api/tags")
                response.raise_for_status()
                models = [m["name"] for m in response.json().get("models", [])]
                model_available = any(
                    m == self._settings.ollama_model or m.startswith(f"{self._settings.ollama_model}:")
                    for m in models
                )
                return {
                    "status": "healthy" if model_available else "model_not_found",
                    "provider": self.name,
                    "model": self._settings.ollama_model,
                    "base_url": self._base_url,
                    "available_models": models,
                }
        except httpx.HTTPError as exc:
            return {
                "status": "unreachable",
                "provider": self.name,
                "base_url": self._base_url,
                "error": str(exc),
            }
