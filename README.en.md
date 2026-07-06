# Image Format Converter MVP

[Українська](README.md) | [English](README.en.md)

**Image Format Converter** is a local Python 3.12+ application for converting image files. The current MVP supports two entry points:

- CLI through `python -m app.main`;
- a simple PySide6 GUI through `python -m app.gui_main`.

The project focuses on regular image conversion and RAW camera files. Conversion logic is kept in the shared `ConversionService`, so the CLI and GUI use the same pipeline.

This MVP does not include a web server, database, audio/video/document conversion, ready-made EXE build, or installer.

## Features

- Convert a single file or a folder.
- Optional recursive folder scanning.
- Preserve folder structure with `--keep-structure`.
- Safe batch error handling: one bad file does not stop the whole batch.
- Safe unique output names when `--overwrite` is not enabled.
- Resize while preserving aspect ratio.
- GUI controls for input/output, format, quality, resize, recursive, overwrite, progress, and logs.
- GUI supports Ukrainian and English with live language switching.
- Soft batch cancellation through the `Cancel` / `Скасувати` button.
- Lazy `rawpy`: GUI and regular conversion start without a top-level `rawpy` import; RAW conversion reports a clear error if `rawpy` is unavailable.

## Supported Formats

RAW input:

- `.nef`
- `.cr2`
- `.arw`
- `.dng`

RAW output:

- `jpg`
- `jpeg`
- `png`
- `tif`
- `tiff`

RAW to WEBP is not supported in the current MVP.

Regular image input:

- `.jpg`
- `.jpeg`
- `.png`
- `.webp`
- `.tif`
- `.tiff`

Regular image output:

- `jpg`
- `jpeg`
- `png`
- `webp`
- `tif`
- `tiff`

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Dependencies:

- `Pillow` for regular image conversion.
- `rawpy` for RAW camera files.
- `numpy` for RAW image arrays.
- `PySide6` for the GUI.
- `pytest` for tests.

For JPG/PNG/WEBP/TIFF conversion, Pillow is enough. `rawpy` is loaded lazily and is only needed when converting RAW files. If `rawpy` is unavailable, regular conversion still works, while RAW conversion reports:

```text
RAW conversion requires rawpy. Install it with: pip install rawpy
```

## GUI Usage

```bash
python -m app.gui_main
```

In the GUI:

1. Select an input file or input folder.
2. Select an output folder.
3. Choose the target format.
4. Adjust quality, resize, recursive, keep structure, or overwrite options.
5. Press `Convert` / `Конвертувати`.
6. Press `Cancel` / `Скасувати` if needed; the current file finishes, and the rest of the batch is marked as skipped.

GUI conversion runs in a worker thread, so the window should stay responsive during batch conversion. Progress and logs are updated through callbacks from `ConversionService`.

## GUI Localization

The GUI supports Ukrainian and English. Ukrainian is the default language.

The language can be changed directly in the window with the `Українська / English` selector; restarting the GUI is not required. The selected language is persisted between launches with `QSettings`.

GUI labels, buttons, placeholders, validation messages, main status messages, and GUI-generated dialogs/logs are localized. The CLI is not localized yet. Core service logs and `JobResult.summary()` may remain in English in this MVP.

## CLI Examples

Convert a single RAW file to JPG:

```bash
python -m app.main --input "D:/Photos/photo.nef" --output "D:/Converted" --to jpg --quality 92
```

Convert all supported files in a folder:

```bash
python -m app.main --input "D:/Photos" --output "D:/Converted" --to jpg --quality 90
```

Convert recursively and preserve folder structure:

```bash
python -m app.main --input "D:/Photos" --output "D:/Converted" --to png --recursive --keep-structure
```

Convert to WEBP and overwrite existing files:

```bash
python -m app.main --input "D:/Photos" --output "D:/Converted" --to webp --quality 85 --overwrite
```

Resize while preserving aspect ratio:

```bash
python -m app.main --input "D:/Photos" --output "D:/Converted" --to jpg --resize-width 1600
```

Fit inside a box without distortion:

```bash
python -m app.main --input "D:/Photos" --output "D:/Converted" --to jpg --resize-width 1600 --resize-height 1200
```

Enable verbose logs:

```bash
python -m app.main --input "D:/Photos" --output "D:/Converted" --to jpg --verbose
```

## CLI Arguments

| Argument | Description |
| --- | --- |
| `--input` | Path to an input file or folder. Required. |
| `--output` | Output folder. Required. Created automatically when possible. |
| `--to` | Target format: `jpg`, `jpeg`, `png`, `webp`, `tif`, or `tiff`. Required. |
| `--quality` | JPEG/WebP quality from `1` to `100`. Default: `92`. |
| `--recursive` | Scan nested folders when input is a directory. |
| `--overwrite` | Overwrite existing output files. Without this flag, unique names such as `photo_1.jpg` are generated. |
| `--keep-structure` | Preserve input folder structure inside the output directory. Useful with `--recursive`. |
| `--resize-width` | Resize to this width while preserving aspect ratio. |
| `--resize-height` | Resize to this height while preserving aspect ratio. |
| `--verbose` | Show detailed console logs: processing, output paths, and failure reasons. |

## Conversion Behavior

- Regular image conversion uses Pillow.
- RAW conversion uses `rawpy`, imported only during RAW conversion.
- EXIF Orientation is normalized for regular images with `ImageOps.exif_transpose`.
- PNG transparency is flattened onto a white background when saving to JPG/JPEG.
- JPG/JPEG output is saved as `RGB`.
- PNG preserves transparency where possible.
- WEBP supports quality settings.
- TIFF supports `.tif` and `.tiff`.
- A failed file does not stop the whole batch; the final summary lists failed files and reasons.

## MVP Limitations

- The GUI is intentionally simple and focused on local conversion.
- No audio, video, or document conversion yet.
- No web API or web server.
- No database.
- No persisted conversion history or batch queue.
- No ready-made EXE build or installer packaging.
- RAW files are only converted from RAW to regular image formats.
- Conversion back into RAW is not supported.
- RAW to WEBP is not supported.
- EXIF support is limited to orientation normalization for regular images.
- Basic tests do not require real RAW files.

## Development

Run tests:

```bash
python -m pytest
```

CLI help:

```bash
python -m app.main --help
```

Notes for a future Windows EXE build:

```text
docs/packaging.md
```

Core structure:

- `app/converters/base.py` defines `BaseConverter`.
- `app/converters/image_converter.py` implements regular image conversion.
- `app/converters/raw_converter.py` implements RAW conversion.
- `app/converters/registry.py` selects the right converter.
- `app/core/conversion_options.py` defines `ConversionOptions`.
- `app/core/conversion_service.py` contains the shared conversion pipeline.
- `app/core/file_scanner.py` scans input files.
- `app/core/path_utils.py` handles output paths and unique names.
- `app/core/job_result.py` stores batch result summaries.

GUI:

- `app/gui_main.py` starts the PySide6 GUI.
- `app/gui/main_window.py` contains layout, validation flow, and signal wiring.
- `app/gui/conversion_worker.py` runs `ConversionService` outside the UI thread.
- `app/gui/i18n.py` contains dictionary-based GUI localization.
- `app/gui/options_builder.py` maps GUI state into `ConversionOptions`.
- `app/gui/settings.py` persists GUI settings, including the selected language.
- `app/gui/validation.py` validates form values.

To add a new converter later, implement `BaseConverter`, register it in `ConverterRegistry`, and add focused tests.

## Roadmap

- Windows EXE packaging through PyInstaller or another packaging tool.
- More advanced GUI features with PySide6.
- Audio conversion through FFmpeg.
- Presets for web, print, and social media.
- Drag-and-drop.
- Conversion history.
- Batch queue.
- EXIF options.
