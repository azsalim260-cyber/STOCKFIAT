"""
views/dialogs/stock_laptop_dialog.py — Formulaire de saisie d'un Laptop en Stock
───────────────────────────────────────────────────────────────────────────────
Contenu :
  • NUM FAN (vérification d'unicité)
  • SERIAL
  • MODEL
  • QUANTITE (nombre entier >= 1)
  • OS LICENSE (Liste déroulante : 'Sans licence', 'Avec licence')
  • Bouton Ajouter / Enregistrer & Bouton Annuler
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QSpinBox, QComboBox, QPushButton,
    QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from models.stock_laptop_model import StockLaptopModel, LICENSE_OPTIONS


class StockLaptopDialog(QDialog):
    """Dialogue de saisie / modification pour un équipement du stock laptop."""

    def __init__(self, parent=None, data: dict | None = None):
        super().__init__(parent)
        self.data = data or {}
        self.is_edit_mode = bool(data)
        self.model = StockLaptopModel()

        title = "Modifier Laptop du Stock" if self.is_edit_mode else "Ajouter Laptop au Stock"
        self.setWindowTitle(title)
        self.setFixedWidth(480)
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

        # ── Formulaire ──
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setColumnStretch(1, 1)

        row = 0
        # 1. NUM FAN (Unique)
        lbl_fan = QLabel("NUM FAN : *")
        lbl_fan.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._inp_fan = QLineEdit(self.data.get("fan", ""))
        self._inp_fan.setPlaceholderText("Ex: FAN-8820")
        grid.addWidget(lbl_fan, row, 0)
        grid.addWidget(self._inp_fan, row, 1)

        row += 1
        # 2. SERIAL
        lbl_serial = QLabel("SERIAL :")
        lbl_serial.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._inp_serial = QLineEdit(self.data.get("serial", ""))
        self._inp_serial.setPlaceholderText("Ex: CNU910283X")
        grid.addWidget(lbl_serial, row, 0)
        grid.addWidget(self._inp_serial, row, 1)

        row += 1
        # 3. MODEL
        lbl_model = QLabel("MODEL :")
        lbl_model.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._inp_model = QLineEdit(self.data.get("model", ""))
        self._inp_model.setPlaceholderText("Ex: HP EliteBook 840 G8")
        grid.addWidget(lbl_model, row, 0)
        grid.addWidget(self._inp_model, row, 1)

        row += 1
        # 4. QUANTITÉ
        lbl_qty = QLabel("QUANTITÉ : *")
        lbl_qty.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._spin_qty = QSpinBox()
        self._spin_qty.setRange(1, 9999)
        self._spin_qty.setValue(int(self.data.get("quantite", 1)))
        self._spin_qty.setFixedHeight(34)
        grid.addWidget(lbl_qty, row, 0)
        grid.addWidget(self._spin_qty, row, 1)

        row += 1
        # 5. OS LICENSE (Droplist: Sans licence, Avec licence)
        lbl_lic = QLabel("OS LICENSE : *")
        lbl_lic.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._combo_license = QComboBox()
        self._combo_license.setFixedHeight(34)
        for opt in LICENSE_OPTIONS:
            self._combo_license.addItem(opt)

        current_lic = self.data.get("license", "Sans licence")
        idx = self._combo_license.findText(current_lic)
        if idx >= 0:
            self._combo_license.setCurrentIndex(idx)

        grid.addWidget(lbl_lic, row, 0)
        grid.addWidget(self._combo_license, row, 1)

        layout.addLayout(grid)

        # Note de validation
        lbl_note = QLabel("ℹ️  Le numéro FAN doit être unique dans tout le stock.")
        lbl_note.setStyleSheet("color: #7F8C8D; font-size: 11px; margin-top: 4px;")
        layout.addWidget(lbl_note)

        # ── Boutons d'action ──
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Annuler")
        btn_cancel.setObjectName("btn_cancel")
        btn_cancel.setFixedSize(110, 36)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_save = QPushButton("Enregistrer" if self.is_edit_mode else "Ajouter")
        btn_save.setObjectName("btn_save")
        btn_save.setDefault(True)
        btn_save.setFixedSize(120, 36)
        btn_save.clicked.connect(self._validate_and_accept)
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)

    def _validate_and_accept(self) -> None:
        fan = self._inp_fan.text().strip()
        if not fan:
            QMessageBox.warning(self, "Champ requis", "Veuillez saisir le numéro FAN.")
            self._inp_fan.setFocus()
            return

        # ── Vérification condition d'unicité du FAN ──
        exclude_id = self.data.get("id") if self.is_edit_mode else None
        if self.model.is_fan_exists(fan, exclude_id=exclude_id):
            QMessageBox.warning(
                self,
                "NUM FAN déjà existant",
                f"Le numéro FAN « {fan} » est déjà utilisé par un autre équipement dans le stock !\n"
                "Chaque équipement doit avoir un numéro FAN unique."
            )
            self._inp_fan.setFocus()
            return

        self.accept()

    def get_data(self) -> dict:
        """Retourne les valeurs saisies dans le formulaire."""
        return {
            "fan": self._inp_fan.text().strip(),
            "serial": self._inp_serial.text().strip(),
            "model": self._inp_model.text().strip(),
            "quantite": self._spin_qty.value(),
            "license": self._combo_license.currentText(),
        }

