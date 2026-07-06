"""Main window for the PySide6 GUI."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.core.config import (
    DEFAULT_QUALITY,
    MAX_QUALITY,
    MIN_QUALITY,
    SUPPORTED_OUTPUT_FORMATS,
)
from app.core.conversion_options import ConversionOptions
from app.core.conversion_service import ConversionService
from app.core.job_result import JobResult
from app.gui.conversion_worker import ConversionWorker
from app.gui.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, translate
from app.gui.options_builder import build_conversion_options
from app.gui.settings import load_gui_language, save_gui_language
from app.gui.validation import validate_conversion_form


class MainWindow(QMainWindow):
    """Main application window for the MVP v2 GUI."""

    def __init__(self) -> None:
        super().__init__()
        self._thread: QThread | None = None
        self._worker: ConversionWorker | None = None
        self._language = load_gui_language()
        self._status_key = "status.ready"
        self._status_params: dict[str, object] = {}
        self.setWindowTitle(self._t("app.title"))
        self.setMinimumSize(800, 600)
        self.setCentralWidget(self._build_central_widget())
        self._connect_signals()

    def _t(self, key: str) -> str:
        """Translate a GUI text key using the current window language."""
        language = (
            self._language
            if self._language in SUPPORTED_LANGUAGES
            else DEFAULT_LANGUAGE
        )
        return translate(language, key)

    def _connect_signals(self) -> None:
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        self.select_file_button.clicked.connect(self._select_input_file)
        self.select_folder_button.clicked.connect(self._select_input_folder)
        self.select_output_button.clicked.connect(self._select_output_folder)
        self.convert_button.clicked.connect(self._start_conversion)
        self.cancel_button.clicked.connect(self._cancel_conversion)

    def _on_language_changed(self) -> None:
        language = self.language_combo.currentData()
        self._set_language(language if isinstance(language, str) else DEFAULT_LANGUAGE)

    def _set_language(self, language: str) -> None:
        self._language = (
            language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
        )
        self._retranslate_ui()
        save_gui_language(self._language)

    def _set_status(self, key: str, **params: object) -> None:
        self._status_key = key
        self._status_params = params
        self._refresh_status()

    def _refresh_status(self) -> None:
        self.status_label.setText(
            self._t(self._status_key).format(**self._status_params)
        )

    def _retranslate_ui(self) -> None:
        """Update existing widget text for the current language."""
        self.setWindowTitle(self._t("app.title"))

        self.language_group.setTitle(self._t("group.language"))
        self.language_label.setText(self._t("label.language"))
        was_blocked = self.language_combo.blockSignals(True)
        self.language_combo.setItemText(0, self._t("language.ukrainian"))
        self.language_combo.setItemText(1, self._t("language.english"))
        self.language_combo.setCurrentIndex(
            SUPPORTED_LANGUAGES.index(self._language)
            if self._language in SUPPORTED_LANGUAGES
            else 0
        )
        self.language_combo.blockSignals(was_blocked)

        self.input_group.setTitle(self._t("group.input"))
        self.input_path_label.setText(self._t("label.input_path"))
        self.input_path_edit.setPlaceholderText(self._t("placeholder.input_path"))
        self.select_file_button.setText(self._t("button.select_file"))
        self.select_folder_button.setText(self._t("button.select_folder"))

        self.output_group.setTitle(self._t("group.output"))
        self.output_folder_label.setText(self._t("label.output_folder"))
        self.output_path_edit.setPlaceholderText(self._t("placeholder.output_folder"))
        self.select_output_button.setText(self._t("button.select_output_folder"))

        self.format_group.setTitle(self._t("group.format"))
        self.target_format_label.setText(self._t("label.target_format"))

        self.options_group.setTitle(self._t("group.options"))
        self.quality_label.setText(self._t("label.quality"))
        self.resize_width_label.setText(self._t("label.resize_width"))
        self.resize_height_label.setText(self._t("label.resize_height"))
        self.recursive_checkbox.setText(self._t("checkbox.recursive"))
        self.keep_structure_checkbox.setText(self._t("checkbox.keep_structure"))
        self.overwrite_checkbox.setText(self._t("checkbox.overwrite"))

        self.action_group.setTitle(self._t("group.action"))
        self.convert_button.setText(self._t("button.convert"))
        self.cancel_button.setText(self._t("button.cancel"))

        self.progress_group.setTitle(self._t("group.progress"))
        self._refresh_status()

        self.log_group.setTitle(self._t("group.log"))
        self._set_log_placeholder()

    def _select_input_file(self) -> None:
        file_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            self._t("dialog.select_input_file.title"),
        )
        if file_path:
            self.input_path_edit.setText(file_path)

    def _select_input_folder(self) -> None:
        folder_path = QFileDialog.getExistingDirectory(
            self,
            self._t("dialog.select_input_folder.title"),
        )
        if folder_path:
            self.input_path_edit.setText(folder_path)

    def _select_output_folder(self) -> None:
        folder_path = QFileDialog.getExistingDirectory(
            self,
            self._t("dialog.select_output_folder.title"),
        )
        if folder_path:
            self.output_path_edit.setText(folder_path)

    def build_conversion_options(self) -> ConversionOptions:
        """Build core conversion options from current form values."""
        return build_conversion_options(
            input_path=self.input_path_edit.text(),
            output_dir=self.output_path_edit.text(),
            target_format=self.target_format_combo.currentText(),
            quality=self.quality_spin.value(),
            recursive=self.recursive_checkbox.isChecked(),
            overwrite=self.overwrite_checkbox.isChecked(),
            keep_structure=self.keep_structure_checkbox.isChecked(),
            resize_width=self.resize_width_spin.value(),
            resize_height=self.resize_height_spin.value(),
        )

    def validate_form(self) -> list[str]:
        """Validate current form values and return error messages."""
        return validate_conversion_form(
            input_path=self.input_path_edit.text(),
            output_dir=self.output_path_edit.text(),
            target_format=self.target_format_combo.currentText(),
            quality=self.quality_spin.value(),
            resize_width=self.resize_width_spin.value(),
            resize_height=self.resize_height_spin.value(),
            language=self._language,
        )

    def show_validation_warning(self, errors: list[str]) -> None:
        """Show validation errors to the user."""
        if not errors:
            return
        QMessageBox.warning(self, self._t("dialog.validation.title"), "\n".join(errors))

    def _start_conversion(self) -> None:
        if self._thread is not None:
            return

        errors = self.validate_form()
        if errors:
            self.show_validation_warning(errors)
            return

        self._prepare_conversion_run()
        options = self.build_conversion_options()
        service = ConversionService()
        thread = QThread(self)
        worker = ConversionWorker(service, options)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.progress_changed.connect(self._on_progress_changed)
        worker.log_message.connect(self._append_log_message)
        worker.finished.connect(self._on_conversion_finished)
        worker.failed.connect(self._on_conversion_failed)
        worker.finished.connect(lambda _result: thread.quit())
        worker.failed.connect(lambda _message: thread.quit())
        worker.finished.connect(lambda _result: worker.deleteLater())
        worker.failed.connect(lambda _message: worker.deleteLater())
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_worker_references)

        self._thread = thread
        self._worker = worker
        self.convert_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        thread.start()

    def _cancel_conversion(self) -> None:
        if self._worker is None:
            return
        self.cancel_button.setEnabled(False)
        self._set_status("status.cancelling")
        self._append_log_message(self._t("log.cancel_requested"))
        self._worker.request_cancel()

    def _prepare_conversion_run(self) -> None:
        self.log_edit.clear()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self._set_status("status.starting")
        self.cancel_button.setEnabled(False)
        self._append_log_message(self._t("log.starting"))

    def _append_log_message(self, message: str) -> None:
        self.log_edit.appendPlainText(message)

    def _set_log_placeholder(self) -> None:
        self.log_edit.setPlaceholderText(self._t("placeholder.log"))
        self.log_edit.viewport().update()

    def _on_progress_changed(self, current: int, total: int, path: str) -> None:
        if total > 0:
            self.progress_bar.setRange(0, total)
            self.progress_bar.setValue(current)
        self._set_status(
            "status.processing",
            current=current,
            total=total,
            file=Path(path).name,
        )

    def _on_conversion_finished(self, result: JobResult) -> None:
        is_cancelled = result.skipped and result.skipped > 0
        self._append_log_message(
            self._t("log.cancelled") if is_cancelled else self._t("log.finished")
        )
        self._append_log_message(result.summary())
        self._set_status("status.cancelled" if is_cancelled else "status.finished")
        if result.total_found > 0:
            self.progress_bar.setRange(0, result.total_found)
            self.progress_bar.setValue(result.converted + result.failed)
        self.convert_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        title = (
            self._t("dialog.cancelled.title")
            if is_cancelled
            else self._t("dialog.finished.title")
        )
        QMessageBox.information(self, title, result.summary())

    def _on_conversion_failed(self, message: str) -> None:
        self._append_log_message(self._t("log.failed").format(message=message))
        self._set_status("status.failed")
        self.convert_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        QMessageBox.critical(self, self._t("dialog.failed.title"), message)

    def _clear_worker_references(self) -> None:
        self._worker = None
        self._thread = None

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 - Qt override.
        if self._thread is None:
            event.accept()
            return

        answer = QMessageBox.question(
            self,
            self._t("dialog.running.title"),
            self._t("dialog.running.message"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self._cancel_conversion()
        event.ignore()

    def _build_central_widget(self) -> QWidget:
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.addWidget(self._build_language_group())
        layout.addWidget(self._build_input_group())
        layout.addWidget(self._build_output_group())
        layout.addWidget(self._build_format_group())
        layout.addWidget(self._build_options_group())
        layout.addWidget(self._build_action_group())
        layout.addWidget(self._build_progress_group())
        layout.addWidget(self._build_log_group(), stretch=1)
        return widget

    def _build_language_group(self) -> QGroupBox:
        self.language_group = QGroupBox(self._t("group.language"))
        layout = QHBoxLayout(self.language_group)

        self.language_label = QLabel(self._t("label.language"))
        self.language_combo = QComboBox()
        self.language_combo.addItem(self._t("language.ukrainian"), "uk")
        self.language_combo.addItem(self._t("language.english"), "en")
        self.language_combo.setCurrentIndex(
            SUPPORTED_LANGUAGES.index(self._language)
            if self._language in SUPPORTED_LANGUAGES
            else 0
        )
        layout.addWidget(self.language_label)
        layout.addWidget(self.language_combo)
        layout.addStretch(1)

        return self.language_group

    def _build_input_group(self) -> QGroupBox:
        self.input_group = QGroupBox(self._t("group.input"))
        layout = QVBoxLayout(self.input_group)

        path_layout = QHBoxLayout()
        self.input_path_label = QLabel(self._t("label.input_path"))
        path_layout.addWidget(self.input_path_label)
        self.input_path_edit = QLineEdit()
        self.input_path_edit.setPlaceholderText(self._t("placeholder.input_path"))
        path_layout.addWidget(self.input_path_edit, stretch=1)
        layout.addLayout(path_layout)

        button_layout = QHBoxLayout()
        self.select_file_button = QPushButton(self._t("button.select_file"))
        self.select_folder_button = QPushButton(self._t("button.select_folder"))
        button_layout.addWidget(self.select_file_button)
        button_layout.addWidget(self.select_folder_button)
        button_layout.addStretch(1)
        layout.addLayout(button_layout)

        return self.input_group

    def _build_output_group(self) -> QGroupBox:
        self.output_group = QGroupBox(self._t("group.output"))
        layout = QHBoxLayout(self.output_group)

        self.output_folder_label = QLabel(self._t("label.output_folder"))
        layout.addWidget(self.output_folder_label)
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText(self._t("placeholder.output_folder"))
        self.select_output_button = QPushButton(
            self._t("button.select_output_folder")
        )
        layout.addWidget(self.output_path_edit, stretch=1)
        layout.addWidget(self.select_output_button)

        return self.output_group

    def _build_format_group(self) -> QGroupBox:
        self.format_group = QGroupBox(self._t("group.format"))
        layout = QHBoxLayout(self.format_group)

        self.target_format_label = QLabel(self._t("label.target_format"))
        layout.addWidget(self.target_format_label)
        self.target_format_combo = QComboBox()
        self.target_format_combo.addItems(sorted(SUPPORTED_OUTPUT_FORMATS))
        self.target_format_combo.setCurrentText("jpg")
        layout.addWidget(self.target_format_combo)
        layout.addStretch(1)

        return self.format_group

    def _build_options_group(self) -> QGroupBox:
        self.options_group = QGroupBox(self._t("group.options"))
        layout = QVBoxLayout(self.options_group)

        numeric_layout = QHBoxLayout()
        self.quality_label = QLabel(self._t("label.quality"))
        numeric_layout.addWidget(self.quality_label)
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(MIN_QUALITY, MAX_QUALITY)
        self.quality_spin.setValue(DEFAULT_QUALITY)
        numeric_layout.addWidget(self.quality_spin)

        self.resize_width_label = QLabel(self._t("label.resize_width"))
        numeric_layout.addWidget(self.resize_width_label)
        self.resize_width_spin = QSpinBox()
        self.resize_width_spin.setRange(0, 100_000)
        self.resize_width_spin.setValue(0)
        numeric_layout.addWidget(self.resize_width_spin)

        self.resize_height_label = QLabel(self._t("label.resize_height"))
        numeric_layout.addWidget(self.resize_height_label)
        self.resize_height_spin = QSpinBox()
        self.resize_height_spin.setRange(0, 100_000)
        self.resize_height_spin.setValue(0)
        numeric_layout.addWidget(self.resize_height_spin)
        numeric_layout.addStretch(1)
        layout.addLayout(numeric_layout)

        checkbox_layout = QHBoxLayout()
        self.recursive_checkbox = QCheckBox(self._t("checkbox.recursive"))
        self.keep_structure_checkbox = QCheckBox(self._t("checkbox.keep_structure"))
        self.overwrite_checkbox = QCheckBox(self._t("checkbox.overwrite"))
        checkbox_layout.addWidget(self.recursive_checkbox)
        checkbox_layout.addWidget(self.keep_structure_checkbox)
        checkbox_layout.addWidget(self.overwrite_checkbox)
        checkbox_layout.addStretch(1)
        layout.addLayout(checkbox_layout)

        return self.options_group

    def _build_action_group(self) -> QGroupBox:
        self.action_group = QGroupBox(self._t("group.action"))
        layout = QHBoxLayout(self.action_group)

        self.convert_button = QPushButton(self._t("button.convert"))
        self.cancel_button = QPushButton(self._t("button.cancel"))
        self.cancel_button.setEnabled(False)
        layout.addWidget(self.convert_button)
        layout.addWidget(self.cancel_button)
        layout.addStretch(1)

        return self.action_group

    def _build_progress_group(self) -> QGroupBox:
        self.progress_group = QGroupBox(self._t("group.progress"))
        layout = QVBoxLayout(self.progress_group)

        self.status_label = QLabel(self._t("status.ready"))
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)

        return self.progress_group

    def _build_log_group(self) -> QGroupBox:
        self.log_group = QGroupBox(self._t("group.log"))
        layout = QVBoxLayout(self.log_group)

        self.log_edit = QPlainTextEdit()
        self.log_edit.setReadOnly(True)
        self._set_log_placeholder()
        layout.addWidget(self.log_edit)

        return self.log_group
