# parc_app.spec
# ─────────────────────────────────────────────────────────────────────────────
# PyInstaller spec file for Gestionnaire de Parc Informatique & Téléphonique
#
# HOW TO BUILD
# ─────────────
# 1. Activate your venv:       .\venv\Scripts\activate
# 2. Install deps:             pip install -r requirements.txt
# 3. Run PyInstaller:          pyinstaller parc_app.spec
# 4. Find your .exe in:        dist\ParcIT\ParcIT.exe
# ─────────────────────────────────────────────────────────────────────────────

import sys
from pathlib import Path
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

# Project root (same directory as this .spec file)
ROOT = Path(SPECPATH)

# ── Collect ALL Python source packages ───────────────────────
block_cipher = None

a = Analysis(
    [str(ROOT / "main.py")],            # entry point
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        # Include the default (possibly empty) database
        (str(ROOT / "parc.db"),  "."),
        # Include all sub-packages so PyInstaller finds them
        (str(ROOT / "database"),    "database"),
        (str(ROOT / "models"),      "models"),
        (str(ROOT / "workers"),     "workers"),
        (str(ROOT / "views"),       "views"),
        (str(ROOT / "controllers"), "controllers"),
        (str(ROOT / "styles"),      "styles"),
        (str(ROOT / "utils"),       "utils"),
    ],
    hiddenimports=[
        # Qt platform plugin required on Windows
        "PyQt6.QtWidgets",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.sip",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ParcIT",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    # icon="assets/icon.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ParcIT",
)
