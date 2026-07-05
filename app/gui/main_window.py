"""Main window for the PySide6 GUI."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread
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
from app.gui.options_builder import build_conversion_options
from app.gui.validation import validate_conversion_form


class MainWindow(QMainWindow):
    """Main application window for the MVP v2 GUI."""

    def __init__(self) -> None:
        super().__init__()
        self._thread: QThread | None = None
        self._worker: ConversionWorker | None = None
        self.setWindowTitle("Image Format Converter")
        self.setMinimumSize(800, 600)
        self.setCentralWidget(self._build_central_widget())
        self._connect_signals()

    def _connect_signals(self) -> None:
        self.select_file_button.clicked.connect(self._select_input_file)
        self.select_folder_button.clicked.connect(self._select_input_folder)
        self.select_output_button.clicked.connect(self._select_output_folder)
        self.convert_button.clicked.connect(self._start_conversion)

    def _select_input_file(self) -> None:
        file_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Select input file",
        )
        if file_path:
            self.input_path_edit.setText(file_path)

    def _select_input_folder(self) -> None:
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select input folder",
        )
        if folder_path:
            self.input_path_edit.setText(folder_path)

    def _select_output_folder(self) -> None:
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select output folder",
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
        )

    def show_validation_warning(self, errors: list[str]) -> None:
        """Show validation errors to the user."""
        if not errors:
            return
        QMessageBox.warning(self, "Invalid conversion options", "\n".join(errors))

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
        thread.start()

    def _prepare_conversion_run(self) -> None:
        self.log_edit.clear()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting conversion...")
        self._append_log_message("Starting conversion...")

    def _append_log_message(self, message: str) -> None:
        self.log_edit.appendPlainText(message)

    def _on_progress_changed(self, current: int, total: int, path: str) -> None:
        if total > 0:
            self.progress_bar.setRange(0, total)
            self.progress_bar.setValue(current)
        self.status_label.setText(f"Processing {current} / {total}: {Path(path).name}")

    def _on_conversion_finished(self, result: JobResult) -> None:
        self._append_log_message(result.summary())
        self.status_label.setText("Finished")
        if result.total_found > 0:
            self.progress_bar.setRange(0, result.total_found)
            self.progress_bar.setValue(result.total_found)
        self.convert_button.setEnabled(True)
        QMessageBox.information(self, "Conversion finished", result.summary())

    def _on_conversion_failed(self, message: str) -> None:
        self._append_log_message(f"Error: {message}")
        self.status_label.setText("Failed")
        self.convert_button.setEnabled(True)
        QMessageBox.critical(self, "Conversion failed", message)

    def _clear_worker_references(self) -> None:
        self._worker = None
        self._thread = None

    def _build_central_widget(self) -> QWidget:
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.addWidget(self._build_input_group())
        layout.addWidget(self._build_output_group())
        layout.addWidget(self._build_format_group())
        layout.addWidget(self._build_options_group())
        layout.addWidget(self._build_action_group())
        layout.addWidget(self._build_progress_group())
        layout.addWidget(self._build_log_group(), stretch=1)
        return widget

    def _build_input_group(self) -> QGroupBox:
        group = QGroupBox("Input")
        layout = QVBoxLayout(group)

        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Input path"))
        self.input_path_edit = QLineEdit()
        self.input_path_edit.setPlaceholderText("Select an input file or folder")
        path_layout.addWidget(self.input_path_edit, stretch=1)
        layout.addLayout(path_layout)

        button_layout = QHBoxLayout()
        self.select_file_button = QPushButton("Select File")
        self.select_folder_button = QPushButton("Select Folder")
        button_layout.addWidget(self.select_file_button)
        button_layout.addWidget(self.select_folder_button)
        button_layout.addStretch(1)
        layout.addLayout(button_layout)

        return group

    def _build_output_group(self) -> QGroupBox:
        group = QGroupBox("Output")
        layout = QHBoxLayout(group)

        layout.addWidget(QLabel("Output folder"))
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText("Select an output folder")
        self.select_output_button = QPushButton("Select Output Folder")
        layout.addWidget(self.output_path_edit, stretch=1)
        layout.addWidget(self.select_output_button)

        return group

    def _build_format_group(self) -> QGroupBox:
        group = QGroupBox("Format")
        layout = QHBoxLayout(group)

        layout.addWidget(QLabel("Target format"))
        self.target_format_combo = QComboBox()
        self.target_format_combo.addItems(sorted(SUPPORTED_OUTPUT_FORMATS))
        self.target_format_combo.setCurrentText("jpg")
        layout.addWidget(self.target_format_combo)
        layout.addStretch(1)

        return group

    def _build_options_group(self) -> QGroupBox:
        group = QGroupBox("Options")
        layout = QVBoxLayout(group)

        numeric_layout = QHBoxLayout()
        numeric_layout.addWidget(QLabel("Quality"))
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(MIN_QUALITY, MAX_QUALITY)
        self.quality_spin.setValue(DEFAULT_QUALITY)
        numeric_layout.addWidget(self.quality_spin)

        numeric_layout.addWidget(QLabel("Resize width"))
        self.resize_width_spin = QSpinBox()
        self.resize_width_spin.setRange(0, 100_000)
        self.resize_width_spin.setValue(0)
        numeric_layout.addWidget(self.resize_width_spin)

        numeric_layout.addWidget(QLabel("Resize height"))
        self.resize_height_spin = QSpinBox()
        self.resize_height_spin.setRange(0, 100_000)
        self.resize_height_spin.setValue(0)
        numeric_layout.addWidget(self.resize_height_spin)
        numeric_layout.addStretch(1)
        layout.addLayout(numeric_layout)

        checkbox_layout = QHBoxLayout()
        self.recursive_checkbox = QCheckBox("Recursive")
        self.keep_structure_checkbox = QCheckBox("Keep folder structure")
        self.overwrite_checkbox = QCheckBox("Overwrite existing files")
        checkbox_layout.addWidget(self.recursive_checkbox)
        checkbox_layout.addWidget(self.keep_structure_checkbox)
        checkbox_layout.addWidget(self.overwrite_checkbox)
        checkbox_layout.addStretch(1)
        layout.addLayout(checkbox_layout)

        return group

    def _build_action_group(self) -> QGroupBox:
        group = QGroupBox("Action")
        layout = QHBoxLayout(group)

        self.convert_button = QPushButton("Convert")
        layout.addWidget(self.convert_button)
        layout.addStretch(1)

        return group

    def _build_progress_group(self) -> QGroupBox:
        group = QGroupBox("Progress")
        layout = QVBoxLayout(group)

        self.status_label = QLabel("Ready")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)

        return group

    def _build_log_group(self) -> QGroupBox:
        group = QGroupBox("Log")
        layout = QVBoxLayout(group)

        self.log_edit = QPlainTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setPlaceholderText("Conversion log will appear here")
        layout.addWidget(self.log_edit)

        return group
