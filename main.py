"""
main.py — Application entry point
──────────────────────────────────
Sets up:
  • Structured logging (file + console)
  • SQLite WAL database initialization (parc & users tables)
  • Default administrator account creation (admin / admin)
  • QApplication + global stylesheet
  • Authentication via LoginDialog before launching MainWindow
  • MainWindow (MVC orchestrator with RBAC permissions)
  • Global exception hook so uncaught errors are written to app.log
"""

import sys
import logging
import traceback

from PyQt6.QtWidgets import QApplication, QMessageBox  # type: ignore[import-not-found]

from config import APP_NAME, APP_VERSION, LOG_FILE
from database.connection import init_db
from styles.style import STYLE
from views.dialogs.login_dialog import LoginDialog
from views.main_window import MainWindow


# ── Logging setup ─────────────────────────────────────────────
def _configure_logging() -> None:
    """Send INFO+ to app.log and WARNING+ to the console."""
    fmt = logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh = logging.FileHandler(str(LOG_FILE), encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)

    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(fh)
    root.addHandler(ch)


# ── Global exception hook ─────────────────────────────────────
def _excepthook(exc_type, exc_value, exc_tb) -> None:
    """Log every unhandled exception to app.log then show a dialog."""
    msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logging.critical("Uncaught exception:\n%s", msg)
    if QApplication.instance():
        QMessageBox.critical(
            None,
            "Erreur inattendue",
            f"Une erreur critique s'est produite.\n\n{exc_value}\n\n"
            f"Détails écrits dans :\n{LOG_FILE}",
        )


# ── Entry point ───────────────────────────────────────────────
def main() -> None:
    _configure_logging()
    sys.excepthook = _excepthook

    logger = logging.getLogger(__name__)
    logger.info("═══ %s v%s starting ═══", APP_NAME, APP_VERSION)

    # Initialise DB (WAL mode + tables + indexes + default admin)
    try:
        init_db()
    except Exception as exc:
        print(f"[FATAL] Database init failed: {exc}", file=sys.stderr)
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setStyleSheet(STYLE)

    # ── Écran de connexion (Login Dialog) ──
    login_dlg = LoginDialog()
    if login_dlg.exec() != LoginDialog.DialogCode.Accepted:
        logger.info("Login cancelled by user. Exiting.")
        sys.exit(0)

    current_user = login_dlg.authenticated_user
    logger.info(
        "User logged in: %s (Role: %s)",
        current_user["username"],
        current_user["role"],
    )

    # ── Lancement de la fenêtre principale avec le profil utilisateur ──
    window = MainWindow(current_user=current_user)
    window.show()

    exit_code = app.exec()
    logger.info("Application exited with code %d.", exit_code)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
