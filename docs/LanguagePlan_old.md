# План реалізації локалізації GUI

Цей план створений на основі `language.md` для поточного проєкту **Image Format Converter MVP v2 / early MVP v3**.

Мета: додати просту, стабільну українську та англійську локалізацію саме для **PySide6 GUI**, без переписування conversion core і без зміни CLI.

## Головні принципи

- GUI залишається PySide6, не Vue, не web, не Electron.
- CLI не локалізується в цій фазі.
- Core conversion modules не мають залежати від GUI language.
- Усі нові GUI user-facing strings мають проходити через централізований i18n helper.
- Технічні значення форматів `jpg`, `jpeg`, `png`, `webp`, `tif`, `tiff` не перекладати.
- Перемикання мови не має очищати input/output fields, progress або log.
- UI не треба створювати заново при зміні мови; потрібно оновлювати тексти існуючих widgets.

## Фаза 1. Підготовка i18n helper

### Ціль

Створити просту dictionary-based систему перекладів без зовнішніх залежностей.

### Задачі

- Створити файл:

```text
app/gui/i18n.py
```

- Додати константи:

```python
SUPPORTED_LANGUAGES = ("uk", "en")
DEFAULT_LANGUAGE = "uk"
FALLBACK_LANGUAGE = "en"
```

- Додати `TRANSLATIONS` для `uk` і `en`.
- Додати функцію:

```python
def translate(language: str, key: str) -> str:
    ...
```

- Реалізувати fallback logic:
  - unknown language -> `DEFAULT_LANGUAGE`;
  - missing key in selected language -> `FALLBACK_LANGUAGE`;
  - missing key in English -> український переклад;
  - missing key everywhere -> сам key.

### Результат

Є централізований i18n module, який можна використовувати в GUI і validation.

## Фаза 2. Повний набір translation keys

### Ціль

Покрити всі поточні GUI user-facing strings ключами перекладу.

### Задачі

Додати ключі для:

- window title;
- language selector;
- group boxes;
- labels;
- buttons;
- checkboxes;
- placeholders;
- status messages;
- dialog titles/messages;
- validation messages;
- GUI-generated log messages.

Мінімальний список ключів:

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

### Результат

Усі поточні GUI labels/messages мають ключі в `TRANSLATIONS`.

## Фаза 3. MainWindow language state

### Ціль

Додати в `MainWindow` стан поточної мови та helper для перекладу.

### Задачі

- У `app/gui/main_window.py` імпортувати:

```python
from app.gui.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, translate
```

- Додати:

```python
self._language = DEFAULT_LANGUAGE
```

- Додати helper:

```python
def _t(self, key: str) -> str:
    return translate(self._language, key)
```

- Замінити hardcoded GUI text на `_t(...)` там, де це можливо без зміни логіки.

### Результат

`MainWindow` може читати переклади з централізованого словника.

## Фаза 4. Language selector у GUI

### Ціль

Додати видимий перемикач мови.

### Задачі

- Додати `QComboBox` для вибору мови.
- Варіанти:

```text
Українська -> uk
English -> en
```

- Додати label:

```text
Мова:
Language:
```

- Додати handler:

```python
def _on_language_changed(self) -> None:
    language = self.language_combo.currentData()
    self._set_language(language)
```

- Додати:

```python
def _set_language(self, language: str) -> None:
    ...
```

### Результат

Користувач бачить перемикач `Українська / English` у GUI.

## Фаза 5. Retranslate existing UI

### Ціль

Навчити GUI змінювати мову без перезапуску й без перебудови UI.

### Задачі

- Додати метод:

```python
def _retranslate_ui(self) -> None:
    ...
```

- `_retranslate_ui()` має оновлювати:
  - window title;
  - group box titles;
  - labels;
  - buttons;
  - checkboxes;
  - placeholders;
  - language selector label;
  - status label, якщо поточний стан idle/ready/finished/cancelled/failed.

- Не очищати:
  - input path;
  - output path;
  - log;
  - progress;
  - current conversion state.

### Результат

Мова перемикається наживо, стан форми не втрачається.

## Фаза 6. Validation localization

### Ціль

Зробити validation messages двомовними.

### Задачі

- Оновити `app/gui/validation.py`.
- Додати параметр:

```python
language: str = DEFAULT_LANGUAGE
```

- Використовувати:

```python
translate(language, key).format(...)
```

- У `MainWindow.validate_form()` передавати:

```python
language=self._language
```

### Результат

Validation errors відповідають поточній мові GUI.

## Фаза 7. GUI-generated logs і dialogs

### Ціль

Локалізувати GUI-generated messages без великого refactor core.

### Задачі

- Локалізувати:
  - старт конвертації;
  - cancel requested;
  - error prefix;
  - finished/cancelled/failed dialog titles;
  - running conversion close dialog.

- Core service logs і `JobResult.summary()` можна залишити англійськими в MVP.
- У README зазначити, що core summary/logs можуть залишатися англійськими.

### Результат

Основні повідомлення GUI відповідають вибраній мові.

## Фаза 8. Persistence через QSettings

### Ціль

Зберігати вибрану мову між запусками.

### Задачі

- Реалізувати простий helper або прямо використати `QSettings`.
- Параметри:

```text
organization: ImageFormatConverter
application: ImageFormatConverter
key: language
default: uk
```

- При старті `MainWindow` завантажувати language.
- При зміні мови зберігати language.
- Якщо `QSettings` ускладнює тести, винести в маленький helper:

```text
app/gui/settings.py
```

### Результат

Обрана мова зберігається між запусками GUI.

## Фаза 9. Tests для i18n helper

### Ціль

Покрити translation fallback behavior.

### Задачі

Створити:

```text
tests/test_gui_i18n.py
```

Перевірити:

- `translate("uk", "button.convert") == "Конвертувати"`;
- `translate("en", "button.convert") == "Convert"`;
- unknown language fallback;
- missing selected-language key fallback на English;
- missing English key fallback на Ukrainian;
- missing key everywhere returns key;
- `SUPPORTED_LANGUAGES` містить `uk`, `en`;
- `DEFAULT_LANGUAGE == "uk"`.

### Результат

Translation helper має focused unit tests.

## Фаза 10. Tests для validation localization

### Ціль

Переконатися, що validation messages локалізуються.

### Задачі

Оновити:

```text
tests/test_gui_validation.py
```

Додати перевірки:

- українські validation messages для `language="uk"`;
- англійські validation messages для `language="en"`;
- unknown language не ламає validation;
- missing input path локалізується;
- missing output folder локалізується;
- invalid quality локалізується;
- negative resize локалізується.

### Результат

Validation tests підтверджують двомовність.

## Фаза 11. Tests для MainWindow localization

### Ціль

Перевірити GUI language switching без heavy integration tests.

### Задачі

Оновити:

```text
tests/test_gui_main_window.py
```

Додати перевірки:

- default language is Ukrainian;
- language selector exists;
- switching to English changes button/label text;
- switching back to Ukrainian restores Ukrainian text;
- switching language does not clear input path;
- switching language does not clear output path;
- switching language does not clear log;
- format combo values залишаються `jpg`, `jpeg`, `png`, `webp`, `tif`, `tiff`.

### Результат

MainWindow локалізація перевірена тестами без запуску важкого GUI сценарію.

## Фаза 12. README update

### Ціль

Описати локалізацію в документації.

### Задачі

Оновити:

```text
README.md
README.en.md
```

Додати розділ про GUI language switching:

- GUI підтримує українську та англійську;
- default language: Ukrainian;
- мову можна перемикати без перезапуску;
- CLI наразі не локалізується;
- core logs/summary можуть залишатися англійськими в MVP.

### Результат

README пояснює мовний перемикач GUI.

## Фаза 13. AGENTS.md update

### Ціль

Зафіксувати правила для майбутніх GUI text changes.

### Задачі

Оновити `AGENTS.md`:

- усі нові GUI user-facing strings мають іти через `app/gui/i18n.py`;
- не писати hardcoded UI text напряму в widgets;
- при додаванні нового GUI element додавати translation keys;
- GUI підтримує `uk` і `en`;
- default GUI language: `uk`;
- CLI localization не входить у цю задачу;
- core conversion modules не залежать від GUI language;
- не перекладати технічні формати.

### Результат

Майбутні зміни GUI не обходять i18n систему.

## Фаза 14. Automated verification

### Ціль

Переконатися, що зміни не зламали існуючий MVP.

### Команди

Запустити:

```bash
python -m pytest
```

Перевірити CLI:

```bash
python -m app.main --help
```

Перевірити compile:

```bash
python -m compileall app tests
```

### Результат

Тести проходять, CLI не зламаний, код компілюється.

## Фаза 15. Manual GUI verification

### Ціль

Ручно перевірити фактичну поведінку GUI.

### Сценарії

Запустити:

```bash
python -m app.gui_main
```

Перевірити:

1. стартова мова — українська;
2. перемикання на English;
3. перемикання назад на Українська;
4. input field не очищається;
5. output field не очищається;
6. log не очищається;
7. format values не перекладаються;
8. validation messages змінюють мову;
9. Convert / Cancel / status / dialogs мають правильну мову;
10. конвертація все ще працює;
11. cancel все ще працює.

### Результат

GUI локалізація працює у реальному сценарії.

## Фаза 16. Definition of Done

Локалізація GUI вважається готовою, коли:

- GUI має видимий selector `Українська / English`;
- default language — українська;
- English перемикає GUI labels/buttons/status/dialogs на англійську;
- Українська повертає українські тексти;
- input/output/log/progress не очищаються при зміні мови;
- validation messages відповідають поточній мові;
- GUI-generated logs відповідають поточній мові;
- технічні формати не перекладаються;
- GUI все ще використовує `ConversionService`;
- CLI не зламаний;
- core conversion modules не залежать від GUI language;
- `python -m pytest` проходить;
- README оновлений;
- AGENTS.md оновлений.

## Що не входить у цю задачу

Не реалізовувати:

- web/Vue/React локалізацію;
- повну локалізацію CLI;
- великий refactor `ConversionService` для перекладу core logs;
- нові GUI framework dependencies;
- Qt `.ts/.qm` translation system;
- plugin system;
- database;
- cloud sync;
- audio/video conversion;
- web server.
