Внеси покращення в поточний Python CLI MVP-проєкт **Image Format Converter**.

Мета змін: не переписувати весь проєкт, а акуратно покращити архітектуру перед майбутнім MVP v2 з GUI.

Потрібно виправити 2 ключові речі:

1. `rawpy` не має ламати запуск програми, якщо користувач конвертує тільки звичайні зображення.
2. Основний conversion pipeline потрібно винести з `app/main.py` в окремий сервіс, щоб у майбутньому CLI і GUI могли використовувати одне й те саме ядро.

---

## 1. Зробити `rawpy` lazy dependency

Поточна проблема: якщо `rawpy` не встановлений, програма може не стартувати взагалі, навіть коли користувач хоче зробити звичайну конвертацію типу PNG → JPG.

Потрібно зробити так:

* Програма має нормально запускатися без `rawpy`.
* Звичайні конвертації JPG/PNG/WEBP/TIFF мають працювати без `rawpy`.
* `rawpy` має бути потрібен тільки тоді, коли користувач реально конвертує RAW-файл: `.nef`, `.cr2`, `.arw`, `.dng`.
* Якщо користувач пробує конвертувати RAW-файл без встановленого `rawpy`, програма має показати зрозумілу помилку, наприклад:

```text
RAW conversion requires rawpy. Install it with: pip install rawpy
```

або:

```text
RAW conversion is unavailable because rawpy is not installed.
Run: pip install -r requirements.txt
```

### Як реалізувати

Не імпортуй `rawpy` на рівні модуля в `raw_converter.py`.

Погано:

```python
import rawpy
```

на верхньому рівні файлу.

Добре:

```python
def convert(...):
    try:
        import rawpy
    except ImportError as exc:
        raise RuntimeError(
            "RAW conversion requires rawpy. Install it with: pip install rawpy"
        ) from exc
```

Або зроби приватний helper:

```python
def _load_rawpy():
    try:
        import rawpy
        return rawpy
    except ImportError as exc:
        raise RuntimeError(
            "RAW conversion requires rawpy. Install it with: pip install rawpy"
        ) from exc
```

Потім у `RawConverter.convert()` використовуй:

```python
rawpy = _load_rawpy()
```

### Важливо

* Не прибирай `rawpy` з `requirements.txt`.
* `rawpy` все ще має бути рекомендованою залежністю для повної функціональності MVP.
* Просто зроби так, щоб без нього не ламалися звичайні конвертації.

---

## 2. Винести pipeline з `main.py` у `ConversionService`

Поточна проблема: `app/main.py` може містити забагато логіки: сканування файлів, вибір конвертера, побудова output path, запуск конвертації, збір результатів.

Для майбутнього GUI це погано, бо GUI не має дублювати цю логіку.

Потрібно створити окреме ядро конвертації:

```text
app/core/conversion_options.py
app/core/conversion_service.py
```

---

## 3. Створити `ConversionOptions`

Файл:

```text
app/core/conversion_options.py
```

Створи dataclass:

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ConversionOptions:
    input_path: Path
    output_dir: Path
    target_format: str
    quality: int = 92
    recursive: bool = False
    overwrite: bool = False
    keep_structure: bool = False
    resize_width: int | None = None
    resize_height: int | None = None
    verbose: bool = False
```

Можна додати інші поля, якщо вони вже є в CLI, але не вигадуй зайвого.

---

## 4. Створити `ConversionService`

Файл:

```text
app/core/conversion_service.py
```

`ConversionService` має відповідати за весь процес конвертації.

Він має використовувати вже існуючі модулі:

* `file_scanner.py`
* `path_utils.py`
* `job_result.py`
* `ConverterRegistry`
* `ImageConverter`
* `RawConverter`

Приблизна структура:

```python
from collections.abc import Callable
from pathlib import Path

from app.core.conversion_options import ConversionOptions
from app.core.job_result import JobResult
from app.core.file_scanner import scan_files
from app.converters.registry import ConverterRegistry


ProgressCallback = Callable[[int, int, Path], None]
LogCallback = Callable[[str], None]


class ConversionService:
    def __init__(self, registry: ConverterRegistry | None = None) -> None:
        self.registry = registry or ConverterRegistry.default()

    def run(
        self,
        options: ConversionOptions,
        on_progress: ProgressCallback | None = None,
        on_log: LogCallback | None = None,
    ) -> JobResult:
        ...
```

### Логіка `run()`

Метод `run()` має:

1. Просканувати файли.
2. Створити `JobResult`.
3. Для кожного файлу:

   * знайти потрібний конвертер через `ConverterRegistry`;
   * перевірити підтримку target format;
   * побудувати output path;
   * виконати конвертацію;
   * записати успіх у `JobResult`;
   * при помилці записати помилку в `JobResult`, але не зупиняти всю batch-обробку.
4. Викликати `on_progress`, якщо callback переданий.
5. Викликати `on_log`, якщо callback переданий.
6. Повернути `JobResult`.

Важливо: одна помилка на одному файлі не має валити всю конвертацію папки.

---

## 5. Оновити `main.py`

`app/main.py` має залишитися CLI-точкою входу, але більше не має містити всю бізнес-логіку.

`main.py` має робити тільки це:

1. Парсити CLI-аргументи через `argparse`.
2. Валідувати базові аргументи.
3. Створити `ConversionOptions`.
4. Налаштувати logging.
5. Створити `ConversionService`.
6. Запустити `service.run(...)`.
7. Вивести фінальний summary.

Тобто `main.py` має стати тонким шаром над `ConversionService`.

Не ламай існуючі CLI-команди. Вони мають працювати так само, як і раніше:

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

---

## 6. Оновити тести

Додай або онови тести так, щоб перевірити:

### Для lazy `rawpy`

1. Імпорт `RawConverter` не падає без реального імпорту `rawpy`.
2. Звичайний `ImageConverter` може працювати незалежно від `rawpy`.
3. Якщо `rawpy` відсутній і виконується RAW-конвертація, повертається зрозуміла помилка.

Не обов’язково використовувати реальні RAW-файли. Можна протестувати поведінку через mock/monkeypatch.

### Для `ConversionService`

Додай файл:

```text
tests/test_conversion_service.py
```

Перевірити:

1. `ConversionService` обробляє один файл.
2. `ConversionService` продовжує batch, якщо один файл впав з помилкою.
3. `ConversionService` викликає progress callback.
4. `ConversionService` повертає `JobResult`.
5. CLI використовує `ConversionService`, а не дублює pipeline напряму.

---

## 7. Оновити README

У README потрібно додати або уточнити:

### Про `rawpy`

Напиши, що:

* для звичайних форматів JPG/PNG/WEBP/TIFF достатньо Pillow;
* для RAW-конвертації потрібен `rawpy`;
* якщо `rawpy` не встановлений, RAW-конвертація буде недоступна;
* повне встановлення:

```bash
pip install -r requirements.txt
```

### Про архітектуру

Додай короткий блок:

```text
CLI and future GUI use the same conversion core through ConversionService.
```

Поясни, що `ConversionService` є центральним ядром, яке потім можна буде викликати з PySide6 GUI.

---

## 8. Не робити зайвого

Не додавай зараз:

* GUI;
* PySide6;
* audio conversion;
* video conversion;
* document conversion;
* web server;
* database;
* background queue з історією;
* складну систему plugin discovery.

Це тільки архітектурне покращення MVP v1 перед майбутнім MVP v2.

---

## 9. Очікуваний результат

Після змін має бути:

* `rawpy` більше не ламає запуск програми для звичайної image-конвертації.
* RAW-конвертація все ще працює, якщо `rawpy` встановлений.
* Якщо `rawpy` не встановлений, RAW-конвертація показує зрозумілу помилку.
* `main.py` став тоншим.
* Основна логіка конвертації винесена в `ConversionService`.
* CLI-команди залишилися сумісними.
* Тести проходять.
* README оновлений.
* Архітектура готова до майбутнього GUI MVP v2.
