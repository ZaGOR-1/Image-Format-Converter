"""Conversion options shared by CLI and future UI layers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.core.config import DEFAULT_QUALITY


@dataclass(frozen=True)
class ConversionOptions:
    """User-selected options for a conversion run."""

    input_path: Path
    output_dir: Path
    target_format: str
    quality: int = DEFAULT_QUALITY
    recursive: bool = False
    overwrite: bool = False
    keep_structure: bool = False
    resize_width: int | None = None
    resize_height: int | None = None
    verbose: bool = False
