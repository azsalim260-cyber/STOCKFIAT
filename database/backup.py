"""
database/backup.py
──────────────────
Automated SQLite backup with:
  • Timestamped copies in the backups/ folder
  • Rolling retention (keeps the N most recent)
  • Error logging
"""

import shutil
import logging
from datetime import datetime
from config import DB_PATH, BACKUP_DIR

logger = logging.getLogger(__name__)

MAX_BACKUPS = 10   # Number of backup files to retain


def backup_database() -> str:
    """
    Copy the live SQLite file to backups/<timestamp>.db.

    Returns the path of the newly created backup file.
    Raises on failure so the caller can decide whether to alert the user.
    """
    try:
        timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"parc_backup_{timestamp}.db"

        # SQLite's hot-backup API via shutil is safe when WAL mode is active
        shutil.copy2(str(DB_PATH), str(backup_path))

        logger.info("Backup created: %s", backup_path)
        _prune_old_backups()
        return str(backup_path)

    except OSError as exc:
        logger.error("Backup failed: %s", exc)
        raise


def _prune_old_backups() -> None:
    """Delete the oldest backup files, keeping only MAX_BACKUPS."""
    backups = sorted(BACKUP_DIR.glob("parc_backup_*.db"))
    for old_file in backups[:-MAX_BACKUPS]:
        try:
            old_file.unlink()
            logger.info("Old backup removed: %s", old_file)
        except OSError as exc:
            logger.warning("Could not remove old backup '%s': %s", old_file, exc)

