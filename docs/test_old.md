Ти — senior Python developer, code reviewer, QA engineer і security reviewer.

**Image Format Converter MVP v2**. Проведи повний технічний аудит проєкту.

## Контекст проєкту

Це локальна Python-програма для конвертації зображень.

Поточний стан:

* MVP v1: CLI-конвертер зображень;
* MVP v2: доданий GUI на PySide6;
* є підтримка звичайних форматів:

  * JPG / JPEG
  * PNG
  * WEBP
  * TIF / TIFF
* є підтримка RAW-файлів камер:

  * NEF
  * CR2
  * ARW
  * DNG
* RAW-конвертація працює через `rawpy`;
* `rawpy` має бути lazy dependency, тобто програма не повинна падати без `rawpy`, якщо користувач конвертує тільки звичайні формати;
* CLI має запускатися через:

```bash
python -m app.main
```

* GUI має запускатися через:

```bash
python -m app.gui_main
```

* GUI має використовувати існуюче ядро `ConversionService`, а не дублювати логіку конвертації.

## Головна ціль аудиту

Перевір, чи MVP v2 реалізований правильно:

1. архітектура;
2. якість коду;
3. баги;
4. потенційні баги;
5. edge cases;
6. безпека;
7. стабільність;
8. тестове покриття;
9. GUI-логіка;
10. CLI-логіка;
11. робота з RAW;
12. робота з файлами й папками;
13. готовність до майбутнього MVP v3.

Не переписуй увесь проєкт з нуля. Спочатку зроби аудит і дай висновки.

---

## Що потрібно перевірити

### 1. Загальна структура проєкту

Перевір:

* чи нормальна структура папок;
* чи немає хаосу в модулях;
* чи не лежить уся логіка в одному файлі;
* чи є правильне розділення:

  * CLI;
  * GUI;
  * core;
  * converters;
  * tests;
* чи немає дублювання логіки між CLI і GUI;
* чи немає зайвих файлів у проєкті:

  * `.git`;
  * `__pycache__`;
  * `.pytest_cache`;
  * `.pyc`;
  * тимчасові файли;
  * зайві архіви.

---

### 2. Архітектура

Особливо перевір:

* чи `ConversionService` є центральним ядром конвертації;
* чи CLI використовує `ConversionService`;
* чи GUI використовує `ConversionService`;
* чи GUI не дублює pipeline конвертації;
* чи `ConversionOptions` нормально використовується і в CLI, і в GUI;
* чи `ConverterRegistry` правильно вибирає конвертери;
* чи `ImageConverter` і `RawConverter` не змішують відповідальність;
* чи `file_scanner.py`, `path_utils.py`, `job_result.py` мають чітку відповідальність.

Оціни архітектуру за шкалою від 1 до 10 і поясни чому.

---

### 3. CLI audit

Перевір CLI:

* чи працює `python -m app.main`;
* чи всі аргументи працюють:

  * `--input`;
  * `--output`;
  * `--to`;
  * `--quality`;
  * `--recursive`;
  * `--overwrite`;
  * `--keep-structure`;
  * `--resize-width`;
  * `--resize-height`;
  * `--verbose`;
* чи є нормальна валідація аргументів;
* чи не падає програма на поганих шляхах;
* чи нормально створюється output-папка;
* чи є зрозумілі помилки;
* чи не ламається batch-конвертація через один проблемний файл;
* чи коректно працює summary.

Перевір приклади:

```bash
python -m app.main --input "test_data/input/test.png" --output "test_data/out" --to jpg --quality 92
```

```bash
python -m app.main --input "test_data/input" --output "test_data/out" --to webp --quality 85 --recursive
```

```bash
python -m app.main --input "test_data/input" --output "test_data/out" --to png --recursive --keep-structure
```

---

### 4. GUI audit

Перевір GUI:

* чи запускається `python -m app.gui_main`;
* чи GUI не блокується під час конвертації;
* чи конвертація запускається в окремому worker thread;
* чи використовується `QThread` або інший правильний механізм PySide6;
* чи немає прямої важкої роботи в UI thread;
* чи кнопка Convert блокується під час виконання;
* чи не можна запустити дві конвертації паралельно;
* чи progress bar оновлюється правильно;
* чи log section показує корисну інформацію;
* чи помилки показуються нормально;
* чи після завершення worker/thread коректно очищаються;
* чи немає ризику memory leak або dangling thread;
* чи GUI коректно обробляє:

  * вибір одного файлу;
  * вибір папки;
  * вибір output-папки;
  * recursive;
  * keep structure;
  * overwrite;
  * quality;
  * resize width/height;
  * RAW без `rawpy`.

Особливо перевір PySide6 signals/slots і роботу `ConversionWorker`.

---

### 5. RAW conversion audit

Перевір RAW-логіку:

* чи `rawpy` не імпортується на верхньому рівні модуля;
* чи програма запускається без `rawpy`, якщо не конвертуються RAW-файли;
* чи при RAW-конвертації без `rawpy` показується зрозуміла помилка;
* чи RAW підтримує тільки дозволені output formats;
* чи RAW → WEBP заборонений, якщо так заплановано;
* чи `raw.postprocess()` використовується адекватно;
* чи помилки RAW-файлів не валять всю batch-обробку.

---

### 6. Regular image conversion audit

Перевір `ImageConverter`:

* JPG → PNG;
* PNG → JPG;
* PNG з прозорістю → JPG;
* WEBP → JPG;
* TIFF/TIF → JPG;
* resize по ширині;
* resize по висоті;
* resize по ширині + висоті без спотворення;
* JPEG/WebP quality;
* EXIF orientation через `ImageOps.exif_transpose`;
* коректну роботу з alpha-channel;
* коректне збереження RGB для JPEG.

Особливо перевір, чи PNG з alpha-каналом не викликає помилку при збереженні в JPG.

---

### 7. File scanning і output paths

Перевір:

* сканування одного файлу;
* сканування папки без recursive;
* сканування папки з recursive;
* ігнорування непідтримуваних файлів;
* підтримку `.tif` і `.tiff`;
* поведінку `--keep-structure`;
* поведінку `--overwrite`;
* unique naming:

  * `photo.jpg`;
  * `photo_1.jpg`;
  * `photo_2.jpg`;
* що output files не перезаписуються випадково;
* що output directory не потрапляє в повторне сканування, якщо вона знаходиться всередині input directory.

Якщо output-папка всередині input-папки може створити проблему — вкажи це як баг або потенційний баг.

---

### 8. Security audit

Проєкт локальний, але все одно перевір:

* path traversal ризики;
* небезпечну роботу з файлами;
* випадкове перезаписування даних;
* обробку пошкоджених/величезних зображень;
* ризик image decompression bomb у Pillow;
* обробку symlink-ів;
* нескінченне рекурсивне сканування;
* output directory всередині input directory;
* чи немає виконання shell-команд;
* чи немає небезпечного `eval`, `exec`;
* чи немає хардкодів секретів;
* чи немає зайвого доступу до мережі;
* чи немає небезпечного логування приватних даних.

Дай список security-ризиків за рівнем:

* Critical;
* High;
* Medium;
* Low;
* Informational.

---

### 9. Tests audit

Перевір тести:

* чи проходить `pytest`;
* які частини покриті тестами;
* які частини не покриті;
* чи є тести для:

  * path utils;
  * file scanner;
  * image converter;
  * raw converter lazy dependency;
  * registry;
  * conversion service;
  * CLI;
  * GUI helper logic;
* чи потрібні GUI integration tests;
* чи тести не залежать від реальних RAW-файлів;
* чи тести не крихкі;
* чи тести не створюють сміття після себе.

Запропонуй, які тести додати першочергово.

---

### 10. Dependency audit

Перевір:

* `requirements.txt`;
* чи немає зайвих залежностей;
* чи всі потрібні залежності вказані;
* чи PySide6 доданий правильно;
* чи `rawpy` описаний у README;
* чи можна відокремити optional dependencies у майбутньому;
* чи не варто у майбутньому перейти на `pyproject.toml`.

Не потрібно обов’язково мігрувати на `pyproject.toml` зараз, просто дай рекомендацію.

---

### 11. README / AGENTS.md audit

Перевір документацію:

* чи README пояснює CLI;
* чи README пояснює GUI;
* чи є приклади запуску;
* чи описані підтримувані формати;
* чи описані обмеження MVP v2;
* чи описана lazy dependency `rawpy`;
* чи AGENTS.md відповідає фактичній архітектурі;
* чи немає застарілих інструкцій.

---

### 12. Performance audit

Перевір:

* чи batch-конвертація не тримає зайві дані в пам’яті;
* чи великі RAW-файли не створюють очевидних проблем;
* чи GUI не зависає;
* чи немає неефективного повторного сканування;
* чи можна в майбутньому додати cancel/progress/pause;
* чи є сенс додати обмеження на максимальний розмір файлу або попередження.

---

## Формат відповіді

Дай відповідь у такій структурі:

```text
# Audit Report: Image Format Converter MVP v2

## 1. Executive Summary

Короткий висновок: чи MVP v2 нормальний, чи можна вважати його робочим.

Оцінки:
- Architecture: X/10
- Code quality: X/10
- Stability: X/10
- Security: X/10
- Test coverage: X/10
- GUI implementation: X/10
- CLI compatibility: X/10

## 2. What Works Well

Список того, що зроблено правильно.

## 3. Critical Issues

Тільки реально критичні проблеми. Якщо їх немає — напиши “No critical issues found”.

## 4. High Priority Issues

Проблеми, які бажано виправити перед тим, як вважати MVP v2 завершеним.

Для кожної проблеми:
- файл;
- проблема;
- чому це важливо;
- як виправити.

## 5. Medium Priority Issues

Проблеми, які можна виправити після high-priority.

## 6. Low Priority / Cleanup

Косметика, чистка архіву, README, naming, style.

## 7. Security Findings

З класифікацією Critical/High/Medium/Low/Info.

## 8. Architecture Review

Оціни, чи правильно зроблено CLI + GUI через `ConversionService`.

## 9. GUI Review

Оціни PySide6 реалізацію, worker thread, signals, validation, UX.

## 10. CLI Review

Оціни CLI, аргументи, помилки, сумісність з MVP v1.

## 11. Tests Review

Що є, чого не вистачає, які тести додати.

## 12. Dependency Review

Оціни залежності й requirements.txt.

## 13. Recommended Fix Plan

Дай конкретний план виправлень у порядку пріоритету:

1. ...
2. ...
3. ...

## 14. Suggested Patch Prompt

Напиши окремий промпт, який я зможу потім дати AI-агенту, щоб він виправив знайдені проблеми без переписування всього проєкту.

## 15. Final Verdict

Чітко скажи:
- MVP v2 готовий / майже готовий / не готовий;
- що обов’язково виправити;
- що можна залишити на MVP v3.
```

---

## Важливі правила аудиту

* Не вигадуй проблеми, яких немає.
* Не переписуй проєкт з нуля.
* Не пропонуй занадто складну enterprise-архітектуру.
* Не вимагай Docker, CI/CD, базу даних або web server для MVP.
* Не пропонуй audio/video conversion зараз.
* Не пропонуй повний plugin manager зараз.
* Орієнтуйся на реальний MVP для локального desktop/CLI застосунку.
* Якщо проблема не критична для MVP, познач її як Medium або Low.
* Якщо щось не можеш перевірити через відсутність середовища або GUI, чесно напиши це.
* Даючи рекомендації, пояснюй, чому саме це важливо.
