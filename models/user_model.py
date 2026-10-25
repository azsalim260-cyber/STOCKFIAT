"""
models/user_model.py — MODEL layer for User Management & Authentication
────────────────────────────────────────────────────────────────────────
Handles:
  • Password hashing with salt (PBKDF2-HMAC-SHA256 via standard hashlib)
  • Default admin creation if not exists
  • CRUD operations for users with parameterized queries
  • Role definitions and permission checks
"""

import os
import hashlib
import secrets
import logging
from database.connection import get_connection

logger = logging.getLogger(__name__)

# Available roles with their display labels and permissions
ROLES = {
    "ADMIN": {
        "label": "Administrateur",
        "description": "Accès total (CRUD équipements, gestion des utilisateurs, sauvegardes)",
        "can_add": True,
        "can_edit": True,
        "can_delete": True,
        "can_export": True,
        "can_manage_users": True,
    },
    "TECHNICIEN": {
        "label": "Technicien / Éditeur",
        "description": "Ajout, modification et export d'équipements. Pas de suppression ni gestion des utilisateurs.",
        "can_add": True,
        "can_edit": True,
        "can_delete": False,
        "can_export": True,
        "can_manage_users": False,
    },
    "LECTEUR": {
        "label": "Lecteur / Consultation",
        "description": "Consultation et recherche uniquement. Aucun droit de modification.",
        "can_add": False,
        "can_edit": False,
        "can_delete": False,
        "can_export": True,
        "can_manage_users": False,
    },
}


class UserModel:
    """Data access object for the `users` table."""

    @staticmethod
    def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
        """Hash password using PBKDF2-HMAC-SHA256 with 100,000 iterations."""
        if salt is None:
            salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100_000
        ).hex()
        return pwd_hash, salt

    @classmethod
    def verify_password(cls, password: str, salt: str, expected_hash: str) -> bool:
        """Verify a password against stored salt and expected hash."""
        pwd_hash, _ = cls.hash_password(password, salt)
        return secrets.compare_digest(pwd_hash, expected_hash)

    def init_default_admin(self) -> None:
        """Ensure at least one admin account exists."""
        try:
            with get_connection() as conn:
                count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
                if count == 0:
                    pwd_hash, salt = self.hash_password("admin")
                    conn.execute(
                        """
                        INSERT INTO users (username, password_hash, salt, full_name, role)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        ("admin", pwd_hash, salt, "Administrateur Principal", "ADMIN"),
                    )
                    conn.commit()
                    logger.info("Default admin created (username: 'admin', password: 'admin')")
        except Exception as exc:
            logger.error("Failed to initialize default admin: %s", exc)
            raise

    def authenticate(self, username: str, password: str) -> dict | None:
        """Authenticate user by username and password. Returns user dict on success."""
        username = username.strip()
        if not username or not password:
            return None
        try:
            with get_connection() as conn:
                row = conn.execute(
                    "SELECT * FROM users WHERE LOWER(username) = LOWER(?)",
                    (username,)
                ).fetchone()

                if row and self.verify_password(password, row["salt"], row["password_hash"]):
                    return {
                        "id": row["id"],
                        "username": row["username"],
                        "full_name": row["full_name"],
                        "role": row["role"],
                        "created_at": row["created_at"],
                    }
                return None
        except Exception as exc:
            logger.error("authenticate(%s) error: %s", username, exc)
            raise

    def get_all(self) -> list[dict]:
        """Fetch all users sorted by id."""
        try:
            with get_connection() as conn:
                rows = conn.execute(
                    "SELECT id, username, full_name, role, created_at, updated_at FROM users ORDER BY id"
                ).fetchall()
                return [dict(r) for r in rows]
        except Exception as exc:
            logger.error("get_all() users failed: %s", exc)
            raise

    def get_by_id(self, user_id: int) -> dict | None:
        """Fetch user by primary key."""
        try:
            with get_connection() as conn:
                row = conn.execute(
                    "SELECT id, username, full_name, role, created_at, updated_at FROM users WHERE id = ?",
                    (user_id,)
                ).fetchone()
                return dict(row) if row else None
        except Exception as exc:
            logger.error("get_by_id(%s) failed: %s", user_id, exc)
            raise

    def create(self, username: str, password: str, full_name: str, role: str) -> int:
        """Create a new user with hashed password."""
        username = username.strip()
        full_name = full_name.strip()
        if not username:
            raise ValueError("Le nom d'utilisateur est obligatoire.")
        if not password:
            raise ValueError("Le mot de passe est obligatoire.")
        if role not in ROLES:
            raise ValueError(f"Rôle invalide: {role}")

        pwd_hash, salt = self.hash_password(password)

        try:
            with get_connection() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO users (username, password_hash, salt, full_name, role)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (username, pwd_hash, salt, full_name, role),
                )
                conn.commit()
                logger.info("User created: %s (%s)", username, role)
                return cursor.lastrowid
        except Exception as exc:
            logger.error("create user (%s) failed: %s", username, exc)
            raise

    def update(self, user_id: int, username: str, full_name: str, role: str, new_password: str | None = None) -> None:
        """Update user profile and optionally change password."""
        username = username.strip()
        full_name = full_name.strip()
        if not username:
            raise ValueError("Le nom d'utilisateur est obligatoire.")
        if role not in ROLES:
            raise ValueError(f"Rôle invalide: {role}")

        try:
            with get_connection() as conn:
                if new_password and new_password.strip():
                    pwd_hash, salt = self.hash_password(new_password.strip())
                    conn.execute(
                        """
                        UPDATE users
                        SET username = ?, full_name = ?, role = ?, password_hash = ?, salt = ?,
                            updated_at = datetime('now', 'localtime')
                        WHERE id = ?
                        """,
                        (username, full_name, role, pwd_hash, salt, user_id),
                    )
                else:
                    conn.execute(
                        """
                        UPDATE users
                        SET username = ?, full_name = ?, role = ?,
                            updated_at = datetime('now', 'localtime')
                        WHERE id = ?
                        """,
                        (username, full_name, role, user_id),
                    )
                conn.commit()
                logger.info("User %s updated.", user_id)
        except Exception as exc:
            logger.error("update user (%s) failed: %s", user_id, exc)
            raise

    def delete(self, user_id: int) -> None:
        """Delete user by ID with safety checks (prevent deleting last admin)."""
        try:
            with get_connection() as conn:
                user = conn.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()
                if not user:
                    return

                if user["role"] == "ADMIN":
                    admin_count = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'ADMIN'").fetchone()[0]
                    if admin_count <= 1:
                        raise ValueError("Impossible de supprimer le dernier compte administrateur.")

                conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
                logger.info("User %s deleted.", user_id)
        except Exception as exc:
            logger.error("delete user (%s) failed: %s", user_id, exc)
            raise

    def username_exists(self, username: str, exclude_id: int | None = None) -> bool:
        """Check if username is already in use."""
        try:
            with get_connection() as conn:
                if exclude_id is not None:
                    count = conn.execute(
                        "SELECT COUNT(*) FROM users WHERE LOWER(username) = LOWER(?) AND id != ?",
                        (username.strip(), exclude_id),
                    ).fetchone()[0]
                else:
                    count = conn.execute(
                        "SELECT COUNT(*) FROM users WHERE LOWER(username) = LOWER(?)",
                        (username.strip(),),
                    ).fetchone()[0]
                return count > 0
        except Exception as exc:
            logger.error("username_exists(%s) failed: %s", username, exc)
            raise

