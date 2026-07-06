"""Tests for the PySide6 conversion worker."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app.core.conversion_options import ConversionOptions
from app.core.job_result import JobResult
from app.gui.conversion_worker import ConversionWorker


def _qt_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class FakeService:
    def __init__(self, result: JobResult | None = None) -> None:
        self.result = result or JobResult(total_found=1, converted=1)
        self.calls: list[ConversionOptions] = []

    def run(  # noqa: ANN001, ANN201
        self,
        options,
        on_progress=None,
        on_log=None,
        should_cancel=None,
    ):
        self.calls.append(options)
        assert should_cancel is not None
        assert should_cancel() is False
        if on_log is not None:
            on_log("Found 1 supported file(s).")
        if on_progress is not None:
            on_progress(1, 1, Path("photo.png"))
        return self.result


class FailingService:
    def run(  # noqa: ANN001, ANN201
        self,
        options,
        on_progress=None,
        on_log=None,
        should_cancel=None,
    ):
        raise RuntimeError("service exploded")


def test_conversion_worker_emits_progress_log_and_finished() -> None:
    _qt_app()
    options = ConversionOptions(
        input_path=Path("input.png"),
        output_dir=Path("out"),
        target_format="jpg",
    )
    service = FakeService()
    worker = ConversionWorker(service, options)
    progress: list[tuple[int, int, str]] = []
    messages: list[str] = []
    finished: list[JobResult] = []
    failures: list[str] = []
    worker.progress_changed.connect(
        lambda current, total, path: progress.append((current, total, path))
    )
    worker.log_message.connect(messages.append)
    worker.finished.connect(finished.append)
    worker.failed.connect(failures.append)

    worker.run()

    assert service.calls == [options]
    assert progress == [(1, 1, "photo.png")]
    assert messages == ["Found 1 supported file(s)."]
    assert finished == [service.result]
    assert failures == []


def test_conversion_worker_emits_failed_for_unexpected_exception() -> None:
    _qt_app()
    options = ConversionOptions(
        input_path=Path("input.png"),
        output_dir=Path("out"),
        target_format="jpg",
    )
    worker = ConversionWorker(FailingService(), options)
    failures: list[str] = []
    finished: list[JobResult] = []
    worker.failed.connect(failures.append)
    worker.finished.connect(finished.append)

    worker.run()

    assert failures == ["service exploded"]
    assert finished == []


def test_conversion_worker_cancel_request_sets_cancel_state() -> None:
    _qt_app()
    options = ConversionOptions(
        input_path=Path("input.png"),
        output_dir=Path("out"),
        target_format="jpg",
    )
    worker = ConversionWorker(FakeService(), options)
    worker.request_cancel()

    assert worker.is_cancel_requested() is True
