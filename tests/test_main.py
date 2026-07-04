"""Tests for the CLI pipeline."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from app import main as cli


def test_main_converts_single_file(tmp_path: Path) -> None:
    input_path = tmp_path / "source.png"
    output_dir = tmp_path / "out"
    Image.new("RGB", (8, 8), (10, 20, 30)).save(input_path)

    exit_code = cli.main(
        [
            "--input",
            str(input_path),
            "--output",
            str(output_dir),
            "--to",
            "jpg",
        ]
    )

    assert exit_code == 0
    output_path = output_dir / "source.jpg"
    assert output_path.exists()
    with Image.open(output_path) as result:
        assert result.format == "JPEG"


def test_main_converts_folder_recursively_with_structure(tmp_path: Path) -> None:
    input_dir = tmp_path / "photos"
    nested_dir = input_dir / "trip"
    nested_dir.mkdir(parents=True)
    Image.new("RGB", (8, 8), (10, 20, 30)).save(input_dir / "top.png")
    Image.new("RGB", (8, 8), (30, 20, 10)).save(nested_dir / "nested.png")
    (nested_dir / "notes.txt").write_text("ignore", encoding="utf-8")

    output_dir = tmp_path / "converted"
    exit_code = cli.main(
        [
            "--input",
            str(input_dir),
            "--output",
            str(output_dir),
            "--to",
            "jpg",
            "--recursive",
            "--keep-structure",
        ]
    )

    assert exit_code == 0
    assert (output_dir / "top.jpg").exists()
    assert (output_dir / "trip" / "nested.jpg").exists()
    assert not (output_dir / "trip" / "notes.jpg").exists()


def test_main_generates_unique_name_without_overwrite(tmp_path: Path) -> None:
    input_path = tmp_path / "source.png"
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    Image.new("RGB", (8, 8), (10, 20, 30)).save(input_path)
    (output_dir / "source.jpg").write_text("existing", encoding="utf-8")

    exit_code = cli.main(
        [
            "--input",
            str(input_path),
            "--output",
            str(output_dir),
            "--to",
            "jpg",
        ]
    )

    assert exit_code == 0
    assert (output_dir / "source_1.jpg").exists()


def test_parse_args_rejects_invalid_quality(tmp_path: Path) -> None:
    input_path = tmp_path / "source.png"
    input_path.write_bytes(b"placeholder")

    with pytest.raises(SystemExit):
        cli.parse_args(
            [
                "--input",
                str(input_path),
                "--output",
                str(tmp_path / "out"),
                "--to",
                "jpg",
                "--quality",
                "101",
            ]
        )


def test_run_conversion_records_raw_to_webp_failure(tmp_path: Path) -> None:
    input_path = tmp_path / "photo.nef"
    output_dir = tmp_path / "out"
    input_path.write_bytes(b"not real raw")
    args = cli.parse_args(
        [
            "--input",
            str(input_path),
            "--output",
            str(output_dir),
            "--to",
            "webp",
        ]
    )

    result = cli.run_conversion(args)

    assert result.total_found == 1
    assert result.converted == 0
    assert result.failed == 1
    assert "Unsupported output format" in result.errors[0].reason


def test_default_logging_shows_found_progress_and_summary(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    input_path = tmp_path / "source.png"
    output_dir = tmp_path / "out"
    Image.new("RGB", (8, 8), (10, 20, 30)).save(input_path)
    args = cli.parse_args(
        [
            "--input",
            str(input_path),
            "--output",
            str(output_dir),
            "--to",
            "jpg",
        ]
    )

    cli.run_conversion(args)

    logs = capsys.readouterr().err
    assert "Found 1 supported file(s)." in logs
    assert "Converted 1/1: source.png" in logs
    assert "Total files found: 1" in logs


def test_verbose_logging_shows_processing_and_output_path(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    input_path = tmp_path / "source.png"
    output_dir = tmp_path / "out"
    Image.new("RGB", (8, 8), (10, 20, 30)).save(input_path)
    args = cli.parse_args(
        [
            "--input",
            str(input_path),
            "--output",
            str(output_dir),
            "--to",
            "jpg",
            "--verbose",
        ]
    )

    cli.run_conversion(args)

    logs = capsys.readouterr().err
    assert f"Processing file 1/1: {input_path}" in logs
    assert f"Output path: {output_dir / 'source.jpg'}" in logs


def test_batch_continues_after_one_bad_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    bad_file = input_dir / "bad.jpg"
    good_file = input_dir / "good.png"
    bad_file.write_text("not an image", encoding="utf-8")
    Image.new("RGB", (8, 8), (10, 20, 30)).save(good_file)
    output_dir = tmp_path / "out"
    args = cli.parse_args(
        [
            "--input",
            str(input_dir),
            "--output",
            str(output_dir),
            "--to",
            "jpg",
            "--verbose",
        ]
    )

    result = cli.run_conversion(args)

    logs = capsys.readouterr().err
    assert result.converted == 1
    assert result.failed == 1
    assert (output_dir / "good.jpg").exists()
    assert "Failed 1/2: bad.jpg" in logs
    assert f"Failure reason for {bad_file}" in logs
