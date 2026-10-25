@echo off
:: ─────────────────────────────────────────────────────────────
::  setup_venv.bat — Create venv & install all dependencies
::  Run once before first launch or after pulling new changes.
:: ─────────────────────────────────────────────────────────────
cd /d "%~dp0"

echo [1/3] Creating virtual environment...
"C:\Program Files\Python312\python.exe" -m venv venv
if %ERRORLEVEL% neq 0 (
    echo ERROR: Could not create venv. Is Python 3.12 installed?
    pause & exit /b 1
)

echo [2/3] Activating venv and upgrading pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet

echo [3/3] Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo.
echo ✔  Virtual environment ready.
echo    To launch the app run:  lancer.bat
pause

