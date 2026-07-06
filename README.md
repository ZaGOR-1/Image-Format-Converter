# Image Format Converter MVP

[Українська](README.md) | [English](README.en.md)

**Image Format Converter** — локальний Python 3.12+ застосунок для конвертації зображень. Поточний MVP має два способи запуску:

- CLI через `python -m app.main`;
- простий GUI на PySide6 через `python -m app.gui_main`.

Проєкт фокусується на конвертації звичайних форматів зображень і RAW-файлів камер. Конвертаційна логіка винесена в спільний `ConversionService`, тому CLI і GUI використовують один pipeline.

У цьому MVP немає web server, database, audio/video/document conversion, готової EXE-збірки або інсталятора.

## Можливості

- Конвертація одного файлу або папки.
- Опціональне recursive-сканування папок.
- Збереження структури папок через `--keep-structure`.
- Безпечна обробка помилок: один поганий файл не зупиняє весь batch.
- Унікальні імена вихідних файлів, якщо `--overwrite` не увімкнено.
- Resize зі збереженням пропорцій.
- GUI з вибором input/output, формату, quality, resize, recursive, overwrite і progress/log секціями.
- GUI підтримує українську та англійську мову з перемиканням без перезапуску.
- М'яке скасування batch-конвертації через кнопку `Скасувати`.
- Lazy `rawpy`: GUI і regular conversion стартують без top-level імпорту `rawpy`; RAW-конвертація показує зрозумілу помилку, якщо `rawpy` недоступний.

## Підтримувані формати

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

RAW to WEBP у поточному MVP не підтримується.

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

## Встановлення

Створити й активувати virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Встановити залежності:

```bash
python -m pip install -r requirements.txt
```

Залежності:

- `Pillow` для звичайних зображень.
- `rawpy` для RAW-файлів.
- `numpy` для RAW image arrays.
- `PySide6` для GUI.
- `pytest` для тестів.

Для JPG/PNG/WEBP/TIFF конвертації достатньо Pillow. `rawpy` завантажується lazy і потрібен тільки під час RAW-конвертації. Якщо `rawpy` недоступний, звичайна конвертація продовжить працювати, а RAW-конвертація поверне помилку:

```text
RAW conversion requires rawpy. Install it with: pip install rawpy
```

## Запуск GUI

```bash
python -m app.gui_main
```

У GUI:

1. Виберіть input file або input folder.
2. Виберіть output folder.
3. Виберіть target format.
4. Налаштуйте quality, resize, recursive, keep structure або overwrite.
5. Натисніть `Конвертувати`.
6. За потреби натисніть `Скасувати`; поточний файл завершиться, а решта batch буде позначена як skipped.

Конвертація у GUI виконується у worker thread, тому вікно не має зависати під час batch conversion. Progress і log оновлюються через callbacks із `ConversionService`.

## Локалізація GUI

GUI підтримує українську та англійську мову. Українська є мовою за замовчуванням.

Мову можна перемикати прямо у вікні через selector `Українська / English`; перезапуск GUI не потрібен. Вибрана мова зберігається між запусками через `QSettings`.

Локалізовані GUI labels, buttons, placeholders, validation messages, основні status messages і GUI-generated dialogs/logs. CLI наразі не локалізується. Core service logs і `JobResult.summary()` можуть залишатися англійськими в цьому MVP.

## CLI приклади

Конвертація одного RAW-файлу в JPG:

```bash
python -m app.main --input "D:/Photos/photo.nef" --output "D:/Converted" --to jpg --quality 92
```

Конвертація всіх підтримуваних файлів у папці:

```bash
python -m app.main --input "D:/Photos" --output "D:/Converted" --to jpg --quality 90
```

Recursive-конвертація зі збереженням структури:

```bash
python -m app.main --input "D:/Photos" --output "D:/Converted" --to png --recursive --keep-structure
```

WEBP з overwrite:

```bash
python -m app.main --input "D:/Photos" --output "D:/Converted" --to webp --quality 85 --overwrite
```

Resize зі збереженням пропорцій:

```bash
python -m app.main --input "D:/Photos" --output "D:/Converted" --to jpg --resize-width 1600
```

Fit inside box без distortion:

```bash
python -m app.main --input "D:/Photos" --output "D:/Converted" --to jpg --resize-width 1600 --resize-height 1200
```

Verbose logs:

```bash
python -m app.main --input "D:/Photos" --output "D:/Converted" --to jpg --verbose
```

## CLI аргументи

| Аргумент | Опис |
| --- | --- |
| `--input` | Шлях до input file або folder. Обов'язковий. |
| `--output` | Output folder. Обов'язковий. Створюється автоматично, якщо можливо. |
| `--to` | Target format: `jpg`, `jpeg`, `png`, `webp`, `tif`, `tiff`. Обов'язковий. |
| `--quality` | JPEG/WebP quality від `1` до `100`. Default: `92`. |
| `--recursive` | Сканувати вкладені папки, якщо input є папкою. |
| `--overwrite` | Перезаписувати існуючі output files. Без цього прапорця генеруються імена на кшталт `photo_1.jpg`. |
| `--keep-structure` | Зберігати структуру input folders всередині output folder. Корисно з `--recursive`. |
| `--resize-width` | Resize до цієї ширини зі збереженням пропорцій. |
| `--resize-height` | Resize до цієї висоти зі збереженням пропорцій. |
| `--verbose` | Детальні console logs: processing, output paths і failure reasons. |

## Поведінка конвертації

- Regular image conversion використовує Pillow.
- RAW conversion використовує `rawpy`, але імпорт відбувається тільки під час RAW-конвертації.
- EXIF Orientation нормалізується для regular images через `ImageOps.exif_transpose`.
- PNG transparency flatten-иться на білий фон під час збереження в JPG/JPEG.
- JPG/JPEG output зберігається як `RGB`.
- PNG зберігає transparency, коли це можливо.
- WEBP підтримує quality.
- TIFF підтримує `.tif` і `.tiff`.
- Помилка одного файлу не зупиняє весь batch; final summary містить failed files і reasons.

## Обмеження MVP

- GUI простий і сфокусований на локальній конвертації.
- Немає audio, video або document conversion.
- Немає web API або web server.
- Немає database.
- Немає persisted conversion history або batch queue.
- Немає готової EXE-збірки або installer packaging.
- RAW файли конвертуються тільки з RAW у regular image formats.
- Конвертація назад у RAW не підтримується.
- RAW to WEBP не підтримується.
- EXIF support обмежений orientation normalization для regular images.
- Базові tests не потребують реальних RAW-файлів.

## Розробка

Запуск тестів:

```bash
python -m pytest
```

CLI help:

```bash
python -m app.main --help
```

Нотатки щодо майбутньої Windows EXE-збірки:

```text
docs/packaging.md
```

Структура core:

- `app/converters/base.py` — `BaseConverter`.
- `app/converters/image_converter.py` — regular image conversion.
- `app/converters/raw_converter.py` — RAW conversion.
- `app/converters/registry.py` — вибір converter.
- `app/core/conversion_options.py` — `ConversionOptions`.
- `app/core/conversion_service.py` — спільний conversion pipeline.
- `app/core/file_scanner.py` — scanning input files.
- `app/core/path_utils.py` — output paths і unique names.
- `app/core/job_result.py` — batch result summary.

GUI:

- `app/gui_main.py` — entry point для PySide6 GUI.
- `app/gui/main_window.py` — layout, validation flow і signal wiring.
- `app/gui/conversion_worker.py` — worker для запуску `ConversionService` поза UI thread.
- `app/gui/i18n.py` — dictionary-based GUI localization.
- `app/gui/options_builder.py` — mapping GUI state у `ConversionOptions`.
- `app/gui/settings.py` — persistence для GUI settings, зокрема вибраної мови.
- `app/gui/validation.py` — validation form values.

Щоб додати новий converter у майбутньому, реалізуйте `BaseConverter`, зареєструйте його в `ConverterRegistry` і додайте focused tests.

## Roadmap

- Windows EXE packaging через PyInstaller або інший packaging tool.
- Більш розвинений GUI на PySide6.
- Audio conversion через FFmpeg.
- Presets для web, print і social media.
- Drag-and-drop.
- Conversion history.
- Batch queue.
- EXIF options.
