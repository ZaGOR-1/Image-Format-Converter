"""Background conversion worker for the PySide6 GUI."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from app.core.conversion_options import ConversionOptions
from app.core.conversion_service import ConversionService


class ConversionWorker(QObject):
    """Run ConversionService in a QObject suitable for QThread."""

    progress_changed = Signal(int, int, str)
    log_message = Signal(str)
    finished = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        service: ConversionService,
        options: ConversionOptions,
    ) -> None:
        super().__init__()
        self.service = service
        self.options = options

    @Slot()
    def run(self) -> None:
        """Run conversion and emit result signals."""
        try:
            result = self.service.run(
                self.options,
                on_progress=self._on_progress,
                on_log=self._on_log,
            )
        except Exception as exc:  # noqa: BLE001 - protect the GUI thread boundary.
            self.failed.emit(str(exc))
            return

        self.finished.emit(result)

    def _on_progress(self, current: int, total: int, path: Path) -> None:
        self.progress_changed.emit(current, total, str(path))

    def _on_log(self, message: str) -> None:
        self.log_message.emit(message)
