#!/usr/bin/env python3
"""Generate PostgreSQL schema documentation directly from the database."""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "calk_kmf")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASS
    )


def fetch_all(conn, sql):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql)
        return cur.fetchall()


def escape_md(text):
    if text is None:
        return ""
    return str(text).replace("|", "\\|").replace("\n", " ")


def main():
    conn = get_connection()
    
    # Get all tables
    tables = fetch_all(conn, """
        SELECT table_name, table_type
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    
    # Get columns
    columns = fetch_all(conn, """
        SELECT table_name, column_name, data_type, is_nullable,
               column_default, character_maximum_length,
               numeric_precision, numeric_scale
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position
    """)
    
    # Get indexes
    indexes = fetch_all(conn, """
        SELECT t.relname AS table_name, i.relname AS index_name,
               am.amname AS index_type, ix.indisunique AS is_unique,
               ix.indisprimary AS is_primary,
               array_agg(a.attname ORDER BY array_position(ix.indkey, a.attnum))
                   FILTER (WHERE a.attnum > 0) AS columns
        FROM pg_index ix
        JOIN pg_class t ON t.oid = ix.indrelid
        JOIN pg_class i ON i.oid = ix.indexrelid
        JOIN pg_am am ON am.oid = i.relam
        JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
        JOIN pg_namespace n ON n.oid = t.relnamespace
        WHERE n.nspname = 'public' AND t.relkind = 'r'
        GROUP BY t.relname, i.relname, am.amname, ix.indisunique, ix.indisprimary
        ORDER BY t.relname, i.relname
    """)
    
    # Get FKs
    fks = fetch_all(conn, """
        SELECT tc.constraint_name, tc.table_name,
               kcu.column_name, ccu.table_name AS foreign_table_name,
               ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema = 'public'
        ORDER BY tc.table_name, tc.constraint_name
    """)
    
    # Get table comments
    tbl_comments = fetch_all(conn, """
        SELECT c.relname AS table_name, d.description AS comment
        FROM pg_description d
        JOIN pg_class c ON c.oid = d.objoid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND d.objsubid = 0 AND c.relkind = 'r'
        ORDER BY c.relname
    """)
    
    # Get column comments
    col_comments = fetch_all(conn, """
        SELECT c.relname AS table_name, a.attname AS column_name,
               d.description AS comment
        FROM pg_description d
        JOIN pg_class c ON c.oid = d.objoid
        JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum = d.objsubid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND d.objsubid > 0
        ORDER BY c.relname, a.attnum
    """)
    
    # Build lookup dicts
    cols_by_table = {}
    for c in columns:
        cols_by_table.setdefault(c["table_name"], []).append(c)
    
    idx_by_table = {}
    for ix in indexes:
        idx_by_table.setdefault(ix["table_name"], []).append(ix)
    
    fk_by_table = {}
    for fk in fks:
        fk_by_table.setdefault(fk["table_name"], []).append(fk)
    
    tbl_comment_map = {r["table_name"]: r["comment"] for r in tbl_comments}
    col_comment_map = {}
    for r in col_comments:
        col_comment_map[(r["table_name"], r["column_name"])] = r["comment"]
    
    # Group definitions
    spr_groups = {
        "Базовые справочники БаЦзы": [
            "spr_heavenly_stem", "spr_earthly_branch", "spr_solar_term",
            "spr_jiazi_extended", "spr_pillar_cycle", "spr_pillar_hour_rule",
            "spr_pillar_month_rule", "spr_leader_stems", "spr_bazi_qi_phase"
        ],
        "Ци Мэнь Дунь Цзя": [
            "spr_qimen_templates", "spr_gates", "spr_gods", "spr_stars"
        ],
        "Тун Шу / Фэн Шуй": [
            "spr_flying_star_map",
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
    
    t_groups = {
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
    
    def format_type(c):
        dt = c["data_type"]
        if c["character_maximum_length"]:
            return f"{dt}({c['character_maximum_length']})"
        if c["numeric_precision"] and c["numeric_scale"]:
            return f"{dt}({c['numeric_precision']},{c['numeric_scale']})"
        return dt
    
    def write_table_section(lines, tbl_name):
        comment = tbl_comment_map.get(tbl_name, "")
        lines.append(f"#### `{tbl_name}`")
        if comment:
            lines.append(f"*{escape_md(comment)}*")
        lines.append("")
        
        # Columns
        tbl_cols = cols_by_table.get(tbl_name, [])
        if tbl_cols:
            lines.append("| Колонка | Тип | NULL | DEFAULT | Комментарий |")
            lines.append("|---------|-----|------|---------|-------------|")
            for c in tbl_cols:
                col_name = c["column_name"]
                col_type = format_type(c)
                nullable = c["is_nullable"]
                default = escape_md(c["column_default"]) if c["column_default"] else ""
                cmt = escape_md(col_comment_map.get((tbl_name, col_name), ""))
                lines.append(f"| `{col_name}` | {col_type} | {nullable} | {default} | {cmt} |")
            lines.append("")
        
        # Indexes
        tbl_idx = idx_by_table.get(tbl_name, [])
        if tbl_idx:
            lines.append("**Индексы:**")
            for ix in tbl_idx:
                uniq = "UNIQUE " if ix["is_unique"] else ""
                pk = "PK " if ix["is_primary"] else ""
                cols = ", ".join(ix["columns"])
                lines.append(f"- `{ix['index_name']}` — {uniq}{pk}({cols})")
            lines.append("")
        
        # FKs
        tbl_fks = fk_by_table.get(tbl_name, [])
        if tbl_fks:
            lines.append("**Внешние ключи:**")
            for fk in tbl_fks:
                lines.append(f"- `{fk['column_name']}` → `{fk['foreign_table_name']}.{fk['foreign_column_name']}`")
            lines.append("")
    
    lines = []
    lines.append("# Схема PostgreSQL БД `calk_kmf`\n")
    lines.append("> **Автоматически сгенерировано:** 2026-05-31  ")
    lines.append("> **Всего таблиц:** 98  ")
    lines.append("> **Справочники (spr_\\*):** ~60  ")
    lines.append("> **Таблицы данных (t_\\*):** ~38  ")
    lines.append("")
    lines.append("## Правило поддержки")
    lines.append("")
    lines.append("При выполнении `ALTER TABLE` необходимо обновить **оба** файла:")
    lines.append("1. `data/ddl_full_schema_raw.sql` — перегенерировать через `pg_dump --schema-only`")
    lines.append("2. `Metodology/postgresql_schema.md` — обновить описание изменённых таблиц")
    lines.append("")
    
    # TOC
    lines.append("## Содержание")
    lines.append("")
    lines.append("- [Справочные таблицы (spr_*)](#справочные-таблицы-spr)")
    for g in spr_groups:
        anchor = g.lower().replace(' ', '-').replace('(', '').replace(')', '').replace('/', '')
        lines.append(f"  - [{g}](#{anchor})")
    lines.append("- [Таблицы данных (t_*)](#таблицы-данных-t)")
    for g in t_groups:
        anchor = g.lower().replace(' ', '-').replace('(', '').replace(')', '').replace('/', '')
        lines.append(f"  - [{g}](#{anchor})")
    lines.append("- [Индексы](#индексы)")
    lines.append("- [Внешние ключи](#внешние-ключи)")
    lines.append("- [Триггеры и функции](#триггеры-и-функции)")
    lines.append("")
    
    # spr_* tables
    lines.append("---")
    lines.append("## Справочные таблицы (spr_*)\n")
    
    for group_name, tables in spr_groups.items():
        lines.append(f"### {group_name}\n")
        for tbl in tables:
            write_table_section(lines, tbl)
    
    # t_* tables
    lines.append("---")
    lines.append("## Таблицы данных (t_*)\n")
    
    for group_name, tables in t_groups.items():
        lines.append(f"### {group_name}\n")
        for tbl in tables:
            write_table_section(lines, tbl)
    
    # Indexes summary
    lines.append("---")
    lines.append("## Индексы\n")
    lines.append("Все индексы используют тип **btree**. Каждая таблица имеет первичный ключ (PK).")
    lines.append("Дополнительные индексы созданы для часто используемых столбцов.")
    lines.append("")
    lines.append("| Таблица | Индекс | Тип | Столбцы |")
    lines.append("|---------|--------|-----|---------|")
    for ix in indexes:
        if not ix["is_primary"]:
            cols = ", ".join(ix["columns"])
            lines.append(f"| `{ix['table_name']}` | `{ix['index_name']}` | {ix['index_type']} | {cols} |")
    lines.append("")
    
    # Foreign keys
    lines.append("---")
    lines.append("## Внешние ключи\n")
    lines.append("| Таблица | Колонка | Ссылается на |")
    lines.append("|---------|---------|--------------|")
    for fk in fks:
        lines.append(f"| `{fk['table_name']}` | `{fk['column_name']}` | `{fk['foreign_table_name']}.{fk['foreign_column_name']}` |")
    lines.append("")
    
    # Triggers
    lines.append("---")
    lines.append("## Триггеры и функции\n")
    triggers = fetch_all(conn, """
        SELECT tg.tgname AS trigger_name, c.relname AS table_name,
               p.proname AS function_name,
               CASE tg.tgtype & 2 WHEN 2 THEN 'BEFORE' ELSE 'AFTER' END AS timing,
               CASE WHEN tg.tgtype & 4 = 4 THEN 'INSERT'
                    WHEN tg.tgtype & 8 = 8 THEN 'DELETE'
                    WHEN tg.tgtype & 16 = 16 THEN 'UPDATE'
                    ELSE 'OTHER' END AS event
        FROM pg_trigger tg
        JOIN pg_class c ON c.oid = tg.tgrelid
        JOIN pg_proc p ON p.oid = tg.tgfoid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND NOT tg.tgisinternal
        ORDER BY c.relname, tg.tgname
    """)
    lines.append("| Триггер | Таблица | Тайминг | Событие | Функция |")
    lines.append("|---------|---------|---------|---------|---------|")
    for t in triggers:
        lines.append(f"| `{t['trigger_name']}` | `{t['table_name']}` | {t['timing']} | {t['event']} | `{t['function_name']}` |")
    lines.append("")
    
    # Views
    lines.append("---")
    lines.append("## Представления (Views)\n")
    views = fetch_all(conn, """
        SELECT schemaname, viewname FROM pg_views
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
        ORDER BY schemaname, viewname
    """)
    if views:
        lines.append("| Схема | Имя |")
        lines.append("|-------|-----|")
        for v in views:
            lines.append(f"| `{v['schemaname']}` | `{v['viewname']}` |")
    else:
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
    
    lines.append("---")
    lines.append("*Конец документа*")
    
    out_path = "Metodology/postgresql_schema.md"
    content = "\n".join(lines)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Generated: {out_path}")
    print(f"Size: {len(content)} bytes")


if __name__ == "__main__":
    main()
