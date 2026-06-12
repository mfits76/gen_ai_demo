@echo off
cd /d "%~dp0"

echo Pushing to https://github.com/mfitsilis/gen_ai_demo
echo.
echo If this fails with "Repository not found", create the repo first:
echo   1. Open https://github.com/new
echo   2. Repository name: gen_ai_demo
echo   3. Leave it empty (no README, no .gitignore)
echo   4. Click Create repository
echo   5. Run this script again
echo.

git push -u origin main
pause
