#!/usr/bin/env python3
"""Generate PostgreSQL schema documentation from metadata queries."""

import json
import os

# This script reads schema metadata collected via SQL queries and generates
# a markdown file. Run after updating the database schema.

# Table comments collected from pg_description
table_comments = {
    "spr_analysis_scope": "Области применения анализа (здоровье, бизнес и т.д.)",
    "spr_bazi_qi_phase": "Фазы Ци столпов (месяц/день/час)",
    "spr_column_comment": "Хранилище комментариев к колонкам (legacy/резерв)",
    "spr_day_officer_mapping": "Маппинг Дневных Офицеров (建除十二直) по ветви месяца + ветви дня",
    "spr_earthly_branch": "Справочник 12 Земных Ветвей (地支)",
    "spr_flying_star_map": "Карта Летящих Звёзд: период + направление → звёзды",
    "spr_gates": "Справочник 8 Врат Ци Мэнь Дуня (八門)",
    "spr_gods": "Справочник 8 Божеств Ци Мэнь Дуня (八神)",
    "spr_heavenly_stem": "Справочник 10 Небесных Стволов (天干)",
    "spr_hour_stars": "Часовые звёзды для Фэн Шуй",
    "spr_indicator": "Справочник индикаторов анализа (группировка правил)",
    "spr_indicator_scope": "Связь индикаторов с областями применения",
    "spr_indicator_value": "Значения индикаторов с числовым score",
    "spr_leader_stems": "Ведущие стволы для определения часового/месячного столпа",
    "spr_master_dano_mapping": "Маппинг Мастера Дун Гуна по ветви месяца + стволу/ветви дня",
    "spr_month_stars": "Месячные звёзды для Фэн Шуй",
    "spr_pillar_cycle": "Справочник столпов (год/месяц/день) для цикла Цзя-Цзы",
    "spr_pillar_hour_rule": "Правила вычисления часового столпа из дневного ствола",
    "spr_pillar_month_rule": "Правила вычисления месячного столпа из годового ствола",
    "spr_qimen_templates": "Шаблоны раскладов Ци Мэнь (базовые конфигурации)",
    "spr_skdg_hexagram_pairs": "СКДГ: пары гексаграмм по комбинациям Хэ Ту, Комб.10, одинаковый элемент/период",
    "spr_skdg_wuxing_relation": "СКДГ: отношения У-Син между группами элементов Хэ Ту (1=Вода,2=Огонь,3=Дерево,4=Металл)",
    "spr_solar_term": "Справочник 24 солнечных терминов (節氣)",
    "spr_stars": "Справочник 9 Звёзд Ци Мэнь Дуня (九星)",
    "spr_table_comment": "Хранилище комментариев к таблицам (legacy/резерв)",
    "spr_taiyi_jianchu": "Справочник 12 созвездий 建除十二神 с score",
    "spr_tongshu_black_rabbit_rating": "Оценки звёзд Чёрного Кролика по Тун Шу",
    "spr_tongshu_black_rabbit_star": "Звёзды Чёрного Кролика по Тун Шу",
    "spr_tongshu_branch_combo_rule": "Правила комбинаций Земных Ветвей (三合/六合/刑/冲/害/破)",
    "spr_tongshu_guigu_outcome": "Результаты Гуй Гу Шу (鬼谷數)",
    "spr_tongshu_jiazi_profile": "Профили 60 Цзя-Цзы по Тун Шу",
    "spr_tongshu_phase": "Фазы Ци (氣) по Тун Шу",
    "spr_tongshu_phase_mapping": "Маппинг фаз Ци по столпам",
    "spr_tongshu_shensha_rule": "Правила Шэнь Ша (神煞) — духи и демоны",
    "spr_tongshu_stem_combo_rule": "Правила комбинаций Небесных Стволов (合/冲)",
    "spr_tongshu_ten_god": "Справочник 10 Богов (十神)",
    "spr_yanqin_day_constellation": "Справочник 28 созвездий 演禽 по дню недели + группе ветвей",
    "spr_yellow_black_matrix": "Матрица Жёлтого/Чёрного пути: ветвь месяца + ветвь дня → ID звезды",
    "spr_yellow_black_stars": "Звёзды Жёлтого/Чёрного пути с оценкой (+1/-1)",
    "t_analysis_date": "Дополнительные данные анализа по датам",
    "t_analysis_day": "Результаты анализа дневного уровня (~365 расчётов/год/правило)",
    "t_analysis_direction": "Базовая таблица анализа направлений",
    "t_analysis_direction_day": "Анализ направлений: дневной уровень (Ци Мэнь)",
    "t_analysis_direction_hour": "Анализ направлений: часовой уровень (Ци Мэнь)",
    "t_analysis_direction_month": "Анализ направлений: месячный уровень",
    "t_analysis_direction_year": "Анализ направлений: годовой уровень",
    "t_analysis_hour": "Результаты анализа часового уровня (~8760 расчётов/год/правило)",
    "t_analysis_month": "Результаты анализа месячного уровня (12 расчётов/год/правило)",
    "t_analysis_year": "Результаты анализа годового уровня (1 расчёт/год/правило)",
    "t_control_t_bazi_hourly": "Контрольные данные для верификации t_bazi_hourly",
    "t_control_t_flying_stars": "Контрольные данные для верификации t_flying_stars",
    "t_control_t_qumen_chauby_hourly": "Контрольные данные для Ци Мэнь Чай Бу (часовой)",
    "t_control_t_qumen_dgiren_day": "Контрольные данные для Ци Мэнь Чжи Жэнь (дневной)",
    "t_control_t_qumen_dgiren_hourly": "Контрольные данные для Ци Мэнь Чжи Жэнь (часовой)",
    "t_control_t_qumen_dgiren_month": "Контрольные данные для Ци Мэнь Чжи Жэнь (месячный)",
    "t_control_t_qumen_dgiren_year": "Контрольные данные для Ци Мэнь Чжи Жэнь (годовой)",
    "t_profile": "Профили пользователей для персонализированных расчетов",
    "t_profile_birth_chart": "Рассчитанные карты рождения (8 столпов)",
    "t_profile_history": "История обращений к профилю",
    "t_qumen_tayi_day": "Итоговый дневной расклад Тай И (плоский: 9 строк/день, 1 строка/дворец)",
    "t_rule_registry": "Реестр правил анализа (predicate_code, period_type, is_active)",
    "t_rule_scope": "Связь правил с областями применения",
    "t_solar_term_time": "Точное время наступления солнечных терминов (астрономический расчёт)",
    "t_solar_term_time_hko": "Время солнечных терминов из HKO (контрольные данные)",
    "t_sys_calculation_log": "Журнал расчётов: этапы, длительность, ошибки",
    "t_time_grid_hourly": "Сетка двухчасовых слотов (основа для t_bazi_hourly)",
}

# Column comments
col_comments = {
    ("spr_earthly_branch", "branch_id"): "ID ветви (1-12)",
    ("spr_earthly_branch", "branch_char"): "Иероглиф ветви",
    ("spr_earthly_branch", "branch_pinyin"): "Пиньинь",
    ("spr_earthly_branch", "element"): "Элемент",
    ("spr_heavenly_stem", "stem_id"): "ID ствола (1-10)",
    ("spr_heavenly_stem", "stem_char"): "Иероглиф ствола",
    ("spr_heavenly_stem", "stem_pinyin"): "Пиньинь",
    ("spr_heavenly_stem", "element"): "Элемент (Дерево/Огонь/Земля/Металл/Вода)",
    ("t_analysis_day", "date_val"): "Дата",
    ("t_analysis_day", "year_pillar"): "Столп года",
    ("t_analysis_day", "month_pillar"): "Столп месяца",
    ("t_analysis_day", "day_pillar"): "Столп дня",
    ("t_analysis_day", "rule_id"): "ID правила (FK t_rule_registry)",
    ("t_analysis_day", "result_value"): "Текстовый результат правила",
    ("t_analysis_day", "score"): "Числовой score правила",
    ("t_analysis_hour", "hour_id"): "ID часового слота (FK t_bazi_hourly)",
    ("t_analysis_hour", "year_pillar"): "Столп года",
    ("t_analysis_hour", "month_pillar"): "Столп месяца",
    ("t_analysis_hour", "day_pillar"): "Столп дня",
    ("t_analysis_hour", "hour_pillar"): "Столп часа",
    ("t_analysis_hour", "rule_id"): "ID правила (FK t_rule_registry)",
    ("t_analysis_hour", "result_value"): "Текстовый результат",
    ("t_analysis_hour", "score"): "Числовой score",
    ("t_profile", "name"): "Имя человека",
    ("t_profile", "birth_date"): "Дата рождения",
    ("t_profile", "birth_time"): "Время рождения",
    ("t_profile", "birth_city"): "Город рождения",
    ("t_profile", "birth_city_lat"): "Широта города рождения",
    ("t_profile", "birth_city_lon"): "Долгота города рождения",
    ("t_profile", "birth_timezone"): "Часовой пояс (IANA)",
    ("t_profile", "notes"): "Заметки",
    ("t_qumen_tayi_day", "date_val"): "Дата (PK часть 1)",
    ("t_qumen_tayi_day", "palace_no"): "Номер дворца 1-9 (PK часть 2)",
    ("t_qumen_tayi_day", "year_pillar"): "Столп года",
    ("t_qumen_tayi_day", "month_pillar"): "Столп месяца",
    ("t_qumen_tayi_day", "day_pillar"): "Столп дня",
    ("t_qumen_tayi_day", "run_type"): "Тип цикла YIN/YANG",
    ("t_qumen_tayi_day", "tai_yi_palace"): "Дворец Тай И (денормализовано)",
    ("t_qumen_tayi_day", "xiu_men_palace"): "Дворец Врат Отдыха",
    ("t_qumen_tayi_day", "xi_shen_palace"): "Дворец Духа Счастья",
    ("t_qumen_tayi_day", "star"): "Звезда дворца (иероглиф)",
    ("t_qumen_tayi_day", "gate"): "Врата дворца (иероглиф, NULL для P5)",
    ("t_qumen_tayi_day", "hhd_spirits"): "Духи ХХД направления (иероглифы, / для 2-ветвевых)",
    ("t_qumen_tayi_day", "jianchu"): "建除 направления (иероглифы)",
    ("t_qumen_tayi_day", "is_xi_shen"): "Флаг: Дух Счастья в этом дворце",
    ("t_qumen_tayi_day", "is_noble"): "Флаг: благородное направление (OR)",
    ("t_qumen_tayi_day", "is_kong_wang"): "Флаг: пустота направления (OR)",
    ("t_qumen_tayi_day", "gate_score"): "Score врат (-1/0/1)",
    ("t_qumen_tayi_day", "star_score"): "Score звезды (-1/0/1)",
    ("t_qumen_tayi_day", "jianchu_score"): "Score 建除 (avg для 2-ветвевых)",
    ("t_qumen_tayi_day", "total_score"): "Итого: (gate*2+star*2+jianchu+xi_shen+noble)*(1-kong_wang)",
    ("t_rule_registry", "rule_id"): "MD5-хеш ID правила (PK)",
    ("t_rule_registry", "predicate_code"): "Код предиката правила",
    ("t_rule_registry", "description"): "Описание правила",
    ("t_rule_registry", "is_active"): "1=активное, 0=неактивное",
    ("t_rule_registry", "period_type"): "Уровень: year/month/day/hour",
}

# Group definitions
SPR_GROUPS = {
    "Базовые справочники БаЦзы": [
        "spr_heavenly_stem", "spr_earthly_branch", "spr_solar_term",
        "spr_jiazi_extended", "spr_pillar_cycle", "spr_pillar_hour_rule",
        "spr_pillar_month_rule", "spr_leader_stems", "spr_bazi_qi_phase"
    ],
    "Ци Мэнь Дунь Цзя": [
        "spr_qimen_templates", "spr_gates", "spr_gods", "spr_stars"
    ],
    "Тун Шу / Фэн Шуй": [
        "spr_tongshu_black_rabbit_rating", "spr_tongshu_black_rabbit_star",
        "spr_tongshu_branch_combo_rule", "spr_tongshu_guigu_outcome",
        "spr_tongshu_jiazi_profile", "spr_tongshu_phase",
        "spr_tongshu_phase_mapping", "spr_tongshu_shensha_rule",
        "spr_tongshu_stem_combo_rule", "spr_tongshu_ten_god",
        "spr_day_officer_mapping", "spr_master_dano_mapping",
        "spr_hour_stars", "spr_month_stars",
        "spr_yanqin_day_constellation", "spr_yellow_black_matrix",
        "spr_yellow_black_stars", "spr_black_rabbit_day_joey",
        "spr_black_rabbit_hour_joey", "spr_black_rabbit_matrix",
        "spr_black_rabbit_scores"
    ],
    "Тай И Шэнь Шу": [
        "spr_taiyi_gate_seq", "spr_taiyi_gates", "spr_taiyi_jianchu",
        "spr_taiyi_kong_wang", "spr_taiyi_noble", "spr_taiyi_palace_ring",
        "spr_taiyi_qing_long_start", "spr_taiyi_spirits",
        "spr_taiyi_star_start", "spr_taiyi_stars", "spr_taiyi_xi_shen"
    ],
    "Система анализа (Rule Engine)": [
        "spr_analysis_scope", "spr_indicator", "spr_indicator_scope",
        "spr_indicator_value", "spr_element_display"
    ],
    "СКДГ (Секретный Код Дракона)": [
        "spr_scdg", "spr_skdg_hexagram_pairs", "spr_skdg_wuxing_relation"
    ],
    "Сервисные": [
        "spr_table_comment", "spr_column_comment"
    ],
}

T_GROUPS = {
    "Базовые расчёты и сетка времени": [
        "t_time_grid_hourly", "t_bazi_hourly", "t_solar_term_time",
        "t_solar_term_time_hko", "t_flying_stars"
    ],
    "Результаты анализа (Rule Engine)": [
        "t_rule_registry", "t_rule_scope",
        "t_analysis_year", "t_analysis_month", "t_analysis_day",
        "t_analysis_hour", "t_analysis_date",
        "t_analysis_direction", "t_analysis_direction_year",
        "t_analysis_direction_month", "t_analysis_direction_day",
        "t_analysis_direction_hour"
    ],
    "Ци Мэнь Дунь Цзя": [
        "t_qumen_chauby_hourly", "t_qumen_dgiren_day",
        "t_qumen_dgiren_hourly", "t_qumen_dgiren_month",
        "t_qumen_dgiren_year", "t_qumen_tayi_day"
    ],
    "Тай И Шэнь Шу": [
        "t_taiyi_day", "t_taiyi_hours"
    ],
    "Тун Шу": [
        "t_tung_shu_daily"
    ],
    "CRM": [
        "t_crm_client", "t_crm_calculation", "t_crm_note", "t_crm_session"
    ],
    "Профили и карты рождения": [
        "t_profile", "t_profile_birth_chart", "t_profile_history"
    ],
    "Система и журналы": [
        "t_event", "t_sys_calculation_log"
    ],
    "Контрольные данные": [
        "t_control_t_bazi_hourly", "t_control_t_flying_stars",
        "t_control_t_qumen_chauby_hourly", "t_control_t_qumen_dgiren_day",
        "t_control_t_qumen_dgiren_hourly", "t_control_t_qumen_dgiren_month",
        "t_control_t_qumen_dgiren_year"
    ],
}

FK_LIST = [
    ("spr_tongshu_black_rabbit_star.cycle_index", "spr_tongshu_jiazi_profile.cycle_index"),
    ("t_crm_calculation.client_id", "t_crm_client.id"),
    ("t_crm_note.client_id", "t_crm_client.id"),
    ("t_crm_session.client_id", "t_crm_client.id"),
    ("t_profile_birth_chart.profile_id", "t_profile.id"),
    ("t_profile_history.profile_id", "t_profile.id"),
    ("t_solar_term_time.solar_term_id", "spr_solar_term.solar_term_id"),
    ("t_solar_term_time_hko.solar_term_id", "spr_solar_term.solar_term_id"),
]

TRIGGERS = [
    ("trg_profile_updated_at", "t_profile", "BEFORE UPDATE", "update_profile_updated_at",
     "Обновляет updated_at при изменении профиля"),
]

def main():
    out_path = "Metodology/postgresql_schema.md"
    lines = []
    
    # Header
    lines.append("# Схема PostgreSQL БД `calk_kmf`\n")
    lines.append("> **Автоматически сгенерировано:** 2026-05-31  ")
    lines.append("> **Всего таблиц:** 98  ")
    lines.append("> **Справочники (spr_\*):** ~60  ")
    lines.append("> **Таблицы данных (t_\*):** ~38  ")
    lines.append("")
    lines.append("## Правило поддержки")
    lines.append("")
    lines.append("При выполнении `ALTER TABLE` необходимо обновить **оба** файла:")
    lines.append("1. `data/ddl_full_schema_raw.sql` — перегенерировать через `pg_dump --schema-only`")
    lines.append("2. `Metodology/postgresql_schema.md` — обновить описание изменённых таблиц")
    lines.append("")
    
    # Table of contents
    lines.append("## Содержание")
    lines.append("")
    lines.append("- [Справочные таблицы (spr_*)](#справочные-таблицы-spr)")
    for group_name in SPR_GROUPS:
        anchor = group_name.lower().replace(' ', '-').replace('(', '').replace(')', '').replace('/', '')
        lines.append(f"  - [{group_name}](#{anchor})")
    lines.append("- [Таблицы данных (t_*)](#таблицы-данных-t)")
    for group_name in T_GROUPS:
        anchor = group_name.lower().replace(' ', '-').replace('(', '').replace(')', '').replace('/', '')
        lines.append(f"  - [{group_name}](#{anchor})")
    lines.append("- [Индексы](#индексы)")
    lines.append("- [Внешние ключи](#внешние-ключи)")
    lines.append("- [Триггеры и функции](#триггеры-и-функции)")
    lines.append("")
    
    # spr_* tables
    lines.append("---")
    lines.append("## Справочные таблицы (spr_*)\n")
    
    all_spr = set()
    for group_tables in SPR_GROUPS.values():
        all_spr.update(group_tables)
    
    for group_name, tables in SPR_GROUPS.items():
        anchor = group_name.lower().replace(' ', '-').replace('(', '').replace(')', '').replace('/', '')
        lines.append(f"### {group_name}\n")
        for tbl in tables:
            comment = table_comments.get(tbl, "")
            lines.append(f"#### `{tbl}`")
            if comment:
                lines.append(f"*{comment}*")
            lines.append("")
            lines.append("| Колонка | Тип | NULL | DEFAULT | Комментарий |")
            lines.append("|---------|-----|------|---------|-------------|")
            # We don't have full column details here without the DB, 
            # so we'll reference the raw schema dump for DDL.
            lines.append("| *см. DDL* | | | | |")
            lines.append("")
    
    # t_* tables
    lines.append("---")
    lines.append("## Таблицы данных (t_*)\n")
    
    for group_name, tables in T_GROUPS.items():
        anchor = group_name.lower().replace(' ', '-').replace('(', '').replace(')', '').replace('/', '')
        lines.append(f"### {group_name}\n")
        for tbl in tables:
            comment = table_comments.get(tbl, "")
            lines.append(f"#### `{tbl}`")
            if comment:
                lines.append(f"*{comment}*")
            lines.append("")
            lines.append("| Колонка | Тип | NULL | DEFAULT | Комментарий |")
            lines.append("|---------|-----|------|---------|-------------|")
            lines.append("| *см. DDL* | | | | |")
            lines.append("")
    
    # Indexes summary
    lines.append("---")
    lines.append("## Индексы\n")
    lines.append("Все индексы используют тип **btree**. Каждая таблица имеет первичный ключ (PK).")
    lines.append("Дополнительные индексы созданы для часто используемых столбцов.")
    lines.append("")
    lines.append("### Ключевые индексы")
    lines.append("")
    lines.append("| Таблица | Индекс | Тип | Столбцы |")
    lines.append("|---------|--------|-----|---------|")
    lines.append("| `t_bazi_hourly` | `idx_bazi_hourly_utc` | btree | tz_offset_hours, slot_start_date_utc, slot_start_time_utc |")
    lines.append("| `t_bazi_hourly` | `idx_bazi_hourly_local` | btree | tz_offset_hours, slot_start_date_local, slot_start_time_local |")
    lines.append("| `t_flying_stars` | `idx_fs_hour` | btree | hour_id |")
    lines.append("| `t_qumen_chauby_hourly` | `idx_qimen_cb_hr_hour` | btree | hour_id |")
    lines.append("| `t_qumen_dgiren_day` | `idx_qimen_d_date` | btree | year_pillar, month_pillar, day_pillar |")
    lines.append("| `t_qumen_dgiren_hourly` | `idx_qimen_hr_hour` | btree | hour_id |")
    lines.append("| `t_taiyi_hours` | `idx_taiyi_hours_date` | btree | date_val |")
    lines.append("| `t_profile` | `idx_profile_name` | btree | name |")
    lines.append("| `t_profile` | `idx_profile_birth_date` | btree | birth_date |")
    lines.append("| `t_profile_history` | `idx_profile_history_profile_id` | btree | profile_id |")
    lines.append("| `t_profile_history` | `idx_profile_history_created_at` | btree | created_at |")
    lines.append("")
    
    # Foreign keys
    lines.append("---")
    lines.append("## Внешние ключи\n")
    lines.append("| Таблица | Колонка | Ссылается на |")
    lines.append("|---------|---------|--------------|")
    for fk in FK_LIST:
        src, dst = fk
        lines.append(f"| `{src.split('.')[0]}` | `{src.split('.')[1]}` | `{dst}` |")
    lines.append("")
    
    # Triggers
    lines.append("---")
    lines.append("## Триггеры и функции\n")
    lines.append("| Триггер | Таблица | Тайминг | Функция | Назначение |")
    lines.append("|---------|---------|---------|---------|------------|")
    for t in TRIGGERS:
        lines.append(f"| `{t[0]}` | `{t[1]}` | {t[2]} | `{t[3]}` | {t[4]} |")
    lines.append("")
    
    # Sequences
    lines.append("---")
    lines.append("## Последовательности (Sequences)\n")
    lines.append("Используются для автоинкрементных ID в таблицах:")
    lines.append("- `spr_element_display_element_id_seq` → `spr_element_display.element_id`")
    lines.append("- `spr_scdg_id_seq` → `spr_scdg.id`")
    lines.append("- `t_crm_calculation_id_seq` → `t_crm_calculation.id`")
    lines.append("- `t_crm_client_id_seq` → `t_crm_client.id`")
    lines.append("- `t_crm_note_id_seq` → `t_crm_note.id`")
    lines.append("- `t_crm_session_id_seq` → `t_crm_session.id`")
    lines.append("- `t_profile_id_seq` → `t_profile.id`")
    lines.append("- `t_profile_birth_chart_id_seq` → `t_profile_birth_chart.id`")
    lines.append("- `t_profile_history_id_seq` → `t_profile_history.id`")
    lines.append("")
    
    # Views reference
    lines.append("---")
    lines.append("## Представления (Views)\n")
    lines.append("На момент генерации в схеме `public` **нет** представлений.")
    lines.append("Исторические views были задокументированы в `data/ddl_views.sql` (архив).")
    lines.append("")
    
    # Raw DDL reference
    lines.append("---")
    lines.append("## Полный DDL\n")
    lines.append("Полный DDL схемы доступен в:")
    lines.append("- `data/ddl_full_schema_raw.sql` — `pg_dump --schema-only --no-owner --no-privileges`")
    lines.append("- `data/ddl_comments.sql` — `COMMENT ON` для таблиц и колонок")
    lines.append("")
    
    # Footer
    lines.append("---")
    lines.append("*Конец документа*")
    
    content = "\n".join(lines)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Generated: {out_path}")
    print(f"Size: {len(content)} bytes")

if __name__ == "__main__":
    main()
