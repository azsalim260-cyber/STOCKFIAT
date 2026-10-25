"""
views/dialogs/record_dialog.py  —  VIEW layer (MVC)
────────────────────────────────────────────────────
Add / Edit dialog. Pure UI — no DB calls here.
The controller calls get_data() after exec().
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QGroupBox,
)
from PyQt6.QtGui import QFont, QKeySequence


class RecordDialog(QDialog):
    """
    Parameters
    ----------
    parent : QWidget | None
    data   : dict | None
        Pre-fills fields when editing; None means "add new record".
    """

    def __init__(self, parent=None, data: dict | None = None):
        super().__init__(parent)
        self._inputs: dict[str, QLineEdit] = {}
        self.setWindowTitle(
            "Ajouter un équipement" if data is None else "Modifier l'équipement"
        )
        self.setMinimumWidth(580)
        self.setModal(True)
        self._build_ui(data or {})

    # ── UI construction ───────────────────────────────────────
    def _build_ui(self, data: dict) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(14)
        root.setContentsMargins(22, 22, 22, 22)

        # Title
        title = QLabel(self.windowTitle())
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #1A3A5C; margin-bottom: 4px;")
        root.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #AED6F1;")
        root.addWidget(sep)

        # ── Section: Utilisateur ──
        root.addWidget(self._make_section("👤  Utilisateur", [
            ("fan",        "FAN"),
            ("user_id",    "USER ID"),
            ("nom_prenom", "NOM PRÉNOM"),
            ("num_tel",    "NUM TÉL"),
        ], data))

        # ── Section: Informatique ──
        root.addWidget(self._make_section("💻  Équipement Informatique", [
            ("pc",            "PC"),
            ("pc_serial",     "PC SERIAL"),
            ("casque",        "CASQUE"),
            ("disque_backup", "DISQUE BACKUP"),
        ], data))

        # ── Section: Téléphonie ──
        root.addWidget(self._make_section("📞  Équipement Téléphonique", [
            ("app_tel",        "APPAREIL TÉL"),
            ("app_tel_serial", "APP TÉL SERIAL"),
        ], data))

        # ── Buttons ──
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancel = QPushButton("✕  Annuler")
        btn_cancel.setObjectName("btn_cancel")
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("✔  Enregistrer")
        btn_save.setObjectName("btn_save")
        btn_save.setDefault(True)
        btn_save.clicked.connect(self.accept)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        root.addLayout(btn_row)

    def _make_section(
        self, title: str, fields: list[tuple[str, str]], data: dict
    ) -> QGroupBox:
        grp  = QGroupBox(title)
        grid = QGridLayout(grp)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(8)

        for i, (key, label) in enumerate(fields):
            row_idx, col_idx = divmod(i, 2)
            lbl = QLabel(label + " :")
            inp = QLineEdit(data.get(key, ""))
            inp.setPlaceholderText(f"Saisir {label.lower()}…")
            self._inputs[key] = inp
            grid.addWidget(lbl, row_idx, col_idx * 2)
            grid.addWidget(inp, row_idx, col_idx * 2 + 1)

        return grp

    # ── Public API (used by controller) ──────────────────────
    def get_data(self) -> dict:
        """Return all field values stripped of surrounding whitespace."""
        return {key: inp.text().strip() for key, inp in self._inputs.items()}

