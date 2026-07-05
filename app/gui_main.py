"""GUI entry point for Image Format Converter MVP v2."""

from __future__ import annotations

import sys
from collections.abc import Sequence

from PySide6.QtWidgets import QApplication

from app.gui.main_window import MainWindow


def main(argv: Sequence[str] | None = None) -> int:
    """Start the PySide6 GUI application."""
    app = QApplication(list(argv) if argv is not None else sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
