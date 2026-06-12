from typing import Any

from genai_hub.config import Settings
from genai_hub.providers.base import LLMMessage, LLMProvider, LLMResponse


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import AsyncOpenAI
            except ImportError as exc:
                raise RuntimeError("Install openai: pip install 'genai-integration-hub[openai]'") from exc
            self._client = AsyncOpenAI(api_key=self._settings.openai_api_key)
        return self._client

    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        system_prompt: str | None = None,
    ) -> LLMResponse:
        client = self._get_client()
        api_messages: list[dict[str, str]] = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        api_messages.extend({"role": m.role, "content": m.content} for m in messages)

        response = await client.chat.completions.create(
            model=self._settings.openai_model,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        choice = response.choices[0]
        usage = response.usage
        return LLMResponse(
            content=choice.message.content or "",
            provider=self.name,
            model=self._settings.openai_model,
            usage={
                "prompt_tokens": usage.prompt_tokens if usage else 0,
                "completion_tokens": usage.completion_tokens if usage else 0,
            },
        )

    async def health_check(self) -> dict[str, Any]:
        if not self._settings.openai_api_key:
            return {"status": "unconfigured", "provider": self.name}
        return {"status": "configured", "provider": self.name, "model": self._settings.openai_model}
