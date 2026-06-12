@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
    .venv\Scripts\pip install -e ".[dev]"
)

echo.
echo Ollama example - POST requests only, not a browser URL
echo.

.venv\Scripts\python.exe examples\test_ollama.py
pause
