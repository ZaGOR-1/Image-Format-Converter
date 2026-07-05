# План реалізації Image Format Converter MVP v2

Цей документ описує поетапний план реалізації **MVP v2** для поточного Python-проєкту **Image Format Converter** на основі вимог із `docs/mvp2.md`.

Поточний стан: MVP v1 уже реалізований як Python CLI, основний pipeline винесений у `ConversionService`, є `ConversionOptions`, `ImageConverter`, `RawConverter`, `ConverterRegistry`, lazy `rawpy`, README і тести. MVP v2 не має переписувати це з нуля.

Мета MVP v2: додати простий GUI на PySide6 поверх існуючого ядра конвертації, не дублюючи CLI-логіку.

## Головні принципи

- GUI має використовувати `ConversionService`.
- CLI має залишитися робочим і сумісним з існуючими командами.
- Не дублювати conversion pipeline у GUI.
- Не переписувати `ImageConverter`, `RawConverter`, `ConverterRegistry`, `file_scanner`, `path_utils`, якщо це не потрібно для GUI-інтеграції.
- Не запускати конвертацію в UI thread.
- Для GUI використовувати тільки PySide6.
- Не додавати audio/video/document conversion, web server, database, PyInstaller packaging або plugin system у MVP v2.

## Фаза 1. Підготовка залежностей і структури GUI

### Ціль

Підготувати мінімальну структуру GUI без зміни існуючого CLI-ядра.

### Задачі

- Додати `PySide6` у `requirements.txt`.
- Створити файли:

```text
app/
  gui_main.py
  gui/
    __init__.py
    main_window.py
    conversion_worker.py
```

- За потреби додати невеликий helper:

```text
app/gui/options_builder.py
```

тільки якщо це реально спростить побудову `ConversionOptions`.

- Не додавати PyInstaller, теми, plugin discovery або інші великі підсистеми.

### Результат фази

Проєкт має базову структуру GUI, а залежності вказані явно.

## Фаза 2. GUI entry point

### Ціль

Додати запуск GUI через модульну команду.

### Задачі

- У `app/gui_main.py` створити entry point для PySide6.
- Команда запуску має працювати так:

```bash
python -m app.gui_main
```

- Створити `QApplication`.
- Створити й показати `MainWindow`.
- Не запускати жодну конвертацію при старті.
- Переконатися, що CLI досі запускається:

```bash
python -m app.main --input "D:/Photos" --output "D:/Converted" --to jpg --quality 92
```

### Результат фази

GUI-додаток стартує окремою командою, CLI не зламаний.

## Фаза 3. MainWindow layout

### Ціль

Створити просте, зрозуміле головне вікно без складного дизайну.

### Задачі

- У `app/gui/main_window.py` створити `MainWindow`.
- Використати `QMainWindow` або `QWidget` як основну оболонку.
- Встановити title:

```text
Image Format Converter
```

- Встановити рекомендований мінімальний розмір:

```text
800x600
```

- Додати секції:
  - Input;
  - Output;
  - Format;
  - Options;
  - Action;
  - Progress;
  - Log.

- Використовувати прості PySide6 widgets:
  - `QVBoxLayout`;
  - `QHBoxLayout`;
  - `QGroupBox`;
  - `QLineEdit`;
  - `QPushButton`;
  - `QComboBox`;
  - `QSpinBox`;
  - `QCheckBox`;
  - `QProgressBar`;
  - `QPlainTextEdit`;
  - `QMessageBox`;
  - `QFileDialog`.

### Результат фази

Відкривається акуратне головне вікно з усіма основними секціями.

## Фаза 4. Input та output selection

### Ціль

Дати користувачу можливість вибрати файл або папку для input і папку для output.

### Задачі

- Додати поле `Input path`.
- Додати кнопки:

```text
Select File
Select Folder
```

- `Select File` має відкривати `QFileDialog.getOpenFileName`.
- `Select Folder` має відкривати `QFileDialog.getExistingDirectory`.
- Після вибору показувати шлях у `Input path`.
- Додати поле `Output folder`.
- Додати кнопку:

```text
Select Output Folder
```

- Після вибору показувати шлях у `Output folder`.

### Результат фази

Користувач може вибрати input file, input folder і output folder.

## Фаза 5. Format та options section

### Ціль

Додати GUI-контроли для всіх базових `ConversionOptions`.

### Задачі

- Додати `QComboBox` для target format.
- Формати брати з існуючих констант у `app/core/config.py`, а не дублювати вручну.
- Підтримати:

```text
jpg
jpeg
png
webp
tif
tiff
```

- Додати `Quality` як `QSpinBox`:
  - default `92`;
  - range `1-100`;
  - використовувати константи з `config.py`, якщо можливо.

- Додати `Resize width`:
  - `QSpinBox`;
  - `0` означає `None`.

- Додати `Resize height`:
  - `QSpinBox`;
  - `0` означає `None`.

- Додати checkboxes:
  - `Recursive`;
  - `Keep folder structure`;
  - `Overwrite existing files`.

- Не додавати опції, яких немає в `ConversionOptions`.

### Результат фази

GUI дозволяє налаштувати формат, quality, resize, recursive, keep structure і overwrite.

## Фаза 6. Побудова ConversionOptions

### Ціль

Перетворити стан форми GUI на `ConversionOptions`, не створюючи окремої GUI-логіки конвертації.

### Задачі

- Реалізувати побудову `ConversionOptions` з GUI-полів.
- Якщо створюється helper `app/gui/options_builder.py`, він має бути малим і тестованим.
- Mapping:

```python
options = ConversionOptions(
    input_path=Path(input_text),
    output_dir=Path(output_text),
    target_format=target_format,
    quality=quality,
    recursive=recursive_checkbox.isChecked(),
    overwrite=overwrite_checkbox.isChecked(),
    keep_structure=keep_structure_checkbox.isChecked(),
    resize_width=resize_width if resize_width > 0 else None,
    resize_height=resize_height if resize_height > 0 else None,
)
```

- Не виставляти `verbose=True` без потреби.
- Для GUI логи мають приходити через `on_log`.

### Результат фази

GUI може створити коректний `ConversionOptions`, сумісний із `ConversionService`.

## Фаза 7. GUI validation

### Ціль

Перевіряти введені дані до старту conversion worker.

### Задачі

Перед запуском конвертації перевірити:

- input path не порожній;
- input path існує;
- output path не порожній;
- output directory існує або може бути створена;
- target format підтримується;
- quality у діапазоні `1-100`;
- resize width/height не від'ємні.

Якщо валідація не пройдена:

- показати `QMessageBox.warning`;
- не запускати worker;
- не блокувати кнопку `Convert`.

### Результат фази

Користувач отримує зрозумілі validation errors до старту конвертації.

## Фаза 8. ConversionWorker у QThread

### Ціль

Запускати конвертацію у фоні, щоб GUI не зависав.

### Задачі

- У `app/gui/conversion_worker.py` створити `ConversionWorker(QObject)`.
- Використати signals:

```python
progress_changed = Signal(int, int, str)
log_message = Signal(str)
finished = Signal(object)
failed = Signal(str)
```

- Worker має приймати:
  - `ConversionService`;
  - `ConversionOptions`.

- Worker метод `run()` має:
  - викликати `ConversionService.run(...)`;
  - передати `on_progress`;
  - передати `on_log`;
  - emit `finished(result)` при успіху;
  - emit `failed(str(exc))` при неочікуваній помилці.

- `_on_progress(current, total, path)` має emit `progress_changed(current, total, str(path))`.
- `_on_log(message)` має emit `log_message(message)`.

### Результат фази

Конвертація запускається у background worker і не блокує UI thread.

## Фаза 9. Convert button behavior

### Ціль

Зв'язати UI з worker thread і забезпечити передбачувану поведінку кнопки Convert.

### Задачі

Після натискання `Convert`:

- виконати GUI validation;
- очистити старий log або додати розділювач нового запуску;
- скинути progress bar;
- створити `ConversionOptions`;
- створити `ConversionService`;
- створити `ConversionWorker`;
- створити `QThread`;
- перемістити worker у thread;
- підключити signals до UI slots;
- заблокувати кнопку `Convert`;
- не дозволяти другу конвертацію паралельно;
- запустити thread.

Після завершення:

- показати summary у log section;
- показати `QMessageBox.information`;
- знову увімкнути кнопку `Convert`;
- коректно зупинити й очистити thread/worker references.

При помилці:

- показати помилку у log section;
- показати `QMessageBox.critical`;
- знову увімкнути кнопку `Convert`;
- коректно очистити thread/worker references.

### Результат фази

Кнопка `Convert` запускає безпечну фонову конвертацію і коректно повертає UI у нормальний стан.

## Фаза 10. Progress та log section

### Ціль

Показувати користувачу стан конвертації під час виконання.

### Задачі

- Додати `QProgressBar`.
- Додати status label, наприклад:

```text
Processing 3 / 25: photo.nef
```

- Progress bar має оновлюватися через `progress_changed`.
- Додати read-only `QPlainTextEdit` для log section.
- Показувати:
  - старт конвертації;
  - кількість знайдених файлів;
  - поточний файл;
  - output path, якщо це приходить через `on_log`;
  - помилки;
  - фінальний summary.

### Результат фази

Користувач бачить progress і log без зависання інтерфейсу.

## Фаза 11. RAW behavior у GUI

### Ціль

Зберегти lazy `rawpy` поведінку в GUI.

### Задачі

- Переконатися, що `python -m app.gui_main` стартує без top-level import `rawpy`.
- Звичайна конвертація JPG/PNG/WEBP/TIFF має працювати без `rawpy`.
- Якщо користувач вибрав RAW-файл без встановленого `rawpy`:
  - помилка має з'явитися в log section;
  - помилка може бути показана через `QMessageBox`;
  - GUI не має падати.

- Не змінювати lazy dependency підхід у `RawConverter`.

### Результат фази

GUI не падає без `rawpy`, а RAW-помилки показуються зрозуміло.

## Фаза 12. README та AGENTS.md update

### Ціль

Оновити документацію під MVP v2.

### README задачі

Додати розділ:

```text
GUI usage
```

У ньому описати:

- встановлення залежностей:

```bash
pip install -r requirements.txt
```

- запуск GUI:

```bash
python -m app.gui_main
```

- як користуватися GUI:
  - вибрати файл або папку;
  - вибрати output folder;
  - вибрати формат;
  - налаштувати quality/resize/recursive/overwrite;
  - натиснути `Convert`.

- пояснити, що CLI все ще доступний:

```bash
python -m app.main --input "D:/Photos" --output "D:/Converted" --to jpg --quality 92
```

### AGENTS.md задачі

Додати правила для MVP v2:

- GUI має використовувати `ConversionService`;
- не дублювати conversion logic у GUI;
- не блокувати UI thread;
- використовувати worker thread;
- CLI має залишатися робочим;
- PySide6 — єдиний GUI framework для цього MVP.

### Результат фази

Документація пояснює запуск GUI, архітектуру та межі MVP v2.

## Фаза 13. Тести

### Ціль

Не зламати існуючу test suite і додати мінімальні тести для нової helper-логіки.

### Задачі

- Запустити існуючі тести:

```bash
pytest
```

- Якщо створено `app/gui/options_builder.py`, додати тести для:
  - `0` resize width -> `None`;
  - `0` resize height -> `None`;
  - target format mapping;
  - checkbox mapping into `ConversionOptions`.

- Не робити важкі GUI integration tests, якщо це ускладнює MVP.
- Переконатися, що `ConversionService` тести досі проходять.
- Переконатися, що CLI pipeline тести досі проходять.

### Результат фази

Автоматичні тести підтверджують, що GUI-додавання не зламало core/CLI.

## Фаза 14. Ручна перевірка MVP v2

### Ціль

Переконатися, що GUI і CLI працюють у реальних сценаріях.

### Обов'язкові команди

Запустити tests:

```bash
pytest
```

Перевірити CLI:

```bash
python -m app.main --input "D:/Photos/test.png" --output "D:/Converted" --to jpg --quality 92
```

Запустити GUI:

```bash
python -m app.gui_main
```

### Ручні GUI сценарії

Перевірити:

- GUI запускається;
- можна вибрати input file;
- можна вибрати input folder;
- можна вибрати output folder;
- можна вибрати target format;
- quality змінюється;
- resize width/height працюють;
- recursive працює для folder input;
- keep folder structure працює;
- overwrite працює;
- кнопка `Convert` блокується під час конвертації;
- друга паралельна конвертація не стартує;
- progress bar оновлюється;
- status label показує поточний файл;
- log section показує процес;
- після завершення показується summary;
- помилки показуються зрозуміло;
- CLI після GUI-змін досі працює.

### RAW manual behavior

Якщо є реальний RAW-файл:

- перевірити RAW -> JPG/PNG/TIFF.

Якщо `rawpy` недоступний:

- GUI має стартувати;
- regular conversion має працювати;
- RAW conversion має показати зрозумілу помилку.

### Результат фази

MVP v2 перевірений автоматично й вручну.

## Фаза 15. Definition of Done

MVP v2 вважається готовим, коли:

- GUI запускається через `python -m app.gui_main`;
- CLI не зламаний;
- існуючі тести проходять;
- можна вибрати input file;
- можна вибрати input folder;
- можна вибрати output folder;
- можна вибрати output format;
- можна задати quality;
- можна задати resize width/height;
- можна ввімкнути recursive;
- можна ввімкнути keep folder structure;
- можна ввімкнути overwrite;
- конвертація запускається через `ConversionService`;
- GUI не зависає під час конвертації;
- progress bar оновлюється;
- log section показує процес;
- після завершення показується summary;
- помилки показуються зрозуміло;
- RAW без `rawpy` не валить програму;
- README оновлений;
- AGENTS.md оновлений.

## Що не входить у MVP v2

Не додавати:

- audio conversion;
- video conversion;
- document conversion;
- database;
- conversion history;
- web API;
- drag-and-drop, якщо це сильно ускладнює реалізацію;
- PyInstaller `.exe` packaging;
- складну систему тем;
- plugin manager;
- authorization;
- cloud sync;
- background queue з persisted history.

## Ризики та рішення

| Ризик | Рішення |
| --- | --- |
| GUI зависає під час batch conversion | Використати `ConversionWorker` у `QThread` |
| GUI дублює CLI pipeline | Усі conversion calls мають проходити через `ConversionService` |
| `rawpy` ламає старт GUI | Зберегти lazy import у `RawConverter`; не імпортувати `rawpy` у GUI |
| CLI випадково ламається | Запускати CLI tests і ручний CLI smoke test після GUI-змін |
| PySide6 ускладнює CI/тести | Не робити важкі GUI integration tests у MVP v2; тестувати helper-логіку |
| Неправильна очистка QThread | Після `finished`/`failed` викликати cleanup і звільняти references |

## Рекомендований порядок виконання

1. Додати `PySide6` у `requirements.txt`.
2. Створити `app/gui_main.py`.
3. Створити `app/gui/__init__.py`.
4. Створити каркас `MainWindow`.
5. Додати input/output selectors.
6. Додати format/options controls.
7. Реалізувати побудову `ConversionOptions`.
8. Реалізувати GUI validation.
9. Створити `ConversionWorker`.
10. Підключити worker до `QThread`.
11. Підключити progress/log/finished/error signals до UI.
12. Реалізувати поведінку кнопки `Convert`.
13. Перевірити RAW/lazy rawpy behavior у GUI.
14. Оновити README.
15. Оновити AGENTS.md.
16. Додати helper tests, якщо з'явився helper module.
17. Запустити `pytest`.
18. Перевірити CLI командою `python -m app.main ...`.
19. Перевірити GUI командою `python -m app.gui_main`.
20. Зафіксувати залишкові обмеження для майбутніх версій.

## Після реалізації потрібно повідомити

Після виконання MVP v2 коротко вивести:

1. які файли були додані;
2. які файли були змінені;
3. як запустити GUI;
4. як запустити CLI;
5. результат `pytest`;
6. які обмеження залишилися для майбутніх версій.
