"""Tests for persistent GUI settings helpers."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings

from app.gui.settings import (
    LANGUAGE_KEY,
    load_gui_language,
    normalize_language,
    save_gui_language,
)


def _temp_settings(path: Path) -> QSettings:
    settings = QSettings(str(path), QSettings.Format.IniFormat)
    settings.clear()
    return settings


def test_load_gui_language_returns_default_without_saved_value(
    tmp_path: Path,
) -> None:
    settings = _temp_settings(tmp_path / "settings.ini")

    assert load_gui_language(settings) == "uk"


def test_save_and_load_gui_language(
    tmp_path: Path,
) -> None:
    settings = _temp_settings(tmp_path / "settings.ini")

    save_gui_language("en", settings)

    assert load_gui_language(settings) == "en"


def test_save_gui_language_normalizes_unknown_language(
    tmp_path: Path,
) -> None:
    settings = _temp_settings(tmp_path / "settings.ini")

    save_gui_language("de", settings)

    assert settings.value(LANGUAGE_KEY) == "uk"
    assert load_gui_language(settings) == "uk"


def test_load_gui_language_normalizes_unknown_persisted_value(
    tmp_path: Path,
) -> None:
    settings = _temp_settings(tmp_path / "settings.ini")
    settings.setValue(LANGUAGE_KEY, "de")

    assert load_gui_language(settings) == "uk"


def test_normalize_language_accepts_only_supported_language_codes() -> None:
    assert normalize_language("uk") == "uk"
    assert normalize_language("en") == "en"
    assert normalize_language("de") == "uk"
    assert normalize_language(None) == "uk"
