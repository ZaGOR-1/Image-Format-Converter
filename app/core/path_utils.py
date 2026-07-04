"""Output path and filename utilities."""

from __future__ import annotations

from pathlib import Path

from app.core.config import is_supported_output_format, normalize_output_format


def normalize_output_extension(output_format: str) -> str:
    """Return a supported output extension with a leading dot."""
    normalized = normalize_output_format(output_format)
    if not is_supported_output_format(normalized):
        raise ValueError(f"Unsupported output format: {output_format}")
    return f".{normalized}"


def build_output_filename(input_path: Path, output_format: str) -> str:
    """Build an output filename from the input stem and target format."""
    return f"{input_path.stem}{normalize_output_extension(output_format)}"


def ensure_unique_path(output_path: Path) -> Path:
    """Return output_path or a numbered variant that does not exist."""
    if not output_path.exists():
        return output_path

    counter = 1
    while True:
        candidate = output_path.with_name(
            f"{output_path.stem}_{counter}{output_path.suffix}"
        )
        if not candidate.exists():
            return candidate
        counter += 1


def build_output_path(
    input_path: Path,
    output_dir: Path,
    output_format: str,
    *,
    overwrite: bool = False,
    keep_structure: bool = False,
    input_root: Path | None = None,
) -> Path:
    """Build the final output path for a conversion job."""
    target_dir = output_dir

    if keep_structure:
        if input_root is None:
            raise ValueError("input_root is required when keep_structure is enabled.")

        root = input_root.parent if input_root.is_file() else input_root
        try:
            relative_parent = input_path.parent.relative_to(root)
        except ValueError as exc:
            raise ValueError(
                "input_path must be inside input_root when keep_structure is enabled."
            ) from exc
        target_dir = output_dir / relative_parent

    target_dir.mkdir(parents=True, exist_ok=True)
    candidate = target_dir / build_output_filename(input_path, output_format)

    if overwrite:
        return candidate
    return ensure_unique_path(candidate)
