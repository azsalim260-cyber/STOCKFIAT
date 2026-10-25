@echo off
:: ─────────────────────────────────────────────────────────────
::  lancer.bat — Launch the application using the local venv
:: ─────────────────────────────────────────────────────────────
cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    echo Lancement via venv...
    venv\Scripts\python.exe main.py
) else (
    echo Venv non trouve — utilisation du Python systeme...
    "C:\Program Files\Python312\python.exe" main.py
)

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERREUR: Impossible de lancer l'application.
    echo  - Verifiez que PyQt6 est installe : pip install PyQt6
    echo  - Ou executez d'abord : setup_venv.bat
    pause
)
