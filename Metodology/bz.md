# База знаний: ошибки и решения (Calk_KMF)

> Файл для фиксации проблем, с которыми столкнулись при разработке, и их решений.
> Цель: не повторять ошибки, быстро обходить известные сложности.

---

## Ошибка 1: SQLAlchemy 2.0 — raw SQL без `text()`

**Контекст:** Переписывание `tongshu_service.py` для работы с PostgreSQL.

**Симптом:**
```
Textual SQL expression 'SELECT ...' should be explicitly declared as text('SELECT ...')
```

**Причина:** В SQLAlchemy 2.0 передача строки в `db.execute()` требует обёртки `text()` из `sqlalchemy`.

**Решение:**
```python
from sqlalchemy import text
# Было:
result = db.execute("SELECT * FROM t WHERE id = :id", {"id": 1})
# Стало:
result = db.execute(text("SELECT * FROM t WHERE id = :id"), {"id": 1})
```

**Где встречалось:**
- `api/app/services/tongshu_service.py` — все запросы
- `api/app/routers/profiles.py` — `db.execute(sql, ...)`
- `api/app/services/fengshui_service.py` — `db.execute(query, ...)`

---

## Ошибка 2: Pydantic schema mismatch при смене источника данных

**Контекст:** Перевод `tongshu_service.py` с `t_bazi_hourly` на `t_tung_shu_daily`.

**Симптом:**
```
ResponseValidationError: 7 validation errors:
  {'type': 'missing', 'loc': ('response', 'date'), ...}
  {'type': 'missing', 'loc': ('response', 'ten_gods_day'), ...}
```

**Причина:** `TongshuDayData` (старая схема) ожидала поля `date`, `ten_gods_day`, `day_rating`, `suitable_activities`, `unsuitable_activities`, `lunar_month`, `lunar_year`. Новый источник (`t_tung_shu_daily`) возвращал `calendar_date`, `day_officer_*`, `constellation_*`, `belt_*`, `symbolic_stars`.

**Решение:**
1. Переименовать response_model в роутере с `TongshuDayData` на `TongshuDailyData`
2. Убедиться, что `TongshuDailyData` включает все поля из `t_tung_shu_daily`
3. Добавить `symbolic_stars: Optional[List[dict]] = None` в схему

**Файлы:**
- `api/app/schemas/tongshu.py`
- `api/app/routers/tongshu.py`

---

## Ошибка 3: Windows кодировка консоли (cp1251) и Unicode

**Контекст:** Вывод китайских иероглифов и русского текста в консоль Git Bash на Windows.

**Симптом:**
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u7984' in position 28: character maps to <undefined>
```

**Решение:**
1. Перенастроить stdout перед выводом:
```python
import sys
sys.stdout.reconfigure(encoding='utf-8')
```
2. Или использовать `repr()` для вывода:
```python
print(repr(data))
```
3. Или писать в файл с `encoding='utf-8'`

**Правило проекта:** Все Python-скрипты, выводящие Unicode, должны использовать `sys.stdout.reconfigure(encoding='utf-8')` или писать в файл.

---

## Ошибка 4: Uvicorn orphan processes (порт 8000 занят)

**Контекст:** Перезапуск FastAPI сервера после изменений.

**Симптом:**
```
[Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)
```

**Причина:** Процессы uvicorn (reloader + worker) остаются висеть на порту после `kill` или `Ctrl+C`.

**Решение (Windows):**
```bash
# Найти PID
netstat -ano | grep 8000
# Убить через taskkill
cmd //c "taskkill /F /IM python.exe"
# Или перезапустить на другом порту
uvicorn app.main:app --port 8001
```

**Решение (Bash/Git Bash):**
```bash
ps aux | grep uvicorn | grep -v grep
kill -9 <PID_reloader> <PID_worker>
```

---

## Ошибка 5: PostgreSQL `DO $$` блок не работает через psycopg2 + SQLAlchemy

**Контекст:** Попытка добавить колонку условно через `DO $$ BEGIN ... END $$`.

**Симптом:**
```
psycopg2.errors.SyntaxError: ОШИБКА:  ошибка синтаксиса (примерное положение: "3890")
LINE 2:         DO 3890
```

**Причина:** SQLAlchemy/ psycopg2 не корректно обрабатывает `DO $$` блоки при передаче через `text()`.

**Решение:** Проверять наличие колонки через `information_schema.columns` отдельно, затем выполнять `ALTER TABLE`:
```python
inspector = inspect(engine)
cols = [c['name'] for c in inspector.get_columns('table_name')]
if 'column_name' not in cols:
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE ... ADD COLUMN ..."))
```

---

## Ошибка 6: Данные `t_tung_shu_daily` в PostgreSQL не синхронизированы с SQLite

**Контекст:** Добавление `symbolic_stars` в SQLite, ожидание что они появятся в PostgreSQL.

**Симптом:** `symbolic_stars` возвращает `None` из PostgreSQL, хотя в SQLite есть данные.

**Причина:** `t_tung_shu_daily` существует в обеих БД, но заполнялась отдельно. SQLite обновлён, PostgreSQL — нет.

**Решение:** Явная синхронизация:
```python
# Читаем из SQLite, пишем в PostgreSQL
with engine.begin() as conn:
    for row in sqlite_cursor.fetchall():
        conn.execute(text("UPDATE t_tung_shu_daily SET col = :val WHERE date = :date"),
                     {'val': row[1], 'date': row[0]})
```

**Профилактика:** Всегда проверять, что агрегатные таблицы синхронизированы в обеих БД после изменений в генераторе.

---

## Ошибка 7: React `npm run build` зависает

**Контекст:** Сборка frontend после изменений.

**Симптом:** Команда `npm run build` выполняется бесконечно (более 5 минут).

**Причина:** Возможно, процесс create-react-app ждёт ввода или завис на оптимизации.

**Решение:**
1. Запускать в background с перенаправлением в файл:
```bash
npm run build > build.log 2>&1 &
```
2. Или использовать `CI=true npm run build` для CI-режима
3. Проверить, что `NODE_ENV=production`

---

---

## Ошибка 8: Bash на Windows заменяет `$$` на PID процесса

**Контекст:** Выполнение PostgreSQL `DO $$ BEGIN ... END $$` через inline Python (`python -c "..."`) в Git Bash.

**Симптом:**
```
psycopg2.errors.SyntaxError: DO 4222 BEGIN
```

**Причина:** Git Bash интерпретирует `$$` как PID текущего процесса (4222) и подставляет число вместо литерала `$$`.

**Решение:** Никогда не использовать `DO $$` в inline-командах bash. Варианты:
1. Вынести SQL в отдельный Python-скрипт и выполнять `python script.py`
2. Использовать `information_schema.columns` + обычный `ALTER TABLE` без `DO $$`
3. Использовать heredoc или файл с SQL

**Файлы:**
- `tmp_add_br_columns.py`
- `tmp_add_lunar_month.py`

---

## Ошибка 9: React Hook вызван после early return

**Контекст:** Добавление `useState` в компонент `DailyDayView` после проверки `if (!data) return null;`.

**Симптом:**
```
[eslint] React Hook "useState" is called conditionally. React Hooks must be called in the exact same order in every component render.
```

**Причина:** Правило React Hooks: все `useState`, `useEffect`, `useMemo` и т.д. должны вызываться в одном и том же порядке при каждом рендере. Early return (`if (!data) return null;`) прерывает выполнение до хуков, если `data` отсутствует.

**Решение:** ВСЕГДА размещать хуки ДО любых условных return'ов:
```javascript
function DailyDayView({ data }) {
    const [expandedHour, setExpandedHour] = useState(null); // ✅ ДО проверки
    if (!data) return null; // ❌ Если проверка ДО useState — ошибка
    // ...
}
```

**Файлы:**
- `frontend/src/pages/TongShuPage.js`

---

## Ошибка 10: Отсутствие `lunar_month` в `t_tung_shu_daily` блокирует расчёт

**Контекст:** Необходимость вычислить Black Rabbit (Joey Yap) для каждого дня. Алгоритм требует `day_stem`, `day_branch`, `lunar_day`, `lunar_month`.

**Симптом:** `t_tung_shu_daily` содержит `lunar_day`, но не `lunar_month`. Невозможно определить первый день лунного месяца для Black Rabbit.

**Причина:** Генератор `t_tung_shu_daily` не сохранял `lunar_month`, считая его избыточным (есть в `t_bazi_hourly`).

**Решение:**
1. Добавить `lunar_month TEXT` в `t_tung_shu_daily`
2. Извлечь `lunar_month` из первой записи `t_bazi_hourly` для каждого дня
3. Заполнить обе БД (SQLite + PostgreSQL)
4. Обновить Pydantic схему `TongshuDailyData`

**Профилактика:** При проектировании агрегатных таблиц проверять, что все поля, необходимые для downstream-расчётов, включены в схему.

---

## Ошибка 11: Qi Men — несоответствие имён таблиц в коде и БД

**Контекст:** Исправление API endpoints `/api/qimen/charts/{method}` и `/api/qimen/chart/{chart_id}`.

**Симптом:**
```
psycopg2.errors.UndefinedTable: ОШИБКА:  отношение "t_qimen_zhirun_chart" не существует
```

**Причина:** В `qimen_service.py` использовались имена таблиц `t_qimen_zhirun_chart` / `t_qimen_chauby_chart`, тогда как в реальной схеме PostgreSQL таблицы называются `t_qumen_dgiren_hourly/day/month/year` и `t_qumen_chauby_hourly/day` (с "u" вместо "i", lean-архитектура с `rasklad_id` → `spr_qimen_templates`).

**Решение:**
1. Удалить старый `qimen_service.py` с неверными именами таблиц
2. Создать `qimen_pg_service.py`, работающий с реальными таблицами через JOIN с `spr_qimen_templates`
3. В роутере `qimen.py` заменить импорты на новый сервис
4. Добавить fallback: если основной SQL сломается, использовать PostgreSQL-запросы напрямую

**Файлы:**
- `api/app/services/qimen_pg_service.py` (новый)
- `api/app/services/qimen_service.py` (обновлён)
- `api/app/routers/qimen.py` (обновлён)

---

## Ошибка 12: `code/calendar` shadowing стандартной библиотеки `calendar`

**Контекст:** Запуск API сервера из корня проекта с `PYTHONPATH=%PROJECT_ROOT%`.

**Симптом:**
```
ImportError: cannot import name 'monthrange' from 'calendar'
```

**Причина:** В проекте есть директория `code/calendar/` (модуль календаря Бацзы). Когда `PYTHONPATH` включает корень проекта, Python находит `code.calendar` раньше стандартной библиотеки `calendar`. Это ломает `dateutil.parser` и `pg8000.converters`, которые импортируют `calendar.monthrange`.

**Решение:**
1. Запускать сервер из директории `api/` с `sys.path.insert(0, '..')` вместо `PYTHONPATH` из корня
2. Или использовать абсолютные импорты внутри `api/app/main.py`
3. При inline-тестировании через `python -c` — запускать из `api/`:
```bash
cd api && python -c "from app.routers.qimen import router"
```

**Файлы:**
- `start_portal.bat` (пре-Existing issue, не исправлено — требует архитектурного решения)

---

## Ошибка 13: Bash на Windows подменяет `$$` на PID в inline SQL

**Контекст:** Добавление колонок в PostgreSQL через inline Python (`python -c "..."`) в Git Bash.

**Симптом:**
```
psycopg2.errors.SyntaxError: DO 4222 BEGIN
```

**Причина:** Git Bash интерпретирует `$$` как PID текущего процесса и подставляет число.

**Решение:**
1. Никогда не использовать `DO $$ BEGIN ... END $$` в inline-командах bash
2. Вместо этого: проверять `information_schema.columns`, затем выполнять обычный `ALTER TABLE`
3. Лучше всего — выносить DDL в отдельный Python-скрипт и запускать `python script.py`

**Файлы:**
- `scripts/populate_qimen_refs_pg.py` (новый, правильный подход)

---

## Ошибка 14: React `toBeInTheDocument` недоступен без `@testing-library/jest-dom`

**Контекст:** Написание тестов для `QiMenPage.js`.

**Симптом:**
```
TypeError: expect(...).toBeInTheDocument is not a function
```

**Причина:** Проект не импортирует `@testing-library/jest-dom` в тестовых файлах (отсутствует `import '@testing-library/jest-dom'` в setupTests.js или в самом тесте).

**Решение:** Использовать нативные матчеры Jest:
```javascript
// Вместо:
expect(element).toBeInTheDocument();
// Использовать:
expect(element).toBeTruthy();
```

**Файлы:**
- `frontend/src/pages/QiMenPage.test.js`
- `frontend/src/components/qimen/QimenGridV2.test.js`

---

## Ошибка 15: QimenEngine зависит от минимального набора колонок в справочниках

**Контекст:** Добавление `star_char`, `pinyin`, `element` и др. в `spr_stars`, `spr_gates`, `spr_gods`.

**Симптом:** Потенциальный риск: `load_config_from_db()` в `code/common/config.py` читает `SELECT id, name_en, name_ru FROM spr_stars`.

**Причина:** QimenEngine ожидает строго определённый набор колонок. Изменение схемы без проверки может сломать расчёт.

**Решение:**
1. Добавлять новые колонки как `NULLABLE` (не `NOT NULL`)
2. Не удалять и не переименовывать существующие колонки (`id`, `name_en`, `name_ru`)
3. Обновить `load_config_from_db()` для чтения новых колонок (опционально, с fallback)
4. Протестировать engine после изменений: `python code/tests/test_analysis_qimen.py`

**Файлы:**
- `code/common/config.py`
- `scripts/populate_qimen_refs_pg.py`

---

## Ошибка 16: Таблицы `spr_day_officer_value` и `spr_tongshu_constellation` отсутствовали в PostgreSQL

**Контекст:** Перевод `refs.py` на PostgreSQL-only.

**Симптом:**
```
psycopg2.errors.UndefinedTable: отношение "spr_day_officer_value" не существует
```

**Причина:** При миграции SQLite → PostgreSQL некоторые справочники не были перенесены.

**Решение:**
1. Создать таблицы в PostgreSQL с соответствующей структурой
2. Перенести данные из SQLite через Python + SQLAlchemy
3. Проверить все endpoint'ы refs.py после переноса

**Файлы:**
- `api/app/routers/refs.py`

---

## Ошибка 17: Структура `spr_tongshu_black_rabbit_star` в PostgreSQL отличалась от SQLite

**Контекст:** Перевод `refs.py` на PostgreSQL-only.

**Симптом:**
```
psycopg2.errors.UndefinedColumn: колонка "icon_svg" не существует
```

**Причина:** В SQLite таблица была справочником звёзд (star_name, description_ru, nature, color_hex, icon_svg). В PostgreSQL она стала матрицей (cycle_index, lunar_day, method_code, star_name, ...).

**Решение:**
1. Добавить недостающие колонки в PostgreSQL через `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`
2. Или создать отдельную таблицу-справочник

**Файлы:**
- `api/app/routers/refs.py`

---

## Ошибка 18: `code/__init__.py` shadowing стандартной библиотеки `code`

**Контекст:** Запуск pytest для тестов проекта.

**Симптом:**
```
AttributeError: module 'code' has no attribute 'InteractiveConsole'
```

**Причина:** Папка `code/` в корне проекта конфликтует со стандартной библиотекой Python `code` (используется в pdb, pytest).

**Решение:**
1. Для pytest: временно переименовать `code/__init__.py`, запустить тесты, вернуть
2. Для production: проблемы нет, так как сервер запускается из `api/`
3. В долгосрочной перспективе: рассмотреть переименование пакета `code` → `calk_kmf`

**Файлы:**
- `code/__init__.py`

---

## Ошибка 19: Множество справочников `spr_*` отсутствовали в PostgreSQL после миграции

**Контекст:** Перевод тестов и API на PostgreSQL-only.

**Симптом:**
```
psycopg2.errors.UndefinedTable: отношение "spr_tongshu_constellation_cycle" не существует
psycopg2.errors.UndefinedTable: отношение "spr_great_sun_mountain" не существует
psycopg2.errors.UndefinedColumn: колонка "dagua_family" не существует
```

**Причина:** При первоначальной миграции SQLite → PostgreSQL (~2026-02) часть справочников не была перенесена. SQLite оставался fallback, поэтому проблема не проявлялась.

**Решение:**
1. Получить список всех таблиц `spr_*` из SQLite
2. Сравнить с PostgreSQL
3. Автоматически создать недостающие таблицы с правильной структурой
4. Перенести данные через Python + SQLAlchemy
5. Скрипт для проверки синхронности:
```python
sqlite_tables = [r[0] for r in sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'spr_%'")]
pg_tables = [r[0] for r in pg_conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE 'spr_%'"))]
missing = [t for t in sqlite_tables if t not in pg_tables]
```

**Файлы:**
- `code/tongshu/core/tongshu_day.py`
- Все тесты, использующие TongShuDay

---

*Последнее обновление: 2026-06-05*
## Ошибка 20: Остаточный `await` в синхронных роутерах после Phase 10.3

**Контекст:** Перевод всех роутеров на синхронные `def` (Phase 10.3). Некоторые fallback-блоки и декораторы остались асинхронными.

**Симптомы:**
```
SyntaxError: 'await' outside async function
```
- `api/app/routers/qimen.py` — fallback в `get_palace_data` вызывал `await get_qimen_chart(...)`.
- `api/app/routers/refs.py` — декоратор `cache_with_ttl` использовал `await func(...)`.

**Причина:** Роутеры стали синхронными, но внутренние вызовы и декораторы не были переведены.

**Решение:**
1. В fallback `get_palace_data` заменить `await get_qimen_chart(...)` на `qimen_service.get_chart_by_id(db, chart_id)`.
2. В декораторе `cache_with_ttl` заменить `await func(...)` на `func(...)` — все оборачиваемые функции синхронные.

**Файлы:**
- `api/app/routers/qimen.py`
- `api/app/routers/refs.py`

---

## Ошибка 21: `spr_element_display` пуста — `/api/refs/elements` возвращает `[]`

**Контекст:** Проверка endpoint `/api/refs/elements` в регрессионных тестах.

**Симптом:**
```
[FAIL] test_refs_elements: assert len(data) == 5
```

**Причина:** Таблица `spr_element_display` существует в PostgreSQL, но не была заполнена при миграции.

**Решение:** Заполнить таблицу 5 элементами (Вода, Дерево, Огонь, Земля, Металл) с цветовой схемой.

```sql
INSERT INTO spr_element_display (element_id, element_name_ru, element_name_en, element_char, color_hex, bg_color_hex, text_color_hex, display_order) VALUES
(1, 'Вода', 'Water', '水', '#2196F3', '#E3F2FD', '#0D47A1', 1),
(2, 'Дерево', 'Wood', '木', '#4CAF50', '#E8F5E9', '#1B5E20', 2),
(3, 'Огонь', 'Fire', '火', '#F44336', '#FFEBEE', '#B71C1C', 3),
(4, 'Земля', 'Earth', '土', '#FF9800', '#FFF3E0', '#E65100', 4),
(5, 'Металл', 'Metal', '金', '#9E9E9E', '#F5F5F5', '#212121', 5);
```

**Файлы:**
- `api/app/routers/refs.py`
- `data/ddl_full_schema_raw.sql` (если данные должны быть в DDL)

---

## Ошибка 22: UnicodeEncodeError в `test_api_endpoints_http.py` на Windows

**Контекст:** Запуск HTTP-тестов API из Git Bash на Windows.

**Симптом:**
```
'ascii' codec can't encode character '\u7532' in position 37: ordinal not in range(128)
```

**Причина:**
1. `print(...)` выводит китайские иероглифы в консоль Git Bash, которая по умолчанию использует cp1251/cp866.
2. URL с китайскими иероглифами (`/api/qimen/references/stem_combo/甲/丙`) не кодируется перед передачей в `urllib.request.Request`.

**Решение:**
1. Добавить `sys.stdout.reconfigure(encoding='utf-8')` в начало теста.
2. Кодировать каждый сегмент пути через `urllib.parse.quote(segment, safe="")` перед формированием URL.

**Файлы:**
- `code/tests/test_api_endpoints_http.py`

---

## Ошибка 23: `code/calendar` shadowing stdlib `calendar` при запуске `test_tongshu_day_extended.py`

**Контекст:** Запуск Python-теста, импортирующего `code.common.db_manager` → `pg8000` → `dateutil.parser` → `calendar.monthrange`.

**Симптом:**
```
ImportError: cannot import name 'monthrange' from 'calendar' (E:\Project\Calk_KMF\code\calendar\__init__.py)
```

**Причина:** `sys.path.insert(0, project_root)` добавляет корень проекта в начало пути, и Python находит `code.calendar` раньше стандартной библиотеки.

**Решение:** Предварительно загрузить stdlib `calendar` до добавления корня проекта в `sys.path`:
```python
import calendar
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

**Файлы:**
- `code/tests/test_tongshu_day_extended.py`

---

## Ошибка 24: GitHub отклоняет создание репозитория `Calk_KMF`

**Контекст:** Публикация проекта на GitHub через API.

**Симптом:**
```json
{
  "message": "Repository creation failed.",
  "errors": [{
    "resource": "Repository",
    "code": "custom",
    "field": "name",
    "message": "name already exists on this account"
  }]
}
```

**Причина:** Имя `Calk_KMF` недоступно для создания в аккаунте `dkfcnm`. Возможно, репозиторий с таким именем существовал ранее и был удалён, но имя ещё не освободилось, либо зарезервировано.

**Решение:**
1. Проверить существование репозитория через `GET /repos/{owner}/{repo}`.
2. Если репозиторий не существует, но API не позволяет создать — использовать альтернативное имя, сохраняющее смысл (например, `Calk-KMF`).
3. Обновить remote URL и документацию под фактическое имя.

**Файлы:**
- `.git/config`
- `docs/commit-guidelines.md`
- `CHANGELOG.md`

---

## Ошибка 25: Personal Access Token с scope `public_repo` не позволяет удалять репозитории

**Контекст:** Попытка удалить временный тестовый репозиторий `test-calk-kmf-temp`.

**Симптом:**
```json
{
  "message": "Must have admin rights to Repository.",
  "status": 403
}
```

**Причина:** Scope `public_repo` даёт право создавать и изменять публичные репозитории, но не удалять их. Для удаления требуется scope `repo` (полный контроль) или `delete_repo`.

**Решение:**
1. Для публикации и push достаточно `public_repo`.
2. Для удаления репозиториев создавать отдельный токен с scope `repo`/`delete_repo` или удалять вручную через веб-интерфейс.

**Файлы:**
- GitHub Settings → Developer settings → Personal access tokens

---

## Ошибка 26: Первый `git commit` занял слишком много времени

**Контекст:** Создание первого коммита с 349 файлами.

**Симптом:**
```
Auto packing the repository for optimum performance.
```
Команда `git commit` зависла и была убита по таймауту.

**Причина:** Git автоматически запустил `gc` (garbage collection) после первого коммита большого репозитория.

**Решение:**
1. Проверить, что коммит всё-таки создался: `git log --oneline -1`.
2. При необходимости запустить `git gc` вручную заранее.
3. Для больших первичных коммитов увеличить таймаут операции.

**Файлы:**
- `.git/`

---

## Ошибка 27: Git remote/upstream сохраняет URL с токеном

**Контекст:** Настройка upstream branch после `git push -u https://user:TOKEN@github.com/...`.

**Симптом:**
```
[branch "main"]
    remote = https://dkfcnm:ghp_...TOKEN...@github.com/dkfcnm/Calk-KMF.git
```

**Причина:** `git push -u <url>` записывает полный URL с credentials в `.git/config`.

**Решение:**
1. После push обязательно проверить `.git/config`.
2. Установить remote на чистый URL:
```bash
git remote set-url origin https://github.com/dkfcnm/Calk-KMF.git
git config branch.main.remote origin
```
3. Никогда не коммитить `.git/config`.

**Файлы:**
- `.git/config`

---

## Ошибка 28: GitHub Actions workflow не пушится без scope `workflow`

**Контекст:** Попытка запушить файл `.github/workflows/commit-message-check.yml` на GitHub.

**Симптом:**
```
! [remote rejected] main -> main (refusing to allow a Personal Access Token to create or update workflow `.github/workflows/commit-message-check.yml` without `workflow` scope)
error: failed to push some refs to 'https://github.com/dkfcnm/Calk-KMF.git'
```

**Причина:** GitHub требует отдельный scope `workflow` для любых изменений в директории `.github/workflows/`. Scope `public_repo` недостаточно.

**Решение:**
1. Создать новый Personal Access Token с scope `workflow` (или `repo` для полного контроля).
2. Использовать этот токен для push файлов workflow:
```bash
git push https://dkfcnm:TOKEN@github.com/dkfcnm/Calk-KMF.git main
```
3. Альтернатива: создать workflow через веб-интерфейс GitHub (Actions → New workflow) или через GitHub CLI `gh workflow create`.

**Файлы:**
- `.github/workflows/commit-message-check.yml`

---

## Ошибка 29: GitHub Actions runner не стартует в тестовом окружении

**Контекст:** Активация workflow `.github/workflows/commit-message-check.yml` и тестовые запуски.

**Симптом:**
- Workflow создаётся и активируется успешно.
- Статус run: `completed`, `conclusion: failure`.
- В логах только `system.txt`:
  ```
  Job is waiting for a hosted runner to come online.
  Job is about to start running on the hosted runner: GitHub Actions 1000000001
  ```
- Шаги workflow не выполняются, runner не выдаёт логи шагов.

**Причина:** Вероятно, ограничение тестового/sandbox окружения GitHub. Runner назначается, но не может физически запустить job. В реальном production-окружении GitHub Actions runner должен работать корректно.

**Решение:**
1. Убедиться, что workflow YAML валиден (`python -c "import yaml; yaml.safe_load(open('.github/workflows/...'))"`).
2. Проверить, что Actions включены в настройках репозитория.
3. Использовать стабильный runner (`ubuntu-22.04` или `ubuntu-latest`).
4. Если проблема сохраняется в production — проверить billing/limitations аккаунта.

**Файлы:**
- `.github/workflows/commit-message-check.yml`

---

*Последнее обновление: 2026-06-12*
