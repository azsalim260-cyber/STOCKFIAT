"""
models/stock_laptop_model.py — MODEL layer for Stock Laptops
─────────────────────────────────────────────────────────────
Handles all database operations for the `stock_laptops` table:
  • Unique FAN validation (exempts 'FREE' / 'free' to allow unlimited stock laptops)
  • When FAN == 'FREE' and quantite > 1, inserts individual records (one per laptop)
  • Parameterized queries to prevent SQL injections
  • Search by FAN, search by USER ID, and filter by OS License
  • Full CRUD operations
"""

import logging
from database.connection import get_connection

logger = logging.getLogger(__name__)

LICENSE_OPTIONS = ["Sans licence", "Avec licence"]


class StockLaptopModel:
    """Data Access Object for stock_laptops table."""

    def is_fan_exists(self, fan: str, exclude_id: int | None = None) -> bool:
        """
        Check if a NUM FAN already exists in the stock database.
        Note: If FAN is 'FREE' (case-insensitive), duplicate entries are explicitly allowed.
        """
        fan_clean = fan.strip()
        if not fan_clean:
            return False

        # 'FREE' is an unassigned stock pool identifier, exempt from uniqueness
        if fan_clean.upper() == "FREE":
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

    def fetch_all(
        self,
        search_fan: str = "",
        search_user_id: str = "",
        filter_license: str = "Toutes licences"
    ) -> list[dict]:
        """Fetch stock laptops filtered by search fan, search user_id, and license dropdown."""
        query = "SELECT * FROM stock_laptops WHERE 1=1"
        params: list = []

        if search_fan and search_fan.strip():
            query += " AND fan LIKE ?"
            params.append(f"%{search_fan.strip()}%")

        if search_user_id and search_user_id.strip():
            query += " AND user_id LIKE ?"
            params.append(f"%{search_user_id.strip()}%")

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

    def insert(
        self,
        fan: str,
        serial: str,
        model: str,
        quantite: int,
        license: str,
        user_id: str = ""
    ) -> list[int]:
        """
        Insert laptop(s) into stock.
        When FAN == 'FREE' and quantite > 1, inserts `quantite` individual records
        (each with quantite=1) in a single atomic transaction so they display one under one.
        """
        fan_clean = fan.strip()
        user_id_clean = user_id.strip() if user_id else ""
        serial_clean = serial.strip() if serial else ""
        model_clean = model.strip() if model else ""

        if not fan_clean:
            raise ValueError("Le numéro FAN est obligatoire.")

        if quantite < 1:
            quantite = 1

        if license not in LICENSE_OPTIONS:
            license = LICENSE_OPTIONS[0]

        is_free = (fan_clean.upper() == "FREE")

        # Non-FREE FANs must be strictly unique
        if not is_free and self.is_fan_exists(fan_clean):
            raise ValueError(f"Le numéro FAN « {fan_clean} » existe déjà dans le stock.")

        inserted_ids: list[int] = []
        try:
            with get_connection() as conn:
                if is_free and quantite > 1:
                    # Insert N individual records one under one
                    conn.execute("BEGIN")
                    try:
                        for _ in range(quantite):
                            cursor = conn.execute(
                                """
                                INSERT INTO stock_laptops (fan, user_id, serial, model, quantite, license)
                                VALUES (?, ?, ?, ?, 1, ?)
                                """,
                                ("FREE", user_id_clean, serial_clean, model_clean, license),
                            )
                            inserted_ids.append(cursor.lastrowid)
                        conn.execute("COMMIT")
                        logger.info("Batch inserted %d individual FREE stock laptops.", quantite)
                    except Exception:
                        conn.execute("ROLLBACK")
                        raise
                else:
                    # Single record insert
                    cursor = conn.execute(
                        """
                        INSERT INTO stock_laptops (fan, user_id, serial, model, quantite, license)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            "FREE" if is_free else fan_clean,
                            user_id_clean,
                            serial_clean,
                            model_clean,
                            quantite,
                            license
                        ),
                    )
                    conn.commit()
                    inserted_ids.append(cursor.lastrowid)
                    logger.info("Inserted stock laptop ID=%s FAN=%s", cursor.lastrowid, fan_clean)

                return inserted_ids
        except Exception as exc:
            logger.error("insert stock laptop failed: %s", exc)
            raise

    def update(
        self,
        item_id: int,
        fan: str,
        serial: str,
        model: str,
        quantite: int,
        license: str,
        user_id: str = ""
    ) -> None:
        """Update an existing stock laptop with unique FAN validation for non-FREE fans."""
        fan_clean = fan.strip()
        user_id_clean = user_id.strip() if user_id else ""
        serial_clean = serial.strip() if serial else ""
        model_clean = model.strip() if model else ""

        if not fan_clean:
            raise ValueError("Le numéro FAN est obligatoire.")

        is_free = (fan_clean.upper() == "FREE")
        if not is_free and self.is_fan_exists(fan_clean, exclude_id=item_id):
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
                    SET fan = ?, user_id = ?, serial = ?, model = ?, quantite = ?, license = ?,
                        updated_at = datetime('now', 'localtime')
                    WHERE id = ?
                    """,
                    (
                        "FREE" if is_free else fan_clean,
                        user_id_clean,
                        serial_clean,
                        model_clean,
                        quantite,
                        license,
                        item_id
                    ),
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

    def count(
        self,
        search_fan: str = "",
        search_user_id: str = "",
        filter_license: str = "Toutes licences"
    ) -> int:
        """Return total count of filtered records."""
        query = "SELECT COUNT(*) FROM stock_laptops WHERE 1=1"
        params: list = []

        if search_fan and search_fan.strip():
            query += " AND fan LIKE ?"
            params.append(f"%{search_fan.strip()}%")

        if search_user_id and search_user_id.strip():
            query += " AND user_id LIKE ?"
            params.append(f"%{search_user_id.strip()}%")

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
                free_count = conn.execute(
                    "SELECT COALESCE(SUM(quantite), 0) FROM stock_laptops WHERE UPPER(TRIM(fan)) = 'FREE'"
                ).fetchone()[0]
                return {
                    "total_references": total_refs,
                    "total_quantite": total_qty,
                    "avec_licence": with_lic,
                    "sans_licence": no_lic,
                    "free_laptops": free_count,
                }
        except Exception as exc:
            logger.error("get_stats failed: %s", exc)
            return {
                "total_references": 0,
                "total_quantite": 0,
                "avec_licence": 0,
                "sans_licence": 0,
                "free_laptops": 0,
            }
