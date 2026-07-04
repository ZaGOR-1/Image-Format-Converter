"""Shared configuration constants for the converter MVP."""

from __future__ import annotations

RAW_INPUT_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".nef",
        ".cr2",
        ".arw",
        ".dng",
    }
)

REGULAR_IMAGE_INPUT_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".tif",
        ".tiff",
    }
)

REGULAR_IMAGE_OUTPUT_FORMATS: frozenset[str] = frozenset(
    {
        "jpg",
        "jpeg",
        "png",
        "webp",
        "tif",
        "tiff",
    }
)

RAW_OUTPUT_FORMATS: frozenset[str] = frozenset(
    {
        "jpg",
        "jpeg",
        "png",
        "tif",
        "tiff",
    }
)

SUPPORTED_INPUT_EXTENSIONS: frozenset[str] = frozenset(
    RAW_INPUT_EXTENSIONS | REGULAR_IMAGE_INPUT_EXTENSIONS
)

SUPPORTED_OUTPUT_FORMATS: frozenset[str] = frozenset(
    REGULAR_IMAGE_OUTPUT_FORMATS | RAW_OUTPUT_FORMATS
)

DEFAULT_QUALITY = 92
MIN_QUALITY = 1
MAX_QUALITY = 100


def normalize_extension(extension: str) -> str:
    """Return a lowercase file extension with a leading dot."""
    cleaned = extension.strip().lower()
    if not cleaned:
        return cleaned
    return cleaned if cleaned.startswith(".") else f".{cleaned}"


def normalize_output_format(output_format: str) -> str:
    """Return a lowercase output format without a leading dot."""
    return output_format.strip().lower().lstrip(".")


def is_supported_input_extension(extension: str) -> bool:
    """Check whether a file extension is supported as input."""
    return normalize_extension(extension) in SUPPORTED_INPUT_EXTENSIONS


def is_raw_input_extension(extension: str) -> bool:
    """Check whether a file extension is a supported RAW input."""
    return normalize_extension(extension) in RAW_INPUT_EXTENSIONS


def is_regular_image_input_extension(extension: str) -> bool:
    """Check whether a file extension is a supported regular image input."""
    return normalize_extension(extension) in REGULAR_IMAGE_INPUT_EXTENSIONS


def is_supported_output_format(output_format: str) -> bool:
    """Check whether an output format is supported by any MVP converter."""
    return normalize_output_format(output_format) in SUPPORTED_OUTPUT_FORMATS


def is_valid_quality(quality: int) -> bool:
    """Check whether quality is inside the allowed CLI range."""
    return MIN_QUALITY <= quality <= MAX_QUALITY
