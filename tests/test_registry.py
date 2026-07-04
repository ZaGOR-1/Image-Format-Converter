"""Tests for converter registry selection."""

from pathlib import Path

import pytest

from app.converters.image_converter import ImageConverter
from app.converters.raw_converter import RawConverter
from app.converters.registry import ConverterRegistry


def test_registry_selects_image_converter_for_regular_images() -> None:
    converter = ConverterRegistry().get_converter(Path("photo.jpg"))

    assert isinstance(converter, ImageConverter)


def test_registry_selects_raw_converter_for_raw_images() -> None:
    converter = ConverterRegistry().get_converter(Path("photo.nef"))

    assert isinstance(converter, RawConverter)


def test_registry_rejects_unsupported_input() -> None:
    with pytest.raises(ValueError, match="Unsupported input format"):
        ConverterRegistry().get_converter(Path("notes.txt"))


def test_registry_validates_supported_output_for_converter() -> None:
    converter = ConverterRegistry().get_converter_for(Path("photo.png"), "webp")

    assert isinstance(converter, ImageConverter)


def test_registry_rejects_raw_to_webp() -> None:
    with pytest.raises(ValueError, match="Unsupported output format"):
        ConverterRegistry().get_converter_for(Path("photo.nef"), "webp")


def test_registry_normalizes_output_format() -> None:
    converter = ConverterRegistry().get_converter_for(Path("photo.nef"), ".JPG")

    assert isinstance(converter, RawConverter)
