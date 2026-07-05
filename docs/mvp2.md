Реалізуй **MVP v2** для поточного Python-проєкту **Image Format Converter**.

Поточний стан проєкту:

* вже реалізований MVP v1 як Python CLI;
* є модульна архітектура;
* є `app/core/conversion_options.py`;
* є `app/core/conversion_service.py`;
* є `ImageConverter`;
* є `RawConverter`;
* `rawpy` зроблений як lazy dependency;
* CLI працює через `app/main.py`;
* основний pipeline уже винесений у `ConversionService`;
* є тести для core/converters/CLI;
* не потрібно переписувати MVP v1 з нуля.

Мета MVP v2: **додати простий GUI на PySide6 поверх існуючого ядра**, не дублюючи логіку CLI.

---

## Головний принцип

Не переписуй існуючу логіку конвертації.

GUI має використовувати той самий conversion engine, що й CLI:

```text
CLI -> ConversionService -> scanner / registry / converters / JobResult

GUI -> ConversionService -> scanner / registry / converters / JobResult
```

`ConversionService` має залишитися центральним ядром.

Не створюй окрему GUI-логіку конвертації.
Не дублюй код із `main.py`.
Не переписуй `ImageConverter`, `RawConverter`, `ConverterRegistry`, `file_scanner`, `path_utils`, якщо це не потрібно для інтеграції GUI.

---

## Технології для MVP v2

Додай:

```text
PySide6
```

у `requirements.txt`.

Використовуй:

* Python 3.12+
* PySide6
* існуючий `ConversionService`
* існуючий `ConversionOptions`
* існуючий `JobResult`
* існуючі converter/core модулі

Не додавай:

* Flask/FastAPI/Django;
* Electron;
* Tauri;
* базу даних;
* audio/video conversion;
* web server;
* складний plugin system;
* PyInstaller packaging у цьому етапі, якщо явно не потрібно.

---

## Потрібна структура для GUI

Додай такі файли:

```text
app/
  gui_main.py
  gui/
    __init__.py
    main_window.py
    conversion_worker.py
```

Можна додати додаткові невеликі helper-файли, якщо це справді покращує структуру, наприклад:

```text
app/gui/options_builder.py
app/gui/ui_state.py
```

Але не роздувай MVP.

---

## Запуск GUI

GUI має запускатися командою:

```bash
python -m app.gui_main
```

CLI має залишитися робочим:

```bash
python -m app.main --input "D:/Photos" --output "D:/Converted" --to jpg --quality 92
```

Не ламай існуючі CLI-команди.

---

## Мінімальний функціонал GUI

Створи просте головне вікно `MainWindow`.

У вікні мають бути:

### Input section

Користувач має мати можливість вибрати:

* один файл;
* або папку.

Реалізуй кнопки:

```text
Select File
Select Folder
```

Після вибору показуй шлях у текстовому полі.

Можна зробити одне поле `Input path`.

---

### Output section

Кнопка:

```text
Select Output Folder
```

Після вибору показуй шлях у текстовому полі.

---

### Format section

Додай `QComboBox` для target format:

```text
jpg
jpeg
png
webp
tif
tiff
```

Важливо: якщо поточне ядро підтримує тільки певний список форматів, використовуй саме існуючі константи з `config.py`, а не дублюй список вручну без потреби.

---

### Options section

Додай налаштування:

* `Quality` — `QSpinBox`, default `92`, range `1-100`;
* `Resize width` — `QSpinBox` або поле, де `0` означає “не використовувати”;
* `Resize height` — `QSpinBox` або поле, де `0` означає “не використовувати”;
* `Recursive` — `QCheckBox`;
* `Keep folder structure` — `QCheckBox`;
* `Overwrite existing files` — `QCheckBox`.

Не додавай опції, яких немає в `ConversionOptions`, якщо для цього треба сильно змінювати ядро.

---

### Action section

Додай кнопку:

```text
Convert
```

Після натискання:

1. перевірити, що input path заданий;
2. перевірити, що output folder заданий;
3. перевірити, що target format заданий;
4. створити `ConversionOptions`;
5. запустити конвертацію через `ConversionService`;
6. показувати прогрес;
7. після завершення показати summary.

---

### Progress section

Додай:

* `QProgressBar`;
* label зі статусом, наприклад:

```text
Processing 3 / 25: photo.nef
```

Прогрес має оновлюватися під час конвертації.

---

### Log section

Додай текстове поле для логів:

* `QPlainTextEdit` або `QTextEdit`;
* read-only;
* показувати основні події:

  * старт конвертації;
  * знайдено файлів;
  * поточний файл;
  * помилки;
  * фінальне summary.

---

## Дуже важливо: не блокувати GUI

Не запускай конвертацію напряму в UI thread.

Потрібно реалізувати worker у фоні:

```text
MainWindow
  -> створює ConversionWorker
  -> запускає його в QThread
  -> worker викликає ConversionService.run(...)
  -> worker через signals оновлює progress/log/finished/error
```

Файл:

```text
app/gui/conversion_worker.py
```

Створи `ConversionWorker` на основі `QObject`.

Приблизна структура:

```python
from PySide6.QtCore import QObject, Signal, Slot

class ConversionWorker(QObject):
    progress_changed = Signal(int, int, str)
    log_message = Signal(str)
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, service, options):
        super().__init__()
        self.service = service
        self.options = options

    @Slot()
    def run(self):
        try:
            result = self.service.run(
                self.options,
                on_progress=self._on_progress,
                on_log=self._on_log,
            )
            self.finished.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))

    def _on_progress(self, current, total, path):
        self.progress_changed.emit(current, total, str(path))

    def _on_log(self, message):
        self.log_message.emit(message)
```

Адаптуй під реальну сигнатуру поточного `ConversionService`.

---

## Поведінка кнопки Convert

Після натискання `Convert`:

* заблокувати кнопку `Convert`, поки йде конвертація;
* не дозволяти запускати другу конвертацію паралельно;
* очистити старий лог або додати розділювач нового запуску;
* скинути progress bar;
* після завершення знову увімкнути кнопку.

Якщо сталася помилка:

* показати її в log section;
* показати `QMessageBox.critical`;
* повернути кнопку `Convert` у нормальний стан.

Якщо завершено успішно:

* показати summary в log section;
* показати `QMessageBox.information`.

---

## Валідація GUI

Перед запуском конвертації перевір:

* input path не порожній;
* input path існує;
* output path не порожній;
* output directory існує або може бути створена;
* quality у діапазоні `1-100`;
* resize width/height не від’ємні;
* target format підтримується.

Якщо валідація не пройдена, показати `QMessageBox.warning`.

---

## ConversionOptions mapping

GUI має створювати `ConversionOptions` з поточних значень форми.

Приклад:

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

Не додавай `verbose=True` без потреби. Для GUI краще передавати лог через `on_log`.

---

## GUI layout

Не потрібен складний дизайн.

Зроби простий, акуратний, зрозумілий інтерфейс.

Можна використовувати:

* `QMainWindow`;
* `QWidget`;
* `QVBoxLayout`;
* `QHBoxLayout`;
* `QGroupBox`;
* `QLineEdit`;
* `QPushButton`;
* `QComboBox`;
* `QSpinBox`;
* `QCheckBox`;
* `QProgressBar`;
* `QPlainTextEdit`;
* `QMessageBox`;
* `QFileDialog`.

Вікно має мати title:

```text
Image Format Converter
```

Рекомендований мінімальний розмір:

```text
800x600
```

---

## RAW behavior у GUI

Оскільки `rawpy` є lazy dependency:

* GUI має запускатися навіть без `rawpy`;
* звичайна конвертація JPG/PNG/WEBP/TIFF має працювати без `rawpy`;
* якщо користувач вибрав RAW-файл без встановленого `rawpy`, помилка має з’явитися в log section і/або QMessageBox;
* програма не має падати.

Не змінюй цю поведінку.

---

## README update

Онови `README.md`.

Додай розділ:

```text
GUI usage
```

У ньому поясни:

1. як встановити залежності:

```bash
pip install -r requirements.txt
```

2. як запустити GUI:

```bash
python -m app.gui_main
```

3. як користуватися GUI:

   * вибрати файл або папку;
   * вибрати output folder;
   * вибрати формат;
   * налаштувати quality/resize/recursive/overwrite;
   * натиснути Convert.

4. поясни, що CLI все ще доступний.

---

## AGENTS.md update

Онови `AGENTS.md`, якщо він є.

Додай правила для MVP v2:

* GUI має використовувати `ConversionService`;
* не дублювати conversion logic у GUI;
* не блокувати UI thread;
* використовувати worker thread;
* CLI має залишатися робочим;
* PySide6 — єдиний GUI framework для цього MVP.

---

## Тести

Не потрібно робити повноцінні GUI integration tests, якщо це складно.

Але потрібно:

1. Не зламати існуючі тести.
2. Додати прості тести для helper-логіки, якщо буде створений `options_builder.py` або подібний модуль.
3. Переконатися, що `pytest` проходить.
4. Переконатися, що CLI досі працює.

Обов’язкова ручна перевірка:

```bash
pytest
```

```bash
python -m app.main --input "D:/Photos/test.png" --output "D:/Converted" --to jpg --quality 92
```

```bash
python -m app.gui_main
```

---

## Definition of Done для MVP v2

MVP v2 готовий, коли:

* GUI запускається через `python -m app.gui_main`;
* CLI не зламаний;
* існуючі тести проходять;
* можна вибрати input file;
* можна вибрати input folder;
* можна вибрати output folder;
* можна вибрати output format;
* можна задати quality;
* можна задати resize width/height;
* можна ввімкнути recursive;
* можна ввімкнути keep folder structure;
* можна ввімкнути overwrite;
* конвертація запускається через `ConversionService`;
* GUI не зависає під час конвертації;
* progress bar оновлюється;
* log section показує процес;
* після завершення показується summary;
* помилки показуються зрозуміло;
* RAW без `rawpy` не валить програму;
* README оновлений;
* AGENTS.md оновлений.

---

## Що НЕ робити в MVP v2

Не додавай:

* аудіоконвертацію;
* відеоконвертацію;
* конвертацію документів;
* базу даних;
* історію конвертацій;
* web API;
* drag-and-drop, якщо це сильно ускладнює реалізацію;
* PyInstaller `.exe` packaging;
* складну систему тем;
* складний plugin manager;
* авторизацію;
* cloud sync.

Ціль MVP v2 — не зробити “комбайн”, а додати нормальний GUI до вже робочого CLI-ядра.

---

## Після реалізації

Після внесення змін коротко виведи:

1. які файли були додані;
2. які файли були змінені;
3. як запустити GUI;
4. як запустити CLI;
5. результат `pytest`;
6. які обмеження залишилися для майбутніх версій.
