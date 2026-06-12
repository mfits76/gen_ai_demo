@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Creating .venv and installing dependencies...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -e ".[dev]"
)

echo.
echo GenAI Integration Hub - CLI Demo
echo.

.venv\Scripts\python.exe examples\run_demo.py
