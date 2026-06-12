#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Populate Qi Men tables in PostgreSQL from SQLite source.
- Alters spr_stars, spr_gates, spr_gods with new columns
- Populates reference tables (stars, gates, gods, stem_combos, trigrams)
- Creates missing t_qumen_chauby_day/month/year and populates them
- Migrates large chart tables (t_qumen_dgiren_* and t_qumen_chauby_hourly) via COPY.
"""
import os
import sys
import sqlite3
import csv
import subprocess

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from code.common.db_manager import db
from code.common.db_config import PG_CONFIG, PG_BIN_PATH

SQLITE_PATH = os.path.join(PROJECT_ROOT, "calk_kmf.sqlite")


def sqlite_conn():
    return sqlite3.connect(SQLITE_PATH)


def column_exists(table: str, column: str) -> bool:
    rows = db.fetch_all(
        "SELECT 1 FROM information_schema.columns WHERE table_name = %s AND column_name = %s",
        [table, column]
    )
    return bool(rows)


def add_column(table: str, column: str, dtype: str):
    if not column_exists(table, column):
        db.execute_query(f"ALTER TABLE {table} ADD COLUMN {column} {dtype}")
        print(f"  + Added {table}.{column} {dtype}")
    else:
        print(f"  = {table}.{column} already exists")


def alter_tables():
    print("Altering spr_stars...")
    for col, dtype in [
        ("star_char", "TEXT"),
        ("star_pinyin", "TEXT"),
        ("element", "TEXT"),
        ("nature", "TEXT"),
        ("description_ru", "TEXT"),
        ("palace_orig", "INTEGER"),
    ]:
        add_column("spr_stars", col, dtype)

    print("Altering spr_gates...")
    for col, dtype in [
        ("gate_char", "TEXT"),
        ("gate_pinyin", "TEXT"),
        ("element", "TEXT"),
        ("nature", "TEXT"),
        ("description_ru", "TEXT"),
        ("palace_orig", "INTEGER"),
    ]:
        add_column("spr_gates", col, dtype)

    print("Altering spr_gods...")
    for col, dtype in [
        ("spirit_char", "TEXT"),
        ("spirit_pinyin", "TEXT"),
        ("element", "TEXT"),
        ("nature", "TEXT"),
        ("description_ru", "TEXT"),
    ]:
        add_column("spr_gods", col, dtype)


def populate_stars():
    print("Populating spr_stars...")
    conn = sqlite_conn()
    c = conn.cursor()
    c.execute("""
        SELECT star_id, star_char, star_name_ru, star_name_en, star_name_zh,
               palace_orig, element, nature, description_ru
        FROM spr_qimen_stars ORDER BY star_id
    """)
    rows = c.fetchall()
    conn.close()

    db.execute_query("DELETE FROM spr_stars")
    sql = """
        INSERT INTO spr_stars (id, name_en, name_ru, star_char, star_pinyin,
                               element, nature, description_ru, palace_orig)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = []
    for r in rows:
        star_id, star_char, star_name_ru, star_name_en, star_name_zh, palace_orig, element, nature, description_ru = r
        params.append([
            star_id, star_name_en, star_name_ru, star_char, star_name_zh,
            element, nature, description_ru, palace_orig
        ])
    db.execute_batch(sql, params)
    print(f"  -> Inserted {len(params)} stars")


def populate_gates():
    print("Populating spr_gates...")
    conn = sqlite_conn()
    c = conn.cursor()
    c.execute("""
        SELECT gate_id, gate_char, gate_name_ru, gate_name_en, gate_name_zh,
               palace_orig, element, nature, description_ru
        FROM spr_qimen_gates ORDER BY gate_id
    """)
    rows = c.fetchall()
    conn.close()

    db.execute_query("DELETE FROM spr_gates")
    sql = """
        INSERT INTO spr_gates (id, name_en, name_ru, gate_char, gate_pinyin,
                               element, nature, description_ru, palace_orig)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = []
    for r in rows:
        gate_id, gate_char, gate_name_ru, gate_name_en, gate_name_zh, palace_orig, element, nature, description_ru = r
        params.append([
            gate_id, gate_name_en, gate_name_ru, gate_char, gate_name_zh,
            element, nature, description_ru, palace_orig
        ])
    db.execute_batch(sql, params)
    print(f"  -> Inserted {len(params)} gates")


def populate_gods():
    print("Populating spr_gods...")
    conn = sqlite_conn()
    c = conn.cursor()
    c.execute("""
        SELECT spirit_id, spirit_char, spirit_name_ru, spirit_name_en, spirit_name_zh,
               element, nature, description_ru
        FROM spr_qimen_spirits ORDER BY spirit_id
    """)
    rows = c.fetchall()
    conn.close()

    db.execute_query("DELETE FROM spr_gods")
    sql = """
        INSERT INTO spr_gods (id, name_en, name_ru, spirit_char, spirit_pinyin,
                              element, nature, description_ru)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = []
    for r in rows:
        spirit_id, spirit_char, spirit_name_ru, spirit_name_en, spirit_name_zh, element, nature, description_ru = r
        params.append([
            spirit_id, spirit_name_en, spirit_name_ru, spirit_char, spirit_name_zh,
            element, nature, description_ru
        ])
    db.execute_batch(sql, params)
    print(f"  -> Inserted {len(params)} spirits")


def create_and_populate_stem_combos():
    print("Creating spr_qimen_stem_combos...")
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS spr_qimen_stem_combos (
            combo_id INTEGER PRIMARY KEY,
            stem_top TEXT,
            stem_bottom TEXT,
            combo_char TEXT,
            favorability INTEGER,
            name_ru TEXT,
            description_ru TEXT
        )
    """)
    conn = sqlite_conn()
    c = conn.cursor()
    c.execute("SELECT combo_id, stem_top, stem_bottom, combo_char, favorability, name_ru, description_ru FROM spr_qimen_stem_combos ORDER BY combo_id")
    rows = c.fetchall()
    conn.close()

    db.execute_query("DELETE FROM spr_qimen_stem_combos")
    sql = """
        INSERT INTO spr_qimen_stem_combos (combo_id, stem_top, stem_bottom, combo_char, favorability, name_ru, description_ru)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = [list(r) for r in rows]
    db.execute_batch(sql, params)
    print(f"  -> Inserted {len(params)} stem combos")


def create_and_populate_trigrams():
    print("Creating spr_qimen_trigrams...")
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS spr_qimen_trigrams (
            trigram_id INTEGER PRIMARY KEY,
            trigram_char TEXT,
            trigram_name_ru TEXT,
            trigram_name_en TEXT,
            trigram_name_zh TEXT,
            palace_nos TEXT,
            element TEXT,
            nature TEXT,
            description_ru TEXT
        )
    """)
    trigrams = [
        (1, '乾', 'Небо', 'Qian', '乾', '6', 'Металл', 'auspicious', 'Триграмма Неба, символизирует творчество, силу, отца. Благоприятна для лидерства и начинаний.'),
        (2, '兑', 'Озеро', 'Dui', '兑', '7', 'Металл', 'auspicious', 'Триграмма Озера, символизирует радость, удовольствие, молодую дочь. Благоприятна для творчества и общения.'),
        (3, '离', 'Огонь', 'Li', '离', '9', 'Огонь', 'mixed', 'Триграмма Огня, символизирует свет, красоту, зрелую дочь. Благоприятна для просвещения, но может приносить конфликты.'),
        (4, '震', 'Гром', 'Zhen', '震', '3', 'Дерево', 'auspicious', 'Триграмма Грома, символизирует движение, потрясение, старшего сына. Благоприятна для начала новых дел.'),
        (5, '巽', 'Ветер', 'Xun', '巽', '4', 'Дерево', 'auspicious', 'Триграмма Ветра, символизирует проникновение, гибкость, старшую дочь. Благоприятна для торговли и обучения.'),
        (6, '坎', 'Вода', 'Kan', '坎', '1', 'Вода', 'inauspicious', 'Триграмма Воды, символизирует опасность, глубину, среднего сына. Требует осторожности, но даёт мудрость.'),
        (7, '艮', 'Гора', 'Gen', '艮', '8', 'Земля', 'mixed', 'Триграмма Горы, символизирует покой, остановку, младшего сына. Благоприятна для медитации и обороны.'),
        (8, '坤', 'Земля', 'Kun', '坤', '2', 'Земля', 'auspicious', 'Триграмма Земли, символизирует принятие, материнство, покорность. Благоприятна для поддержки и накопления.'),
    ]
    db.execute_query("DELETE FROM spr_qimen_trigrams")
    sql = """
        INSERT INTO spr_qimen_trigrams (trigram_id, trigram_char, trigram_name_ru, trigram_name_en, trigram_name_zh, palace_nos, element, nature, description_ru)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    db.execute_batch(sql, [list(t) for t in trigrams])
    print(f"  -> Inserted {len(trigrams)} trigrams")


def migrate_table_via_copy(sqlite_table: str, pg_table: str):
    """Migrate a table from SQLite to PostgreSQL using CSV + psql COPY."""
    print(f"Migrating {sqlite_table} -> {pg_table} ...")
    # Check if already populated
    cnt = db.fetch_one(f"SELECT COUNT(*) FROM {pg_table}")
    if cnt and cnt[0] > 0:
        print(f"  = {pg_table} already has {cnt[0]} rows, skipping")
        return

    csv_path = os.path.join(PROJECT_ROOT, f"_tmp_{sqlite_table}.csv")
    conn = sqlite_conn()
    c = conn.cursor()
    c.execute(f"SELECT * FROM {sqlite_table}")
    headers = [d[0] for d in c.description]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        while True:
            batch = c.fetchmany(50000)
            if not batch:
                break
            writer.writerows(batch)
    conn.close()

    psql = os.path.join(PG_BIN_PATH, "psql.exe")
    copy_cmd = f"\\copy {pg_table} FROM '{csv_path.replace(chr(92), '/')}' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')"
    cmd = [
        psql,
        "-h", PG_CONFIG["host"],
        "-p", str(PG_CONFIG["port"]),
        "-U", PG_CONFIG["user"],
        "-d", PG_CONFIG["database"],
        "-c", copy_cmd,
    ]
    env = os.environ.copy()
    env["PGPASSWORD"] = PG_CONFIG["password"]
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ! ERROR: {result.stderr}")
        raise RuntimeError(f"COPY failed for {pg_table}: {result.stderr}")
    # psql prints "COPY N" on stdout
    print(f"  -> {result.stdout.strip()}")
    os.remove(csv_path)


def create_and_populate_chauby_tables():
    print("Ensuring t_qumen_chauby_day/month/year exist...")
    schemas = {
        "t_qumen_chauby_day": """
            CREATE TABLE IF NOT EXISTS t_qumen_chauby_day (
                chart_id TEXT,
                year_pillar TEXT,
                month_pillar TEXT,
                day_pillar TEXT,
                rasklad_id TEXT,
                palace_no INTEGER,
                chart_type TEXT
            )
        """,
        "t_qumen_chauby_month": """
            CREATE TABLE IF NOT EXISTS t_qumen_chauby_month (
                chart_id TEXT,
                year_pillar TEXT,
                month_pillar TEXT,
                rasklad_id TEXT,
                palace_no INTEGER,
                chart_type TEXT
            )
        """,
        "t_qumen_chauby_year": """
            CREATE TABLE IF NOT EXISTS t_qumen_chauby_year (
                chart_id TEXT,
                year_pillar TEXT,
                rasklad_id TEXT,
                palace_no INTEGER,
                chart_type TEXT
            )
        """,
    }
    for tbl, ddl in schemas.items():
        db.execute_query(ddl)
        cnt = db.fetch_one(f"SELECT COUNT(*) FROM {tbl}")
        if cnt and cnt[0] > 0:
            print(f"  = {tbl} already has {cnt[0]} rows, skipping")
            continue
        migrate_table_via_copy(tbl, tbl)


def main():
    print("Starting Qi Men PG population script...")
    alter_tables()
    populate_stars()
    populate_gates()
    populate_gods()
    create_and_populate_stem_combos()
    create_and_populate_trigrams()
    create_and_populate_chauby_tables()

    # Migrate large chart tables
    for sqlite_tbl, pg_tbl in [
        ("t_qumen_dgiren_hourly", "t_qumen_dgiren_hourly"),
        ("t_qumen_dgiren_day", "t_qumen_dgiren_day"),
        ("t_qumen_dgiren_month", "t_qumen_dgiren_month"),
        ("t_qumen_dgiren_year", "t_qumen_dgiren_year"),
        ("t_qumen_chauby_hourly", "t_qumen_chauby_hourly"),
    ]:
        migrate_table_via_copy(sqlite_tbl, pg_tbl)

    print("Done.")


if __name__ == "__main__":
    main()
