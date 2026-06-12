import json
import time
from typing import Any

import structlog

from genai_hub.config import Settings, get_settings
from genai_hub.integrations.crm import SalesforceCRMConnector
from genai_hub.integrations.erp import SAPERPConnector
from genai_hub.integrations.sharepoint import SharePointConnector
from genai_hub.mapping.transformer import DataTransformer
from genai_hub.providers.base import LLMMessage
from genai_hub.providers.factory import get_llm_provider
from genai_hub.security.governance import DataGovernance
from genai_hub.workflows.models import WorkflowResult, WorkflowStatus, WorkflowStepResult

logger = structlog.get_logger()


def _parse_llm_json(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text}


class WorkflowEngine:
    """Orchestrates multi-step GenAI integration workflows across enterprise systems."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.crm = SalesforceCRMConnector()
        self.erp = SAPERPConnector()
        self.sharepoint = SharePointConnector()
        self.transformer = DataTransformer()
        regions = [r.strip() for r in self.settings.allowed_data_regions.split(",")]
        self.governance = DataGovernance(
            redaction_enabled=self.settings.pii_redaction_enabled,
            allowed_regions=regions,
        )

    async def _run_step(self, name: str, system: str, fn) -> WorkflowStepResult:
        start = time.perf_counter()
        try:
            output = await fn()
            duration = (time.perf_counter() - start) * 1000
            return WorkflowStepResult(step=name, system=system, status="ok", output=output, duration_ms=duration)
        except Exception as exc:
            duration = (time.perf_counter() - start) * 1000
            logger.error("workflow_step_failed", step=name, error=str(exc))
            return WorkflowStepResult(
                step=name, system=system, status="error", output={"error": str(exc)}, duration_ms=duration
            )

    async def crm_ticket_triage(self, ticket_id: str, provider_name: str | None = None) -> WorkflowResult:
        """CRM → PII redaction → LLM analysis → CRM update."""
        result = WorkflowResult(workflow_name="crm_ticket_triage", status=WorkflowStatus.RUNNING)
        provider = get_llm_provider(provider_name, self.settings)

        ticket_step = await self._run_step("fetch_ticket", "salesforce_crm", lambda: self.crm.fetch(ticket_id))
        result.steps.append(ticket_step)
        if ticket_step.status == "error":
            result.status = WorkflowStatus.FAILED
            return result

        ticket = ticket_step.output
        prompt = self.transformer.crm_ticket_to_prompt(ticket)
        safe_prompt, gov_report = self.governance.prepare_for_llm(prompt, ticket)
        result.governance = {
            "redacted_fields": gov_report.redacted_fields,
            "region_allowed": gov_report.allowed_region,
            "warnings": gov_report.warnings,
        }

        if not gov_report.allowed_region:
            result.status = WorkflowStatus.FAILED
            result.final_output = {"error": "Data region not permitted for LLM processing"}
            return result

        async def llm_call():
            response = await provider.complete(
                [LLMMessage(role="user", content=safe_prompt)],
                system_prompt="Du bist ein CRM-Assistent. Antworte nur mit validem JSON.",
            )
            return {"llm_response": response.content, "provider": response.provider, "usage": response.usage}

        llm_step = await self._run_step("llm_analysis", provider.name, llm_call)
        result.steps.append(llm_step)

        async def update_crm():
            update = self.transformer.llm_json_to_crm_update(llm_step.output["llm_response"], ticket_id)
            return await self.crm.push(update)

        update_step = await self._run_step("update_crm", "salesforce_crm", update_crm)
        result.steps.append(update_step)

        result.status = WorkflowStatus.COMPLETED if update_step.status == "ok" else WorkflowStatus.FAILED
        result.final_output = {
            "ticket_id": ticket_id,
            "ai_analysis": _parse_llm_json(llm_step.output.get("llm_response", "{}")) if llm_step.status == "ok" else {},
            "crm_update": update_step.output,
        }
        return result

    async def email_order_extraction(
        self, email_text: str, customer_ref: str | None = None, provider_name: str | None = None
    ) -> WorkflowResult:
        """Unstructured email → LLM extraction → ERP inventory check → draft order."""
        result = WorkflowResult(workflow_name="email_order_extraction", status=WorkflowStatus.RUNNING)
        provider = get_llm_provider(provider_name, self.settings)

        safe_text, gov_report = self.governance.prepare_for_llm(email_text)
        result.governance = {"redacted_fields": gov_report.redacted_fields}

        prompt = self.transformer.EMAIL_TO_ORDER_TEMPLATE.format(text=safe_text)

        async def llm_call():
            response = await provider.complete([LLMMessage(role="user", content=prompt)])
            return {"llm_response": response.content, "provider": response.provider}

        llm_step = await self._run_step("extract_order", provider.name, llm_call)
        result.steps.append(llm_step)

        order_payload = self.transformer.llm_json_to_erp_order(llm_step.output.get("llm_response", "{}"), customer_ref)

        async def check_stock():
            lines = order_payload.get("lines", [])
            if not lines:
                return {"available": False, "reason": "no_lines_extracted"}
            line = lines[0]
            return await self.erp.check_inventory(line["sku"], line["quantity"])

        inventory_step = await self._run_step("inventory_check", "sap_erp", check_stock)
        result.steps.append(inventory_step)

        async def create_order():
            enriched = dict(order_payload)
            for line in enriched.get("lines", []):
                inv = await self.erp.check_inventory(line["sku"], line["quantity"])
                line["unit_price_chf"] = inv.get("unit_price_chf", 0)
            return await self.erp.push(enriched)

        if inventory_step.output.get("available"):
            order_step = await self._run_step("create_draft_order", "sap_erp", create_order)
            result.steps.append(order_step)
            result.final_output = {
                "inventory": inventory_step.output,
                "order": order_step.output,
            }
        else:
            result.final_output = {
                "inventory": inventory_step.output,
                "order": None,
                "message": "Insufficient stock — manual review required",
            }

        result.status = WorkflowStatus.COMPLETED
        return result

    async def document_summarization(self, document_id: str, provider_name: str | None = None) -> WorkflowResult:
        """SharePoint document → LLM summary with key points and action items."""
        result = WorkflowResult(workflow_name="document_summarization", status=WorkflowStatus.RUNNING)
        provider = get_llm_provider(provider_name, self.settings)

        doc_step = await self._run_step("fetch_document", "sharepoint", lambda: self.sharepoint.fetch(document_id))
        result.steps.append(doc_step)
        if doc_step.status == "error":
            result.status = WorkflowStatus.FAILED
            return result

        document = doc_step.output
        prompt = self.transformer.sharepoint_doc_to_prompt(document)
        safe_prompt, gov_report = self.governance.prepare_for_llm(prompt, document)
        result.governance = {"redacted_fields": gov_report.redacted_fields}

        async def llm_call():
            response = await provider.complete(
                [LLMMessage(role="user", content=safe_prompt)],
                system_prompt="Fasse Dokumente präzise zusammen. Antworte als JSON.",
            )
            return {"llm_response": response.content, "provider": response.provider}

        llm_step = await self._run_step("summarize", provider.name, llm_call)
        result.steps.append(llm_step)

        summary = _parse_llm_json(llm_step.output.get("llm_response", "{}"))

        result.status = WorkflowStatus.COMPLETED
        result.final_output = {"document_id": document_id, "summary": summary}
        return result
