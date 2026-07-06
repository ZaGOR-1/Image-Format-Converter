"""Tests for GUI validation helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.gui.validation import validate_conversion_form


def test_validate_conversion_form_accepts_valid_values(tmp_path: Path) -> None:
    input_path = tmp_path / "source.png"
    output_dir = tmp_path / "out"
    input_path.write_bytes(b"placeholder")

    errors = validate_conversion_form(
        input_path=str(input_path),
        output_dir=str(output_dir),
        target_format="jpg",
        quality=92,
        resize_width=0,
        resize_height=0,
    )

    assert errors == []
    assert not output_dir.exists()


def test_validate_conversion_form_requires_input_path(tmp_path: Path) -> None:
    errors = validate_conversion_form(
        input_path="",
        output_dir=str(tmp_path / "out"),
        target_format="jpg",
        quality=92,
        resize_width=0,
        resize_height=0,
    )

    assert "Input шлях обов'язковий." in errors


def test_validate_conversion_form_requires_existing_input(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing.png"

    errors = validate_conversion_form(
        input_path=str(missing),
        output_dir=str(tmp_path / "out"),
        target_format="jpg",
        quality=92,
        resize_width=0,
        resize_height=0,
    )

    assert f"Input шлях не існує: {missing}" in errors


def test_validate_conversion_form_requires_output_folder() -> None:
    errors = validate_conversion_form(
        input_path="input.png",
        output_dir="",
        target_format="jpg",
        quality=92,
        resize_width=0,
        resize_height=0,
    )

    assert "Output папка обов'язкова." in errors


def test_validate_conversion_form_rejects_file_as_output_folder(
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "source.png"
    output_file = tmp_path / "out.txt"
    input_path.write_bytes(b"placeholder")
    output_file.write_text("not a folder", encoding="utf-8")

    errors = validate_conversion_form(
        input_path=str(input_path),
        output_dir=str(output_file),
        target_format="jpg",
        quality=92,
        resize_width=0,
        resize_height=0,
    )

    assert f"Output шлях не є папкою: {output_file}" in errors


def test_validate_conversion_form_rejects_unsupported_format(
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "source.png"
    input_path.write_bytes(b"placeholder")

    errors = validate_conversion_form(
        input_path=str(input_path),
        output_dir=str(tmp_path / "out"),
        target_format="gif",
        quality=92,
        resize_width=0,
        resize_height=0,
    )

    assert "Непідтримуваний цільовий формат: gif" in errors


def test_validate_conversion_form_rejects_invalid_quality(
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "source.png"
    input_path.write_bytes(b"placeholder")

    errors = validate_conversion_form(
        input_path=str(input_path),
        output_dir=str(tmp_path / "out"),
        target_format="jpg",
        quality=101,
        resize_width=0,
        resize_height=0,
    )

    assert "Якість має бути від 1 до 100." in errors


def test_validate_conversion_form_rejects_negative_resize_values(
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "source.png"
    input_path.write_bytes(b"placeholder")

    errors = validate_conversion_form(
        input_path=str(input_path),
        output_dir=str(tmp_path / "out"),
        target_format="jpg",
        quality=92,
        resize_width=-1,
        resize_height=-2,
    )

    assert "Ширина не може бути від'ємною." in errors
    assert "Висота не може бути від'ємною." in errors


@pytest.mark.parametrize(
    ("language", "expected_messages"),
    [
        (
            "uk",
            [
                "Input шлях обов'язковий.",
                "Output папка обов'язкова.",
                "Цільовий формат обов'язковий.",
                "Якість має бути від 1 до 100.",
                "Ширина не може бути від'ємною.",
                "Висота не може бути від'ємною.",
            ],
        ),
        (
            "en",
            [
                "Input path is required.",
                "Output folder is required.",
                "Target format is required.",
                "Quality must be between 1 and 100.",
                "Resize width cannot be negative.",
                "Resize height cannot be negative.",
            ],
        ),
    ],
)
def test_validate_conversion_form_localizes_common_errors(
    language: str,
    expected_messages: list[str],
) -> None:
    errors = validate_conversion_form(
        input_path="",
        output_dir="",
        target_format="",
        quality=0,
        resize_width=-1,
        resize_height=-2,
        language=language,
    )

    for message in expected_messages:
        assert message in errors


def test_validate_conversion_form_returns_english_messages() -> None:
    errors = validate_conversion_form(
        input_path="",
        output_dir="",
        target_format="gif",
        quality=101,
        resize_width=-1,
        resize_height=-2,
        language="en",
    )

    assert "Input path is required." in errors
    assert "Output folder is required." in errors
    assert "Unsupported target format: gif" in errors
    assert "Quality must be between 1 and 100." in errors
    assert "Resize width cannot be negative." in errors
    assert "Resize height cannot be negative." in errors


def test_validate_conversion_form_falls_back_to_default_language() -> None:
    errors = validate_conversion_form(
        input_path="",
        output_dir="",
        target_format="",
        quality=0,
        resize_width=-1,
        resize_height=-2,
        language="de",
    )

    assert "Input шлях обов'язковий." in errors
    assert "Output папка обов'язкова." in errors
    assert "Цільовий формат обов'язковий." in errors
    assert "Якість має бути від 1 до 100." in errors
    assert "Ширина не може бути від'ємною." in errors
    assert "Висота не може бути від'ємною." in errors
