"""Interactive demo script for portfolio presentations."""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VENV_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"


def _ensure_project_python() -> None:
    """Re-launch with the local .venv, creating it on first run if needed."""
    if Path(sys.executable).resolve() == VENV_PYTHON.resolve():
        return

    if not VENV_PYTHON.exists():
        print(f"First run: creating virtual environment in {PROJECT_ROOT}")
        subprocess.check_call([sys.executable, "-m", "venv", str(PROJECT_ROOT / ".venv")])
        subprocess.check_call(
            [str(VENV_PYTHON), "-m", "pip", "install", "-e", ".[dev]"],
            cwd=PROJECT_ROOT,
        )

    raise SystemExit(subprocess.call([str(VENV_PYTHON), *sys.argv]))


_ensure_project_python()
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from genai_hub.workflows.engine import WorkflowEngine


def print_section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


def print_result(result) -> None:
    print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))


async def main() -> None:
    provider = "ollama" if "--ollama" in sys.argv else None
    engine = WorkflowEngine()

    print_section("GenAI Integration Hub - Live Demo")
    print("Enterprise context: MF Corp")
    if provider:
        print("LLM provider: ollama (local)")
    print("Demonstrates: CRM/ERP/SharePoint + LLM workflows with PII governance")

    print_section("1. CRM Ticket Triage (Salesforce -> LLM -> CRM)")
    result = await engine.crm_ticket_triage("TKT-1001", provider_name=provider)
    print_result(result)

    print_section("2. Email Order Extraction (Unstructured -> LLM -> SAP ERP)")
    email = (
        "Sehr geehrte Damen und Herren,\n"
        "bitte bestellen Sie 5 Stück SKU-A100 für Kunde CUST-4521.\n"
        "Bei Fragen: billing@mueller-ag.ch\n"
        "Freundliche Grüsse, Müller AG"
    )
    result = await engine.email_order_extraction(email, provider_name=provider)
    print_result(result)

    print_section("3. Document Summarization (SharePoint -> LLM)")
    result = await engine.document_summarization("DOC-ROADMAP-Q2", provider_name=provider)
    print_result(result)

    print_section("4. System Health")
    for name, connector in [("CRM", engine.crm), ("ERP", engine.erp), ("SharePoint", engine.sharepoint)]:
        health = await connector.health_check()
        print(f"  {name}: {health}")

    print("\nDemo complete. Start API with: start.bat")


if __name__ == "__main__":
    asyncio.run(main())
