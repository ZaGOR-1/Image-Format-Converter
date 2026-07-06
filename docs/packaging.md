# Windows EXE Packaging

This project does not ship a prebuilt EXE yet, but the recommended MVP packaging
path is PyInstaller.

## Install Packaging Tool

```bash
python -m pip install pyinstaller
```

## Build GUI EXE

```bash
python -m PyInstaller --onefile --windowed --name ImageFormatConverter app/gui_main.py
```

The generated executable should appear at:

```text
dist/ImageFormatConverter.exe
```

## Smoke Checks After Build

Run these checks before treating the EXE as release-ready:

1. Start `dist/ImageFormatConverter.exe`.
2. Convert a PNG with alpha channel to JPG.
3. Convert a folder recursively.
4. Verify progress and log updates in the GUI.
5. Verify RAW behavior:
   - RAW to JPG/PNG/TIFF works when `rawpy` and its native binaries are bundled.
   - RAW shows a clear error if `rawpy` is unavailable.

## Known Packaging Notes

- PySide6 builds can be large.
- RAW support may require extra PyInstaller hidden imports or binary collection,
  depending on the target machine and PyInstaller version.
- Keep `requirements.txt` pinned for reproducible packaging runs.
