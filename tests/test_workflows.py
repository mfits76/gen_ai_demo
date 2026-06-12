import pytest

from genai_hub.workflows.engine import WorkflowEngine
from genai_hub.workflows.models import WorkflowStatus


@pytest.fixture
def engine():
    return WorkflowEngine()


@pytest.mark.asyncio
async def test_crm_ticket_triage(engine):
    result = await engine.crm_ticket_triage("TKT-1001")
    assert result.status == WorkflowStatus.COMPLETED
    assert len(result.steps) == 3
    assert result.final_output["ticket_id"] == "TKT-1001"
    assert "ai_analysis" in result.final_output


@pytest.mark.asyncio
async def test_email_order_extraction(engine):
    email = "Please order 3 units of SKU-B200 for customer CUST-8830"
    result = await engine.email_order_extraction(email)
    assert result.status == WorkflowStatus.COMPLETED
    assert result.final_output.get("inventory", {}).get("available") is True


@pytest.mark.asyncio
async def test_document_summarization(engine):
    result = await engine.document_summarization("DOC-ROADMAP-Q2")
    assert result.status == WorkflowStatus.COMPLETED
    assert "summary" in result.final_output
