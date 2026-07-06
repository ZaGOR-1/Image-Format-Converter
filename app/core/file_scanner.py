"""File discovery utilities for supported input formats."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from app.core.config import is_supported_input_extension


def scan_files(
    input_path: Path,
    *,
    recursive: bool = False,
    exclude_dirs: Iterable[Path] | None = None,
) -> list[Path]:
    """Return supported input files from a file or directory path."""
    excluded = _resolve_excluded_dirs(exclude_dirs)

    if _safe_is_file(input_path):
        if _is_inside_excluded_dir(input_path, excluded):
            return []
        return [input_path] if is_supported_file(input_path) else []

    if _safe_is_dir(input_path):
        files = _scan_directory(
            input_path,
            recursive=recursive,
            excluded_dirs=excluded,
            visited_dirs=set(),
        )
        return sorted(files, key=_sort_key)

    return []


def is_supported_file(path: Path) -> bool:
    """Return whether path is a readable file with a supported extension."""
    return _safe_is_file(path) and is_supported_input_extension(path.suffix)


def _scan_directory(
    directory: Path,
    *,
    recursive: bool,
    excluded_dirs: set[Path],
    visited_dirs: set[Path],
) -> list[Path]:
    resolved_directory = _safe_resolve(directory)
    if resolved_directory in visited_dirs:
        return []
    visited_dirs.add(resolved_directory)

    files: list[Path] = []

    for child in _iter_directory(directory):
        if _is_inside_excluded_dir(child, excluded_dirs):
            continue

        if is_supported_file(child):
            files.append(child)
            continue

        if recursive and _safe_is_dir(child) and not _safe_is_symlink(child):
            files.extend(
                _scan_directory(
                    child,
                    recursive=True,
                    excluded_dirs=excluded_dirs,
                    visited_dirs=visited_dirs,
                )
            )

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


def _safe_is_symlink(path: Path) -> bool:
    try:
        return path.is_symlink()
    except OSError:
        return False


def _safe_resolve(path: Path) -> Path:
    try:
        return path.resolve(strict=False)
    except OSError:
        return path.absolute()


def _resolve_excluded_dirs(exclude_dirs: Iterable[Path] | None) -> set[Path]:
    if exclude_dirs is None:
        return set()
    return {_safe_resolve(path) for path in exclude_dirs}


def _is_inside_excluded_dir(path: Path, excluded_dirs: set[Path]) -> bool:
    if not excluded_dirs:
        return False

    resolved = _safe_resolve(path)
    for excluded in excluded_dirs:
        if resolved == excluded or _is_relative_to(resolved, excluded):
            return True
    return False


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _sort_key(path: Path) -> str:
    return str(path).lower()
