"""Tests for MainWindow GUI helper behavior."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

from app.core.config import (
    DEFAULT_QUALITY,
    MAX_QUALITY,
    MIN_QUALITY,
    SUPPORTED_OUTPUT_FORMATS,
)
from app.core.conversion_options import ConversionOptions
from app.core.job_result import JobResult
from app.gui import main_window as main_window_module
from app.gui.main_window import MainWindow


@pytest.fixture
def qt_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_select_input_file_updates_input_path(
    qt_app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = MainWindow()
    input_file = tmp_path / "photo.png"

    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (str(input_file), ""),
    )

    window._select_input_file()

    assert window.input_path_edit.text() == str(input_file)


def test_select_input_folder_updates_input_path(
    qt_app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = MainWindow()

    monkeypatch.setattr(
        QFileDialog,
        "getExistingDirectory",
        lambda *args, **kwargs: str(tmp_path),
    )

    window._select_input_folder()

    assert window.input_path_edit.text() == str(tmp_path)


def test_select_output_folder_updates_output_path(
    qt_app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = MainWindow()

    monkeypatch.setattr(
        QFileDialog,
        "getExistingDirectory",
        lambda *args, **kwargs: str(tmp_path),
    )

    window._select_output_folder()

    assert window.output_path_edit.text() == str(tmp_path)


def test_cancelled_file_dialog_keeps_existing_input_path(
    qt_app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = MainWindow()
    window.input_path_edit.setText("existing")
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: ("", ""),
    )

    window._select_input_file()

    assert window.input_path_edit.text() == "existing"


def test_format_combo_uses_supported_output_formats(qt_app: QApplication) -> None:
    window = MainWindow()

    combo_items = [
        window.target_format_combo.itemText(index)
        for index in range(window.target_format_combo.count())
    ]

    assert combo_items == sorted(SUPPORTED_OUTPUT_FORMATS)
    assert window.target_format_combo.currentText() == "jpg"


def test_quality_control_uses_config_defaults(qt_app: QApplication) -> None:
    window = MainWindow()

    assert window.quality_spin.minimum() == MIN_QUALITY
    assert window.quality_spin.maximum() == MAX_QUALITY
    assert window.quality_spin.value() == DEFAULT_QUALITY


def test_resize_controls_start_disabled_by_zero_value(qt_app: QApplication) -> None:
    window = MainWindow()

    assert window.resize_width_spin.minimum() == 0
    assert window.resize_width_spin.value() == 0
    assert window.resize_height_spin.minimum() == 0
    assert window.resize_height_spin.value() == 0


def test_conversion_option_checkboxes_default_to_unchecked(
    qt_app: QApplication,
) -> None:
    window = MainWindow()

    assert window.recursive_checkbox.text() == "Recursive"
    assert window.keep_structure_checkbox.text() == "Keep folder structure"
    assert window.overwrite_checkbox.text() == "Overwrite existing files"
    assert window.recursive_checkbox.isChecked() is False
    assert window.keep_structure_checkbox.isChecked() is False
    assert window.overwrite_checkbox.isChecked() is False


def test_build_conversion_options_from_window_state(
    qt_app: QApplication,
    tmp_path: Path,
) -> None:
    window = MainWindow()
    input_path = tmp_path / "input"
    output_path = tmp_path / "output"
    window.input_path_edit.setText(str(input_path))
    window.output_path_edit.setText(str(output_path))
    window.target_format_combo.setCurrentText("png")
    window.quality_spin.setValue(80)
    window.resize_width_spin.setValue(1000)
    window.resize_height_spin.setValue(0)
    window.recursive_checkbox.setChecked(True)
    window.keep_structure_checkbox.setChecked(True)
    window.overwrite_checkbox.setChecked(True)

    options = window.build_conversion_options()

    assert options == ConversionOptions(
        input_path=input_path,
        output_dir=output_path,
        target_format="png",
        quality=80,
        recursive=True,
        overwrite=True,
        keep_structure=True,
        resize_width=1000,
        resize_height=None,
    )


def test_validate_form_uses_current_window_values(
    qt_app: QApplication,
    tmp_path: Path,
) -> None:
    window = MainWindow()
    input_path = tmp_path / "source.png"
    output_dir = tmp_path / "out"
    input_path.write_bytes(b"placeholder")
    window.input_path_edit.setText(str(input_path))
    window.output_path_edit.setText(str(output_dir))
    window.target_format_combo.setCurrentText("jpg")
    window.quality_spin.setValue(92)
    window.resize_width_spin.setValue(0)
    window.resize_height_spin.setValue(0)

    assert window.validate_form() == []


def test_show_validation_warning_uses_message_box(
    qt_app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = MainWindow()
    calls: list[tuple[str, str]] = []

    def fake_warning(parent: object, title: str, message: str) -> None:
        assert parent is window
        calls.append((title, message))

    monkeypatch.setattr(QMessageBox, "warning", fake_warning)

    window.show_validation_warning(["Input path is required.", "Output required."])

    assert calls == [
        (
            "Invalid conversion options",
            "Input path is required.\nOutput required.",
        )
    ]
    assert window.convert_button.isEnabled() is True


def test_show_validation_warning_ignores_empty_errors(
    qt_app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = MainWindow()
    calls: list[str] = []
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda *args, **kwargs: calls.append("called"),
    )

    window.show_validation_warning([])

    assert calls == []


def test_start_conversion_with_validation_errors_shows_warning_only(
    qt_app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = MainWindow()
    warnings: list[tuple[str, str]] = []

    monkeypatch.setattr(
        window,
        "validate_form",
        lambda: ["Input path is required."],
    )
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda parent, title, message: warnings.append((title, message)),
    )

    window._start_conversion()

    assert warnings == [
        ("Invalid conversion options", "Input path is required."),
    ]
    assert window.convert_button.isEnabled() is True
    assert window._thread is None
    assert window._worker is None


class FakeSignal:
    def __init__(self) -> None:
        self._callbacks = []

    def connect(self, callback):
        self._callbacks.append(callback)

    def emit(self, *args):
        for callback in list(self._callbacks):
            callback(*args)


class FakeThread:
    def __init__(self, parent=None) -> None:
        self.parent = parent
        self.started = FakeSignal()
        self.finished = FakeSignal()
        self.started_flag = False
        self.deleted = False

    def start(self) -> None:
        self.started_flag = True
        self.started.emit()

    def quit(self) -> None:
        self.finished.emit()

    def deleteLater(self) -> None:
        self.deleted = True


class FakeService:
    pass


class SuccessfulFakeWorker:
    created: list["SuccessfulFakeWorker"] = []

    def __init__(self, service, options) -> None:
        self.service = service
        self.options = options
        self.progress_changed = FakeSignal()
        self.log_message = FakeSignal()
        self.finished = FakeSignal()
        self.failed = FakeSignal()
        self.moved_to_thread = None
        self.deleted = False
        SuccessfulFakeWorker.created.append(self)

    def moveToThread(self, thread) -> None:
        self.moved_to_thread = thread

    def deleteLater(self) -> None:
        self.deleted = True

    def run(self) -> None:
        self.log_message.emit("Found 1 supported file(s).")
        self.log_message.emit("Processing file 1/1: photo.png")
        self.log_message.emit("Output path: out/photo.jpg")
        self.progress_changed.emit(1, 1, "photo.png")
        self.finished.emit(JobResult(total_found=1, converted=1))


class FailingFakeWorker(SuccessfulFakeWorker):
    created: list["FailingFakeWorker"] = []

    def __init__(self, service, options) -> None:
        super().__init__(service, options)
        FailingFakeWorker.created.append(self)

    def run(self) -> None:
        self.failed.emit("worker exploded")


def test_start_conversion_runs_worker_thread_and_restores_ui(
    qt_app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_path = tmp_path / "source.png"
    output_path = tmp_path / "out"
    input_path.write_bytes(b"placeholder")
    window = MainWindow()
    window.input_path_edit.setText(str(input_path))
    window.output_path_edit.setText(str(output_path))
    infos: list[tuple[str, str]] = []
    fake_thread = FakeThread(window)
    SuccessfulFakeWorker.created = []
    monkeypatch.setattr(main_window_module, "QThread", lambda parent: fake_thread)
    monkeypatch.setattr(main_window_module, "ConversionService", FakeService)
    monkeypatch.setattr(main_window_module, "ConversionWorker", SuccessfulFakeWorker)
    monkeypatch.setattr(
        QMessageBox,
        "information",
        lambda parent, title, message: infos.append((title, message)),
    )

    window._start_conversion()

    assert fake_thread.started_flag is True
    assert window.convert_button.isEnabled() is True
    assert window._thread is None
    assert window._worker is None
    assert SuccessfulFakeWorker.created[0].moved_to_thread is fake_thread
    assert "Starting conversion..." in window.log_edit.toPlainText()
    assert "Found 1 supported file(s)." in window.log_edit.toPlainText()
    assert "Processing file 1/1: photo.png" in window.log_edit.toPlainText()
    assert "Output path: out/photo.jpg" in window.log_edit.toPlainText()
    assert "Converted: 1" in window.log_edit.toPlainText()
    assert window.progress_bar.value() == 1
    assert window.status_label.text() == "Finished"
    assert infos and infos[0][0] == "Conversion finished"


def test_start_conversion_failed_worker_restores_ui_and_shows_error(
    qt_app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_path = tmp_path / "source.png"
    output_path = tmp_path / "out"
    input_path.write_bytes(b"placeholder")
    window = MainWindow()
    window.input_path_edit.setText(str(input_path))
    window.output_path_edit.setText(str(output_path))
    criticals: list[tuple[str, str]] = []
    fake_thread = FakeThread(window)
    FailingFakeWorker.created = []
    monkeypatch.setattr(main_window_module, "QThread", lambda parent: fake_thread)
    monkeypatch.setattr(main_window_module, "ConversionService", FakeService)
    monkeypatch.setattr(main_window_module, "ConversionWorker", FailingFakeWorker)
    monkeypatch.setattr(
        QMessageBox,
        "critical",
        lambda parent, title, message: criticals.append((title, message)),
    )

    window._start_conversion()

    assert window.convert_button.isEnabled() is True
    assert window._thread is None
    assert window._worker is None
    assert "Error: worker exploded" in window.log_edit.toPlainText()
    assert window.status_label.text() == "Failed"
    assert criticals == [("Conversion failed", "worker exploded")]


def test_start_conversion_ignores_parallel_request(
    qt_app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = MainWindow()
    window._thread = object()
    called = []
    monkeypatch.setattr(window, "validate_form", lambda: called.append("called"))

    window._start_conversion()

    assert called == []


def test_progress_changed_updates_progress_bar_and_status(
    qt_app: QApplication,
) -> None:
    window = MainWindow()

    window._on_progress_changed(3, 25, "D:/Photos/photo.nef")

    assert window.progress_bar.maximum() == 25
    assert window.progress_bar.value() == 3
    assert window.status_label.text() == "Processing 3 / 25: photo.nef"


def test_log_section_is_read_only_and_appends_messages(qt_app: QApplication) -> None:
    window = MainWindow()

    window._append_log_message("First")
    window._append_log_message("Second")

    assert window.log_edit.isReadOnly() is True
    assert window.log_edit.toPlainText() == "First\nSecond"
