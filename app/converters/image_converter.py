"""Regular image converter implementation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image, ImageOps

from app.converters.base import BaseConverter
from app.core.config import (
    DEFAULT_QUALITY,
    REGULAR_IMAGE_OUTPUT_FORMATS,
    is_regular_image_input_extension,
    is_valid_quality,
    normalize_output_format,
)

JPEG_FORMATS = frozenset({"jpg", "jpeg"})
QUALITY_FORMATS = frozenset({"jpg", "jpeg", "webp"})
PIL_SAVE_FORMATS = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
    "tif": "TIFF",
    "tiff": "TIFF",
}


class ImageConverter(BaseConverter):
    """Convert regular image files through Pillow."""

    def supports_input(self, input_path: Path) -> bool:
        """Return whether this converter can read the input file."""
        return is_regular_image_input_extension(input_path.suffix)

    def supported_outputs(self) -> set[str]:
        """Return regular image output formats supported by MVP v1."""
        return set(REGULAR_IMAGE_OUTPUT_FORMATS)

    def convert(
        self,
        input_path: Path,
        output_path: Path,
        options: dict[str, Any],
    ) -> None:
        """Convert a regular image file to the requested output format."""
        output_format = normalize_output_format(output_path.suffix)
        if output_format not in REGULAR_IMAGE_OUTPUT_FORMATS:
            raise ValueError(f"Unsupported output format: {output_path.suffix}")

        quality = _get_quality(options)
        resize_width = _get_optional_positive_int(options, "resize_width")
        resize_height = _get_optional_positive_int(options, "resize_height")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with Image.open(input_path) as image:
            prepared = ImageOps.exif_transpose(image)
            prepared = _resize_image(
                prepared,
                width=resize_width,
                height=resize_height,
            )
            prepared = _prepare_for_output(prepared, output_format)

            save_options: dict[str, Any] = {"format": PIL_SAVE_FORMATS[output_format]}
            if output_format in QUALITY_FORMATS:
                save_options["quality"] = quality

            prepared.save(output_path, **save_options)


def _prepare_for_output(image: Image.Image, output_format: str) -> Image.Image:
    if output_format in JPEG_FORMATS:
        return _to_rgb_with_white_background(image)
    return image


def _to_rgb_with_white_background(image: Image.Image) -> Image.Image:
    if image.mode == "RGB":
        return image

    if image.mode in {"RGBA", "LA"} or "transparency" in image.info:
        rgba = image.convert("RGBA")
        background = Image.new("RGB", rgba.size, (255, 255, 255))
        background.paste(rgba, mask=rgba.getchannel("A"))
        return background

    return image.convert("RGB")


def _resize_image(
    image: Image.Image,
    *,
    width: int | None,
    height: int | None,
) -> Image.Image:
    if width is None and height is None:
        return image

    original_width, original_height = image.size
    target_size = _calculate_target_size(
        original_width,
        original_height,
        width=width,
        height=height,
    )
    if target_size == image.size:
        return image

    return image.resize(target_size, Image.Resampling.LANCZOS)


def _calculate_target_size(
    original_width: int,
    original_height: int,
    *,
    width: int | None,
    height: int | None,
) -> tuple[int, int]:
    if width is not None and height is None:
        ratio = width / original_width
    elif height is not None and width is None:
        ratio = height / original_height
    elif width is not None and height is not None:
        ratio = min(width / original_width, height / original_height)
    else:
        return original_width, original_height

    return (
        max(1, round(original_width * ratio)),
        max(1, round(original_height * ratio)),
    )


def _get_quality(options: dict[str, Any]) -> int:
    value = options.get("quality", DEFAULT_QUALITY)
    quality = DEFAULT_QUALITY if value is None else int(value)
    if not is_valid_quality(quality):
        raise ValueError("quality must be between 1 and 100")
    return quality


def _get_optional_positive_int(options: dict[str, Any], key: str) -> int | None:
    value = options.get(key)
    if value is None:
        return None

    converted = int(value)
    if converted <= 0:
        raise ValueError(f"{key} must be greater than 0")
    return converted
