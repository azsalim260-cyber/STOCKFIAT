"""
views/main_window.py  —  VIEW layer (MVC)
──────────────────────────────────────────
Fenêtre principale intégrant :
  • Barre supérieure (Top Bar) avec navigation multi-écrans :
      1. [📋 Affectations Parc] : Gestion et suivi des équipements affectés
      2. [💻 Stock Laptops] : Gestion du stock de laptops avec ajout, recherche, licence & export Excel
  • Contrôle d'accès basé sur les rôles (RBAC : Admin, Technicien, Lecteur)
  • Gestion des utilisateurs (Admin) et bouton de Déconnexion
  • Horloge en direct et journalisation structurée
"""

import importlib
import logging
from datetime import datetime

try:
    QtWidgets = importlib.import_module("PyQt6.QtWidgets")
    QtCore = importlib.import_module("PyQt6.QtCore")
    QtGui = importlib.import_module("PyQt6.QtGui")
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "PyQt6 is required to run the Parc Informatique application. "
        "Install it with: pip install PyQt6"
    ) from exc

QMainWindow = QtWidgets.QMainWindow
QWidget = QtWidgets.QWidget
QVBoxLayout = QtWidgets.QVBoxLayout
QHBoxLayout = QtWidgets.QHBoxLayout
QTableWidget = QtWidgets.QTableWidget
QTableWidgetItem = QtWidgets.QTableWidgetItem
QHeaderView = QtWidgets.QHeaderView
QPushButton = QtWidgets.QPushButton
QLineEdit = QtWidgets.QLineEdit
QLabel = QtWidgets.QLabel
QComboBox = QtWidgets.QComboBox
QToolBar = QtWidgets.QToolBar
QStatusBar = QtWidgets.QStatusBar
QProgressBar = QtWidgets.QProgressBar
QStackedWidget = QtWidgets.QStackedWidget
QSizePolicy = QtWidgets.QSizePolicy
QAbstractItemView = QtWidgets.QAbstractItemView
QMessageBox = QtWidgets.QMessageBox
QFrame = QtWidgets.QFrame

Qt = QtCore.Qt
QTimer = QtCore.QTimer
QSize = QtCore.QSize
pyqtSignal = QtCore.pyqtSignal

QFont = QtGui.QFont
QKeySequence = QtGui.QKeySequence

from config import COLUMNS, PAGE_SIZE
from models.user_model import ROLES
from controllers.parc_controller import ParcController
from views.stock_laptop_view import StockLaptopView

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Fenêtre principale avec barre de navigation supérieure et gestion de session.
    """

    page_changed = pyqtSignal(int)

    def __init__(self, current_user: dict | None = None) -> None:
        super().__init__()
        self.current_user = current_user or {}
        self._total_pages = 1
        self._ctrl = ParcController(self)

        self.setWindowTitle("Gestionnaire de Parc Informatique & Téléphonique")
        self.setMinimumSize(1340, 780)
        self._build_ui()
        self._apply_permissions()

        # Chargement initial des données de la page d'affectations
        self._ctrl.load_page()

    # ══════════════════════════════════════════════════════════
    #  Construction de l'interface
    # ══════════════════════════════════════════════════════════
    def _build_ui(self) -> None:
        # Barre d'outils supérieure principale (Top Bar)
        self.addToolBar(self._make_toolbar())

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(10, 8, 10, 6)
        root_layout.setSpacing(6)

        # ── QStackedWidget pour naviguer entre les écrans ──
        self._stacked = QStackedWidget()

        # Écran 1 : Affectations du Parc Informatique
        self._parc_screen = self._build_parc_screen()
        self._stacked.addWidget(self._parc_screen)

        # Écran 2 : Stock Laptops
        self._stock_screen = StockLaptopView(parent=self, current_user=self.current_user)
        self._stacked.addWidget(self._stock_screen)

        root_layout.addWidget(self._stacked)

        # ── Status bar globale ──
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

        self._lbl_status_user = QLabel()
        self._status_bar.addWidget(self._lbl_status_user)

        self._lbl_count = QLabel()
        self._status_bar.addPermanentWidget(self._lbl_count)

        self._progress = QProgressBar()
        self._progress.setMaximumWidth(160)
        self._progress.setRange(0, 0)
        self._progress.setVisible(False)
        self._status_bar.addPermanentWidget(self._progress)

        # Activer le premier onglet visuellement
        self._switch_screen(0)

    # ── Barre supérieure principale (Top Bar) ────────────────
    def _make_toolbar(self) -> QToolBar:
        tb = QToolBar("Main Navigation Toolbar")
        tb.setMovable(False)
        tb.setIconSize(QSize(22, 22))
        tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        # Logo / Titre
        app_lbl = QLabel("🖥️  Parc IT & Télécom")
        app_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        app_lbl.setStyleSheet("color: white; padding: 0 10px;")
        tb.addWidget(app_lbl)

        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setStyleSheet("color: rgba(255, 255, 255, 0.3); margin: 0 6px;")
        tb.addWidget(sep1)

        # ── Boutons de Navigation (Top Bar Screens) ──
        self._btn_nav_parc = QPushButton("📋  Affectations Parc")
        self._btn_nav_parc.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_nav_parc.clicked.connect(lambda: self._switch_screen(0))
        tb.addWidget(self._btn_nav_parc)

        self._btn_nav_stock = QPushButton("💻  Stock Laptops")
        self._btn_nav_stock.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_nav_stock.clicked.connect(lambda: self._switch_screen(1))
        tb.addWidget(self._btn_nav_stock)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tb.addWidget(spacer)

        # ── Badge Utilisateur connecté ──
        self._lbl_user_badge = QLabel()
        self._lbl_user_badge.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                background-color: rgba(0, 0, 0, 0.28);
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 12px;
                padding: 4px 12px;
                font-weight: 600;
                font-size: 12px;
                margin-right: 8px;
            }
        """)
        tb.addWidget(self._lbl_user_badge)

        # ── Bouton Gestion Utilisateurs (Admin uniquement) ──
        self._btn_manage_users = QPushButton("👥  Utilisateurs")
        self._btn_manage_users.setObjectName("btn_manage_users")
        self._btn_manage_users.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_manage_users.setStyleSheet("""
            QPushButton#btn_manage_users {
                background-color: #8E44AD;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 12px;
                font-weight: 700;
                margin-right: 6px;
            }
            QPushButton#btn_manage_users:hover {
                background-color: #7D3C98;
            }
        """)
        self._btn_manage_users.clicked.connect(self._ctrl.on_manage_users)
        tb.addWidget(self._btn_manage_users)

        # ── Bouton Déconnexion ──
        self._btn_logout = QPushButton("🔒  Déconnexion")
        self._btn_logout.setObjectName("btn_logout")
        self._btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_logout.setStyleSheet("""
            QPushButton#btn_logout {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.4);
                border-radius: 5px;
                padding: 5px 12px;
                font-weight: 600;
                margin-right: 8px;
            }
            QPushButton#btn_logout:hover {
                background-color: #C0392B;
                border-color: #C0392B;
            }
        """)
        self._btn_logout.clicked.connect(self._on_logout)
        tb.addWidget(self._btn_logout)

        # ── Horloge ──
        self._clock_lbl = QLabel()
        self._clock_lbl.setStyleSheet(
            "color: #AED6F1; font-size: 12px; padding-right: 12px;"
        )
        tb.addWidget(self._clock_lbl)
        clock = QTimer(self)
        clock.timeout.connect(self._tick_clock)
        clock.start(1000)
        self._tick_clock()

        return tb

    # ── Commutation d'écran via la Top Bar ────────────────────
    def _switch_screen(self, index: int) -> None:
        self._stacked.setCurrentIndex(index)

        # Styles des boutons de navigation actifs / inactifs
        style_active = """
            QPushButton {
                background-color: #FFFFFF;
                color: #1A3A5C;
                font-weight: 700;
                font-size: 12px;
                padding: 6px 14px;
                border-radius: 6px;
                border: 1px solid white;
            }
        """
        style_inactive = """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                color: #FFFFFF;
                font-weight: 600;
                font-size: 12px;
                padding: 6px 14px;
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 0.25);
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """

        if index == 0:
            self._btn_nav_parc.setStyleSheet(style_active)
            self._btn_nav_stock.setStyleSheet(style_inactive)
            self._lbl_count.setVisible(True)
        else:
            self._btn_nav_parc.setStyleSheet(style_inactive)
            self._btn_nav_stock.setStyleSheet(style_active)
            self._lbl_count.setVisible(False)
            self._stock_screen._ctrl.refresh()

    # ── Construction de l'écran 1 (Affectations Parc) ─────────
    def _build_parc_screen(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        layout.addLayout(self._make_ctrl_bar())
        layout.addWidget(self._make_table())
        layout.addLayout(self._make_pagination_bar())

        return widget

    def _make_ctrl_bar(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)

        self._combo_col = QComboBox()
        self._combo_col.addItem("Toutes colonnes")
        for _, label in COLUMNS:
            self._combo_col.addItem(label)
        row.addWidget(self._combo_col)

        self._search = QLineEdit()
        self._search.setObjectName("search_bar")
        self._search.setPlaceholderText("🔍  Rechercher dans les affectations…")
        self._search.textChanged.connect(self._on_search_changed)
        self._combo_col.currentTextChanged.connect(lambda _: self._on_search_changed())
        row.addWidget(self._search)

        row.addStretch()

        self._btn_add = QPushButton("➕  Ajouter")
        self._btn_add.setObjectName("btn_add")
        self._btn_add.setShortcut(QKeySequence("Ctrl+N"))
        self._btn_add.clicked.connect(self._on_add)
        row.addWidget(self._btn_add)

        self._btn_edit = QPushButton("✏  Modifier")
        self._btn_edit.setObjectName("btn_edit")
        self._btn_edit.setShortcut(QKeySequence("Ctrl+E"))
        self._btn_edit.clicked.connect(self._on_edit)
        row.addWidget(self._btn_edit)

        self._btn_del = QPushButton("🗑  Supprimer")
        self._btn_del.setObjectName("btn_del")
        self._btn_del.setShortcut(QKeySequence("Delete"))
        self._btn_del.clicked.connect(self._on_delete)
        row.addWidget(self._btn_del)

        self._btn_export = QPushButton("📤  Exporter CSV")
        self._btn_export.setObjectName("btn_export")
        self._btn_export.setShortcut(QKeySequence("Ctrl+S"))
        self._btn_export.clicked.connect(self._on_export)
        row.addWidget(self._btn_export)

        return row

    def _make_table(self) -> QTableWidget:
        self._table = QTableWidget()
        self._table.setColumnCount(len(COLUMNS))
        self._table.setHorizontalHeaderLabels([lbl for _, lbl in COLUMNS])
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setDefaultSectionSize(34)
        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        hdr.setStretchLastSection(True)
        self._table.setSortingEnabled(True)
        self._table.doubleClicked.connect(self._on_table_double_clicked)
        return self._table

    def _make_pagination_bar(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)

        self._btn_prev = QPushButton("◀  Précédent")
        self._btn_prev.setObjectName("btn_prev")
        self._btn_prev.clicked.connect(self._ctrl.on_prev_page)

        self._lbl_page = QLabel("Page 1 / 1")
        self._lbl_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_page.setMinimumWidth(130)

        self._btn_next = QPushButton("Suivant  ▶")
        self._btn_next.setObjectName("btn_next")
        self._btn_next.clicked.connect(lambda: self._ctrl.on_next_page(self._total_pages))

        row.addStretch()
        row.addWidget(self._btn_prev)
        row.addWidget(self._lbl_page)
        row.addWidget(self._btn_next)
        row.addStretch()
        return row

    # ══════════════════════════════════════════════════════════
    #  Role-Based Access Control (RBAC)
    # ══════════════════════════════════════════════════════════
    def set_current_user(self, user: dict) -> None:
        """Met à jour l'utilisateur actif et réapplique les droits sur tous les écrans."""
        self.current_user = user
        self._apply_permissions()
        if hasattr(self, "_stock_screen"):
            self._stock_screen.set_current_user(user)

    def _apply_permissions(self) -> None:
        """Adapte les boutons et accès selon le rôle de l'utilisateur."""
        role_key = self.current_user.get("role", "LECTEUR")
        perms = ROLES.get(role_key, ROLES["LECTEUR"])

        username = self.current_user.get("username", "Anonyme")
        fullname = self.current_user.get("full_name") or username
        role_label = perms["label"]

        # Mise à jour du badge utilisateur dans la barre d'outils
        self._lbl_user_badge.setText(f"👤  {fullname}  •  {role_label}")

        # Statut dans la status bar
        self._lbl_status_user.setText(f"  Connecté en tant que : <b>{username}</b> ({role_label})  |  ")

        # Permissions sur les boutons de l'écran Parc
        self._btn_add.setVisible(perms["can_add"])
        self._btn_edit.setVisible(perms["can_edit"])
        self._btn_del.setVisible(perms["can_delete"])
        self._btn_export.setVisible(perms["can_export"])
        self._btn_manage_users.setVisible(perms["can_manage_users"])

    # ══════════════════════════════════════════════════════════
    #  Interface publique pour le contrôleur
    # ══════════════════════════════════════════════════════════
    def populate_table(self, rows: list[dict]) -> None:
        keys = [key for key, _ in COLUMNS]
        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, key in enumerate(keys):
                item = QTableWidgetItem(str(row.get(key) or ""))
                self._table.setItem(r, c, item)
            self._table.item(r, 0).setData(
                Qt.ItemDataRole.UserRole, row.get("id")
            )
        self._table.setSortingEnabled(True)

    def update_pagination(self, page: int, total_pages: int, total: int) -> None:
        self._total_pages = total_pages
        shown = self._table.rowCount()
        self._lbl_page.setText(f"Page {page} / {total_pages}")
        self._btn_prev.setEnabled(page > 1)
        self._btn_next.setEnabled(page < total_pages)
        self._lbl_count.setText(
            f"  {shown} affiché(s) / {total} enregistrement(s) total  "
        )
        self._status_bar.showMessage(
            f"Dernière mise à jour : {datetime.now().strftime('%H:%M:%S')} "
            f"  —  Page {page}/{total_pages}"
        )

    def set_loading(self, loading: bool) -> None:
        self._progress.setVisible(loading)

    def show_status(self, msg: str, timeout: int = 0) -> None:
        self._status_bar.showMessage(msg, timeout)

    # ══════════════════════════════════════════════════════════
    #  Slots internes
    # ══════════════════════════════════════════════════════════
    def _tick_clock(self) -> None:
        self._clock_lbl.setText(datetime.now().strftime("%d/%m/%Y  %H:%M:%S"))

    def _on_search_changed(self) -> None:
        if not hasattr(self, "_search_timer"):
            self._search_timer = QTimer(self)
            self._search_timer.setSingleShot(True)
            self._search_timer.timeout.connect(self._do_search)
        self._search_timer.start(300)

    def _do_search(self) -> None:
        self._ctrl.load_page(
            page=1,
            search=self._search.text().strip(),
            column=self._combo_col.currentText(),
        )

    def _on_add(self) -> None:
        self._ctrl.on_add()

    def _on_edit(self) -> None:
        row_id, row_data = self._selected_row()
        self._ctrl.on_edit(row_id, row_data)

    def _on_table_double_clicked(self) -> None:
        role = self.current_user.get("role", "LECTEUR")
        if ROLES.get(role, {}).get("can_edit", False):
            self._on_edit()

    def _on_delete(self) -> None:
        row_id, row_data = self._selected_row()
        nom = row_data.get("nom_prenom", "")
        self._ctrl.on_delete(row_id, nom)

    def _on_export(self) -> None:
        self._ctrl.on_export()

    def _on_logout(self) -> None:
        reply = QMessageBox.question(
            self,
            "Déconnexion",
            "Voulez-vous vraiment vous déconnecter de votre session ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from views.dialogs.login_dialog import LoginDialog
            login_dlg = LoginDialog(self)
            if login_dlg.exec():
                new_user = login_dlg.authenticated_user
                self.set_current_user(new_user)
                self._ctrl.reload()
                self.show_status(f"Bienvenue, {new_user.get('full_name') or new_user.get('username')}.", 3000)

    def _selected_row(self) -> tuple[int | None, dict]:
        r = self._table.currentRow()
        if r < 0:
            return None, {}
        keys = [key for key, _ in COLUMNS]
        row_id = self._table.item(r, 0).data(Qt.ItemDataRole.UserRole) \
                 if self._table.item(r, 0) else None
        data = {
            key: (self._table.item(r, c).text() if self._table.item(r, c) else "")
            for c, key in enumerate(keys)
        }
        return row_id, data

    def closeEvent(self, event) -> None:
        from database.backup import backup_database
        try:
            path = backup_database()
            logger.info("Close-time backup: %s", path)
        except Exception as exc:
            logger.warning("Close-time backup failed: %s", exc)
        super().closeEvent(event)
