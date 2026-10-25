@echo off
:: Capture exact installed versions for reproducible installs
cd /d "%~dp0"
call venv\Scripts\activate.bat
pip freeze > pip_freeze.txt
echo ✔  pip_freeze.txt updated.
pause

