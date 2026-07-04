Створи повноцінний MVP v1 Python CLI-проєкту: **Image Format Converter**.

Мета проєкту: локальна консольна програма для пакетної конвертації зображень. Перша версія має підтримувати RAW-файли камер і звичайні формати зображень.

## Основний функціонал MVP v1

Потрібно реалізувати Python CLI-програму, яка вміє:

1. Конвертувати RAW-файли:

   * `.NEF`
   * `.CR2`
   * `.ARW`
   * `.DNG`

   У формати:

   * `.jpg`
   * `.jpeg`
   * `.png`
   * `.tif`
   * `.tiff`

2. Конвертувати звичайні зображення між форматами:

   * `.jpg`
   * `.jpeg`
   * `.png`
   * `.webp`
   * `.tif`
   * `.tiff`

3. Підтримувати пакетну обробку:

   * один файл;
   * папка з файлами;
   * опціонально рекурсивний режим для вкладених папок.

4. Підтримувати CLI-аргументи:

   * `--input` — шлях до файлу або папки;
   * `--output` — папка для результатів;
   * `--to` — формат виходу: `jpg`, `jpeg`, `png`, `webp`, `tif`, `tiff`;
   * `--quality` — якість JPEG/WebP від 1 до 100, за замовчуванням 92;
   * `--recursive` — обробляти вкладені папки;
   * `--overwrite` — перезаписувати файли, якщо вже існують;
   * `--keep-structure` — зберігати структуру папок при рекурсивній обробці;
   * `--resize-width` — змінити ширину зображення, зберігаючи пропорції;
   * `--resize-height` — змінити висоту зображення, зберігаючи пропорції;
   * `--verbose` — детальний лог у консолі.

5. Програма має показувати:

   * скільки файлів знайдено;
   * скільки успішно конвертовано;
   * скільки помилок;
   * список файлів з помилками.

## Технології

Використати:

* Python 3.12+
* `Pillow` для звичайних форматів зображень
* `rawpy` для RAW-файлів
* `numpy`, якщо потрібно для роботи з RAW
* `argparse` для CLI
* `pathlib` для роботи з шляхами
* `logging` для логування

Не використовувати GUI в першій версії. Це має бути саме CLI MVP.

## Важливі технічні вимоги

1. RAW не потрібно конвертувати назад у RAW. Тільки:

   * RAW → JPG
   * RAW → PNG
   * RAW → TIF
   * RAW → TIFF

   RAW → WEBP у MVP v1 не підтримується.

2. Звичайні формати можна конвертувати між собою:

   * JPG → PNG
   * PNG → JPG
   * PNG → WEBP
   * WEBP → JPG
   * TIF → JPG
   * TIFF → JPG
   * тощо.

3. Для звичайних зображень потрібно застосувати автоповорот по EXIF Orientation через `ImageOps.exif_transpose`, щоб фото з камер і телефонів не конвертувалися з неправильною орієнтацією.

4. Якщо вихідний формат `jpg` або `jpeg`, зображення треба конвертувати в `RGB`, щоб уникнути помилок з alpha-каналом.

5. Якщо PNG має прозорість і користувач конвертує його в JPG, треба коректно прибрати alpha-канал, замінивши прозорість білим фоном.

6. Якщо файл не підтримується, програма не має падати. Вона має пропустити файл і записати помилку в лог.

7. Якщо вихідний файл вже існує:

   * без `--overwrite` створити назву типу `image_1.jpg`, `image_2.jpg`;
   * з `--overwrite` перезаписати файл.

8. Програма має бути структурована так, щоб у майбутньому можна було додати:

   * audio converter;
   * video converter;
   * document converter;
   * GUI.

## Бажана структура проєкту

Створи структуру безпосередньо в поточному корені проєкту `D:\work\Image Format Converter`.
Не створюй додаткову вкладену директорію `image_converter_mvp/` всередині цього репозиторію.

```text
app/
  __init__.py
  main.py
  core/
    __init__.py
    config.py
    file_scanner.py
    job_result.py
    path_utils.py
  converters/
    __init__.py
    base.py
    image_converter.py
    raw_converter.py
    registry.py
tests/
  test_path_utils.py
  test_file_scanner.py
  test_image_converter.py
requirements.txt
README.md
.gitignore
```

## Архітектура

Зроби базовий клас або протокол конвертера:

```python
class BaseConverter:
    def supports_input(self, input_path: Path) -> bool:
        ...

    def supported_outputs(self) -> set[str]:
        ...

    def convert(self, input_path: Path, output_path: Path, options: dict) -> None:
        ...
```

Окремо реалізуй:

* `ImageConverter` — для JPG/PNG/WEBP/TIF/TIFF;
* `RawConverter` — для NEF/CR2/ARW/DNG;
* `ConverterRegistry` — вибирає правильний конвертер залежно від вхідного файлу.

## Приклади використання

Програма має працювати приблизно так:

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

## README

Створи нормальний `README.md`, де буде:

1. Опис проєкту.
2. Які формати підтримуються.
3. Як встановити залежності.
4. Як запускати.
5. Приклади команд.
6. Обмеження MVP v1.
7. План майбутнього розвитку:

   * GUI на PySide6;
   * підтримка аудіоформатів через FFmpeg;
   * пресети для web/print/social media;
   * drag-and-drop;
   * історія конвертацій;
   * batch queue;
   * EXIF options.

## requirements.txt

Додай мінімально потрібні залежності:

```text
Pillow
rawpy
numpy
pytest
```

## Тести

Додай базові тести:

* `tests/test_path_utils.py`;
* `tests/test_file_scanner.py`;
* `tests/test_image_converter.py`.

У `test_image_converter.py` обов'язково перевірити сценарій PNG з alpha-каналом → JPG:

* створити тимчасовий PNG з прозорістю;
* конвертувати його в JPG;
* перевірити, що файл створився;
* перевірити, що результат має режим `RGB`.

## Якість коду

Код має бути чистим, зрозумілим і структурованим.

Вимоги:

* використовувати type hints;
* не писати весь код в одному файлі;
* додати обробку помилок;
* додати логування;
* не використовувати глобальний хаос;
* не робити GUI;
* не додавати зайві фреймворки;
* не використовувати базу даних;
* не використовувати веб-сервер.

## Очікуваний результат

Згенеруй повний робочий проєкт з усіма файлами.

Після генерації коротко поясни:

1. Як встановити залежності.
2. Як запустити конвертацію одного файлу.
3. Як запустити конвертацію всієї папки.
4. Як додати новий конвертер у майбутньому.
