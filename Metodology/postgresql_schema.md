# Схема PostgreSQL БД `calk_kmf`

> **Автоматически сгенерировано:** 2026-05-31  
> **Всего таблиц:** 98  
> **Справочники (spr_\*):** ~60  
> **Таблицы данных (t_\*):** ~38  

## Правило поддержки

При выполнении `ALTER TABLE` необходимо обновить **оба** файла:
1. `data/ddl_full_schema_raw.sql` — перегенерировать через `pg_dump --schema-only`
2. `Metodology/postgresql_schema.md` — обновить описание изменённых таблиц

## Содержание

- [Справочные таблицы (spr_*)](#справочные-таблицы-spr)
  - [Базовые справочники БаЦзы](#базовые-справочники-бацзы)
  - [Ци Мэнь Дунь Цзя](#ци-мэнь-дунь-цзя)
  - [Тун Шу / Фэн Шуй](#тун-шу--фэн-шуй)
  - [Тай И Шэнь Шу](#тай-и-шэнь-шу)
  - [Система анализа (Rule Engine)](#система-анализа-rule-engine)
  - [СКДГ (Секретный Код Дракона)](#скдг-секретный-код-дракона)
  - [Сервисные](#сервисные)
- [Таблицы данных (t_*)](#таблицы-данных-t)
  - [Базовые расчёты и сетка времени](#базовые-расчёты-и-сетка-времени)
  - [Результаты анализа (Rule Engine)](#результаты-анализа-rule-engine)
  - [Ци Мэнь Дунь Цзя](#ци-мэнь-дунь-цзя)
  - [Тай И Шэнь Шу](#тай-и-шэнь-шу)
  - [Тун Шу](#тун-шу)
  - [CRM](#crm)
  - [Профили и карты рождения](#профили-и-карты-рождения)
  - [Система и журналы](#система-и-журналы)
  - [Контрольные данные](#контрольные-данные)
- [Индексы](#индексы)
- [Внешние ключи](#внешние-ключи)
- [Триггеры и функции](#триггеры-и-функции)

---
## Справочные таблицы (spr_*)

### Базовые справочники БаЦзы

#### `spr_heavenly_stem`
*Справочник 10 Небесных Стволов (天干)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `stem_id` | bigint | NO |  | ID ствола (1-10) |
| `stem_char` | text | NO |  | Иероглиф ствола |
| `stem_pinyin` | text | YES |  | Пиньинь |
| `stem_rus` | text | YES |  |  |
| `element` | text | YES |  | Элемент (Дерево/Огонь/Земля/Металл/Вода) |
| `yin_yang` | text | YES |  |  |
| `guigu_score` | bigint | YES |  |  |
| `color_hex` | character varying(7) | YES |  |  |

**Индексы:**
- `spr_heavenly_stem_pkey` — UNIQUE PK (stem_id)

#### `spr_earthly_branch`
*Справочник 12 Земных Ветвей (地支)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `branch_id` | bigint | NO |  | ID ветви (1-12) |
| `branch_char` | text | NO |  | Иероглиф ветви |
| `branch_pinyin` | text | YES |  | Пиньинь |
| `branch_rus` | text | YES |  |  |
| `element` | text | YES |  | Элемент |
| `yin_yang` | text | YES |  |  |
| `yuan_level` | bigint | YES |  |  |
| `start_hour` | bigint | YES |  |  |
| `end_hour` | bigint | YES |  |  |
| `guigu_score` | bigint | YES |  |  |
| `color_hex` | character varying(7) | YES |  |  |

**Индексы:**
- `spr_earthly_branch_pkey` — UNIQUE PK (branch_id)

#### `spr_solar_term`
*Справочник 24 солнечных терминов (節氣)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `solar_term_id` | bigint | NO |  |  |
| `solar_term_char` | text | NO |  |  |
| `solar_term_name_ru` | text | YES |  |  |
| `solar_term_pinyin` | text | YES |  |  |
| `longitude_deg` | bigint | NO |  |  |
| `month_branch_id` | bigint | NO |  |  |
| `upper_ju` | bigint | YES |  |  |
| `middle_ju` | bigint | YES |  |  |
| `lower_ju` | bigint | YES |  |  |

**Индексы:**
- `spr_solar_term_pkey` — UNIQUE PK (solar_term_id)

#### `spr_jiazi_extended`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `jiazi_id` | integer | NO |  |  |
| `stem` | text | YES |  |  |
| `branch` | text | YES |  |  |
| `nayin_element` | text | YES |  |  |
| `nayin_name` | text | YES |  |  |
| `dagua_element` | integer | YES |  |  |
| `dagua_period` | integer | YES |  |  |
| `dagua_role` | text | YES |  |  |
| `upper_ju_yang` | integer | YES |  |  |
| `middle_ju_yang` | integer | YES |  |  |
| `lower_ju_yang` | integer | YES |  |  |
| `upper_ju_yin` | integer | YES |  |  |
| `middle_ju_yin` | integer | YES |  |  |
| `lower_ju_yin` | integer | YES |  |  |

**Индексы:**
- `idx_jiazi_stem_branch` — (stem, branch)
- `spr_jiazi_extended_pkey` — UNIQUE PK (jiazi_id)

#### `spr_pillar_cycle`
*Справочник столпов (год/месяц/день) для цикла Цзя-Цзы*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `cycle_index` | bigint | NO |  |  |
| `stem_id` | bigint | NO |  |  |
| `branch_id` | bigint | NO |  |  |

**Индексы:**
- `spr_pillar_cycle_pkey` — UNIQUE PK (cycle_index)

#### `spr_pillar_hour_rule`
*Правила вычисления часового столпа из дневного ствола*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `day_stem_id` | bigint | NO |  |  |
| `hour_branch_id` | bigint | NO |  |  |
| `hour_stem_id` | bigint | NO |  |  |

**Индексы:**
- `spr_pillar_hour_rule_pkey` — UNIQUE PK (day_stem_id, hour_branch_id)

#### `spr_pillar_month_rule`
*Правила вычисления месячного столпа из годового ствола*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `year_stem_id` | bigint | NO |  |  |
| `month_index` | bigint | NO |  |  |
| `month_stem_id` | bigint | NO |  |  |

**Индексы:**
- `spr_pillar_month_rule_pkey` — UNIQUE PK (year_stem_id, month_index)

#### `spr_leader_stems`
*Ведущие стволы для определения часового/месячного столпа*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `idx` | bigint | NO |  |  |
| `stem` | text | YES |  |  |

**Индексы:**
- `spr_leader_stems_pkey` — UNIQUE PK (idx)

#### `spr_bazi_qi_phase`
*Фазы Ци столпов (месяц/день/час)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `id` | bigint | NO |  |  |
| `stem_char` | text | NO |  |  |
| `branch_char` | text | NO |  |  |
| `phase_id` | bigint | NO |  |  |
| `phase_name` | text | NO |  |  |
| `numeric_score` | double precision | YES |  |  |

**Индексы:**
- `idx_qi_phase_stem_branch` — (stem_char, branch_char)
- `spr_bazi_qi_phase_pkey` — UNIQUE PK (id)

### Ци Мэнь Дунь Цзя

#### `spr_qimen_templates`
*Шаблоны раскладов Ци Мэнь (базовые конфигурации)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `template_id` | text | NO |  |  |
| `rasklad_id` | text | YES |  |  |
| `yin_yang` | text | YES |  |  |
| `ju_num` | bigint | YES |  |  |
| `hour_stem_branch` | text | YES |  |  |
| `palace_no` | bigint | YES |  |  |
| `structure` | text | YES |  |  |
| `heaven_stem` | text | YES |  |  |
| `is_fou_tou_heaven` | bigint | YES |  |  |
| `earth_stem` | text | YES |  |  |
| `is_fou_tou_earth` | bigint | YES |  |  |
| `star` | text | YES |  |  |
| `is_main_star` | bigint | YES |  |  |
| `gate` | text | YES |  |  |
| `is_main_gate` | bigint | YES |  |  |
| `spirit` | text | YES |  |  |

**Индексы:**
- `idx_qimen_templates_rasklad` — (rasklad_id, palace_no)
- `idx_qimen_templates_stems` — (heaven_stem, earth_stem)
- `spr_qimen_templates_pkey` — UNIQUE PK (template_id)

#### `spr_gates`
*Справочник 8 Врат Ци Мэнь Дуня (八門)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `id` | bigint | NO |  |  |
| `name_en` | text | YES |  |  |
| `name_ru` | text | YES |  |  |

**Индексы:**
- `spr_gates_pkey` — UNIQUE PK (id)

#### `spr_gods`
*Справочник 8 Божеств Ци Мэнь Дуня (八神)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `id` | bigint | NO |  |  |
| `name_en` | text | YES |  |  |
| `name_ru` | text | YES |  |  |

**Индексы:**
- `spr_gods_pkey` — UNIQUE PK (id)

#### `spr_stars`
*Справочник 9 Звёзд Ци Мэнь Дуня (九星)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `id` | bigint | NO |  |  |
| `name_en` | text | YES |  |  |
| `name_ru` | text | YES |  |  |

**Индексы:**
- `spr_stars_pkey` — UNIQUE PK (id)

### Тун Шу / Фэн Шуй

#### `spr_flying_star_map`
*Карта Летящих Звёзд: период + направление → звёзды*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `center_star` | integer | NO |  |  |
| `palace` | integer | NO |  |  |
| `resident_star` | integer | YES |  |  |

**Индексы:**
- `spr_flying_star_map_pkey` — UNIQUE PK (center_star, palace)

#### `spr_tongshu_black_rabbit_rating`
*Оценки звёзд Чёрного Кролика по Тун Шу*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `star_name` | text | NO |  |  |
| `rating_code` | text | NO |  |  |
| `rating_name` | text | NO |  |  |
| `description_ru` | text | YES |  |  |

**Индексы:**
- `spr_tongshu_black_rabbit_rating_pkey` — UNIQUE PK (star_name)

#### `spr_tongshu_black_rabbit_star`
*Звёзды Чёрного Кролика по Тун Шу*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `cycle_index` | integer | NO |  |  |
| `lunar_day` | integer | NO |  |  |
| `method_code` | text | NO | 'primary'::text |  |
| `star_name` | text | NO |  |  |
| `description_ru` | text | YES |  |  |
| `nature` | character varying(20) | YES |  |  |
| `color_hex` | character varying(7) | YES |  |  |

**Индексы:**
- `spr_tongshu_black_rabbit_star_pkey` — UNIQUE PK (cycle_index, lunar_day, method_code)

**Внешние ключи:**
- `cycle_index` → `spr_tongshu_jiazi_profile.cycle_index`

#### `spr_tongshu_branch_combo_rule`
*Правила комбинаций Земных Ветвей (三合/六合/刑/冲/害/破)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `rule_id` | bigint | NO |  |  |
| `combo_name` | text | NO |  |  |
| `combo_type_id` | bigint | NO |  |  |
| `numeric_score` | double precision | NO |  |  |
| `item1` | text | NO |  |  |
| `item2` | text | NO |  |  |
| `item3` | text | YES |  |  |
| `description` | text | YES |  |  |

**Индексы:**
- `spr_tongshu_branch_combo_rule_pkey` — UNIQUE PK (rule_id)

#### `spr_tongshu_guigu_outcome`
*Результаты Гуй Гу Шу (鬼谷數)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `outcome_number` | bigint | NO |  |  |
| `name_ru` | text | NO |  |  |
| `verdict_code` | text | NO |  |  |
| `description_ru` | text | YES |  |  |
| `numeric_score` | double precision | YES |  |  |

**Индексы:**
- `spr_tongshu_guigu_outcome_pkey` — UNIQUE PK (outcome_number)

#### `spr_tongshu_jiazi_profile`
*Профили 60 Цзя-Цзы по Тун Шу*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `cycle_index` | bigint | NO |  |  |
| `pillar_text` | text | NO |  |  |
| `nayin_name` | text | YES |  |  |
| `nayin_element` | text | YES |  |  |
| `nayin_code` | text | YES |  |  |
| `dagua_element` | bigint | YES |  |  |
| `dagua_period` | bigint | YES |  |  |
| `family_code` | text | YES |  |  |
| `family_role` | text | YES |  |  |

**Индексы:**
- `spr_tongshu_jiazi_profile_pkey` — UNIQUE PK (cycle_index)

#### `spr_tongshu_phase`
*Фазы Ци (氣) по Тун Шу*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `phase_id` | bigint | NO |  |  |
| `name_ru` | text | NO |  |  |
| `numeric_score` | double precision | NO |  |  |

**Индексы:**
- `spr_tongshu_phase_pkey` — UNIQUE PK (phase_id)

#### `spr_tongshu_phase_mapping`
*Маппинг фаз Ци по столпам*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `day_stem` | text | NO |  |  |
| `phase_id` | bigint | NO |  |  |
| `reference_branch` | text | NO |  |  |

**Индексы:**
- `spr_tongshu_phase_mapping_pkey` — UNIQUE PK (day_stem, phase_id)

#### `spr_tongshu_shensha_rule`
*Правила Шэнь Ша (神煞) — духи и демоны*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `rule_id` | bigint | NO |  | ID правила |
| `star_name` | text | NO |  | Название звезды (на русском) |
| `master_scope` | text | NO |  | Область поиска мастера: `day_stem`, `day_branch`, `year_branch`, `month_branch` |
| `master_value` | text | NO |  | Значение мастера (ствол/ветвь) |
| `target_scope` | text | NO |  | Область поиска цели: `day_branch`, `year_branch`, `month_branch`, `hour_branch`, `day_stem`, `year_stem`, `month_stem`, `hour_stem` |
| `target_value` | text | NO |  | Значение цели |
| `notes` | text | YES |  | Примечания |
| `source` | character varying(50) | YES | `classical` | Источник метода: `classical` — классическая школа, `vladimir_zakharov` — методология В.Захарова |

**Индексы:**
- `spr_tongshu_shensha_rule_pkey` — UNIQUE PK (rule_id)

#### `spr_shensha_config`
*Конфигурация символических звёзд Шэнь Ша (神煞) — управление отображением, категориями и интерпретациями*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `config_id` | integer | NO |  | PK, автоинкремент |
| `star_key` | character varying(50) | NO |  | Уникальный ключ звезды (латиница: `lu`, `wangshen`, `taohua` и т.д.) |
| `display_name_ru` | character varying(100) | NO |  | Отображаемое имя на русском |
| `display_name_zh` | character varying(50) | YES |  | Иероглифическое название |
| `category` | character varying(50) | NO |  | Категория: `auspicious`, `inauspicious`, `relationships`, `finance`, `reputation`, `health`, `neutral` |
| `nature` | character varying(20) | YES | `neutral` | Характер: `auspicious` (благоприятная), `inauspicious` (неблагоприятная), `neutral` (нейтральная) |
| `color_hex` | character varying(7) | YES | `#808080` | Цвет отображения |
| `is_active` | integer | YES | `1` | Флаг активности (1 — отображается, 0 — скрыта) |
| `tooltip_text` | text | YES |  | Текст всплывающей подсказки |
| `interpretation_text` | text | YES |  | Полная интерпретация |
| `short_interpretation` | character varying(255) | YES |  | Краткая интерпретация |
| `source` | character varying(50) | YES | `classical` | Источник: `classical` или `vladimir_zakharov` |
| `display_order` | integer | YES | `0` | Порядок отображения |
| `created_at` | timestamp without time zone | YES | `CURRENT_TIMESTAMP` |  |
| `updated_at` | timestamp without time zone | YES | `CURRENT_TIMESTAMP` |  |

**Индексы:**
- `spr_shensha_config_pkey` — UNIQUE PK (config_id)

#### `spr_tongshu_stem_combo_rule`
*Правила комбинаций Небесных Стволов (合/冲)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `rule_id` | bigint | NO |  |  |
| `combo_name` | text | NO |  |  |
| `combo_type_id` | bigint | NO |  |  |
| `numeric_score` | double precision | NO |  |  |
| `item1` | text | NO |  |  |
| `item2` | text | NO |  |  |
| `description` | text | YES |  |  |

**Индексы:**
- `spr_tongshu_stem_combo_rule_pkey` — UNIQUE PK (rule_id)

#### `spr_tongshu_ten_god`
*Справочник 10 Богов (十神)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `day_stem` | text | NO |  |  |
| `god_code` | text | NO |  |  |
| `related_stem` | text | NO |  |  |

**Индексы:**
- `spr_tongshu_ten_god_pkey` — UNIQUE PK (day_stem, god_code)

#### `spr_day_officer_mapping`
*Маппинг Дневных Офицеров (建除十二直) по ветви месяца + ветви дня*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `month_branch_id` | bigint | NO |  |  |
| `day_branch_id` | bigint | NO |  |  |
| `officer_value_id` | bigint | NO |  |  |

**Индексы:**
- `spr_day_officer_mapping_pkey` — UNIQUE PK (month_branch_id, day_branch_id)

#### `spr_master_dano_mapping`
*Маппинг Мастера Дун Гуна по ветви месяца + стволу/ветви дня*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `month_branch_id` | bigint | NO |  |  |
| `day_stem_id` | bigint | NO |  |  |
| `day_branch_id` | bigint | NO |  |  |
| `indicator_value_id` | bigint | NO |  |  |

**Индексы:**
- `spr_master_dano_mapping_pkey` — UNIQUE PK (month_branch_id, day_stem_id, day_branch_id)

#### `spr_hour_stars`
*Часовые звёзды для Фэн Шуй*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `day_branch` | text | NO |  |  |
| `yin_yang` | bigint | NO |  |  |
| `hour_branch` | text | NO |  |  |
| `star` | bigint | YES |  |  |

**Индексы:**
- `spr_hour_stars_pkey` — UNIQUE PK (day_branch, yin_yang, hour_branch)

#### `spr_month_stars`
*Месячные звёзды для Фэн Шуй*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `year_branch` | text | NO |  |  |
| `month_branch` | text | NO |  |  |
| `star` | bigint | YES |  |  |

**Индексы:**
- `spr_month_stars_pkey` — UNIQUE PK (year_branch, month_branch)

#### `spr_yanqin_day_constellation`
*Справочник 28 созвездий 演禽 по дню недели + группе ветвей*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `dow` | integer | NO |  |  |
| `branch_group` | integer | NO |  |  |
| `constellation_char` | text | NO |  |  |
| `constellation_name` | text | NO |  |  |
| `star_element` | text | NO |  |  |
| `score` | double precision | NO |  |  |

**Индексы:**
- `spr_yanqin_day_constellation_pkey` — UNIQUE PK (dow, branch_group)

#### `spr_yellow_black_matrix`
*Матрица Жёлтого/Чёрного пути: ветвь месяца + ветвь дня → ID звезды*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `month_branch` | text | NO |  |  |
| `day_branch` | text | NO |  |  |
| `star_id` | bigint | YES |  |  |

**Индексы:**
- `spr_yellow_black_matrix_pkey` — UNIQUE PK (month_branch, day_branch)

#### `spr_yellow_black_stars`
*Звёзды Жёлтого/Чёрного пути с оценкой (+1/-1)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `id` | bigint | NO |  |  |
| `name` | text | YES |  |  |
| `score` | double precision | YES |  |  |

**Индексы:**
- `spr_yellow_black_stars_pkey` — UNIQUE PK (id)

#### `spr_black_rabbit_day_joey`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `first_day_jiazi_id` | integer | NO |  |  |
| `lunar_day` | integer | NO |  |  |
| `star_name` | text | NO |  |  |
| `score` | double precision | NO |  |  |

**Индексы:**
- `spr_black_rabbit_day_joey_pkey` — UNIQUE PK (first_day_jiazi_id, lunar_day)

#### `spr_black_rabbit_hour_joey`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `day_stem` | text | NO |  |  |
| `hour_branch` | text | NO |  |  |
| `star_name` | text | NO |  |  |
| `score` | double precision | NO |  |  |

**Индексы:**
- `spr_black_rabbit_hour_joey_pkey` — UNIQUE PK (day_stem, hour_branch)

#### `spr_black_rabbit_matrix`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `jiazi_id` | integer | NO |  |  |
| `lunar_day` | integer | NO |  |  |
| `star_name` | text | YES |  |  |

**Индексы:**
- `spr_black_rabbit_matrix_pkey` — UNIQUE PK (jiazi_id, lunar_day)

#### `spr_black_rabbit_scores`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `star_name` | text | NO |  |  |
| `numeric_score` | double precision | YES |  |  |

**Индексы:**
- `spr_black_rabbit_scores_pkey` — UNIQUE PK (star_name)

### Тай И Шэнь Шу

#### `spr_taiyi_gate_seq`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `cycle_type` | text | NO |  |  |
| `seq_idx` | integer | NO |  |  |
| `palace_id` | integer | YES |  |  |

**Индексы:**
- `spr_taiyi_gate_seq_pkey` — UNIQUE PK (cycle_type, seq_idx)

#### `spr_taiyi_gates`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `id` | integer | NO |  |  |
| `code` | text | YES |  |  |
| `name_cn` | text | YES |  |  |
| `name_ru` | text | YES |  |  |
| `lucky_score` | integer | YES |  |  |

**Индексы:**
- `spr_taiyi_gates_pkey` — UNIQUE PK (id)

#### `spr_taiyi_jianchu`
*Справочник 12 созвездий 建除十二神 с score*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `id` | integer | NO |  |  |
| `char_cn` | text | NO |  |  |
| `name_ru` | text | NO |  |  |
| `description` | text | YES |  |  |
| `score` | integer | NO |  |  |

**Индексы:**
- `spr_taiyi_jianchu_pkey` — UNIQUE PK (id)

#### `spr_taiyi_kong_wang`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `day_stem_id` | integer | NO |  |  |
| `hour_branch_id` | integer | NO |  |  |

**Индексы:**
- `spr_taiyi_kong_wang_pkey` — UNIQUE PK (day_stem_id, hour_branch_id)

#### `spr_taiyi_noble`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `day_stem_id` | integer | NO |  |  |
| `hour_branch_id` | integer | NO |  |  |

**Индексы:**
- `spr_taiyi_noble_pkey` — UNIQUE PK (day_stem_id, hour_branch_id)

#### `spr_taiyi_palace_ring`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `palace_id` | integer | NO |  |  |
| `ring_idx` | integer | YES |  |  |

**Индексы:**
- `spr_taiyi_palace_ring_pkey` — UNIQUE PK (palace_id)

#### `spr_taiyi_qing_long_start`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `day_branch_id` | integer | NO |  |  |
| `start_hour_idx` | integer | YES |  |  |

**Индексы:**
- `spr_taiyi_qing_long_start_pkey` — UNIQUE PK (day_branch_id)

#### `spr_taiyi_spirits`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `id` | integer | NO |  |  |
| `code` | text | YES |  |  |
| `name_cn` | text | YES |  |  |
| `name_ru` | text | YES |  |  |
| `lucky_score` | integer | YES |  |  |

**Индексы:**
- `spr_taiyi_spirits_pkey` — UNIQUE PK (id)

#### `spr_taiyi_star_start`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `cycle_type` | text | NO |  |  |
| `decade_idx` | integer | NO |  |  |
| `start_palace` | integer | YES |  |  |

**Индексы:**
- `spr_taiyi_star_start_pkey` — UNIQUE PK (cycle_type, decade_idx)

#### `spr_taiyi_stars`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `id` | integer | NO |  |  |
| `code` | text | YES |  |  |
| `name_cn` | text | YES |  |  |
| `name_ru` | text | YES |  |  |
| `lucky_score` | integer | YES |  |  |

**Индексы:**
- `spr_taiyi_stars_pkey` — UNIQUE PK (id)

#### `spr_taiyi_xi_shen`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `day_stem_id` | integer | NO |  |  |
| `palace_id` | integer | YES |  |  |

**Индексы:**
- `spr_taiyi_xi_shen_pkey` — UNIQUE PK (day_stem_id)

### Система анализа (Rule Engine)

#### `spr_analysis_scope`
*Области применения анализа (здоровье, бизнес и т.д.)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `scope_code` | text | NO |  |  |
| `name_ru` | text | NO |  |  |
| `description_ru` | text | YES |  |  |

**Индексы:**
- `spr_analysis_scope_pkey` — UNIQUE PK (scope_code)

#### `spr_indicator`
*Справочник индикаторов анализа (группировка правил)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `indicator_id` | bigint | NO |  |  |
| `code` | text | NO |  |  |
| `name_ru` | text | NO |  |  |
| `description_ru` | text | YES |  |  |
| `level` | text | NO |  |  |
| `value_type` | text | NO |  |  |
| `is_active` | bigint | NO |  |  |

**Индексы:**
- `spr_indicator_pkey` — UNIQUE PK (indicator_id)

#### `spr_indicator_scope`
*Связь индикаторов с областями применения*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `indicator_id` | bigint | NO |  |  |
| `scope_code` | text | NO |  |  |

**Индексы:**
- `spr_indicator_scope_pkey` — UNIQUE PK (indicator_id, scope_code)

#### `spr_indicator_value`
*Значения индикаторов с числовым score*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `value_id` | bigint | NO |  |  |
| `indicator_id` | bigint | NO |  |  |
| `code` | text | NO |  |  |
| `name_ru` | text | NO |  |  |
| `description_ru` | text | YES |  |  |
| `favorable_actions` | text | YES |  |  |
| `unfavorable_actions` | text | YES |  |  |
| `interpretation_ru` | text | YES |  |  |
| `numeric_score` | double precision | NO |  |  |

**Индексы:**
- `spr_indicator_value_pkey` — UNIQUE PK (value_id)

#### `spr_element_display`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `element_id` | integer | NO | nextval('spr_element_display_element_id_seq'::regclass) |  |
| `element_name_ru` | text | NO |  |  |
| `element_name_en` | text | YES |  |  |
| `element_char` | text | YES |  |  |
| `color_hex` | text | YES | '#000000'::text |  |
| `bg_color_hex` | text | YES | '#ffffff'::text |  |
| `text_color_hex` | text | YES | '#000000'::text |  |
| `display_order` | integer | YES | 0 |  |

**Индексы:**
- `spr_element_display_element_name_ru_key` — UNIQUE (element_name_ru)
- `spr_element_display_pkey` — UNIQUE PK (element_id)

### СКДГ (Секретный Код Дракона)

#### `spr_scdg`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `id` | integer | NO | nextval('spr_scdg_id_seq'::regclass) |  |
| `jiazi_id` | integer | YES |  |  |
| `stem` | text | YES |  |  |
| `branch` | text | YES |  |  |
| `family_name` | text | YES |  |  |
| `parent_child` | text | YES |  |  |
| `family_role` | text | YES |  |  |
| `element_name` | text | YES |  |  |
| `element_glyph` | text | YES |  |  |
| `stem_element` | text | YES |  |  |
| `branch_animal` | text | YES |  |  |
| `element_num` | integer | YES |  |  |
| `period_num` | integer | YES |  |  |
| `hexagram_num` | integer | YES |  |  |
| `hexagram_name` | text | YES |  |  |
| `degrees_from` | numeric | YES |  |  |
| `degrees_to` | numeric | YES |  |  |
| `direction` | text | YES |  |  |
| `outer_gua_1` | integer | YES |  |  |
| `outer_gua_2` | integer | YES |  |  |
| `outer_gua_3` | integer | YES |  |  |
| `score_1` | integer | YES |  |  |
| `score_2` | integer | YES |  |  |
| `score_3` | integer | YES |  |  |
| `score_4` | integer | YES |  |  |
| `score_5` | integer | YES |  |  |
| `score_6` | integer | YES |  |  |

**Индексы:**
- `spr_scdg_pkey` — UNIQUE PK (id)

#### `spr_skdg_hexagram_pairs`
*СКДГ: пары гексаграмм по комбинациям Хэ Ту, Комб.10, одинаковый элемент/период*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `jiazi_id_a` | integer | NO |  |  |
| `pillar_a` | text | NO |  |  |
| `el_a` | integer | NO |  |  |
| `per_a` | integer | NO |  |  |
| `jiazi_id_b` | integer | NO |  |  |
| `pillar_b` | text | NO |  |  |
| `el_b` | integer | NO |  |  |
| `per_b` | integer | NO |  |  |
| `is_hetu_el_per` | boolean | YES | false |  |
| `is_c10_el_per` | boolean | YES | false |  |
| `is_same_element` | boolean | YES | false |  |
| `is_same_period` | boolean | YES | false |  |

**Индексы:**
- `spr_skdg_hexagram_pairs_pkey` — UNIQUE PK (jiazi_id_a, jiazi_id_b)

#### `spr_skdg_wuxing_relation`
*СКДГ: отношения У-Син между группами элементов Хэ Ту (1=Вода,2=Огонь,3=Дерево,4=Металл)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `group_a` | integer | NO |  |  |
| `group_b` | integer | NO |  |  |
| `group_a_name` | text | NO |  |  |
| `group_b_name` | text | NO |  |  |
| `relation` | text | NO |  |  |
| `relation_ru` | text | NO |  |  |

**Индексы:**
- `spr_skdg_wuxing_relation_pkey` — UNIQUE PK (group_a, group_b)

### Сервисные

#### `spr_table_comment`
*Хранилище комментариев к таблицам (legacy/резерв)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `table_name` | text | NO |  |  |
| `comment_text` | text | NO |  |  |

**Индексы:**
- `spr_table_comment_pkey` — UNIQUE PK (table_name)

#### `spr_column_comment`
*Хранилище комментариев к колонкам (legacy/резерв)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `table_name` | text | NO |  |  |
| `column_name` | text | NO |  |  |
| `comment_text` | text | NO |  |  |

**Индексы:**
- `spr_column_comment_pkey` — UNIQUE PK (table_name, column_name)

---
## Таблицы данных (t_*)

### Базовые расчёты и сетка времени

#### `t_time_grid_hourly`
*Сетка двухчасовых слотов (основа для t_bazi_hourly)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `dt_utc` | text | NO |  |  |
| `dt_gmt0` | text | NO |  |  |
| `year` | bigint | NO |  |  |
| `month` | bigint | NO |  |  |
| `day` | bigint | NO |  |  |
| `hour` | bigint | NO |  |  |
| `weekday` | bigint | NO |  |  |

#### `t_bazi_hourly`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `hour_id` | text | NO |  |  |
| `tz_offset_hours` | integer | NO |  |  |
| `slot_start_date_utc` | text | NO |  |  |
| `slot_start_time_utc` | text | NO |  |  |
| `slot_end_date_utc` | text | YES |  |  |
| `slot_end_time_utc` | text | YES |  |  |
| `slot_start_date_local` | text | YES |  |  |
| `slot_start_time_local` | text | YES |  |  |
| `slot_end_date_local` | text | YES |  |  |
| `slot_end_time_local` | text | YES |  |  |
| `weekday_local` | text | YES |  |  |
| `solar_term_id` | integer | YES |  |  |
| `year_pillar` | text | YES |  |  |
| `month_pillar` | text | YES |  |  |
| `day_pillar` | text | YES |  |  |
| `hour_pillar` | text | YES |  |  |
| `year_stem` | text | YES |  |  |
| `year_branch` | text | YES |  |  |
| `month_stem` | text | YES |  |  |
| `month_branch` | text | YES |  |  |
| `day_stem` | text | YES |  |  |
| `day_branch` | text | YES |  |  |
| `hour_stem` | text | YES |  |  |
| `hour_branch` | text | YES |  |  |
| `lunar_month` | integer | YES |  |  |
| `lunar_day` | integer | YES |  |  |
| `lunar_is_leap` | integer | YES |  |  |
| `lunar_month_zi` | integer | YES |  |  |
| `lunar_day_zi` | integer | YES |  |  |
| `lunar_is_leap_zi` | integer | YES |  |  |
| `year_int` | integer | YES |  |  |

**Индексы:**
- `idx_bazi_hourly_local` — (tz_offset_hours, slot_start_date_local, slot_start_time_local)
- `idx_bazi_hourly_utc` — (tz_offset_hours, slot_start_date_utc, slot_start_time_utc)
- `t_bazi_hourly_pkey` — UNIQUE PK (tz_offset_hours, slot_start_date_utc, slot_start_time_utc)

#### `t_solar_term_time`
*Точное время наступления солнечных терминов (астрономический расчёт)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `year` | integer | NO |  |  |
| `solar_term_id` | integer | NO |  |  |
| `longitude_deg` | integer | NO |  |  |
| `crossing_utc` | timestamp without time zone | NO |  |  |
| `crossing_gmt0` | timestamp without time zone | NO |  |  |

**Индексы:**
- `t_solar_term_time_pkey` — UNIQUE PK (year, solar_term_id)

**Внешние ключи:**
- `solar_term_id` → `spr_solar_term.solar_term_id`

#### `t_solar_term_time_hko`
*Время солнечных терминов из HKO (контрольные данные)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `year` | integer | NO |  |  |
| `solar_term_id` | integer | NO |  |  |
| `longitude_deg` | integer | NO |  |  |
| `crossing_hkt` | timestamp without time zone | NO |  |  |
| `crossing_utc` | timestamp without time zone | NO |  |  |
| `tz_offset_hours` | integer | NO | 8 |  |

**Индексы:**
- `t_solar_term_time_hko_pkey` — UNIQUE PK (year, solar_term_id)

**Внешние ключи:**
- `solar_term_id` → `spr_solar_term.solar_term_id`

#### `t_flying_stars`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `hour_id` | text | NO |  |  |
| `palace` | integer | NO |  |  |
| `year_star` | integer | YES |  |  |
| `month_star` | integer | YES |  |  |
| `day_star` | integer | YES |  |  |
| `hour_star` | integer | YES |  |  |

**Индексы:**
- `idx_fs_hour` — (hour_id)
- `t_flying_stars_pkey` — UNIQUE PK (hour_id, palace)

### Результаты анализа (Rule Engine)

#### `t_rule_registry`
*Реестр правил анализа (predicate_code, period_type, is_active)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `rule_id` | text | NO |  | MD5-хеш ID правила (PK) |
| `name_ru` | text | NO |  |  |
| `predicate_code` | text | NO |  | Код предиката правила |
| `params_json` | text | YES |  |  |
| `score_base` | double precision | YES |  |  |
| `score_formula` | text | YES |  |  |
| `description` | text | YES |  | Описание правила |
| `is_active` | bigint | YES |  | 1=активное, 0=неактивное |
| `period_type` | text | YES | 'hour'::text | Уровень: year/month/day/hour |

**Индексы:**
- `t_rule_registry_pkey` — UNIQUE PK (rule_id)

#### `t_rule_scope`
*Связь правил с областями применения*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `rule_id` | text | NO |  |  |
| `scope_type` | text | NO |  |  |
| `is_stop` | bigint | YES |  |  |

**Индексы:**
- `t_rule_scope_pkey` — UNIQUE PK (rule_id, scope_type)

#### `t_analysis_year`
*Результаты анализа годового уровня (1 расчёт/год/правило)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `year` | integer | NO |  |  |
| `year_pillar` | text | NO |  |  |
| `rule_id` | text | NO |  |  |
| `result_value` | text | NO |  |  |
| `score` | double precision | YES |  |  |

**Индексы:**
- `t_analysis_year_pkey` — UNIQUE PK (year, rule_id, result_value, year_pillar)

#### `t_analysis_month`
*Результаты анализа месячного уровня (12 расчётов/год/правило)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `year` | integer | NO |  |  |
| `month` | integer | NO |  |  |
| `year_pillar` | text | NO |  |  |
| `month_pillar` | text | NO |  |  |
| `rule_id` | text | NO |  |  |
| `result_value` | text | NO |  |  |
| `score` | double precision | YES |  |  |

**Индексы:**
- `t_analysis_month_pkey` — UNIQUE PK (year, month, rule_id, result_value, year_pillar, month_pillar)

#### `t_analysis_day`
*Результаты анализа дневного уровня (~365 расчётов/год/правило)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `date_val` | date | NO |  | Дата |
| `year_pillar` | text | NO |  | Столп года |
| `month_pillar` | text | NO |  | Столп месяца |
| `day_pillar` | text | NO |  | Столп дня |
| `rule_id` | text | NO |  | ID правила (FK t_rule_registry) |
| `result_value` | text | NO |  | Текстовый результат правила |
| `score` | double precision | YES |  | Числовой score правила |

**Индексы:**
- `t_analysis_day_pkey` — UNIQUE PK (date_val, rule_id, result_value, year_pillar, month_pillar, day_pillar)

#### `t_analysis_hour`
*Результаты анализа часового уровня (~8760 расчётов/год/правило)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `hour_id` | text | NO |  | ID часового слота (FK t_bazi_hourly) |
| `year_pillar` | text | YES |  | Столп года |
| `month_pillar` | text | YES |  | Столп месяца |
| `day_pillar` | text | YES |  | Столп дня |
| `hour_pillar` | text | YES |  | Столп часа |
| `rule_id` | text | NO |  | ID правила (FK t_rule_registry) |
| `result_value` | text | YES |  | Текстовый результат |
| `score` | double precision | YES |  | Числовой score |

**Индексы:**
- `t_analysis_hour_pkey` — UNIQUE PK (hour_id, rule_id)

#### `t_analysis_date`
*Дополнительные данные анализа по датам*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `hour_id` | text | NO |  |  |
| `rule_id` | text | NO |  |  |
| `result_value` | text | YES |  |  |
| `score` | double precision | YES |  |  |

**Индексы:**
- `t_analysis_date_pkey` — UNIQUE PK (hour_id, rule_id)

#### `t_analysis_direction`
*Базовая таблица анализа направлений*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `hour_id` | text | NO |  |  |
| `palace_no` | bigint | NO |  |  |
| `system_type` | text | NO |  |  |
| `chart_level` | text | NO |  |  |
| `rule_id` | text | NO |  |  |
| `result_value` | text | YES |  |  |
| `score` | double precision | YES |  |  |

**Индексы:**
- `t_analysis_direction_pkey` — UNIQUE PK (hour_id, palace_no, system_type, chart_level, rule_id)

#### `t_analysis_direction_year`
*Анализ направлений: годовой уровень*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `year` | integer | NO |  |  |
| `year_pillar` | text | NO |  |  |
| `palace_no` | integer | NO |  |  |
| `system_type` | text | NO |  |  |
| `rule_id` | text | NO |  |  |
| `result_value` | text | YES |  |  |
| `score` | double precision | YES |  |  |

**Индексы:**
- `t_analysis_direction_year_pkey` — UNIQUE PK (year, palace_no, system_type, rule_id, year_pillar)

#### `t_analysis_direction_month`
*Анализ направлений: месячный уровень*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `year` | integer | NO |  |  |
| `month` | integer | NO |  |  |
| `year_pillar` | text | NO |  |  |
| `month_pillar` | text | NO |  |  |
| `palace_no` | integer | NO |  |  |
| `system_type` | text | NO |  |  |
| `rule_id` | text | NO |  |  |
| `result_value` | text | YES |  |  |
| `score` | double precision | YES |  |  |

**Индексы:**
- `t_analysis_direction_month_pkey` — UNIQUE PK (year, month, palace_no, system_type, rule_id, year_pillar, month_pillar)

#### `t_analysis_direction_day`
*Анализ направлений: дневной уровень (Ци Мэнь)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `date_val` | date | NO |  |  |
| `year_pillar` | text | NO |  |  |
| `month_pillar` | text | NO |  |  |
| `day_pillar` | text | NO |  |  |
| `palace_no` | integer | NO |  |  |
| `system_type` | text | NO |  |  |
| `rule_id` | text | NO |  |  |
| `result_value` | text | YES |  |  |
| `score` | double precision | YES |  |  |

**Индексы:**
- `t_analysis_direction_day_pkey` — UNIQUE PK (date_val, palace_no, system_type, rule_id, year_pillar, month_pillar, day_pillar)

#### `t_analysis_direction_hour`
*Анализ направлений: часовой уровень (Ци Мэнь)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `hour_id` | text | NO |  |  |
| `year_pillar` | text | YES |  |  |
| `month_pillar` | text | YES |  |  |
| `day_pillar` | text | YES |  |  |
| `hour_pillar` | text | YES |  |  |
| `palace_no` | integer | NO |  |  |
| `system_type` | text | NO |  |  |
| `rule_id` | text | NO |  |  |
| `result_value` | text | YES |  |  |
| `score` | double precision | YES |  |  |

**Индексы:**
- `t_analysis_direction_hour_pkey` — UNIQUE PK (hour_id, palace_no, system_type, rule_id)

### Ци Мэнь Дунь Цзя

#### `t_qumen_chauby_hourly`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `chart_id` | text | NO |  |  |
| `hour_id` | text | NO |  |  |
| `rasklad_id` | text | YES |  |  |
| `palace_no` | integer | YES |  |  |
| `chart_type` | text | YES |  |  |

**Индексы:**
- `idx_qimen_cb_hr_hour` — (hour_id)
- `t_qumen_chauby_hourly_pkey` — UNIQUE PK (chart_id)

#### `t_qumen_dgiren_day`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `chart_id` | text | NO |  |  |
| `year_pillar` | text | YES |  |  |
| `month_pillar` | text | YES |  |  |
| `day_pillar` | text | YES |  |  |
| `rasklad_id` | text | YES |  |  |
| `palace_no` | integer | YES |  |  |
| `chart_type` | text | YES |  |  |

**Индексы:**
- `idx_qimen_d_date` — (year_pillar, month_pillar, day_pillar)
- `t_qumen_dgiren_day_pkey` — UNIQUE PK (chart_id)

#### `t_qumen_dgiren_hourly`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `chart_id` | text | NO |  |  |
| `hour_id` | text | NO |  |  |
| `rasklad_id` | text | YES |  |  |
| `palace_no` | integer | YES |  |  |
| `chart_type` | text | YES |  |  |

**Индексы:**
- `idx_qimen_hr_hour` — (hour_id)
- `t_qumen_dgiren_hourly_pkey` — UNIQUE PK (chart_id)

#### `t_qumen_dgiren_month`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `chart_id` | text | NO |  |  |
| `year_pillar` | text | YES |  |  |
| `month_pillar` | text | YES |  |  |
| `rasklad_id` | text | YES |  |  |
| `palace_no` | integer | YES |  |  |
| `chart_type` | text | YES |  |  |

**Индексы:**
- `t_qumen_dgiren_month_pkey` — UNIQUE PK (chart_id)

#### `t_qumen_dgiren_year`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `chart_id` | text | NO |  |  |
| `year_pillar` | text | YES |  |  |
| `rasklad_id` | text | YES |  |  |
| `palace_no` | integer | YES |  |  |
| `chart_type` | text | YES |  |  |

**Индексы:**
- `t_qumen_dgiren_year_pkey` — UNIQUE PK (chart_id)

#### `t_qumen_tayi_day`
*Итоговый дневной расклад Тай И (плоский: 9 строк/день, 1 строка/дворец)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `date_val` | date | NO |  | Дата (PK часть 1) |
| `palace_no` | smallint | NO |  | Номер дворца 1-9 (PK часть 2) |
| `year_pillar` | text | YES |  | Столп года |
| `month_pillar` | text | YES |  | Столп месяца |
| `day_pillar` | text | YES |  | Столп дня |
| `run_type` | text | YES |  | Тип цикла YIN/YANG |
| `tai_yi_palace` | smallint | YES |  | Дворец Тай И (денормализовано) |
| `xiu_men_palace` | smallint | YES |  | Дворец Врат Отдыха |
| `xi_shen_palace` | smallint | YES |  | Дворец Духа Счастья |
| `star` | text | YES |  | Звезда дворца (иероглиф) |
| `gate` | text | YES |  | Врата дворца (иероглиф, NULL для P5) |
| `hhd_spirits` | text | YES |  | Духи ХХД направления (иероглифы, / для 2-ветвевых) |
| `jianchu` | text | YES |  | 建除 направления (иероглифы) |
| `is_xi_shen` | smallint | YES | 0 | Флаг: Дух Счастья в этом дворце |
| `is_noble` | smallint | YES | 0 | Флаг: благородное направление (OR) |
| `is_kong_wang` | smallint | YES | 0 | Флаг: пустота направления (OR) |
| `gate_score` | real | YES | 0 | Score врат (-1/0/1) |
| `star_score` | real | YES | 0 | Score звезды (-1/0/1) |
| `jianchu_score` | real | YES | 0 | Score 建除 (avg для 2-ветвевых) |
| `total_score` | real | YES | 0 | Итого: (gate*2+star*2+jianchu+xi_shen+noble)*(1-kong_wang) |

**Индексы:**
- `t_qumen_tayi_day_pkey` — UNIQUE PK (date_val, palace_no)

### Тай И Шэнь Шу

#### `t_taiyi_day`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `date_val` | date | NO |  |  |
| `day_ganzhi_idx` | integer | YES |  |  |
| `day_stem` | integer | YES |  |  |
| `day_branch` | integer | YES |  |  |
| `solar_term_id` | integer | YES |  |  |
| `run_type` | text | YES |  |  |
| `xiu_men_palace` | integer | YES |  |  |
| `tai_yi_palace` | integer | YES |  |  |
| `xi_shen_palace` | integer | YES |  |  |
| `palace_1_score` | integer | YES |  |  |
| `palace_2_score` | integer | YES |  |  |
| `palace_3_score` | integer | YES |  |  |
| `palace_4_score` | integer | YES |  |  |
| `palace_5_score` | integer | YES |  |  |
| `palace_6_score` | integer | YES |  |  |
| `palace_7_score` | integer | YES |  |  |
| `palace_8_score` | integer | YES |  |  |
| `palace_9_score` | integer | YES |  |  |
| `chart_data` | jsonb | YES |  |  |

**Индексы:**
- `t_taiyi_day_pkey` — UNIQUE PK (date_val)

#### `t_taiyi_hours`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `date_val` | date | NO |  |  |
| `hour_branch` | integer | NO |  |  |
| `spirit_name` | text | YES |  |  |
| `spirit_score` | integer | YES |  |  |
| `is_noble` | boolean | YES |  |  |
| `is_kong_wang` | boolean | YES |  |  |

**Индексы:**
- `idx_taiyi_hours_date` — (date_val)
- `t_taiyi_hours_pkey` — UNIQUE PK (date_val, hour_branch)

### Тун Шу

#### `t_tung_shu_daily`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `calendar_date` | date | NO |  |  |
| `year_pillar` | text | YES |  |  |
| `month_pillar` | text | YES |  |  |
| `day_pillar` | text | YES |  |  |
| `year_stem` | text | YES |  |  |
| `year_branch` | text | YES |  |  |
| `month_stem` | text | YES |  |  |
| `month_branch` | text | YES |  |  |
| `day_stem` | text | YES |  |  |
| `day_branch` | text | YES |  |  |
| `solar_term_id` | integer | YES |  |  |
| `solar_term_char` | text | YES |  |  |
| `solar_term_name_ru` | text | YES |  |  |
| `nayin_element` | text | YES |  |  |
| `nayin_name` | text | YES |  |  |
| `day_officer_char` | text | YES |  |  |
| `day_officer_name_ru` | text | YES |  |  |
| `day_officer_category` | text | YES |  |  |
| `constellation_char` | text | YES |  |  |
| `constellation_name_ru` | text | YES |  |  |
| `constellation_direction` | text | YES |  |  |
| `constellation_nature` | text | YES |  |  |
| `belt_type` | text | YES |  |  |
| `belt_stars` | text | YES |  |  |
| `moon_phase_name` | text | YES |  |  |
| `moon_phase_pct` | real | YES |  |  |
| `tongshu_phase_name_ru` | text | YES |  |  |
| `created_at` | timestamp without time zone | YES | CURRENT_TIMESTAMP |  |
| `year_nayin_element` | text | YES |  |  |
| `year_nayin_name` | text | YES |  |  |
| `month_nayin_element` | text | YES |  |  |
| `month_nayin_name` | text | YES |  |  |
| `day_nayin_element` | text | YES |  |  |
| `day_nayin_name` | text | YES |  |  |
| `year_period` | integer | YES |  |  |
| `month_period` | integer | YES |  |  |
| `day_period` | integer | YES |  |  |
| `year_element_num` | integer | YES |  |  |
| `month_element_num` | integer | YES |  |  |
| `day_element_num` | integer | YES |  |  |
| `hexagram_family_same` | integer | YES |  |  |
| `production_chain` | integer | YES |  |  |
| `lunar_day` | integer | YES |  |  |

**Индексы:**
- `t_tung_shu_daily_pkey` — UNIQUE PK (calendar_date)

### CRM

#### `t_crm_client`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `id` | integer | NO | nextval('t_crm_client_id_seq'::regclass) |  |
| `name` | character varying(255) | NO |  |  |
| `email` | character varying(255) | YES |  |  |
| `phone` | character varying(50) | YES |  |  |
| `birth_date` | date | YES |  |  |
| `birth_time` | character varying(10) | YES |  |  |
| `notes` | text | YES |  |  |
| `created_at` | timestamp with time zone | YES | now() |  |
| `updated_at` | timestamp with time zone | YES | now() |  |

**Индексы:**
- `ix_t_crm_client_email` — (email)
- `ix_t_crm_client_id` — (id)
- `ix_t_crm_client_name` — (name)
- `ix_t_crm_client_phone` — (phone)
- `t_crm_client_pkey` — UNIQUE PK (id)

#### `t_crm_calculation`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `id` | integer | NO | nextval('t_crm_calculation_id_seq'::regclass) |  |
| `client_id` | integer | NO |  |  |
| `calculation_type` | character varying(50) | NO |  |  |
| `reference_id` | character varying(255) | NO |  |  |
| `notes` | text | YES |  |  |
| `created_at` | timestamp with time zone | YES | now() |  |

**Индексы:**
- `ix_t_crm_calculation_calculation_type` — (calculation_type)
- `ix_t_crm_calculation_id` — (id)
- `t_crm_calculation_pkey` — UNIQUE PK (id)

**Внешние ключи:**
- `client_id` → `t_crm_client.id`

#### `t_crm_note`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `id` | integer | NO | nextval('t_crm_note_id_seq'::regclass) |  |
| `client_id` | integer | NO |  |  |
| `note_text` | text | NO |  |  |
| `calculation_id` | character varying(255) | YES |  |  |
| `created_at` | timestamp with time zone | YES | now() |  |

**Индексы:**
- `ix_t_crm_note_id` — (id)
- `t_crm_note_pkey` — UNIQUE PK (id)

**Внешние ключи:**
- `client_id` → `t_crm_client.id`

#### `t_crm_session`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `id` | integer | NO | nextval('t_crm_session_id_seq'::regclass) |  |
| `client_id` | integer | NO |  |  |
| `date` | date | NO |  |  |
| `notes` | text | YES |  |  |
| `summary` | text | YES |  |  |
| `created_at` | timestamp with time zone | YES | now() |  |

**Индексы:**
- `ix_t_crm_session_date` — (date)
- `ix_t_crm_session_id` — (id)
- `t_crm_session_pkey` — UNIQUE PK (id)

**Внешние ключи:**
- `client_id` → `t_crm_client.id`

### Профили и карты рождения

#### `t_profile`
*Профили пользователей для персонализированных расчетов*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `id` | integer | NO | nextval('t_profile_id_seq'::regclass) |  |
| `name` | character varying(255) | NO |  | Имя человека |
| `birth_date` | date | NO |  | Дата рождения |
| `birth_time` | time without time zone | YES |  | Время рождения |
| `birth_city` | character varying(255) | YES |  | Город рождения |
| `birth_city_lat` | numeric(10,7) | YES |  | Широта города рождения |
| `birth_city_lon` | numeric(10,7) | YES |  | Долгота города рождения |
| `birth_timezone` | character varying(50) | YES |  | Часовой пояс (IANA) |
| `notes` | text | YES |  | Заметки |
| `created_at` | timestamp with time zone | YES | CURRENT_TIMESTAMP |  |
| `updated_at` | timestamp with time zone | YES | CURRENT_TIMESTAMP |  |

**Индексы:**
- `idx_profile_birth_date` — (birth_date)
- `idx_profile_name` — (name)
- `t_profile_pkey` — UNIQUE PK (id)

#### `t_profile_birth_chart`
*Рассчитанные карты рождения (8 столпов)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `id` | integer | NO | nextval('t_profile_birth_chart_id_seq'::regclass) |  |
| `profile_id` | integer | NO |  |  |
| `year_pillar` | character varying(10) | YES |  |  |
| `month_pillar` | character varying(10) | YES |  |  |
| `day_pillar` | character varying(10) | YES |  |  |
| `hour_pillar` | character varying(10) | YES |  |  |
| `day_master` | character varying(10) | YES |  |  |
| `day_master_element` | character varying(20) | YES |  |  |
| `calculated_at` | timestamp with time zone | YES | CURRENT_TIMESTAMP |  |

**Индексы:**
- `t_profile_birth_chart_pkey` — UNIQUE PK (id)
- `uq_profile_birth_chart` — UNIQUE (profile_id)

**Внешние ключи:**
- `profile_id` → `t_profile.id`

#### `t_profile_history`
*История обращений к профилю*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `id` | integer | NO | nextval('t_profile_history_id_seq'::regclass) |  |
| `profile_id` | integer | NO |  |  |
| `action_type` | character varying(50) | NO |  |  |
| `module` | character varying(50) | YES |  |  |
| `reference_date` | date | YES |  |  |
| `notes` | text | YES |  |  |
| `created_at` | timestamp with time zone | YES | CURRENT_TIMESTAMP |  |

**Индексы:**
- `idx_profile_history_created_at` — (created_at)
- `idx_profile_history_profile_id` — (profile_id)
- `t_profile_history_pkey` — UNIQUE PK (id)

**Внешние ключи:**
- `profile_id` → `t_profile.id`

### Система и журналы

#### `t_event`

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `id` | text | NO |  |  |
| `dt_start` | timestamp without time zone | NO |  |  |
| `dt_end` | timestamp without time zone | NO |  |  |
| `calendar` | text | NO |  |  |
| `title` | text | NO |  |  |
| `comment` | text | YES |  |  |

**Индексы:**
- `t_event_pkey` — UNIQUE PK (id)

#### `t_sys_calculation_log`
*Журнал расчётов: этапы, длительность, ошибки*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `id` | bigint | NO |  |  |
| `stage_name` | text | NO |  |  |
| `start_dt` | text | NO |  |  |
| `end_dt` | text | YES |  |  |
| `duration_sec` | double precision | YES |  |  |
| `record_count` | bigint | YES |  |  |
| `status` | text | YES |  |  |
| `error_msg` | text | YES |  |  |

**Индексы:**
- `t_sys_calculation_log_pkey` — UNIQUE PK (id)

### Контрольные данные

#### `t_control_t_bazi_hourly`
*Контрольные данные для верификации t_bazi_hourly*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `hour_id` | text | YES |  |  |
| `tz_offset_hours` | integer | YES |  |  |
| `slot_start_date_utc` | text | YES |  |  |
| `slot_start_time_utc` | text | YES |  |  |
| `slot_end_date_utc` | text | YES |  |  |
| `slot_end_time_utc` | text | YES |  |  |
| `slot_start_date_local` | text | YES |  |  |
| `slot_start_time_local` | text | YES |  |  |
| `slot_end_date_local` | text | YES |  |  |
| `slot_end_time_local` | text | YES |  |  |
| `weekday_local` | text | YES |  |  |
| `solar_term_id` | integer | YES |  |  |
| `solar_term_name` | text | YES |  |  |
| `year_pillar` | text | YES |  |  |
| `month_pillar` | text | YES |  |  |
| `day_pillar` | text | YES |  |  |
| `hour_pillar` | text | YES |  |  |
| `year_stem` | text | YES |  |  |
| `year_branch` | text | YES |  |  |
| `month_stem` | text | YES |  |  |
| `month_branch` | text | YES |  |  |
| `day_stem` | text | YES |  |  |
| `day_branch` | text | YES |  |  |
| `hour_stem` | text | YES |  |  |
| `hour_branch` | text | YES |  |  |
| `lunar_month` | integer | YES |  |  |
| `lunar_day` | integer | YES |  |  |
| `lunar_is_leap` | integer | YES |  |  |
| `lunar_month_zi` | integer | YES |  |  |
| `lunar_day_zi` | integer | YES |  |  |
| `lunar_is_leap_zi` | integer | YES |  |  |
| `day_officer_value_id` | integer | YES |  |  |

#### `t_control_t_flying_stars`
*Контрольные данные для верификации t_flying_stars*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `hour_id` | text | YES |  |  |
| `palace` | integer | YES |  |  |
| `year_star` | integer | YES |  |  |
| `month_star` | integer | YES |  |  |
| `day_star` | integer | YES |  |  |
| `hour_star` | integer | YES |  |  |

#### `t_control_t_qumen_chauby_hourly`
*Контрольные данные для Ци Мэнь Чай Бу (часовой)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `chart_id` | text | YES |  |  |
| `hour_id` | text | YES |  |  |
| `rasklad_id` | text | YES |  |  |
| `palace_no` | integer | YES |  |  |
| `chart_type` | text | YES |  |  |

#### `t_control_t_qumen_dgiren_day`
*Контрольные данные для Ци Мэнь Чжи Жэнь (дневной)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `chart_id` | text | YES |  |  |
| `year_pillar` | text | YES |  |  |
| `month_pillar` | text | YES |  |  |
| `day_pillar` | text | YES |  |  |
| `rasklad_id` | text | YES |  |  |
| `palace_no` | integer | YES |  |  |
| `chart_type` | text | YES |  |  |

#### `t_control_t_qumen_dgiren_hourly`
*Контрольные данные для Ци Мэнь Чжи Жэнь (часовой)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `chart_id` | text | YES |  |  |
| `hour_id` | text | YES |  |  |
| `rasklad_id` | text | YES |  |  |
| `palace_no` | integer | YES |  |  |
| `chart_type` | text | YES |  |  |

#### `t_control_t_qumen_dgiren_month`
*Контрольные данные для Ци Мэнь Чжи Жэнь (месячный)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `chart_id` | text | YES |  |  |
| `year_pillar` | text | YES |  |  |
| `month_pillar` | text | YES |  |  |
| `rasklad_id` | text | YES |  |  |
| `palace_no` | integer | YES |  |  |
| `chart_type` | text | YES |  |  |

#### `t_control_t_qumen_dgiren_year`
*Контрольные данные для Ци Мэнь Чжи Жэнь (годовой)*

| Колонка | Тип | NULL | DEFAULT | Комментарий |
|---------|-----|------|---------|-------------|
| `chart_id` | text | YES |  |  |
| `year_pillar` | text | YES |  |  |
| `rasklad_id` | text | YES |  |  |
| `palace_no` | integer | YES |  |  |
| `chart_type` | text | YES |  |  |

---
## Индексы

Все индексы используют тип **btree**. Каждая таблица имеет первичный ключ (PK).
Дополнительные индексы созданы для часто используемых столбцов.

| Таблица | Индекс | Тип | Столбцы |
|---------|--------|-----|---------|
| `spr_bazi_qi_phase` | `idx_qi_phase_stem_branch` | btree | stem_char, branch_char |
| `spr_element_display` | `spr_element_display_element_name_ru_key` | btree | element_name_ru |
| `spr_jiazi_extended` | `idx_jiazi_stem_branch` | btree | stem, branch |
| `spr_qimen_templates` | `idx_qimen_templates_rasklad` | btree | rasklad_id, palace_no |
| `spr_qimen_templates` | `idx_qimen_templates_stems` | btree | heaven_stem, earth_stem |
| `t_bazi_hourly` | `idx_bazi_hourly_local` | btree | tz_offset_hours, slot_start_date_local, slot_start_time_local |
| `t_bazi_hourly` | `idx_bazi_hourly_utc` | btree | tz_offset_hours, slot_start_date_utc, slot_start_time_utc |
| `t_crm_calculation` | `ix_t_crm_calculation_calculation_type` | btree | calculation_type |
| `t_crm_calculation` | `ix_t_crm_calculation_id` | btree | id |
| `t_crm_client` | `ix_t_crm_client_email` | btree | email |
| `t_crm_client` | `ix_t_crm_client_id` | btree | id |
| `t_crm_client` | `ix_t_crm_client_name` | btree | name |
| `t_crm_client` | `ix_t_crm_client_phone` | btree | phone |
| `t_crm_note` | `ix_t_crm_note_id` | btree | id |
| `t_crm_session` | `ix_t_crm_session_date` | btree | date |
| `t_crm_session` | `ix_t_crm_session_id` | btree | id |
| `t_flying_stars` | `idx_fs_hour` | btree | hour_id |
| `t_profile` | `idx_profile_birth_date` | btree | birth_date |
| `t_profile` | `idx_profile_name` | btree | name |
| `t_profile_birth_chart` | `uq_profile_birth_chart` | btree | profile_id |
| `t_profile_history` | `idx_profile_history_created_at` | btree | created_at |
| `t_profile_history` | `idx_profile_history_profile_id` | btree | profile_id |
| `t_qumen_chauby_hourly` | `idx_qimen_cb_hr_hour` | btree | hour_id |
| `t_qumen_dgiren_day` | `idx_qimen_d_date` | btree | year_pillar, month_pillar, day_pillar |
| `t_qumen_dgiren_hourly` | `idx_qimen_hr_hour` | btree | hour_id |
| `t_taiyi_hours` | `idx_taiyi_hours_date` | btree | date_val |

---
## Внешние ключи

| Таблица | Колонка | Ссылается на |
|---------|---------|--------------|
| `spr_tongshu_black_rabbit_star` | `cycle_index` | `spr_tongshu_jiazi_profile.cycle_index` |
| `t_crm_calculation` | `client_id` | `t_crm_client.id` |
| `t_crm_note` | `client_id` | `t_crm_client.id` |
| `t_crm_session` | `client_id` | `t_crm_client.id` |
| `t_profile_birth_chart` | `profile_id` | `t_profile.id` |
| `t_profile_history` | `profile_id` | `t_profile.id` |
| `t_solar_term_time` | `solar_term_id` | `spr_solar_term.solar_term_id` |
| `t_solar_term_time_hko` | `solar_term_id` | `spr_solar_term.solar_term_id` |

---
## Триггеры и функции

| Триггер | Таблица | Тайминг | Событие | Функция |
|---------|---------|---------|---------|---------|
| `trg_profile_updated_at` | `t_profile` | BEFORE | UPDATE | `update_profile_updated_at` |

---
## Представления (Views)

На момент генерации в схеме `public` **нет** представлений.
Исторические views были задокументированы в `data/ddl_views.sql` (архив).

---
## Полный DDL

Полный DDL схемы доступен в:
- `data/ddl_full_schema_raw.sql` — `pg_dump --schema-only --no-owner --no-privileges`
- `data/ddl_comments.sql` — `COMMENT ON` для таблиц и колонок

---
*Конец документа*