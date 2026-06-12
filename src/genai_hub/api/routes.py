from fastapi import APIRouter, Depends

from genai_hub import __version__
from genai_hub.api.schemas import (
    CRMTriageRequest,
    DocumentSummaryRequest,
    HealthResponse,
    OrderExtractionRequest,
    TokenRequest,
    TokenResponse,
)
from genai_hub.config import Settings, get_settings
from genai_hub.providers.factory import get_llm_provider
from genai_hub.security.auth import create_access_token, verify_api_key_or_token
from genai_hub.workflows.engine import WorkflowEngine
from genai_hub.workflows.models import WorkflowResult

router = APIRouter(prefix="/api/v1")


def get_engine() -> WorkflowEngine:
    return WorkflowEngine()


@router.get("/health", response_model=HealthResponse)
async def health(engine: WorkflowEngine = Depends(get_engine)) -> HealthResponse:
    crm_health = await engine.crm.health_check()
    erp_health = await engine.erp.health_check()
    sp_health = await engine.sharepoint.health_check()
    provider_health = await get_llm_provider().health_check()
    return HealthResponse(
        status="healthy",
        version=__version__,
        systems={"crm": crm_health, "erp": erp_health, "sharepoint": sp_health},
        providers={"default": provider_health},
    )


@router.post("/auth/token", response_model=TokenResponse)
async def issue_token(
    body: TokenRequest,
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    """OAuth2-style token endpoint for demo integrations."""
    token = create_access_token(body.client_id, settings)
    return TokenResponse(access_token=token, expires_in=settings.jwt_expire_minutes * 60)


@router.post("/workflows/crm-triage", response_model=WorkflowResult)
async def run_crm_triage(
    body: CRMTriageRequest,
    _: str = Depends(verify_api_key_or_token),
    engine: WorkflowEngine = Depends(get_engine),
) -> WorkflowResult:
    return await engine.crm_ticket_triage(body.ticket_id, body.provider)


@router.post("/workflows/order-extraction", response_model=WorkflowResult)
async def run_order_extraction(
    body: OrderExtractionRequest,
    _: str = Depends(verify_api_key_or_token),
    engine: WorkflowEngine = Depends(get_engine),
) -> WorkflowResult:
    return await engine.email_order_extraction(body.email_text, body.customer_ref, body.provider)


@router.post("/workflows/document-summary", response_model=WorkflowResult)
async def run_document_summary(
    body: DocumentSummaryRequest,
    _: str = Depends(verify_api_key_or_token),
    engine: WorkflowEngine = Depends(get_engine),
) -> WorkflowResult:
    return await engine.document_summarization(body.document_id, body.provider)


@router.get("/integrations/crm/tickets")
async def list_crm_tickets(
    _: str = Depends(verify_api_key_or_token),
    engine: WorkflowEngine = Depends(get_engine),
):
    return await engine.crm.list_open_tickets()


@router.get("/integrations/erp/inventory/{sku}")
async def get_inventory(
    sku: str,
    quantity: int = 1,
    _: str = Depends(verify_api_key_or_token),
    engine: WorkflowEngine = Depends(get_engine),
):
    return await engine.erp.check_inventory(sku, quantity)


@router.get("/integrations/sharepoint/documents")
async def list_documents(
    _: str = Depends(verify_api_key_or_token),
    engine: WorkflowEngine = Depends(get_engine),
):
    return await engine.sharepoint.list_documents()
