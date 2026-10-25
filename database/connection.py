"""
database/connection.py
─────────────────────
SQLite connection factory with:
  • WAL (Write-Ahead Logging) journal mode  → better concurrency & read performance
  • NORMAL synchronous mode                → safe yet fast
  • 8 MB page cache                        → fewer disk reads
  • Foreign-key enforcement
  • Parameterized queries everywhere        → no SQL injection
  • Table + index creation on first run (parc, users, stock_laptops)
  • Default administrator account creation
  • Structured error logging
"""

import sqlite3
import logging
from config import DB_PATH, COLUMNS

logger = logging.getLogger(__name__)


# ── Low-level factory ─────────────────────────────────────────
def get_connection() -> sqlite3.Connection:
    """
    Open and return a WAL-enabled SQLite connection.
    The caller is responsible for closing / using as context manager.
    """
    try:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row

        # Performance & safety PRAGMAs
        conn.execute("PRAGMA journal_mode = WAL")       # Write-Ahead Logging
        conn.execute("PRAGMA synchronous  = NORMAL")    # Safe but faster than FULL
        conn.execute("PRAGMA cache_size   = -8000")     # 8 MB page cache
        conn.execute("PRAGMA temp_store   = MEMORY")    # Temp tables in RAM
        conn.execute("PRAGMA foreign_keys = ON")        # Enforce FK constraints

        return conn
    except sqlite3.Error as exc:
        logger.error("Cannot open database '%s': %s", DB_PATH, exc)
        raise


# ── Schema bootstrap ──────────────────────────────────────────
def init_db() -> None:
    """
    Create default tables (parc, users, stock_laptops) and performance indexes
    if they do not already exist. Uses parameterized-style DDL.
    """
    try:
        with get_connection() as conn:
            # ── Main table: parc (affectations) ──
            conn.execute("""
                CREATE TABLE IF NOT EXISTS parc (
                    id             INTEGER PRIMARY KEY AUTOINCREMENT,
                    fan            TEXT,
                    user_id        TEXT,
                    nom_prenom     TEXT,
                    pc             TEXT,
                    pc_serial      TEXT,
                    num_tel        TEXT,
                    app_tel        TEXT,
                    app_tel_serial TEXT,
                    casque         TEXT,
                    disque_backup  TEXT,
                    created_at     TEXT DEFAULT (datetime('now', 'localtime')),
                    updated_at     TEXT DEFAULT (datetime('now', 'localtime'))
                )
            """)

            # Indexes for parc
            index_cols = ["fan", "user_id", "nom_prenom", "pc", "num_tel"]
            for col in index_cols:
                conn.execute(
                    f"CREATE INDEX IF NOT EXISTS idx_parc_{col} ON parc({col})"
                )

            # ── Users & Roles table ──
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id             INTEGER PRIMARY KEY AUTOINCREMENT,
                    username       TEXT UNIQUE NOT NULL,
                    password_hash  TEXT NOT NULL,
                    salt           TEXT NOT NULL,
                    full_name      TEXT,
                    role           TEXT NOT NULL,
                    created_at     TEXT DEFAULT (datetime('now', 'localtime')),
                    updated_at     TEXT DEFAULT (datetime('now', 'localtime'))
                )
            """)

            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)"
            )

            # ── Stock Laptops table ──
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stock_laptops (
                    id             INTEGER PRIMARY KEY AUTOINCREMENT,
                    fan            TEXT UNIQUE NOT NULL,
                    serial         TEXT,
                    model          TEXT,
                    quantite       INTEGER DEFAULT 1,
                    license        TEXT NOT NULL DEFAULT 'Sans licence',
                    created_at     TEXT DEFAULT (datetime('now', 'localtime')),
                    updated_at     TEXT DEFAULT (datetime('now', 'localtime'))
                )
            """)

            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_stock_fan ON stock_laptops(fan)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_stock_license ON stock_laptops(license)"
            )

            conn.commit()
            logger.info("Database initialized at '%s' (WAL mode).", DB_PATH)

        # Seed default admin account if not already present
        from models.user_model import UserModel
        UserModel().init_default_admin()

    except sqlite3.Error as exc:
        logger.error("Database initialization failed: %s", exc)
        raise
