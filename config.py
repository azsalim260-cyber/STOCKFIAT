"""
config.py — Centralized application constants and paths.
"""

from pathlib import Path

# ── Paths ────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
DB_PATH    = BASE_DIR / "parc.db"
BACKUP_DIR = BASE_DIR / "backups"
LOG_DIR    = BASE_DIR / "logs"
LOG_FILE   = LOG_DIR  / "app.log"

# Ensure runtime directories exist
BACKUP_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# ── Table schema ─────────────────────────────────────────────
COLUMNS = [
    ("fan",            "FAN"),
    ("user_id",        "USER ID"),
    ("nom_prenom",     "NOM PRÉNOM"),
    ("pc",             "PC"),
    ("pc_serial",      "PC SERIAL"),
    ("num_tel",        "NUM TÉL"),
    ("app_tel",        "APPAREIL TÉL"),
    ("app_tel_serial", "APP TÉL SERIAL"),
    ("casque",         "CASQUE"),
    ("disque_backup",  "DISQUE BACKUP"),
]

# ── Pagination ───────────────────────────────────────────────
PAGE_SIZE = 50  # Records displayed per page

# ── App metadata ─────────────────────────────────────────────
APP_NAME    = "Gestionnaire Parc IT"
APP_VERSION = "2.0"

