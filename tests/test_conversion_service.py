"""Tests for the shared conversion service."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from app.core.conversion_options import ConversionOptions
from app.core.conversion_service import ConversionService
from app.core.job_result import JobResult


def test_conversion_service_processes_single_file(tmp_path: Path) -> None:
    input_path = tmp_path / "source.png"
    output_dir = tmp_path / "out"
    Image.new("RGB", (8, 8), (10, 20, 30)).save(input_path)

    result = ConversionService().run(
        ConversionOptions(
            input_path=input_path,
            output_dir=output_dir,
            target_format="jpg",
        )
    )

    assert isinstance(result, JobResult)
    assert result.total_found == 1
    assert result.converted == 1
    assert result.failed == 0
    assert (output_dir / "source.jpg").exists()


def test_conversion_service_continues_batch_after_failure(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    bad_file = input_dir / "bad.jpg"
    good_file = input_dir / "good.png"
    bad_file.write_text("not an image", encoding="utf-8")
    Image.new("RGB", (8, 8), (10, 20, 30)).save(good_file)
    output_dir = tmp_path / "out"

    result = ConversionService().run(
        ConversionOptions(
            input_path=input_dir,
            output_dir=output_dir,
            target_format="jpg",
        )
    )

    assert result.total_found == 2
    assert result.converted == 1
    assert result.failed == 1
    assert (output_dir / "good.jpg").exists()


def test_conversion_service_calls_progress_callback(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    Image.new("RGB", (8, 8), (10, 20, 30)).save(input_dir / "a.png")
    Image.new("RGB", (8, 8), (30, 20, 10)).save(input_dir / "b.png")
    calls: list[tuple[int, int, Path]] = []

    ConversionService().run(
        ConversionOptions(
            input_path=input_dir,
            output_dir=tmp_path / "out",
            target_format="jpg",
        ),
        on_progress=lambda index, total, path: calls.append((index, total, path)),
    )

    assert calls == [
        (1, 2, input_dir / "a.png"),
        (2, 2, input_dir / "b.png"),
    ]


def test_conversion_service_emits_log_messages(tmp_path: Path) -> None:
    input_path = tmp_path / "source.png"
    Image.new("RGB", (8, 8), (10, 20, 30)).save(input_path)
    messages: list[str] = []

    result = ConversionService().run(
        ConversionOptions(
            input_path=input_path,
            output_dir=tmp_path / "out",
            target_format="jpg",
            verbose=True,
        ),
        on_log=messages.append,
    )

    assert result.converted == 1
    assert "Found 1 supported file(s)." in messages
    assert any(message.startswith("Processing file 1/1:") for message in messages)
    assert any(message.startswith("Output path:") for message in messages)
    assert "Converted 1/1: source.png" in messages
