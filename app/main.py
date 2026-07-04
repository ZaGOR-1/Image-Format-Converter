"""CLI entry point for Image Format Converter MVP."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Sequence

from app.core.config import (
    DEFAULT_QUALITY,
    MAX_QUALITY,
    MIN_QUALITY,
    SUPPORTED_OUTPUT_FORMATS,
    is_supported_output_format,
    is_valid_quality,
    normalize_output_format,
)
from app.core.conversion_options import ConversionOptions
from app.core.conversion_service import ConversionService
from app.core.job_result import JobResult

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

    options = build_conversion_options(args)
    service = ConversionService()
    result = service.run(options, on_log=_log_service_message)

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


def build_conversion_options(args: argparse.Namespace) -> ConversionOptions:
    """Create service options from parsed CLI arguments."""
    return ConversionOptions(
        input_path=args.input,
        output_dir=args.output,
        target_format=args.to,
        quality=args.quality,
        recursive=args.recursive,
        overwrite=args.overwrite,
        keep_structure=args.keep_structure,
        resize_width=args.resize_width,
        resize_height=args.resize_height,
        verbose=args.verbose,
    )


def _log_service_message(message: str) -> None:
    if message.startswith("Failed "):
        LOGGER.warning(message)
    elif message.startswith("Processing file ") or message.startswith(
        "Output path: "
    ) or message.startswith("Failure reason for "):
        LOGGER.debug(message)
    else:
        LOGGER.info(message)


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
