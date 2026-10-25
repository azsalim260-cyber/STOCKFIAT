"""
Gestionnaire de Parc Informatique & Téléphonique
Interface graphique PyQt6
"""

import sys
import csv
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QLineEdit, QLabel, QMessageBox, QHeaderView, QFrame, QStatusBar,
    QFileDialog, QComboBox, QToolBar, QSizePolicy, QAbstractItemView,
    QGroupBox, QGridLayout, QSplitter, QTextEdit, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import (
    QIcon, QFont, QColor, QAction, QPalette, QKeySequence,
    QLinearGradient, QBrush, QPainter, QPixmap
)

from main import Database, DB_PATH, COLUMNS

# ─────────────────────────────────────────────────────────────
#  Palette de couleurs (thème corporate bleu/gris)
# ─────────────────────────────────────────────────────────────
STYLE = """
QMainWindow, QDialog {
    background-color: #F4F6F9;
}
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
    color: #2C3E50;
}
/* ── Toolbar ── */
QToolBar {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #1A3A5C, stop:1 #2E86C1);
    border: none;
    padding: 4px 8px;
    spacing: 6px;
}
QToolBar QLabel {
    color: white;
    font-size: 18px;
    font-weight: bold;
    padding: 0 12px;
}
/* ── Boutons toolbar ── */
QToolBar QPushButton {
    background-color: rgba(255,255,255,0.15);
    color: white;
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 600;
    min-width: 90px;
}
QToolBar QPushButton:hover {
    background-color: rgba(255,255,255,0.28);
    border: 1px solid white;
}
QToolBar QPushButton:pressed {
    background-color: rgba(255,255,255,0.10);
}
/* ── Bouton Ajouter ── */
QPushButton#btn_add {
    background-color: #27AE60;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 16px;
    font-weight: 700;
}
QPushButton#btn_add:hover { background-color: #229954; }
/* ── Bouton Modifier ── */
QPushButton#btn_edit {
    background-color: #2980B9;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 16px;
    font-weight: 700;
}
QPushButton#btn_edit:hover { background-color: #1F618D; }
/* ── Bouton Supprimer ── */
QPushButton#btn_del {
    background-color: #C0392B;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 16px;
    font-weight: 700;
}
QPushButton#btn_del:hover { background-color: #A93226; }
/* ── Bouton Export ── */
QPushButton#btn_export {
    background-color: #8E44AD;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 16px;
    font-weight: 700;
}
QPushButton#btn_export:hover { background-color: #7D3C98; }
/* ── Barre de recherche ── */
QLineEdit#search_bar {
    border: 2px solid #BDC3C7;
    border-radius: 18px;
    padding: 6px 14px;
    background-color: white;
    font-size: 13px;
    min-width: 260px;
}
QLineEdit#search_bar:focus {
    border-color: #2E86C1;
}
/* ── Tableau ── */
QTableWidget {
    background-color: white;
    alternate-background-color: #EBF5FB;
    border: 1px solid #D5D8DC;
    border-radius: 6px;
    gridline-color: #D5D8DC;
    selection-background-color: #2E86C1;
    selection-color: white;
}
QTableWidget::item {
    padding: 6px 8px;
}
QHeaderView::section {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #2E86C1, stop:1 #1A5276);
    color: white;
    font-weight: 700;
    padding: 8px 6px;
    border: none;
    border-right: 1px solid #1A5276;
    font-size: 12px;
}
QHeaderView::section:first { border-radius: 6px 0 0 0; }
QHeaderView::section:last  { border-radius: 0 6px 0 0; border-right: none; }
/* ── Status bar ── */
QStatusBar {
    background-color: #1A3A5C;
    color: #AED6F1;
    font-size: 12px;
    padding: 2px 10px;
}
/* ── Formulaire Dialog ── */
QDialog QLabel {
    font-weight: 600;
    color: #1A5276;
}
QDialog QLineEdit {
    border: 1.5px solid #BDC3C7;
    border-radius: 5px;
    padding: 7px 10px;
    background: white;
    min-width: 260px;
}
QDialog QLineEdit:focus { border-color: #2E86C1; }
QGroupBox {
    font-weight: 700;
    color: #1A5276;
    border: 2px solid #AED6F1;
    border-radius: 8px;
    margin-top: 12px;
    padding: 8px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    background-color: #F4F6F9;
}
/* ── Boutons dialog ── */
QPushButton#btn_save {
    background-color: #27AE60;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 28px;
    font-weight: 700;
    font-size: 14px;
}
QPushButton#btn_save:hover { background-color: #229954; }
QPushButton#btn_cancel {
    background-color: #95A5A6;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 28px;
    font-weight: 700;
    font-size: 14px;
}
QPushButton#btn_cancel:hover { background-color: #7F8C8D; }
/* ── Combo filtre colonne ── */
QComboBox {
    border: 2px solid #BDC3C7;
    border-radius: 14px;
    padding: 5px 10px;
    background: white;
    min-width: 140px;
}
QComboBox:focus { border-color: #2E86C1; }
QComboBox QAbstractItemView {
    background: white;
    border: 1px solid #BDC3C7;
    selection-background-color: #2E86C1;
    selection-color: white;
}
"""


# ─────────────────────────────────────────────────────────────
#  Dialog Ajouter / Modifier
# ─────────────────────────────────────────────────────────────
class RecordDialog(QDialog):
    def __init__(self, parent=None, data: dict = None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un équipement" if data is None else "Modifier l'équipement")
        self.setMinimumWidth(560)
        self.setModal(True)
        self._inputs = {}
        self._build_ui(data or {})

    def _build_ui(self, data: dict):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        # ── Titre ──
        title = QLabel(self.windowTitle())
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #1A3A5C; margin-bottom: 6px;")
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #AED6F1;")
        layout.addWidget(sep)

        # ── Section Utilisateur ──
        grp_user = QGroupBox("👤  Utilisateur")
        form_user = QGridLayout(grp_user)
        form_user.setColumnStretch(1, 1)
        form_user.setColumnStretch(3, 1)
        form_user.setHorizontalSpacing(12)
        form_user.setVerticalSpacing(8)

        user_fields = [
            ("fan",        "FAN"),
            ("user_id",    "USER ID"),
            ("nom_prenom", "NOM PRÉNOM"),
            ("num_tel",    "NUM TÉL"),
        ]
        for i, (key, label) in enumerate(user_fields):
            row, col = divmod(i, 2)
            lbl = QLabel(label + " :")
            inp = QLineEdit(data.get(key, ""))
            inp.setPlaceholderText(f"Saisir {label.lower()}...")
            self._inputs[key] = inp
            form_user.addWidget(lbl, row, col * 2)
            form_user.addWidget(inp, row, col * 2 + 1)
        layout.addWidget(grp_user)

        # ── Section Informatique ──
        grp_it = QGroupBox("💻  Équipement Informatique")
        form_it = QGridLayout(grp_it)
        form_it.setColumnStretch(1, 1)
        form_it.setColumnStretch(3, 1)
        form_it.setHorizontalSpacing(12)
        form_it.setVerticalSpacing(8)

        it_fields = [
            ("pc",            "PC"),
            ("pc_serial",     "PC SERIAL"),
            ("casque",        "CASQUE"),
            ("disque_backup", "DISQUE BACKUP"),
        ]
        for i, (key, label) in enumerate(it_fields):
            row, col = divmod(i, 2)
            lbl = QLabel(label + " :")
            inp = QLineEdit(data.get(key, ""))
            inp.setPlaceholderText(f"Saisir {label.lower()}...")
            self._inputs[key] = inp
            form_it.addWidget(lbl, row, col * 2)
            form_it.addWidget(inp, row, col * 2 + 1)
        layout.addWidget(grp_it)

        # ── Section Téléphonie ──
        grp_tel = QGroupBox("📞  Équipement Téléphonique")
        form_tel = QGridLayout(grp_tel)
        form_tel.setColumnStretch(1, 1)
        form_tel.setColumnStretch(3, 1)
        form_tel.setHorizontalSpacing(12)
        form_tel.setVerticalSpacing(8)

        tel_fields = [
            ("app_tel",       "APPAREIL TÉL"),
            ("app_tel_serial","APP TÉL SERIAL"),
        ]
        for i, (key, label) in enumerate(tel_fields):
            row, col = divmod(i, 2)
            lbl = QLabel(label + " :")
            inp = QLineEdit(data.get(key, ""))
            inp.setPlaceholderText(f"Saisir {label.lower()}...")
            self._inputs[key] = inp
            form_tel.addWidget(lbl, row, col * 2)
            form_tel.addWidget(inp, row, col * 2 + 1)
        layout.addWidget(grp_tel)

        # ── Boutons ──
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton("✕  Annuler")
        btn_cancel.setObjectName("btn_cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("✔  Enregistrer")
        btn_save.setObjectName("btn_save")
        btn_save.clicked.connect(self.accept)
        btn_save.setDefault(True)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    def get_data(self) -> dict:
        return {key: inp.text().strip() for key, inp in self._inputs.items()}


# ─────────────────────────────────────────────────────────────
#  Fenêtre principale
# ─────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database(DB_PATH)
        self.setWindowTitle("Gestionnaire de Parc Informatique & Téléphonique")
        self.setMinimumSize(1280, 720)
        self._build_ui()
        self._refresh()

    # ── Construction UI ──────────────────────────────────────
    def _build_ui(self):
        # Toolbar principale
        toolbar = self._make_toolbar()
        self.addToolBar(toolbar)

        # Conteneur central
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 10, 12, 10)
        main_layout.setSpacing(8)

        # Barre de contrôle (recherche + boutons actions)
        ctrl_bar = self._make_ctrl_bar()
        main_layout.addLayout(ctrl_bar)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(len(COLUMNS))
        self.table.setHorizontalHeaderLabels([label for _, label in COLUMNS])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setDefaultSectionSize(36)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSortingEnabled(True)
        self.table.doubleClicked.connect(self._on_edit)
        main_layout.addWidget(self.table)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self._lbl_count = QLabel()
        self.status.addPermanentWidget(self._lbl_count)

    def _make_toolbar(self) -> QToolBar:
        tb = QToolBar("Main Toolbar")
        tb.setMovable(False)
        tb.setIconSize(QSize(22, 22))
        tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        title_lbl = QLabel("🖥  Parc Informatique & Téléphonique")
        title_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: white; padding: 0 8px;")
        tb.addWidget(title_lbl)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tb.addWidget(spacer)

        # Heure
        self._clock_lbl = QLabel()
        self._clock_lbl.setStyleSheet("color: #AED6F1; font-size:12px; padding-right:10px;")
        tb.addWidget(self._clock_lbl)
        clock_timer = QTimer(self)
        clock_timer.timeout.connect(self._update_clock)
        clock_timer.start(1000)
        self._update_clock()

        return tb

    def _make_ctrl_bar(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)

        # Combo colonne filtre
        self._combo_col = QComboBox()
        self._combo_col.addItem("Toutes colonnes")
        for _, label in COLUMNS:
            self._combo_col.addItem(label)
        row.addWidget(self._combo_col)

        # Barre de recherche
        self._search = QLineEdit()
        self._search.setObjectName("search_bar")
        self._search.setPlaceholderText("🔍  Rechercher...")
        self._search.textChanged.connect(self._refresh)
        self._combo_col.currentTextChanged.connect(lambda _: self._refresh())
        row.addWidget(self._search)

        row.addStretch()

        # Boutons CRUD
        btn_add = QPushButton("➕  Ajouter")
        btn_add.setObjectName("btn_add")
        btn_add.setShortcut(QKeySequence("Ctrl+N"))
        btn_add.clicked.connect(self._on_add)
        row.addWidget(btn_add)

        btn_edit = QPushButton("✏  Modifier")
        btn_edit.setObjectName("btn_edit")
        btn_edit.setShortcut(QKeySequence("Ctrl+E"))
        btn_edit.clicked.connect(self._on_edit)
        row.addWidget(btn_edit)

        btn_del = QPushButton("🗑  Supprimer")
        btn_del.setObjectName("btn_del")
        btn_del.setShortcut(QKeySequence("Delete"))
        btn_del.clicked.connect(self._on_delete)
        row.addWidget(btn_del)

        btn_export = QPushButton("📤  Exporter CSV")
        btn_export.setObjectName("btn_export")
        btn_export.setShortcut(QKeySequence("Ctrl+S"))
        btn_export.clicked.connect(self._on_export)
        row.addWidget(btn_export)

        return row

    # ── Horloge ──────────────────────────────────────────────
    def _update_clock(self):
        now = datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
        self._clock_lbl.setText(now)

    # ── Chargement données ────────────────────────────────────
    def _refresh(self):
        search = self._search.text().strip()
        column = self._combo_col.currentText()
        rows = self.db.fetch_all(search, column)

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(str(row["fan"] or "")))
            self.table.setItem(r, 1, QTableWidgetItem(str(row["user_id"] or "")))
            self.table.setItem(r, 2, QTableWidgetItem(str(row["nom_prenom"] or "")))
            self.table.setItem(r, 3, QTableWidgetItem(str(row["pc"] or "")))
            self.table.setItem(r, 4, QTableWidgetItem(str(row["pc_serial"] or "")))
            self.table.setItem(r, 5, QTableWidgetItem(str(row["num_tel"] or "")))
            self.table.setItem(r, 6, QTableWidgetItem(str(row["app_tel"] or "")))
            self.table.setItem(r, 7, QTableWidgetItem(str(row["app_tel_serial"] or "")))
            self.table.setItem(r, 8, QTableWidgetItem(str(row["casque"] or "")))
            self.table.setItem(r, 9, QTableWidgetItem(str(row["disque_backup"] or "")))
            # Stocker l'id en UserRole sur la 1ère colonne
            self.table.item(r, 0).setData(Qt.ItemDataRole.UserRole, row["id"])

        self.table.setSortingEnabled(True)
        total = self.db.count()
        shown = len(rows)
        self._lbl_count.setText(
            f"  {shown} affiché(s) / {total} enregistrement(s) total  "
        )
        self.status.showMessage(
            f"Base de données : {DB_PATH}  |  Dernière mise à jour : {datetime.now().strftime('%H:%M:%S')}"
        )

    # ── Récupérer la ligne sélectionnée ──────────────────────
    def _selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None, None
        item = self.table.item(row, 0)
        if item is None:
            return None, None
        return item.data(Qt.ItemDataRole.UserRole), row

    def _row_data(self, row: int) -> dict:
        keys = [key for key, _ in COLUMNS]
        return {key: (self.table.item(row, c).text() if self.table.item(row, c) else "")
                for c, key in enumerate(keys)}

    # ── CRUD ─────────────────────────────────────────────────
    def _on_add(self):
        dlg = RecordDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.db.insert(dlg.get_data())
            self._refresh()
            self.status.showMessage("✔  Enregistrement ajouté avec succès.", 3000)

    def _on_edit(self):
        row_id, row_idx = self._selected_id()
        if row_id is None:
            QMessageBox.information(self, "Sélection", "Veuillez sélectionner une ligne à modifier.")
            return
        data = self._row_data(row_idx)
        dlg = RecordDialog(self, data)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.db.update(row_id, dlg.get_data())
            self._refresh()
            self.status.showMessage("✔  Enregistrement modifié avec succès.", 3000)

    def _on_delete(self):
        row_id, row_idx = self._selected_id()
        if row_id is None:
            QMessageBox.information(self, "Sélection", "Veuillez sélectionner une ligne à supprimer.")
            return
        nom = self.table.item(row_idx, 2).text() if self.table.item(row_idx, 2) else ""
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Supprimer l'enregistrement de  « {nom} »  ?\nCette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete(row_id)
            self._refresh()
            self.status.showMessage("✔  Enregistrement supprimé.", 3000)

    # ── Export CSV ───────────────────────────────────────────
    def _on_export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter en CSV",
            str(Path.home() / f"parc_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"),
            "CSV Files (*.csv)"
        )
        if not path:
            return
        rows = self.db.fetch_all()
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([label for _, label in COLUMNS])
            for row in rows:
                writer.writerow([row[key] or "" for key, _ in COLUMNS])
        QMessageBox.information(self, "Export réussi",
                                f"✔  Fichier exporté avec succès :\n{path}")


# ─────────────────────────────────────────────────────────────
#  Point d'entrée
# ─────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Gestionnaire Parc IT")
    app.setApplicationVersion("1.0")
    app.setStyleSheet(STYLE)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

