"""
workers/db_worker.py
────────────────────
QThread-based background workers so the UI never freezes.

Pattern
───────
  1. Instantiate a worker with the data it needs.
  2. Connect its pyqtSignal(s) to GUI slots.
  3. Call worker.start()  — the heavy work runs in a separate OS thread.
  4. When done the signal fires → GUI slot runs safely in the main thread.

Workers provided
────────────────
  FetchWorker  – paginated SELECT + total count
  ExportWorker – full table dump for CSV export
"""

import csv
import logging
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

logger = logging.getLogger(__name__)


# ── Paginated fetch ───────────────────────────────────────────
class FetchWorker(QThread):
    """
    Signals
    -------
    results_ready(rows: list[dict], total: int)
        Emitted when both the page and the count query succeed.
    error(message: str)
        Emitted if any exception occurs; the UI should surface it.
    """

    results_ready: pyqtSignal = pyqtSignal(list, int)
    error:         pyqtSignal = pyqtSignal(str)

    def __init__(self, model, page: int, search: str, column: str, parent=None):
        super().__init__(parent)
        self._model  = model
        self._page   = page
        self._search = search
        self._column = column

    def run(self) -> None:           # Executes in the background thread
        try:
            rows  = self._model.fetch_page(self._page, self._search, self._column)
            total = self._model.count(self._search, self._column)
            self.results_ready.emit(rows, total)   # ← safe cross-thread emit
        except Exception as exc:
            logger.error("FetchWorker error: %s", exc)
            self.error.emit(str(exc))


# ── CSV export ────────────────────────────────────────────────
class ExportWorker(QThread):
    """
    Signals
    -------
    finished(path: str)      – export written successfully
    error(message: str)      – something went wrong
    progress(current, total) – optional progress updates
    """

    finished: pyqtSignal = pyqtSignal(str)
    error:    pyqtSignal = pyqtSignal(str)
    progress: pyqtSignal = pyqtSignal(int, int)

    def __init__(self, model, dest_path: str, columns: list, parent=None):
        super().__init__(parent)
        self._model     = model
        self._dest_path = dest_path
        self._columns   = columns   # [(key, label), ...]

    def run(self) -> None:
        try:
            rows = self._model.fetch_all()
            total = len(rows)
            with open(self._dest_path, "w", newline="", encoding="utf-8-sig") as fh:
                writer = csv.writer(fh, delimiter=";")
                writer.writerow([label for _, label in self._columns])
                for i, row in enumerate(rows, 1):
                    writer.writerow(
                        [row.get(key, "") or "" for key, _ in self._columns]
                    )
                    if i % 500 == 0:
                        self.progress.emit(i, total)
            self.progress.emit(total, total)
            self.finished.emit(self._dest_path)
        except Exception as exc:
            logger.error("ExportWorker error: %s", exc)
            self.error.emit(str(exc))

