"""Core conversion pipeline shared by CLI and future UI layers."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from app.converters.registry import ConverterRegistry
from app.core.conversion_options import ConversionOptions
from app.core.file_scanner import scan_files
from app.core.job_result import JobResult
from app.core.path_utils import build_output_path

ProgressCallback = Callable[[int, int, Path], None]
LogCallback = Callable[[str], None]


class ConversionService:
    """Run batch conversions without depending on a specific UI."""

    def __init__(self, registry: ConverterRegistry | None = None) -> None:
        self.registry = registry or ConverterRegistry.default()

    def run(
        self,
        options: ConversionOptions,
        on_progress: ProgressCallback | None = None,
        on_log: LogCallback | None = None,
    ) -> JobResult:
        """Run a conversion batch and return the aggregate result."""
        input_files = scan_files(options.input_path, recursive=options.recursive)
        result = JobResult(total_found=len(input_files))

        _emit(on_log, f"Found {result.total_found} supported file(s).")

        converter_options = _build_converter_options(options)
        for index, input_file in enumerate(input_files, start=1):
            _emit(
                on_log,
                f"Processing file {index}/{result.total_found}: {input_file}",
            )
            try:
                converter = self.registry.get_converter_for(
                    input_file,
                    options.target_format,
                )
                output_path = build_output_path(
                    input_file,
                    options.output_dir,
                    options.target_format,
                    overwrite=options.overwrite,
                    keep_structure=options.keep_structure,
                    input_root=options.input_path,
                )
                _emit(on_log, f"Output path: {output_path}")
                converter.convert(input_file, output_path, converter_options)
                result.record_success()
                _emit(
                    on_log,
                    f"Converted {index}/{result.total_found}: {input_file.name}",
                )
            except Exception as exc:  # noqa: BLE001 - batch conversion must continue.
                result.record_failure(input_file, str(exc))
                _emit(on_log, f"Failed {index}/{result.total_found}: {input_file.name}")
                _emit(on_log, f"Failure reason for {input_file}: {exc}")
            finally:
                if on_progress is not None:
                    on_progress(index, result.total_found, input_file)

        return result


def _build_converter_options(options: ConversionOptions) -> dict[str, int | None]:
    return {
        "quality": options.quality,
        "resize_width": options.resize_width,
        "resize_height": options.resize_height,
    }


def _emit(on_log: LogCallback | None, message: str) -> None:
    if on_log is not None:
        on_log(message)

