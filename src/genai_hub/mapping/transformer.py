import json
import re
from typing import Any


class DataTransformer:
    """Maps and transforms data between enterprise systems and GenAI payloads."""

    CRM_TO_LLM_TEMPLATE = (
        "Analysiere folgendes CRM-Ticket und gib eine JSON-Antwort mit "
        "intent, priority, category, suggested_response und confidence:\n\n"
        "Kunde: {customer_name}\n"
        "Betreff: {subject}\n"
        "Beschreibung: {description}\n"
        "Priorität: {priority}"
    )

    EMAIL_TO_ORDER_TEMPLATE = (
        "Extrahiere Bestelldaten aus folgender E-Mail als JSON "
        "(extracted_order mit sku, quantity, customer_ref):\n\n{text}"
    )

    @staticmethod
    def crm_ticket_to_prompt(ticket: dict[str, Any]) -> str:
        return DataTransformer.CRM_TO_LLM_TEMPLATE.format(
            customer_name=ticket.get("customer_name", "Unbekannt"),
            subject=ticket.get("subject", ""),
            description=ticket.get("description", ""),
            priority=ticket.get("priority", "medium"),
        )

    @staticmethod
    def llm_json_to_crm_update(llm_output: str, ticket_id: str) -> dict[str, Any]:
        try:
            parsed = json.loads(llm_output)
        except json.JSONDecodeError:
            parsed = {"suggested_response": llm_output, "confidence": 0.5}
        return {
            "id": ticket_id,
            "ai_analysis": parsed,
            "status": "in_progress",
            "ai_suggested_reply": parsed.get("suggested_response", ""),
        }

    @staticmethod
    def llm_json_to_erp_order(llm_output: str, customer_ref: str | None = None) -> dict[str, Any]:
        try:
            parsed = json.loads(llm_output)
        except json.JSONDecodeError:
            return {"lines": [], "customer_ref": customer_ref, "error": "parse_failed"}

        order_data = parsed.get("extracted_order", parsed)
        customer_ref_val = order_data.get("customer_ref")
        if isinstance(customer_ref_val, re.Match):
            order_data["customer_ref"] = customer_ref_val.group(0)

        sku = str(order_data.get("sku", "UNKNOWN")).upper()
        if sku != "UNKNOWN" and not sku.startswith("SKU"):
            sku = f"SKU-{sku.removeprefix('SKU-').removeprefix('SKU')}"
        quantity = int(order_data.get("quantity", 1))
        return {
            "customer_ref": customer_ref or order_data.get("customer_ref"),
            "lines": [{"sku": sku, "quantity": quantity}],
        }

    @staticmethod
    def sharepoint_doc_to_prompt(document: dict[str, Any]) -> str:
        return (
            f"Fasse folgendes interne Dokument zusammen und extrahiere key_points "
            f"und action_items als JSON:\n\n"
            f"Titel: {document.get('title', '')}\n\n"
            f"{document.get('content', '')}"
        )

    @staticmethod
    def xml_to_dict(xml_string: str) -> dict[str, Any]:
        """Minimal XML-to-dict for legacy SOAP integrations."""
        result: dict[str, Any] = {}
        for match in re.finditer(r"<(\w+)>([^<]*)</\1>", xml_string):
            result[match.group(1)] = match.group(2)
        return result
