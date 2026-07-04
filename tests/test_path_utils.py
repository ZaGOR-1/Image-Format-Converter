"""Tests for output path utilities."""

from pathlib import Path

import pytest

from app.core.path_utils import (
    build_output_filename,
    build_output_path,
    ensure_unique_path,
    normalize_output_extension,
)


def test_normalize_output_extension_adds_dot_and_lowercases() -> None:
    assert normalize_output_extension("JPG") == ".jpg"
    assert normalize_output_extension(".PNG") == ".png"


def test_normalize_output_extension_rejects_unsupported_format() -> None:
    with pytest.raises(ValueError, match="Unsupported output format"):
        normalize_output_extension("gif")


def test_build_output_filename_replaces_extension() -> None:
    assert build_output_filename(Path("photo.raw.nef"), "jpeg") == "photo.raw.jpeg"


def test_ensure_unique_path_returns_original_when_available(tmp_path: Path) -> None:
    output_path = tmp_path / "photo.jpg"

    assert ensure_unique_path(output_path) == output_path


def test_ensure_unique_path_adds_counter_when_file_exists(tmp_path: Path) -> None:
    (tmp_path / "photo.jpg").write_text("existing", encoding="utf-8")
    (tmp_path / "photo_1.jpg").write_text("existing", encoding="utf-8")

    assert ensure_unique_path(tmp_path / "photo.jpg") == tmp_path / "photo_2.jpg"


def test_build_output_path_uses_unique_name_without_overwrite(
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "input" / "photo.png"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "photo.jpg").write_text("existing", encoding="utf-8")

    output_path = build_output_path(input_path, output_dir, "jpg")

    assert output_path == output_dir / "photo_1.jpg"


def test_build_output_path_allows_existing_name_with_overwrite(
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "input" / "photo.png"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "photo.jpg").write_text("existing", encoding="utf-8")

    output_path = build_output_path(
        input_path,
        output_dir,
        "jpg",
        overwrite=True,
    )

    assert output_path == output_dir / "photo.jpg"


def test_build_output_path_keeps_relative_structure(tmp_path: Path) -> None:
    input_root = tmp_path / "photos"
    input_path = input_root / "trip" / "day1" / "photo.png"
    output_dir = tmp_path / "converted"

    output_path = build_output_path(
        input_path,
        output_dir,
        "webp",
        keep_structure=True,
        input_root=input_root,
    )

    assert output_path == output_dir / "trip" / "day1" / "photo.webp"
    assert output_path.parent.is_dir()


def test_build_output_path_requires_root_for_keep_structure(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="input_root is required"):
        build_output_path(
            tmp_path / "photos" / "photo.png",
            tmp_path / "converted",
            "jpg",
            keep_structure=True,
        )
