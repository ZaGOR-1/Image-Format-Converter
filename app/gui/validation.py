"""Validation helpers for GUI conversion form values."""

from __future__ import annotations

from pathlib import Path

from app.core.config import is_supported_output_format, is_valid_quality
from app.gui.i18n import DEFAULT_LANGUAGE, translate


def validate_conversion_form(
    *,
    input_path: str,
    output_dir: str,
    target_format: str,
    quality: int,
    resize_width: int,
    resize_height: int,
    language: str = DEFAULT_LANGUAGE,
) -> list[str]:
    """Return validation error messages for GUI form values."""
    errors: list[str] = []
    cleaned_input = input_path.strip()
    cleaned_output = output_dir.strip()
    cleaned_target = target_format.strip().lower()

    if not cleaned_input:
        errors.append(translate(language, "validation.input_required"))
    elif not Path(cleaned_input).exists():
        errors.append(
            translate(language, "validation.input_missing").format(
                path=cleaned_input,
            )
        )

    if not cleaned_output:
        errors.append(translate(language, "validation.output_required"))
    else:
        output_path = Path(cleaned_output)
        if output_path.exists() and not output_path.is_dir():
            errors.append(
                translate(language, "validation.output_not_folder").format(
                    path=cleaned_output,
                )
            )
        elif not output_path.exists() and not _has_existing_parent(output_path):
            errors.append(
                translate(language, "validation.output_parent_missing").format(
                    path=cleaned_output,
                )
            )

    if not cleaned_target:
        errors.append(translate(language, "validation.target_required"))
    elif not is_supported_output_format(cleaned_target):
        errors.append(
            translate(language, "validation.target_unsupported").format(
                format=target_format,
            )
        )

    if not is_valid_quality(quality):
        errors.append(translate(language, "validation.quality_invalid"))

    if resize_width < 0:
        errors.append(translate(language, "validation.resize_width_negative"))

    if resize_height < 0:
        errors.append(translate(language, "validation.resize_height_negative"))

    return errors


def _has_existing_parent(path: Path) -> bool:
    parent = path.parent
    while not parent.exists() and parent != parent.parent:
        parent = parent.parent
    return parent.exists() and parent.is_dir()
