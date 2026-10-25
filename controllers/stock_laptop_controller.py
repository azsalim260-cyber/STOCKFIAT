"""
controllers/stock_laptop_controller.py — CONTROLLER layer for Stock Laptops
───────────────────────────────────────────────────────────────────────────
Gère la logique métier du stock des laptops :
  • Chargement des données avec filtres (recherche par FAN et filtre par licence)
  • Ajout, modification, suppression avec contrôle des droits (RBAC)
  • Validation de la condition d'unicité du NUM FAN
  • Impression / Exportation vers fichier Excel (.xlsx / .xls / .csv)
"""

import logging
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import QMessageBox, QFileDialog

from models.stock_laptop_model import StockLaptopModel
from models.user_model import ROLES
from utils.excel_exporter import export_stock_to_excel

logger = logging.getLogger(__name__)


class StockLaptopController:
    """Contrôleur pour l'écran de gestion du stock de laptops."""

    def __init__(self, view) -> None:
        self._model = StockLaptopModel()
        self._view = view

    # ── Permission check helper ───────────────────────────────
    def _can(self, permission_key: str) -> bool:
        user = getattr(self._view, "current_user", None) or {}
        role = user.get("role", "LECTEUR")
        return ROLES.get(role, {}).get(permission_key, False)

    # ── Chargement des données ────────────────────────────────
    def refresh(self) -> None:
        """Charge et filtre les données du stock selon les critères de l'UI."""
        search_fan = self._view.get_search_fan()
        filter_license = self._view.get_filter_license()

        try:
            rows = self._model.fetch_all(search_fan, filter_license)
            stats = self._model.get_stats()
            self._view.populate_table(rows)
            self._view.update_stats(stats, count_shown=len(rows))
        except Exception as exc:
            logger.error("Stock refresh error: %s", exc)
            QMessageBox.critical(self._view, "Erreur base de données", str(exc))

    # ── Ajouter un laptop ─────────────────────────────────────
    def on_add(self) -> None:
        if not self._can("can_add"):
            QMessageBox.warning(
                self._view, "Permission refusée",
                "Votre compte ne dispose pas des droits nécessaires pour ajouter des équipements."
            )
            return

        from views.dialogs.stock_laptop_dialog import StockLaptopDialog
        dlg = StockLaptopDialog(self._view)
        if dlg.exec():
            data = dlg.get_data()
            try:
                self._model.insert(
                    fan=data["fan"],
                    serial=data["serial"],
                    model=data["model"],
                    quantite=data["quantite"],
                    license=data["license"],
                )
                self.refresh()
                QMessageBox.information(
                    self._view, "Succès",
                    f"✔ Le laptop « {data['fan']} » a été ajouté au stock avec succès."
                )
            except Exception as exc:
                logger.error("Add laptop error: %s", exc)
                QMessageBox.critical(self._view, "Erreur d'ajout", str(exc))

    # ── Modifier un laptop ────────────────────────────────────
    def on_edit(self, item_id: int, current_data: dict) -> None:
        if not self._can("can_edit"):
            QMessageBox.information(
                self._view, "Mode consultation",
                "Votre compte est en lecture seule. Vous ne pouvez pas modifier cet équipement."
            )
            return

        if not item_id:
            QMessageBox.warning(self._view, "Sélection", "Veuillez sélectionner un laptop à modifier.")
            return

        from views.dialogs.stock_laptop_dialog import StockLaptopDialog
        dlg = StockLaptopDialog(self._view, data=current_data)
        if dlg.exec():
            data = dlg.get_data()
            try:
                self._model.update(
                    item_id=item_id,
                    fan=data["fan"],
                    serial=data["serial"],
                    model=data["model"],
                    quantite=data["quantite"],
                    license=data["license"],
                )
                self.refresh()
                QMessageBox.information(
                    self._view, "Succès",
                    f"✔ Les informations du laptop « {data['fan']} » ont été mises à jour."
                )
            except Exception as exc:
                logger.error("Update laptop error: %s", exc)
                QMessageBox.critical(self._view, "Erreur de modification", str(exc))

    # ── Supprimer un laptop ───────────────────────────────────
    def on_delete(self, item_id: int, fan: str) -> None:
        if not self._can("can_delete"):
            QMessageBox.warning(
                self._view, "Permission refusée",
                "Seul un administrateur peut supprimer un équipement du stock."
            )
            return

        if not item_id:
            QMessageBox.warning(self._view, "Sélection", "Veuillez sélectionner un laptop à supprimer.")
            return

        reply = QMessageBox.question(
            self._view,
            "Confirmation de suppression",
            f"Voulez-vous vraiment supprimer le laptop FAN  « {fan} »  du stock ?\n"
            "Cette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self._model.delete(item_id)
                self.refresh()
                QMessageBox.information(self._view, "Supprimé", f"Le laptop « {fan} » a été supprimé du stock.")
            except Exception as exc:
                logger.error("Delete laptop error: %s", exc)
                QMessageBox.critical(self._view, "Erreur de suppression", str(exc))

    # ── Imprimer / Exporter vers Excel ────────────────────────
    def on_print_excel(self) -> None:
        """Exporte l'intégralité du tableau de stock dans un fichier Excel."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = str(Path.home() / f"stock_laptops_{timestamp}.xlsx")

        file_path, _ = QFileDialog.getSaveFileName(
            self._view,
            "Imprimer / Exporter le stock vers Excel",
            default_filename,
            "Classeur Excel (*.xlsx);;Fichier Excel XML (*.xls);;Fichier CSV (*.csv)",
        )
        if not file_path:
            return

        try:
            # Récupérer les données filtrées actuelles
            search_fan = self._view.get_search_fan()
            filter_license = self._view.get_filter_license()
            records = self._model.fetch_all(search_fan, filter_license)

            headers = ["ID", "NUM FAN", "SERIAL", "MODEL", "QUANTITÉ", "OS LICENSE", "DATE CRÉATION"]
            rows_data = [
                [
                    r.get("id"),
                    r.get("fan"),
                    r.get("serial") or "",
                    r.get("model") or "",
                    r.get("quantite") or 1,
                    r.get("license") or "Sans licence",
                    str(r.get("created_at") or ""),
                ]
                for r in records
            ]

            export_stock_to_excel(file_path, headers, rows_data)

            QMessageBox.information(
                self._view,
                "Impression Excel réussie",
                f"✔ Le stock complet ({len(rows_data)} laptops) a été exporté avec succès dans le fichier :\n\n{file_path}\n\n"
                "Vous pouvez l'ouvrir directement dans Microsoft Excel.",
            )
        except Exception as exc:
            logger.error("Export stock to Excel error: %s", exc)
            QMessageBox.critical(self._view, "Erreur d'exportation", f"Impossible d'exporter le fichier : {exc}")

