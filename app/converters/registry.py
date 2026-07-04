"""Converter registry."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from app.converters.base import BaseConverter
from app.converters.image_converter import ImageConverter
from app.converters.raw_converter import RawConverter
from app.core.config import normalize_output_format


class ConverterRegistry:
    """Select the correct converter for an input file and output format."""

    def __init__(self, converters: Sequence[BaseConverter] | None = None) -> None:
        self._converters = list(converters) if converters is not None else [
            ImageConverter(),
            RawConverter(),
        ]

    def get_converter(self, input_path: Path) -> BaseConverter:
        """Return the first converter that supports input_path."""
        for converter in self._converters:
            if converter.supports_input(input_path):
                return converter

        raise ValueError(f"Unsupported input format: {input_path.suffix}")

    def get_converter_for(self, input_path: Path, output_format: str) -> BaseConverter:
        """Return a converter after validating the requested output format."""
        converter = self.get_converter(input_path)
        normalized_output = normalize_output_format(output_format)

        if normalized_output not in converter.supported_outputs():
            raise ValueError(
                f"Unsupported output format for {input_path.suffix}: "
                f"{output_format}"
            )

        return converter
