"""Persistent GUI settings helpers."""

from __future__ import annotations

from PySide6.QtCore import QSettings

from app.gui.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES

ORGANIZATION_NAME = "ImageFormatConverter"
APPLICATION_NAME = "ImageFormatConverter"
LANGUAGE_KEY = "language"


def load_gui_language(settings: QSettings | None = None) -> str:
    """Load the saved GUI language or return the default language."""
    value = _settings(settings).value(LANGUAGE_KEY, DEFAULT_LANGUAGE)
    return normalize_language(value)


def save_gui_language(language: str, settings: QSettings | None = None) -> None:
    """Persist a supported GUI language, falling back to the default."""
    qsettings = _settings(settings)
    qsettings.setValue(LANGUAGE_KEY, normalize_language(language))
    qsettings.sync()


def normalize_language(language: object) -> str:
    """Return a supported language code for untrusted persisted values."""
    if isinstance(language, str) and language in SUPPORTED_LANGUAGES:
        return language
    return DEFAULT_LANGUAGE


def _settings(settings: QSettings | None) -> QSettings:
    return settings or QSettings(ORGANIZATION_NAME, APPLICATION_NAME)
