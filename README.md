# GenAI Integration Hub

A production-style Python platform for **MF Corp** that demonstrates how Large Language Models can be integrated into existing enterprise landscapes — connecting CRM, ERP, and collaboration systems through secure REST APIs and automated workflows.

## Why this project maps to the role

| Job requirement | Implementation |
|-----------------|----------------|
| LLM integration (OpenAI, Anthropic, Azure, Hugging Face) | Pluggable provider abstraction with mock, OpenAI, and Anthropic backends |
| Enterprise system coupling (CRM, ERP, collaboration) | Salesforce-style CRM, SAP-style ERP, SharePoint connectors |
| API development & management (REST, OAuth) | FastAPI REST layer with API-key and OAuth2 bearer token auth |
| Workflow automation | Three end-to-end workflows orchestrating fetch → govern → LLM → push |
| Data mapping & transformation | `DataTransformer` for JSON/XML mapping between system schemas |
| Security & data privacy | PII redaction, regional compliance checks before LLM calls |
| Python expertise | Core language; async/await throughout |
| Technical documentation | OpenAPI docs at `/docs`, architecture below |

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  CRM        │────▶│  Workflow Engine │────▶│  LLM Providers  │
│  (Salesforce)│     │  + Data Gov.     │     │  mock/openai/   │
├─────────────┤     │  + Transformer   │     │  anthropic      │
│  ERP (SAP)  │◀───▶│                  │◀───▶└─────────────────┘
├─────────────┤     └────────┬─────────┘
│ SharePoint  │              │
└─────────────┘              ▼
                    ┌──────────────────┐
                    │  FastAPI REST    │
                    │  /api/v1/...     │
                    └──────────────────┘
```

## Workflows

1. **CRM Ticket Triage** — Fetch support ticket → redact PII → LLM classifies intent and drafts response → update CRM
2. **Email Order Extraction** — Parse unstructured email → extract SKU/quantity → check ERP inventory → create draft order
3. **Document Summarization** — Fetch SharePoint document → LLM summary with key points and action items

## Quick start

```bash
# Create virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment config
copy .env.example .env

# Run interactive demo (no API keys needed)
python examples/run_demo.py

# Start REST API
uvicorn genai_hub.main:app --reload
```

Open **http://localhost:8000/docs** for the interactive API explorer.

## API usage

All workflow endpoints require authentication via `X-API-Key` header or OAuth2 bearer token.

```bash
# Health check (no auth)
curl http://localhost:8000/api/v1/health

# CRM triage workflow
curl -X POST http://localhost:8000/api/v1/workflows/crm-triage \
  -H "X-API-Key: demo-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{"ticket_id": "TKT-1001"}'

# Get OAuth2 token
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"client_id": "demo-client", "client_secret": "demo-secret"}'
```

## Connecting real LLM providers

Set keys in `.env`:

```env
DEFAULT_LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

Install optional provider packages:

```bash
pip install -e ".[openai,anthropic]"
```

## Running tests

```bash
pytest -v
```

## Project structure

```
src/genai_hub/
├── api/            # FastAPI routes and schemas
├── integrations/   # CRM, ERP, SharePoint connectors
├── mapping/        # Data transformation between systems
├── providers/      # LLM provider abstraction
├── security/       # Auth (API key, OAuth2) and PII governance
└── workflows/      # Orchestration engine
```

## Presentation tips

1. Run `python examples/run_demo.py` live to show all three workflows
2. Walk through `/docs` to highlight REST API design and auth
3. Open `workflows/engine.py` to explain the fetch → govern → LLM → push pattern
4. Mention extensibility: swap mock connectors for real Salesforce/SAP APIs via the same interface

## License

MIT — free to use in portfolio and interview contexts.
