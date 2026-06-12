#!/usr/bin/env python3
"""
SQLite-совместимая версия run_update_optimized.py для пересоздания t_bazi_hourly.
"""

import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import os

sys.path.insert(0, os.getcwd())

import sqlite3
from code.bazi_calendar.engine import BaziEngine
from code.bazi_calendar.hourly import (
    ensure_bazi_hourly_table, SLOT_START_HOURS, SLOT_DURATION,
    _align_to_slot_start, _format_date, _format_time, WEEKDAY_SHORT_RU, _format_iso_minute
)
from code.bazi_calendar.solar_terms import tz_from_offset

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "calk_kmf.sqlite"

YEAR_START = 2025
YEAR_END = 2027
TZ_OFFSETS = range(-12, 15)
BATCH_SIZE = 50000


def run_update_sqlite():
    print("Initializing Bazi Engine for SQLite...")
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    engine = BaziEngine(conn)
    
    print("Ensuring table schema...")
    ensure_bazi_hourly_table(conn)
    
    cursor = conn.cursor()
    print("Clearing t_bazi_hourly...")
    cursor.execute("DELETE FROM t_bazi_hourly")
    conn.commit()
    
    print(f"Generating data for years {YEAR_START}-{YEAR_END}...")
    
    data_batch = []
    total_count = 0
    
    for offset in TZ_OFFSETS:
        local_tz = tz_from_offset(offset)
        
        start_local = datetime(YEAR_START, 1, 1, 0, 0, tzinfo=local_tz)
        end_local = datetime(YEAR_END + 1, 1, 1, 0, 0, tzinfo=local_tz)
        
        curr_local = _align_to_slot_start(start_local)
        start_utc = curr_local.astimezone(timezone.utc)
        end_utc = end_local.astimezone(timezone.utc)
        
        print(f"Processing offset {offset:+d} (Start: {_format_iso_minute(start_utc)})...")
        
        prev_month_str = None
        prev_day_str = None
        lunar_m_zi = 0
        lunar_d_zi = 0
        lunar_leap_zi = 0
        
        while True:
            slot_end_local = curr_local + SLOT_DURATION
            
            if curr_local >= end_local:
                break
                
            curr_utc = curr_local.astimezone(timezone.utc)
            slot_end_utc = slot_end_local.astimezone(timezone.utc)
            
            res = engine.calc_pillars(curr_utc, offset)
            
            y = res['year']
            m = res['month']
            d = res['day']
            h = res['hour']
            
            y_str = str(y)
            m_str = str(m)
            d_str = str(d)
            h_str = str(h)
            
            lunar = res['lunar']
            lunar_m, lunar_d, lunar_leap = lunar
            
            if prev_month_str is None or m_str != prev_month_str:
                lunar_m_zi = lunar_m
                lunar_leap_zi = int(lunar_leap)
            
            if prev_day_str is None or d_str != prev_day_str:
                lunar_d_zi = lunar_d
                
            prev_month_str = m_str
            prev_day_str = d_str
            
            s_d_loc = _format_date(curr_local)
            s_t_loc = _format_time(curr_local)
            e_d_loc = _format_date(slot_end_local)
            e_t_loc = _format_time(slot_end_local)
            
            hash_src = f"{offset}|{s_d_loc}|{s_t_loc}|{e_d_loc}|{e_t_loc}"
            hour_id = hashlib.sha1(hash_src.encode('utf-8')).hexdigest()
            
            weekday = WEEKDAY_SHORT_RU[curr_local.weekday()]
            
            row = (
                hour_id, offset,
                _format_date(curr_utc), _format_time(curr_utc),
                _format_date(slot_end_utc), _format_time(slot_end_utc),
                s_d_loc, s_t_loc,
                e_d_loc, e_t_loc,
                weekday,
                res['solar_term_id'],
                y_str, m_str, d_str, h_str,
                y.stem, y.branch,
                m.stem, m.branch,
                d.stem, d.branch,
                h.stem, h.branch,
                lunar_m, lunar_d, int(lunar_leap),
                lunar_m_zi, lunar_d_zi, lunar_leap_zi
            )
            
            data_batch.append(row)
            
            if len(data_batch) >= BATCH_SIZE:
                values_ph = ",".join(["?"] * 30)
                cursor.executemany(f"""
                    INSERT INTO t_bazi_hourly (
                        hour_id, tz_offset_hours,
                        slot_start_date_utc, slot_start_time_utc,
                        slot_end_date_utc, slot_end_time_utc,
                        slot_start_date_local, slot_start_time_local,
                        slot_end_date_local, slot_end_time_local,
                        weekday_local, solar_term_id,
                        year_pillar, month_pillar, day_pillar, hour_pillar,
                        year_stem, year_branch, month_stem, month_branch,
                        day_stem, day_branch, hour_stem, hour_branch,
                        lunar_month, lunar_day, lunar_is_leap,
                        lunar_month_zi, lunar_day_zi, lunar_is_leap_zi
                    ) VALUES ({values_ph})
                """, data_batch)
                conn.commit()
                total_count += len(data_batch)
                print(f"  Inserted {total_count:,} rows...")
                data_batch = []
            
            curr_local = slot_end_local
    
    if data_batch:
        values_ph = ",".join(["?"] * 30)
        cursor.executemany(f"""
            INSERT INTO t_bazi_hourly (
                hour_id, tz_offset_hours,
                slot_start_date_utc, slot_start_time_utc,
                slot_end_date_utc, slot_end_time_utc,
                slot_start_date_local, slot_start_time_local,
                slot_end_date_local, slot_end_time_local,
                weekday_local, solar_term_id,
                year_pillar, month_pillar, day_pillar, hour_pillar,
                year_stem, year_branch, month_stem, month_branch,
                day_stem, day_branch, hour_stem, hour_branch,
                lunar_month, lunar_day, lunar_is_leap,
                lunar_month_zi, lunar_day_zi, lunar_is_leap_zi
            ) VALUES ({values_ph})
        """, data_batch)
        conn.commit()
        total_count += len(data_batch)
    
    print(f"Total inserted: {total_count:,} rows")
    conn.close()
    print("Done!")


if __name__ == "__main__":
    run_update_sqlite()
