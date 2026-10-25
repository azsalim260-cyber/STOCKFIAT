"""
controllers/parc_controller.py  —  CONTROLLER layer (MVC)
──────────────────────────────────────────────────────────
Mediates between ParcModel (data) and MainWindow (view).
All business logic lives here; neither Model nor View
should know about the other.
Contrôle des permissions selon le rôle de l'utilisateur connecté.
"""

import logging
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import QMessageBox, QFileDialog

from models.parc_model import ParcModel
from models.user_model import ROLES
from workers.db_worker import FetchWorker, ExportWorker
from config import COLUMNS, PAGE_SIZE

logger = logging.getLogger(__name__)


class ParcController:
    def __init__(self, view) -> None:
        self._model          = ParcModel()
        self._view           = view
        self._fetch_worker: FetchWorker | None  = None
        self._export_worker: ExportWorker | None = None

        # Current pagination / filter state
        self._page   = 1
        self._search = ""
        self._column = "Toutes colonnes"

    # ── Permission check helper ───────────────────────────────
    def _can(self, permission_key: str) -> bool:
        user = getattr(self._view, "current_user", None) or {}
        role = user.get("role", "LECTEUR")
        return ROLES.get(role, {}).get(permission_key, False)

    # ── Data loading (non-blocking via QThread) ───────────────
    def load_page(
        self,
        page: int = 1,
        search: str = "",
        column: str = "Toutes colonnes",
    ) -> None:
        """Kick off a background FetchWorker for the requested page."""
        self._page   = page
        self._search = search
        self._column = column

        # Cancel any in-flight fetch
        if self._fetch_worker and self._fetch_worker.isRunning():
            self._fetch_worker.quit()
            self._fetch_worker.wait()

        worker = FetchWorker(self._model, page, search, column)
        worker.results_ready.connect(self._on_data_ready)
        worker.error.connect(self._on_fetch_error)
        self._fetch_worker = worker

        self._view.set_loading(True)
        worker.start()

    def reload(self) -> None:
        """Reload current page with current filter (convenience method)."""
        self.load_page(self._page, self._search, self._column)

    # ── Slots wired to FetchWorker signals ────────────────────
    def _on_data_ready(self, rows: list, total: int) -> None:
        self._view.set_loading(False)
        self._view.populate_table(rows)
        total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        self._view.update_pagination(self._page, total_pages, total)

    def _on_fetch_error(self, msg: str) -> None:
        self._view.set_loading(False)
        QMessageBox.critical(self._view, "Erreur base de données", msg)

    # ── CRUD actions (called by MainWindow buttons) ───────────
    def on_add(self) -> None:
        if not self._can("can_add"):
            QMessageBox.warning(
                self._view, "Permission refusée",
                "Votre rôle ne vous autorise pas à ajouter des équipements."
            )
            return

        from views.dialogs.record_dialog import RecordDialog
        dlg = RecordDialog(self._view)
        if dlg.exec():
            try:
                self._model.insert(dlg.get_data())
                self.reload()
                self._view.show_status("✔  Enregistrement ajouté avec succès.", 3000)
            except Exception as exc:
                logger.error("on_add: %s", exc)
                QMessageBox.critical(self._view, "Erreur ajout", str(exc))

    def on_edit(self, row_id: int, current_data: dict) -> None:
        if not self._can("can_edit"):
            QMessageBox.information(
                self._view, "Mode consultation",
                "Votre compte est en lecture seule. Vous ne pouvez pas modifier les données."
            )
            return

        if row_id is None:
            QMessageBox.information(
                self._view, "Sélection", "Veuillez sélectionner une ligne à modifier."
            )
            return

        from views.dialogs.record_dialog import RecordDialog
        dlg = RecordDialog(self._view, current_data)
        if dlg.exec():
            try:
                self._model.update(row_id, dlg.get_data())
                self.reload()
                self._view.show_status("✔  Enregistrement modifié avec succès.", 3000)
            except Exception as exc:
                logger.error("on_edit(id=%s): %s", row_id, exc)
                QMessageBox.critical(self._view, "Erreur modification", str(exc))

    def on_delete(self, row_id: int, nom: str) -> None:
        if not self._can("can_delete"):
            QMessageBox.warning(
                self._view, "Permission refusée",
                "Seul un administrateur peut supprimer un équipement."
            )
            return

        if row_id is None:
            QMessageBox.information(
                self._view, "Sélection", "Veuillez sélectionner une ligne à supprimer."
            )
            return

        reply = QMessageBox.question(
            self._view,
            "Confirmation",
            f"Supprimer l'enregistrement de  « {nom} »  ?\n"
            "Cette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self._model.delete(row_id)
                self.reload()
                self._view.show_status("✔  Enregistrement supprimé.", 3000)
            except Exception as exc:
                logger.error("on_delete(id=%s): %s", row_id, exc)
                QMessageBox.critical(self._view, "Erreur suppression", str(exc))

    # ── User management (Admin only) ──────────────────────────
    def on_manage_users(self) -> None:
        if not self._can("can_manage_users"):
            QMessageBox.warning(
                self._view, "Permission refusée",
                "Seul un administrateur peut gérer les comptes utilisateurs."
            )
            return

        from views.dialogs.user_manager_dialog import UserManagerDialog
        dlg = UserManagerDialog(self._view, current_user=self._view.current_user)
        dlg.exec()

    # ── CSV export (non-blocking via ExportWorker) ────────────
    def on_export(self) -> None:
        dest, _ = QFileDialog.getSaveFileName(
            self._view,
            "Exporter en CSV",
            str(
                Path.home()
                / f"parc_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            ),
            "CSV Files (*.csv)",
        )
        if not dest:
            return

        worker = ExportWorker(self._model, dest, COLUMNS)
        worker.finished.connect(self._on_export_done)
        worker.error.connect(self._on_export_error)
        worker.progress.connect(
            lambda cur, tot: self._view.show_status(
                f"Export en cours… {cur}/{tot} lignes", 0
            )
        )
        self._export_worker = worker
        self._view.set_loading(True)
        worker.start()

    def _on_export_done(self, path: str) -> None:
        self._view.set_loading(False)
        QMessageBox.information(
            self._view, "Export réussi", f"✔  Fichier exporté avec succès :\n{path}"
        )

    def _on_export_error(self, msg: str) -> None:
        self._view.set_loading(False)
        QMessageBox.critical(self._view, "Erreur export CSV", msg)

    # ── Pagination helpers ────────────────────────────────────
    def on_prev_page(self) -> None:
        if self._page > 1:
            self.load_page(self._page - 1, self._search, self._column)

    def on_next_page(self, total_pages: int) -> None:
        if self._page < total_pages:
            self.load_page(self._page + 1, self._search, self._column)
