from typing import Any

from genai_hub.config import Settings
from genai_hub.providers.base import LLMMessage, LLMProvider, LLMResponse


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic
            except ImportError as exc:
                raise RuntimeError(
                    "Install anthropic: pip install 'genai-integration-hub[anthropic]'"
                ) from exc
            self._client = AsyncAnthropic(api_key=self._settings.anthropic_api_key)
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
        response = await client.messages.create(
            model=self._settings.anthropic_model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=[{"role": m.role, "content": m.content} for m in messages if m.role != "system"],
        )
        text = "".join(block.text for block in response.content if hasattr(block, "text"))
        return LLMResponse(
            content=text,
            provider=self.name,
            model=self._settings.anthropic_model,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
            },
        )

    async def health_check(self) -> dict[str, Any]:
        if not self._settings.anthropic_api_key:
            return {"status": "unconfigured", "provider": self.name}
        return {"status": "configured", "provider": self.name, "model": self._settings.anthropic_model}
