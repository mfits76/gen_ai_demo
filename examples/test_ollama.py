"""Test local Ollama (e.g. qwen2.5:0.5b) with the GenAI Integration Hub.

Ollama /api/chat only accepts POST — opening the URL in a browser sends GET
and returns 405 Method Not Allowed. That is normal.

Run from project root:
  test_ollama.bat
  python examples/test_ollama.py
"""

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

from genai_hub.config import Settings
from genai_hub.providers.base import LLMMessage
from genai_hub.providers.factory import get_llm_provider
from genai_hub.workflows.engine import WorkflowEngine


async def main() -> None:
    settings = Settings(default_llm_provider="ollama")
    provider = get_llm_provider("ollama", settings)

    print("=" * 60)
    print("  Ollama test")
    print("=" * 60)
    print(f"  Base URL : {settings.ollama_base_url}")
    print(f"  Model    : {settings.ollama_model}")
    print()
    print("  Browser GET on /api/chat -> 405 (expected)")
    print("  This script uses POST via the app.")
    print()

    print("--- Step 1: Health check (GET /api/tags) ---")
    health = await provider.health_check()
    print(json.dumps(health, indent=2))
    if health.get("status") != "healthy":
        print("\nOllama is not ready. Check: ollama list")
        sys.exit(1)

    print("\n--- Step 2: Direct LLM call (POST /api/chat) ---")
    response = await provider.complete([LLMMessage(role="user", content="Reply with exactly: Ollama works")])
    print(f"  Response: {response.content.strip()}")
    print(f"  Tokens  : {response.usage}")

    print("\n--- Step 3: CRM workflow via Ollama ---")
    engine = WorkflowEngine(settings)
    result = await engine.crm_ticket_triage("TKT-1001", provider_name="ollama")
    print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))

    print("\nDone. For the full API, run start.bat and open /docs")


if __name__ == "__main__":
    asyncio.run(main())
