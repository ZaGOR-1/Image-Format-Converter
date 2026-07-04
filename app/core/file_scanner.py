"""File discovery utilities for supported input formats."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from app.core.config import is_supported_input_extension


def scan_files(input_path: Path, *, recursive: bool = False) -> list[Path]:
    """Return supported input files from a file or directory path."""
    if _safe_is_file(input_path):
        return [input_path] if is_supported_file(input_path) else []

    if _safe_is_dir(input_path):
        files = _scan_directory(input_path, recursive=recursive)
        return sorted(files, key=_sort_key)

    return []


def is_supported_file(path: Path) -> bool:
    """Return whether path is a readable file with a supported extension."""
    return _safe_is_file(path) and is_supported_input_extension(path.suffix)


def _scan_directory(directory: Path, *, recursive: bool) -> list[Path]:
    files: list[Path] = []

    for child in _iter_directory(directory):
        if is_supported_file(child):
            files.append(child)
            continue

        if recursive and _safe_is_dir(child):
            files.extend(_scan_directory(child, recursive=True))

    return files


def _iter_directory(directory: Path) -> Iterable[Path]:
    try:
        return sorted(directory.iterdir(), key=_sort_key)
    except OSError:
        return []


def _safe_is_file(path: Path) -> bool:
    try:
        return path.is_file()
    except OSError:
        return False


def _safe_is_dir(path: Path) -> bool:
    try:
        return path.is_dir()
    except OSError:
        return False


def _sort_key(path: Path) -> str:
    return str(path).lower()
