"""Tests for supported file scanning."""

from pathlib import Path

import pytest

from app.core.file_scanner import is_supported_file, scan_files


def test_scan_single_supported_file(tmp_path: Path) -> None:
    image = tmp_path / "photo.JPG"
    image.write_bytes(b"not a real image yet")

    assert scan_files(image) == [image]


def test_scan_single_unsupported_file_returns_empty_list(tmp_path: Path) -> None:
    text_file = tmp_path / "notes.txt"
    text_file.write_text("ignore me", encoding="utf-8")

    assert scan_files(text_file) == []


def test_scan_directory_filters_unsupported_files(tmp_path: Path) -> None:
    jpg = tmp_path / "photo.jpg"
    png = tmp_path / "diagram.png"
    raw = tmp_path / "camera.NEF"
    unsupported = tmp_path / "notes.txt"
    for path in (jpg, png, raw, unsupported):
        path.write_bytes(b"placeholder")

    assert scan_files(tmp_path) == [raw, png, jpg]


def test_scan_directory_is_not_recursive_by_default(tmp_path: Path) -> None:
    top_level = tmp_path / "top.webp"
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()
    nested = nested_dir / "nested.jpg"
    top_level.write_bytes(b"placeholder")
    nested.write_bytes(b"placeholder")

    assert scan_files(tmp_path) == [top_level]


def test_scan_directory_recursively_includes_nested_files(tmp_path: Path) -> None:
    top_level = tmp_path / "top.webp"
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()
    nested = nested_dir / "nested.jpg"
    top_level.write_bytes(b"placeholder")
    nested.write_bytes(b"placeholder")

    assert scan_files(tmp_path, recursive=True) == [nested, top_level]


def test_scan_directory_excludes_requested_output_tree(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    output_dir = tmp_path / "out"
    output_file = output_dir / "old.png"
    output_dir.mkdir()
    source.write_bytes(b"placeholder")
    output_file.write_bytes(b"placeholder")

    assert scan_files(tmp_path, recursive=True, exclude_dirs=[output_dir]) == [source]


def test_scan_directory_does_not_follow_symlink_directories(tmp_path: Path) -> None:
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    nested = target_dir / "nested.jpg"
    nested.write_bytes(b"placeholder")
    link_dir = tmp_path / "link"
    try:
        link_dir.symlink_to(target_dir, target_is_directory=True)
    except OSError:
        pytest.skip("Directory symlinks are not available in this environment.")

    assert scan_files(tmp_path, recursive=True) == [nested]


def test_scan_directory_returns_empty_list_when_iterdir_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_iterdir = Path.iterdir

    def raise_os_error(directory: Path):
        if directory == tmp_path:
            raise OSError(f"Cannot read {directory}")
        return original_iterdir(directory)

    monkeypatch.setattr(Path, "iterdir", raise_os_error)

    assert scan_files(tmp_path) == []


def test_is_supported_file_uses_supported_extensions(tmp_path: Path) -> None:
    supported = tmp_path / "image.tiff"
    unsupported = tmp_path / "image.gif"
    supported.write_bytes(b"placeholder")
    unsupported.write_bytes(b"placeholder")

    assert is_supported_file(supported) is True
    assert is_supported_file(unsupported) is False
