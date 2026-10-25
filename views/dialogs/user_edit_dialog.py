"""
views/dialogs/user_edit_dialog.py — Formulaire d'ajout / modification d'utilisateur
─────────────────────────────────────────────────────────────────────────────────
Permet à l'administrateur de :
  • Créer un nouveau compte utilisateur avec un rôle défini
  • Modifier le nom complet et le rôle d'un compte existant
  • Réinitialiser ou mettre à jour le mot de passe
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QFrame,
    QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from models.user_model import ROLES, UserModel


class UserEditDialog(QDialog):
    """Dialogue pour ajouter ou éditer un utilisateur."""

    def __init__(self, parent=None, user_data: dict | None = None):
        super().__init__(parent)
        self.user_data = user_data or {}
        self.is_edit_mode = bool(user_data)
        self.user_model = UserModel()

        title = "Modifier l'utilisateur" if self.is_edit_mode else "Créer un nouvel utilisateur"
        self.setWindowTitle(title)
        self.setFixedWidth(460)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 22, 24, 22)

        # ── Titre ──
        lbl_title = QLabel(self.windowTitle())
        lbl_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #1A3A5C;")
        layout.addWidget(lbl_title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #AED6F1;")
        layout.addWidget(sep)

        # ── Formulaire en grille ──
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setColumnStretch(1, 1)

        row = 0
        # Identifiant
        lbl_username = QLabel("Identifiant : *")
        lbl_username.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._inp_username = QLineEdit(self.user_data.get("username", ""))
        self._inp_username.setPlaceholderText("Ex: jdupont")
        grid.addWidget(lbl_username, row, 0)
        grid.addWidget(self._inp_username, row, 1)

        row += 1
        # Nom complet
        lbl_name = QLabel("Nom complet :")
        lbl_name.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._inp_fullname = QLineEdit(self.user_data.get("full_name", ""))
        self._inp_fullname.setPlaceholderText("Ex: Jean Dupont")
        grid.addWidget(lbl_name, row, 0)
        grid.addWidget(self._inp_fullname, row, 1)

        row += 1
        # Rôle
        lbl_role = QLabel("Rôle : *")
        lbl_role.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._combo_role = QComboBox()
        for role_key, info in ROLES.items():
            self._combo_role.addItem(f"{info['label']} ({role_key})", role_key)

        current_role = self.user_data.get("role", "TECHNICIEN")
        index = self._combo_role.findData(current_role)
        if index >= 0:
            self._combo_role.setCurrentIndex(index)

        grid.addWidget(lbl_role, row, 0)
        grid.addWidget(self._combo_role, row, 1)

        row += 1
        # Mot de passe
        lbl_pwd = QLabel("Mot de passe : " + ("" if self.is_edit_mode else "*"))
        lbl_pwd.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._inp_pwd = QLineEdit()
        self._inp_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        if self.is_edit_mode:
            self._inp_pwd.setPlaceholderText("Laisser vide pour ne pas modifier")
        else:
            self._inp_pwd.setPlaceholderText("Saisir un mot de passe")
        grid.addWidget(lbl_pwd, row, 0)
        grid.addWidget(self._inp_pwd, row, 1)

        row += 1
        # Confirmation mot de passe
        lbl_pwd_confirm = QLabel("Confirmation :")
        lbl_pwd_confirm.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._inp_pwd_confirm = QLineEdit()
        self._inp_pwd_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self._inp_pwd_confirm.setPlaceholderText("Confirmer le mot de passe")
        grid.addWidget(lbl_pwd_confirm, row, 0)
        grid.addWidget(self._inp_pwd_confirm, row, 1)

        layout.addLayout(grid)

        # Note d'information sur les rôles
        self._lbl_role_desc = QLabel()
        self._lbl_role_desc.setWordWrap(True)
        self._lbl_role_desc.setStyleSheet(
            "color: #4A5568; background-color: #EBF5FB; padding: 8px; border-radius: 6px; font-size: 11px;"
        )
        self._combo_role.currentIndexChanged.connect(self._update_role_desc)
        layout.addWidget(self._lbl_role_desc)
        self._update_role_desc()

        # ── Boutons d'action ──
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_save = QPushButton("Enregistrer")
        btn_save.setDefault(True)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                font-weight: 700;
                padding: 6px 16px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        btn_save.clicked.connect(self._validate_and_accept)
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)

    def _update_role_desc(self) -> None:
        role_key = self._combo_role.currentData()
        info = ROLES.get(role_key, {})
        desc = info.get("description", "")
        self._lbl_role_desc.setText(f"ℹ️  <b>{info.get('label', '')}</b> : {desc}")

    def _validate_and_accept(self) -> None:
        username = self._inp_username.text().strip()
        pwd = self._inp_pwd.text()
        pwd_confirm = self._inp_pwd_confirm.text()
        role = self._combo_role.currentData()

        if not username:
            QMessageBox.warning(self, "Validation", "Veuillez spécifier un identifiant utilisateur.")
            self._inp_username.setFocus()
            return

        # Check username uniqueness
        exclude_id = self.user_data.get("id") if self.is_edit_mode else None
        if self.user_model.username_exists(username, exclude_id):
            QMessageBox.warning(
                self, "Validation", f"L'identifiant « {username} » est déjà utilisé par un autre compte."
            )
            self._inp_username.setFocus()
            return

        if not self.is_edit_mode and not pwd:
            QMessageBox.warning(self, "Validation", "Le mot de passe est obligatoire pour un nouveau compte.")
            self._inp_pwd.setFocus()
            return

        if pwd and pwd != pwd_confirm:
            QMessageBox.warning(self, "Validation", "Les deux mots de passe ne correspondent pas.")
            self._inp_pwd_confirm.setFocus()
            return

        self.accept()

    def get_data(self) -> dict:
        """Retourne les données validées du formulaire."""
        return {
            "username": self._inp_username.text().strip(),
            "full_name": self._inp_fullname.text().strip(),
            "role": self._combo_role.currentData(),
            "password": self._inp_pwd.text().strip() or None,
        }

