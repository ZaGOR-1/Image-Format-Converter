"""Tests for RAW image conversion without real RAW fixtures."""

from pathlib import Path
from typing import Any

import numpy as np
import pytest
from PIL import Image

from app.converters import raw_converter
from app.converters.raw_converter import RawConverter


class FakeRaw:
    def __init__(self) -> None:
        self.postprocess_kwargs: dict[str, Any] | None = None

    def __enter__(self) -> "FakeRaw":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def postprocess(self, **kwargs: Any) -> np.ndarray:
        self.postprocess_kwargs = kwargs
        return np.full((10, 20, 3), 127, dtype=np.uint8)


def test_supports_raw_inputs_only() -> None:
    converter = RawConverter()

    assert converter.supports_input(Path("photo.NEF")) is True
    assert converter.supports_input(Path("photo.dng")) is True
    assert converter.supports_input(Path("photo.jpg")) is False


def test_supported_outputs_reject_webp() -> None:
    assert RawConverter().supported_outputs() == {
        "jpg",
        "jpeg",
        "png",
        "tif",
        "tiff",
    }


def test_convert_raw_to_jpg_uses_rawpy_postprocess(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_raw = FakeRaw()

    def fake_imread(path: str) -> FakeRaw:
        assert path == str(tmp_path / "photo.nef")
        return fake_raw

    monkeypatch.setattr(raw_converter.rawpy, "imread", fake_imread)

    input_path = tmp_path / "photo.nef"
    output_path = tmp_path / "photo.jpg"

    RawConverter().convert(
        input_path,
        output_path,
        {"quality": 90, "resize_width": 10},
    )

    assert fake_raw.postprocess_kwargs == {
        "use_camera_wb": True,
        "no_auto_bright": False,
        "output_bps": 8,
    }
    with Image.open(output_path) as result:
        assert result.format == "JPEG"
        assert result.mode == "RGB"
        assert result.size == (10, 5)


def test_raw_to_webp_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="RAW to WEBP is not supported"):
        RawConverter().convert(tmp_path / "photo.nef", tmp_path / "photo.webp", {})
