"""Tests for GUI ConversionOptions mapping."""

from __future__ import annotations

from pathlib import Path

from app.core.conversion_options import ConversionOptions
from app.gui.options_builder import build_conversion_options


def test_build_conversion_options_maps_all_fields() -> None:
    options = build_conversion_options(
        input_path=" D:/Photos ",
        output_dir=" D:/Converted ",
        target_format="JPG",
        quality=88,
        recursive=True,
        overwrite=True,
        keep_structure=True,
        resize_width=1600,
        resize_height=1200,
    )

    assert options == ConversionOptions(
        input_path=Path("D:/Photos"),
        output_dir=Path("D:/Converted"),
        target_format="jpg",
        quality=88,
        recursive=True,
        overwrite=True,
        keep_structure=True,
        resize_width=1600,
        resize_height=1200,
    )


def test_build_conversion_options_maps_zero_resize_to_none() -> None:
    options = build_conversion_options(
        input_path="D:/Photos",
        output_dir="D:/Converted",
        target_format="png",
        quality=92,
        recursive=False,
        overwrite=False,
        keep_structure=False,
        resize_width=0,
        resize_height=0,
    )

    assert options.resize_width is None
    assert options.resize_height is None
    assert options.verbose is False


def test_build_conversion_options_maps_zero_width_to_none_only() -> None:
    options = build_conversion_options(
        input_path="D:/Photos",
        output_dir="D:/Converted",
        target_format="png",
        quality=92,
        recursive=False,
        overwrite=False,
        keep_structure=False,
        resize_width=0,
        resize_height=900,
    )

    assert options.resize_width is None
    assert options.resize_height == 900


def test_build_conversion_options_maps_zero_height_to_none_only() -> None:
    options = build_conversion_options(
        input_path="D:/Photos",
        output_dir="D:/Converted",
        target_format="png",
        quality=92,
        recursive=False,
        overwrite=False,
        keep_structure=False,
        resize_width=1200,
        resize_height=0,
    )

    assert options.resize_width == 1200
    assert options.resize_height is None


def test_build_conversion_options_normalizes_target_format() -> None:
    options = build_conversion_options(
        input_path="D:/Photos",
        output_dir="D:/Converted",
        target_format=" WebP ",
        quality=92,
        recursive=False,
        overwrite=False,
        keep_structure=False,
        resize_width=0,
        resize_height=0,
    )

    assert options.target_format == "webp"


def test_build_conversion_options_maps_checkbox_values() -> None:
    options = build_conversion_options(
        input_path="D:/Photos",
        output_dir="D:/Converted",
        target_format="jpg",
        quality=92,
        recursive=True,
        overwrite=False,
        keep_structure=True,
        resize_width=0,
        resize_height=0,
    )

    assert options.recursive is True
    assert options.overwrite is False
    assert options.keep_structure is True
