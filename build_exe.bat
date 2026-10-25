@echo off
:: ─────────────────────────────────────────────────────────────
::  build_exe.bat — Package the app into a single folder .exe
::  Requires: setup_venv.bat to have been run first.
:: ─────────────────────────────────────────────────────────────
cd /d "%~dp0"
call venv\Scripts\activate.bat

echo Cleaning previous build...
if exist build  rmdir /s /q build
if exist dist   rmdir /s /q dist

echo Running PyInstaller...
pyinstaller parc_app.spec --noconfirm

if %ERRORLEVEL% equ 0 (
    echo.
    echo ✔  Build successful!
    echo    Executable: dist\ParcIT\ParcIT.exe
) else (
    echo.
    echo ✖  Build failed. See output above.
)
pause

