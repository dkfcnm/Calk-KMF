#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрая синхронизация t_bazi_hourly из SQLite в PostgreSQL через CSV + psql COPY.
Оптимизация: заменяет медленную Python-генерацию (~7 мин) на загрузку за ~10 сек.
"""

import sqlite3
import csv
import subprocess
import os
import time

PG_BIN = r"d:\Program Files\PostgreSQL\18\bin\psql.exe"
PG_HOST = "localhost"
PG_PORT = "5432"
PG_USER = "postgres"
PG_DB = "calk_kmf"
PG_PASSWORD = "1Dct,eltn!"

SQLITE_DB = "calk_kmf.sqlite"
CSV_FILE = "t_bazi_hourly.csv"

COLUMNS = [
    "hour_id", "tz_offset_hours", "slot_start_date_utc", "slot_start_time_utc",
    "slot_end_date_utc", "slot_end_time_utc", "slot_start_date_local", "slot_start_time_local",
    "slot_end_date_local", "slot_end_time_local", "weekday_local", "solar_term_id",
    "year_pillar", "month_pillar", "day_pillar", "hour_pillar",
    "year_stem", "year_branch", "month_stem", "month_branch", "day_stem", "day_branch",
    "hour_stem", "hour_branch", "lunar_month", "lunar_day", "lunar_is_leap",
    "lunar_month_zi", "lunar_day_zi", "lunar_is_leap_zi", "year_int"
]

def export_csv():
    print("[1/4] Exporting from SQLite to CSV...")
    conn = sqlite3.connect(SQLITE_DB)
    cur = conn.cursor()
    cols = ", ".join(COLUMNS)
    cur.execute(f"SELECT {cols} FROM t_bazi_hourly")
    
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(cur.fetchall())
    
    conn.close()
    print(f"  CSV exported: {os.path.getsize(CSV_FILE)} bytes")

def recreate_table():
    print("[2/4] Recreating table in PostgreSQL...")
    ddl = """
DROP TABLE IF EXISTS t_bazi_hourly CASCADE;
CREATE TABLE t_bazi_hourly (
    hour_id TEXT NOT NULL,
    tz_offset_hours INTEGER NOT NULL,
    slot_start_date_utc TEXT NOT NULL,
    slot_start_time_utc TEXT NOT NULL,
    slot_end_date_utc TEXT,
    slot_end_time_utc TEXT,
    slot_start_date_local TEXT,
    slot_start_time_local TEXT,
    slot_end_date_local TEXT,
    slot_end_time_local TEXT,
    weekday_local TEXT,
    solar_term_id INTEGER,
    year_pillar TEXT,
    month_pillar TEXT,
    day_pillar TEXT,
    hour_pillar TEXT,
    year_stem TEXT,
    year_branch TEXT,
    month_stem TEXT,
    month_branch TEXT,
    day_stem TEXT,
    day_branch TEXT,
    hour_stem TEXT,
    hour_branch TEXT,
    lunar_month INTEGER,
    lunar_day INTEGER,
    lunar_is_leap INTEGER,
    lunar_month_zi INTEGER,
    lunar_day_zi INTEGER,
    lunar_is_leap_zi INTEGER,
    year_int INTEGER,
    PRIMARY KEY (tz_offset_hours, slot_start_date_utc, slot_start_time_utc)
);
CREATE INDEX idx_bazi_hourly_utc ON t_bazi_hourly(tz_offset_hours, slot_start_date_utc, slot_start_time_utc);
CREATE INDEX idx_bazi_hourly_local ON t_bazi_hourly(tz_offset_hours, slot_start_date_local, slot_start_time_local);
"""
    env = os.environ.copy()
    env["PGPASSWORD"] = PG_PASSWORD
    subprocess.run([PG_BIN, "-h", PG_HOST, "-p", PG_PORT, "-U", PG_USER, "-d", PG_DB, "-c", ddl], 
                   env=env, check=True, capture_output=True)
    print("  Table recreated.")

def load_csv():
    print("[3/4] Loading CSV via COPY...")
    env = os.environ.copy()
    env["PGPASSWORD"] = PG_PASSWORD
    cols = ", ".join(COLUMNS)
    copy_cmd = f"\COPY t_bazi_hourly ({cols}) FROM '{os.path.abspath(CSV_FILE)}' WITH (FORMAT CSV, ENCODING 'UTF8')"
    result = subprocess.run([PG_BIN, "-h", PG_HOST, "-p", PG_PORT, "-U", PG_USER, "-d", PG_DB, "-c", copy_cmd],
                           env=env, check=True, capture_output=True, text=True)
    print(f"  {result.stdout.strip()}")

def cleanup():
    print("[4/4] Cleaning up...")
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
    print("  Done.")

def verify():
    env = os.environ.copy()
    env["PGPASSWORD"] = PG_PASSWORD
    result = subprocess.run([PG_BIN, "-h", PG_HOST, "-p", PG_PORT, "-U", PG_USER, "-d", PG_DB, 
                            "-c", "SELECT COUNT(*) FROM t_bazi_hourly"],
                           env=env, capture_output=True, text=True)
    print(f"[Verify] PostgreSQL t_bazi_hourly: {result.stdout.strip()}")

if __name__ == "__main__":
    start = time.time()
    export_csv()
    recreate_table()
    load_csv()
    cleanup()
    verify()
    print(f"\nTotal time: {time.time()-start:.1f}s")
