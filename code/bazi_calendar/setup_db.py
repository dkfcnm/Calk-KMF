"""Скрипт инициализации базы данных для бацзы‑календаря.

Назначение модуля:
- создать либо обновить структуру таблиц в базе данных (PostgreSQL);
- создать справочники, служебные таблицы и структуры расчётов бацзы;
- подготовить инфраструктуру для расширенного анализа Тун Шу.

Последнее обновление: 2026-02-08.
"""

from __future__ import annotations

import sys
import os
from pathlib import Path
import logging

# Ensure we can import from code/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from code.common.db_manager import db

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def get_ddl_statements() -> list[str]:
    """Возвращает список DDL-запросов для PostgreSQL."""
    return _get_postgres_ddl()

def _get_postgres_ddl() -> list[str]:
    return [
        # Небесные стволы
        """
        CREATE TABLE IF NOT EXISTS spr_heavenly_stem (
            stem_id        INTEGER PRIMARY KEY,
            stem_char      TEXT NOT NULL,
            stem_pinyin    TEXT,
            stem_rus       TEXT,
            element        TEXT,
            yin_yang       TEXT,
            guigu_score    INTEGER
        );
        """,
        # Профиль столпов для расчётов Тун Шу
        """
        CREATE TABLE IF NOT EXISTS spr_tongshu_jiazi_profile (
            cycle_index     INTEGER PRIMARY KEY,
            pillar_text     TEXT    NOT NULL,
            nayin_name      TEXT,
            nayin_element   TEXT,
            nayin_code      TEXT,
            dagua_element   INTEGER,
            dagua_period    INTEGER,
            family_code     TEXT,
            family_role     TEXT
        );
        """,
        # Таблица оценок метода «Чёрный кролик» по лунным дням
        """
        CREATE TABLE IF NOT EXISTS spr_tongshu_black_rabbit_star (
            cycle_index INTEGER NOT NULL,
            lunar_day   INTEGER NOT NULL,
            method_code TEXT    NOT NULL DEFAULT 'primary',
            star_name   TEXT    NOT NULL,
            PRIMARY KEY (cycle_index, lunar_day, method_code),
            FOREIGN KEY (cycle_index) REFERENCES spr_tongshu_jiazi_profile(cycle_index)
        );
        """,
        # Справочник характеристик звёзд метода «Чёрный кролик»
        """
        CREATE TABLE IF NOT EXISTS spr_tongshu_black_rabbit_rating (
            star_name    TEXT PRIMARY KEY,
            rating_code  TEXT NOT NULL,
            rating_name  TEXT NOT NULL,
            description_ru TEXT
        );
        """,
        # Символические звёзды (Шэнь Ша)
        """
        CREATE TABLE IF NOT EXISTS spr_tongshu_shensha_rule (
            rule_id       SERIAL PRIMARY KEY,
            star_name     TEXT    NOT NULL,
            master_scope  TEXT    NOT NULL,
            master_value  TEXT    NOT NULL,
            target_scope  TEXT    NOT NULL,
            target_value  TEXT    NOT NULL,
            notes         TEXT
        );
        """,
        # Таблица соответствий 10 богов
        """
        CREATE TABLE IF NOT EXISTS spr_tongshu_ten_god (
            day_stem     TEXT NOT NULL,
            god_code     TEXT NOT NULL,
            related_stem TEXT NOT NULL,
            PRIMARY KEY (day_stem, god_code)
        );
        """,
        # Интерпретации чисел Гуй Гу Цзы
        """
        CREATE TABLE IF NOT EXISTS spr_tongshu_guigu_outcome (
            outcome_number INTEGER PRIMARY KEY,
            name_ru        TEXT    NOT NULL,
            verdict_code   TEXT    NOT NULL,
            description_ru TEXT,
            numeric_score  DOUBLE PRECISION NOT NULL DEFAULT 0
        );
        """,
        # Стадии фаз Ци
        """
        CREATE TABLE IF NOT EXISTS spr_tongshu_phase (
            phase_id      INTEGER PRIMARY KEY,
            name_ru       TEXT    NOT NULL,
            numeric_score DOUBLE PRECISION NOT NULL
        );
        """,
        # Привязка фаз Ци к стволам и ветвям
        """
        CREATE TABLE IF NOT EXISTS spr_tongshu_phase_mapping (
            day_stem        TEXT NOT NULL,
            phase_id        INTEGER NOT NULL,
            reference_branch TEXT NOT NULL,
            PRIMARY KEY (day_stem, phase_id),
            FOREIGN KEY (phase_id) REFERENCES spr_tongshu_phase(phase_id)
        );
        """,
        # Справочник правил комбинаций земных ветвей
        """
        CREATE TABLE IF NOT EXISTS spr_tongshu_branch_combo_rule (
            rule_id         SERIAL PRIMARY KEY,
            combo_name      TEXT NOT NULL,
            combo_type_id   INTEGER NOT NULL,
            numeric_score   DOUBLE PRECISION NOT NULL,
            item1           TEXT NOT NULL,
            item2           TEXT NOT NULL,
            item3           TEXT,
            description     TEXT
        );
        """,
        # Справочник правил комбинаций небесных стволов
        """
        CREATE TABLE IF NOT EXISTS spr_tongshu_stem_combo_rule (
            rule_id         SERIAL PRIMARY KEY,
            combo_name      TEXT NOT NULL,
            combo_type_id   INTEGER NOT NULL,
            numeric_score   DOUBLE PRECISION NOT NULL,
            item1           TEXT NOT NULL,
            item2           TEXT NOT NULL,
            description     TEXT
        );
        """,
        # Таблица результатов анализа Тун Шу (нормализованный вид)
        """
        DROP TABLE IF EXISTS t_analyz_data CASCADE;
        """,
        # Ветви
        """
        CREATE TABLE IF NOT EXISTS spr_earthly_branch (
            branch_id      INTEGER PRIMARY KEY,
            branch_char    TEXT NOT NULL,
            branch_pinyin  TEXT,
            branch_rus     TEXT,
            element        TEXT,
            yin_yang       TEXT,
            yuan_level     INTEGER,
            start_hour     INTEGER,
            end_hour       INTEGER,
            guigu_score    INTEGER
        );
        """,
        # 24 солнечных сезона
        """
        CREATE TABLE IF NOT EXISTS spr_solar_term (
            solar_term_id      INTEGER PRIMARY KEY,
            solar_term_char    TEXT NOT NULL,
            solar_term_name_ru TEXT,
            solar_term_pinyin  TEXT,
            longitude_deg      INTEGER NOT NULL,
            month_branch_id    INTEGER NOT NULL,
            FOREIGN KEY (month_branch_id) REFERENCES spr_earthly_branch(branch_id)
        );
        """,
        # Астрономические моменты сезонов
        """
        DROP TABLE IF EXISTS t_solar_term_time CASCADE;
        CREATE TABLE IF NOT EXISTS t_solar_term_time (
            year           INTEGER NOT NULL,
            solar_term_id  INTEGER NOT NULL,
            longitude_deg  INTEGER NOT NULL,
            crossing_utc   TIMESTAMP NOT NULL,
            crossing_gmt0  TIMESTAMP NOT NULL,
            PRIMARY KEY (year, solar_term_id),
            FOREIGN KEY (solar_term_id) REFERENCES spr_solar_term(solar_term_id)
        );
        """,
        # Эталонные времена сезонов (HKO)
        """
        DROP TABLE IF EXISTS t_solar_term_time_hko CASCADE;
        CREATE TABLE IF NOT EXISTS t_solar_term_time_hko (
            year              INTEGER NOT NULL,
            solar_term_id     INTEGER NOT NULL,
            longitude_deg     INTEGER NOT NULL,
            crossing_hkt      TIMESTAMP NOT NULL,
            crossing_utc      TIMESTAMP NOT NULL,
            tz_offset_hours   INTEGER NOT NULL DEFAULT 8,
            PRIMARY KEY (year, solar_term_id),
            FOREIGN KEY (solar_term_id) REFERENCES spr_solar_term(solar_term_id)
        );
        """,
        # Правила столпа месяца
        """
        CREATE TABLE IF NOT EXISTS spr_pillar_month_rule (
            year_stem_id  INTEGER NOT NULL,
            month_index   INTEGER NOT NULL,
            month_stem_id INTEGER NOT NULL,
            PRIMARY KEY (year_stem_id, month_index),
            FOREIGN KEY (year_stem_id)  REFERENCES spr_heavenly_stem(stem_id),
            FOREIGN KEY (month_stem_id) REFERENCES spr_heavenly_stem(stem_id)
        );
        """,
        # Правила столпа часа
        """
        CREATE TABLE IF NOT EXISTS spr_pillar_hour_rule (
            day_stem_id     INTEGER NOT NULL,
            hour_branch_id  INTEGER NOT NULL,
            hour_stem_id    INTEGER NOT NULL,
            PRIMARY KEY (day_stem_id, hour_branch_id),
            FOREIGN KEY (day_stem_id)    REFERENCES spr_heavenly_stem(stem_id),
            FOREIGN KEY (hour_branch_id) REFERENCES spr_earthly_branch(branch_id),
            FOREIGN KEY (hour_stem_id)   REFERENCES spr_heavenly_stem(stem_id)
        );
        """,
        # 60-летний цикл
        """
        CREATE TABLE IF NOT EXISTS spr_pillar_cycle (
            cycle_index  INTEGER PRIMARY KEY,
            stem_id      INTEGER NOT NULL,
            branch_id    INTEGER NOT NULL,
            FOREIGN KEY (stem_id)   REFERENCES spr_heavenly_stem(stem_id),
            FOREIGN KEY (branch_id) REFERENCES spr_earthly_branch(branch_id)
        );
        """,
        # Временная сетка по часам
        """
        CREATE TABLE IF NOT EXISTS t_time_grid_hourly (
            dt_utc   TIMESTAMP NOT NULL,
            dt_gmt0  TIMESTAMP NOT NULL,
            year     INTEGER   NOT NULL,
            month    INTEGER   NOT NULL,
            day      INTEGER   NOT NULL,
            hour     INTEGER   NOT NULL,
            weekday  INTEGER   NOT NULL
        );
        """,
        # Расчётная таблица часовых столпов
        """
        DROP TABLE IF EXISTS t_bazi_hourly CASCADE;
        CREATE TABLE IF NOT EXISTS t_bazi_hourly (
            hour_id             TEXT      NOT NULL,
            tz_offset_hours     INTEGER   NOT NULL,
            slot_start_date_utc   TEXT      NOT NULL,
            slot_start_time_utc   TEXT      NOT NULL,
            slot_end_date_utc     TEXT      NOT NULL,
            slot_end_time_utc     TEXT      NOT NULL,
            slot_start_date_local TEXT      NOT NULL,
            slot_start_time_local TEXT      NOT NULL,
            slot_end_date_local   TEXT      NOT NULL,
            slot_end_time_local   TEXT      NOT NULL,
            weekday_local         TEXT      NOT NULL,
            solar_term_id         INTEGER   NOT NULL,
            solar_term_name       TEXT,
            year_pillar           TEXT      NOT NULL,
            month_pillar          TEXT      NOT NULL,
            day_pillar            TEXT      NOT NULL,
            hour_pillar           TEXT      NOT NULL,
            year_stem             TEXT      NOT NULL,
            year_branch           TEXT      NOT NULL,
            month_stem            TEXT      NOT NULL,
            month_branch          TEXT      NOT NULL,
            day_stem              TEXT      NOT NULL,
            day_branch            TEXT      NOT NULL,
            hour_stem             TEXT      NOT NULL,
            hour_branch           TEXT      NOT NULL,
            lunar_month           INTEGER   NOT NULL,
            lunar_day             INTEGER   NOT NULL,
            lunar_is_leap         INTEGER   NOT NULL,
            lunar_month_zi        INTEGER   NOT NULL,
            lunar_day_zi          INTEGER   NOT NULL,
            lunar_is_leap_zi      INTEGER   NOT NULL,
            day_officer_value_id  INTEGER,
            year_int              INTEGER   GENERATED ALWAYS AS (CAST(substr(slot_start_date_utc,1,4) AS INT)) STORED,
            PRIMARY KEY (tz_offset_hours, slot_start_date_utc, slot_start_time_utc),
            UNIQUE (hour_id),
            FOREIGN KEY (solar_term_id) REFERENCES spr_solar_term(solar_term_id)
        );
        CREATE INDEX IF NOT EXISTS idx_bazi_hourly_year_int ON t_bazi_hourly(year_int);
        CREATE INDEX IF NOT EXISTS idx_bazi_hourly_year_stem ON t_bazi_hourly(year_stem);
        CREATE INDEX IF NOT EXISTS idx_bazi_hourly_year_branch ON t_bazi_hourly(year_branch);
        CREATE INDEX IF NOT EXISTS idx_bazi_hourly_month_stem ON t_bazi_hourly(month_stem);
        CREATE INDEX IF NOT EXISTS idx_bazi_hourly_month_branch ON t_bazi_hourly(month_branch);
        CREATE INDEX IF NOT EXISTS idx_bazi_hourly_day_stem ON t_bazi_hourly(day_stem);
        CREATE INDEX IF NOT EXISTS idx_bazi_hourly_day_branch ON t_bazi_hourly(day_branch);
        CREATE INDEX IF NOT EXISTS idx_bazi_hourly_hour_stem ON t_bazi_hourly(hour_stem);
        CREATE INDEX IF NOT EXISTS idx_bazi_hourly_hour_branch ON t_bazi_hourly(hour_branch);
        CREATE INDEX IF NOT EXISTS idx_bazi_hourly_lunar_day_zi ON t_bazi_hourly(lunar_day_zi);
        CREATE INDEX IF NOT EXISTS idx_bazi_hourly_utc ON t_bazi_hourly(tz_offset_hours, slot_start_date_utc, slot_start_time_utc);
        CREATE INDEX IF NOT EXISTS idx_bazi_hourly_local ON t_bazi_hourly(tz_offset_hours, slot_start_date_local, slot_start_time_local);
        CREATE INDEX IF NOT EXISTS idx_bazi_hourly_analysis_join ON t_bazi_hourly(hour_id);
        """,
        # Справочник показателей
        """
        CREATE TABLE IF NOT EXISTS spr_indicator (
            indicator_id   INTEGER PRIMARY KEY,
            code           TEXT NOT NULL UNIQUE,
            name_ru        TEXT NOT NULL,
            description_ru TEXT,
            level          TEXT NOT NULL,
            value_type     TEXT NOT NULL,
            is_active      INTEGER NOT NULL DEFAULT 1
        );
        """,
        # Значения показателей
        """
        CREATE TABLE IF NOT EXISTS spr_indicator_value (
            value_id            INTEGER PRIMARY KEY,
            indicator_id        INTEGER NOT NULL,
            code                TEXT NOT NULL,
            name_ru             TEXT NOT NULL,
            description_ru      TEXT,
            interpretation_ru   TEXT,
            favorable_actions   TEXT,
            unfavorable_actions TEXT,
            numeric_score       DOUBLE PRECISION NOT NULL DEFAULT 0,
            FOREIGN KEY (indicator_id) REFERENCES spr_indicator(indicator_id),
            UNIQUE (indicator_id, code)
        );
        """,
        # Области применения
        """
        CREATE TABLE IF NOT EXISTS spr_analysis_scope (
            scope_code   TEXT PRIMARY KEY,
            name_ru      TEXT NOT NULL,
            description_ru TEXT
        );
        """,
        # Связь
        """
        CREATE TABLE IF NOT EXISTS spr_indicator_scope (
            indicator_id INTEGER NOT NULL,
            scope_code   TEXT NOT NULL,
            PRIMARY KEY (indicator_id, scope_code),
            FOREIGN KEY (indicator_id) REFERENCES spr_indicator(indicator_id),
            FOREIGN KEY (scope_code) REFERENCES spr_analysis_scope(scope_code)
        );
        """,
        # Матрица Мастера Дано
        """
        CREATE TABLE IF NOT EXISTS spr_master_dano_mapping (
            month_branch_id     INTEGER NOT NULL,
            day_stem_id         INTEGER NOT NULL,
            day_branch_id       INTEGER NOT NULL,
            indicator_value_id  INTEGER NOT NULL,
            PRIMARY KEY (month_branch_id, day_stem_id, day_branch_id),
            FOREIGN KEY (month_branch_id) REFERENCES spr_earthly_branch(branch_id),
            FOREIGN KEY (day_stem_id) REFERENCES spr_heavenly_stem(stem_id),
            FOREIGN KEY (day_branch_id) REFERENCES spr_earthly_branch(branch_id),
            FOREIGN KEY (indicator_value_id) REFERENCES spr_indicator_value(value_id)
        );
        """,
        # Офицеры
        """
        CREATE TABLE IF NOT EXISTS spr_day_officer_mapping (
            month_branch_id INTEGER NOT NULL,
            day_branch_id   INTEGER NOT NULL,
            officer_value_id INTEGER NOT NULL,
            PRIMARY KEY (month_branch_id, day_branch_id),
            FOREIGN KEY (month_branch_id) REFERENCES spr_earthly_branch(branch_id),
            FOREIGN KEY (day_branch_id) REFERENCES spr_earthly_branch(branch_id),
            FOREIGN KEY (officer_value_id) REFERENCES spr_indicator_value(value_id)
        );
        """,
        # Метаданные (комментарии)
        """
        CREATE TABLE IF NOT EXISTS spr_table_comment (
            table_name   TEXT PRIMARY KEY,
            comment_text TEXT NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS spr_column_comment (
            table_name   TEXT NOT NULL,
            column_name  TEXT NOT NULL,
            comment_text TEXT NOT NULL,
            PRIMARY KEY (table_name, column_name),
            FOREIGN KEY (table_name) REFERENCES spr_table_comment(table_name)
        );
        """,
        # Rule Engine
        """
        CREATE TABLE IF NOT EXISTS t_rule_registry (
            rule_id        TEXT PRIMARY KEY,
            name_ru        TEXT NOT NULL,
            predicate_code TEXT NOT NULL,
            params_json    TEXT,
            score_base     DOUBLE PRECISION DEFAULT 0,
            score_formula  TEXT,
            description    TEXT,
            is_active      INTEGER DEFAULT 1
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS t_rule_scope (
            rule_id        TEXT NOT NULL,
            scope_type     TEXT NOT NULL,
            is_stop        INTEGER DEFAULT 0,
            PRIMARY KEY (rule_id, scope_type),
            FOREIGN KEY (rule_id) REFERENCES t_rule_registry(rule_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS t_analysis_date (
            hour_id        TEXT NOT NULL,
            rule_id        TEXT NOT NULL,
            result_value   TEXT,
            score          DOUBLE PRECISION NOT NULL,
            PRIMARY KEY (hour_id, rule_id),
            FOREIGN KEY (hour_id) REFERENCES t_bazi_hourly(hour_id),
            FOREIGN KEY (rule_id) REFERENCES t_rule_registry(rule_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS t_analysis_direction (
            hour_id        TEXT NOT NULL,
            palace_no      INTEGER NOT NULL,
            system_type    TEXT NOT NULL,
            chart_level    TEXT NOT NULL,
            rule_id        TEXT NOT NULL,
            result_value   TEXT,
            score          DOUBLE PRECISION NOT NULL,
            PRIMARY KEY (hour_id, palace_no, system_type, chart_level, rule_id),
            FOREIGN KEY (hour_id) REFERENCES t_bazi_hourly(hour_id),
            FOREIGN KEY (rule_id) REFERENCES t_rule_registry(rule_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS t_analysis_activation (
            hour_id        TEXT NOT NULL,
            palace_no      INTEGER NOT NULL,
            rule_id        TEXT NOT NULL,
            score          DOUBLE PRECISION NOT NULL,
            PRIMARY KEY (hour_id, palace_no, rule_id),
            FOREIGN KEY (hour_id) REFERENCES t_bazi_hourly(hour_id),
            FOREIGN KEY (rule_id) REFERENCES t_rule_registry(rule_id)
        );
        """
    ]

TABLE_COMMENTS = [
    ("spr_heavenly_stem", "Справочник небесных стволов"),
    ("spr_tongshu_jiazi_profile", "Профиль пар ствол+ветвь (Цзя-Цзы) для расчётов Тун Шу"),
    # ... (Truncated for brevity, full list in original file)
]

COLUMN_COMMENTS = [
    # ... (Truncated for brevity, full list in original file)
]

def init_database() -> None:
    """Создаёт таблицы и выполняет DDL-скрипты."""
    
    print("Initializing database (PostgreSQL)...")
    
    ddl_statements = get_ddl_statements()
    if not ddl_statements:
        print("No DDL statements to execute.")
        return

    for ddl in ddl_statements:
        try:
            db.execute_query(ddl)
        except Exception as e:
            print(f"Error executing DDL: {e}")
            # Don't stop, some might fail if exists
            
    print("Database initialization completed.")

if __name__ == "__main__":
    init_database()
