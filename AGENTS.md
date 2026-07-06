# AGENTS.md

## Project: Image Format Converter MVP

You are working on a Python image conversion MVP project called **Image Format Converter**.

The goal is to build a clean, maintainable, local tool for converting image formats. The current MVP includes the original CLI plus a simple PySide6 GUI on top of the same conversion core. The architecture must be prepared for future expansion to audio, video, and document converters.

Do not add web server functionality.
Do not add a database.
Do not overcomplicate the project.

---

## Main Goal

Build a Python 3.12+ CLI and GUI application that can:

* Convert RAW camera files to common image formats.
* Convert common image formats between each other.
* Process either a single file or a folder.
* Support optional recursive folder scanning.
* Preserve folder structure when requested.
* Handle errors safely without crashing the whole batch.
* Be structured in a modular way so future converters can be added.
* Provide a simple MVP v2 GUI that reuses the existing conversion core.

---

## Supported Input Formats

### RAW formats

The app must support reading:

* `.nef`
* `.cr2`
* `.arw`
* `.dng`

RAW files are only converted **from RAW to normal image formats**.

Do not implement conversion back into RAW.

Allowed RAW output formats:

* `.jpg`
* `.jpeg`
* `.png`
* `.tif`
* `.tiff`

RAW to WEBP is not supported in the current MVP.

### Regular image formats

The app must support reading:

* `.jpg`
* `.jpeg`
* `.png`
* `.webp`
* `.tif`
* `.tiff`

Allowed regular image output formats:

* `.jpg`
* `.jpeg`
* `.png`
* `.webp`
* `.tif`
* `.tiff`

---

## Technology Stack

Use:

* Python 3.12+
* `Pillow` for regular image conversion
* `rawpy` for RAW image processing
* `numpy` if needed for RAW image arrays
* `argparse` for CLI arguments
* `pathlib` for paths
* `logging` for logs
* `pytest` for tests
* `PySide6` for the MVP v2 GUI

Do not use:

* GUI frameworks other than `PySide6` in MVP v2
* Flask, FastAPI, Django, or any web framework
* Database engines
* Heavy unnecessary dependencies
* Audio/video libraries yet, except placeholder architecture if needed

---

## Required Project Structure

Use this structure directly in the current project root (`D:\work\Image Format Converter`).
Do not create an extra nested `image_converter_mvp/` directory inside this repository.

```text
app/
  __init__.py
  main.py
  gui_main.py
  core/
    __init__.py
    config.py
    conversion_options.py
    conversion_service.py
    file_scanner.py
    job_result.py
    path_utils.py
  converters/
    __init__.py
    base.py
    image_converter.py
    raw_converter.py
    registry.py
  gui/
    __init__.py
    i18n.py
    main_window.py
    conversion_worker.py
    options_builder.py
    settings.py
    validation.py
tests/
  test_path_utils.py
  test_file_scanner.py
  test_image_converter.py
requirements.txt
README.md
.gitignore
```

Keep code separated by responsibility.

Do not place all logic inside `main.py`.

---

## MVP v2 GUI Requirements

The GUI must be runnable like this:

```bash
python -m app.gui_main
```

GUI rules:

* GUI must use `ConversionService`.
* GUI must build `ConversionOptions` from form state.
* GUI must not duplicate conversion pipeline logic from CLI/core.
* GUI must not call converters directly from UI code.
* GUI must not block the UI thread during conversion.
* Conversion must run through a worker object in a `QThread`.
* GUI progress and logs must be updated through worker/service callbacks.
* CLI must remain working and compatible with existing commands.
* `PySide6` is the only GUI framework allowed for MVP v2.
* Do not add PyInstaller packaging, themes, plugin systems, web APIs, or persisted job queues in MVP v2.

The GUI should stay a thin layer for:

* selecting input file or folder;
* selecting output folder;
* choosing target format;
* setting quality, resize, recursive, keep-structure, and overwrite options;
* starting conversion;
* showing progress, logs, validation messages, and final summary.

RAW behavior in GUI:

* Keep `rawpy` lazy-loaded in `RawConverter`.
* `python -m app.gui_main` must not require top-level `rawpy` import.
* Regular JPG/PNG/WEBP/TIFF conversion must work even if `rawpy` is unavailable.
* RAW conversion without `rawpy` must show a clear error in the GUI log/result instead of crashing the app.

---

## GUI Localization Requirements

The PySide6 GUI supports Ukrainian and English localization.

Rules for GUI text changes:

* All new GUI user-facing strings must go through `app/gui/i18n.py`.
* Do not write hardcoded UI text directly into widgets, dialogs, status messages, validation messages, placeholders, or GUI-generated logs.
* When adding a new GUI element, add translation keys for both `uk` and `en`.
* Default GUI language is `uk`.
* Use `QSettings`-based persistence from `app/gui/settings.py` for the selected GUI language.
* GUI language switching must not clear input path, output path, log, progress, or selected format values.
* CLI localization is not part of the current task.
* Core conversion modules must not depend on GUI language or GUI i18n helpers.
* Do not translate technical format values such as `jpg`, `jpeg`, `png`, `webp`, `tif`, and `tiff`.
* Core service logs and `JobResult.summary()` may remain in English in this MVP.

When changing GUI localization behavior, update focused tests in:

```text
tests/test_gui_i18n.py
tests/test_gui_main_window.py
tests/test_gui_settings.py
tests/test_gui_validation.py
```

---

## CLI Requirements

The program must be runnable like this:

```bash
python -m app.main --input "D:/Photos/photo.nef" --output "D:/Converted" --to jpg --quality 92
```

```bash
python -m app.main --input "D:/Photos" --output "D:/Converted" --to jpg --quality 90
```

```bash
python -m app.main --input "D:/Photos" --output "D:/Converted" --to png --recursive --keep-structure
```

```bash
python -m app.main --input "D:/Photos" --output "D:/Converted" --to webp --quality 85 --overwrite
```

The CLI must support these arguments:

* `--input`
  Path to input file or folder.

* `--output`
  Output folder.

* `--to`
  Target format. Allowed values: `jpg`, `jpeg`, `png`, `webp`, `tif`, `tiff`.

* `--quality`
  Output quality for JPEG/WebP. Allowed range: `1-100`. Default: `92`.

* `--recursive`
  Scan folders recursively.

* `--overwrite`
  Overwrite existing output files.

* `--keep-structure`
  Preserve folder structure inside output directory when processing recursively.

* `--resize-width`
  Resize image to this width while preserving aspect ratio.

* `--resize-height`
  Resize image to this height while preserving aspect ratio.

* `--verbose`
  Enable detailed console logs.

---

## Architecture Requirements

Create a base converter interface/class in:

```text
app/converters/base.py
```

It should expose methods similar to:

```python
from pathlib import Path
from abc import ABC, abstractmethod


class BaseConverter(ABC):
    @abstractmethod
    def supports_input(self, input_path: Path) -> bool:
        pass

    @abstractmethod
    def supported_outputs(self) -> set[str]:
        pass

    @abstractmethod
    def convert(self, input_path: Path, output_path: Path, options: dict) -> None:
        pass
```

Implement:

```text
app/converters/image_converter.py
```

For regular image formats:

* JPG
* JPEG
* PNG
* WEBP
* TIF
* TIFF

Implement:

```text
app/converters/raw_converter.py
```

For RAW formats:

* NEF
* CR2
* ARW
* DNG

Implement:

```text
app/converters/registry.py
```

The registry must select the correct converter for a given input file.

Do not hardcode all conversion logic directly inside `main.py`.

---

## Important Conversion Rules

### RAW conversion

Use `rawpy` for RAW files.

RAW conversion should:

* open RAW file safely;
* use camera white balance when possible;
* postprocess RAW into RGB image;
* save result through Pillow.

Recommended logic:

```python
with rawpy.imread(str(input_path)) as raw:
    rgb = raw.postprocess(
        use_camera_wb=True,
        no_auto_bright=False,
        output_bps=8,
    )
```

Then convert the array to a Pillow image.

### EXIF orientation

For regular images, apply EXIF Orientation auto-rotation before conversion:

```python
from PIL import ImageOps

image = ImageOps.exif_transpose(image)
```

This is basic orientation normalization, not advanced EXIF management.

### JPEG conversion

When saving to `.jpg` or `.jpeg`:

* ensure image mode is `RGB`;
* handle PNG alpha channel correctly;
* use white background when removing transparency;
* support quality value in the `1-100` range.

If an image has transparency and is saved as JPEG, flatten it onto a white background.

### PNG conversion

PNG should preserve transparency where possible.

### WEBP conversion

WEBP should support quality settings.

### TIFF conversion

TIF and TIFF should be supported as normal output formats.

---

## Existing File Handling

If output file already exists:

* If `--overwrite` is provided, overwrite the file.
* If `--overwrite` is not provided, generate a safe unique name:

Examples:

```text
photo.jpg
photo_1.jpg
photo_2.jpg
photo_3.jpg
```

This logic should be placed in:

```text
app/core/path_utils.py
```

---

## File Scanning

Implement file scanning in:

```text
app/core/file_scanner.py
```

Requirements:

* If input is a file, process only this file.
* If input is a directory, scan supported files.
* If `--recursive` is enabled, scan nested folders.
* Ignore unsupported files.
* Do not crash on unreadable files.
* Return a clean list of paths.

---

## Job Result

Create a simple result model in:

```text
app/core/job_result.py
```

It should track:

* total found files;
* successfully converted files;
* failed files;
* skipped files;
* error messages.

The final console output must show:

* total files found;
* converted count;
* failed count;
* skipped count;
* failed file list with reasons.

---

## Logging

Use Python `logging`.

Default mode:

* show concise progress and final summary.

Verbose mode:

* show detailed file-by-file processing.

Do not spam logs in non-verbose mode.

---

## Error Handling

The program must not crash the entire batch because of one bad file.

For each file:

* catch conversion errors;
* store the error in job result;
* continue with the next file.

Only fail immediately for invalid CLI arguments, for example:

* input path does not exist;
* output path cannot be created;
* unsupported output format.

---

## Resize Behavior

Support optional resizing:

* `--resize-width`
* `--resize-height`

Rules:

* If only width is provided, calculate height automatically.
* If only height is provided, calculate width automatically.
* If both are provided, fit inside the given box while preserving aspect ratio.
* Do not distort image proportions.

Use Pillow resize methods.

---

## README Requirements

Create a useful `README.md` with:

1. Project description.
2. Supported formats.
3. Installation instructions.
4. Usage examples.
5. CLI arguments.
6. MVP limitations.
7. Future roadmap.

Roadmap must mention:

* GUI with PySide6;
* audio conversion through FFmpeg;
* presets for web/print/social media;
* drag-and-drop;
* conversion history;
* batch queue;
* EXIF options.

---

## requirements.txt

Include:

```text
Pillow
rawpy
numpy
pytest
PySide6
```

Do not add unnecessary dependencies.

---

## Testing Requirements

Add basic tests for:

```text
tests/test_path_utils.py
tests/test_file_scanner.py
tests/test_image_converter.py
```

Test at least:

* unique output file naming;
* unsupported file filtering;
* recursive scanning;
* non-recursive scanning;
* output extension handling.
* PNG with alpha channel to JPG conversion;
* resulting JPG mode is `RGB`.

Do not require real RAW files for basic tests.

---

## Code Quality Rules

Follow these rules:

* Use type hints.
* Use `pathlib.Path`, not raw string paths.
* Keep functions small and focused.
* Avoid global mutable state.
* Use clear names.
* Prefer explicit error messages.
* Keep architecture ready for future converters.
* Do not mix CLI parsing, scanning, conversion, and saving in one function.
* Do not silently ignore important errors.
* Do not add fake features that are not implemented.

---

## Implementation Order

When implementing from scratch, follow this order:

1. Create project structure.
2. Add `requirements.txt`.
3. Implement converter base class.
4. Implement image converter.
5. Implement RAW converter.
6. Implement converter registry.
7. Implement path utilities.
8. Implement file scanner.
9. Implement job result model.
10. Implement CLI in `main.py`.
11. Add logging.
12. Add README.
13. Add tests.
14. Run tests.
15. Verify example commands.

---

## Definition of Done

The MVP is complete when:

* CLI starts correctly.
* Single file conversion works.
* Folder conversion works.
* Recursive folder conversion works.
* JPG/PNG/WEBP/TIF/TIFF regular conversion works.
* RAW to JPG/PNG/TIF/TIFF conversion logic is implemented.
* RAW to WEBP is rejected in the current MVP.
* EXIF Orientation is normalized for regular images.
* PNG with alpha channel converts to JPG with an RGB result.
* Existing files are handled safely.
* Errors are reported without stopping the whole batch.
* README explains usage clearly.
* Tests for scanner, path utils, and the PNG alpha to JPG image converter case pass.
* Code is modular and ready for future audio/video converters.

---

## Future Expansion Notes

Do not implement these now, but keep architecture ready for them:

### GUI

The current GUI uses PySide6. Future GUI work may add:

* file picker
* drag-and-drop
* progress bar
* conversion queue

### Audio converter

Future audio support may use:

* FFmpeg
* MP3
* WAV
* FLAC
* AAC
* OGG

### Video converter

Future video support may use:

* FFmpeg
* MP4
* MKV
* MOV
* WEBM

### Presets

Future presets may include:

* Web optimized
* Print quality
* Telegram/social media
* Archive TIFF
* Small preview JPEG

---

## Agent Behavior

When editing this project:

* First inspect existing files.
* Do not rewrite the whole project unless necessary.
* Preserve the established architecture.
* Make minimal, focused changes.
* If adding a new feature, add or update tests.
* If changing CLI behavior, update README.
* If changing dependencies, update `requirements.txt`.
* Do not remove useful error handling.
* Do not remove type hints.
* Do not add GUI frameworks other than PySide6 unless explicitly requested.
* Do not add audio/video conversion unless explicitly requested.
