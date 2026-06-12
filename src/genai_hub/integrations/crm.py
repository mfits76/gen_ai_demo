from datetime import datetime, timezone
from typing import Any

from genai_hub.integrations.base import EnterpriseConnector


class SalesforceCRMConnector(EnterpriseConnector):
    """Salesforce-style CRM connector with in-memory demo data."""

    system_name = "salesforce_crm"

    def __init__(self) -> None:
        self._tickets: dict[str, dict[str, Any]] = {
            "TKT-1001": {
                "id": "TKT-1001",
                "customer_id": "CUST-4521",
                "customer_name": "Müller AG",
                "subject": "Rechnungsabweichung Q1",
                "description": (
                    "Die Rechnung #INV-2026-034 zeigt einen Betrag von CHF 12'450, "
                    "erwartet waren CHF 11'200 laut Vertrag."
                ),
                "status": "open",
                "priority": "high",
                "region": "CH",
                "contact_email": "billing@mueller-ag.ch",
            },
            "TKT-1002": {
                "id": "TKT-1002",
                "customer_id": "CUST-8830",
                "customer_name": "TechStart GmbH",
                "subject": "API-Integrationsfrage",
                "description": "Wie binden wir Ihr GenAI-Modul an unser ERP an?",
                "status": "open",
                "priority": "medium",
                "region": "DE",
                "contact_email": "dev@techstart.de",
            },
        }

    async def fetch(self, resource_id: str) -> dict[str, Any]:
        ticket = self._tickets.get(resource_id)
        if not ticket:
            raise KeyError(f"CRM ticket '{resource_id}' not found")
        return dict(ticket)

    async def push(self, payload: dict[str, Any]) -> dict[str, Any]:
        ticket_id = payload.get("id") or f"TKT-{1000 + len(self._tickets) + 1}"
        record = {
            **payload,
            "id": ticket_id,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._tickets[ticket_id] = record
        return {"status": "upserted", "id": ticket_id, "system": self.system_name}

    async def list_open_tickets(self) -> list[dict[str, Any]]:
        return [t for t in self._tickets.values() if t.get("status") == "open"]

    async def health_check(self) -> dict[str, Any]:
        return {
            "status": "healthy",
            "system": self.system_name,
            "open_tickets": len(await self.list_open_tickets()),
        }
