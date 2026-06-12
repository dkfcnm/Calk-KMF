#!/usr/bin/env python3
"""
SQLite-совместимая версия run_update.py для пересоздания t_flying_stars.
Использует тот же алгоритм, что и PG-версия, но с SQLite-совместимым SQL.
"""

import sys
import os
import time
import sqlite3

sys.path.insert(0, os.getcwd())

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "calk_kmf.sqlite")


def run_update_sqlite(logger=None):
    log_id = None
    if logger:
        log_id = logger.start_stage("Flying Stars Calculation (SQLite)")

    print("Starting Flying Stars Calculation (SQLite)...")
    start_time = time.time()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Recreating t_flying_stars table...")
    cursor.execute("DROP TABLE IF EXISTS t_flying_stars")
    cursor.execute("""
    CREATE TABLE t_flying_stars (
        hour_id TEXT,
        palace INTEGER,
        year_star INTEGER,
        month_star INTEGER,
        day_star INTEGER,
        hour_star INTEGER,
        PRIMARY KEY (hour_id, palace)
    )
    """)

    print("Executing SQL calculation...")
    
    # SQLite-compatible version of the SQL query
    # Replace ::DATE with substr, LATERAL with subquery, and date arithmetic with julianday
    sql = """
    INSERT INTO t_flying_stars (hour_id, palace, year_star, month_star, day_star, hour_star)
    WITH base_data AS (
        SELECT 
            h.hour_id,
            substr(h.slot_start_date_utc, 1, 10) as curr_date,
            CAST(substr(h.slot_start_date_utc, 1, 4) AS INT) as cal_year,
            h.year_branch,
            h.month_branch,
            h.day_branch,
            h.hour_branch,
            h.solar_term_id
        FROM t_bazi_hourly h
    ),
    solstices AS (
        SELECT 
            solar_term_id,
            substr(crossing_utc, 1, 10) as s_date
        FROM t_solar_term_time 
        WHERE solar_term_id IN (10, 22)
    ),
    -- Find the latest solstice <= current date for each row
    latest_solstice AS (
        SELECT 
            b.hour_id,
            b.curr_date,
            b.cal_year,
            b.year_branch,
            b.month_branch,
            b.day_branch,
            b.hour_branch,
            b.solar_term_id,
            (SELECT solar_term_id FROM solstices s WHERE s.s_date <= b.curr_date ORDER BY s.s_date DESC LIMIT 1) as solstice_type,
            (SELECT s_date FROM solstices s WHERE s.s_date <= b.curr_date ORDER BY s.s_date DESC LIMIT 1) as solstice_date
        FROM base_data b
    ),
    calc_centers AS (
        SELECT
            ls.hour_id,
            -- YEAR CENTER
            CASE 
                WHEN ls.solar_term_id IN (23, 24) THEN 
                     CASE WHEN (10 - ((ls.cal_year - 1) % 100 % 9 + 1)) = 0 THEN 1 
                          ELSE (10 - ((ls.cal_year - 1) % 100 % 9 + 1)) 
                     END
                ELSE 
                     CASE WHEN (10 - (ls.cal_year % 100 % 9 + 1)) = 0 THEN 1 
                          ELSE (10 - (ls.cal_year % 100 % 9 + 1)) 
                     END
            END as year_center,
            ls.year_branch,
            ls.month_branch,
            ls.solstice_type,
            CAST(julianday(ls.curr_date) - julianday(ls.solstice_date) AS INT) as days_diff,
            CASE WHEN ls.solar_term_id BETWEEN 10 AND 21 THEN 1 ELSE 2 END as day_yy,
            ls.day_branch,
            ls.hour_branch
        FROM latest_solstice ls
    ),
    resolved_centers AS (
        SELECT
            c.hour_id,
            c.year_center,
            COALESCE(ms.star, 5) as month_center,
            CASE 
                WHEN c.solstice_type = 22 THEN (c.days_diff % 9) + 1
                ELSE 9 - (c.days_diff % 9)
            END as day_center,
            COALESCE(hs.star, 5) as hour_center
        FROM calc_centers c
        LEFT JOIN spr_month_stars ms 
            ON ms.year_branch = c.year_branch 
            AND ms.month_branch = c.month_branch
        LEFT JOIN spr_hour_stars hs 
            ON hs.day_branch = c.day_branch 
            AND hs.yin_yang = c.day_yy 
            AND hs.hour_branch = c.hour_branch
    )
    SELECT 
        rc.hour_id,
        m_y.palace,
        m_y.resident_star as year_star,
        m_m.resident_star as month_star,
        m_d.resident_star as day_star,
        m_h.resident_star as hour_star
    FROM resolved_centers rc
    JOIN spr_flying_star_map m_y ON m_y.center_star = rc.year_center
    JOIN spr_flying_star_map m_m ON m_m.center_star = rc.month_center AND m_m.palace = m_y.palace
    JOIN spr_flying_star_map m_d ON m_d.center_star = rc.day_center AND m_d.palace = m_y.palace
    JOIN spr_flying_star_map m_h ON m_h.center_star = rc.hour_center AND m_h.palace = m_y.palace
    """

    cursor.execute(sql)

    print("Creating index...")
    cursor.execute("CREATE INDEX idx_fs_hour ON t_flying_stars(hour_id)")

    conn.commit()
    conn.close()

    duration = time.time() - start_time
    print(f"Flying Stars (SQLite) completed in {duration:.4f} seconds.")

    if logger and log_id:
        logger.end_stage(log_id)


if __name__ == "__main__":
    run_update_sqlite()
