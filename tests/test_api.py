import pytest
from httpx import ASGITransport, AsyncClient

from genai_hub.main import create_app

API_KEY = "demo-api-key-change-in-production"


@pytest.fixture
def app():
    return create_app()


@pytest.mark.asyncio
async def test_health_endpoint(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "crm" in data["systems"]


@pytest.mark.asyncio
async def test_crm_triage_requires_auth(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/workflows/crm-triage", json={"ticket_id": "TKT-1001"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_crm_triage_with_api_key(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/workflows/crm-triage",
            json={"ticket_id": "TKT-1001"},
            headers={"X-API-Key": API_KEY},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_name"] == "crm_ticket_triage"
    assert data["status"] == "completed"
