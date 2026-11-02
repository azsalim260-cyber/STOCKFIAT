"""
views/dialogs/login_dialog.py — Formulaire de connexion (Login Dialog)
────────────────────────────────────────────────────────────────────
Fenêtre de connexion au démarrage :
  • Authentification sécurisée via UserModel (PBKDF2-HMAC-SHA256)
  • Compte administrateur par défaut : admin / admin pré-rempli pour accès immédiat
  • Gestion des erreurs claire et ergonomique
  • Support de la touche Entrée pour soumettre le formulaire
"""

from PyQt6.QtWidgets import (  # type: ignore[import-not-found]
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt  # type: ignore[import-not-found]
from PyQt6.QtGui import QFont, QColor, QIcon, QKeySequence  # type: ignore[import-not-found]

from models.user_model import UserModel


class LoginDialog(QDialog):
    """
    Dialogue modal de connexion.
    Une fois accepté (exec() == Accepted), l'utilisateur connecté est
    accessible via l'attribut `authenticated_user`.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_model = UserModel()
        self.authenticated_user: dict | None = None

        self.setWindowTitle("Connexion — Gestionnaire de Parc IT")
        self.setFixedSize(430, 480)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self._build_ui()

    def _build_ui() -> None:
        pass  # will be overridden by instance method

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(36, 28, 36, 28)

        # ── En-tête / Logo ──
        lbl_logo = QLabel("🖥️")
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo.setStyleSheet("font-size: 44px; margin-bottom: 2px;")
        layout.addWidget(lbl_logo)

        lbl_title = QLabel("Gestionnaire de Parc IT")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #1A3A5C; font-weight: 700;")
        layout.addWidget(lbl_title)

        lbl_sub = QLabel("Veuillez vous authentifier pour continuer")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sub.setFont(QFont("Segoe UI", 10))
        lbl_sub.setStyleSheet("color: #7F8C8D; margin-bottom: 4px;")
        layout.addWidget(lbl_sub)

        # Séparateur décoratif
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #D5D8DC; margin-bottom: 8px;")
        layout.addWidget(sep)

        # ── Message d'erreur dynamique ──
        self._lbl_error = QLabel()
        self._lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_error.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._lbl_error.setStyleSheet("color: #C0392B; padding: 4px; border-radius: 4px; background-color: #FDEDEC;")
        self._lbl_error.setVisible(False)
        layout.addWidget(self._lbl_error)

        # ── Champ Identifiant ──
        lbl_user = QLabel("Identifiant utilisateur :")
        lbl_user.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl_user.setStyleSheet("color: #2C3E50;")
        layout.addWidget(lbl_user)

        self._inp_username = QLineEdit("admin")
        self._inp_username.setPlaceholderText("Ex: admin")
        self._inp_username.setObjectName("login_input")
        self._inp_username.setStyleSheet("""
            QLineEdit#login_input {
                border: 1.5px solid #BDC3C7;
                border-radius: 6px;
                padding: 9px 12px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit#login_input:focus {
                border-color: #2E86C1;
            }
        """)
        self._inp_username.textChanged.connect(self._clear_error)
        layout.addWidget(self._inp_username)

        # ── Champ Mot de passe ──
        lbl_pwd = QLabel("Mot de passe :")
        lbl_pwd.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl_pwd.setStyleSheet("color: #2C3E50;")
        layout.addWidget(lbl_pwd)

        self._inp_password = QLineEdit("admin")
        self._inp_password.setEchoMode(QLineEdit.EchoMode.Password)
        self._inp_password.setPlaceholderText("••••••••")
        self._inp_password.setObjectName("login_pwd")
        self._inp_password.setStyleSheet("""
            QLineEdit#login_pwd {
                border: 1.5px solid #BDC3C7;
                border-radius: 6px;
                padding: 9px 12px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit#login_pwd:focus {
                border-color: #2E86C1;
            }
        """)
        self._inp_password.textChanged.connect(self._clear_error)
        self._inp_password.returnPressed.connect(self._handle_login)
        layout.addWidget(self._inp_password)

        # Indication du compte par défaut
        lbl_hint = QLabel("💡 Compte par défaut : <b>admin</b> / <b>admin</b>")
        lbl_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_hint.setStyleSheet("color: #5D6D7E; font-size: 11px; margin-top: 2px;")
        layout.addWidget(lbl_hint)

        # ── Boutons d'action ──
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.setContentsMargins(0, 10, 0, 0)

        self._btn_quit = QPushButton("Quitter")
        self._btn_quit.setFixedHeight(38)
        self._btn_quit.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_quit.setStyleSheet("""
            QPushButton {
                background-color: #E2E8F0;
                color: #4A5568;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #CBD5E0;
            }
        """)
        self._btn_quit.clicked.connect(self.reject)
        btn_layout.addWidget(self._btn_quit)

        self._btn_login = QPushButton("Se connecter")
        self._btn_login.setFixedHeight(38)
        self._btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_login.setDefault(True)
        self._btn_login.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #1A5276, stop:1 #2E86C1);
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #154360, stop:1 #2471A3);
            }
            QPushButton:pressed {
                background-color: #1A5276;
            }
        """)
        self._btn_login.clicked.connect(self._handle_login)
        btn_layout.addWidget(self._btn_login)

        layout.addLayout(btn_layout)

        # Focus initial sur le bouton se connecter ou mot de passe
        self._btn_login.setFocus()

    def _clear_error(self) -> None:
        if self._lbl_error.isVisible():
            self._lbl_error.setVisible(False)

    def _show_error(self, message: str) -> None:
        self._lbl_error.setText(f"⚠️  {message}")
        self._lbl_error.setVisible(True)

    def _handle_login(self) -> None:
        username = self._inp_username.text().strip()
        password = self._inp_password.text()

        if not username:
            self._show_error("Veuillez saisir votre identifiant.")
            self._inp_username.setFocus()
            return

        if not password:
            self._show_error("Veuillez saisir votre mot de passe.")
            self._inp_password.setFocus()
            return

        try:
            user = self.user_model.authenticate(username, password)
            if user:
                self.authenticated_user = user
                self.accept()
            else:
                self._show_error("Identifiant ou mot de passe incorrect.")
                self._inp_password.clear()
                self._inp_password.setFocus()
        except Exception as exc:
            self._show_error(f"Erreur de connexion : {exc}")
