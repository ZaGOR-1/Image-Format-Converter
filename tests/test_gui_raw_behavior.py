"""GUI RAW behavior tests for lazy rawpy handling."""

from __future__ import annotations

import builtins
import importlib
import os
from pathlib import Path
import sys

import pytest
from PIL import Image

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app.core.conversion_options import ConversionOptions
from app.core.conversion_service import ConversionService
from app.core.job_result import JobResult
from app.gui.conversion_worker import ConversionWorker


def _qt_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def hide_rawpy(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make rawpy unavailable even if it is installed in the test environment."""
    original_import = builtins.__import__

    def import_without_rawpy(name: str, *args: object, **kwargs: object):
        if name == "rawpy":
            raise ImportError("rawpy intentionally hidden")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", import_without_rawpy)


def test_gui_entry_import_does_not_require_rawpy(hide_rawpy: None) -> None:
    for module_name in [
        "app.gui_main",
        "app.gui.main_window",
        "app.gui.conversion_worker",
        "app.core.conversion_service",
        "app.converters.registry",
        "app.converters.raw_converter",
    ]:
        sys.modules.pop(module_name, None)

    imported = importlib.import_module("app.gui_main")

    assert callable(imported.main)


def test_gui_worker_regular_conversion_works_without_rawpy(
    tmp_path: Path,
    hide_rawpy: None,
) -> None:
    _qt_app()
    input_path = tmp_path / "source.png"
    output_dir = tmp_path / "out"
    Image.new("RGBA", (8, 8), (10, 20, 30, 128)).save(input_path)
    options = ConversionOptions(
        input_path=input_path,
        output_dir=output_dir,
        target_format="jpg",
    )
    worker = ConversionWorker(ConversionService(), options)
    messages: list[str] = []
    finished: list[JobResult] = []
    failures: list[str] = []
    worker.log_message.connect(messages.append)
    worker.finished.connect(finished.append)
    worker.failed.connect(failures.append)

    worker.run()

    assert failures == []
    assert len(finished) == 1
    assert finished[0].converted == 1
    assert finished[0].failed == 0
    assert (output_dir / "source.jpg").exists()
    assert any("Converted 1/1: source.png" in message for message in messages)


def test_gui_worker_raw_without_rawpy_logs_clear_failure(
    tmp_path: Path,
    hide_rawpy: None,
) -> None:
    _qt_app()
    input_path = tmp_path / "photo.nef"
    output_dir = tmp_path / "out"
    input_path.write_bytes(b"not a real raw file")
    options = ConversionOptions(
        input_path=input_path,
        output_dir=output_dir,
        target_format="jpg",
    )
    worker = ConversionWorker(ConversionService(), options)
    messages: list[str] = []
    finished: list[JobResult] = []
    failures: list[str] = []
    worker.log_message.connect(messages.append)
    worker.finished.connect(finished.append)
    worker.failed.connect(failures.append)

    worker.run()

    assert failures == []
    assert len(finished) == 1
    assert finished[0].converted == 0
    assert finished[0].failed == 1
    assert "RAW conversion requires rawpy" in finished[0].errors[0].reason
    assert any("Failed 1/1: photo.nef" in message for message in messages)
    assert any("RAW conversion requires rawpy" in message for message in messages)
