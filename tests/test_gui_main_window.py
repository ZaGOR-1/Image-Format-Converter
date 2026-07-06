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


@pytest.fixture(autouse=True)
def isolated_language_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> list[str]:
    saved_languages: list[str] = []
    monkeypatch.setattr(main_window_module, "load_gui_language", lambda: "uk")
    monkeypatch.setattr(
        main_window_module,
        "save_gui_language",
        saved_languages.append,
    )
    return saved_languages


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
    assert window.keep_structure_checkbox.text() == "Зберігати структуру папок"
    assert window.overwrite_checkbox.text() == "Перезаписувати існуючі файли"
    assert window.recursive_checkbox.isChecked() is False
    assert window.keep_structure_checkbox.isChecked() is False
    assert window.overwrite_checkbox.isChecked() is False
    assert window.cancel_button.text() == "Скасувати"
    assert window.cancel_button.isEnabled() is False


def test_language_selector_defaults_to_ukrainian(qt_app: QApplication) -> None:
    window = MainWindow()

    assert window._language == "uk"
    assert window.language_label.text() == "Мова"
    assert window.language_combo.count() == 2
    assert window.language_combo.itemText(0) == "Українська"
    assert window.language_combo.itemData(0) == "uk"
    assert window.language_combo.itemText(1) == "English"
    assert window.language_combo.itemData(1) == "en"
    assert window.language_combo.currentData() == "uk"


def test_main_window_loads_saved_language(
    qt_app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(main_window_module, "load_gui_language", lambda: "en")

    window = MainWindow()

    assert window._language == "en"
    assert window.language_combo.currentData() == "en"
    assert window.convert_button.text() == "Convert"


def test_language_selector_updates_language_state(
    qt_app: QApplication,
    isolated_language_settings: list[str],
) -> None:
    window = MainWindow()

    window.language_combo.setCurrentIndex(1)

    assert window._language == "en"
    assert window.language_combo.currentData() == "en"
    assert window.convert_button.text() == "Convert"
    assert window.input_path_label.text() == "Input path"
    assert window.keep_structure_checkbox.text() == "Keep folder structure"
    assert window.status_label.text() == "Ready"
    assert isolated_language_settings == ["en"]


def test_language_switch_to_english_updates_visible_ui_text(
    qt_app: QApplication,
) -> None:
    window = MainWindow()

    window.language_combo.setCurrentIndex(1)

    assert window.windowTitle() == "Image Format Converter"
    assert window.language_group.title() == "Language"
    assert window.input_group.title() == "Input"
    assert window.output_group.title() == "Output"
    assert window.format_group.title() == "Format"
    assert window.options_group.title() == "Options"
    assert window.action_group.title() == "Action"
    assert window.progress_group.title() == "Progress"
    assert window.log_group.title() == "Log"
    assert window.input_path_edit.placeholderText() == "Select an input file or folder"
    assert window.output_path_edit.placeholderText() == "Select an output folder"
    assert window.log_edit.placeholderText() == "Conversion log will appear here"
    assert window.select_file_button.text() == "Select File"
    assert window.select_folder_button.text() == "Select Folder"
    assert window.select_output_button.text() == "Select Output Folder"
    assert window.target_format_label.text() == "Target format"
    assert window.quality_label.text() == "Quality"
    assert window.resize_width_label.text() == "Resize width"
    assert window.resize_height_label.text() == "Resize height"
    assert window.overwrite_checkbox.text() == "Overwrite existing files"


def test_language_switch_back_to_ukrainian_restores_text(
    qt_app: QApplication,
) -> None:
    window = MainWindow()

    window.language_combo.setCurrentIndex(1)
    window.language_combo.setCurrentIndex(0)

    assert window._language == "uk"
    assert window.convert_button.text() == "Конвертувати"
    assert window.input_path_label.text() == "Input шлях"
    assert window.keep_structure_checkbox.text() == "Зберігати структуру папок"
    assert window.log_edit.placeholderText() == "Лог конвертації з'явиться тут"
    assert window.status_label.text() == "Готово"


def test_language_switch_preserves_form_log_progress_and_format_values(
    qt_app: QApplication,
) -> None:
    window = MainWindow()
    window.input_path_edit.setText("D:/Photos/input")
    window.output_path_edit.setText("D:/Photos/output")
    window.target_format_combo.setCurrentText("webp")
    window._append_log_message("Existing log")
    window.progress_bar.setRange(0, 10)
    window.progress_bar.setValue(4)
    window._on_progress_changed(4, 10, "D:/Photos/photo.png")
    formats_before = [
        window.target_format_combo.itemText(index)
        for index in range(window.target_format_combo.count())
    ]

    window.language_combo.setCurrentIndex(1)

    formats_after = [
        window.target_format_combo.itemText(index)
        for index in range(window.target_format_combo.count())
    ]
    assert window.input_path_edit.text() == "D:/Photos/input"
    assert window.output_path_edit.text() == "D:/Photos/output"
    assert window.target_format_combo.currentText() == "webp"
    assert window.log_edit.toPlainText() == "Existing log"
    assert window.progress_bar.maximum() == 10
    assert window.progress_bar.value() == 4
    assert window.status_label.text() == "Processing 4 / 10: photo.png"
    assert formats_after == formats_before == sorted(SUPPORTED_OUTPUT_FORMATS)


def test_set_language_falls_back_to_default_for_unknown_language(
    qt_app: QApplication,
    isolated_language_settings: list[str],
) -> None:
    window = MainWindow()

    window._set_language("de")

    assert window._language == "uk"
    assert isolated_language_settings == ["uk"]


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


def test_validate_form_uses_current_language(qt_app: QApplication) -> None:
    window = MainWindow()
    window.language_combo.setCurrentIndex(1)
    window.input_path_edit.setText("")
    window.output_path_edit.setText("")
    window.target_format_combo.setCurrentText("jpg")
    window.quality_spin.setValue(92)
    window.resize_width_spin.setValue(0)
    window.resize_height_spin.setValue(0)

    errors = window.validate_form()

    assert "Input path is required." in errors
    assert "Output folder is required." in errors


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

    window.show_validation_warning(["Input шлях обов'язковий.", "Output required."])

    assert calls == [
        (
            "Некоректні параметри",
            "Input шлях обов'язковий.\nOutput required.",
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
        lambda: ["Input шлях обов'язковий."],
    )
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda parent, title, message: warnings.append((title, message)),
    )

    window._start_conversion()

    assert warnings == [
        ("Некоректні параметри", "Input шлях обов'язковий."),
    ]
    assert window.convert_button.isEnabled() is True
    assert window.cancel_button.isEnabled() is False
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
        self.cancel_requested = False
        SuccessfulFakeWorker.created.append(self)

    def moveToThread(self, thread) -> None:
        self.moved_to_thread = thread

    def deleteLater(self) -> None:
        self.deleted = True

    def request_cancel(self) -> None:
        self.cancel_requested = True

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
    assert "Початок конвертації..." in window.log_edit.toPlainText()
    assert "Found 1 supported file(s)." in window.log_edit.toPlainText()
    assert "Processing file 1/1: photo.png" in window.log_edit.toPlainText()
    assert "Output path: out/photo.jpg" in window.log_edit.toPlainText()
    assert "Конвертацію завершено." in window.log_edit.toPlainText()
    assert "Converted: 1" in window.log_edit.toPlainText()
    assert window.progress_bar.value() == 1
    assert window.status_label.text() == "Готово"
    assert window.cancel_button.isEnabled() is False
    assert infos and infos[0][0] == "Конвертація завершена"


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
    assert window.cancel_button.isEnabled() is False
    assert window._thread is None
    assert window._worker is None
    assert "Конвертація не вдалася: worker exploded" in window.log_edit.toPlainText()
    assert window.status_label.text() == "Помилка"
    assert criticals == [("Конвертація не вдалася", "worker exploded")]


def test_finish_and_cancelled_dialogs_use_current_language(
    qt_app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = MainWindow()
    window.language_combo.setCurrentIndex(1)
    infos: list[tuple[str, str]] = []
    monkeypatch.setattr(
        QMessageBox,
        "information",
        lambda parent, title, message: infos.append((title, message)),
    )

    window._on_conversion_finished(JobResult(total_found=1, converted=1))
    window._on_conversion_finished(JobResult(total_found=1, skipped=1))

    assert "Conversion finished." in window.log_edit.toPlainText()
    assert "Conversion cancelled." in window.log_edit.toPlainText()
    assert infos[0][0] == "Conversion finished"
    assert infos[1][0] == "Conversion cancelled"
    assert window.status_label.text() == "Cancelled"


def test_failed_dialog_and_log_use_current_language(
    qt_app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = MainWindow()
    window.language_combo.setCurrentIndex(1)
    criticals: list[tuple[str, str]] = []
    monkeypatch.setattr(
        QMessageBox,
        "critical",
        lambda parent, title, message: criticals.append((title, message)),
    )

    window._on_conversion_failed("worker exploded")

    assert "Conversion failed: worker exploded" in window.log_edit.toPlainText()
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
    assert window.status_label.text() == "Обробка 3 / 25: photo.nef"


def test_log_section_is_read_only_and_appends_messages(qt_app: QApplication) -> None:
    window = MainWindow()

    window._append_log_message("First")
    window._append_log_message("Second")

    assert window.log_edit.isReadOnly() is True
    assert window.log_edit.toPlainText() == "First\nSecond"


def test_cancel_conversion_requests_worker_cancel(qt_app: QApplication) -> None:
    window = MainWindow()
    worker = SuccessfulFakeWorker(FakeService(), object())
    window._worker = worker
    worker.log_message.connect(window._append_log_message)
    window.cancel_button.setEnabled(True)

    window._cancel_conversion()

    assert worker.cancel_requested is True
    assert window.cancel_button.isEnabled() is False
    assert window.status_label.text() == "Скасування..."
    assert (
        "Запит на скасування. Очікуємо завершення поточного файлу..."
        in window.log_edit.toPlainText()
    )


def test_cancel_conversion_log_uses_current_language(qt_app: QApplication) -> None:
    window = MainWindow()
    window.language_combo.setCurrentIndex(1)
    worker = SuccessfulFakeWorker(FakeService(), object())
    window._worker = worker
    window.cancel_button.setEnabled(True)

    window._cancel_conversion()

    assert worker.cancel_requested is True
    assert window.status_label.text() == "Cancelling..."
    assert (
        "Cancellation requested. Waiting for current file..."
        in window.log_edit.toPlainText()
    )


class FakeCloseEvent:
    def __init__(self) -> None:
        self.accepted = False
        self.ignored = False

    def accept(self) -> None:
        self.accepted = True

    def ignore(self) -> None:
        self.ignored = True


def test_close_event_requests_cancel_when_conversion_is_running(
    qt_app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = MainWindow()
    worker = SuccessfulFakeWorker(FakeService(), object())
    window._thread = object()
    window._worker = worker
    event = FakeCloseEvent()
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )

    window.closeEvent(event)

    assert worker.cancel_requested is True
    assert event.ignored is True
    assert event.accepted is False


def test_close_event_dialog_uses_current_language(
    qt_app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = MainWindow()
    window.language_combo.setCurrentIndex(1)
    worker = SuccessfulFakeWorker(FakeService(), object())
    window._thread = object()
    window._worker = worker
    event = FakeCloseEvent()
    questions: list[tuple[str, str]] = []

    def fake_question(parent, title, message, *args, **kwargs):
        questions.append((title, message))
        return QMessageBox.StandardButton.No

    monkeypatch.setattr(QMessageBox, "question", fake_question)

    window.closeEvent(event)

    assert questions == [
        (
            "Conversion running",
            "A conversion is still running. Cancel it and close after it finishes?",
        )
    ]
    assert worker.cancel_requested is False
    assert event.ignored is True
