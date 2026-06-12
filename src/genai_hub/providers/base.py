from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMMessage:
    role: str
    content: str


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    usage: dict[str, int] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class LLMProvider(ABC):
    """Abstract base for GenAI model providers (OpenAI, Anthropic, Azure, etc.)."""

    name: str

    @abstractmethod
    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        system_prompt: str | None = None,
    ) -> LLMResponse:
        ...

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        ...
