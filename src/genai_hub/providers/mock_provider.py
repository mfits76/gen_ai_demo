import json
import re
from typing import Any

from genai_hub.providers.base import LLMMessage, LLMProvider, LLMResponse


class MockLLMProvider(LLMProvider):
    """Deterministic mock provider for demos and CI — no API key required."""

    name = "mock"

    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        system_prompt: str | None = None,
    ) -> LLMResponse:
        user_text = " ".join(m.content for m in messages if m.role == "user")
        response = self._generate_response(user_text, system_prompt)
        return LLMResponse(
            content=response,
            provider=self.name,
            model="mock-genai-v1",
            usage={"prompt_tokens": len(user_text.split()), "completion_tokens": len(response.split())},
            metadata={"temperature": temperature, "demo_mode": True},
        )

    def _generate_response(self, user_text: str, system_prompt: str | None) -> str:
        lower = user_text.lower()

        if "summar" in lower or ("document" in lower and "sharepoint" in lower) or "fasse folgendes" in lower:
            return json.dumps(
                {
                    "summary": (
                        "Das Dokument beschreibt die Q2-Integrationsroadmap: "
                        "Phase 1 CRM-Anbindung, Phase 2 ERP-Synchronisation, "
                        "Phase 3 Self-Service-Portal mit GenAI-Assistent."
                    ),
                    "key_points": [
                        "CRM-Integration bis KW 26",
                        "ERP-Datenmapping nach JSON-Schema v2",
                        "DSGVO-konforme PII-Redaktion vor LLM-Aufruf",
                    ],
                    "action_items": ["Stakeholder-Review planen", "API-Gateway konfigurieren"],
                },
                ensure_ascii=False,
            )

        if "crm-ticket" in lower or "crm ticket" in lower or ("analysiere" in lower and "ticket" in lower):
            return json.dumps(
                {
                    "intent": "support_inquiry",
                    "priority": "medium",
                    "category": "billing",
                    "suggested_response": (
                        "Vielen Dank für Ihre Anfrage. Wir prüfen Ihre Rechnung "
                        "und melden uns innerhalb von 24 Stunden."
                    ),
                    "confidence": 0.87,
                },
                ensure_ascii=False,
            )

        if "order" in lower or "bestell" in lower or "erp" in lower:
            sku_match = re.search(r"(SKU[-\s]?\w+)", user_text, re.IGNORECASE)
            qty_match = re.search(r"(\d+)\s*(?:units?|stk|stück)", user_text, re.IGNORECASE)
            return json.dumps(
                {
                    "extracted_order": {
                        "sku": sku_match.group(1).upper().replace(" ", "-") if sku_match else "UNKNOWN",
                        "quantity": int(qty_match.group(1)) if qty_match else 1,
                        "customer_ref": (
                            m.group(0) if (m := re.search(r"CUST[-\s]?\d+", user_text, re.IGNORECASE)) else None
                        ),
                    },
                    "validation_status": "pending_inventory_check",
                    "confidence": 0.82,
                },
                ensure_ascii=False,
                default=str,
            )

        return json.dumps(
            {
                "analysis": "Allgemeine Anfrage verarbeitet.",
                "reply": f"Basierend auf Ihrer Eingabe ({len(user_text)} Zeichen) empfehlen wir eine manuelle Prüfung.",
                "confidence": 0.65,
            },
            ensure_ascii=False,
        )

    async def health_check(self) -> dict[str, Any]:
        return {"status": "healthy", "provider": self.name, "mode": "demo"}
