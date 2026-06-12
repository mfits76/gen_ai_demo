from abc import ABC, abstractmethod
from typing import Any


class EnterpriseConnector(ABC):
    """Base class for enterprise system connectors (CRM, ERP, collaboration)."""

    system_name: str

    @abstractmethod
    async def fetch(self, resource_id: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def push(self, payload: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        ...
