from typing import Any

from pydantic import BaseModel, Field


class TokenRequest(BaseModel):
    client_id: str = "demo-client"
    client_secret: str = "demo-secret"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class WorkflowRequest(BaseModel):
    provider: str | None = Field(None, description="LLM provider: mock, openai, anthropic")


class CRMTriageRequest(WorkflowRequest):
    ticket_id: str = "TKT-1001"


class OrderExtractionRequest(WorkflowRequest):
    email_text: str = (
        "Guten Tag, bitte bestellen Sie 5 units von SKU-A100 für Kunde CUST-4521. "
        "Kontakt: billing@mueller-ag.ch"
    )
    customer_ref: str | None = None


class DocumentSummaryRequest(WorkflowRequest):
    document_id: str = "DOC-ROADMAP-Q2"


class HealthResponse(BaseModel):
    status: str
    version: str
    systems: dict[str, Any]
    providers: dict[str, Any]
