"""
views/dialogs/user_manager_dialog.py — Interface d'administration des utilisateurs
─────────────────────────────────────────────────────────────────────────────────
Permet aux administrateurs de :
  • Lister tous les comptes enregistrés dans le système
  • Créer de nouveaux utilisateurs avec un rôle (Admin, Technicien, Lecteur)
  • Modifier les informations d'un utilisateur ou réinitialiser son mot de passe
  • Supprimer un utilisateur en toute sécurité (avec protections)
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QMessageBox,
    QHeaderView, QAbstractItemView, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from models.user_model import UserModel, ROLES
from views.dialogs.user_edit_dialog import UserEditDialog

logger = logging.getLogger(__name__)


class UserManagerDialog(QDialog):
    """Fenêtre de gestion des comptes utilisateurs pour les administrateurs."""

    def __init__(self, parent=None, current_user: dict | None = None):
        super().__init__(parent)
        self.user_model = UserModel()
        self.current_user = current_user or {}

        self.setWindowTitle("Administration des Utilisateurs & Rôles")
        self.resize(760, 480)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self._build_ui()
        self._load_users()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(18, 18, 18, 18)

        # ── En-tête ──
        header_layout = QHBoxLayout()
        lbl_title = QLabel("👥  Gestion des Comptes & Rôles")
        lbl_title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #1A3A5C;")
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()

        self._lbl_count = QLabel("0 utilisateur(s)")
        self._lbl_count.setStyleSheet("color: #7F8C8D; font-weight: 600;")
        header_layout.addWidget(self._lbl_count)
        layout.addLayout(header_layout)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #D5D8DC;")
        layout.addWidget(sep)

        # ── Barre d'actions ──
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(8)

        self._btn_add = QPushButton("➕  Nouvel Utilisateur")
        self._btn_add.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                font-weight: 700;
                padding: 6px 14px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        self._btn_add.clicked.connect(self._on_add_user)
        btn_bar.addWidget(self._btn_add)

        self._btn_edit = QPushButton("✏  Modifier")
        self._btn_edit.setStyleSheet("""
            QPushButton {
                background-color: #2980B9;
                color: white;
                font-weight: 700;
                padding: 6px 14px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #1F618D; }
        """)
        self._btn_edit.clicked.connect(self._on_edit_user)
        btn_bar.addWidget(self._btn_edit)

        self._btn_del = QPushButton("🗑  Supprimer")
        self._btn_del.setStyleSheet("""
            QPushButton {
                background-color: #C0392B;
                color: white;
                font-weight: 700;
                padding: 6px 14px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #A93226; }
        """)
        self._btn_del.clicked.connect(self._on_delete_user)
        btn_bar.addWidget(self._btn_del)

        btn_refresh = QPushButton("🔄  Actualiser")
        btn_refresh.clicked.connect(self._load_users)
        btn_bar.addWidget(btn_refresh)

        btn_bar.addStretch()
        layout.addLayout(btn_bar)

        # ── Tableau des utilisateurs ──
        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels([
            "ID", "Identifiant", "Nom complet", "Rôle", "Date de création"
        ])
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setDefaultSectionSize(34)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setColumnWidth(0, 50)
        self._table.setColumnWidth(1, 140)
        self._table.setColumnWidth(2, 200)
        self._table.setColumnWidth(3, 160)
        self._table.doubleClicked.connect(self._on_edit_user)
        layout.addWidget(self._table)

        # ── Pied de page ──
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()

        btn_close = QPushButton("Fermer")
        btn_close.setFixedWidth(100)
        btn_close.clicked.connect(self.accept)
        footer_layout.addWidget(btn_close)

        layout.addLayout(footer_layout)

    def _load_users(self) -> None:
        """Charge tous les utilisateurs depuis la base de données."""
        try:
            users = self.user_model.get_all()
            self._table.setRowCount(len(users))

            role_colors = {
                "ADMIN": "#8E44AD",       # Purple
                "TECHNICIEN": "#2980B9",  # Blue
                "LECTEUR": "#27AE60",     # Green
            }

            for row_idx, user in enumerate(users):
                # ID
                item_id = QTableWidgetItem(str(user["id"]))
                item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._table.setItem(row_idx, 0, item_id)

                # Identifiant (+ indication si compte actuel)
                uname = user["username"]
                if user["id"] == self.current_user.get("id"):
                    uname += " (Vous)"
                item_uname = QTableWidgetItem(uname)
                item_uname.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                self._table.setItem(row_idx, 1, item_uname)

                # Nom complet
                self._table.setItem(row_idx, 2, QTableWidgetItem(user["full_name"] or ""))

                # Rôle formaté avec libellé
                role_key = user["role"]
                role_label = ROLES.get(role_key, {}).get("label", role_key)
                item_role = QTableWidgetItem(f"🏷️ {role_label}")
                color = role_colors.get(role_key, "#2C3E50")
                item_role.setForeground(QColor(color))
                item_role.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                self._table.setItem(row_idx, 3, item_role)

                # Date création
                created = user.get("created_at", "") or ""
                self._table.setItem(row_idx, 4, QTableWidgetItem(str(created)))

                # Stocker les données complètes de l'utilisateur sur la 1ère colonne
                item_id.setData(Qt.ItemDataRole.UserRole, user)

            self._lbl_count.setText(f"{len(users)} utilisateur(s) enregistré(s)")

        except Exception as exc:
            logger.error("Failed to load users: %s", exc)
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les utilisateurs : {exc}")

    def _selected_user(self) -> dict | None:
        """Retourne l'utilisateur sélectionné dans le tableau."""
        r = self._table.currentRow()
        if r < 0:
            return None
        item = self._table.item(r, 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _on_add_user(self) -> None:
        dlg = UserEditDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            try:
                self.user_model.create(
                    username=data["username"],
                    password=data["password"],
                    full_name=data["full_name"],
                    role=data["role"]
                )
                self._load_users()
                QMessageBox.information(self, "Succès", f"L'utilisateur « {data['username']} » a été créé avec succès.")
            except Exception as exc:
                QMessageBox.critical(self, "Erreur de création", str(exc))

    def _on_edit_user(self) -> None:
        user = self._selected_user()
        if not user:
            QMessageBox.information(self, "Sélection", "Veuillez sélectionner un utilisateur à modifier.")
            return

        dlg = UserEditDialog(self, user)
        if dlg.exec():
            data = dlg.get_data()
            try:
                self.user_model.update(
                    user_id=user["id"],
                    username=data["username"],
                    full_name=data["full_name"],
                    role=data["role"],
                    new_password=data["password"]
                )
                self._load_users()
                QMessageBox.information(self, "Succès", f"L'utilisateur « {data['username']} » a été mis à jour.")
            except Exception as exc:
                QMessageBox.critical(self, "Erreur de modification", str(exc))

    def _on_delete_user(self) -> None:
        user = self._selected_user()
        if not user:
            QMessageBox.information(self, "Sélection", "Veuillez sélectionner un utilisateur à supprimer.")
            return

        # Protection: impossible de se supprimer soi-même
        if user["id"] == self.current_user.get("id"):
            QMessageBox.warning(
                self, "Action interdite", "Vous ne pouvez pas supprimer votre propre compte connecté."
            )
            return

        reply = QMessageBox.question(
            self,
            "Confirmation de suppression",
            f"Voulez-vous vraiment supprimer le compte « {user['username']} » ({user['full_name']}) ?\n"
            "Cette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.user_model.delete(user["id"])
                self._load_users()
                QMessageBox.information(self, "Supprimé", f"L'utilisateur « {user['username']} » a été supprimé.")
            except Exception as exc:
                QMessageBox.critical(self, "Erreur de suppression", str(exc))

