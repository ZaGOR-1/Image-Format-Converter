"""Validation helpers for GUI conversion form values."""

from __future__ import annotations

from pathlib import Path

from app.core.config import is_supported_output_format, is_valid_quality


def validate_conversion_form(
    *,
    input_path: str,
    output_dir: str,
    target_format: str,
    quality: int,
    resize_width: int,
    resize_height: int,
) -> list[str]:
    """Return validation error messages for GUI form values."""
    errors: list[str] = []
    cleaned_input = input_path.strip()
    cleaned_output = output_dir.strip()
    cleaned_target = target_format.strip().lower()

    if not cleaned_input:
        errors.append("Input path is required.")
    elif not Path(cleaned_input).exists():
        errors.append(f"Input path does not exist: {cleaned_input}")

    if not cleaned_output:
        errors.append("Output folder is required.")
    else:
        try:
            Path(cleaned_output).mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            errors.append(f"Output folder cannot be created: {exc}")

    if not cleaned_target:
        errors.append("Target format is required.")
    elif not is_supported_output_format(cleaned_target):
        errors.append(f"Unsupported target format: {target_format}")

    if not is_valid_quality(quality):
        errors.append("Quality must be between 1 and 100.")

    if resize_width < 0:
        errors.append("Resize width cannot be negative.")

    if resize_height < 0:
        errors.append("Resize height cannot be negative.")

    return errors
