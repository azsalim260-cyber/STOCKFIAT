"""
models/parc_model.py  —  MODEL layer (MVC)
──────────────────────────────────────────
All database operations for the `parc` table.

Rules enforced here:
  • Every user-supplied value goes through a parameterized query (?)
  • Bulk inserts use a single explicit transaction
  • Pagination is done at the SQL level (LIMIT / OFFSET)
  • Every method logs and re-raises on failure
"""

import logging
from database.connection import get_connection
from config import COLUMNS, PAGE_SIZE

logger = logging.getLogger(__name__)


class ParcModel:
    # ── Read ──────────────────────────────────────────────────
    def fetch_page(
        self,
        page: int = 1,
        search: str = "",
        column: str = "Toutes colonnes",
    ) -> list[dict]:
        """Return one page of records (LIMIT/OFFSET), optionally filtered."""
        offset = (page - 1) * PAGE_SIZE
        try:
            with get_connection() as conn:
                rows = conn.execute(
                    *self._build_select(search, column, PAGE_SIZE, offset)
                ).fetchall()
            return [dict(r) for r in rows]
        except Exception as exc:
            logger.error("fetch_page(page=%s) failed: %s", page, exc)
            raise

    def count(self, search: str = "", column: str = "Toutes colonnes") -> int:
        """Total matching record count (for pagination control)."""
        try:
            with get_connection() as conn:
                sql, params = self._build_count(search, column)
                return conn.execute(sql, params).fetchone()[0]
        except Exception as exc:
            logger.error("count() failed: %s", exc)
            raise

    def fetch_all(self) -> list[dict]:
        """Full dump — used only for CSV export (not for display)."""
        try:
            with get_connection() as conn:
                rows = conn.execute(
                    "SELECT * FROM parc ORDER BY id"
                ).fetchall()
            return [dict(r) for r in rows]
        except Exception as exc:
            logger.error("fetch_all() failed: %s", exc)
            raise

    # ── Write ─────────────────────────────────────────────────
    def insert(self, data: dict) -> None:
        """Insert a single record using parameterized query."""
        cols         = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        try:
            with get_connection() as conn:
                conn.execute(
                    f"INSERT INTO parc ({cols}) VALUES ({placeholders})",
                    list(data.values()),
                )
        except Exception as exc:
            logger.error("insert() failed: %s", exc)
            raise

    def bulk_insert(self, records: list[dict]) -> None:
        """
        Insert many records in ONE transaction.
        Dramatically faster than individual inserts for large datasets.
        """
        if not records:
            return
        cols         = ", ".join(records[0].keys())
        placeholders = ", ".join(["?"] * len(records[0]))
        sql          = f"INSERT INTO parc ({cols}) VALUES ({placeholders})"
        try:
            with get_connection() as conn:
                conn.execute("BEGIN")
                try:
                    conn.executemany(sql, [list(r.values()) for r in records])
                    conn.execute("COMMIT")
                    logger.info("bulk_insert: %d records committed.", len(records))
                except Exception:
                    conn.execute("ROLLBACK")
                    raise
        except Exception as exc:
            logger.error("bulk_insert() failed: %s", exc)
            raise

    def update(self, row_id: int, data: dict) -> None:
        """Update an existing record by primary key (parameterized)."""
        set_clause = ", ".join(f"{k} = ?" for k in data.keys())
        set_clause += ", updated_at = datetime('now', 'localtime')"
        try:
            with get_connection() as conn:
                conn.execute(
                    f"UPDATE parc SET {set_clause} WHERE id = ?",
                    [*data.values(), row_id],
                )
        except Exception as exc:
            logger.error("update(id=%s) failed: %s", row_id, exc)
            raise

    def delete(self, row_id: int) -> None:
        """Delete a record by primary key (parameterized)."""
        try:
            with get_connection() as conn:
                conn.execute("DELETE FROM parc WHERE id = ?", (row_id,))
        except Exception as exc:
            logger.error("delete(id=%s) failed: %s", row_id, exc)
            raise

    # ── Query builders (private) ──────────────────────────────
    @staticmethod
    def _build_select(
        search: str, column: str, limit: int, offset: int
    ) -> tuple[str, list]:
        field_map = {label: key for key, label in COLUMNS}
        if search:
            if column in field_map:
                col_key = field_map[column]
                return (
                    f"SELECT * FROM parc WHERE {col_key} LIKE ? ORDER BY id LIMIT ? OFFSET ?",
                    [f"%{search}%", limit, offset],
                )
            clauses = " OR ".join(f"{key} LIKE ?" for key, _ in COLUMNS)
            params  = [f"%{search}%"] * len(COLUMNS) + [limit, offset]
            return (
                f"SELECT * FROM parc WHERE {clauses} ORDER BY id LIMIT ? OFFSET ?",
                params,
            )
        return ("SELECT * FROM parc ORDER BY id LIMIT ? OFFSET ?", [limit, offset])

    @staticmethod
    def _build_count(search: str, column: str) -> tuple[str, list]:
        field_map = {label: key for key, label in COLUMNS}
        if search:
            if column in field_map:
                col_key = field_map[column]
                return (
                    f"SELECT COUNT(*) FROM parc WHERE {col_key} LIKE ?",
                    [f"%{search}%"],
                )
            clauses = " OR ".join(f"{key} LIKE ?" for key, _ in COLUMNS)
            return (
                f"SELECT COUNT(*) FROM parc WHERE {clauses}",
                [f"%{search}%"] * len(COLUMNS),
            )
        return ("SELECT COUNT(*) FROM parc", [])

