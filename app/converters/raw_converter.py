"""RAW image converter implementation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import rawpy
from PIL import Image

from app.converters.base import BaseConverter
from app.converters.image_converter import (
    PIL_SAVE_FORMATS,
    QUALITY_FORMATS,
    _get_optional_positive_int,
    _get_quality,
    _prepare_for_output,
    _resize_image,
)
from app.core.config import (
    RAW_OUTPUT_FORMATS,
    is_raw_input_extension,
    normalize_output_format,
)


class RawConverter(BaseConverter):
    """Convert RAW camera files to regular image formats."""

    def supports_input(self, input_path: Path) -> bool:
        """Return whether this converter can read the input file."""
        return is_raw_input_extension(input_path.suffix)

    def supported_outputs(self) -> set[str]:
        """Return RAW output formats supported by MVP v1."""
        return set(RAW_OUTPUT_FORMATS)

    def convert(
        self,
        input_path: Path,
        output_path: Path,
        options: dict[str, Any],
    ) -> None:
        """Convert a RAW camera file through rawpy and Pillow."""
        output_format = normalize_output_format(output_path.suffix)
        if output_format not in RAW_OUTPUT_FORMATS:
            raise ValueError(
                f"Unsupported RAW output format: {output_path.suffix}. "
                "RAW to WEBP is not supported in MVP v1."
            )

        quality = _get_quality(options)
        resize_width = _get_optional_positive_int(options, "resize_width")
        resize_height = _get_optional_positive_int(options, "resize_height")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with rawpy.imread(str(input_path)) as raw:
            rgb = raw.postprocess(
                use_camera_wb=True,
                no_auto_bright=False,
                output_bps=8,
            )

        image = Image.fromarray(rgb)
        image = _resize_image(image, width=resize_width, height=resize_height)
        image = _prepare_for_output(image, output_format)

        save_options: dict[str, Any] = {"format": PIL_SAVE_FORMATS[output_format]}
        if output_format in QUALITY_FORMATS:
            save_options["quality"] = quality

        image.save(output_path, **save_options)
