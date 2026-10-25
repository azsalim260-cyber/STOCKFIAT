"""
models/stock_laptop_model.py — MODEL layer for Stock Laptops
─────────────────────────────────────────────────────────────
Handles all database operations for the `stock_laptops` table:
  • Unique FAN validation and checking
  • Parameterized queries to prevent SQL injections
  • Search by FAN and filter by OS License
  • Full CRUD operations
"""

import logging
from database.connection import get_connection

logger = logging.getLogger(__name__)

LICENSE_OPTIONS = ["Sans licence", "Avec licence"]


class StockLaptopModel:
    """Data Access Object for stock_laptops table."""

    def is_fan_exists(self, fan: str, exclude_id: int | None = None) -> bool:
        """Check if a NUM FAN already exists in the stock database."""
        fan_clean = fan.strip()
        if not fan_clean:
            return False
        try:
            with get_connection() as conn:
                if exclude_id is not None:
                    count = conn.execute(
                        "SELECT COUNT(*) FROM stock_laptops WHERE LOWER(fan) = LOWER(?) AND id != ?",
                        (fan_clean, exclude_id),
                    ).fetchone()[0]
                else:
                    count = conn.execute(
                        "SELECT COUNT(*) FROM stock_laptops WHERE LOWER(fan) = LOWER(?)",
                        (fan_clean,),
                    ).fetchone()[0]
                return count > 0
        except Exception as exc:
            logger.error("is_fan_exists(%s) failed: %s", fan, exc)
            raise

    def fetch_all(self, search_fan: str = "", filter_license: str = "Toutes licences") -> list[dict]:
        """Fetch stock laptops filtered by search fan and license dropdown."""
        query = "SELECT * FROM stock_laptops WHERE 1=1"
        params: list = []

        if search_fan and search_fan.strip():
            query += " AND fan LIKE ?"
            params.append(f"%{search_fan.strip()}%")

        if filter_license and filter_license != "Toutes licences":
            query += " AND license = ?"
            params.append(filter_license)

        query += " ORDER BY id DESC"

        try:
            with get_connection() as conn:
                rows = conn.execute(query, params).fetchall()
                return [dict(r) for r in rows]
        except Exception as exc:
            logger.error("fetch_all stock laptops failed: %s", exc)
            raise

    def get_by_id(self, item_id: int) -> dict | None:
        """Retrieve a single laptop record by primary key."""
        try:
            with get_connection() as conn:
                row = conn.execute(
                    "SELECT * FROM stock_laptops WHERE id = ?", (item_id,)
                ).fetchone()
                return dict(row) if row else None
        except Exception as exc:
            logger.error("get_by_id(%s) failed: %s", item_id, exc)
            raise

    def insert(self, fan: str, serial: str, model: str, quantite: int, license: str) -> int:
        """Insert a new laptop into stock with unique FAN validation."""
        fan_clean = fan.strip()
        serial_clean = serial.strip()
        model_clean = model.strip()

        if not fan_clean:
            raise ValueError("Le numéro FAN est obligatoire.")

        if self.is_fan_exists(fan_clean):
            raise ValueError(f"Le numéro FAN « {fan_clean} » existe déjà dans le stock.")

        if quantite < 1:
            quantite = 1

        if license not in LICENSE_OPTIONS:
            license = LICENSE_OPTIONS[0]

        try:
            with get_connection() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO stock_laptops (fan, serial, model, quantite, license)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (fan_clean, serial_clean, model_clean, quantite, license),
                )
                conn.commit()
                logger.info("Inserted stock laptop ID=%s FAN=%s", cursor.lastrowid, fan_clean)
                return cursor.lastrowid
        except Exception as exc:
            logger.error("insert stock laptop failed: %s", exc)
            raise

    def update(self, item_id: int, fan: str, serial: str, model: str, quantite: int, license: str) -> None:
        """Update an existing stock laptop with unique FAN validation."""
        fan_clean = fan.strip()
        serial_clean = serial.strip()
        model_clean = model.strip()

        if not fan_clean:
            raise ValueError("Le numéro FAN est obligatoire.")

        if self.is_fan_exists(fan_clean, exclude_id=item_id):
            raise ValueError(f"Le numéro FAN « {fan_clean} » est déjà attribué à un autre équipement.")

        if quantite < 1:
            quantite = 1

        if license not in LICENSE_OPTIONS:
            license = LICENSE_OPTIONS[0]

        try:
            with get_connection() as conn:
                conn.execute(
                    """
                    UPDATE stock_laptops
                    SET fan = ?, serial = ?, model = ?, quantite = ?, license = ?,
                        updated_at = datetime('now', 'localtime')
                    WHERE id = ?
                    """,
                    (fan_clean, serial_clean, model_clean, quantite, license, item_id),
                )
                conn.commit()
                logger.info("Updated stock laptop ID=%s", item_id)
        except Exception as exc:
            logger.error("update stock laptop failed: %s", exc)
            raise

    def delete(self, item_id: int) -> None:
        """Delete a laptop record from stock."""
        try:
            with get_connection() as conn:
                conn.execute("DELETE FROM stock_laptops WHERE id = ?", (item_id,))
                conn.commit()
                logger.info("Deleted stock laptop ID=%s", item_id)
        except Exception as exc:
            logger.error("delete stock laptop failed: %s", exc)
            raise

    def count(self, search_fan: str = "", filter_license: str = "Toutes licences") -> int:
        """Return total count of filtered records."""
        query = "SELECT COUNT(*) FROM stock_laptops WHERE 1=1"
        params: list = []

        if search_fan and search_fan.strip():
            query += " AND fan LIKE ?"
            params.append(f"%{search_fan.strip()}%")

        if filter_license and filter_license != "Toutes licences":
            query += " AND license = ?"
            params.append(filter_license)

        try:
            with get_connection() as conn:
                return conn.execute(query, params).fetchone()[0]
        except Exception as exc:
            logger.error("count stock laptops failed: %s", exc)
            raise

    def get_stats(self) -> dict:
        """Return summary statistics of the laptop stock."""
        try:
            with get_connection() as conn:
                total_refs = conn.execute("SELECT COUNT(*) FROM stock_laptops").fetchone()[0]
                total_qty = conn.execute("SELECT COALESCE(SUM(quantite), 0) FROM stock_laptops").fetchone()[0]
                with_lic = conn.execute(
                    "SELECT COALESCE(SUM(quantite), 0) FROM stock_laptops WHERE license = 'Avec licence'"
                ).fetchone()[0]
                no_lic = conn.execute(
                    "SELECT COALESCE(SUM(quantite), 0) FROM stock_laptops WHERE license = 'Sans licence'"
                ).fetchone()[0]
                return {
                    "total_references": total_refs,
                    "total_quantite": total_qty,
                    "avec_licence": with_lic,
                    "sans_licence": no_lic,
                }
        except Exception as exc:
            logger.error("get_stats failed: %s", exc)
            return {"total_references": 0, "total_quantite": 0, "avec_licence": 0, "sans_licence": 0}

