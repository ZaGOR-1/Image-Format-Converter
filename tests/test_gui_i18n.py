"""Tests for GUI localization helpers."""

from __future__ import annotations

from app.gui import i18n
from app.gui.i18n import (
    DEFAULT_LANGUAGE,
    FALLBACK_LANGUAGE,
    SUPPORTED_LANGUAGES,
    translate,
)


def test_translate_returns_ukrainian_text() -> None:
    assert translate("uk", "button.convert") == "Конвертувати"


def test_translate_returns_english_text() -> None:
    assert translate("en", "button.convert") == "Convert"


def test_translate_unknown_language_falls_back_to_default_language() -> None:
    assert translate("de", "button.convert") == "Конвертувати"


def test_translate_missing_selected_language_key_falls_back_to_english(
    monkeypatch,
) -> None:
    translations = {
        "uk": {},
        "en": {"test.only_english": "English fallback"},
    }
    monkeypatch.setattr(i18n, "TRANSLATIONS", translations)

    assert translate("uk", "test.only_english") == "English fallback"


def test_translate_missing_english_key_falls_back_to_ukrainian(monkeypatch) -> None:
    translations = {
        "uk": {"test.only_ukrainian": "Український fallback"},
        "en": {},
    }
    monkeypatch.setattr(i18n, "TRANSLATIONS", translations)

    assert translate("en", "test.only_ukrainian") == "Український fallback"


def test_translate_missing_key_everywhere_returns_key() -> None:
    assert translate("uk", "missing.key") == "missing.key"


def test_supported_languages_include_ukrainian_and_english() -> None:
    assert SUPPORTED_LANGUAGES == ("uk", "en")


def test_default_and_fallback_languages_are_stable() -> None:
    assert DEFAULT_LANGUAGE == "uk"
    assert FALLBACK_LANGUAGE == "en"
