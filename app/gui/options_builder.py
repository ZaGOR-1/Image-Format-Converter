"""Build ConversionOptions from GUI form values."""

from __future__ import annotations

from pathlib import Path

from app.core.conversion_options import ConversionOptions


def build_conversion_options(
    *,
    input_path: str,
    output_dir: str,
    target_format: str,
    quality: int,
    recursive: bool,
    overwrite: bool,
    keep_structure: bool,
    resize_width: int,
    resize_height: int,
) -> ConversionOptions:
    """Build core conversion options from raw GUI field values."""
    return ConversionOptions(
        input_path=Path(input_path.strip()),
        output_dir=Path(output_dir.strip()),
        target_format=target_format.strip().lower(),
        quality=quality,
        recursive=recursive,
        overwrite=overwrite,
        keep_structure=keep_structure,
        resize_width=resize_width if resize_width > 0 else None,
        resize_height=resize_height if resize_height > 0 else None,
    )
