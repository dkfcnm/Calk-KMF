# Схема расчётных таблиц и представлений бацзы-календаря

Обновлено: 2025-12-31 12:45 (MSK)

## Общие принципы

- Базовая таблица `t_bazi_hourly` хранит расчёты в UTC, но для каждой записи фиксируется локальное время, смещение `tz_offset_hours` и лунные показатели (месяц, день, признак високосного месяца).
- Привязка к часовым поясам осуществляется на стороне таблицы и специализированных view: данные рассчитываются сразу по всем поддерживаемым смещениям (по умолчанию от −12 до +14 часов).
- Все текстовые описания (названия сезонов, часов и т.п.) берутся из справочников `spr_*`, а не дублируются в расчётных таблицах, кроме вспомогательного столбца `solar_term_name` для отладки.
- Любое изменение структуры таблиц/представлений в этом файле **обязательно** сопровождается актуализацией данного описания.
- Комментарии к таблицам и колонкам фиксируются в специализированных справочниках `spr_table_comment` и `spr_column_comment`, которые пересобираются скриптом `code/bazi_calendar/setup_db.py`. Любое изменение DDL должно сопровождаться обновлением записей в этих справочниках.
- Все объекты хранятся в SQLite (`calk_kmf.sqlite`). Функции, работающие с таблицей и view, находятся в пакете `code.bazi_calendar.hourly`.

## Таблица t_bazi_hourly (расчётная, UTC)

Назначение: хранение китайских двухчасовок бацзы в UTC и локальном времени для заданного диапазона лет.

Создаётся и заполняется функциями `ensure_bazi_hourly_table`, `populate_bazi_hourly_table` и `populate_bazi_hourly_for_years` из модуля `code.bazi_calendar.hourly`.

### Столбцы

- `tz_offset_hours INTEGER NOT NULL`
  - Смещение локального времени относительно UTC, часы (может принимать значения от −12 до +14).
- `slot_start_date_utc TEXT NOT NULL`
  - Дата начала двухчасовки в UTC (формат `YYYY-MM-DD`).
- `slot_start_time_utc TEXT NOT NULL`
  - Время начала двухчасовки в UTC (формат `HH:MM`).
- `slot_end_date_utc TEXT NOT NULL`
  - Дата окончания двухчасовки в UTC (учитывая возможный переход через сутки).
- `slot_end_time_utc TEXT NOT NULL`
  - Время окончания двухчасовки в UTC.
- `slot_start_date_local TEXT NOT NULL`
  - Дата начала двухчасовки в локальном времени, уже со смещением `tz_offset_hours`.
- `slot_start_time_local TEXT NOT NULL`
  - Время начала двухчасовки в локальном времени.
- `slot_end_date_local TEXT NOT NULL`
  - Дата окончания двухчасовки в локальном времени.
- `slot_end_time_local TEXT NOT NULL`
  - Время окончания двухчасовки в локальном времени.
- `weekday_local TEXT NOT NULL`
  - Сокращённое русское обозначение дня недели для локального времени (`Пн`, `Вт`, ...).
- `solar_term_id INTEGER NOT NULL`
  - Идентификатор солнечного сезона из `spr_solar_term`.
- `solar_term_name TEXT`
  - Русское название сезона (опционально, для отладки). Во view предпочтительно подтягивать значения из справочника.
- `year_pillar`, `month_pillar`, `day_pillar`, `hour_pillar` TEXT NOT NULL
  - Столпы года, месяца, дня и часа в виде конкатенации ствола и ветви.
  - **Методология расчета:**
    - **Год и Месяц:** Определяются по астрономическим моментам смены солнечных сезонов (Solar Terms). Момент смены сезона един для всей планеты (UTC), но дата начала года/месяца может варьироваться в зависимости от часового пояса (когда этот момент наступает в локальном времени).
    - **День и Час:** Определяются строго по **локальному времени** (`slot_start_time_local`). Смена суток (столпа Дня) происходит в 23:00 локального времени (начало часа Крысы). Смена столпа Часа происходит каждые 2 часа по локальному времени (23:00, 01:00, 03:00 и т.д.), независимо от астрономических событий.
- `year_stem`, `year_branch`, `month_stem`, `month_branch`, `day_stem`, `day_branch`, `hour_stem`, `hour_branch` TEXT NOT NULL
  - Отдельные символы небесных стволов и земных ветвей для каждого столпа.
- `lunar_month INTEGER NOT NULL`
  - Номер лунного месяца китайского календаря (1–12) либо 0, если дата вне диапазона расчётов конвертера.
- `lunar_day INTEGER NOT NULL`
  - Номер лунного дня (1–30) либо 0 при отсутствии данных.
- `lunar_is_leap INTEGER NOT NULL`
  - Флаг високосного (дополнительного) месяца: 1 — високосный, 0 — обычный.
- `lunar_month_zi INTEGER NOT NULL`

### Ключи и индексы

- Первичный ключ: `PRIMARY KEY (tz_offset_hours, slot_start_date_utc, slot_start_time_utc)`.
- Вспомогательный индекс: `idx_bazi_hourly_local` по `(tz_offset_hours, slot_start_date_local, slot_start_time_local)` для ускорения выборок локальных представлений.

## Представление v_bazi_hourly (UTC)

Назначение: удобное чтение двухчасовых слотов бацзы в UTC/локальном представлении с подтягиванием русских названий сезонов и часов из справочников.

Создаётся функцией `create_bazi_hourly_views` (модуль `code.bazi_calendar.hourly`).

### Источник данных

- Базовая таблица: `t_bazi_hourly`.
- Справочники:
  - `spr_solar_term(solar_term_id, solar_term_name_ru, ...)` — сезоны;
  - `spr_earthly_branch(branch_char, branch_rus, ...)` — земные ветви с русскими названиями.
- `t_bazi_hourly.lunar_month`, `lunar_day`, `lunar_is_leap` заимствуются из конвертера китайского лунного календаря (`code.bazi_calendar.lunar`).

### Логика

Условный SQL (упрощённо):

```sql
CREATE VIEW v_bazi_hourly AS
SELECT
    t.tz_offset_hours,
    t.slot_start_date_utc,
    t.slot_start_time_utc,
    t.slot_end_date_utc,
    t.slot_end_time_utc,
    t.slot_start_date_local,
    t.slot_start_time_local,
    t.slot_end_date_local,
    t.slot_end_time_local,
    t.weekday_local,
    t.solar_term_id,
    st.solar_term_name_ru,
    t.solar_term_name,
    t.year_pillar,
    t.month_pillar,
    t.day_pillar,
    t.hour_pillar,
    t.year_stem,
    t.year_branch,
    t.month_stem,
    t.month_branch,
    t.day_stem,
    t.day_branch,
    t.hour_stem,
    t.hour_branch AS hour_branch_char,
    t.lunar_month,
    t.lunar_day,
    t.lunar_is_leap,
    t.lunar_month_zi,
    t.lunar_day_zi,
    t.lunar_is_leap_zi,
    eb.branch_rus AS hour_name_ru
FROM t_bazi_hourly AS t
LEFT JOIN spr_solar_term AS st
       ON st.solar_term_id = t.solar_term_id
LEFT JOIN spr_earthly_branch AS eb
       ON eb.branch_char = t.hour_branch
WHERE 1 = 1
  AND t.slot_start_date_utc >= date('now')
ORDER BY t.tz_offset_hours, t.slot_start_date_utc, t.slot_start_time_utc;
```

## Представления `v_bazi_hourly_tz_*` (все часовые пояса)

Назначение: доступ к данным `t_bazi_hourly` в локальном времени для каждого поддерживаемого смещения `tz_offset_hours`.

- Формат имени: `v_bazi_hourly_tz_{suffix}`, где `suffix` имеет вид `pHH` для положительных/нулевого смещения и `mHH` для отрицательных. Примеры: `v_bazi_hourly_tz_p03` (UTC+3), `v_bazi_hourly_tz_m08` (UTC−8), `v_bazi_hourly_tz_p14` (UTC+14).
- Источник данных: `v_bazi_hourly`, фильтр по `tz_offset_hours`.
- Список колонок идентичен `v_bazi_hourly`, включая лунные показатели (в том числе `*_zi`), но локальные столбцы `slot_start_*_local`, `slot_end_*_local` и `weekday_local` отражают время конкретного часового пояса.
- Представления создаются функцией `create_bazi_hourly_views`, принимающей список смещений (по умолчанию диапазон −12…+14).

## Представление v_bazi_hourly_msk (Москва, UTC+3)

- Псевдоним для `v_bazi_hourly_tz_p03`, оставлен для обратной совместимости и удобства.
- Колонки повторяют `v_bazi_hourly_tz_p03`, но локальные временные столбцы переименованы в московские (`slot_start_*_msk`, `slot_end_*_msk`, `weekday_msk`). Лунные поля сохраняются без переименования.
- Создаётся автоматически функцией `create_bazi_hourly_views` при передаче `default_offset_hours=3`.

## Правило уровня проекта

- **Любое изменение структуры** следующих объектов:
  - таблица `t_bazi_hourly`;
  - представление `v_bazi_hourly`;
  - представление `v_bazi_hourly_msk`;
  - а также любых связанных с ними расчётных таблиц для бацзы-календаря,

обязательно сопровождается обновлением данного файла `bazci_04_schema_bazi_hourly.md` в папке `Metodology`.

- При добавлении новых расчётных таблиц/представлений для бацзы-календаря:
  - нужно добавить раздел с описанием столбцов (имя, тип, назначение);
  - описать связь с существующими `spr_*` справочниками и используемую часовую зону.
  - в DDL таблиц обязательно оставлять комментарии (комментарий к таблице и к каждому полю), фиксируя их в коде.

- Массовое наполнение `t_bazi_hourly` выполняется функцией `populate_bazi_hourly_for_years`, которая обеспечивает расчёты по всем указанным часовым поясам и диапазону лет. Перед запуском следует убедиться в наличии данных по солнечным сезонам `t_solar_term_time`/`t_solar_term_time_hko` для нужного диапазона.
- При обновлении данных рекомендуется использовать вспомогательный скрипт `code/bazi_calendar/run_update.py`, который пересоздаёт таблицу и view с учётом лунных полей.
- Контрольные данные (`control_pillars_utc.csv`, таблица `t_control_pillars`) поддерживаются скриптом `rebuild_control_data.py`; он использует `calc_four_pillars` и автоматически приводит контрольные столпы в соответствие с приоритетом HKO.

- Скрипты/функции, создающие/изменяющие эти таблицы и view (в частности, в `bazi_calendar.py`), должны рассматриваться как изменяющие **схему проекта**, а не только данные. Перед коммитом или фиксацией таких изменений необходимо проверить и актуализировать этот файл.

## Справочники бацзы и календаря

В этом разделе описаны ключевые справочные таблицы (`spr_*`), используемые при расчёте бацзы‑календаря.

### Таблица spr_heavenly_stem (небесные стволы)

Назначение: справочник небесных стволов.

Столбцы:

- `stem_id INTEGER PRIMARY KEY`
  - Идентификатор ствола (1–10).

- `stem_char TEXT NOT NULL`
  - Иероглиф ствола (甲, 乙, 丙, ...).

- `stem_pinyin TEXT`
  - Латинская транскрипция (пининь).

- `stem_rus TEXT`
  - Русская транскрипция/название.

- `element TEXT`
  - Стихия, связанная со стволом.

- `yin_yang TEXT`
  - Полярность: Инь/Ян.

### Таблица spr_earthly_branch (земные ветви)

Назначение: справочник земных ветвей.

Столбцы:

- `branch_id INTEGER PRIMARY KEY`
  - Идентификатор ветви (1–12).

- `branch_char TEXT NOT NULL`
  - Иероглиф ветви (子, 丑, 寅, ...).

- `branch_pinyin TEXT`
  - Пининь.

- `branch_rus TEXT`
  - Русское название ветви (Тигр, Кролик и т.п.).

- `element TEXT`
  - Стихия ветви.

- `yin_yang TEXT`
  - Полярность: Инь/Ян.

### Таблица spr_solar_term (солнечные сезоны)

Назначение: справочник 24 солнечных сезонов.

Столбцы:

- `solar_term_id INTEGER PRIMARY KEY`
  - Идентификатор сезона (1–24).

- `solar_term_char TEXT NOT NULL`
  - Китайское название сезона (иероглифы).

- `solar_term_name_ru TEXT`
  - Русское название сезона.

- `solar_term_pinyin TEXT`
  - Пининь.

- `longitude_deg INTEGER NOT NULL`
  - Эклиптическая долгота Солнца, при которой наступает сезон.

- `month_branch_id INTEGER NOT NULL`
  - Ссылка на земную ветвь месяца (`spr_earthly_branch.branch_id`).

### Таблица spr_hour_branch (ветви часов)

Назначение: соответствие часовых слотов (Chen) и земных ветвей в GMT+8.

Столбцы:

- `hour_slot_id INTEGER PRIMARY KEY`
  - Идентификатор часового слота (1–12).

- `branch_id INTEGER NOT NULL`
  - Ссылка на земную ветвь (`spr_earthly_branch.branch_id`).

- `start_hour_gmt8 INTEGER NOT NULL`
  - Час начала слота в GMT+8 (0–23).

- `end_hour_gmt8 INTEGER NOT NULL`
  - Час окончания слота в GMT+8 (0–23), возможен переход через полночь.

### Таблица spr_pillar_cycle (60‑летний/60‑дневный цикл Дзя‑Цзы)

Назначение: сопоставление индекса цикла (0–59) паре (ствол, ветвь).

Столбцы:

- `cycle_index INTEGER PRIMARY KEY`
  - Индекс пары ствол+ветвь в 60‑летнем цикле (0–59).

- `stem_id INTEGER NOT NULL`
  - Ссылка на `spr_heavenly_stem.stem_id`.

- `branch_id INTEGER NOT NULL`
  - Ссылка на `spr_earthly_branch.branch_id`.

### Таблица spr_pillar_month_rule (правила столпа месяца)

Назначение: определение небесного ствола месяца по небесному стволу года и индексу месяца.

Столбцы:

- `year_stem_id INTEGER NOT NULL`
  - Идентификатор ствола года (`spr_heavenly_stem.stem_id`).

- `month_index INTEGER NOT NULL`
  - Индекс солнечного месяца (1–12).

- `month_stem_id INTEGER NOT NULL`
  - Идентификатор ствола месяца (`spr_heavenly_stem.stem_id`).

### Таблица spr_pillar_hour_rule (правила столпа часа)

Назначение: определение ствола часа по стволу дня и ветви часа.

Столбцы:

- `day_stem_id INTEGER NOT NULL`
  - Идентификатор ствола дня (`spr_heavenly_stem.stem_id`).

- `hour_branch_id INTEGER NOT NULL`
  - Идентификатор ветви часа (`spr_earthly_branch.branch_id`), как в `spr_hour_branch`.

- `hour_stem_id INTEGER NOT NULL`
  - Идентификатор ствола часа (`spr_heavenly_stem.stem_id`).


## Вспомогательные расчётные таблицы

### Таблица t_solar_term_time (моменты смены сезонов)

Назначение: хранение астрономических моментов наступления 24 сезонов по годам.

Столбцы:

- `year INTEGER NOT NULL`
  - Григорианский год.

- `solar_term_id INTEGER NOT NULL`
  - Ссылка на `spr_solar_term.solar_term_id`.

- `longitude_deg INTEGER NOT NULL`
  - Эклиптическая долгота Солнца в момент смены сезона (должна совпадать с `spr_solar_term.longitude_deg`).

- `crossing_utc TIMESTAMP NOT NULL`
  - Момент смены сезона в UTC.

- `crossing_gmt0 TIMESTAMP NOT NULL`
  - Дублирующее поле для хранения/отладки (эквивалент UTC).

### Таблица t_time_grid_hourly (часовая сетка времени)

Назначение: базовая часовая временная сетка в UTC для заданного диапазона лет.

Столбцы:

- `dt_utc TIMESTAMP NOT NULL`
  - Момент часа в UTC.

- `dt_gmt0 TIMESTAMP NOT NULL`
  - Дублирующее поле GMT0 (эквивалент UTC).

- `year INTEGER NOT NULL`, `month INTEGER NOT NULL`, `day INTEGER NOT NULL`, `hour INTEGER NOT NULL`
  - Компоненты календарной даты/времени.

- `weekday INTEGER NOT NULL`
  - Номер дня недели (0–6), соответствующий `dt_utc`.

### Таблица t_bazi_control (контрольные примеры бацзы)

Назначение: хранение контрольных дат/часов и ожидаемых столпов для тестирования корректности расчётов.

Столбцы:

- `date_str TEXT NOT NULL`
  - Дата в строковом формате (для человека).

- `time_range TEXT NOT NULL`
  - Описание диапазона времени (например, часового слота).

- `dt_start_gmt8 TIMESTAMP`
  - Время начала интервала в GMT+8.

- `dt_start_gmt0 TIMESTAMP`
  - Время начала интервала в GMT0/UTC.

- `year_stem_char TEXT`, `year_branch_char TEXT`
  - Ожидаемый ствол и ветвь года.

- `month_stem_char TEXT`, `month_branch_char TEXT`
  - Ожидаемый ствол и ветвь месяца.

- `day_stem_char TEXT`, `day_branch_char TEXT`
  - Ожидаемый ствол и ветвь дня.

- `hour_stem_char TEXT`, `hour_branch_char TEXT`
  - Ожидаемый ствол и ветвь часа.

### Таблица spr_table_comment (комментарии к таблицам)

Назначение: централизованное хранение пояснений по назначению таблиц и представлений.

Столбцы:

- `table_name TEXT PRIMARY KEY`
  - Имя таблицы или представления из файла `sqlite_master`.

- `comment_text TEXT NOT NULL`
  - Развёрнутое описание назначения.

Таблица автоматически очищается и заполняется актуальными данными при выполнении `setup_db.py`.

### Таблица spr_column_comment (комментарии к колонкам)

Назначение: хранение назначений всех колонок таблиц/представлений проекта.

Столбцы:

- `table_name TEXT NOT NULL`
  - Объект, к которому относится колонка.

- `column_name TEXT NOT NULL`
  - Имя колонки.

- `comment_text TEXT NOT NULL`
  - Описание значения/назначения.

Первичный ключ составной `(table_name, column_name)`. Таблица поддерживается скриптом `setup_db.py` синхронно с `spr_table_comment`.
