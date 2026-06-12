# GenAI Integration Hub

[![CI](https://github.com/mfits76/gen_ai_demo/actions/workflows/ci.yml/badge.svg)](https://github.com/mfits76/gen_ai_demo/actions/workflows/ci.yml)
[![Demo](https://img.shields.io/badge/demo-live-blue)](https://mfits76.github.io/gen_ai_demo/)

Python demo for **MF Corp**: integrate LLMs with CRM, ERP, and SharePoint via REST APIs and automated workflows.

**[Live demo](https://mfits76.github.io/gen_ai_demo/)** · **[CI runs](https://github.com/mfits76/gen_ai_demo/actions)** · no install needed for the static output

## What it does

Three workflows, all following **fetch → govern → LLM → push**:

1. **CRM ticket triage** — classify support tickets and draft replies
2. **Email order extraction** — pull orders from text, check ERP stock
3. **Document summarization** — summarize SharePoint docs with action items

LLM backends: **mock** (default, no keys), **Ollama**, OpenAI, Anthropic. Includes API-key/OAuth auth and PII redaction before LLM calls.

## Quick start (Windows)

```bat
start.bat          REM REST API  -> http://localhost:8000/docs
run_demo.bat       REM CLI demo (mock LLM)
test_ollama.bat    REM local Ollama, e.g. qwen2.5:0.5b
```

Manual setup:

```bash
python -m venv .venv
.venv\Scripts\pip install -e ".[dev]"
copy .env.example .env
python examples/run_demo.py
```

## API

Default API key: `demo-api-key-change-in-production`

```bash
curl http://localhost:8000/api/v1/health

curl -X POST http://localhost:8000/api/v1/workflows/crm-triage \
  -H "X-API-Key: demo-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{"ticket_id": "TKT-1001", "provider": "mock"}'
```

Use Ollama locally — in `.env`:

```env
DEFAULT_LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:0.5b
```

## Project layout

```
src/genai_hub/
  api/            REST endpoints
  integrations/   CRM, ERP, SharePoint (demo connectors)
  providers/      LLM backends
  workflows/      orchestration engine
  security/       auth + PII governance
```

## Tests

```bash
pytest -v
```

Also runs automatically on every push via GitHub Actions.

## License

MIT
