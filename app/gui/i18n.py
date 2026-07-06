"""Simple dictionary-based localization helpers for the GUI."""

from __future__ import annotations

SUPPORTED_LANGUAGES: tuple[str, str] = ("uk", "en")
DEFAULT_LANGUAGE = "uk"
FALLBACK_LANGUAGE = "en"

TRANSLATIONS: dict[str, dict[str, str]] = {
    "uk": {
        "app.title": "Конвертер зображень",
        "group.language": "Мова",
        "label.language": "Мова",
        "language.ukrainian": "Українська",
        "language.english": "English",
        "group.input": "Input",
        "label.input_path": "Input шлях",
        "placeholder.input_path": "Виберіть input файл або папку",
        "button.select_file": "Вибрати файл",
        "button.select_folder": "Вибрати папку",
        "dialog.select_input_file.title": "Вибрати input файл",
        "dialog.select_input_folder.title": "Вибрати input папку",
        "group.output": "Output",
        "label.output_folder": "Output папка",
        "placeholder.output_folder": "Виберіть output папку",
        "button.select_output_folder": "Вибрати output папку",
        "dialog.select_output_folder.title": "Вибрати output папку",
        "group.format": "Format",
        "label.target_format": "Цільовий формат",
        "group.options": "Options",
        "label.quality": "Якість",
        "label.resize_width": "Ширина",
        "label.resize_height": "Висота",
        "checkbox.recursive": "Recursive",
        "checkbox.keep_structure": "Зберігати структуру папок",
        "checkbox.overwrite": "Перезаписувати існуючі файли",
        "group.action": "Action",
        "button.convert": "Конвертувати",
        "button.cancel": "Скасувати",
        "group.progress": "Progress",
        "status.ready": "Готово",
        "status.starting": "Початок конвертації...",
        "status.processing": "Обробка {current} / {total}: {file}",
        "status.cancelling": "Скасування...",
        "status.finished": "Готово",
        "status.cancelled": "Скасовано",
        "status.failed": "Помилка",
        "group.log": "Log",
        "placeholder.log": "Лог конвертації з'явиться тут",
        "dialog.validation.title": "Некоректні параметри",
        "dialog.finished.title": "Конвертація завершена",
        "dialog.cancelled.title": "Конвертацію скасовано",
        "dialog.failed.title": "Конвертація не вдалася",
        "dialog.running.title": "Конвертація триває",
        "dialog.running.message": (
            "Конвертація ще триває. Скасувати її та закрити після завершення?"
        ),
        "dialog.success.title": "Успішно",
        "dialog.error.title": "Помилка",
        "dialog.warning.title": "Попередження",
        "validation.input_required": "Input шлях обов'язковий.",
        "validation.input_missing": "Input шлях не існує: {path}",
        "validation.output_required": "Output папка обов'язкова.",
        "validation.output_not_folder": "Output шлях не є папкою: {path}",
        "validation.output_parent_missing": (
            "Батьківська папка для output не існує: {path}"
        ),
        "validation.target_required": "Цільовий формат обов'язковий.",
        "validation.target_unsupported": "Непідтримуваний цільовий формат: {format}",
        "validation.quality_invalid": "Якість має бути від 1 до 100.",
        "validation.resize_width_negative": "Ширина не може бути від'ємною.",
        "validation.resize_height_negative": "Висота не може бути від'ємною.",
        "log.starting": "Початок конвертації...",
        "log.error": "Помилка: {message}",
        "log.cancel_requested": "Запит на скасування. Очікуємо завершення поточного файлу...",
        "log.finished": "Конвертацію завершено.",
        "log.cancelled": "Конвертацію скасовано.",
        "log.failed": "Конвертація не вдалася: {message}",
    },
    "en": {
        "app.title": "Image Format Converter",
        "group.language": "Language",
        "label.language": "Language",
        "language.ukrainian": "Українська",
        "language.english": "English",
        "group.input": "Input",
        "label.input_path": "Input path",
        "placeholder.input_path": "Select an input file or folder",
        "button.select_file": "Select File",
        "button.select_folder": "Select Folder",
        "dialog.select_input_file.title": "Select input file",
        "dialog.select_input_folder.title": "Select input folder",
        "group.output": "Output",
        "label.output_folder": "Output folder",
        "placeholder.output_folder": "Select an output folder",
        "button.select_output_folder": "Select Output Folder",
        "dialog.select_output_folder.title": "Select output folder",
        "group.format": "Format",
        "label.target_format": "Target format",
        "group.options": "Options",
        "label.quality": "Quality",
        "label.resize_width": "Resize width",
        "label.resize_height": "Resize height",
        "checkbox.recursive": "Recursive",
        "checkbox.keep_structure": "Keep folder structure",
        "checkbox.overwrite": "Overwrite existing files",
        "group.action": "Action",
        "button.convert": "Convert",
        "button.cancel": "Cancel",
        "group.progress": "Progress",
        "status.ready": "Ready",
        "status.starting": "Starting conversion...",
        "status.processing": "Processing {current} / {total}: {file}",
        "status.cancelling": "Cancelling...",
        "status.finished": "Finished",
        "status.cancelled": "Cancelled",
        "status.failed": "Failed",
        "group.log": "Log",
        "placeholder.log": "Conversion log will appear here",
        "dialog.validation.title": "Invalid conversion options",
        "dialog.finished.title": "Conversion finished",
        "dialog.cancelled.title": "Conversion cancelled",
        "dialog.failed.title": "Conversion failed",
        "dialog.running.title": "Conversion running",
        "dialog.running.message": (
            "A conversion is still running. Cancel it and close after it finishes?"
        ),
        "dialog.success.title": "Success",
        "dialog.error.title": "Error",
        "dialog.warning.title": "Warning",
        "validation.input_required": "Input path is required.",
        "validation.input_missing": "Input path does not exist: {path}",
        "validation.output_required": "Output folder is required.",
        "validation.output_not_folder": "Output path is not a folder: {path}",
        "validation.output_parent_missing": (
            "Output folder parent does not exist: {path}"
        ),
        "validation.target_required": "Target format is required.",
        "validation.target_unsupported": "Unsupported target format: {format}",
        "validation.quality_invalid": "Quality must be between 1 and 100.",
        "validation.resize_width_negative": "Resize width cannot be negative.",
        "validation.resize_height_negative": "Resize height cannot be negative.",
        "log.starting": "Starting conversion...",
        "log.error": "Error: {message}",
        "log.cancel_requested": "Cancellation requested. Waiting for current file...",
        "log.finished": "Conversion finished.",
        "log.cancelled": "Conversion cancelled.",
        "log.failed": "Conversion failed: {message}",
    },
}


def translate(language: str, key: str) -> str:
    """Translate a GUI text key with safe fallbacks."""
    selected_language = language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE

    return (
        TRANSLATIONS.get(selected_language, {}).get(key)
        or TRANSLATIONS.get(FALLBACK_LANGUAGE, {}).get(key)
        or TRANSLATIONS.get(DEFAULT_LANGUAGE, {}).get(key)
        or key
    )
