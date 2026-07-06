# Prompt: Додати українську та англійську локалізацію GUI

Ти працюєш у проєкті **Image Format Converter MVP v2 / early MVP v3**.

Це Python 3.12+ застосунок для локальної конвертації зображень.

Поточний стан проєкту:

* CLI запускається через:

```bash
python -m app.main
```

* GUI запускається через:

```bash
python -m app.gui_main
```

* GUI реалізований на **PySide6**.
* Це не web-застосунок, не Vue, не React, не Electron.
* Основний GUI-файл:

```text
app/gui/main_window.py
```

* GUI вже використовує:

  * `ConversionService`;
  * `ConversionWorker`;
  * `QThread`;
  * `ConversionOptions`;
  * `validate_conversion_form`;
  * `build_conversion_options`.

Не переписуй conversion core.
Не дублюй conversion pipeline у GUI.
Не ламай CLI.
Не змінюй логіку конвертації без потреби.

---

## Ціль

Додати нормальну двомовну локалізацію GUI:

* українська;
* англійська.

У GUI має бути простий перемикач мови:

```text
Мова: [Українська ▼]
```

або англійською:

```text
Language: [English ▼]
```

Рекомендовано використати `QComboBox` з варіантами:

```text
Українська
English
```

Внутрішні значення:

```text
uk
en
```

Користувач має мати можливість перемикати мову **без перезапуску програми**.

---

## Важливі вимоги

1. За замовчуванням використовувати українську мову.
2. Додати централізований словник перекладів.
3. Не розкидати `if language == ...` по всьому UI.
4. Не хардкодити нові user-facing тексти прямо у PySide6 widgets.
5. Перекласти всі GUI labels, buttons, group boxes, placeholder text, dialog titles, validation messages, status messages.
6. CLI не змінювати.
7. Core conversion logic не змінювати без потреби.
8. `ConversionService`, `ImageConverter`, `RawConverter`, `file_scanner`, `path_utils` не повинні залежати від GUI language.
9. GUI має залишитися простим MVP, без важких i18n framework dependencies.
10. Не додавати web server, database, Vue, React, Flask, FastAPI, Docker або plugin system.
11. Не ламати існуючі тести.
12. Додати або оновити тести для локалізації GUI.
13. Не створювати UI заново при перемиканні мови — потрібно оновлювати тексти існуючих widgets.
14. Не очищати input/output fields, progress і log при зміні мови.

---

## Рекомендована реалізація

Створити новий файл:

```text
app/gui/i18n.py
```

У ньому зробити просту dictionary-based i18n систему без зовнішніх залежностей.

Приклад:

```python
SUPPORTED_LANGUAGES = ("uk", "en")
DEFAULT_LANGUAGE = "uk"
FALLBACK_LANGUAGE = "en"

TRANSLATIONS = {
    "uk": {
        "app.title": "Конвертер зображень",
        "language.ukrainian": "Українська",
        "language.english": "English",
        "button.convert": "Конвертувати",
    },
    "en": {
        "app.title": "Image Format Converter",
        "language.ukrainian": "Українська",
        "language.english": "English",
        "button.convert": "Convert",
    },
}
```

Реалізувати функцію:

```python
def translate(language: str, key: str) -> str:
    ...
```

або клас:

```python
class Translator:
    def __init__(self, language: str = DEFAULT_LANGUAGE) -> None:
        ...

    def set_language(self, language: str) -> None:
        ...

    def get_language(self) -> str:
        ...

    def tr(self, key: str) -> str:
        ...
```

Для поточного MVP достатньо функції `translate(...)`, але клас `Translator` теж допустимий, якщо він не ускладнює код.

---

## Fallback behavior

Вимоги до `translate`:

1. Якщо language невідомий — fallback на `DEFAULT_LANGUAGE`.
2. Якщо key відсутній у вибраній мові — fallback на `FALLBACK_LANGUAGE`, тобто English.
3. Якщо key відсутній в English — fallback на український переклад.
4. Якщо key відсутній всюди — повернути сам key.
5. Відсутній переклад не має ламати GUI.

Приклад логіки:

```python
def translate(language: str, key: str) -> str:
    if language not in SUPPORTED_LANGUAGES:
        language = DEFAULT_LANGUAGE

    return (
        TRANSLATIONS.get(language, {}).get(key)
        or TRANSLATIONS.get(FALLBACK_LANGUAGE, {}).get(key)
        or TRANSLATIONS.get(DEFAULT_LANGUAGE, {}).get(key)
        or key
    )
```

---

## Зміни в MainWindow

У `app/gui/main_window.py`:

1. Додати поле:

```python
self._language = DEFAULT_LANGUAGE
```

або, якщо реалізовано збереження мови, завантажувати її з налаштувань.

2. Додати helper:

```python
def _t(self, key: str) -> str:
    return translate(self._language, key)
```

3. Додати `QComboBox` для вибору мови.

Рекомендовано:

```python
self.language_combo = QComboBox()
self.language_combo.addItem("Українська", "uk")
self.language_combo.addItem("English", "en")
self.language_combo.currentIndexChanged.connect(self._on_language_changed)
```

4. Додати handler:

```python
def _on_language_changed(self) -> None:
    language = self.language_combo.currentData()
    self._set_language(language)
```

5. Додати:

```python
def _set_language(self, language: str) -> None:
    self._language = language
    self._retranslate_ui()
```

6. Додати:

```python
def _retranslate_ui(self) -> None:
    ...
```

`_retranslate_ui()` має оновлювати тексти для:

* window title;
* group boxes;
* labels;
* buttons;
* checkboxes;
* placeholders;
* status label, якщо зараз idle/ready;
* dialog titles/messages, де це можливо через keys.

Не створюй UI заново при перемиканні мови.
Не очищай input/output fields.
Не очищай progress.
Не очищай log.
Не скидай поточний стан конвертації.

---

## Що потрібно перекласти

Мінімальний набір ключів:

```text
app.title

group.language
language.ukrainian
language.english

group.input
label.input_path
placeholder.input_path
button.select_file
button.select_folder

group.output
label.output_folder
placeholder.output_folder
button.select_output_folder

group.format
label.target_format

group.options
label.quality
label.resize_width
label.resize_height
checkbox.recursive
checkbox.keep_structure
checkbox.overwrite

group.action
button.convert
button.cancel

group.progress
status.ready
status.starting
status.processing
status.cancelling
status.finished
status.cancelled
status.failed

group.log
placeholder.log

dialog.validation.title
dialog.finished.title
dialog.cancelled.title
dialog.failed.title
dialog.running.title
dialog.running.message
dialog.success.title
dialog.error.title
dialog.warning.title

validation.input_required
validation.input_missing
validation.output_required
validation.output_not_folder
validation.output_parent_missing
validation.target_required
validation.target_unsupported
validation.quality_invalid
validation.resize_width_negative
validation.resize_height_negative

log.starting
log.error
log.cancel_requested
log.finished
log.cancelled
log.failed
```

Для status із параметрами використовуй `.format(...)`.

Приклад:

```python
self._t("status.processing").format(
    current=current,
    total=total,
    file=file_name,
)
```

Український текст:

```text
status.processing = "Обробка {current} / {total}: {file}"
```

Англійський текст:

```text
status.processing = "Processing {current} / {total}: {file}"
```

---

## Validation messages

Зараз validation helper знаходиться тут:

```text
app/gui/validation.py
```

Якщо він повертає готові рядки українською, потрібно змінити це так, щоб validation не був захардкоджений під одну мову.

Для MVP можна зробити простий варіант:

```python
validate_conversion_form(..., language: str = DEFAULT_LANGUAGE) -> list[str]
```

Усередині використовувати:

```python
translate(language, key).format(...)
```

`MainWindow` має передавати поточну мову:

```python
language=self._language
```

Альтернативно можна зробити structured validation errors з keys та params, але для MVP простіше передавати `language`.

---

## Worker logs і core logs

Core service logs можуть залишитися англійськими, якщо їх переклад потребує великого refactor.

Але GUI-generated logs мають перекладатися:

* старт конвертації;
* запит на скасування;
* unexpected GUI/worker error prefix;
* повідомлення про завершення;
* повідомлення про помилку.

Не потрібно зараз переписувати `JobResult.summary()` або core summary, якщо це створює великий refactor.

Можна залишити core summary англійською і зазначити це в README як поточне MVP limitation.

---

## Не локалізувати технічні значення

Не перекладай технічні значення форматів:

```text
jpg
jpeg
png
webp
tif
tiff
```

Вони мають залишатися як є.

Не перекладай:

* file paths;
* extensions;
* технічні module names;
* CLI commands;
* Python package names;
* internal keys.

Наприклад, у `QComboBox` для форматів мають залишитися:

```text
jpg
jpeg
png
webp
tif
tiff
```

а не “зображення JPG” чи “ВебП”.

---

## Persistence

Бажано зберігати вибрану мову між запусками.

Рекомендований варіант — `QSettings`:

```python
from PySide6.QtCore import QSettings
```

Параметри:

```text
organization: ImageFormatConverter
application: ImageFormatConverter
key: language
default: uk
```

Приклад:

```python
settings = QSettings("ImageFormatConverter", "ImageFormatConverter")
language = settings.value("language", DEFAULT_LANGUAGE)
settings.setValue("language", language)
```

Якщо `QSettings` ускладнює тести, можна зробити окремий helper module, наприклад:

```text
app/gui/settings.py
```

Якщо persistence не реалізується, чітко вкажи в README як обмеження MVP.

---

## README

Оновити:

```text
README.md
```

Додати розділ:

```text
GUI language switching
```

Описати:

* GUI підтримує українську та англійську;
* default language: Ukrainian;
* language can be changed in the GUI;
* мова перемикається без перезапуску;
* CLI наразі не локалізується.

Якщо в проєкті вже існує:

```text
README.en.md
```

оновити також його.

Не створювати `README.en.md` з нуля, якщо його немає, без потреби.

---

## AGENTS.md

Оновити `AGENTS.md`, якщо він є.

Додати правила:

* усі нові GUI user-facing strings мають іти через `app/gui/i18n.py`;
* не писати hardcoded UI text напряму в PySide6 widgets;
* при додаванні нового GUI-елемента треба додавати ключі в `TRANSLATIONS`;
* GUI має підтримувати `uk` і `en`;
* default GUI language: `uk`;
* CLI localization не входить у цю задачу;
* core conversion modules не повинні залежати від GUI language;
* не перекладати технічні значення форматів: `jpg`, `jpeg`, `png`, `webp`, `tif`, `tiff`.

---

## Тести

Додати або оновити тести.

### 1. i18n tests

Створити:

```text
tests/test_gui_i18n.py
```

Перевірити:

```python
translate("uk", "button.convert") == "Конвертувати"
translate("en", "button.convert") == "Convert"
```

Також перевірити:

* unknown language fallback;
* missing key fallback;
* fallback на English;
* якщо key відсутній всюди — повертається сам key;
* `SUPPORTED_LANGUAGES` містить `uk` і `en`;
* `DEFAULT_LANGUAGE == "uk"`.

### 2. validation tests

Створити або оновити:

```text
tests/test_gui_validation.py
```

Перевірити:

* validation returns Ukrainian messages for `language="uk"`;
* validation returns English messages for `language="en"`;
* unknown language не ламає validation;
* invalid input path повертає локалізоване повідомлення;
* missing output folder повертає локалізоване повідомлення.

### 3. MainWindow tests

Якщо в проєкті вже є GUI-тести, оновити їх.

Перевірити:

* default language is Ukrainian;
* language selector exists;
* switching to English changes button/label text;
* switching back to Ukrainian restores Ukrainian text;
* switching language does not clear input path;
* switching language does not clear output path;
* switching language does not clear log.

Не робити важкі GUI integration tests, якщо це сильно ускладнює проєкт.

---

## Перевірка після реалізації

Після змін запустити:

```bash
python -m pytest
```

Перевірити CLI:

```bash
python -m app.main --help
```

Перевірити GUI:

```bash
python -m app.gui_main
```

У GUI вручну перевірити:

1. стартова мова — українська;
2. перемикання на English;
3. перемикання назад на Українська;
4. input/output fields не очищаються;
5. validation messages змінюють мову;
6. Convert / Cancel / status / dialogs мають правильну мову;
7. конвертація все ще працює;
8. cancel все ще працює.

---

## Definition of Done

Готово, коли:

* GUI має видимий перемикач мови `Українська / English`;
* default language — українська;
* перемикання на English переводить GUI labels/buttons/status/dialogs на англійську;
* перемикання назад на Українська повертає українську;
* input/output paths не очищаються при перемиканні мови;
* log не очищається при перемиканні мови;
* validation messages відповідають вибраній мові;
* GUI-generated logs відповідають вибраній мові;
* технічні формати `jpg/png/webp/tiff` не перекладаються;
* GUI все ще використовує `ConversionService`;
* CLI не зламаний;
* conversion core не залежить від GUI language;
* `python -m pytest` проходить;
* `python -m app.gui_main` стартує;
* README оновлений;
* AGENTS.md оновлений, якщо він є.

---

## Обмеження

Не реалізовувати зараз:

* web/Vue/React локалізацію;
* повну локалізацію CLI;
* переклад усіх core service logs, якщо це потребує великого refactor;
* нові GUI framework dependencies;
* Qt `.ts/.qm` translation system;
* plugin system;
* database;
* cloud sync;
* audio/video conversion;
* web server.

Ціль: акуратно додати просту, стабільну, двомовну локалізацію GUI до поточного PySide6 MVP без переписування проєкту.
