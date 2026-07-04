"""CLI entry point for Image Format Converter MVP."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Sequence

from app.converters.registry import ConverterRegistry
from app.core.config import (
    DEFAULT_QUALITY,
    MAX_QUALITY,
    MIN_QUALITY,
    SUPPORTED_OUTPUT_FORMATS,
    is_supported_output_format,
    is_valid_quality,
    normalize_output_format,
)
from app.core.file_scanner import scan_files
from app.core.job_result import JobResult
from app.core.path_utils import build_output_path

LOGGER = logging.getLogger(__name__)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Convert RAW and regular image formats locally.",
    )
    parser.add_argument("--input", required=True, type=Path, help="Input file or folder.")
    parser.add_argument("--output", required=True, type=Path, help="Output folder.")
    parser.add_argument(
        "--to",
        required=True,
        type=normalize_output_format,
        choices=sorted(SUPPORTED_OUTPUT_FORMATS),
        help="Target format.",
    )
    parser.add_argument(
        "--quality",
        type=_quality_arg,
        default=DEFAULT_QUALITY,
        help=f"JPEG/WebP quality from {MIN_QUALITY} to {MAX_QUALITY}.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Scan folders recursively.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files.",
    )
    parser.add_argument(
        "--keep-structure",
        action="store_true",
        help="Preserve input folder structure inside the output folder.",
    )
    parser.add_argument(
        "--resize-width",
        type=_positive_int_arg,
        help="Resize to this width while preserving aspect ratio.",
    )
    parser.add_argument(
        "--resize-height",
        type=_positive_int_arg,
        help="Resize to this height while preserving aspect ratio.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed console logs.",
    )

    args = parser.parse_args(argv)
    validate_args(args, parser)
    return args


def validate_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    """Validate arguments that need filesystem checks."""
    if not args.input.exists():
        parser.error(f"input path does not exist: {args.input}")

    if not is_supported_output_format(args.to):
        parser.error(f"unsupported output format: {args.to}")

    try:
        args.output.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        parser.error(f"output directory cannot be created: {exc}")


def run_conversion(args: argparse.Namespace) -> JobResult:
    """Run the conversion pipeline and return the batch result."""
    setup_logging(args.verbose)

    input_files = scan_files(args.input, recursive=args.recursive)
    result = JobResult(total_found=len(input_files))
    registry = ConverterRegistry()
    options = _build_converter_options(args)

    LOGGER.info("Found %s supported file(s).", result.total_found)

    for index, input_file in enumerate(input_files, start=1):
        LOGGER.debug("Processing file %s/%s: %s", index, result.total_found, input_file)
        try:
            converter = registry.get_converter_for(input_file, args.to)
            output_path = build_output_path(
                input_file,
                args.output,
                args.to,
                overwrite=args.overwrite,
                keep_structure=args.keep_structure,
                input_root=args.input,
            )
            LOGGER.debug("Output path: %s", output_path)
            converter.convert(input_file, output_path, options)
            result.record_success()
            LOGGER.info(
                "Converted %s/%s: %s",
                index,
                result.total_found,
                input_file.name,
            )
        except Exception as exc:  # noqa: BLE001 - batch conversion must continue.
            result.record_failure(input_file, str(exc))
            LOGGER.warning(
                "Failed %s/%s: %s",
                index,
                result.total_found,
                input_file.name,
            )
            LOGGER.debug("Failure reason for %s: %s", input_file, exc)

    LOGGER.info(result.summary())
    return result


def setup_logging(verbose: bool) -> None:
    """Configure console logging for CLI execution."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(message)s", force=True)
    logging.getLogger("PIL").setLevel(logging.WARNING)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    args = parse_args(argv)
    result = run_conversion(args)
    return 1 if result.has_failures else 0


def _build_converter_options(args: argparse.Namespace) -> dict[str, int | None]:
    return {
        "quality": args.quality,
        "resize_width": args.resize_width,
        "resize_height": args.resize_height,
    }


def _quality_arg(value: str) -> int:
    quality = int(value)
    if not is_valid_quality(quality):
        raise argparse.ArgumentTypeError(
            f"quality must be between {MIN_QUALITY} and {MAX_QUALITY}"
        )
    return quality


def _positive_int_arg(value: str) -> int:
    converted = int(value)
    if converted <= 0:
        raise argparse.ArgumentTypeError("value must be greater than 0")
    return converted


if __name__ == "__main__":
    raise SystemExit(main())
