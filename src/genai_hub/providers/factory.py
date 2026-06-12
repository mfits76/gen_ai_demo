from genai_hub.config import Settings, get_settings
from genai_hub.providers.anthropic_provider import AnthropicProvider
from genai_hub.providers.base import LLMProvider
from genai_hub.providers.mock_provider import MockLLMProvider
from genai_hub.providers.ollama_provider import OllamaProvider
from genai_hub.providers.openai_provider import OpenAIProvider

_PROVIDERS: dict[str, type[LLMProvider]] = {
    "mock": MockLLMProvider,
    "ollama": OllamaProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
}


def get_llm_provider(name: str | None = None, settings: Settings | None = None) -> LLMProvider:
    settings = settings or get_settings()
    provider_name = (name or settings.default_llm_provider).lower()
    if provider_name not in _PROVIDERS:
        raise ValueError(f"Unknown provider '{provider_name}'. Available: {list(_PROVIDERS)}")
    cls = _PROVIDERS[provider_name]
    if provider_name == "mock":
        return cls()
    return cls(settings)
