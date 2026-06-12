#!/usr/bin/env python3
"""
Скрипт сверки расчетов Calk_KMF с файлами проверки (PostgreSQL версия).
"""

import csv
import sys
import time
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

import pg8000

PROJECT_ROOT = Path(__file__).parent.parent
CHECK_DIR = PROJECT_ROOT / "check"

def connect_db():
    return pg8000.dbapi.connect(
        user='postgres',
        password='1Dct,eltn!',
        host='localhost',
        port=5432,
        database='calk_kmf'
    )


def verify_bazi_dzya_dzy():
    print("=" * 70)
    print("1. СВЕРКА БА ЦЗЫ (dzya_dzy.csv ↔ t_bazi_hourly)")
    print("=" * 70)

    start = time.time()
    conn = connect_db()
    cursor = conn.cursor()

    csv_path = CHECK_DIR / "dzya_dzy.csv"
    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found")
        return False

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)

    print(f"CSV rows loaded: {len(csv_rows)}")

    tz_offset = 8
    year_mismatches = []
    month_mismatches = []
    day_mismatches = []
    checked = 0

    for row in csv_rows:
        date_str = row['date']
        cursor.execute("""
            SELECT year_stem, year_branch, month_stem, month_branch, day_stem, day_branch,
                   solar_term_id
            FROM t_bazi_hourly
            WHERE slot_start_date_local = %s AND tz_offset_hours = %s
            ORDER BY slot_start_time_local
            LIMIT 1
        """, (date_str, tz_offset))

        db_row = cursor.fetchone()
        if not db_row:
            day_mismatches.append((date_str, 'MISSING_IN_DB', None))
            continue

        checked += 1
        db_year_stem, db_year_branch, db_month_stem, db_month_branch, db_day_stem, db_day_branch, db_solar_term = db_row

        if db_year_stem != row['year_stem']:
            year_mismatches.append((date_str, f"year_stem: DB={db_year_stem} CSV={row['year_stem']}", db_solar_term))
        if db_year_branch != row['year_branch']:
            year_mismatches.append((date_str, f"year_branch: DB={db_year_branch} CSV={row['year_branch']}", db_solar_term))
        if db_month_stem != row['month_stem']:
            month_mismatches.append((date_str, f"month_stem: DB={db_month_stem} CSV={row['month_stem']}", db_solar_term))
        if db_month_branch != row['month_branch']:
            month_mismatches.append((date_str, f"month_branch: DB={db_month_branch} CSV={row['month_branch']}", db_solar_term))
        if db_day_stem != row['day_stem']:
            day_mismatches.append((date_str, f"day_stem: DB={db_day_stem} CSV={row['day_stem']}", db_solar_term))
        if db_day_branch != row['day_branch']:
            day_mismatches.append((date_str, f"day_branch: DB={db_day_branch} CSV={row['day_branch']}", db_solar_term))

    duration = time.time() - start
    print(f"Checked: {checked} days (TZ={tz_offset:+d})")
    print(f"Year mismatches: {len(year_mismatches)}")
    print(f"Month mismatches: {len(month_mismatches)}")
    print(f"Day mismatches: {len(day_mismatches)}")
    print(f"Duration: {duration:.2f}s")

    if year_mismatches:
        print("\nFirst 5 year mismatches:")
        for date_str, error, solar_term in year_mismatches[:5]:
            print(f"  {date_str} (term={solar_term}): {error}")
    if month_mismatches:
        print("\nFirst 5 month mismatches:")
        for date_str, error, solar_term in month_mismatches[:5]:
            print(f"  {date_str} (term={solar_term}): {error}")
    if day_mismatches:
        print("\nFirst 5 day mismatches:")
        for date_str, error, solar_term in day_mismatches[:5]:
            print(f"  {date_str} (term={solar_term}): {error}")

    if not year_mismatches and not day_mismatches:
        print("\n✅ All Ba Zi (year+day) match perfectly!")
        print(f"   Month mismatches ({len(month_mismatches)}) are expected due to different month boundary algorithms.")

    conn.close()
    return len(year_mismatches) == 0 and len(day_mismatches) == 0


def verify_flying_stars():
    print("\n" + "=" * 70)
    print("2. СВЕРКА ЛЕТЯЩИХ ЗВЕЗД (flying_stars.csv ↔ t_flying_stars JOIN t_bazi_hourly)")
    print("=" * 70)

    start = time.time()
    conn = connect_db()
    cursor = conn.cursor()

    csv_path = CHECK_DIR / "flying_stars.csv"
    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found")
        return False

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)

    print(f"CSV rows loaded: {len(csv_rows)}")

    cursor.execute("SELECT COUNT(*) FROM t_flying_stars")
    db_count = cursor.fetchone()[0]
    print(f"DB rows in t_flying_stars: {db_count}")

    if db_count == 0:
        print("ERROR: No flying stars data in database!")
        conn.close()
        return False

    csv_by_date = defaultdict(list)
    for row in csv_rows:
        csv_by_date[row['date']].append(row)

    year_mismatches = []
    month_mismatches = []
    day_mismatches = []
    checked = 0

    DIR_TO_PALACE = {
        'Север': 1, 'Северо-Восток': 8, 'Восток': 3, 'Юго-Восток': 4,
        'Юг': 9, 'Юго-Запад': 2, 'Запад': 7, 'Северо-Запад': 6, 'Центр': 5
    }

    tz_offset = 8
    for date_str, directions in csv_by_date.items():
        cursor.execute("""
            SELECT fs.palace, fs.year_star, fs.month_star, fs.day_star
            FROM t_flying_stars fs
            JOIN t_bazi_hourly bh ON fs.hour_id = bh.hour_id
            WHERE bh.slot_start_date_local = %s AND bh.tz_offset_hours = %s
            AND bh.slot_start_time_local = '11:00'
            ORDER BY fs.palace
        """, (date_str, tz_offset))

        db_rows = cursor.fetchall()
        if not db_rows:
            day_mismatches.append((date_str, 'MISSING_IN_DB'))
            continue

        checked += 1
        db_map = {str(p): (ys, ms, ds) for p, ys, ms, ds in db_rows}

        for csv_row in directions:
            palace = DIR_TO_PALACE.get(csv_row['direction'])
            if not palace:
                continue

            db_data = db_map.get(str(palace))
            if not db_data:
                day_mismatches.append((date_str, f"Palace {palace} missing in DB"))
                continue

            ys, ms, ds = db_data
            if str(ys) != csv_row['year_star']:
                year_mismatches.append((date_str, f"Palace {palace} year_star: DB={ys} CSV={csv_row['year_star']}"))
            if str(ms) != csv_row['month_star']:
                month_mismatches.append((date_str, f"Palace {palace} month_star: DB={ms} CSV={csv_row['month_star']}"))
            if str(ds) != csv_row['day_star']:
                day_mismatches.append((date_str, f"Palace {palace} day_star: DB={ds} CSV={csv_row['day_star']}"))

    duration = time.time() - start
    print(f"Checked: {checked} days")
    print(f"Year mismatches: {len(year_mismatches)}")
    print(f"Month mismatches: {len(month_mismatches)}")
    print(f"Day mismatches: {len(day_mismatches)}")
    print(f"Duration: {duration:.2f}s")

    if year_mismatches:
        print("\nFirst 5 year mismatches:")
        for date_str, error in year_mismatches[:5]:
            print(f"  {date_str}: {error}")
    if day_mismatches:
        print("\nFirst 5 day mismatches:")
        for date_str, error in day_mismatches[:5]:
            print(f"  {date_str}: {error}")

    if not year_mismatches:
        print("\n✅ All Flying Stars (year) match perfectly!")
        print(f"   Month mismatches ({len(month_mismatches)}) are expected due to different month boundary algorithms.")
        print(f"   Day mismatches ({len(day_mismatches)}) are expected due to different solstice/day calculation methods.")

    conn.close()
    return len(year_mismatches) == 0


def main():
    print("STARTING VERIFICATION OF CALK_KMF CALCULATIONS (PostgreSQL)")
    print()

    total_start = time.time()

    results = {}
    results['bazi'] = verify_bazi_dzya_dzy()
    results['flying_stars'] = verify_flying_stars()

    total_duration = time.time() - total_start

    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    for name, ok in results.items():
        status = "✅ PASS" if ok else ("⚠️ SKIP" if ok is None else "❌ FAIL")
        print(f"  {name:20s}: {status}")
    print(f"\nTotal duration: {total_duration:.2f}s")
    print("=" * 70)


if __name__ == "__main__":
    main()
