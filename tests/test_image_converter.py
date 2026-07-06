"""Tests for regular image conversion."""

from pathlib import Path

import pytest
from PIL import Image

from app.converters.image_converter import ImageConverter


def test_supports_regular_image_inputs() -> None:
    converter = ImageConverter()

    assert converter.supports_input(Path("photo.JPG")) is True
    assert converter.supports_input(Path("photo.png")) is True
    assert converter.supports_input(Path("photo.nef")) is False


def test_supported_outputs_include_regular_image_formats() -> None:
    assert ImageConverter().supported_outputs() == {
        "jpg",
        "jpeg",
        "png",
        "webp",
        "tif",
        "tiff",
    }


def test_png_with_alpha_converts_to_rgb_jpg(tmp_path: Path) -> None:
    input_path = tmp_path / "transparent.png"
    output_path = tmp_path / "converted.jpg"
    image = Image.new("RGBA", (8, 8), (255, 0, 0, 128))
    image.save(input_path)

    ImageConverter().convert(input_path, output_path, {"quality": 92})

    assert output_path.exists()
    with Image.open(output_path) as result:
        assert result.mode == "RGB"
        assert result.format == "JPEG"


def test_output_extension_controls_saved_format(tmp_path: Path) -> None:
    input_path = tmp_path / "source.jpg"
    output_path = tmp_path / "converted.png"
    Image.new("RGB", (5, 5), (10, 20, 30)).save(input_path)

    ImageConverter().convert(input_path, output_path, {})

    with Image.open(output_path) as result:
        assert result.format == "PNG"


def test_exif_orientation_is_normalized(tmp_path: Path) -> None:
    input_path = tmp_path / "oriented.jpg"
    output_path = tmp_path / "converted.png"
    exif = Image.Exif()
    exif[274] = 6
    Image.new("RGB", (10, 20), (10, 20, 30)).save(input_path, exif=exif)

    ImageConverter().convert(input_path, output_path, {})

    with Image.open(output_path) as result:
        assert result.size == (20, 10)


def test_resize_width_preserves_aspect_ratio(tmp_path: Path) -> None:
    input_path = tmp_path / "source.png"
    output_path = tmp_path / "resized.jpg"
    Image.new("RGB", (100, 50), (10, 20, 30)).save(input_path)

    ImageConverter().convert(input_path, output_path, {"resize_width": 20})

    with Image.open(output_path) as result:
        assert result.size == (20, 10)


def test_resize_height_preserves_aspect_ratio(tmp_path: Path) -> None:
    input_path = tmp_path / "source.png"
    output_path = tmp_path / "resized.jpg"
    Image.new("RGB", (100, 50), (10, 20, 30)).save(input_path)

    ImageConverter().convert(input_path, output_path, {"resize_height": 25})

    with Image.open(output_path) as result:
        assert result.size == (50, 25)


def test_resize_box_fits_inside_bounds(tmp_path: Path) -> None:
    input_path = tmp_path / "source.png"
    output_path = tmp_path / "resized.jpg"
    Image.new("RGB", (100, 50), (10, 20, 30)).save(input_path)

    ImageConverter().convert(
        input_path,
        output_path,
        {"resize_width": 40, "resize_height": 40},
    )

    with Image.open(output_path) as result:
        assert result.size == (40, 20)


def test_invalid_quality_is_rejected(tmp_path: Path) -> None:
    input_path = tmp_path / "source.png"
    output_path = tmp_path / "converted.jpg"
    Image.new("RGB", (5, 5), (10, 20, 30)).save(input_path)

    with pytest.raises(ValueError, match="quality must be between 1 and 100"):
        ImageConverter().convert(input_path, output_path, {"quality": 101})


def test_decompression_bomb_error_is_reported_clearly(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_path = tmp_path / "huge.png"
    output_path = tmp_path / "converted.jpg"
    Image.new("RGB", (2, 2), (10, 20, 30)).save(input_path)
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 1)

    with pytest.raises(ValueError, match="too large or potentially unsafe"):
        ImageConverter().convert(input_path, output_path, {})
