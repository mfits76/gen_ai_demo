@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating .venv and installing dependencies...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -e ".[dev]"
) else (
    call .venv\Scripts\activate.bat
)

echo.
echo GenAI Integration Hub
echo.

.venv\Scripts\python.exe scripts\start_server.py
