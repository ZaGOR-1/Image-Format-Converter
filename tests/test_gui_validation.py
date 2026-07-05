"""Tests for GUI validation helpers."""

from __future__ import annotations

from pathlib import Path

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
    assert output_dir.is_dir()


def test_validate_conversion_form_requires_input_path(tmp_path: Path) -> None:
    errors = validate_conversion_form(
        input_path="",
        output_dir=str(tmp_path / "out"),
        target_format="jpg",
        quality=92,
        resize_width=0,
        resize_height=0,
    )

    assert "Input path is required." in errors


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

    assert f"Input path does not exist: {missing}" in errors


def test_validate_conversion_form_requires_output_folder() -> None:
    errors = validate_conversion_form(
        input_path="input.png",
        output_dir="",
        target_format="jpg",
        quality=92,
        resize_width=0,
        resize_height=0,
    )

    assert "Output folder is required." in errors


def test_validate_conversion_form_reports_output_creation_error(
    tmp_path: Path,
    monkeypatch,
) -> None:
    input_path = tmp_path / "source.png"
    input_path.write_bytes(b"placeholder")

    def raise_os_error(self: Path, *args: object, **kwargs: object) -> None:
        if self == tmp_path / "out":
            raise OSError("permission denied")

    monkeypatch.setattr(Path, "mkdir", raise_os_error)

    errors = validate_conversion_form(
        input_path=str(input_path),
        output_dir=str(tmp_path / "out"),
        target_format="jpg",
        quality=92,
        resize_width=0,
        resize_height=0,
    )

    assert any("Output folder cannot be created:" in error for error in errors)


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

    assert "Unsupported target format: gif" in errors


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

    assert "Quality must be between 1 and 100." in errors


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

    assert "Resize width cannot be negative." in errors
    assert "Resize height cannot be negative." in errors
