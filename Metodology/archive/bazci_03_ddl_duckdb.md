# DDL-скрипты для бацзы‑календаря в DuckDB (v0.1)

Ниже приведены шаблоны DDL‑скриптов для создания основных справочников и служебных таблиц, описанных в `bazci_02_calendar_spec.md`. Эти скрипты **не привязаны** к конкретному пути БД и предполагаются к использованию в отдельном setup‑/миграционном скрипте.

Все имена и типы согласованы со спецификацией; при необходимости типы можно уточнить (например, `VARCHAR` вместо `TEXT`).

---

## 1. Справочники стволов и ветвей

```sql
-- Небесные стволы
CREATE TABLE spr_heavenly_stem (
    stem_id        INTEGER PRIMARY KEY,
    stem_char      TEXT NOT NULL,
    stem_pinyin    TEXT,
    stem_rus       TEXT,
    element        TEXT,
    yin_yang       TEXT
);

-- Земные ветви
CREATE TABLE spr_earthly_branch (
    branch_id      INTEGER PRIMARY KEY,
    branch_char    TEXT NOT NULL,
    branch_pinyin  TEXT,
    branch_rus     TEXT,
    element        TEXT,
    yin_yang       TEXT
);
```

---

## 2. Солнечные сезоны и времена их наступления

```sql
-- 24 солнечных сезона
CREATE TABLE spr_solar_term (
    solar_term_id      INTEGER PRIMARY KEY,
    solar_term_char    TEXT NOT NULL,
    solar_term_name_ru TEXT,
    solar_term_pinyin  TEXT,
    longitude_deg      INTEGER NOT NULL,
    month_branch_id    INTEGER NOT NULL,

    FOREIGN KEY (month_branch_id) REFERENCES spr_earthly_branch(branch_id)
);

-- Астрономические моменты прохождения Солнцем заданных долгот
CREATE TABLE t_solar_term_time (
    year           INTEGER NOT NULL,
    solar_term_id  INTEGER NOT NULL,
    longitude_deg  INTEGER NOT NULL,
    crossing_utc   TIMESTAMP NOT NULL,
    crossing_gmt0  TIMESTAMP NOT NULL,

    PRIMARY KEY (year, solar_term_id),
    FOREIGN KEY (solar_term_id) REFERENCES spr_solar_term(solar_term_id)
);
```

---

## 3. Таблица соответствий часов и земных ветвей

```sql
-- 12 двойных часов (Chen) в системе GMT+8
CREATE TABLE spr_hour_branch (
    hour_slot_id     INTEGER PRIMARY KEY,
    branch_id        INTEGER NOT NULL,
    start_hour_gmt8  INTEGER NOT NULL, -- 0..23
    end_hour_gmt8    INTEGER NOT NULL, -- 0..23

    FOREIGN KEY (branch_id) REFERENCES spr_earthly_branch(branch_id)
);
```

---

## 4. Правила формирования столпов месяца и часа

```sql
-- Стандартная схема: небесный ствол года + номер солнечного месяца → небесный ствол месяца
CREATE TABLE spr_pillar_month_rule (
    year_stem_id  INTEGER NOT NULL,
    month_index   INTEGER NOT NULL, -- 1..12
    month_stem_id INTEGER NOT NULL,

    PRIMARY KEY (year_stem_id, month_index),
    FOREIGN KEY (year_stem_id)  REFERENCES spr_heavenly_stem(stem_id),
    FOREIGN KEY (month_stem_id) REFERENCES spr_heavenly_stem(stem_id)
);

-- Стандартная схема: небесный ствол дня + земная ветвь часа → небесный ствол часа
CREATE TABLE spr_pillar_hour_rule (
    day_stem_id     INTEGER NOT NULL,
    hour_branch_id  INTEGER NOT NULL,
    hour_stem_id    INTEGER NOT NULL,

    PRIMARY KEY (day_stem_id, hour_branch_id),
    FOREIGN KEY (day_stem_id)    REFERENCES spr_heavenly_stem(stem_id),
    FOREIGN KEY (hour_branch_id) REFERENCES spr_earthly_branch(branch_id),
    FOREIGN KEY (hour_stem_id)   REFERENCES spr_heavenly_stem(stem_id)
);
```

---

## 5. 60‑летний цикл столпов

```sql
CREATE TABLE spr_pillar_cycle (
    cycle_index  INTEGER PRIMARY KEY, -- 0..59
    stem_id      INTEGER NOT NULL,
    branch_id    INTEGER NOT NULL,

    FOREIGN KEY (stem_id)   REFERENCES spr_heavenly_stem(stem_id),
    FOREIGN KEY (branch_id) REFERENCES spr_earthly_branch(branch_id)
);
```

---

## 6. Временная сетка (почасовая)

Реализация `t_time_grid_hourly` может быть как материализованной таблицей, так и VIEW на основе генератора дат/часов. Ниже приведён вариант в виде таблицы (для явной генерации ряда Python‑скриптом или SQL‑генератором).

```sql
CREATE TABLE t_time_grid_hourly (
    dt_utc   TIMESTAMP NOT NULL,
    dt_gmt0  TIMESTAMP NOT NULL,
    year     INTEGER   NOT NULL,
    month    INTEGER   NOT NULL,
    day      INTEGER   NOT NULL,
    hour     INTEGER   NOT NULL,
    weekday  INTEGER   NOT NULL  -- 1=Пн .. 7=Вс
);
```

---

## 7. Контрольные значения (опциональная служебная таблица)

Импорт из `bazci_control.md` можно оформить через отдельную таблицу.

```sql
CREATE TABLE t_bazi_control (
    date_str          TEXT NOT NULL, -- исходный текстовый формат даты
    time_range        TEXT NOT NULL, -- текст интервала, как в markdown
    dt_start_gmt8     TIMESTAMP,     -- вычисленный момент начала интервала в GMT+8
    dt_start_gmt0     TIMESTAMP,     -- приведённый к GMT+0

    year_stem_char    TEXT,
    year_branch_char  TEXT,
    month_stem_char   TEXT,
    month_branch_char TEXT,
    day_stem_char     TEXT,
    day_branch_char   TEXT,
    hour_stem_char    TEXT,
    hour_branch_char  TEXT
);
```

---

## 8. VIEW `v_bazi_calendar_hourly` (каркас)

Полная реализация VIEW зависит от того, какие части логики будут вынесены в Python (например, расчёт столпов) и какие — реализованы чистым SQL. Здесь приводится минимальный каркас с JOIN‑ами на справочники; в дальнейшем его нужно будет дополнить конкретными выражениями для расчёта.

```sql
CREATE OR REPLACE VIEW v_bazi_calendar_hourly AS
SELECT
    tg.dt_gmt0                          AS dt_gmt0,

    -- День недели (сокращённое русское имя может быть получено через отдельный spr-справочник
    tg.weekday                          AS weekday_num,

    -- Ветвь часа и её русское название
    hb.branch_id                        AS hour_branch_id,
    eb_hour.branch_char                 AS hour_branch_char,
    eb_hour.branch_rus                  AS hour_name_ru,

    -- Сезон (будет уточнён по t_solar_term_time)
    st.solar_term_id                    AS solar_term_id,
    st.solar_term_name_ru               AS solar_term_name_ru,

    -- Заглушки для столпов (будут заменены реальными расчётами/полями)
    NULL::TEXT                          AS year_pillar,
    NULL::TEXT                          AS month_pillar,
    NULL::TEXT                          AS day_pillar,
    NULL::TEXT                          AS hour_pillar,

    NULL::TEXT                          AS year_stem_char,
    NULL::TEXT                          AS year_branch_char,
    NULL::TEXT                          AS month_stem_char,
    NULL::TEXT                          AS month_branch_char,
    NULL::TEXT                          AS day_stem_char,
    NULL::TEXT                          AS day_branch_char,
    NULL::TEXT                          AS hour_stem_char,
    eb_hour.branch_char                 AS hour_branch_char_dup

FROM t_time_grid_hourly tg

-- Присоединение ветви часа через преобразование времени к GMT+8
LEFT JOIN spr_hour_branch hb
    ON 1 = 1  -- в финальном варианте здесь будет условие по dt_gmt0 → t_gmt8 и часам

LEFT JOIN spr_earthly_branch eb_hour
    ON hb.branch_id = eb_hour.branch_id

-- Присоединение сезона по t_solar_term_time и spr_solar_term
LEFT JOIN t_solar_term_time stt
    ON stt.year = tg.year
   -- и дополнительное условие выбора последнего crossing_gmt0 <= tg.dt_gmt0
LEFT JOIN spr_solar_term st
    ON st.solar_term_id = stt.solar_term_id;
```

> **Важно:** текущий каркас VIEW содержит заглушки (`NULL`) и упрощённые `JOIN`‑условия. После реализации Python‑функций и/или SQL‑выражений расчёта столпов и сезона, этот VIEW должен быть доработан:
>
> - добавить корректное определение текущего сезона (по последнему `crossing_gmt0 <= dt_gmt0`),
> - реализовать присвоение столпов года/месяца/дня/часа согласно алгоритмам из `bazci_02_calendar_spec.md`,
> - учесть дублирование строк при смене сезона внутри часа.

---

## 9. Итоги

- В данном файле собраны **DDL‑заготовки** для всех ключевых таблиц бацзы‑календаря и каркас VIEW.
- Следующий шаг — реализовать:
  - наполнение справочников (`spr_*`),
  - астрономический расчёт и заполнение `t_solar_term_time`,
  - Python‑функции расчёта столпов с опорой на эти таблицы,
  - доработку `v_bazi_calendar_hourly` до полноценного представления.
