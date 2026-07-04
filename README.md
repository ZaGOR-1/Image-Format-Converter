# Image Format Converter MVP

Image Format Converter is a local Python 3.12+ command-line tool for converting image files. MVP v1 focuses on regular image formats and RAW camera files, with a modular converter architecture that can later grow into GUI, audio, video, and document conversion.

This version is intentionally CLI-only. It does not include a GUI, web server, database, or background service.

## Supported Formats

RAW input formats:

- `.nef`
- `.cr2`
- `.arw`
- `.dng`

RAW output formats:

- `jpg`
- `jpeg`
- `png`
- `tif`
- `tiff`

RAW to WEBP is not supported in MVP v1.

Regular image input formats:

- `.jpg`
- `.jpeg`
- `.png`
- `.webp`
- `.tif`
- `.tiff`

Regular image output formats:

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
- `pytest` for tests.

## Usage

Convert a single RAW file to JPG:

```bash
python -m app.main --input "D:/Photos/photo.nef" --output "D:/Converted" --to jpg --quality 92
```

Convert all supported files in a folder:

```bash
python -m app.main --input "D:/Photos" --output "D:/Converted" --to jpg --quality 90
```

Convert a folder recursively and preserve the folder structure:

```bash
python -m app.main --input "D:/Photos" --output "D:/Converted" --to png --recursive --keep-structure
```

Convert regular images to WEBP and overwrite existing files:

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

Enable detailed logs:

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
| `--verbose` | Show detailed file-by-file logs, output paths, and failure reasons. |

## Behavior

- Regular image conversion uses Pillow.
- RAW conversion uses `rawpy`.
- EXIF Orientation is normalized for regular images with `ImageOps.exif_transpose`.
- PNG transparency is flattened onto a white background when saving to JPG/JPEG.
- JPG/JPEG output is saved as `RGB`.
- PNG preserves transparency where possible.
- WEBP supports quality settings.
- TIFF output supports `.tif` and `.tiff`.
- A failed file does not stop the whole batch. The final summary lists failed files and reasons.

## MVP Limitations

- No GUI in MVP v1.
- No audio, video, or document conversion yet.
- No web API or web server.
- No database.
- RAW files are only converted from RAW to regular image formats.
- RAW files are not converted back into RAW.
- RAW to WEBP is rejected in MVP v1.
- Basic unit tests do not require real RAW files.
- EXIF support is limited to orientation normalization for regular images.

## Development

Run tests:

```bash
python -m pytest
```

Run the CLI help:

```bash
python -m app.main --help
```

The project is organized around a shared converter interface:

- `app/converters/base.py` defines `BaseConverter`.
- `app/converters/image_converter.py` implements regular image conversion.
- `app/converters/raw_converter.py` implements RAW conversion.
- `app/converters/registry.py` selects the right converter.
- `app/core/` contains scanning, path handling, config, and job result utilities.

To add a new converter later, implement `BaseConverter`, register it in `ConverterRegistry`, and add focused tests for supported input/output behavior.

## Future Roadmap

- GUI with PySide6.
- Audio conversion through FFmpeg.
- Presets for web, print, and social media.
- Drag-and-drop.
- Conversion history.
- Batch queue.
- EXIF options.
