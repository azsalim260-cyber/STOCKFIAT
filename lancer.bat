@echo off
:: ─────────────────────────────────────────────────────────────
::  lancer.bat — Lanceur de l'application Parc Informatique
:: ─────────────────────────────────────────────────────────────
title Gestionnaire de Parc Informatique
cd /d "%~dp0"

echo ===================================================
echo   Lancement du Gestionnaire de Parc IT...
echo ===================================================

if exist "%~dp0venv\Scripts\python.exe" (
    echo [OK] Environnement virtuel detecte.
    "%~dp0venv\Scripts\python.exe" main.py
) else if exist "C:\Program Files\Python312\python.exe" (
    echo [INFO] Utilisation de Python 3.12 systeme...
    "C:\Program Files\Python312\python.exe" main.py
) else (
    echo [INFO] Utilisation de python dans le PATH...
    python main.py
)

if %ERRORLEVEL% neq 0 (
    echo.
    echo ===================================================
    echo   ERREUR: Impossible d'executer l'application.
    echo   Consultez le fichier de logs : logs\app.log
    echo ===================================================
    echo.
    pause
)
