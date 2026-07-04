"""Base converter interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseConverter(ABC):
    """Common contract for all converter implementations."""

    @abstractmethod
    def supports_input(self, input_path: Path) -> bool:
        """Return whether this converter can read the input file."""

    @abstractmethod
    def supported_outputs(self) -> set[str]:
        """Return output formats supported by this converter."""

    @abstractmethod
    def convert(
        self,
        input_path: Path,
        output_path: Path,
        options: dict[str, Any],
    ) -> None:
        """Convert input_path into output_path using converter options."""
