# Детальный аудит базы данных Calk_KMF (SQLite)

**Дата аудита:** 2026-05-16  
**Файл БД:** `calk_kmf.sqlite`  
**Размер БД:** 4,792.76 MB (~4.7 GB)  
**Режим:** Только чтение (read-only)

---

## 1. Общая сводка

| Показатель | Значение |
|-----------|----------|
| Всего таблиц | **71** |
| Views | **34** |
| Индексов | **20** |
| Основные таблицы (t_*) | 24 |
| Справочники (spr_*) | 37 |
| Контрольные таблицы (t_control_*) | 10 |

---

## 2. Категоризация таблиц

### 2.1. Основные таблицы результатов (24)

| Таблица | Строк | Индексов | Примечание |
|---------|-------|----------|------------|
| `t_analysis_date` | **14,466,428** | 0 | 🔴 Критично: нет индексов |
| `t_flying_stars` | 2,017,809 | 1 | |
| `t_qumen_chauby_hourly` | 2,017,809 | 1 | |
| `t_qumen_dgiren_hourly` | 2,017,809 | 1 | |
| `t_analysis_direction` | 1,793,608 | 0 | 🔴 Критично: нет индексов |
| `t_bazi_hourly` | 354,807 | 12 | |
| `t_analyz_direction` | 34,448 | 0 | 🟡 Возможное дублирование |
| `t_qumen_chauby_day` | 6,642 | 0 | |
| `t_qumen_dgiren_day` | 6,642 | 0 | |
| `t_solar_term_time` | 3,960 | 0 | |
| `t_qumen_chauby_month` | 207 | 0 | |
| `t_qumen_dgiren_month` | 207 | 0 | |
| `t_rule_scope` | 155 | 0 | |
| `t_rule_registry` | 147 | 0 | FK-центр |
| `t_sys_calculation_log` | 109 | 0 | |
| `t_qumen_chauby_year` | 18 | 0 | |
| `t_qumen_dgiren_year` | 18 | 0 | |
| `t_analysis_activation` | 0 | 0 | Пустая |
| `t_analyz_activation` | 0 | 0 | Пустая, дубль? |
| `t_analyz_data` | 0 | 0 | Пустая |
| `t_analyz_date` | 0 | 0 | Пустая, дубль? |
| `t_chart_analysis` | 0 | 0 | Пустая |
| `t_solar_term_time_hko` | 72 | 0 | |
| `t_time_grid_hourly` | 0 | 0 | Пустая |

### 2.2. Справочники (37)

| Таблица | Строк | Индексов | Примечание |
|---------|-------|----------|------------|
| `spr_qimen_templates` | 9,720 | 2 | ✅ Индексы OK |
| `spr_black_rabbit_matrix` | 1,800 | 0 | |
| `spr_master_dano_mapping` | 720 | 0 | |
| `spr_hour_stars` | 288 | 0 | |
| `spr_column_comment` | 196 | 0 | |
| `spr_day_officer_mapping` | 144 | 0 | |
| `spr_month_stars` | 144 | 0 | |
| `spr_yellow_black_matrix` | 144 | 0 | |
| `spr_bazi_qi_phase` | 120 | 1 | ✅ |
| `spr_pillar_hour_rule` | 120 | 0 | |
| `spr_pillar_month_rule` | 120 | 0 | |
| `spr_ri_jia` | 120 | 0 | |
| `spr_jiazi_extended` | 60 | 1 | ✅ |
| `spr_pillar_cycle` | 60 | 0 | |
| `spr_solar_term` | 24 | 0 | |
| `spr_tongshu_guigu_outcome` | 14 | 0 | |
| `spr_earthly_branch` | 12 | 0 | |
| `spr_yellow_black_stars` | 12 | 0 | |
| `spr_heavenly_stem` | 10 | 0 | |
| `spr_gates` | 9 | 0 | |
| `spr_stars` | 9 | 0 | |
| `spr_black_rabbit_scores` | 9 | 0 | |
| `spr_tongshu_stem_combo_rule` | 9 | 0 | |
| `spr_gods` | 8 | 0 | |
| `spr_analysis_scope` | 4 | 0 | |
| `spr_indicator_value` | 17 | 0 | ⚠️ Пустые типы колонок |
| `spr_indicator` | 2 | 0 | |
| `spr_indicator_scope` | 2 | 0 | |
| `spr_tongshu_branch_combo_rule` | 39 | 0 | |
| `spr_leader_stems` | 6 | 0 | |
| `spr_table_comment` | 41 | 0 | |
| `spr_tongshu_guigu_symbol` | **0** | 0 | 🟡 Пустая |
| `spr_tongshu_jiazi_profile` | **0** | 0 | 🟡 Пустая |
| `spr_tongshu_phase` | **0** | 0 | 🟡 Пустая |
| `spr_tongshu_phase_mapping` | **0** | 0 | 🟡 Пустая |
| `spr_tongshu_shensha_rule` | **0** | 0 | 🟡 Пустая |
| `spr_tongshu_ten_god` | **0** | 0 | 🟡 Пустая |

### 2.3. Контрольные таблицы (10)

Все контрольные таблицы имеют по 100 записей (кроме year-таблиц: 18).

- `t_control_t_bazi_hourly`
- `t_control_t_flying_stars`
- `t_control_t_qumen_chauby_day`
- `t_control_t_qumen_chauby_hourly`
- `t_control_t_qumen_chauby_month`
- `t_control_t_qumen_chauby_year`
- `t_control_t_qumen_dgiren_day`
- `t_control_t_qumen_dgiren_hourly`
- `t_control_t_qumen_dgiren_month`
- `t_control_t_qumen_dgiren_year`

---

## 3. Проблемы с индексами

### 🔴 Критично отсутствующие (большие таблицы без индексов)

| Таблица | Строк | Рекомендуемые индексы |
|---------|-------|----------------------|
| `t_analysis_date` | 14.5M | `(hour_id)`, `(rule_id)`, `(hour_id, rule_id)` |
| `t_analysis_direction` | 1.8M | `(hour_id)`, `(palace_no)`, `(hour_id, palace_no)` |
| `t_analyz_direction` | 34K | `(chart_id)`, `(rule_id)` |
| `t_qumen_chauby_day` | 6,642 | `(rasklad_id)`, `(year_pillar, month_pillar, day_pillar)` |
| `t_qumen_chauby_month` | 207 | `(rasklad_id)`, `(year_pillar, month_pillar)` |
| `t_qumen_chauby_year` | 18 | `(rasklad_id)`, `(year_pillar)` |
| `t_qumen_dgiren_day` | 6,642 | `(rasklad_id)`, `(year_pillar, month_pillar, day_pillar)` |
| `t_qumen_dgiren_month` | 207 | `(rasklad_id)`, `(year_pillar, month_pillar)` |
| `t_qumen_dgiren_year` | 18 | `(rasklad_id)`, `(year_pillar)` |
| `t_flying_stars` | 2M | `(palace)`, `(year_star, month_star)` |
| `t_rule_scope` | 155 | `(scope_type)` |

### 🟡 Частично индексированные

| Таблица | Есть | Не хватает |
|---------|------|-----------|
| `t_qumen_chauby_hourly` | `hour_id` | `rasklad_id`, `chart_id`, `(rasklad_id, palace_no)` |
| `t_qumen_dgiren_hourly` | `hour_id` | `rasklad_id`, `chart_id`, `(rasklad_id, palace_no)` |
| `spr_qimen_templates` | 2 индекса | `(template_id)`, `(palace_no)` |

---

## 4. Дублирование и избыточность

### 4.1. Похожие группы таблиц (потенциальные дубли)

**Группа 1: `t_analysis_*` vs `t_analyz_*`**

| analysis (старая?) | analyz (новая?) | Статус |
|-------------------|-----------------|--------|
| `t_analysis_activation` | `t_analyz_activation` | Обе пустые |
| `t_analysis_date` | `t_analyz_date` | analysis: 14.5M, analyz: 0 |
| `t_analysis_direction` | `t_analyz_direction` | analysis: 1.8M, analyz: 34K |
| — | `t_analyz_data` | Только в analyz, пустая |

**Вывод:** Вероятно, `t_analysis_*` — старая версия, `t_analyz_*` — новая, но миграция не завершена. `t_analysis_date` и `t_analysis_direction` содержат данные, а `t_analyz_date` пустая.

**Группа 2: Параллельные системы Ци Мэнь**

| Chauby | Dgiren | Структура |
|--------|--------|-----------|
| `t_qumen_chauby_year` | `t_qumen_dgiren_year` | Идентична |
| `t_qumen_chauby_month` | `t_qumen_dgiren_month` | Идентична |
| `t_qumen_chauby_day` | `t_qumen_dgiren_day` | Идентична |
| `t_qumen_chauby_hourly` | `t_qumen_dgiren_hourly` | Идентична |

Это архитектурно корректно (две школы), но требует унификации индексов.

**Группа 3: Контрольные таблицы дублируют структуру**

Контрольные таблицы имеют те же колонки, но:
- Тип `INT` вместо `INTEGER`
- Нет PK
- Нет NOT NULL ограничений
- Нет FK

### 4.2. Избыточные VIEW (Timezone-каскад)

Создано **25 VIEW** для каждого timezone offset (`v_bazi_hourly_tz_m12` .. `v_bazi_hourly_tz_p14`). Все они идентичны за исключением фильтра `tz_offset_hours = N`.

**Рекомендация:** В PostgreSQL заменить на одну параметризованную функцию или материализованное представление.

---

## 5. Контрольные таблицы: покрытие

**Есть контрольные таблицы (10):**
- `t_bazi_hourly`, `t_flying_stars`
- `t_qumen_chauby_*` (4 шт.)
- `t_qumen_dgiren_*` (4 шт.)

**Отсутствуют контрольные таблицы (14 основных таблиц без контроля):**

| Таблица | Ожидаемая контрольная |
|---------|----------------------|
| `t_analysis_activation` | `t_control_analysis_activation` |
| `t_analysis_date` | `t_control_analysis_date` |
| `t_analysis_direction` | `t_control_analysis_direction` |
| `t_analyz_activation` | `t_control_analyz_activation` |
| `t_analyz_data` | `t_control_analyz_data` |
| `t_analyz_date` | `t_control_analyz_date` |
| `t_analyz_direction` | `t_control_analyz_direction` |
| `t_chart_analysis` | `t_control_chart_analysis` |
| `t_rule_registry` | `t_control_rule_registry` |
| `t_rule_scope` | `t_control_rule_scope` |
| `t_solar_term_time` | `t_control_solar_term_time` |
| `t_solar_term_time_hko` | `t_control_solar_term_time_hko` |
| `t_sys_calculation_log` | `t_control_sys_calculation_log` |
| `t_time_grid_hourly` | `t_control_time_grid_hourly` |

---

## 6. Устаревшие / битые ссылки

### 6.1. Опечатка в VIEW

**`v_good_sequence_gate`** содержит битую ссылку:
```sql
--and v_qimen_chauby_month= '丙午'  -- опечатка: пропущен пробел/алиас, либо это закомментированный код
```
В SQL определении также виден артефакт: `v_qimen_chauby_month=` (строка 4322 в JSON).

### 6.2. Отсутствующая таблица в FK

**`t_chart_analysis`** имеет Foreign Key на `spr_indicator_rule`:
```sql
FOREIGN KEY (rule_id) REFERENCES spr_indicator_rule(rule_id)
```

**Таблица `spr_indicator_rule` ОТСУТСТВУЕТ** в БД. Это критическая ошибка целостности.

### 6.3. Ссылки VIEW на удаленные таблицы

Согласно журналу, были удалены `t_qumen_chauby_year/month/day`, но они **присутствуют** в текущей БД. Возможно, журнал устарел или таблицы были восстановлены.

---

## 7. Проверка ключевых справочников

### 7.1. Структура (все на месте)

| Справочник | Строк | PK | Статус |
|-----------|-------|-----|--------|
| `spr_heavenly_stem` | 10 | `stem_id` | ✅ |
| `spr_earthly_branch` | 12 | `branch_id` | ✅ |
| `spr_gods` | 8 | `id` | ✅ |
| `spr_stars` | 9 | `id` | ✅ |
| `spr_gates` | 9 | `id` | ✅ |
| `spr_solar_term` | 24 | `solar_term_id` | ✅ |
| `spr_jiazi_extended` | 60 | `jiazi_id` | ✅ |

### 7.2. Проблемы в справочниках

- **`spr_indicator_value`**: Колонки `interpretation_ru` и `numeric_score` имеют **пустой тип данных** (`"type": ""`). Это нарушает целостность схемы.
- **`spr_tongshu_guigu_symbol`**, **`spr_tongshu_jiazi_profile`**, **`spr_tongshu_phase`**, **`spr_tongshu_phase_mapping`**, **`spr_tongshu_shensha_rule`**, **`spr_tongshu_ten_god`** — все пустые (0 строк). Возможно, не заполнены или не используются.

---

## 8. VIEW и их зависимости

### 8.1. Иерархия VIEW

```
v_bazi_hourly (базовый, ссылается на t_bazi_hourly + spr_solar_term + spr_earthly_branch)
  ├── v_bazi_hourly_msk (ссылается на v_bazi_hourly_tz_p03)
  └── v_bazi_hourly_tz_* (25 шт., m12..p14, фильтруют tz_offset_hours)

v_qumen_chauby_year  → t_qumen_chauby_year + spr_qimen_templates
v_qumen_chauby_month → t_qumen_chauby_month + spr_qimen_templates
v_qumen_chauby_day   → t_qumen_chauby_day + spr_qimen_templates
v_qumen_chauby_hourly → t_qumen_chauby_hourly + spr_qimen_templates + v_bazi_hourly
  └── v_good_sequence_gate (ссылается на все 4 v_qumen_* + v_bazi_hourly)
```

### 8.2. Проблемы VIEW

- **v_bazi_hourly** содержит фильтр `slot_start_date_utc >= date('now')` — это делает view динамическим, непригодным для анализа исторических данных.
- **v_good_sequence_gate** содержит хардкод `tz_offset_hours = 3` и сложные бизнес-правила в SQL.
- 25 timezone-VIEW можно схлопнуть в одну параметризованную сущность.

---

## 9. Нарушения архитектурных правил

| Правило | Статус | Комментарий |
|---------|--------|-------------|
| SQL-First | ⚠️ Частично | SQLite — staging, но нет явной миграции DDL |
| Комментарии DDL | ✅ | `spr_table_comment` (41), `spr_column_comment` (196) |
| Контрольные таблицы | ⚠️ Частично | Только 10 из 24 основных таблиц |
| Справочники (spr_*) | ✅ | 37 справочников, структура корректна |
| Результаты (t_*) | ⚠️ | Дублирование analysis/analyz, пустые таблицы |
| Индексы | 🔴 **Нет** | 20 индексов на 71 таблицу — критически мало |

---

## 10. Конкретные SQL-рекомендации

### 10.1. Немедленно создать индексы (SQLite)

```sql
-- t_analysis_date (14.5M строк)
CREATE INDEX idx_analysis_date_hour_id ON t_analysis_date(hour_id);
CREATE INDEX idx_analysis_date_rule_id ON t_analysis_date(rule_id);
CREATE INDEX idx_analysis_date_hour_rule ON t_analysis_date(hour_id, rule_id);

-- t_analysis_direction (1.8M строк)
CREATE INDEX idx_analysis_direction_hour_id ON t_analysis_direction(hour_id);
CREATE INDEX idx_analysis_direction_palace ON t_analysis_direction(palace_no);
CREATE INDEX idx_analysis_direction_hour_palace ON t_analysis_direction(hour_id, palace_no);

-- t_analyz_direction
CREATE INDEX idx_analyz_direction_chart_id ON t_analyz_direction(chart_id);
CREATE INDEX idx_analyz_direction_rule_id ON t_analyz_direction(rule_id);

-- t_qumen_chauby_day / t_qumen_dgiren_day
CREATE INDEX idx_qumen_chauby_day_rasklad ON t_qumen_chauby_day(rasklad_id);
CREATE INDEX idx_qumen_dgiren_day_rasklad ON t_qumen_dgiren_day(rasklad_id);

-- t_qumen_chauby_hourly / t_qumen_dgiren_hourly (дополнительные)
CREATE INDEX idx_qumen_chauby_hourly_rasklad ON t_qumen_chauby_hourly(rasklad_id);
CREATE INDEX idx_qumen_dgiren_hourly_rasklad ON t_qumen_dgiren_hourly(rasklad_id);

-- t_flying_stars
CREATE INDEX idx_flying_stars_palace ON t_flying_stars(palace);
CREATE INDEX idx_flying_stars_hour_palace ON t_flying_stars(hour_id, palace);

-- t_rule_scope
CREATE INDEX idx_rule_scope_type ON t_rule_scope(scope_type);
```

### 10.2. Исправить пустые типы колонок

```sql
-- spr_indicator_value: колонки без типа
ALTER TABLE spr_indicator_value ADD COLUMN interpretation_ru_new TEXT;
UPDATE spr_indicator_value SET interpretation_ru_new = interpretation_ru;
-- ... пересоздать таблицу с правильными типами (SQLite не поддерживает ALTER COLUMN TYPE)
```

### 10.3. PostgreSQL: заменить timezone-VIEW на функцию

```sql
-- Вместо 25 VIEW создать одну функцию
CREATE OR REPLACE FUNCTION v_bazi_hourly_tz(p_tz_offset INTEGER)
RETURNS TABLE (...) AS $$
  SELECT * FROM v_bazi_hourly WHERE tz_offset_hours = p_tz_offset;
$$ LANGUAGE SQL STABLE;
```

### 10.4. Создать недостающие контрольные таблицы

```sql
CREATE TABLE t_control_analysis_date (
    hour_id TEXT,
    rule_id TEXT,
    result_value TEXT,
    score REAL
);
-- + аналогично для всех 14 отсутствующих контрольных таблиц
```

### 10.5. Исправить или удалить битый FK

```sql
-- t_chart_analysis ссылается на несуществующую spr_indicator_rule
-- Вариант 1: Создать spr_indicator_rule
-- Вариант 2: Изменить FK на t_rule_registry(rule_id)
-- Вариант 3: Удалить FK
```

### 10.6. Решить дублирование analysis/analyz

```sql
-- Вариант 1: Переименовать t_analysis_* → t_analyz_* и объединить данные
-- Вариант 2: Удалить пустые t_analyz_* если они не нужны
-- Вариант 3: Создать VIEW-прослойку для унификации интерфейса
```

---

## 11. Приоритеты действий

| Приоритет | Действие | Влияние |
|-----------|----------|---------|
| 🔴 **P0** | Создать индексы на `t_analysis_date`, `t_analysis_direction` | Производительность запросов к 16M+ строкам |
| 🔴 **P0** | Разобраться с `spr_indicator_rule` (отсутствует, но есть FK) | Целостность данных |
| 🟡 **P1** | Унифицировать `t_analysis_*` / `t_analyz_*` | Упрощение схемы |
| 🟡 **P1** | Создать недостающие контрольные таблицы | Архитектурное соответствие |
| 🟡 **P1** | Исправить типы колонок в `spr_indicator_value` | Целостность схемы |
| 🟢 **P2** | Схлопнуть 25 timezone-VIEW в PostgreSQL | Упрощение поддержки |
| 🟢 **P2** | Очистить пустые справочники `spr_tongshu_*` | Уменьшение clutter |
| 🟢 **P2** | Добавить PK и NOT NULL в контрольные таблицы | Целостность |

---

## 12. Итоговая оценка

| Критерий | Оценка | Комментарий |
|----------|--------|-------------|
| Структура схемы | ✅ Хорошо | Четкое разделение spr_/t_/t_control_ |
| Полнота данных | ⚠️ Средне | Есть пустые таблицы, незавершенная миграция |
| Индексация | 🔴 Плохо | 20 индексов на 71 таблицу, 16M+ строк без индексов |
| Целостность (FK) | 🔴 Плохо | Битая ссылка на `spr_indicator_rule` |
| Контрольные таблицы | ⚠️ Частично | Покрытие ~42% (10/24) |
| VIEW | ⚠️ Избыточно | 25 идентичных timezone-view |
| Комментарии | ✅ Хорошо | spr_table_comment, spr_column_comment |

**Общий вывод:** БД функциональна, но требует **срочной индексации** и **исправления FK** перед переводом на PostgreSQL. Дублирование `analysis/analyz` и пустые справочники указывают на незавершенный рефакторинг.
