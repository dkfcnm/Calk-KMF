#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate t_tung_shu_daily table — aggregated daily data for Tong Shu calendar.

Usage:
    python scripts/generate_tung_shu_daily.py 2026 5    # Generate for May 2026
    python scripts/generate_tung_shu_daily.py 2026      # Generate for entire 2026
"""

import sqlite3
import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from code.tongshu.core.tongshu_day import TongShuDay

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'calk_kmf.sqlite')


def create_table(conn):
    """Create t_tung_shu_daily if not exists."""
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS t_tung_shu_daily (
        calendar_date TEXT PRIMARY KEY,
        year_pillar TEXT,
        month_pillar TEXT,
        day_pillar TEXT,
        year_stem TEXT,
        year_branch TEXT,
        month_stem TEXT,
        month_branch TEXT,
        day_stem TEXT,
        day_branch TEXT,
        solar_term_id INTEGER,
        solar_term_char TEXT,
        solar_term_name_ru TEXT,
        nayin_element TEXT,
        nayin_name TEXT,
        year_nayin_element TEXT,
        year_nayin_name TEXT,
        month_nayin_element TEXT,
        month_nayin_name TEXT,
        day_nayin_element TEXT,
        day_nayin_name TEXT,
        year_period INTEGER,
        month_period INTEGER,
        day_period INTEGER,
        year_element_num INTEGER,
        month_element_num INTEGER,
        day_element_num INTEGER,
        hexagram_family_same INTEGER,
        production_chain INTEGER,
        lunar_day INTEGER,
        day_officer_char TEXT,
        day_officer_name_ru TEXT,
        day_officer_category TEXT,
        constellation_char TEXT,
        constellation_name_ru TEXT,
        constellation_direction TEXT,
        constellation_nature TEXT,
        belt_type TEXT,
        belt_stars TEXT,  -- JSON array as text
        moon_phase_name TEXT,
        moon_phase_pct REAL,
        tongshu_phase_name_ru TEXT,
        great_sun_mountain TEXT,
        great_sun_mountain_name TEXT,
        symbolic_stars TEXT,  -- JSON array as text
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()


def generate_for_month(conn, year: int, month: int):
    """Generate records for a specific month."""
    cursor = conn.cursor()
    start_date = date(year, month, 1)
    # Find end of month
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    
    current = start_date
    count = 0
    while current < end_date:
        day = TongShuDay(current, conn)
        cursor.execute('''
            INSERT OR REPLACE INTO t_tung_shu_daily (
                calendar_date, year_pillar, month_pillar, day_pillar,
                year_stem, year_branch, month_stem, month_branch, day_stem, day_branch,
                solar_term_id, solar_term_char, solar_term_name_ru,
                nayin_element, nayin_name,
                year_nayin_element, year_nayin_name,
                month_nayin_element, month_nayin_name,
                day_nayin_element, day_nayin_name,
                year_period, month_period, day_period,
                year_element_num, month_element_num, day_element_num,
                hexagram_family_same, production_chain, lunar_day,
                day_officer_char, day_officer_name_ru, day_officer_category,
                constellation_char, constellation_name_ru, constellation_direction, constellation_nature,
                belt_type, belt_stars,
                moon_phase_name, moon_phase_pct,
                tongshu_phase_name_ru,
                great_sun_mountain, great_sun_mountain_name,
                symbolic_stars
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            current.isoformat(),
            day.year_pillar, day.month_pillar, day.day_pillar,
            day.year_stem, day.year_branch, day.month_stem, day.month_branch, day.day_stem, day.day_branch,
            day.solar_term_id, day.solar_term_char, day.solar_term_name_ru,
            day.nayin_element, day.nayin_name,
            day.year_nayin_element, day.year_nayin_name,
            day.month_nayin_element, day.month_nayin_name,
            day.day_nayin_element, day.day_nayin_name,
            day.year_period, day.month_period, day.day_period,
            day.year_element_num, day.month_element_num, day.day_element_num,
            int(day.hexagram_family_same), int(day.production_chain), day.lunar_day,
            day.day_officer_char, day.day_officer_name_ru, day.day_officer_category,
            day.constellation_char, day.constellation_name_ru, day.constellation_direction, day.constellation_nature,
            day.belt_type, json.dumps(day.belt_stars, ensure_ascii=False) if day.belt_stars else None,
            day.moon_phase_name, day.moon_phase_pct,
            day.tongshu_phase_name_ru,
            day.great_sun_mountain, day.great_sun_mountain_name,
            json.dumps(day.symbolic_stars, ensure_ascii=False) if day.symbolic_stars else None,
        ))
        count += 1
        current += timedelta(days=1)
    
    conn.commit()
    return count


def generate_for_year(conn, year: int):
    """Generate records for entire year."""
    total = 0
    for month in range(1, 13):
        count = generate_for_month(conn, year, month)
        total += count
        print(f"  Month {month:02d}: {count} days")
    return total


def main():
    import json  # local import for the function above
    
    if len(sys.argv) < 2:
        print("Usage: python generate_tung_shu_daily.py <year> [month]")
        return 1
    
    year = int(sys.argv[1])
    month = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    print(f"DB: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    create_table(conn)
    
    if month:
        print(f"Generating for {year}-{month:02d}...")
        count = generate_for_month(conn, year, month)
        print(f"Done. {count} records generated.")
    else:
        print(f"Generating for year {year}...")
        total = generate_for_year(conn, year)
        print(f"Done. {total} records generated.")
    
    conn.close()
    return 0


if __name__ == '__main__':
    import json
    sys.exit(main())
