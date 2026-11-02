"""
views/stock_laptop_view.py — Écran de gestion du Stock Laptops (VIEW layer)
───────────────────────────────────────────────────────────────────────────
Fonctionnalités :
  • Bouton « Ajouter Laptop » ouvrant le formulaire de saisie
  • Affichage des laptops sous forme de tableau interactif
  • Saisie et affichage de la colonne USER ID
  • Barre de recherche par NUM FAN
  • Barre de recherche par USER ID
  • Menu déroulant de filtre par OS LICENSE (Toutes, Sans licence, Avec licence)
  • Ligne entière colorée en VERT lorsque le laptop est libre (FAN == 'FREE')
  • Bouton « Imprimer (Excel) » pour exporter/imprimer tout le tableau dans un fichier Excel
  • Contrôle des accès selon le rôle de l'utilisateur (RBAC)
"""

import logging

try:
    from PyQt6.QtWidgets import (  # type: ignore[reportMissingImports, import-not-found]
        QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
        QTableWidgetItem, QPushButton, QLineEdit, QComboBox,
        QLabel, QHeaderView, QAbstractItemView, QFrame,
        QSizePolicy,
    )
    from PyQt6.QtCore import Qt, QTimer  # type: ignore[reportMissingImports, import-not-found]
    from PyQt6.QtGui import QFont, QColor  # type: ignore[reportMissingImports, import-not-found]
except ModuleNotFoundError:
    from PySide6.QtWidgets import (  # type: ignore[reportMissingImports, import-not-found]
        QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
        QTableWidgetItem, QPushButton, QLineEdit, QComboBox,
        QLabel, QHeaderView, QAbstractItemView, QFrame,
        QSizePolicy,
    )
    from PySide6.QtCore import Qt, QTimer  # type: ignore[reportMissingImports, import-not-found]
    from PySide6.QtGui import QFont, QColor  # type: ignore[reportMissingImports, import-not-found]

from models.user_model import ROLES
from controllers.stock_laptop_controller import StockLaptopController

logger = logging.getLogger(__name__)


class StockLaptopView(QWidget):
    """Vue complète pour la gestion du stock des laptops."""

    COLUMNS = [
        ("id", "ID"),
        ("fan", "NUM FAN"),
        ("user_id", "USER ID"),
        ("serial", "SERIAL"),
        ("model", "MODEL"),
        ("quantite", "QUANTITÉ"),
        ("license", "OS LICENSE"),
        ("created_at", "DATE AJOUT"),
        ("actions", "ACTIONS"),
    ]

    def __init__(self, parent=None, current_user: dict | None = None):
        super().__init__(parent)
        self.current_user = current_user or {}
        self._ctrl = StockLaptopController(self)

        self._build_ui()
        self._apply_permissions()
        self._ctrl.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 10)
        layout.setSpacing(10)

        # ── Barre d'actions supérieure ──
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        # 1. Bouton "Ajouter Laptop"
        self._btn_add = QPushButton("➕  Ajouter Laptop")
        self._btn_add.setObjectName("btn_add_laptop")
        self._btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_add.setStyleSheet("""
            QPushButton#btn_add_laptop {
                background-color: #27AE60;
                color: white;
                font-weight: 700;
                font-size: 13px;
                padding: 7px 16px;
                border: none;
                border-radius: 6px;
            }
            QPushButton#btn_add_laptop:hover {
                background-color: #229954;
            }
        """)
        self._btn_add.clicked.connect(self._ctrl.on_add)
        top_bar.addWidget(self._btn_add)

        # Séparateur vertical
        sep_v1 = QFrame()
        sep_v1.setFrameShape(QFrame.Shape.VLine)
        sep_v1.setStyleSheet("color: #D5D8DC; margin: 0 4px;")
        top_bar.addWidget(sep_v1)

        # 2. Barre de recherche par FAN
        self._search_fan = QLineEdit()
        self._search_fan.setPlaceholderText("🔍  Rechercher par FAN...")
        self._search_fan.setClearButtonEnabled(True)
        self._search_fan.setMinimumWidth(190)
        self._search_fan.setStyleSheet("""
            QLineEdit {
                border: 2px solid #BDC3C7;
                border-radius: 16px;
                padding: 5px 12px;
                background-color: white;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #2E86C1;
            }
        """)
        self._search_fan.textChanged.connect(self._on_search_changed)
        top_bar.addWidget(self._search_fan)

        # 3. Barre de recherche par USER ID
        self._search_user_id = QLineEdit()
        self._search_user_id.setPlaceholderText("🔍  Rechercher par USER ID...")
        self._search_user_id.setClearButtonEnabled(True)
        self._search_user_id.setMinimumWidth(190)
        self._search_user_id.setStyleSheet("""
            QLineEdit {
                border: 2px solid #BDC3C7;
                border-radius: 16px;
                padding: 5px 12px;
                background-color: white;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #2E86C1;
            }
        """)
        self._search_user_id.textChanged.connect(self._on_search_changed)
        top_bar.addWidget(self._search_user_id)

        # 4. Liste déroulante de filtre par LICENSE
        lbl_filter = QLabel("Licence :")
        lbl_filter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl_filter.setStyleSheet("color: #2C3E50; margin-left: 4px;")
        top_bar.addWidget(lbl_filter)

        self._combo_license = QComboBox()
        self._combo_license.addItem("Toutes licences")
        self._combo_license.addItem("Avec licence")
        self._combo_license.addItem("Sans licence")
        self._combo_license.setFixedHeight(32)
        self._combo_license.currentTextChanged.connect(lambda _: self._ctrl.refresh())
        top_bar.addWidget(self._combo_license)

        top_bar.addStretch()

        # 5. Bouton "Imprimer / Exporter Excel"
        self._btn_print = QPushButton("🖨️  Imprimer (Excel)")
        self._btn_print.setObjectName("btn_print_excel")
        self._btn_print.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_print.setStyleSheet("""
            QPushButton#btn_print_excel {
                background-color: #8E44AD;
                color: white;
                font-weight: 700;
                font-size: 13px;
                padding: 7px 16px;
                border: none;
                border-radius: 6px;
            }
            QPushButton#btn_print_excel:hover {
                background-color: #7D3C98;
            }
        """)
        self._btn_print.clicked.connect(self._ctrl.on_print_excel)
        top_bar.addWidget(self._btn_print)

        layout.addLayout(top_bar)

        # ── Bandeau des statistiques rapides ──
        self._lbl_stats = QLabel()
        self._lbl_stats.setStyleSheet("""
            QLabel {
                background-color: #EBF5FB;
                color: #1B4F72;
                border: 1px solid #AED6F1;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 600;
            }
        """)
        layout.addWidget(self._lbl_stats)

        # ── Tableau d'affichage des laptops ──
        self._table = QTableWidget()
        self._table.setColumnCount(len(self.COLUMNS))
        self._table.setHorizontalHeaderLabels([label for _, label in self.COLUMNS])
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setDefaultSectionSize(40)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self._table.horizontalHeader().setStretchLastSection(True)

        # Largeurs initiales des colonnes
        self._table.setColumnWidth(0, 45)   # ID
        self._table.setColumnWidth(1, 130)  # NUM FAN
        self._table.setColumnWidth(2, 130)  # USER ID
        self._table.setColumnWidth(3, 140)  # SERIAL
        self._table.setColumnWidth(4, 180)  # MODEL
        self._table.setColumnWidth(5, 80)   # QUANTITÉ
        self._table.setColumnWidth(6, 130)  # OS LICENSE
        self._table.setColumnWidth(7, 140)  # DATE AJOUT
        self._table.setColumnWidth(8, 110)  # ACTIONS

        self._table.doubleClicked.connect(self._on_table_double_clicked)
        layout.addWidget(self._table)

    def _on_search_changed(self) -> None:
        """Déclenche la recherche avec un léger délai (debounce)."""
        if not hasattr(self, "_search_timer"):
            self._search_timer = QTimer(self)
            self._search_timer.setSingleShot(True)
            self._search_timer.timeout.connect(self._ctrl.refresh)
        self._search_timer.start(250)

    # ── Getters pour les filtres ──
    def get_search_fan(self) -> str:
        return self._search_fan.text().strip()

    def get_search_user_id(self) -> str:
        return self._search_user_id.text().strip()

    def get_filter_license(self) -> str:
        return self._combo_license.currentText()

    # ── Remplissage du tableau ──
    def populate_table(self, rows: list[dict]) -> None:
        """
        Remplit le tableau avec les équipements du stock.
        Règle : Lorsque le laptop est libre (FAN == 'FREE'), toute la ligne est colorée en VERT.
        """
        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(rows))

        perms = ROLES.get(self.current_user.get("role", "LECTEUR"), ROLES["LECTEUR"])
        can_edit = perms.get("can_edit", False)
        can_delete = perms.get("can_delete", False)

        # Couleurs pour les lignes "FREE" (vert pastel moderne + texte lisible)
        color_green_bg = QColor("#D4EFDF")    # Fond vert pastel
        color_green_text = QColor("#145A32")  # Texte vert foncé pour fort contraste

        for r, row in enumerate(rows):
            fan_val = str(row.get("fan") or "").strip()
            user_id_val = str(row.get("user_id") or "").strip()

            # Détection de l'état "FREE" (libre)
            is_free = (fan_val.upper() == "FREE") or (user_id_val.upper() in ("FREE", "LIBRE"))

            # 0. ID
            item_id = QTableWidgetItem(str(row.get("id")))
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(r, 0, item_id)

            # 1. NUM FAN (en gras)
            display_fan = "FREE 🟢" if fan_val.upper() == "FREE" else fan_val
            item_fan = QTableWidgetItem(display_fan)
            item_fan.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self._table.setItem(r, 1, item_fan)

            # 2. USER ID
            display_uid = user_id_val if user_id_val else ("(Libre)" if is_free else "-")
            item_uid = QTableWidgetItem(display_uid)
            if not user_id_val and is_free:
                item_uid.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            self._table.setItem(r, 2, item_uid)

            # 3. SERIAL
            self._table.setItem(r, 3, QTableWidgetItem(str(row.get("serial") or "")))

            # 4. MODEL
            self._table.setItem(r, 4, QTableWidgetItem(str(row.get("model") or "")))

            # 5. QUANTITÉ (centrée)
            item_qty = QTableWidgetItem(str(row.get("quantite") or 1))
            item_qty.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(r, 5, item_qty)

            # 6. OS LICENSE (avec couleur/style)
            license_val = str(row.get("license") or "Sans licence")
            item_lic = QTableWidgetItem(license_val)
            item_lic.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_lic.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            if not is_free:
                if license_val == "Avec licence":
                    item_lic.setForeground(QColor("#1E8449"))  # Vert
                else:
                    item_lic.setForeground(QColor("#7F8C8D"))  # Gris
            self._table.setItem(r, 6, item_lic)

            # 7. DATE AJOUT
            item_date = QTableWidgetItem(str(row.get("created_at") or ""))
            item_date.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(r, 7, item_date)

            # Stocker les données complètes sur la 1ère colonne
            item_id.setData(Qt.ItemDataRole.UserRole, row)

            # 8. Colonne ACTIONS : Icônes Modifier ✏️ et Supprimer 🗑️
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 2, 4, 2)
            action_layout.setSpacing(6)
            action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Bouton Modifier (✏️)
            btn_edit_row = QPushButton("✏️")
            btn_edit_row.setToolTip("Modifier cet équipement")
            btn_edit_row.setFixedSize(30, 28)
            btn_edit_row.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_edit_row.setStyleSheet("""
                QPushButton {
                    background-color: #2980B9;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #1F618D; }
                QPushButton:disabled { background-color: #BDC3C7; }
            """)
            btn_edit_row.setEnabled(can_edit)
            btn_edit_row.clicked.connect(lambda _, row_id=row["id"], d=row: self._ctrl.on_edit(row_id, d))
            action_layout.addWidget(btn_edit_row)

            # Bouton Supprimer (🗑️)
            btn_del_row = QPushButton("🗑️")
            btn_del_row.setToolTip("Supprimer du stock")
            btn_del_row.setFixedSize(30, 28)
            btn_del_row.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del_row.setStyleSheet("""
                QPushButton {
                    background-color: #C0392B;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #A93226; }
                QPushButton:disabled { background-color: #BDC3C7; }
            """)
            btn_del_row.setEnabled(can_delete)
            btn_del_row.clicked.connect(lambda _, row_id=row["id"], fan_num=row["fan"]: self._ctrl.on_delete(row_id, fan_num))
            action_layout.addWidget(btn_del_row)

            # ── SI LE LAPTOP EST LIBRE (FREE) : TOUTE LA LIGNE EN VERT ──
            if is_free:
                for c in range(8):  # Pour toutes les colonnes 0 à 7
                    cell_item = self._table.item(r, c)
                    if cell_item:
                        cell_item.setBackground(color_green_bg)
                        cell_item.setForeground(color_green_text)
                action_widget.setStyleSheet("background-color: #D4EFDF; border-radius: 4px;")

            self._table.setCellWidget(r, 8, action_widget)

        self._table.setSortingEnabled(True)

    def update_stats(self, stats: dict, count_shown: int) -> None:
        """Met à jour le bandeau d'information statistique."""
        total_qty = stats.get("total_quantite", 0)
        total_refs = stats.get("total_references", 0)
        free_qty = stats.get("free_laptops", 0)
        with_lic = stats.get("avec_licence", 0)
        without_lic = stats.get("sans_licence", 0)

        self._lbl_stats.setText(
            f"📊  Stock Total : <b>{total_qty}</b> pc(s) ({total_refs} références)  •  "
            f"🟢 <b>Libres (FREE) : {free_qty}</b>  •  "
            f"Avec licence : <b>{with_lic}</b>  •  "
            f"Sans licence : <b>{without_lic}</b>  •  "
            f"Affichés : <b>{count_shown}</b>"
        )

    def set_current_user(self, user: dict) -> None:
        """Met à jour l'utilisateur actif et réapplique les autorisations."""
        self.current_user = user
        self._apply_permissions()
        self._ctrl.refresh()

    def _apply_permissions(self) -> None:
        """Ajuste la visibilité et l'accès des boutons selon le rôle."""
        role_key = self.current_user.get("role", "LECTEUR")
        perms = ROLES.get(role_key, ROLES["LECTEUR"])

        self._btn_add.setVisible(perms.get("can_add", False))
        self._btn_print.setVisible(perms.get("can_export", True))

    def _on_table_double_clicked(self) -> None:
        """Ouvre l'édition au double-clic si l'utilisateur y est autorisé."""
        perms = ROLES.get(self.current_user.get("role", "LECTEUR"), ROLES["LECTEUR"])
        if not perms.get("can_edit", False):
            return

        r = self._table.currentRow()
        if r < 0:
            return
        item_id = self._table.item(r, 0)
        if item_id:
            data = item_id.data(Qt.ItemDataRole.UserRole)
            if data:
                self._ctrl.on_edit(data["id"], data)
