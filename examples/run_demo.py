"""Interactive demo script for portfolio presentations."""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _venv_python() -> Path:
    if sys.platform == "win32":
        return PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    return PROJECT_ROOT / ".venv" / "bin" / "python"


def _ensure_project_python() -> None:
    """Re-launch with the local .venv, creating it on first run if needed."""
    if os.environ.get("CI"):
        return

    venv_python = _venv_python()
    if Path(sys.executable).resolve() == venv_python.resolve():
        return

    if not venv_python.exists():
        print(f"First run: creating virtual environment in {PROJECT_ROOT}")
        subprocess.check_call([sys.executable, "-m", "venv", str(PROJECT_ROOT / ".venv")])
        subprocess.check_call(
            [str(venv_python), "-m", "pip", "install", "-e", ".[dev]"],
            cwd=PROJECT_ROOT,
        )

    raise SystemExit(subprocess.call([str(venv_python), *sys.argv]))


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
